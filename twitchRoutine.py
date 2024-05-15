import os
import subprocess
import requests
from random import choice
import cv2
import streamlink

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

def upload_to_bucket(blob_name, content, bucket_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(content)

gcs_link = "https://storage.googleapis.com/dl_cnn_a3_3dprintfail/link.txt"
while True:
    content = fetch_content_from_gcs(gcs_link)
    streams = streamlink.streams(content)
    if "best" not in streams.keys():
        continue
    
    stream_url = streams["best"].url
        
    vcap = cv2.VideoCapture(stream_url)
    image = vcap.read()[1]
    cv2.imwrite('output_image.jpg', image)

    #change this to be an in-process function where the model can be kept in memory, ideally yolo for faster inferencing
    subprocess.run(['python3', 'ObjectDetection-FasterRCNN-master/inference.py','--input','./output_image.jpg','--weights','./best_model.pth'])
    
    foo = len(os.listdir('outputs/inference'))
    upload_to_bucket('infer_image.jpg', f'./outputs/inference/res_{foo}/output_image.jpg', 'dl_cnn_a3_3dprintfail')