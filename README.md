# U-Boot Bootloader shell tool

A Python utility for embedded device security auditing, firmware extraction, and hardware debugging. This tool continuously sends trigger payloads over serial to interrupt boot sequences (such as MediaTek MT7620 or similar SoCs) and enter the U-BOOT shell (if available), handles baud rate transitions, and seamlessly bridges into an interactive VT100 terminal or command menu simplifying a few tasks.

---

## Features

- **Boot Flood Triggering**: Continuously hammers the Target Device Under Test (DUT) over a serial interface during cold/warm reboots until the bootloader prompt is caught.
- **Escape Sequence & Custom Payload Support**: Supports custom payloads with non-printable ASCII and escape sequences (e.g., `\\r`, `\\n`, `\\x03` for `Ctrl+C`).
- **Interactive VT100 Terminal Mode**: Multi-platform (Linux/macOS raw termios & Windows `msvcrt`) VT100 serial console session.
- **On-the-Fly Command Menu**: Easily toggle out of the live terminal (`Ctrl+B`) to run predefined functions, dump memory, or issue resets.
- **Automated Memory Dumping**: Flash/RAM dumping via `md.b` command sequence streaming directly into local output files.
- **Baud Rate Switching**: Dynamically switch from a high-speed boot flood baud rate to a different operational interactive baud rate once the prompt is hit.

---

## Requirements

