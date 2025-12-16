import os
import requests
import zipfile
import tarfile
import hashlib
import json

def download_file(url, filepath):
    print(f"Downloading {url} to {filepath}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete.")

def verify_sha256(filepath, sha256_url):
    print(f"Verifying SHA256 for {filepath}...")
    # Download SHA256 content
    response = requests.get(sha256_url)
    response.raise_for_status()
    expected_sha256 = response.text.strip().split()[0]

    # Calculate file SHA256
    hash_sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    calculated_sha256 = hash_sha256.hexdigest()

    if calculated_sha256 == expected_sha256:
        print("SHA256 verification successful.")
        return True
    else:
        print(f"SHA256 verification failed! Expected {expected_sha256}, got {calculated_sha256}")
        return False

def verify_md5(filepath, md5_url):
    print(f"Verifying MD5 for {filepath}...")
    # Download MD5 content
    response = requests.get(md5_url)
    response.raise_for_status()
    expected_md5 = response.text.strip().split()[0].replace('"', '').replace("'", "")

    # Calculate file MD5
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    calculated_md5 = hash_md5.hexdigest()

    if calculated_md5 == expected_md5:
        print("MD5 verification successful.")
        return True
    else:
        print(f"MD5 verification failed! Expected {expected_md5}, got {calculated_md5}")
        return False

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

def process_json2(tmp_dir):
    # 1. Handle json2 (ygocdb)
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
    # 2. Handle json1 (ygoprodeck)
    json1_url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
    json1_path = os.path.join(tmp_dir, "json1.json")
    download_file(json1_url, json1_path)

def format_json_files(tmp_dir):
    # 3. Format JSON files
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

def generate_cards_json(tmp_dir, output_path):
    # 4. Generate cards.json from json1.json
    print("Generating cards.json from json1.json...")
    json1_path = os.path.join(tmp_dir, "json1.json")
    json2_path = os.path.join(tmp_dir, "json2.json")
    res_dir = "res"

    # Load limited lists
    limited_lists = load_limited_list(res_dir)

    if os.path.exists(json1_path) and os.path.exists(json2_path):
        try:
            # Load json2 to build a map of id -> data
            print("Loading json2.json for name and description lookup...")
            with open(json2_path, 'r', encoding='utf-8') as f:
                json2_data = json.load(f)

            # json2_data is a dict where values are card objects
            id_to_data = {}
            for card in json2_data.values():
                if "id" in card:
                    card_id = card["id"]
                    cn_name = card.get("cn_name")
                    desc = ""
                    pdesc = ""
                    if "text" in card:
                        if "desc" in card["text"]:
                            desc = card["text"]["desc"].replace('\r\n', '\n')
                        if "pdesc" in card["text"]:
                            pdesc = card["text"]["pdesc"].replace('\r\n', '\n')

                    id_to_data[card_id] = {
                        "name": cn_name,
                        "desc": desc,
                        "pdesc": pdesc
                    }

            print(f"Loaded {len(id_to_data)} cards from json2.json.")

            with open(json1_path, 'r', encoding='utf-8') as f:
                json1_data = json.load(f)

            json1_count = len(json1_data.get("data", []))
            print(f"Loaded {json1_count} cards from json1.json.")

            cards_data = {}
            skipped_count = 0
            if "data" in json1_data:
                for card in json1_data["data"]:
                    # Get the main ID of the card
                    main_id = card.get("id")

                    # Try to find card_info using main_id
                    card_info = id_to_data.get(main_id)

                    # If not found, try using IDs from card_images
                    if not card_info and "card_images" in card:
                        for image in card["card_images"]:
                            if "id" in image:
                                img_id = image["id"]
                                card_info = id_to_data.get(img_id)
                                if card_info:
                                    break

                    # If still not found, skip this card
                    if not card_info:
                        print(f"Error: Card with id {main_id} not found in json2. Skipping.")
                        skipped_count += 1
                        continue

                    cn_name = card_info["name"]
                    desc = card_info["desc"]
                    pdesc = card_info["pdesc"]

                    # Determine cardType based on frameType
                    frame_type = card.get("frameType")
                    processed_frame_type = frame_type.replace('_', '-') if frame_type else None

                    card_type = "monster"
                    if frame_type == "spell":
                        card_type = "spell"
                    elif frame_type == "trap":
                        card_type = "trap"

                    # Determine attribute
                    if card_type == "monster":
                        attribute = card.get("attribute", "").lower()
                    else:
                        attribute = card_type

                    if "card_images" in card:
                        # Calculate minimum ID for uniqueId
                        image_ids = []
                        for image in card["card_images"]:
                            if "id" in image:
                                try:
                                    image_ids.append(int(image["id"]))
                                except ValueError:
                                    pass

                        min_id = min(image_ids) if image_ids else None

                        for image in card["card_images"]:
                            if "id" in image:
                                try:
                                    card_id = int(image["id"])
                                    # Use string of int for key (JSON requirement), int for values
                                    unique_id = min_id if min_id is not None else card_id
                                    card_obj = {
                                        "id": card_id,
                                        "uniqueId": unique_id,
                                        "cardImage": card_id,
                                        "name": cn_name,
                                        "description": desc,
                                        "cardType": card_type,
                                        "attribute": attribute,
                                        "frameType": processed_frame_type
                                    }

                                    # Add limited status
                                    limited_status = {}
                                    for format_name in ["ocg", "tcg", "md"]:
                                        if unique_id in limited_lists[format_name]:
                                            limited_status[format_name] = limited_lists[format_name][unique_id]

                                    if limited_status:
                                        card_obj["limited"] = limited_status

                                    if card_type in ["spell", "trap"]:
                                        card_obj["race"] = card.get("race", "").lower()

                                    if card_type == "monster":
                                        if "atk" in card:
                                            card_obj["atk"] = card["atk"]

                                        # Check if it is a link monster
                                        is_link = frame_type and "link" in frame_type.lower()
                                        if not is_link:
                                            if "def" in card:
                                                card_obj["def"] = card["def"]
                                            if "level" in card:
                                                card_obj["level"] = card["level"]
                                        else:
                                            # Link monster specific attributes
                                            if "linkval" in card:
                                                card_obj["linkVal"] = card["linkval"]
                                            if "linkmarkers" in card:
                                                card_obj["linkMarkers"] = [m.lower() for m in card["linkmarkers"]]

                                        # Check if it is a pendulum monster
                                        is_pendulum = frame_type and "pendulum" in frame_type.lower()
                                        if is_pendulum:
                                            if "scale" in card:
                                                card_obj["scale"] = card["scale"]
                                            card_obj["pendulumDescription"] = pdesc

                                    cards_data[str(card_id)] = card_obj
                                except ValueError:
                                    print(f"Warning: Could not convert id {image['id']} to int.")

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(cards_data, f, ensure_ascii=False, indent=4)

            print("-" * 30)
            print(f"Summary:")
            print(f"json1.json: {json1_count} cards")
            print(f"json2.json: {len(id_to_data)} cards")
            print(f"cards.json: {len(cards_data)} cards")
            if skipped_count > 0:
                print(f"Skipped: {skipped_count} cards (not found in json2)")
            print("-" * 30)

        except Exception as e:
            print(f"Error generating cards.json: {e}")
    else:
        print(f"json1.json or json2.json not found, cannot generate cards.json.")

def main():
    res_dir = "res"
    download_resources(res_dir)

    tmp_dir = "tmp"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    process_json2(tmp_dir)
    process_json1(tmp_dir)
    format_json_files(tmp_dir)
    generate_cards_json(tmp_dir, "cards.json")

if __name__ == "__main__":
    main()
