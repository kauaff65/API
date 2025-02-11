from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# دالة لتعيين المتغير البيئي
def set_env_variable(name, value):
    os.environ[name] = value

# دالة لاسترجاع المتغير البيئي
def get_env_variable(name):
    return os.getenv(name)

# Endpoint لتعيين متغير بيئي
@app.route('/set_variable', methods=['POST'])
def set_variable():
    data = request.json  # الحصول على البيانات من الطلب بصيغة JSON
    name = data.get('name')
    value = data.get('value')

    if not name or not value:
        return jsonify({"error": "Both 'name' and 'value' are required"}), 400

    set_env_variable(name, value)
    return jsonify({"message": f"Environment variable '{name}' set to '{value}'"}), 200

# Endpoint لاسترجاع المتغير البيئي
@app.route('/get_variable', methods=['GET'])
def get_variable():
    name = request.args.get('name')

    if not name:
        return jsonify({"error": "'name' parameter is required"}), 400

    value = get_env_variable(name)
    if value is None:
        return jsonify({"error": f"Environment variable '{name}' not found"}), 404

    return jsonify({"name": name, "value": value}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
