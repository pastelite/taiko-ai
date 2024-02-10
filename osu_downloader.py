import urllib
import urllib.error
import urllib.request
import os
import zipfile


def download_and_extract_file(id):
    print(f"Downloading beatmap {id}")
    url = f"https://beatconnect.io/b/{id}"
    folder = "music"

    # Download the .osz file
    download_file(url, f"{folder}/{id}.osz")

    # Extract the .osz file
    print(f"Extracting beatmap {id}")
    with zipfile.ZipFile(f"{folder}/{id}.osz", "r") as zip_ref:
        zip_ref.extractall(f"{folder}/{id}")


def download_file(url, filename):
    if os.path.exists(filename):
        print(f"File {filename} already exists")
        return

    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    print(f"Downloading {filename}")
    urllib.request.urlretrieve(url, filename)
    print(f"File {filename} downloaded")


if __name__ == "__main__":
    download_and_extract_file(1998016)
