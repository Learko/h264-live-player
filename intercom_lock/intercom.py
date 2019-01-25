#!/usr/bin/env python3

import firebase_admin
from firebase_admin import credentials

from requests import Session
from socket import create_connection


def get_ip_address():
    with create_connection(('1.1.1.1', 80)) as conn:
        return conn.getsockname()[0]


firebase_key_path = 'intercom3-d6b86-firebase-adminsdk-z563j-9d732421e9.json'

path = 'https://fcm.googleapis.com/v1/projects/'
app_name = 'intercom3-d6b86'
method = '/messages:send'

video_stream_port = 8080
audio_stream_port = 8081


if __name__ == '__main__':
    cred = credentials.Certificate(firebase_key_path)
    app = firebase_admin.initialize_app(cred)
    access_token = app.credential.get_access_token().access_token

    url = f'{path}{app_name}{method}'

    sess = Session()
    sess.headers['Authorization'] = f'Bearer {access_token}'

    ip = get_ip_address()
    print(f'public ip: {ip}')

    pl = {
        'message': {
            'topic': 'all',
            'data': {
                'title': 'Hi there',
                'body': 'You have a guest!',
                'video_stream': f'http://{ip}:{video_stream_port}',
                'audio_stream': f'http://{ip}:{audio_stream_port}/audio.wav'
            }
        }
    }

    r = sess.post(url, json=pl)
    print(f'{r.status_code} {r.reason}')
    print(r.text)

    firebase_admin.delete_app(app)
