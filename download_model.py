import os
import zipfile
import requests
import threading
from pathlib import Path
from config.constants import MODELS_DIR, MODEL_FOLDERS

# Map language to URL
MODEL_URLS = {
    "en-US": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
    "en-IN": "https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip"
}

# The folder name inside the extracted zip can differ from our target folder name.
# It is usually the zip filename without the .zip extension.
ZIP_INTERNAL_FOLDERS = {
    "en-US": "vosk-model-small-en-us-0.15",
    "en-IN": "vosk-model-en-in-0.5"
}

def is_model_downloaded(language: str) -> bool:
    folder_name = MODEL_FOLDERS.get(language)
    if not folder_name:
        return False
    final_path = MODELS_DIR / folder_name
    return final_path.exists() and final_path.is_dir()

def download_and_extract(language: str):
    if is_model_downloaded(language):
        print(f"Model for {language} already exists.")
        return True

    url = MODEL_URLS.get(language)
    if not url:
        print(f"No URL defined for language: {language}")
        return False

    final_folder_name = MODEL_FOLDERS[language]
    internal_folder_name = ZIP_INTERNAL_FOLDERS[language]
    zip_path = MODELS_DIR / f"{internal_folder_name}.zip"

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    final_path = MODELS_DIR / final_folder_name

    print(f"Downloading Vosk model for {language} from {url}...")
    
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print("Download complete. Extracting...")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(MODELS_DIR)
                
            # Rename the folder to the final name if they differ
            extracted_path = MODELS_DIR / internal_folder_name
            if extracted_path.exists() and extracted_path != final_path:
                extracted_path.rename(final_path)
                
            # Clean up zip file
            if zip_path.exists():
                zip_path.unlink()
                
            print(f"Model downloaded and extracted successfully to: {final_path.resolve()}")
            return True
        else:
            print(f"Failed to download model. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading model: {e}")
        return False

def download_async(language: str, on_complete=None):
    def run():
        success = download_and_extract(language)
        if on_complete:
            on_complete(success)
    threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    download_and_extract("en-US")
