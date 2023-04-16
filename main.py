import base64
import json
import os
import zipfile
import requests
import wget
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import file
from googleapiclient.errors import HttpError

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
    secret_file = os.path.join("./", 'secrets_gs.json')
    with (open(secret_file)) as f:
        secrets = json.loads(f.read())
    HUGGING_FACE_ACCESS_TONE = secrets['HUGGING_FACE_TOKEN']
    FOLDER_ID = secrets["FOLDER_ID"]
    # print(">>> HG 토큰 : " + HUGGING_FACE_ACCESS_TONE)
    setChromeDriver()

    # 구글 스프레드시트
    json_key_path = "secrets_gs.json"  # JSON Key File Path
    gc = gspread.service_account(filename=json_key_path)
    doc = gc.open("text2image_test")

    # 시트명 설정
    sheet = doc.worksheet("0415")

    # 커맨드 설정
    col_index = 1
    col_data = sheet.col_values(col_index)

    with open('IMAGE_COMMAND_FROM_GS.txt', 'w') as f:
        for cell in col_data:
            f.write(cell)
    command_file = os.path.join("./", "IMAGE_COMMAND_FROM_GS.txt")
    opendFile = open(command_file, 'r')
    Lines = opendFile.readlines()

    # 구글 드라이브
    credentials = service_account.Credentials.from_service_account_file('secrets_gs.json')
    drive_service = build('drive', 'v3', credentials=credentials)

    # 폴더 목록을 가져옵니다.
    # try:
    #     folder_query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
    #     folders = drive_service.files().list(q=folder_query).execute().get('files', [])
    #     for folder in folders:
    #         print(f'Folder Name: {folder.get("name")}, Folder ID: {folder.get("id")}')
    # except HttpError as error:
    #     print(f'An error occurred: {error}')

    count = 0
    for line in Lines:
        print("Line: {}".format(line.strip()))
        image_bytes = getImage({
            "inputs": line.strip(),
        })
        image = Image.open(io.BytesIO(image_bytes))
        count += 1
        file_paths = "result_IMG/test{}.jpg".format(count)
        image.save(file_paths)

        # 이미지 업로드
        # service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': "test{}.jpg".format(count), 'parents': [FOLDER_ID]}
        media = MediaFileUpload(file_paths, mimetype='image/jpg')
        uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print('File ID: %s' % uploaded_file.get('id'))
        image_url = f'https://drive.google.com/uc?id={uploaded_file.get("id")}'
        image_formula = f'=IMAGE("{image_url}")'
        sheet.update_acell('A{}'.format(count), line)
        sheet.update_acell('B{}'.format(count), image_formula)
