import functions_framework
from google.cloud import storage

service_account_file = 'master-magnet-414308-23a8bbb0c34f.json'
storage_client = storage.Client.from_service_account_json(service_account_file)

@functions_framework.http
def hello_http(request):

    request_json = request.get_json(silent=True)
    request_args = request.args
    
    with open('index.html', 'r') as html_file:
        html_content = html_file.read()
    
    response_content = html_content

    if request_args and 'message' in request_args:
        message = request_args['message']
        upload_to_bucket('link.txt', message, 'dl_cnn_a3_3dprintfail')
        response_content = 'now monitoring ' + message

    if request_args and 'emailAddress' in request_args:
        emailAddress = request_args['emailAddress']
        upload_to_bucket('email_address.txt', emailAddress, 'dl_cnn_a3_3dprintfail')
        response_content = 'sending alerts to ' + emailAddress
        
    
    return(response_content)

def upload_to_bucket(blob_name, content, bucket_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(content)

