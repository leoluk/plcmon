import threading
import sys

from flask import Flask, abort, request
from flask_limiter import Limiter

from yowsup.config.manager import ConfigManager
from yowsup.profile.profile import YowProfile

import sendclient

# Start yowsup thread
config = ConfigManager().load(sys.argv[1])
profile = YowProfile(config.phone, config)
stack = sendclient.YowsupSendStack(profile)
worker = threading.Thread(target=stack.start)
worker.setDaemon(True)
worker.start()

# Set up Flask app
app = Flask(__name__)

# Set up rate limits as a safety guard in case the PLC goes crazy
limiter = Limiter(
    app, application_limits=["5 per minute"])


@app.route('/notifyGroup', methods=['POST'])
def notifyGroup():
    if not request.json or not request.json.get('message'):
        abort(400)

    stack.send_message(request.json['message'])
    return '{"status": "success"}'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
