import logging
import zipfile

from flask import Flask, request, render_template, redirect, url_for
from envs import aws_secret, aws_access

import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

BOTO_S3_BUCKET = 'se-saves'
S3_CLIENT = boto3.client('s3', aws_access_key_id=aws_access, aws_secret_access_key=aws_secret)


def list_saves():
    saves = []
    try:
      for key in S3_CLIENT.list_objects(Bucket=BOTO_S3_BUCKET)['Contents']:
          saves.append(key['Key'])
    except ClientError as e:
        logging.error(e)
        print('Exception: {}'.format(e))
        return False 

    print('returning {}, length: {}'.format(saves, len(saves)))
    return saves

def upload_save(file):
    try:
        file_name = file.filename
        file.save(file_name)
        response = S3_CLIENT.upload_file(Key=file_name, Bucket=BOTO_S3_BUCKET, Filename=file_name)
    except ClientError as e:
        logging.error(e)
        print('Exception: {}'.format(e))
        return False
  
    return True

@app.route('/success')
def success():
    print('success')
    success_template = 'success.html' 
    template_data = {'saves': list_saves()}
    return render_template(success_template, **template_data)


@app.route('/upload', methods = ['POST'])
def upload():
    if not request.files:
        print('no files found {}'.format(request))
    else:
        upload_save(request.files['file'])
    return redirect(url_for('success'))


@app.route('/')
def respond():
    index_template = 'index.html'
    saves = list_saves()
    template_data = {'saves': saves}

    return render_template(index_template, **template_data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
