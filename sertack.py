#!/usr/bin/env python3

import sys
import os
import time
import queue
import threading
import serial

if os.name == 'nt':
    import msvcrt
else:
    import tty
    import termios


def print_help():
    help_text = """
sertack - Automated Bootloader Interrupt & Interactive Serial Terminal Tool

Usage:
  python sertack.py [port] [baud] [raw_trigger] [target_prompt] [interval] [interactive_baud]
  python sertack.py -h | --help

Positional Arguments (Optional):
  1. port              Serial port device path (e.g., /dev/ttyUSB0, COM3).
                       [default: /dev/ttyUSB0]
  2. baud              Initial serial baud rate used during boot hammering.
                       [default: 115200]
  3. raw_trigger       Payload string sent continuously to interrupt the boot process.
                       Supports escape sequences (e.g., '4', '\\r\\n', '\\x03').
                       [default: "4"]
  4. target_prompt     Substring/prompt expected upon successfully breaking boot.
                       [default: "MT7620 #"]
  5. interval          Delay in seconds between trigger payloads.
                       [default: 0.05]
  6. interactive_baud  Baud rate to switch to after prompt detection (if different).
                       [default: same as initial baud]

Interactive Terminal Keybindings:
  Ctrl+B               Open the interactive sertack menu (memory dump, printenv, reset, etc.)
  Ctrl+]               Exit the script cleanly

Examples:
  python sertack.py
  python sertack.py /dev/ttyUSB0 115200 "4" "MT7620 #"
  python sertack.py COM4 57600 "\\x03" "U-Boot>" 0.02
  python sertack.py /dev/ttyUSB0 115200 "4\\r\\n" "uboot>" 0.05 115200
"""
    print(help_text.strip())


def parse_payload_arg(raw_arg: str) -> bytes:
    """
    Parses a string containing potential escape sequences (\r, \n, \x00, etc.)
    into its true raw byte sequence.
    """
    parsed_str = raw_arg.encode('utf-8').decode('unicode_escape')
    return parsed_str.encode('latin-1')


def read_from_dut(ser, stop_event, trigger_found_event, expected_response, dump_queue):
    """
    Background thread: Continuously streams incoming DUT output to VT100-like terminal,
    sets the trigger event when target_prompt appears, and pushes decoded text to dump_queue.
    """
    buffer = ""

    while not stop_event.is_set():
        try:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                decoded = data.decode('utf-8', errors='replace')

                # Stream raw DUT output live
                sys.stdout.write(decoded)
                sys.stdout.flush()

                # Push to queue for active dump capture (bounded to avoid unbounded memory growth)
                if dump_queue is not None:
                    try:
                        dump_queue.put_nowait(decoded)
                    except queue.Full:
                        try:
                            dump_queue.get_nowait()
                            dump_queue.put_nowait(decoded)
                        except queue.Empty:
                            pass

                # Buffer matching for prompt during boot flood
                if not trigger_found_event.is_set():
                    buffer += decoded
                    if expected_response in buffer:
                        trigger_found_event.set()

                    if len(buffer) > 2048:
                        buffer = buffer[-1024:]
            else:
                time.sleep(0.001)
        except Exception as e:
            sys.stderr.write(f"\n[!] Serial read error: {e}\n")
            break


def drain_queue(q):
    """Removes any stale items currently sitting in the queue."""
    while True:
        try:
            q.get_nowait()
        except queue.Empty:
            break


def send_uboot_cmd(ser, command, wait_time=1.0):
    time.sleep(0.1)
    payload = command.encode('utf-8') + b'\r\n'
    ser.write(payload)
    time.sleep(wait_time)


def execute_md_dump(ser, target_prompt, dump_queue):
    start_addr = input("Enter start memory address [default: 0xbc000000]: ").strip() or "0xbc000000"
    flash_size = input("Enter dump size [default: 0x800000]: ").strip() or "0x800000"
    out_file = input("Enter output file path [default: ./fw-dump.hex]: ").strip() or "./fw-dump.hex"

    try:
        size_bytes = int(flash_size, 16)
        safety_timeout = max(120.0, (size_bytes / 4096.0) * 12.0 + 120.0)
    except ValueError:
        safety_timeout = 7200.0

    # Clear stale data before starting dump capture
    drain_queue(dump_queue)

    print(f"\n[+] Dumping memory: 'md.b {start_addr} {flash_size}' -> {out_file}...\n")
    print(f"[i] Waiting for prompt '{target_prompt}' to confirm completion (timeout: {safety_timeout:.0f}s)...\n")

    time.sleep(0.1)
    ser.write(f"md.b {start_addr} {flash_size}\r\n".encode('utf-8'))

    tail_window = ""
    prompt_len = max(len(target_prompt), 64)
    start_time = time.monotonic()
    last_data_time = start_time
    completed = False

    try:
        with open(out_file, "w", encoding="utf-8", errors="replace") as f:
            while (time.monotonic() - start_time) < safety_timeout:
                try:
                    chunk = dump_queue.get(timeout=0.25)
                except queue.Empty:
                    # If no data arrived for 15s after we already received dump output, check if prompt was missed
                    if (time.monotonic() - last_data_time) > 15.0 and target_prompt in tail_window:
                        completed = True
                        break
                    continue

                last_data_time = time.monotonic()
                f.write(chunk)

                # Keep enough trailing text to catch prompts split across chunks
                tail_window = (tail_window + chunk)[-(prompt_len * 4):]
                if target_prompt in tail_window:
                    # Drain any remaining immediate chunks in queue so trailing bytes aren't lost
                    time.sleep(0.05)
                    while True:
                        try:
                            extra = dump_queue.get_nowait()
                            f.write(extra)
                        except queue.Empty:
                            break
                    f.flush()
                    completed = True
                    break

            f.flush()
    except KeyboardInterrupt:
        print(f"\n[!] Dump interrupted by user. Partial dump saved to: {out_file}")
        return
    except Exception as e:
        print(f"\n[!] Dump error: {e}. Partial dump saved to: {out_file}")
        return

    if completed:
        print(f"\n[+] Memory dump completed and saved to: {out_file}")
    else:
        print(f"\n[!] Timed out waiting for '{target_prompt}'. Partial dump saved to: {out_file}")


