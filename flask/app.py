from flask import Flask, jsonify, request, send_from_directory
from re import match
from os import path, getenv
from TopUp import Uquid as TopUp
from UquidInfo import UquidOrders as UquidInfo
from SessionChecker import SessionChecker
from Telegram import Login as Telegram
app = Flask(__name__)

@app.route("/session")
def session_route():
    return jsonify({"is_active": SessionChecker().Check()})

@app.route("/login")
def login_route():
        if SessionChecker().Check():
            return jsonify({"status1": "You are already logged in."})
        Telegram().Login()
        return jsonify({"status": True})

@app.route("/balance")
def balance_route():
    if not SessionChecker().Check():
        Telegram().Login()
    return jsonify({"balance": UquidInfo().fetch_balance()})

@app.route("/orders")
def orders_route():
    if not SessionChecker().Check():
        Telegram().Login()
    return jsonify({"Orders": UquidInfo().fetch_orders_page()})

@app.route("/topup", methods=['POST'])
def topup_route():
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        destination_number = data.get("destination_number")
        value = str(data.get("value"))
        if not destination_number or not value:
            return jsonify({"error": "Missing required fields: destination_number, value"}), 400
        if not match(r"^01\d{9}$", destination_number):
            return jsonify({
                "status": False,
                "error_message": "Invalid phone number format. It must be 11 digits and start with '01'.",
                "details": ""
            }), 400
        if int(value) not in range(8, 201):
            return jsonify({
                "status": False,
                "error_message": "Invalid value. It must be an integer between 8 and 200.",
                "details": ""
            }), 400
        if not SessionChecker().Check():
            Telegram().Login()
        order_details = TopUp(f'+2{destination_number}', value).run()
        return jsonify({
            "status": True,
            "error_message": "",
            "order_details": order_details
        }), 200
    except Exception as e:
        return jsonify({"status": False, "error_message": str(e), "details": ""}), 400
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon'), 200
    
@app.route('/a')
def aa():
    cookies = getenv('Cookies')
    if cookies is not None:
        return loads(cookies)
    return send_from_directory(path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon'), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
