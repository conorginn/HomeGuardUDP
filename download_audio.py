import requests
import os

# Server URL and Pi Storage Directory
SERVER_URL = "https://homeguard.website/get_audio_files"
AUDIO_SAVE_DIR = "/home/haroldt2/audio"
USERNAME = "Tan"


def download_audio_files():
    """
    Download audio files from the server to the specified directory.
    """
    # Ensure the save directory exists
    if not os.path.exists(AUDIO_SAVE_DIR):
        os.makedirs(AUDIO_SAVE_DIR)

    try:
        # Fetch audio file metadata from the server
        response = requests.get(SERVER_URL, params={"username": USERNAME})
        if response.status_code != 200:
            print("Failed to fetch audio files:", response.json())
            return

        audio_files = response.json().get("audio_files", [])

        # Download files
        for audio in audio_files:
            file_name = os.path.basename(audio['file_path'])
            file_url = f"http://homeguard.website/static/audio/{file_name}"
            local_file = os.path.join(AUDIO_SAVE_DIR, os.path.basename(audio['file_path']))

            if not os.path.exists(local_file):
                print(f"Downloading {audio['file_path']}...")
                with requests.get(file_url, stream=True) as r:
                    r.raise_for_status()
                    with open(local_file, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                print(f"Saved to {local_file}")
            else:
                print(f"File already exists: {local_file}")

    except Exception as e:
        print("Error downloading files:", e)


if __name__ == "__main__":
    download_audio_files()




