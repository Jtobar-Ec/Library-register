from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host='books_db', database='books_db', user='myuser', password='mypassword')
    return conn

@app.route('/get_books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM books WHERE id = %s;', (book_id,))
    book = cur.fetchone()
    cur.close()
    conn.close()
    if book:
        column_names = [desc[0] for desc in cur.description]
        book_data = dict(zip(column_names, book))
        return jsonify(book_data), 200
    else:
        return '', 404
    
@app.route('/get_books', methods=['GET'])
def get_books():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM books;')
    books = cur.fetchall()
    cur.close()
    conn.close()
    if books:
        column_names = [desc[0] for desc in cur.description]
        books_list = [dict(zip(column_names, book)) for book in books]
        return jsonify(books_list), 200
    else:
        return jsonify([]), 200

@app.route('/books', methods=['POST'])
def add_book():
    new_book = request.get_json()
    title = new_book['title']
    author = new_book['author']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO books (title, author) VALUES (%s, %s) RETURNING id', (title, author))
    new_book_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return '', 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    updated_book = request.get_json()
    title = updated_book['title']
    author = updated_book['author']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE books SET title = %s, author = %s WHERE id = %s', (title, author, book_id))
    conn.commit()
    cur.close()
    conn.close()
    
    return '', 200

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM books WHERE id = %s', (book_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
