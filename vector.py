import os
import subprocess
import json
import sys
import hashlib
import requests
import shutil
import zipfile

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from rich import print
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
)

sys.path.insert(0, os.path.dirname(__file__))

# Setup
db_location = os.path.join(os.path.dirname(__file__), "chroma_db")
index_file = os.path.join(os.path.dirname(__file__), "file_index.json")
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=100,
)


def download_vector_store():
    """Download pre-built vector store from GitHub."""
    download = (
        input(
            "\n📦 Vector store not found. Do you want to download it from GitHub? (y/n): "
        )
        .strip()
        .lower()
    )
    if download == "y":
        # Paths
        tmp_dir = (
            os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp")
            if os.name == "nt"
            else "/tmp"
        )
        zip_path = os.path.join(tmp_dir, "IntuneBuddy.zip")
        extract_dir = os.path.join(tmp_dir, "IntuneBuddy")

        # Download the zip file
        url = "https://github.com/almenscorner/dummy/releases/download/v0.0.1/vector_store.zip"
        print(f"\n⬇️ Downloading from {url}...")
        response = requests.get(url)
        response.raise_for_status()
        with open(zip_path, "wb") as f:
            f.write(response.content)

        # Unzip the file
        print("\n📦 Unzipping...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        # Move files
        print("\n📂 Moving files...")
        shutil.move(
            os.path.join(extract_dir, "chroma_db"),
            os.path.join(os.path.dirname(__file__), "chroma_db"),
        )
        shutil.move(
            os.path.join(extract_dir, "file_index.json"),
            os.path.join(os.path.dirname(__file__), "file_index.json"),
        )

        # Cleanup
        print("\n🧹 Cleaning up...")
        os.remove(zip_path)
        shutil.rmtree(extract_dir)

        print("\n✅ Vector store downloaded successfully.\n")
    else:
        print(
            "\n[yellow]Vector store will be built. This will take a while...[/yellow]\n"
        )


if not os.path.exists(db_location):
    download_vector_store()

vectore_store = Chroma(
    collection_name="Intune_docs",
    persist_directory=db_location,
    embedding_function=embeddings,
)

# Constants
BATCH_SIZE = 5000

# Load existing file index (or empty)
if os.path.exists(index_file):
    with open(index_file, "r") as f:
        file_index = json.load(f)
else:
    file_index = {}

documents = []
ids = []


def normalize_path(path):
    """Normalize file paths to always use forward slashes."""
    return path.replace("\\", "/")


def hash_file(filepath):
    """Return SHA256 hash of file contents with normalized line endings."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        buf = f.read()
        buf = buf.replace(b"\r\n", b"\n")  # Normalize CRLF to LF
        hasher.update(buf)
    return hasher.hexdigest()


def get_intune_docs():
    changed_files = 0
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(current_dir, "IntuneDocs/intune/intune-service")

    base_dirs = [
        os.path.join(current_dir, "IntuneDocs/intune/intune-service"),
        os.path.join(current_dir, "IntuneDocs/autopilot"),
    ]

    for base_dir in base_dirs:
        for root, dirs, files in os.walk(base_dir):
            for filename in files:
                if filename.endswith(".md"):
                    file_path = os.path.join(root, filename)
                    relative_path = normalize_path(
                        os.path.relpath(file_path, start=base_dir)
                    )
                    file_hash = hash_file(file_path)

                    # ❗️Check hash BEFORE opening the file
                    if file_index.get(relative_path) == file_hash:
                        continue  # File unchanged, skip!

                    changed_files += 1

                    # Only read and split if the file changed
                    with open(file_path, "r", encoding="utf-8") as f:
                        raw_text = f.read()

                    chunks = text_splitter.split_text(raw_text)

                    for i, chunk in enumerate(chunks):
                        metadata = {
                            "source": relative_path,
                            "type": "intune",
                        }

                        document = Document(
                            page_content=chunk,
                            metadata=metadata,
                            id=f"{relative_path}-{i}",
                        )
                        documents.append(document)
                        ids.append(f"{relative_path}-{i}")

                    # Update hash only AFTER processing the file
                    file_index[relative_path] = file_hash

    return changed_files


def add_documents_in_batches(vector_store, documents, ids):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.completed}/{task.total}"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(
            "[bright_cyan]Adding content to Vector database...", total=len(documents)
        )
        for i in range(0, len(documents), BATCH_SIZE):
            batch_docs = documents[i : i + BATCH_SIZE]
            batch_ids = ids[i : i + BATCH_SIZE]
            vector_store.add_documents(documents=batch_docs, ids=batch_ids)
            progress.update(task, advance=len(batch_docs))

    print("\n✅ All content have been added to the vector database successfully!\n")


"""git_cmd = ["git", "pull"]
output = subprocess.run(
    git_cmd,
    cwd=os.path.join(os.path.dirname(__file__), "IntuneDocs"),
    capture_output=True,
    text=True,
)"""


def ensure_intunedocs_up_to_date():
    repo_url = "https://github.com/MicrosoftDocs/memdocs.git"
    docs_dir = os.path.join(os.path.dirname(__file__), "IntuneDocs")

    if not os.path.exists(docs_dir):
        print("\n📚 IntuneDocs not found. Cloning fresh copy...\n")
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, docs_dir],
                check=True,
                capture_output=True,
            )

            print("✅ IntuneDocs cloned successfully.\n")
        except subprocess.CalledProcessError:
            print(
                "[red]Failed to clone IntuneDocs. Please check your Git installation.[/red]"
            )
            raise
    else:
        try:
            subprocess.run(
                ["git", "-C", docs_dir, "pull", "--ff-only"],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            print(
                "[red]Failed to update IntuneDocs. Continuing with existing files.[/red]"
            )


# Ensure IntuneDocs is up to date
ensure_intunedocs_up_to_date()

print("\n🔍 Scanning for changed files...\n")
changed_files = get_intune_docs()

if documents:
    print(
        f"📝 {changed_files} changed documents found, updating, this might take a while... ☕\n"
    )
    add_documents_in_batches(vectore_store, documents, ids)
else:
    print("✅ No changes detected. Vector database is up-to-date.\n")

# Save updated index
with open(index_file, "w") as f:
    json.dump(file_index, f, indent=2)

retreiver = vectore_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.4, "k": 8},
)
