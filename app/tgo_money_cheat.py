import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from services.lzstring import LZString

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TGOMoneyCheat:
    """
    A class to modify the money value in RPG save files for 'The Genesis Order' game.
    """
    
    def __init__(self):
        """
        Initializes the TGOMoneyCheat class with default values.
        """
        self.save_file_dir = Path.home() / 'AppData' / 'Local' / 'User Data'
        self.save_files: List[str] = []
        self.temp_file_name = 'temp_save_file.json'
        self.lz = LZString()
        self.is_money_modified = False
    
    def _get_rpg_save_files(self) -> None:
        """
        Retrieves the list of RPG save files from the save file directory.
        """
        self.save_files = [
            file for file in self.save_file_dir.iterdir()
            if file.name.startswith('DefaultTGOfile') and file.name.endswith('.rpgsave')
        ]
    
    def _read_save_file(self, save_file: Path) -> str:
        """
        Reads the content of a save file.

        Args:
            save_file (Path): The path of the save file to read.

        Returns:
            str: The content of the save file.
        """
        with save_file.open('r') as f:
            return f.read()
    
    def _decode_save_file_content(self, save_file_content: str) -> Dict[str, Any]:
        """
        Decodes the content of a save file from base64 and decompresses it.

        Args:
            save_file_content (str): The base64 encoded content of the save file.

        Returns:
            Dict[str, Any]: The decoded and decompressed content of the save file.
        """
        return json.loads(self.lz.decompressFromBase64(save_file_content))
    
    def _encode_json_to_save_file_content(self, json_content: Dict[str, Any]) -> str:
        """
        Encodes and compresses JSON content to base64.

        Args:
            json_content (Dict[str, Any]): The JSON content to encode.

        Returns:
            str: The base64 encoded and compressed content.
        """
        return self.lz.compressToBase64(json.dumps(json_content))
    
    def _save_temp_save_file(self, save_file_content: Dict[str, Any]) -> None:
        """
        Saves the modified save file content to a temporary file.

        Args:
            save_file_content (Dict[str, Any]): The modified save file content.
        """
        logging.info('Saving temporary save file...')
        temp_save_path = self.save_file_dir / self.temp_file_name
        with temp_save_path.open('w') as f:
            json.dump(save_file_content, f, indent=4, sort_keys=True)
        logging.info('Temporary save file saved.')
    
    def _create_new_save_file_from_temp(self, save_file_num: int) -> None:
        """
        Creates a new save file from the temporary file and backs up the original save file.

        Args:
            save_file_num (int): The number of the save file to replace.
        """
        logging.info('Backing up original save file...')
        original_save_file = self.save_file_dir / self.save_files[save_file_num - 1]
        backup_save_file = original_save_file.with_suffix('.bak')
        
        logging.info('Creating new save file...')
        temp_save_path = self.save_file_dir / self.temp_file_name
        with temp_save_path.open('r') as f:
            temp_save_file = json.load(f)
        encoded_save_file = self._encode_json_to_save_file_content(temp_save_file)
        original_save_file.rename(backup_save_file)
        with original_save_file.open('w') as f:
            f.write(encoded_save_file)
        
        logging.info('New save file created.')
    
    def _clean_temp_save_file(self) -> None:
        """
        Deletes the temporary save file.
        """
        logging.info('Cleaning up temporary save file...')
        temp_save_path = self.save_file_dir / self.temp_file_name
        temp_save_path.unlink()
        logging.info('Temporary save file deleted.')
    
    def _select_save_file(self) -> int:
        """
        Prompts the user to select a save file from the list of available save files.

        Returns:
            int: The number of the selected save file.

        Raises:
            ValueError: If the selected save file number is invalid.
        """
        for i, file in enumerate(self.save_files):
            logging.info(f'{i + 1}. {file.name}')
        
        while True:
            try:
                save_file_num = int(input('Select a save file (number): '))
                if 1 <= save_file_num <= len(self.save_files):
                    return save_file_num
                else:
                    logging.error('Invalid save file number! Please try again.')
            except ValueError:
                logging.error('Invalid input! Please enter a number.')
    
    def _modify_save_file(self, decoded_save_file: Dict[str, Any], current_money: int, new_money: int) -> None:
        """
        Modifies the money value in the decoded save file content.

        Args:
            decoded_save_file (Dict[str, Any]): The decoded save file content.
            current_money (int): The current money value in the save file.
            new_money (int): The new money value to set in the save file.
        """
        variables = decoded_save_file.get('variables')
        game_variables = variables['_data']['@a']
        
        for idx, game_var in enumerate(game_variables):
            if isinstance(game_var, int) and game_var == current_money:
                game_variables[idx] = new_money
                self.is_money_modified = True
                break

    def _get_user_input(self, prompt: str) -> int:
        """
        Prompts the user for input and validates it as an integer.

        Args:
            prompt (str): The prompt message to display.

        Returns:
            int: The validated integer input from the user.
        """
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                logging.error('Invalid input! Please enter a number.')

    def start(self) -> None:
        """
        Starts the process of modifying the money value in the save file.
        """
        self._get_rpg_save_files()
        
        if not self.save_files:
            logging.error('No save files found!')
            return
        
        logging.info('Save files found')
        
        try:
            save_file_num = self._select_save_file()
        except ValueError as e:
            logging.error(e)
            return
        
        selected_save_file = self._read_save_file(self.save_files[save_file_num - 1])
        decoded_save_file = self._decode_save_file_content(selected_save_file)
        
        current_money = self._get_user_input('Enter the current money value in the save file: ')
        new_money = self._get_user_input('Enter the new money value you want to set: ')
        
        self._modify_save_file(decoded_save_file, current_money, new_money)
        if not self.is_money_modified:
            logging.error('Money value not found in the save file! No changes made.')
            return
        
        self._save_temp_save_file(decoded_save_file)
        self._create_new_save_file_from_temp(save_file_num)
        self._clean_temp_save_file()
        logging.info('Money value successfully modified.')


if __name__ == '__main__':
    tgo = TGOMoneyCheat()
    tgo.start()
