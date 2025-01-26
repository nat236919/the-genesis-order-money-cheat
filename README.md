# The Genesis Order | Money Cheat

Money Cheat Script for The Genesis Order

## Overview

This script allows you to modify the money value in RPG save files for the game [The Genesis Order](https://store.steampowered.com/app/2553870/The_Genesis_Order/) . It reads the save files, decodes and decompresses them, modifies the money value, and then re-encodes and compresses the save files.

## Requirements

- Python 3.8 or higher
- `autopep8` for code formatting (optional)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/the-genesis-order-money-cheat.git
    cd the-genesis-order-money-cheat
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the script:
    ```sh
    python app/tgo_money_cheat.py
    ```

2. Follow the prompts:
    - Select a save file from the list of available save files.
    - Enter the current money value in the save file (for searching)
    - Enter the new money value you want to set in the save file.

3. The script will create a backup of the original save file and create a new save file with the modified money value.

## License

This project is licensed under the MIT License - see the [LICENSE](http://_vscodecontentref_/1) file for details.