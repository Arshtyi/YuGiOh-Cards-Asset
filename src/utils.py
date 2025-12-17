import requests
import hashlib

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
