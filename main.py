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
from googleapiclient.http import MediaFileUpload
from selenium import webdriver
from selenium.webdriver.common.by import By
import gspread
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import io
from PIL import Image

HUGGING_FACE_ACCESS_TONE = ""
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
FOLDER_ID = ""

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
    FOLDER_ID = secrets["FOLDER_ID"]
    # print(">>> HG 토큰 : " + HUGGING_FACE_ACCESS_TONE)
    setChromeDriver()

    command_file = os.path.join("./", "IMAGE_COMMAND.txt")
    file = open(command_file, 'r')
    Lines = file.readlines()

    # 구글 스프레드시트
    json_key_path = "./secrets.json"  # JSON Key File Path
    gc = gspread.service_account(filename=json_key_path)
    doc = gc.open("text2image_test")
    sheet = doc.worksheet("0415")

    # 구글 드라이브
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/drive.file']


    count = 0
    for line in Lines :
        print("Line: {}".format(line.strip()))
        image_bytes = getImage({
            "inputs": line.strip(),
        })
        image = Image.open(io.BytesIO(image_bytes))
        count += 1
        # image.save("test{}.jpg".format(count))
        image_base64 = base64.b64encode(image_bytes).decode()
        sheet.update_acell('A{}'.format(count), line)

        creds = Credentials.from_authorized_user_file('secrets.json', SCOPES)
        # 이미지 업로드
        # service = build('drive', 'v3', credentials=creds)
        # file_metadata = {'name': 'image{}.jpg'.format(count), 'parents': [FOLDER_ID]}
        # media = MediaFileUpload(image, mimetype='image/jpeg')
        # file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        # print('File ID: %s' % file.get('id'))



