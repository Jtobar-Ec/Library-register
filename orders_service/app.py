from flask import Flask, request, jsonify
import psycopg2
import requests

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host='orders_db', database='orders_db', user='myuser', password='mypassword')
    return conn

def validate_book(book_id):
    conn = psycopg2.connect(host='books_db', database='books_db', user='myuser', password='mypassword')
    cur = conn.cursor()
    cur.execute('SELECT EXISTS(SELECT 1 FROM books WHERE id = %s)', (book_id,))
    exists = cur.fetchone()[0]
    cur.close()
    conn.close()
    return exists

def validate_user(user_id):
    conn = psycopg2.connect(host='users_db', database='users_db', user='myuser', password='mypassword')
    cur = conn.cursor()
    cur.execute('SELECT EXISTS(SELECT 1 FROM users WHERE id = %s)', (user_id,))
    exists = cur.fetchone()[0]
    cur.close()
    conn.close()
    return exists

@app.route('/get_orders', methods=['GET'])
def get_orders():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT o.id AS order_id, 
               o.id_books AS book_id, 
               o.id_users AS user_id
        FROM orders o;
    ''')
    orders = cur.fetchall()
    cur.close()
    conn.close()

    orders_list = []
    for order in orders:
        order_id, book_id, user_id = order
        
        # Cambia 'localhost' por 'books_service'
        book_response = requests.get(f'http://books_service:5001/get_books/{book_id}')
        book_data = book_response.json() if book_response.status_code == 200 else None
        
        # Cambia 'localhost' por 'users_service'
        user_response = requests.get(f'http://users_service:5002/get_users/{user_id}')
        user_data = user_response.json() if user_response.status_code == 200 else None

        orders_list.append({
            'order_id': order_id,
            'book_id': book_id,
            'title': book_data.get('title') if book_data else None,
            'author': book_data.get('author') if book_data else None,
            'user_id': user_id,
            'name': user_data.get('name') if user_data else None,
            'email': user_data.get('email') if user_data else None,
        })

    return jsonify(orders_list)


@app.route('/orders', methods=['POST'])
def add_order():
    new_order = request.get_json()
    id_books = new_order['id_books']
    id_users = new_order['id_users']
    
    # Validar que el id_books y id_users existen
    if not validate_book(id_books):
        return jsonify({'error': 'Book ID does not exist'}), 400
    if not validate_user(id_users):
        return jsonify({'error': 'User ID does not exist'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO orders (id_books, id_users) VALUES (%s, %s) RETURNING id', (id_books, id_users))
    new_order_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'id': new_order_id}), 201

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    updated_order = request.get_json()
    id_books = updated_order['id_books']
    id_users = updated_order['id_users']
    
    # Validar que el id_books y id_users existen
    if not validate_book(id_books):
        return jsonify({'error': 'Book ID does not exist'}), 400
    if not validate_user(id_users):
        return jsonify({'error': 'User ID does not exist'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE orders SET id_books = %s, id_users = %s WHERE id = %s', (id_books, id_users, order_id))
    conn.commit()
    cur.close()
    conn.close()
    
    return '', 200

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM orders WHERE id = %s', (order_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
