import os
import json
import time
import requests
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def download_single_image(card_id, image_id, output_dir, session=None):
    """
    Downloads a single image for the given card_id using image_id for URL.
    Saves it as <card_id>.png in output_dir.
    Returns True if successful (or already exists), False otherwise.
    """
    url = f"https://images.ygoprodeck.com/images/cards_cropped/{image_id}.jpg"
    file_path = os.path.join(output_dir, f"{card_id}.png")

    # Skip if already exists
    if os.path.exists(file_path):
        return True

    if session is None:
        session = requests

    try:
        response = session.get(url, timeout=20)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            return False
    except Exception as e:
        print(f"Error downloading image for {card_id} (Image ID: {image_id}): {e}")
        return False

def download_images(cards_json_path, output_dir):
    """
    Reads cards.json and downloads images for all cards to output_dir.
    Respects rate limit of 20 req/s.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    print(f"Loading cards from {cards_json_path}...")
    if not os.path.exists(cards_json_path):
        print(f"Error: {cards_json_path} not found.")
        return

    with open(cards_json_path, 'r', encoding='utf-8') as f:
        cards_data = json.load(f)

    card_ids = list(cards_data.keys())
    total_cards = len(card_ids)
    print(f"Found {total_cards} cards. Starting image download to '{output_dir}'...")
    print("Note: Rate limiting enabled. Reduced speed to avoid SSL errors.")

    delay = 0.06

    session = create_session()
    failed_ids = []
    success_count = 0

    # Use ThreadPoolExecutor for parallelism
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_to_card = {}
        for i, card_id in enumerate(card_ids):
            card_info = cards_data.get(card_id, {})
            image_id = card_info.get("cardImage", card_id)

            future = executor.submit(download_single_image, card_id, image_id, output_dir, session)
            future_to_card[future] = card_id

            time.sleep(delay)

            if (i + 1) % 100 == 0:
                print(f"Submitted {i + 1}/{total_cards} image requests...", end='\r')

        print(f"\nAll requests submitted. Waiting for completion...")

        for future in concurrent.futures.as_completed(future_to_card):
            card_id = future_to_card[future]
            try:
                if future.result():
                    success_count += 1
                else:
                    failed_ids.append(card_id)
            except Exception:
                failed_ids.append(card_id)

    # Retry logic for failed IDs
    final_failed_ids = []
    if failed_ids:
        print(f"\nRetrying {len(failed_ids)} failed downloads...")
        retry_success_count = 0
        for i, card_id in enumerate(failed_ids):
            print(f"Retrying {i+1}/{len(failed_ids)}: {card_id}...", end='\r')

            # Get image_id again for retry
            card_info = cards_data.get(card_id, {})
            image_id = card_info.get("cardImage", card_id)

            # Retry with a fresh session or existing one, slightly slower to be safe
            time.sleep(0.1)
            if download_single_image(card_id, image_id, output_dir, session):
                retry_success_count += 1
                success_count += 1
            else:
                final_failed_ids.append(card_id)
        print(f"\nRetry finished. Recovered {retry_success_count}/{len(failed_ids)}.")

    print("-" * 30)
    if len(final_failed_ids) > 0:
        print(f"Image download finished with issues.")
        print(f"Successfully downloaded: {success_count}/{total_cards}")
        print(f"Failed: {len(final_failed_ids)}")
        print(f"Failed IDs: {final_failed_ids}")
    else:
        print(f"Image download finished successfully! ({success_count}/{total_cards})")
    print("-" * 30)