def display_interactive_menu(ser, target_prompt, dump_queue):
    while True:
        print("\n" + "=" * 50)
        print("                 sertack MENU")
        print("=" * 50)
        print(" 1. Execute U-BOOT 'printenv'")
        print(" 2. Dump Firmware/Memory to File (md.b)")
        print(" 3. Execute U-BOOT 'help'")
        print(" 4. Return to Interactive Terminal")
        print(" 5. Reset Device and keep VT100 terminal running")
        print(" 6. Mount Root within - Failsafe -")
        print(" 7. Exit")
        print("=" * 50)

        choice = input("Select an option: ").strip().lower()

        if choice == '1':
            print("\n[+] Executing 'printenv'...\n")
            send_uboot_cmd(ser, "printenv", wait_time=1.5)
        elif choice == '2':
            execute_md_dump(ser, target_prompt, dump_queue)
        elif choice == '3':
            ser.write(b'help\r\n')
        elif choice == '4':
            print("\n[+] Returning to Interactive Terminal...")
            return 'vt100'
        elif choice == '5':
            print("\n[+] Resetting device...\n")
            send_uboot_cmd(ser, "reset", wait_time=0.5)
            return 'vt100'
        elif choice == '6':
            print("\n[+] Mounting Root...\n")
            send_uboot_cmd(ser, "mount_root", wait_time=1.5)
            return 'vt100'
        elif choice in ('7', 'q', 'exit'):
            print("\n[+] Cleanly exiting script...")
            return 'exit'
        else:
            print("\n[!] Invalid choice, try again.")


def run_interactive_vt100(ser, stop_event, target_prompt, dump_queue):
    print("\n\n-------------------------------------------------")
    print("      INTERACTIVE VT100 TERMINAL ACTIVE          ")
    print("   Press 'Ctrl+B' for Menu | Press 'Ctrl+]' to Exit ")
    print("-------------------------------------------------\n")
    ser.write(b'\r')

    if os.name != 'nt':
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            while not stop_event.is_set():
                ch = sys.stdin.read(1)

                if ch == '\x1d':  # Ctrl+] -> Exit Script
                    return 'exit'
                elif ch == '\x02':  # Ctrl+B -> Open Menu
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    action = display_interactive_menu(ser, target_prompt, dump_queue)
                    if action == 'exit':
                        return 'exit'
                    tty.setraw(sys.stdin.fileno())
                    print("\n--- INTERACTIVE VT100 TERMINAL ACTIVE (Ctrl+B for Menu | Ctrl+] to Exit) ---\n")
                elif ch in ('\r', '\n', '\x0d'):  # Enter Key
                    ser.write(b'\r\n')
                else:
                    ser.write(ch.encode('utf-8', errors='ignore'))
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    else:
        while not stop_event.is_set():
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch == b'\x1d':  # Ctrl+]
                    return 'exit'
                elif ch == b'\x02':  # Ctrl+B
                    action = display_interactive_menu(ser, target_prompt, dump_queue)
                    if action == 'exit':
                        return 'exit'
                    print("\n--- INTERACTIVE VT100 TERMINAL ACTIVE (Ctrl+B for Menu | Ctrl+] to Exit) ---\n")
                elif ch in (b'\r', b'\n'):
                    ser.write(b'\r\n')
                else:
                    ser.write(ch)
            time.sleep(0.001)
    return 'exit'


def main():
    if any(arg in ('-h', '--help') for arg in sys.argv[1:]):
        print_help()
        sys.exit(0)

    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
    raw_trigger = sys.argv[3] if len(sys.argv) > 3 else "4"
    target_prompt = sys.argv[4] if len(sys.argv) > 4 else "MT7620 #"
    interval = float(sys.argv[5]) if len(sys.argv) > 5 else 0.05
    interactive_baud = int(sys.argv[6]) if len(sys.argv) > 6 else baud

    payload = parse_payload_arg(raw_trigger)

    ser = serial.Serial(port, baud, timeout=0.01)
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    stop_event = threading.Event()
    trigger_found_event = threading.Event()
    dump_queue = queue.Queue(maxsize=10000)

    reader_thread = threading.Thread(
        target=read_from_dut,
        args=(ser, stop_event, trigger_found_event, target_prompt, dump_queue),
        daemon=True
    )
    reader_thread.start()

    print("=================================================================")
    print(f" PORT:             {port} @ {baud} baud")
    print(f" PAYLOAD:          {payload!r} (Hex: {payload.hex()})")
    print(f" TARGET PROMPT:    '{target_prompt}'")
    print(f" INTERVAL:         {interval}s")
    print("=================================================================")
    print("[!] HAMMERING DEVICE NOW... POWER ON THE DUT\n")

    while not trigger_found_event.is_set():
        ser.write(payload)
        time.sleep(interval)

    if interactive_baud != baud:
        ser.reset_output_buffer()
        ser.baudrate = interactive_baud

    run_interactive_vt100(ser, stop_event, target_prompt, dump_queue)

    stop_event.set()
    time.sleep(0.1)
    ser.close()
    print("\n[+] Serial session closed.")


if __name__ == "__main__":
    main()