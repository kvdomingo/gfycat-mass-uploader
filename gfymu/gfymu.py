import io
import json
import os
from getpass import getpass
from multiprocessing import Pool, cpu_count
from pathlib import Path
from time import sleep

import requests
from loguru import logger
from requests.adapters import HTTPAdapter, Retry
from requests_toolbelt import MultipartEncoder
from tqdm import tqdm

NUM_THREADS = cpu_count()
BASE_URL = "https://api.gfycat.com/v1"


class GfycatMassUploader:
    def __init__(self, filepath: Path, tags: list[str], pattern: str = "") -> None:
        self.HOME = Path.home()
        self.tags = tags
        self.filepath = filepath
        self.recursive = bool(pattern)
        self.pattern = pattern
        self.credentials = {}
        self.auth_headers = {}
        self.config = {}
        self.files_to_upload = []
        self.uploaded_slugs = []

        if ".gfymuconfig" not in os.listdir(self.HOME):
            self.setup()
        else:
            with open(self.HOME / ".gfymuconfig", "r") as f:
                self.config = json.load(f)

    def setup(self) -> None:
        logger.info(
            "\nGfycat Mass Uploader first-time setup. Please provide the following:\n"
        )
        config = dict(
            client_id=input("Gfycat API client ID: "),
            client_secret=getpass("Gfycat API client secret: "),
            username=input("Gfycat username: "),
            password=getpass("Gfycat API password: "),
        )
        with open(self.HOME / ".gfymuconfig", "w+", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        self.config = config

    def check_valid_files(self) -> None:
        filepath = self.filepath
        if self.recursive:
            files_to_upload = [
                f for f in self.filepath.glob(self.pattern) if f.name.endswith(".mp4")
            ]
        else:
            if filepath.is_dir():
                files_to_upload = [
                    fp for fp in os.listdir(filepath) if fp.endswith(".mp4")
                ]
                files_to_upload = list(map(lambda p: filepath / p, files_to_upload))
            else:
                files_to_upload = [filepath]

        if len(files_to_upload) == 0:
            raise FileNotFoundError(f"No valid files found in {str(filepath)}")
        self.files_to_upload = files_to_upload

    def token_is_valid(self) -> bool:
        res = requests.get(f"{BASE_URL}/me", headers=self.auth_headers)
        return res.ok

    def get_access_token(self) -> None:
        payload = {**self.config, "grant_type": "password"}
        res = requests.post(
            f"{BASE_URL}/oauth/token",
            data=json.dumps(payload),
            headers={"Accept": "*/*", "Content-Type": "application/json"},
        )
        if not res.ok:
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
        if not res.ok:
            logger.error(
                f"Error {res.status_code} when attempting to refresh token:\n{json.dumps(res.json(), indent=2)}"
            )
            logger.info("\nAttempting to fetch new access token...")
            self.get_access_token()
        else:
            self.credentials = res.json()
            self.auth_headers = {
                "Authorization": f'Bearer {self.credentials["access_token"]}'
            }

    def file_upload(self, file: Path) -> str | None:
        if not self.token_is_valid():
            if self.credentials.get("refresh_token"):
                self.refresh_token()
            else:
                self.get_access_token()
        if self.recursive:
            directory_list = list(map(lambda s: s.lower(), str(file).split(file.root)))
            subdirectory_index = directory_list.index(self.filepath.name.lower())
            tags = [
                self.filepath.name.lower(),
                directory_list[subdirectory_index + 1].lower(),
                *self.tags,
            ]
        else:
            tags = self.tags
        sess = requests.Session()
        retries = Retry(total=100, backoff_factor=0.1)
        sess.mount("https://", HTTPAdapter(max_retries=retries))
        res = sess.post(
            f"{BASE_URL}/gfycats",
            headers={**self.auth_headers, "Content-Type": "application/json"},
            data=json.dumps(
                {
                    "title": file.name,
                    "tags": tags,
                    "nsfw": False,
                    "keepAudio": True,
                    "private": False,
                }
            ),
        )
        metadata = res.json()

        with open(file, "rb") as f:
            new_file = io.BytesIO(f.read())
            new_file.name = metadata["gfyname"]
            new_file.seek(0)
            m = MultipartEncoder(
                fields={
                    "key": metadata["gfyname"],
                    "file": (metadata["gfyname"], new_file, "video/mp4"),
                }
            )
            res = requests.post(
                "https://filedrop.gfycat.com",
                data=m,
                headers={"Content-Type": m.content_type},
            )
        if not res.ok:
            logger.error(res.status_code)
            return None

        while True:
            res = requests.get(f'{BASE_URL}/gfycats/fetch/status/{metadata["gfyname"]}')
            status = res.json()
            if status["task"].lower() in ["notfoundo", "encoding"]:
                sleep(3)
                continue
            if res.ok:
                return f"https://gfycat.com/{metadata['gfyname']}"
            break
        return None

    def main(self) -> None:
        files_to_upload = self.files_to_upload
        if not self.token_is_valid():
            if self.credentials.get("refresh_token"):
                self.refresh_token()
            else:
                self.get_access_token()

        res = requests.get(f"{BASE_URL}/me", headers=self.auth_headers)
        if not res.ok:
            logger.error(res.status_code)
            return

        with Pool(NUM_THREADS) as pool:
            with tqdm(total=len(files_to_upload)) as pbar:
                for status in pool.imap_unordered(self.file_upload, files_to_upload):
                    if status is not None:
                        self.uploaded_slugs.append(status)
                    pbar.update()
        for i in range(0, len(self.uploaded_slugs), 5):
            print("\n", *self.uploaded_slugs[i : i + 5], sep="\n")