- Python 3.6+
- [`pyserial`](https://pypi.org/project/pyserial/)

Install dependencies via `pip`:

```bash
pip install pyserial
```

## Usage
### Syntax
```Bash
python uboot_tool.py [PORT] [BAUD] [TRIGGER_PAYLOAD] [TARGET_PROMPT] [INTERVAL] [INTERACTIVE_BAUD]
```
Positional Arguments
| Argument | Default | Description |
| --- | --- | --- |
| PORT | /dev/ttyUSB0 | Serial port connected to the device UART.
| BAUD Rate (bps) | 115200 | Baud rate for the initial boot-hammering phase.
| TRIGGER_PAYLOAD | "4" | Payload sent repeatedly during boot. Supports escape sequences (\\r, \\n, \\x03, \\x1b).
| TARGET_PROMPT | "MT7620 #" | Substring or prompt pattern to wait for to confirm bootloader entry.
| INTERVAL | 0.05 | Delay in seconds between hammering payloads (e.g., 0.05 = 20 Hz).
| INTERACTIVE_BAUD | [BAUD] | Optional secondary baud rate to switch to after catching the target prompt.

### Examples
1. Basic U-Boot Interrupt
Send character '4' at 115200 baud every 50ms until the prompt MT7620 # appears:

```Bash
python uboot_tool.py /dev/ttyUSB0 115200 "4" "MT7620 #" 0.05
```

2. Triggering with Carriage Return / Line Feed (\r\n)
Pass escape sequences in quotes to interrupt targets requiring newlines:

```Bash
python uboot_tool.py /dev/ttyUSB0 57600 "4\\r\\n" "MT7620 #" 0.05
```

3. Break Sequence via Ctrl+C (\x03)
Send ASCII End-of-Text (0x03) to break standard boot timers:

```Bash
python uboot_tool.py /dev/ttyUSB0 115200 "\\x03" "U-Boot>" 0.02
```

4. Dynamic Baud Rate Transition
Hammer at 57,600 baud during boot, then transition the serial session to 115,200 baud once caught:

```Bash
python uboot_tool.py /dev/ttyUSB0 57600 "4" "MT7620 #" 0.05 115200
```

### In-Session Keyboard Shortcuts
Once the trigger prompt is detected, the script drops into interactive VT100 terminal mode,
However, use the following escape key shortcuts to get the [U-Boot Automation Menu](#u-boot-automation-menu-options) or just end the script cleanly:

Ctrl+B (\x02): Pause live terminal and open the interactive U-Boot Automation Menu.

Ctrl+] (\x1d): Instantly close the serial connection and cleanly exit the script.

## U-Boot Automation Menu Options
Pressing Ctrl+B in terminal mode opens the automation menu:

1. Execute 'printenv': Prints environment variables.

2. Dump Firmware/Memory to File (md.b): Prompts for start address, dump size, and output path to execute a memory hex dump over serial and write raw output to disk.

3. Reset Device ('reset'): Issues the reset command and exits.

4. Return to Interactive Terminal: Re-enters standard VT100 interactive console mode.

5. Exit Script: Closes ports and terminates session.

## License
This project is licensed under the MIT License.

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

with open("README.md", "w", encoding="utf-8") as f:
f.write(readme_content)

print("README.md successfully written.")


```text?code_stdout&code_event_index=1
README.md successfully written.

Your Markdown file is ready:

MD-ikon
README
 MD 
Åben
README.md Preview
Markdown
# U-Boot Bootloader Interactive & Automation Tool

A Python utility for embedded device security auditing, firmware extraction, and hardware debugging. This tool continuously sends trigger payloads over serial to interrupt boot sequences (such as MediaTek MT7620 or similar SoCs), handles baud rate transitions, and seamlessly bridges into an interactive VT100 terminal or automated command menu.

---

## Features

- **Boot Flood Triggering**: Continuously hammers the Target Device Under Test (DUT) over a serial interface during cold/warm reboots until the bootloader prompt is caught.
- **Escape Sequence & Custom Payload Support**: Supports custom payloads with non-printable ASCII and escape sequences (e.g., `\r`, `\n`, `\x03` for `Ctrl+C`).
- **Interactive VT100 Terminal Mode**: Multi-platform (Linux/macOS raw termios & Windows `msvcrt`) VT100 serial console session.
- **On-the-Fly Command Menu**: Easily toggle out of the live terminal (`Ctrl+B`) to run predefined functions, dump memory, or issue resets.
- **Automated Memory Dumping**: Flash/RAM dumping via `md.b` command sequence streaming directly into local output files.
- **Baud Rate Switching**: Dynamically switch from a high-speed boot flood baud rate to a different operational interactive baud rate once the prompt is hit.

---

## Requirements

- Python 3.6+
- [`pyserial`](https://pypi.org/project/pyserial/)

Install dependencies via `pip`:

```bash
pip install pyserial
Usage
Syntax
Bash
python uboot_tool.py [PORT] [BAUD] [TRIGGER_PAYLOAD] [TARGET_PROMPT] [INTERVAL] [INTERACTIVE_BAUD]
Positional Arguments
Argument	Default	Description
PORT	/dev/ttyUSB0	Serial port connected to the device UART.
BAUD	115200	Baud rate for the initial boot-hammering phase.
TRIGGER_PAYLOAD	"4"	Payload sent repeatedly during boot. Supports escape sequences (\r, \n, \x03, \x1b).
TARGET_PROMPT	"MT7620 #"	Substring or prompt pattern to wait for to confirm bootloader entry.
INTERVAL	0.05	Delay in seconds between hammering payloads (e.g., 0.05 = 20 Hz).
INTERACTIVE_BAUD	[BAUD]	Optional secondary baud rate to switch to after catching the target prompt.
Examples
1. Basic U-Boot Interrupt
Send character '4' at 115200 baud every 50ms until the prompt MT7620 # appears:

Bash
python uboot_tool.py /dev/ttyUSB0 115200 "4" "MT7620 #" 0.05
2. Triggering with Carriage Return / Line Feed (\r\n)
Pass escape sequences in quotes to interrupt targets requiring newlines:

Bash
python uboot_tool.py /dev/ttyUSB0 57600 "4\r\n" "MT7620 #" 0.05
3. Break Sequence via Ctrl+C (\x03)
Send ASCII End-of-Text (0x03) to break standard boot timers:

Bash
python uboot_tool.py /dev/ttyUSB0 115200 "\x03" "U-Boot>" 0.02
4. Dynamic Baud Rate Transition
Hammer at 57,600 baud during boot, then transition the serial session to 115,200 baud once caught:

Bash
python uboot_tool.py /dev/ttyUSB0 57600 "4" "MT7620 #" 0.05 115200
In-Session Keyboard Shortcuts
Once the trigger prompt is detected, the script drops into interactive VT100 terminal mode. Use the following escape key shortcuts:

Ctrl+B (\x02): Pause live terminal and open the interactive U-Boot Automation Menu.

Ctrl+] (\x1d): Instantly close the serial connection and cleanly exit the script.

U-Boot Automation Menu Options
Pressing Ctrl+B in terminal mode opens the automation menu:

Execute 'printenv': Prints environment variables.

Dump Firmware/Memory to File (md.b): Prompts for start address, dump size, and output path to execute a memory hex dump over serial and write raw output to disk.

Reset Device ('reset'): Issues the reset command and exits.

Return to Interactive Terminal: Re-enters standard VT100 interactive console mode.

Cleanly Exit Script: Closes ports and terminates session.

License
This project is licensed under the MIT License.




Gemini er et AI-produkt og kan begå fejl, også om personer. Dit privatliv og GeminiÅbnes i et nyt vindue

