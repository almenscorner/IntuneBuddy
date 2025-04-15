import json

from unittest.mock import patch, mock_open
from IntuneBuddy.config import (
    CONFIG_FILE,
    load_config,
    save_config,
    config_file_exists,
    get_user_emoji,
    get_user_name,
    set_user_emoji,
    set_user_name,
    get_user_color,
    set_user_color,
    handle_question,
)


def test_load_config():
    # Test loading a valid config file
    config_data = {
        "user_emoji": "😊",
        "user_name": "Zoey",
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(config_data))):
        loaded_data = load_config()
        assert loaded_data == config_data
        assert loaded_data["user_emoji"] == "😊"


def test_load_config_non_existent():
    # Test loading a non-existent config file
    with patch("builtins.open", side_effect=FileNotFoundError):
        loaded_data = load_config()
        assert loaded_data == {}


def test_load_config_corrupted():
    # Test loading a corrupted config file
    with patch("builtins.open", mock_open(read_data="invalid_json")):
        loaded_data = load_config()
        assert loaded_data == {}


def test_save_config():
    # Test saving config data
    config_data = {
        "user_emoji": "😊",
        "user_name": "Zoey",
    }
    with patch("builtins.open", mock_open()) as mocked_file:
        with patch("json.dump") as mock_dump:
            save_config(config_data)
            mocked_file.assert_called_once_with(CONFIG_FILE, "w")
            mock_dump.assert_called_once_with(config_data, mocked_file(), indent=4)


def test_config_file_exists():
    # Test when config file exists
    with patch("os.path.exists", return_value=True):
        assert config_file_exists() is True

    # Test when config file does not exist
    with patch("os.path.exists", return_value=False):
        assert config_file_exists() is False


def test_get_user_emoji():
    # Test getting user emoji from config
    config_data = {
        "user_emoji": "😊",
        "user_name": "Zoey",
    }
    with patch("IntuneBuddy.config.load_config", return_value=config_data):
        emoji = get_user_emoji()
        assert emoji == "😊"


def test_get_user_name():
    # Test getting user name from config
    config_data = {
        "user_emoji": "😊",
        "user_name": "Zoey",
    }
    with patch("IntuneBuddy.config.load_config", return_value=config_data):
        name = get_user_name()
        assert name == "Zoey"


def test_set_user_emoji():
    # Test setting user emoji
    with patch("builtins.input", return_value="😊"):
        emoji = set_user_emoji()
        assert emoji == "😊"

    # Test setting user emoji with empty input
    with patch("builtins.input", return_value=""):
        emoji = set_user_emoji()
        assert emoji == "🧑"


def test_set_user_name():
    # Test setting user name
    with patch("builtins.input", return_value="Zoey"):
        name = set_user_name()
        assert name == "Zoey"

    # Test setting user name with empty input
    with patch("builtins.input", return_value=""):
        name = set_user_name()
        assert name == "You"


def test_get_user_color():
    # Test getting user color from config
    config_data = {
        "user_emoji": "😊",
        "user_name": "Zoey",
        "user_color": "blue",
    }
    with patch("IntuneBuddy.config.load_config", return_value=config_data):
        color = get_user_color()
        assert color == "blue"


def test_set_user_color():
    # Test setting user color
    with patch("builtins.input", return_value="blue"):
        color = set_user_color()
        assert color == "blue"

    # Test setting user color with empty input
    with patch("builtins.input", return_value=""):
        color = set_user_color()
        assert color == "yellow"


def test_clear_config():
    # Test clearing config
    with patch("os.path.exists", return_value=True):
        with patch("os.remove") as mocked_remove:
            handle_question("clear config", "🤖 Buddy:", "You", "😊", "yellow")
            mocked_remove.assert_called_once_with(CONFIG_FILE)


def test_clear_config_file_not_exists():
    # Test clearing config when file does not exist
    with patch("os.path.exists", return_value=False):
        with patch("os.remove") as mocked_remove:
            handle_question("clear config", "🤖 Buddy:", "You", "😊", "yellow")
            mocked_remove.assert_not_called()


def test_handle_question_set_emoji():
    # Test setting emoji
    with patch("builtins.input", return_value="😊"):
        name, emoji, color = handle_question(
            "set emoji", "🤖 Buddy:", "You", "😊", "yellow"
        )
        assert ("You", "😊", "yellow") == (name, emoji, color)


def test_handle_question_set_name():
    # Test setting name
    with patch("builtins.input", return_value="Zoey"):
        name, emoji, color = handle_question(
            "set name", "🤖 Buddy:", "You", "😊", "yellow"
        )
        assert ("Zoey", "😊", "yellow") == (name, emoji, color)


def test_handle_question_set_color():
    # Test setting color
    with patch("builtins.input", return_value="blue"):
        name, emoji, color = handle_question(
            "set color", "🤖 Buddy:", "You", "😊", "yellow"
        )
        assert ("You", "😊", "blue") == (name, emoji, color)


def test_show_config():
    # Test showing config
    config_data = {
        "user_emoji": "😊",
        "user_name": "Zoey",
        "user_color": "blue",
    }
    with patch("IntuneBuddy.config.load_config", return_value=config_data):
        name, emoji, color = handle_question(
            "show config", "🤖 Buddy:", "Zoey", "😊", "blue"
        )
        assert ("Zoey", "😊", "blue") == (name, emoji, color)


def test_config_help():
    # Test showing config help
    config_data = {
        "user_emoji": "😊",
        "user_name": "Zoey",
        "user_color": "blue",
    }
    with patch("IntuneBuddy.config.load_config", return_value=config_data):
        name, emoji, color = handle_question(
            "config help", "🤖 Buddy:", "Zoey", "😊", "blue"
        )
        assert ("Zoey", "😊", "blue") == (name, emoji, color)
