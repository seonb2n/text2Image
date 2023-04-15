import base64
import json
import os
import time
import zipfile
from typing import List
import io
from PIL import Image
import requests
import requests as r
import wget
from selenium import webdriver
from selenium.webdriver.common.by import By

HUGGING_FACE_ACCESS_TONE = ""
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

def setChromeDriver():
    url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
    response = requests.get(url)
    version_number = response.text
    download_url = "https://chromedriver.storage.googleapis.com/" + version_number + "/chromedriver_win32.zip"
    latest_driver_zip = wget.download(download_url, 'chromedriver.zip')
    with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
        zip_ref.extractall(os.getcwd())
    os.remove(latest_driver_zip)

def getImage(payload):
    headers = {"Authorization": "Bearer " + HUGGING_FACE_ACCESS_TONE}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

if __name__ == '__main__':
    secret_file = os.path.join("./", 'secrets.json')
    with (open(secret_file)) as f:
        secrets = json.loads(f.read())
    HUGGING_FACE_ACCESS_TONE = secrets['HUGGING_FACE_TOKEN']
    # print(">>> HG 토큰 : " + HUGGING_FACE_ACCESS_TONE)
    setChromeDriver()

    command_file = os.path.join("./", "IMAGE_COMMAND.txt")
    file = open(command_file, 'r')
    Lines = file.readlines()

    count = 0
    for line in Lines :
        print("Line: {}".format(line.strip()))
        image_bytes = getImage({
            "inputs": line.strip(),
        })
        image = Image.open(io.BytesIO(image_bytes))
        count += 1
        image.save("test{}.jpg".format(count))
