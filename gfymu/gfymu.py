import os
import json
import shutil
import requests
from multiprocessing import Pool, cpu_count
from requests_toolbelt import MultipartEncoder
from time import sleep
from pathlib import Path
from getpass import getpass
from tqdm import tqdm

NUM_THREADS = cpu_count()
BASE_URL = "https://api.gfycat.com/v1"


class GfycatMassUploader:
    def __init__(self, filepath: Path, tags: list[str]) -> None:
        self.HOME = Path.home()
        self.tags = tags
        self.filepath = filepath
        self.credentials = {}
        self.auth_headers = {}
        self.config = {}
        self.files_to_upload = []

        if ".gfymuconfig" not in os.listdir(self.HOME):
            self.setup()
        else:
            with open(self.HOME / ".gfymuconfig", "r") as f:
                self.config = json.load(f)

    def setup(self) -> None:
        print("Gfycat Mass Uploader first-time setup. Please provide the following:")
        config = dict(
            client_id=input("Gfycat API client ID: "),
            client_secret=input("Gfycat API client secret: "),
            username=input("Gfycat username: "),
            password=getpass("Gfycat API password: "),
        )
        with open(self.HOME / ".gfymuconfig", "w+", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        self.config = config

    def check_valid_files(self) -> None:
        filepath = self.filepath
        if filepath.is_dir():
            files_to_upload = [fp for fp in os.listdir(filepath) if fp.endswith(".mp4")]
            files_to_upload = list(map(lambda p: filepath / p, files_to_upload))
        else:
            files_to_upload = [filepath]

        if len(files_to_upload) == 0:
            raise FileNotFoundError(f"No valid files found in {str(filepath)}")
        self.files_to_upload = files_to_upload

    def token_is_valid(self) -> bool:
        res = requests.get(f"{BASE_URL}/me", headers=self.auth_headers)
        return res.status_code == 200

    def get_access_token(self) -> None:
        payload = {**self.config, "grant_type": "password"}
        res = requests.post(
            f"{BASE_URL}/oauth/token",
            data=json.dumps(payload),
            headers={"Accept": "*/*", "Content-Type": "application/json"},
        )
        if res.status_code != 200:
            raise Exception(
                f"Error {res.status_code}:\n{json.dumps(res.json(), indent=2)}"
            )
        self.credentials = res.json()
        self.auth_headers = {
            "Authorization": f'Bearer {self.credentials["access_token"]}'
        }

    def refresh_token(self) -> None:
        payload = {
            "grant_type": "refresh",
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "refresh_token": self.credentials["refresh_token"],
        }
        res = requests.post(
            f"{BASE_URL}/oauth/token",
            data=json.dumps(payload),
            headers={
                "Accept": "*/*",
                "Content-Type": "application/json",
            },
        )
        if res.status_code != 200:
            print(
                f"Error {res.status_code} when attempting to refresh token:\n{json.dumps(res.json(), indent=2)}"
            )
            print(f"\nAttempting to fetch new access token...")
            self.get_access_token()
        else:
            self.credentials = res.json()
            self.auth_headers = {
                "Authorization": f'Bearer {self.credentials["access_token"]}'
            }

    def file_upload(self, file: Path) -> int:
        if not self.token_is_valid():
            if self.credentials.get("refresh_token"):
                self.refresh_token()
            else:
                self.get_access_token()
        res = requests.post(
            f"{BASE_URL}/gfycats",
            headers={**self.auth_headers, "Content-Type": "application/json"},
            data=json.dumps(
                {
                    "title": file.name,
                    "tags": self.tags,
                    "nsfw": False,
                    "keepAudio": True,
                    "private": False,
                }
            ),
        )
        metadata = res.json()
        new_file = file.parent / metadata["gfyname"]
        shutil.copy2(file, new_file)

        with open(new_file, "rb") as f:
            m = MultipartEncoder(
                fields={
                    "key": metadata["gfyname"],
                    "file": (metadata["gfyname"], f, "video/mp4"),
                }
            )
            res = requests.post(
                "https://filedrop.gfycat.com",
                data=m,
                headers={"Content-Type": m.content_type},
            )
        if res.status_code >= 400:
            os.remove(new_file)
            print(res.status_code)
            return res.status_code

        while True:
            res = requests.get(f'{BASE_URL}/gfycats/fetch/status/{metadata["gfyname"]}')
            status = res.json()
            if status["task"].lower() in ["notfoundo", "encoding"]:
                sleep(3)
                continue
            os.remove(new_file)
            break
        return status

    def main(self) -> None:
        files_to_upload = self.files_to_upload
        if not self.token_is_valid():
            if self.credentials.get("refresh_token"):
                self.refresh_token()
            else:
                self.get_access_token()

        res = requests.get(f"{BASE_URL}/me", headers=self.auth_headers)
        if res.status_code >= 400:
            print(res.status_code)
            return

        with Pool(NUM_THREADS) as pool:
            with tqdm(total=len(files_to_upload)) as pbar:
                for i, _ in pool.imap_unordered(self.file_upload, files_to_upload):
                    pbar.update()