# The Genesis Order | Money Cheat

Money Cheat Script for The Genesis Order

![image](https://github.com/user-attachments/assets/a0b82308-c03d-42d0-8a00-412ba8b48759)

## Overview

This script allows you to modify the money value in RPG save files for the game [The Genesis Order](https://store.steampowered.com/app/2553870/The_Genesis_Order/). It reads the save files, decodes and decompresses them, modifies the money value, and then re-encodes and compresses the save files.

## Requirements

- Python 3.8 or higher
- Windows operating system
- Save File Path: `C:\Users\<username>\AppData\Local\User Data\`
- `autopep8` for code formatting (optional)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/the-genesis-order-money-cheat.git
   cd the-genesis-order-money-cheat
   ```

## Usage

You can run the script in either GUI mode (default) or CLI mode.

### GUI Mode (default)

1. Run the script:
   ```sh
   python tgo_money_cheat.py
   ```
2. Follow the graphical prompts:
   - Select a save file from the list of available save files.
   - Enter the current money value in the save file (for searching)
   - Enter the new money value you want to set in the save file.

### CLI Mode

1. Run the script with the `--cli` flag:
   ```sh
   python tgo_money_cheat.py --cli
   ```
2. Follow the command-line prompts:
   - Select a save file by entering its number.
   - Enter the current money value in the save file (for searching)
   - Enter the new money value you want to set in the save file.

3. The script will create a backup of the original save file and create a new save file with the modified money value.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/nat236919/the-genesis-order-money-cheat/blob/main/LICENSE) file for details.
