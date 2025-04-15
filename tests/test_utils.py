import subprocess
import pytest
from unittest.mock import patch, MagicMock

from IntuneBuddy.utils import (
    clean_output,
    ensure_ollama_installed,
    ensure_git_installed,
    ensure_model_installed,
    retry_chain_invoke,
    stop_models,
)


def test_clean_output_removes_think_tags():
    input_text = "<think>something</think> Hello world"
    assert clean_output(input_text) == "Hello world"


def test_clean_output_removes_greetings():
    input_text = "Hello! Here is your answer."
    assert clean_output(input_text) == "Here is your answer."


def test_clean_output_strips_whitespace():
    input_text = "   Hello.  "
    assert clean_output(input_text) == ""


def test_ensure_ollama_installed_installed():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock()
        ensure_ollama_installed()


def test_ollama_not_found():
    with patch("subprocess.run", side_effect=FileNotFoundError):
        with pytest.raises(SystemExit) as e:
            ensure_ollama_installed()
        assert e.value.code == 1


def test_ollama_fails():
    with patch(
        "subprocess.run", side_effect=subprocess.CalledProcessError(1, "ollama")
    ):
        with pytest.raises(SystemExit) as e:
            ensure_ollama_installed()
        assert e.value.code == 1


def test_ensure_git_installed_installed():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock()
        ensure_git_installed()


def test_git_not_found():
    with patch("subprocess.run", side_effect=FileNotFoundError):
        with pytest.raises(SystemExit) as e:
            ensure_git_installed()
        assert e.value.code == 1


def test_git_fails():
    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "git")):
        with pytest.raises(SystemExit) as e:
            ensure_git_installed()
        assert e.value.code == 1


def test_ensure_model_installed():
    model_name = "test_model"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=f"{model_name}\n")
        ensure_model_installed(model_name)


def test_model_not_installed():
    model_name = "test_model"
    with patch(
        "subprocess.run", side_effect=subprocess.CalledProcessError(1, "ollama")
    ):
        with pytest.raises(SystemExit) as e:
            ensure_model_installed(model_name)
        assert e.value.code == 1


def test_model_not_installed_user_input():
    model_name = "test_model"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="")
        with patch("builtins.input", return_value="y"):
            ensure_model_installed(model_name)
            mock_run.assert_called_with(["ollama", "pull", model_name], check=True)


def test_retry_chain_invoke_success():
    chain = MagicMock()
    inputs = {"key": "value"}
    fallback_response = "Fallback response"
    max_retries = 3

    # Mock the chain to return a valid response on the first call
    chain.invoke.return_value = "Valid response"

    result, retries = retry_chain_invoke(chain, inputs, fallback_response, max_retries)

    assert result == "Valid response"
    assert retries == 1


def test_stop_models_success():
    model_name = "test_model"
    with patch("subprocess.run") as mock_run:
        stop_models(model_name)
        mock_run.assert_called_with(
            ["ollama", "stop", model_name], check=True, capture_output=True, text=True
        )


def test_stop_models_failure():
    model_name = "test_model"
    with patch(
        "subprocess.run", side_effect=subprocess.CalledProcessError(1, "ollama")
    ):
        with pytest.raises(SystemExit) as e:
            stop_models(model_name)
        assert e.value.code == 1
