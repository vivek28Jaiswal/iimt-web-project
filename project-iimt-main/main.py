from flask import Flask, send_from_directory, request, jsonify
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
base_directory = os.path.dirname(os.path.abspath(__file__))
db_config = {
    'user': os.getenv("DATABASE_USER"), 
    'password': os.getenv("DATABASE_PASSWORD"), 
    'host': os.getenv("DATABASE_HOST"),   
    'database': os.getenv("DATABASE_NAME")
}
def create_connection():
    """Create a database connection."""
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection
@app.route('/')
def serve_index():
    return send_from_directory(base_directory, 'index.htm')
@app.route('/courses')
def serve_course_page():
    return send_from_directory(base_directory, 'courses.htm')
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    assets_directory = os.path.join(base_directory, 'assets')
    return send_from_directory(assets_directory, filename)
@app.route('/fonts/<path:filename>')
def serve_fonts(filename):
    fonts_directory = os.path.join(base_directory, 'fonts')
    return send_from_directory(fonts_directory, filename)
@app.route('/<path:filename>')
def serve_files(filename):
    return send_from_directory(base_directory, filename)
@app.route('/register', methods=['POST'])
def register_user():
    name = request.json.get('name')
    email = request.json.get('email')
    phone = request.json.get('phone')
    program = request.json.get('program')
    username = request.json.get('username')
    password = request.json.get('password')
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO user (name, email,phone, program,username,password) VALUES (%s, %s,%s, %s,%s, %s)", 
                       (name, email,phone, program,username,password))
        connection.commit()
        return jsonify({"success": True, "message": "Registration successful!"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()
@app.route('/login', methods=['POST'])
def login_user():
    username = request.json.get('username')
    password = request.json.get('password')
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", 
                       (username, password))
        user = cursor.fetchone()
        if user:
            return jsonify({"success": True, "message": "Login successful!"}), 201
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    finally:
        cursor.close()
        connection.close()
@app.route('/admission', methods=['POST'])
def create_admission():
    name = request.json.get('name')
    email = request.json.get('email')
    phone = request.json.get('phone')
    program = request.json.get('program')
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO admission (name, email,phone, program) VALUES (%s, %s,%s, %s)", 
                       (name, email,phone, program))
        connection.commit()
        return jsonify({"message": "Admission request submitted successfully"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()
@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    username = request.args.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Username is required.'}), 400
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT name, email, phone, program FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            return jsonify({
                'success': True,
                'name': user[0],
                'email': user[1],
                'phone': user[2],
                'program': user[3]
            })
        return jsonify({'success': False, 'message': 'User not found.'}), 404
    finally:
        cursor.close()
        connection.close()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)