# U-Boot Bootloader Interactive & Automation Tool

A Python utility for embedded device security auditing, firmware extraction, and hardware debugging. This tool continuously sends trigger payloads over serial to interrupt boot sequences (such as MediaTek MT7620 or similar SoCs), handles baud rate transitions, and seamlessly bridges into an interactive VT100 terminal or automated command menu.

---

## Features

- **Boot Flood Triggering**: Continuously hammers the Target Device Under Test (DUT) over a serial interface during cold/warm reboots until the bootloader prompt is caught.
- **Escape Sequence & Custom Payload Support**: Supports custom payloads with non-printable ASCII and escape sequences (e.g., `\r`, `\n`, `\x03` for `Ctrl+C`).
- **Interactive VT100 Terminal Mode**: Multi-platform (Linux/macOS raw termios & Windows `msvcrt`) VT100 serial console session.
- **On-the-Fly Command Menu**: Easily toggle out of the live terminal (`Ctrl+B`) to run predefined functions, dump memory, or issue resets.
- **Automated Memory Dumping**: Flash/RAM dumping via `md.b` command sequence streaming directly into local output files.
- **Baud Rate Switching**: Dynamically switch from a high-speed boot flood baud rate to a different operational interactive baud rate once the prompt is hit.

---

## Requirements

- Python 3.6+
- [`pyserial`](https://pypi.org/project/pyserial/)

Install dependencies via `pip`:

```bash
pip install pyserial
```

---

## Usage

### Syntax

```bash
python uboot_tool.py [PORT] [BAUD] [TRIGGER_PAYLOAD] [TARGET_PROMPT] [INTERVAL] [INTERACTIVE_BAUD]
```

### Positional Arguments

| Argument | Default | Description |
| :--- | :--- | :--- |
| `PORT` | `/dev/ttyUSB0` | Serial port connected to the device UART. |
| `BAUD Rate (bps)` | `115200` | Baud rate for the initial boot-hammering phase. |
| `TRIGGER_PAYLOAD` | `"4"` | Payload sent repeatedly during boot. Supports escape sequences (`\r`, `\n`, `\x03`, `\x1b`). |
| `TARGET_PROMPT` | `"MT7620 #"` | Substring or prompt pattern to wait for to confirm bootloader entry. |
| `INTERVAL` | `0.05` | Delay in seconds between hammering payloads (e.g., `0.05` = 20 Hz). |
| `INTERACTIVE_BAUD` | `[BAUD]` | Optional secondary baud rate to switch to after catching the target prompt. |

---

## Examples

### 1. Basic U-Boot Interrupt
Send character `'4'` at 115200 baud every 50ms until the prompt `MT7620 #` appears:

```bash
python uboot_tool.py /dev/ttyUSB0 115200 "4" "MT7620 #" 0.05
```

### 2. Triggering with Carriage Return / Line Feed (`
`)
Pass escape sequences in quotes to interrupt targets requiring newlines:

```bash
python uboot_tool.py /dev/ttyUSB0 57600 "4\r\n" "MT7620 #" 0.05
```

### 3. Break Sequence via `Ctrl+C` (` `)
Send ASCII End-of-Text (`0x03`) to break standard boot timers:

```bash
python uboot_tool.py /dev/ttyUSB0 115200 "\x03" "U-Boot>" 0.02
```

### 4. Dynamic Baud Rate Transition
Hammer at 57,600 baud during boot, then transition the serial session to 115,200 baud once caught:

```bash
python uboot_tool.py /dev/ttyUSB0 57600 "4" "MT7620 #" 0.05 115200
```

---

## In-Session Keyboard Shortcuts

Once the trigger prompt is detected, the script drops into interactive VT100 terminal mode. Use the following escape key shortcuts:

- **`Ctrl+B`** (` `): Pause live terminal and open the interactive **U-Boot Automation Menu**.
- **`Ctrl+]`** (` `): Instantly close the serial connection and cleanly exit the script.

---

## U-Boot Automation Menu Options

Pressing `Ctrl+B` in terminal mode opens the automation menu:

1. **Execute 'printenv'**: Prints environment variables.
2. **Dump Firmware/Memory to File (md.b)**: Prompts for start address, dump size, and output path to execute a memory hex dump over serial and write raw output to disk.
3. **Reset Device ('reset')**: Issues the `reset` command and exits.
4. **Return to Interactive Terminal**: Re-enters standard VT100 interactive console mode.
5. **Cleanly Exit Script**: Closes ports and terminates session.

---

## License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
