import pytest
import json
from pathlib import Path
from tgo_money_cheat import TGOMoneyCheat, LZString


class DummyLZString(LZString):
    """A dummy LZString for bypassing actual compression in tests."""
    @staticmethod
    def compress_to_base_64(uncompressed: str) -> str:
        return uncompressed

    @staticmethod
    def decompress_to_base_64(compressed: str) -> str:
        return compressed


def make_fake_save_file(current_money=1000, slot=0):
    # Simulate the structure expected by TGOMoneyCheat
    data = {
        "variables": {
            "_data": {
                "@a": [0]*slot + [current_money] + [0]*(99-slot)
            }
        }
    }
    return json.dumps(data)


@pytest.fixture
def cheat(tmp_path, monkeypatch):
    # Setup a fake save file directory
    save_dir = tmp_path / "User Data"
    save_dir.mkdir(parents=True)
    save_file = save_dir / "DefaultTGOfile1.rpgsave"
    save_file.write_text(make_fake_save_file(1000, slot=5))
    # Patch home directory
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    # Patch LZString to dummy
    cheat = TGOMoneyCheat(use_gui=False)
    cheat.lz = DummyLZString()
    cheat.save_file_dir = save_dir
    cheat._get_rpg_save_files()
    return cheat


def test_get_rpg_save_files(cheat):
    assert len(cheat.save_files) == 1
    assert cheat.save_files[0].name.startswith("DefaultTGOfile")


def test_decode_and_encode_save_file_content(cheat):
    original = make_fake_save_file(1234, slot=2)
    decoded = cheat._decode_save_file_content(original)
    assert decoded["variables"]["_data"]["@a"][2] == 1234
    encoded = cheat._encode_json_to_save_file_content(decoded)
    assert json.loads(encoded)["variables"]["_data"]["@a"][2] == 1234


def test_modify_save_file(cheat):
    content = make_fake_save_file(5000, slot=10)
    decoded = cheat._decode_save_file_content(content)
    cheat._modify_save_file(decoded, 5000, 9999)
    arr = decoded["variables"]["_data"]["@a"]
    assert 9999 in arr
    assert arr.count(9999) == 1
    assert cheat.is_money_modified


def test_modify_save_file_not_found(cheat):
    content = make_fake_save_file(123, slot=0)
    decoded = cheat._decode_save_file_content(content)
    cheat._modify_save_file(decoded, 999, 888)
    assert not cheat.is_money_modified


def test_save_and_create_new_save_file(tmp_path, monkeypatch):
    save_dir = tmp_path / "User Data"
    save_dir.mkdir(parents=True)
    save_file = save_dir / "DefaultTGOfile1.rpgsave"
    save_file.write_text("dummy")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    cheat = TGOMoneyCheat(use_gui=False)
    cheat.lz = DummyLZString()
    cheat.save_file_dir = save_dir
    cheat.save_files = [save_file]
    data = {"foo": "bar"}
    cheat._save_temp_save_file(data)
    assert (save_dir / cheat.temp_file_name).exists()
    cheat._create_new_save_file_from_temp(1)
    assert (save_dir / "DefaultTGOfile1.bak").exists()
    assert (save_dir / "DefaultTGOfile1.rpgsave").exists()
    cheat._clean_temp_save_file()
    assert not (save_dir / cheat.temp_file_name).exists()
