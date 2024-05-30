import os
import re

def check_email_format(email):
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    assert re.match(email_pattern, email), f"Invalid email address: {email}"

def check_password_format(password):
    password_pattern = r"^[a-z]{4} [a-z]{4} [a-z]{4} [a-z]{4}$"
    assert re.match(password_pattern, password), 'provided app password is not in correct format. to generate app password, go to https://myaccount.google.com/apppasswords'

assert os.path.exists('emaildetails.txt'), "File emaildetails.txt does not exist. create this file and write your email address and app password. https://myaccount.google.com/apppasswords"
assert os.path.exists('yoloweights.pt'), "File yoloweights.pt does not exist, download this file from https://github.com/edwardbruin/3dprintfail/blob/main/yoloweights.pt"

# Read the first two lines from 'emaildetails.txt'
with open('emaildetails.txt', 'r') as file:
    lines = file.readlines()
    assert len(lines) >= 2, "Not enough lines in 'emaildetails.txt'."

# Check email address format
email_address = lines[0].strip()
check_email_format(email_address)

# Check password format
password = lines[1].strip()
check_password_format(password)

print("emaildetails.txt is present")

import cv2, requests, streamlink
from random import choice
from google.cloud import storage
from ultralytics import YOLO
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from datetime import datetime

uploading = False                                               # change to true to enable uploading to bucket to update website
service_account_file = 'master-magnet-414308-23a8bbb0c34f.json' # you will need to include a credentials file to update website
if uploading:
    storage_client = storage.Client.from_service_account_json(service_account_file)

image_path_input = 'output_image.jpg'
image_path_output = 'infer_image.jpg'
model = YOLO('yoloweights.pt')

def SendMail(email_text, ImgFileName = 'infer_image.jpg', 
             Server='smtp.gmail.com',
             Port=587,
             UserName=email_address, 
             UserPassword=password,
             From=email_address, 
             To='skmojo@gmail.com'):
    
    with open(ImgFileName, 'rb') as f:
        img_data = f.read()
    
    msg = MIMEMultipart()
    msg['Subject'] = 'error detected during print'
    msg['From'] = From
    msg['To'] = To

    text = MIMEText(email_text)
    msg.attach(text)
    image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
    msg.attach(image)

    s = smtplib.SMTP(Server, Port)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(UserName, UserPassword)
    try:
        s.sendmail(From, To, msg.as_string())
    except:
        pass
    s.quit()

def upload_to_bucket(blob_name, content, bucket_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(content)
    
def fetch_content_from_gcs(link):
    alp = list(map(chr, range(97, 123)))
    link = link + "?"+choice(alp)+choice(alp)+'='+choice(alp)+choice(alp)
    try:
        response = requests.get(link)
        if response.status_code == 200:
            return response.text
        else:
            return f"Error fetching content. Status code: {response.status_code}"
    except requests.RequestException as e:
        return f"Error: {e}"

gcs_link = "https://storage.googleapis.com/dl_cnn_a3_3dprintfail/link.txt"
gcs_email = "https://storage.googleapis.com/dl_cnn_a3_3dprintfail/email_address.txt"
prevrun = 'last_run_datetime.txt'

print('''_ no detection
e detected error and sent email, uploaded image
x detected error, awaiting 30 second timeout
''')

while True:
    content = fetch_content_from_gcs(gcs_link)
    streams = streamlink.streams(content)
    if "best" not in streams.keys():
        continue
    
    stream_url = streams["best"].url
        
    vcap = cv2.VideoCapture(stream_url)
    image = vcap.read()[1]
    try:
        cv2.imwrite(image_path_input, image)
    except:
        continue

    #results = model(image_path_input)
    results = model(image_path_input, verbose=False)
    if results[0].verbose() == '(no detections), ':
        print('_', end='')
        continue

    try: 
        with open(prevrun, 'r') as f:
            last_run_datetime = datetime.strptime(f.read(), "%d/%m/%Y %H:%M:%S")
        delta = datetime.now() - last_run_datetime
    except:
        with open(prevrun, 'w') as f:
            f.write(datetime.strftime(datetime.now(),"%d/%m/%Y %H:%M:%S"))
        continue

    if (delta.total_seconds() < 30):
        print('x', end='')
        continue

    print('e', end='')
    with open(prevrun, 'w') as f:
        f.write(datetime.strftime(datetime.now(),"%d/%m/%Y %H:%M:%S"))
    
    cv2.imwrite(image_path_output, results[0].plot())
    
    json_object = json.loads(results[0].tojson())
    out_string = ''
    for det in json_object:
        out_string += str(int(det['confidence']*100)) + '% confident occurence of '+ det['name']+'''
'''
    to_address = fetch_content_from_gcs(gcs_email)
    SendMail(out_string, To=to_address)
    
    if uploading:
        upload_to_bucket('infer_image.jpg', f'./{image_path_output}', 'dl_cnn_a3_3dprintfail')
