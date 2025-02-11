from flask import Flask, jsonify, send_from_directory
from os import path
from SessionChecker import SessionChecker
from Telegram import Login as Telegram
app = Flask(__name__)

@app.route("/session")
def session_route():
    return jsonify({"is_active": SessionChecker().Check()})

@app.route("/login")
def login_route():
        if SessionChecker().Check():
            return jsonify({"status": "You are already logged in."})
        Telegram().Login()
        return jsonify({"status": True})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon'), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
