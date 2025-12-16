import os
import requests
import zipfile
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

def generate_cards_json(tmp_dir, output_path):
    # 4. Generate cards.json from json1.json
    print("Generating cards.json from json1.json...")
    json1_path = os.path.join(tmp_dir, "json1.json")
    json2_path = os.path.join(tmp_dir, "json2.json")

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
                    if "text" in card and "desc" in card["text"]:
                        desc = card["text"]["desc"]

                    id_to_data[card_id] = {
                        "name": cn_name,
                        "desc": desc
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
                        for image in card["card_images"]:
                            if "id" in image:
                                try:
                                    card_id = int(image["id"])
                                    # Use string of int for key (JSON requirement), int for values
                                    card_obj = {
                                        "id": card_id,
                                        "cardImage": card_id,
                                        "name": cn_name,
                                        "description": desc,
                                        "cardType": card_type,
                                        "attribute": attribute,
                                        "frameType": processed_frame_type
                                    }

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
    tmp_dir = "tmp"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    process_json2(tmp_dir)
    process_json1(tmp_dir)
    format_json_files(tmp_dir)
    generate_cards_json(tmp_dir, "cards.json")

if __name__ == "__main__":
    main()
