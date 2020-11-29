import json
import logging
import os

import requests

LOGGER = logging.getLogger(__name__)

DB_PATH = "db.sqlite"
HASH_PATH = "hash.json"
HASH_URI = "https://raw.githubusercontent.com/mygbu/timetable/master/md5.html"
DB_URI = "https://github.com/mygbu/timetable/blob/master/varun.sqlite?raw=true"


def db_exists():
    return os.path.exists(DB_PATH)


def hash_exists():
    return os.path.exists(HASH_PATH)


def cleanup():
    if db_exists():
        os.remove(DB_PATH)
    if hash_exists():
        os.remove(HASH_PATH)


def download_hash_and_db():
    cleanup()
    try:
        r_hash = requests.get(HASH_URI)
        open(HASH_PATH, 'x').write(r_hash.text)
        print(f"Downloading Database with MD5 = {r_hash.text}")
        r_db = requests.get(DB_URI)
        open(DB_PATH, 'wb').write(r_db.content)
        print("Fetch Successful")
    except requests.exceptions.BaseHTTPError:
        LOGGER.error("Some Error Occurred!!")


def check_for_updates():
    if db_exists() and hash_exists():
        if json.loads(requests.get(HASH_URI).text)["md5_hash"] != json.load(open(HASH_PATH))["md5_hash"]:
            print("Stale Database Found.")
            download_hash_and_db()
        else:
            print("Using Existing Database, No Updates Found. HASH:", json.load(open(HASH_PATH))["md5_hash"])
    else:
        print("No Database Found.")
        download_hash_and_db()
