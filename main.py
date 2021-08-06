import os
import json
import shutil
import requests
from requests_toolbelt import MultipartEncoder
from time import sleep
from pathlib import Path
from argparse import ArgumentParser
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

BASE_URL = 'https://api.gfycat.com/v1'
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
NUM_THREADS = int(os.environ.get('NUM_THREADS'))
USER_NAME = os.environ.get('USER_NAME')
USER_PASSWORD = os.environ.get('USER_PASSWORD')

with open('./credentials.json', 'r', encoding='utf-8') as f:
    credentials = json.load(f)
AUTH_HEADERS = {'Authorization': credentials['access_token']}


def token_is_valid():
    res = requests.get(f'{BASE_URL}/me', headers=AUTH_HEADERS)
    if res.status_code != 200:
        return False
    return True


def get_token():
    payload = {
        'grant_type': 'password',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'username': USER_NAME,
        'password': USER_PASSWORD,
    }
    res = requests.get(f'{BASE_URL}/oauth/token', data=payload, headers={'Content-Type': 'application/json'})
    if res.status_code != 200:
        print(res.status_code)
        return res.status_code
    data = res.json()
    with open('./credentials.json', 'w') as f:
        json.dump(data, f, indent=2)


def main():
    parser = ArgumentParser()
    parser.add_argument('-f', '--filepath', type=str)
    parser.add_argument('-t', '--tags', type=str)
    args = parser.parse_args()
    if args.tags is not None:
        args.tags = args.tags.replace(', ', ',').split(',')

    if not token_is_valid():
        get_token()

    res = requests.get(f'{BASE_URL}/me', headers=AUTH_HEADERS)
    if res.status_code >= 400:
        print(res.status_code)
        return res.status_code

    filepath = Path(args.filepath).resolve()
    if filepath.is_dir():
        files_to_upload = [fp for fp in os.listdir(filepath) if fp.endswith('.mp4')]
        files_to_upload = list(map(lambda p: filepath / p, files_to_upload))
    else:
        files_to_upload = [filepath]
    # files_to_upload = [files_to_upload[i:i + NUM_THREADS] for i in range(0, len(files_to_upload), NUM_THREADS)]

    for file in tqdm(files_to_upload, leave=False):
        res = requests.post(
            f'{BASE_URL}/gfycats',
            headers={**AUTH_HEADERS, 'Content-Type': 'application/json'},
            data=json.dumps({
                'title': file.name,
                'tags': args.tags,
                'nsfw': False,
                'keepAudio': True,
                'private': False,
            }),
        )
        metadata = res.json()
        new_file = file.parent / metadata['gfyname']
        shutil.copy2(file, new_file)

        with open(new_file, 'rb') as f:
            m = MultipartEncoder(fields={
                'key': metadata['gfyname'],
                'file': (metadata['gfyname'], f, 'video/mp4')
            })
            res = requests.post(
                'https://filedrop.gfycat.com',
                data=m,
                headers={'Content-Type': m.content_type},
            )
        if res.status_code >= 400:
            os.remove(new_file)
            print(res.status_code)
            return res.status_code

        while True:
            res = requests.get(f'{BASE_URL}/gfycats/fetch/status/{metadata["gfyname"]}')
            status = res.json()
            if status['task'].lower() in ['notfoundo', 'encoding']:
                sleep(3)
                continue
            os.remove(new_file)
            print(status)
            break


if __name__ == '__main__':
    main()
