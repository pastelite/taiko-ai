from pprint import pprint
import urllib
import urllib.error
import urllib.request
import os
import zipfile
from ossapi import Ossapi
from dotenv import load_dotenv

def get_difficulty(id):
    load_dotenv()
    api = Ossapi(os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"))
    beatmapset = api.beatmapset(id)

    beatmaps = beatmapset.beatmaps
    result = map(lambda x: (x.version,x.difficulty_rating) ,beatmaps)
    return dict(result)


def download_file(url, filename):
    if os.path.exists(filename):
        print(f"File {filename} already exists")
        return

    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    print(f"Downloading {filename}")
    
    # try:
    urllib.request.urlretrieve(url, filename)
    # except urllib.error.HTTPError as e:
    # print(f"Failed to download {filename} with error {e}")
    
    print(f"File {filename} downloaded")
    
def download_and_extract_file(id):
    print(f"Downloading beatmap {id}")
    url = f"https://beatconnect.io/b/{id}"
    folder = "music"

    # Download the .osz file
    try:
        download_file(url, f"{folder}/{id}.osz")
    except urllib.error.HTTPError as e:
        print(f"Failed to download {id} with error {e}, skipped")
        return

    # Extract the .osz file
    print(f"Extracting beatmap {id}")
    with zipfile.ZipFile(f"{folder}/{id}.osz", "r") as zip_ref:
        zip_ref.extractall(f"{folder}/{id}")
        
    # save difficulty to file
    difficulty = get_difficulty(id)
    with open(f"{folder}/{id}/difficulty.txt", "w") as file:
        file.write(str(difficulty))

if __name__ == "__main__":
    download_and_extract_file(1998016)
    # get_difficulty(1998016)
