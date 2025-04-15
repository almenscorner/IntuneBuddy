import subprocess
import sys
import re

from rich import print


def ensure_ollama_installed():
    try:
        subprocess.run(
            ["ollama", "-v"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        # This happens if the binary doesn't exist at all
        print("[red]Ollama is not installed or not found in PATH.[/red]")
        sys.exit(1)
    except subprocess.CalledProcessError:
        # This happens if the binary exists but fails badly
        print(
            "[red]Ollama was found but it returned an error. Please check the installation.[/red]"
        )
        sys.exit(1)


def ensure_git_installed():
    try:
        subprocess.run(
            ["git", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        # This happens if the binary doesn't exist at all
        print("[red]Git is not installed or not found in PATH.[/red]")
        sys.exit(1)
    except subprocess.CalledProcessError:
        # This happens if the binary exists but fails badly
        print(
            "[red]Git was found but it returned an error. Please check the installation.[/red]"
        )
        sys.exit(1)


def retry_chain_invoke(chain, inputs, fallback_response, max_retries=5):
    retries = 0
    while retries < max_retries:
        retries += 1
        result = chain.invoke(inputs)
        result = clean_output(result)
        if result != fallback_response:
            return result, retries
    return fallback_response, retries


def ensure_model_installed(model_name: str):
    """
    Ensure the specified model is installed.
    """
    try:
        output = subprocess.run(
            ["ollama", "list"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        print(
            f"[red]Failed to check if {model_name} is installed. Please check your Ollama installation.[/red]"
        )
        sys.exit(1)
    if model_name not in output.stdout:
        install_cmd = ["ollama", "pull", model_name]
        should_install = input(
            f"\n{model_name} model is not installed. Do you want to install it? (y/n): "
        )
        if should_install.lower() == "y":
            try:
                subprocess.run(install_cmd, check=True)
            except subprocess.CalledProcessError:
                print(
                    f"[red]Failed to install {model_name}. Please check your Ollama installation.[/red]"
                )
                sys.exit(1)
        else:
            print(
                f"[red]Model is not installed. Please install it by running 'ollama pull {model_name}'[/red]"
            )
            sys.exit(1)


def clean_output(output: str) -> str:
    """
    Cleans the LLM output by removing unwanted patterns and unnecessary greetings.
    """
    # Remove anything between <think>...</think> tags
    output = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL)

    # List of unwanted strings to remove
    unwanted_phrases = [
        "<think>",
        "</think>",
        "**Answer:**",
        "Hello!",
        "Hello.",
    ]

    for phrase in unwanted_phrases:
        output = output.replace(phrase, "")

    # Remove extra leading/trailing whitespace
    return output.strip()


def stop_models(*models):
    """
    Stops the running Ollama model.
    """
    for model in models:
        try:
            subprocess.run(
                ["ollama", "stop", model],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError:
            print(
                f"[red]Failed to stop {model}. Please check your Ollama installation.[/red]"
            )
            sys.exit(1)
