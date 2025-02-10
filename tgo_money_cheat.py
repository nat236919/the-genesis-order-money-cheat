import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class LZString:
    """
    A class for compressing and decompressing strings using LZ-based compression.
    """

    key_str_base_64: str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    base_reversed_dic: dict = {}

    @staticmethod
    def compress_to_base_64(uncompressed: str) -> str:
        """
        Compress a string to Base64 format.

        Args:
            uncompressed (str): The string to compress.

        Returns:
            str: The compressed string in Base64 format.
        """
        if uncompressed is None:
            return ''
        res = LZString._compress(uncompressed, 6, lambda a: LZString.key_str_base_64[a])
        # To produce valid Base64
        end = len(res) % 4
        if end > 0:
            res += '=' * (4 - end)
        return res

    @staticmethod
    def decompress_to_base_64(compressed: str) -> str:
        """
        Decompress a Base64 formatted string.

        Args:
            compressed (str): The compressed string in Base64 format.

        Returns:
            str: The decompressed string.
        """
        if compressed is None:
            return ''
        if compressed == '':
            return None
        return LZString._decompress(len(compressed), 32, lambda index: LZString.get_base_value(LZString.key_str_base_64, compressed[index]))

    @staticmethod
    def get_base_value(alphabet: str, character: str) -> int:
        """
        Get the base value of a character in the given alphabet.

        Args:
            alphabet (str): The alphabet string.
            character (str): The character to find the base value for.

        Returns:
            int: The base value of the character.
        """
        if alphabet not in LZString.base_reversed_dic:
            LZString.base_reversed_dic[alphabet] = {}
        for i in range(len(alphabet)):
            LZString.base_reversed_dic[alphabet][alphabet[i]] = i
        return LZString.base_reversed_dic[alphabet][character]

    @staticmethod
    def _compress(uncompressed: str, bits_per_char: int, get_char_from_int: callable) -> str:
        """
        Compress a string using LZ-based compression.

        Args:
            uncompressed (str): The string to compress.
            bits_per_char (int): The number of bits per character.
            get_char_from_int (function): Function to get character from integer.

        Returns:
            str: The compressed string.
        """
        if uncompressed is None:
            return ''

        context_dictionary: dict = {}
        context_dictionary_to_create: dict = {}
        context_c: str = ''
        context_wc: str = ''
        context_w: str = ''
        context_enlarge_in: int = 2  # Compensate for the first entry which should not count
        context_dict_size: int = 3
        context_num_bits: int = 2
        context_data: list = []
        context_data_val: int = 0
        context_data_position: int = 0

        for ii in range(len(uncompressed)):
            if isinstance(uncompressed, bytes):
                context_c = chr(uncompressed[ii])
            else:
                context_c = uncompressed[ii]
            if context_c not in context_dictionary:
                context_dictionary[context_c] = context_dict_size
                context_dict_size += 1
                context_dictionary_to_create[context_c] = True

            context_wc = context_w + context_c
            if context_wc in context_dictionary:
                context_w = context_wc
            else:
                if context_w in context_dictionary_to_create:
                    if ord(context_w[0]) < 256:
                        for i in range(context_num_bits):
                            context_data_val = (context_data_val << 1)
                            if context_data_position == bits_per_char - 1:
                                context_data_position = 0
                                context_data.append(get_char_from_int(context_data_val))
                                context_data_val = 0
                            else:
                                context_data_position += 1
                        value = ord(context_w[0])
                        for i in range(8):
                            context_data_val = (context_data_val << 1) | (value & 1)
                            if context_data_position == bits_per_char - 1:
                                context_data_position = 0
                                context_data.append(get_char_from_int(context_data_val))
                                context_data_val = 0
                            else:
                                context_data_position += 1
                            value = value >> 1

                    else:
                        value = 1
                        for i in range(context_num_bits):
                            context_data_val = (context_data_val << 1) | value
                            if context_data_position == bits_per_char - 1:
                                context_data_position = 0
                                context_data.append(get_char_from_int(context_data_val))
                                context_data_val = 0
                            else:
                                context_data_position += 1
                            value = 0
                        value = ord(context_w[0])
                        for i in range(16):
                            context_data_val = (context_data_val << 1) | (value & 1)
                            if context_data_position == bits_per_char - 1:
                                context_data_position = 0
                                context_data.append(get_char_from_int(context_data_val))
                                context_data_val = 0
                            else:
                                context_data_position += 1
                            value = value >> 1
                    context_enlarge_in -= 1
                    if context_enlarge_in == 0:
                        context_enlarge_in = pow(2, context_num_bits)
                        context_num_bits += 1
                    del context_dictionary_to_create[context_w]
                else:
                    value = context_dictionary[context_w]
                    for i in range(context_num_bits):
                        context_data_val = (context_data_val << 1) | (value & 1)
                        if context_data_position == bits_per_char - 1:
                            context_data_position = 0
                            context_data.append(get_char_from_int(context_data_val))
                            context_data_val = 0
                        else:
                            context_data_position += 1
                        value = value >> 1

                context_enlarge_in -= 1
                if context_enlarge_in == 0:
                    context_enlarge_in = pow(2, context_num_bits)
                    context_num_bits += 1

                # Add wc to the dictionary.
                context_dictionary[context_wc] = context_dict_size
                context_dict_size += 1
                context_w = str(context_c)

        # Output the code for w.
        if context_w != '':
            if context_w in context_dictionary_to_create:
                if ord(context_w[0]) < 256:
                    for i in range(context_num_bits):
                        context_data_val = (context_data_val << 1)
                        if context_data_position == bits_per_char - 1:
                            context_data_position = 0
                            context_data.append(get_char_from_int(context_data_val))
                            context_data_val = 0
                        else:
                            context_data_position += 1
                    value = ord(context_w[0])
                    for i in range(8):
                        context_data_val = (context_data_val << 1) | (value & 1)
                        if context_data_position == bits_per_char - 1:
                            context_data_position = 0
                            context_data.append(get_char_from_int(context_data_val))
                            context_data_val = 0
                        else:
                            context_data_position += 1
                        value = value >> 1
                else:
                    value = 1
                    for i in range(context_num_bits):
                        context_data_val = (context_data_val << 1) | value
                        if context_data_position == bits_per_char - 1:
                            context_data_position = 0
                            context_data.append(get_char_from_int(context_data_val))
                            context_data_val = 0
                        else:
                            context_data_position += 1
                        value = 0
                    value = ord(context_w[0])
                    for i in range(16):
                        context_data_val = (context_data_val << 1) | (value & 1)
                        if context_data_position == bits_per_char - 1:
                            context_data_position = 0
                            context_data.append(get_char_from_int(context_data_val))
                            context_data_val = 0
                        else:
                            context_data_position += 1
                        value = value >> 1
                context_enlarge_in -= 1
                if context_enlarge_in == 0:
                    context_enlarge_in = pow(2, context_num_bits)
                    context_num_bits += 1
                del context_dictionary_to_create[context_w]
            else:
                value = context_dictionary[context_w]
                for i in range(context_num_bits):
                    context_data_val = (context_data_val << 1) | (value & 1)
                    if context_data_position == bits_per_char - 1:
                        context_data_position = 0
                        context_data.append(get_char_from_int(context_data_val))
                        context_data_val = 0
                    else:
                        context_data_position += 1
                    value = value >> 1

        context_enlarge_in -= 1
        if context_enlarge_in == 0:
            context_enlarge_in = pow(2, context_num_bits)
            context_num_bits += 1

        # Mark the end of the stream
        value = 2
        for i in range(context_num_bits):
            context_data_val = (context_data_val << 1) | (value & 1)
            if context_data_position == bits_per_char - 1:
                context_data_position = 0
                context_data.append(get_char_from_int(context_data_val))
                context_data_val = 0
            else:
                context_data_position += 1
            value = value >> 1

        # Flush the last char
        while True:
            context_data_val = (context_data_val << 1)
            if context_data_position == bits_per_char - 1:
                context_data.append(get_char_from_int(context_data_val))
                break
            else:
                context_data_position += 1

        return ''.join(context_data)

    @staticmethod
    def _decompress(length: int, reset_value: int, get_next_value: callable) -> str:
        """
        Decompress a string using LZ-based decompression.

        Args:
            length (int): The length of the compressed string.
            reset_value (int): The reset value.
            get_next_value (function): Function to get the next value.

        Returns:
            str: The decompressed string.
        """
        dictionary: dict = {}
        enlarge_in: int = 4
        dict_size: int = 4
        num_bits: int = 3
        entry: str = ''
        result: list = []

        data = LZString.Object(
            val=get_next_value(0),
            position=reset_value,
            index=1
        )

        for i in range(3):
            dictionary[i] = i

        bits: int = 0
        maxpower: int = pow(2, 2)
        power: int = 1

        while power != maxpower:
            resb = data.val & data.position
            data.position >>= 1
            if data.position == 0:
                data.position = reset_value
                data.val = get_next_value(data.index)
                data.index += 1

            bits |= power if resb > 0 else 0
            power <<= 1

        next = bits
        if next == 0:
            bits = 0
            maxpower = pow(2, 8)
            power = 1
            while power != maxpower:
                resb = data.val & data.position
                data.position >>= 1
                if data.position == 0:
                    data.position = reset_value
                    data.val = get_next_value(data.index)
                    data.index += 1
                bits |= power if resb > 0 else 0
                power <<= 1
            c = chr(bits)
        elif next == 1:
            bits = 0
            maxpower = pow(2, 16)
            power = 1
            while power != maxpower:
                resb = data.val & data.position
                data.position >>= 1
                if data.position == 0:
                    data.position = reset_value
                    data.val = get_next_value(data.index)
                    data.index += 1
                bits |= power if resb > 0 else 0
                power <<= 1
            c = chr(bits)
        elif next == 2:
            return ''

        dictionary[3] = c
        w = c
        result.append(c)
        counter = 0
        while True:
            counter += 1
            if data.index > length:
                return ''

            bits = 0
            maxpower = pow(2, num_bits)
            power = 1
            while power != maxpower:
                resb = data.val & data.position
                data.position >>= 1
                if data.position == 0:
                    data.position = reset_value
                    data.val = get_next_value(data.index)
                    data.index += 1
                bits |= power if resb > 0 else 0
                power <<= 1

            c = bits
            if c == 0:
                bits = 0
                maxpower = pow(2, 8)
                power = 1
                while power != maxpower:
                    resb = data.val & data.position
                    data.position >>= 1
                    if data.position == 0:
                        data.position = reset_value
                        data.val = get_next_value(data.index)
                        data.index += 1
                    bits |= power if resb > 0 else 0
                    power <<= 1

                dictionary[dict_size] = chr(bits)
                dict_size += 1
                c = dict_size - 1
                enlarge_in -= 1
            elif c == 1:
                bits = 0
                maxpower = pow(2, 16)
                power = 1
                while power != maxpower:
                    resb = data.val & data.position
                    data.position >>= 1
                    if data.position == 0:
                        data.position = reset_value
                        data.val = get_next_value(data.index)
                        data.index += 1
                    bits |= power if resb > 0 else 0
                    power <<= 1
                dictionary[dict_size] = chr(bits)
                dict_size += 1
                c = dict_size - 1
                enlarge_in -= 1
            elif c == 2:
                return ''.join(result)

            if enlarge_in == 0:
                enlarge_in = pow(2, num_bits)
                num_bits += 1

            if c in dictionary:
                entry = dictionary[c]
            else:
                if c == dict_size:
                    entry = w + w[0]
                else:
                    return None
            result.append(entry)

            # Add w+entry[0] to the dictionary.
            dictionary[dict_size] = w + entry[0]
            dict_size += 1
            enlarge_in -= 1

            w = entry
            if enlarge_in == 0:
                enlarge_in = pow(2, num_bits)
                num_bits += 1

    class Object:
        """
        A helper class to store values for decompression.
        """
        def __init__(self, **kwargs):
            """
            Initialize the Object with given keyword arguments.

            Args:
                **kwargs: Arbitrary keyword arguments.
            """
            for k, v in kwargs.items():
                setattr(self, k, v)


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
        return json.loads(self.lz.decompress_to_base_64(save_file_content))
    
    def _encode_json_to_save_file_content(self, json_content: Dict[str, Any]) -> str:
        """
        Encodes and compresses JSON content to base64.

        Args:
            json_content (Dict[str, Any]): The JSON content to encode.

        Returns:
            str: The base64 encoded and compressed content.
        """
        return self.lz.compress_to_base_64(json.dumps(json_content))
    
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
