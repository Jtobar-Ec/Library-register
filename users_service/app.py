from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host='users_db', database='users_db', user='myuser', password='mypassword')
    return conn

@app.route('/get_users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id = %s;', (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        column_names = [desc[0] for desc in cur.description]
        user_data = dict(zip(column_names, user))
        return jsonify(user_data), 200
    else:
        return '', 404
    
@app.route('/get_users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users;')
    users = cur.fetchall()
    cur.close()
    conn.close()
    if users:
        column_names = [desc[0] for desc in cur.description]
        users_list = [dict(zip(column_names, user)) for user in users]
        return jsonify(users_list), 200
    else:
        return jsonify([]), 200

@app.route('/users', methods=['POST'])
def add_user():
    new_user = request.get_json()
    name = new_user['name']
    email = new_user['email']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id', (name, email))
    new_user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return '', 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    updated_user = request.get_json()
    name = updated_user['name']
    email = updated_user['email']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE users SET name = %s, email = %s WHERE id = %s', (name, email, user_id))
    conn.commit()
    cur.close()
    conn.close()
    
    return '', 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
