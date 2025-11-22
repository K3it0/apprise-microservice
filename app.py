import apprise
import os
from flask import Flask, request

envURL = os.environ.get('NOTIFICATION_URLS')
envURLFile = os.environ.get('NOTIFICATION_URLS_FILE')

urls = envURL

if not envURL and envURLFile and os.path.exists(envURLFile):
    with open(envURLFile, 'r') as secrets_file:
        urls = secrets_file.read()

apobj = apprise.Apprise()
apobj.add(urls)

app = Flask(__name__)

lastMessages = dict()

@app.route('/', methods=['POST'])
def notify_post():
    data = request.get_json(force=True)
    send = True
    if 'id' in data:
        state = data['state'] if 'state' in data else {'title': data['title'], 'body': data['body']}
        send = ('forceSend' in data and data['forceSend'] == 'true') or (not (data['id'] in lastMessages and lastMessages[data['id']] == state))
        lastMessages[data['id']] = state

    if send:
        apobj.notify(
            title=data['title'],
            body=data['body'],
            notify_type=data.get('notify_type', None),
        )
    return 'ok' if send else 'deduplicated'
