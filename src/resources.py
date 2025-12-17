import os
import tarfile
import json
from .utils import download_file, verify_sha256

def download_resources(res_dir):
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    # 1. token.json
    token_url = "https://github.com/Arshtyi/YuGiOh-Tokens/releases/download/latest/token.json"
    token_sha256_url = "https://github.com/Arshtyi/YuGiOh-Tokens/releases/download/latest/token.json.sha256"
    token_path = os.path.join(res_dir, "token.json")

    download_file(token_url, token_path)
    if not verify_sha256(token_path, token_sha256_url):
        print("Warning: token.json verification failed.")

    # 2. forbidden_and_limited_list.tar.xz
    limited_url = "https://github.com/Arshtyi/YuGiOh-Forbidden-And-Limited-List/releases/download/latest/forbidden_and_limited_list.tar.xz"
    limited_sha256_url = "https://github.com/Arshtyi/YuGiOh-Forbidden-And-Limited-List/releases/download/latest/forbidden_and_limited_list.tar.xz.sha256"
    limited_path = os.path.join(res_dir, "forbidden_and_limited_list.tar.xz")
    limited_extract_dir = os.path.join(res_dir, "limited")

    download_file(limited_url, limited_path)
    if verify_sha256(limited_path, limited_sha256_url):
        print("Extracting forbidden_and_limited_list.tar.xz...")
        if not os.path.exists(limited_extract_dir):
            os.makedirs(limited_extract_dir)
        with tarfile.open(limited_path, "r:xz") as tar:
            tar.extractall(path=limited_extract_dir)
        print("Extraction complete.")

        # Clean up tar.xz file
        if os.path.exists(limited_path):
            os.remove(limited_path)
            print(f"Removed {limited_path}")
    else:
        print("Warning: forbidden_and_limited_list.tar.xz verification failed.")

    # 3. typeline.conf
    typeline_url = "https://github.com/Arshtyi/Translations-Of-YuGiOh-Cards-Type/releases/download/latest/typeline.conf"
    typeline_sha256_url = "https://github.com/Arshtyi/Translations-Of-YuGiOh-Cards-Type/releases/download/latest/typeline.conf.sha256"
    typeline_path = os.path.join(res_dir, "typeline.conf")

    download_file(typeline_url, typeline_path)
    if not verify_sha256(typeline_path, typeline_sha256_url):
        print("Warning: typeline.conf verification failed.")

def load_typeline_conf(res_dir):
    conf_path = os.path.join(res_dir, "typeline.conf")
    mapping = {}
    if os.path.exists(conf_path):
        with open(conf_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and "=" in line:
                    key, value = line.split("=", 1)
                    mapping[key.strip()] = value.strip()
    return mapping

def load_limited_list(res_dir):
    limited_data = {
        "ocg": {},
        "tcg": {},
        "md": {}
    }

    limited_dir = os.path.join(res_dir, "limited")
    if not os.path.exists(limited_dir):
        print(f"Warning: Limited list directory {limited_dir} not found.")
        return limited_data

    for format_name in ["ocg", "tcg", "md"]:
        file_path = os.path.join(limited_dir, f"{format_name}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Flatten the structure: id -> status
                    # data structure is {"forbidden": [ids], "limited": [ids], "semi-limited": [ids]}
                    for status, ids in data.items():
                        for card_id in ids:
                            limited_data[format_name][card_id] = status
                print(f"Loaded {format_name} limited list.")
            except Exception as e:
                print(f"Error loading {format_name} limited list: {e}")
        else:
            print(f"Warning: {format_name}.json not found in {limited_dir}")

    return limited_data
