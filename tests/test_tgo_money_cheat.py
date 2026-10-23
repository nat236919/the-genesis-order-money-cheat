import pytest
import json
from pathlib import Path
from tgo_money_cheat import TGOMoneyCheat, LZString, MONEY_VARIABLE_ID


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


def test_get_current_money(cheat):
    decoded = cheat._decode_save_file_content(
        make_fake_save_file(310, slot=MONEY_VARIABLE_ID))
    assert cheat._get_current_money(decoded) == 310


def test_get_current_money_unset(cheat):
    decoded = cheat._decode_save_file_content(
        make_fake_save_file(None, slot=MONEY_VARIABLE_ID))
    assert cheat._get_current_money(decoded) == 0


def test_get_current_money_invalid_structure(cheat):
    assert cheat._get_current_money({"foo": "bar"}) is None


def test_modify_save_file(cheat):
    content = make_fake_save_file(5000, slot=MONEY_VARIABLE_ID)
    decoded = cheat._decode_save_file_content(content)
    cheat._modify_save_file(decoded, 9999)
    arr = decoded["variables"]["_data"]["@a"]
    assert arr[MONEY_VARIABLE_ID] == 9999
    assert arr.count(9999) == 1
    assert cheat.is_money_modified


def test_modify_save_file_does_not_touch_other_variables(cheat):
    # Another variable holding the same value as money must stay untouched
    content = make_fake_save_file(5000, slot=MONEY_VARIABLE_ID)
    decoded = cheat._decode_save_file_content(content)
    decoded["variables"]["_data"]["@a"][10] = 5000
    cheat._modify_save_file(decoded, 9999)
    assert decoded["variables"]["_data"]["@a"][10] == 5000


def test_modify_save_file_short_variables_list(cheat):
    decoded = {"variables": {"_data": {"@a": [None]}}}
    cheat._modify_save_file(decoded, 500)
    assert decoded["variables"]["_data"]["@a"][MONEY_VARIABLE_ID] == 500
    assert cheat.is_money_modified


def test_modify_save_file_invalid_structure(cheat):
    cheat._modify_save_file({"foo": "bar"}, 888)
    assert not cheat.is_money_modified


def test_save_files_sorted_numerically(tmp_path):
    for n in (10, 2, 1):
        (tmp_path / f"DefaultTGOfile{n}.rpgsave").write_text("x")
    cheat = TGOMoneyCheat(use_gui=False)
    cheat.save_file_dir = tmp_path
    cheat._get_rpg_save_files()
    assert [f.name for f in cheat.save_files] == [
        "DefaultTGOfile1.rpgsave", "DefaultTGOfile2.rpgsave", "DefaultTGOfile10.rpgsave"]


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

    # Running again must overwrite the existing backup instead of failing
    cheat._save_temp_save_file(data)
    cheat._create_new_save_file_from_temp(1)
    assert (save_dir / "DefaultTGOfile1.bak").exists()
