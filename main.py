import os
import shutil
from src.resources import download_resources
from src.data_manager import process_json2, process_json1, format_json_files
from src.card_processor import generate_cards_json

def main():
    res_dir = "res"
    download_resources(res_dir)
    tmp_dir = "tmp"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    process_json2(tmp_dir)
    process_json1(tmp_dir)
    format_json_files(tmp_dir)
    generate_cards_json(tmp_dir, "cards.json", res_dir)

    # Cleanup
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
        print(f"Removed {tmp_dir}")

    if os.path.exists(res_dir):
        shutil.rmtree(res_dir)
        print(f"Removed {res_dir}")

if __name__ == "__main__":
    main()
