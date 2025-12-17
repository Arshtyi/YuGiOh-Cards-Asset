import os
import zipfile
import json
from .utils import download_file, verify_md5

def process_json2(tmp_dir):
    # Json2 (ygocdb)
    zip_url = "https://ygocdb.com/api/v0/cards.zip"
    md5_url = "https://ygocdb.com/api/v0/cards.zip.md5"
    zip_path = os.path.join(tmp_dir, "cards.zip")

    # Always download to ensure we have the file
    download_file(zip_url, zip_path)

    print("Unzipping cards.zip...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(tmp_dir)

    # The extracted file is expected to be 'cards.json'
    extracted_file = os.path.join(tmp_dir, "cards.json")

    if os.path.exists(extracted_file):
        # Verify MD5 of the extracted JSON file
        if verify_md5(extracted_file, md5_url):
            json2_path = os.path.join(tmp_dir, "json2.json")
            if os.path.exists(json2_path):
                os.remove(json2_path)
            os.rename(extracted_file, json2_path)
            print(f"Renamed {extracted_file} to {json2_path}")

            # Clean up zip file
            if os.path.exists(zip_path):
                os.remove(zip_path)
                print(f"Removed {zip_path}")
        else:
            print("MD5 verification failed for the extracted file.")
    else:
        print(f"Expected extracted file {extracted_file} not found.")

def process_json1(tmp_dir):
    # Json1 (ygoprodeck)
    json1_url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
    json1_path = os.path.join(tmp_dir, "json1.json")
    download_file(json1_url, json1_path)

def format_json_files(tmp_dir):
    # Format JSON files
    for filename in ["json1.json", "json2.json"]:
        filepath = os.path.join(tmp_dir, filename)
        if os.path.exists(filepath):
            print(f"Formatting {filename}...")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"Formatted {filename} successfully.")
            except Exception as e:
                print(f"Error formatting {filename}: {e}")
        else:
            print(f"{filename} not found.")
