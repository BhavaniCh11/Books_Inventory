from flask import Flask, request, jsonify, render_template, make_response
import mysql.connector
import csv
import json
import io  # Import io module for StringIO
from datetime import datetime  # Import datetime for date handling

app = Flask(__name__)

# Database connection
db_connection = mysql.connector.connect(
    host="35.232.48.210",  # Replace with your MySQL host
    user="bhavaniuser",  # Replace with your MySQL username
    password="userbhavani",  # Replace with your MySQL password
    database="book_inventory"  # Your MySQL database name
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    genre = request.form['genre']
    publication_date = request.form['publication_date']  # Ensure this is in the correct format
    isbn = request.form['isbn']
    cursor = db_connection.cursor()
    query = "INSERT INTO Inventory (Title, Author, Genre, PublicationDate, ISBN) VALUES (%s, %s, %s, %s, %s)"
    values = (title, author, genre, publication_date, isbn)
    cursor.execute(query, values)
    db_connection.commit()
    cursor.close()
    return jsonify({"message": "Book added successfully!"}), 201

@app.route('/filter_books', methods=['GET'])
def filter_books():
    title = request.args.get('title')
    author = request.args.get('author')
    genre = request.args.get('genre')
    query = "SELECT * FROM Inventory WHERE 1=1"
    filters = []
    if title:
        query += " AND Title LIKE %s"
        filters.append(f'%{title}%')
    if author:
        query += " AND Author LIKE %s"
        filters.append(f'%{author}%')
    if genre:
        query += " AND Genre LIKE %s"
        filters.append(f'%{genre}%')
    
    cursor = db_connection.cursor()
    cursor.execute(query, filters)
    results = cursor.fetchall()
    cursor.close()
    
    # Convert results to a list of dictionaries for JSON response
    books = [
        {
            "EntryID": row[0],
            "Title": row[1],
            "Author": row[2],
            "Genre": row[3],
            "PublicationDate": row[4].strftime("%Y-%m-%d") if isinstance(row[4], (datetime,)) else str(row[4]),
            "ISBN": row[5]
        } for row in results
    ]
    return jsonify(books)

@app.route('/export_books', methods=['GET'])
def export_books():
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM Inventory")
    rows = cursor.fetchall()
    cursor.close()
    output_format = request.args.get('format', 'csv')  # Default to CSV

    if output_format == 'csv':
        # Use StringIO to create a file-like object
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['EntryID', 'Title', 'Author', 'Genre', 'PublicationDate', 'ISBN'])
        
        # Write each row, converting datetime to string where necessary
        for row in rows:
            publication_date = row[4].strftime("%Y-%m-%d") if isinstance(row[4], (datetime,)) else str(row[4])
            writer.writerow([row[0], row[1], row[2], row[3], publication_date, row[5]])
        
        # Get the CSV string from the StringIO object
        output.seek(0)  # Go to the start of the StringIO object
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=books.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response
    else:
        # Handle JSON export
        books = []
        for row in rows:
            books.append({
                "EntryID": row[0],
                "Title": row[1],
                "Author": row[2],
                "Genre": row[3],
                "PublicationDate": row[4].strftime("%Y-%m-%d") if isinstance(row[4], (datetime,)) else str(row[4]),
                "ISBN": row[5]
            })
        
        # Convert the list of dictionaries to JSON and prepare for download
        json_output = json.dumps(books, indent=4)  # Use indent for pretty printing
        response = make_response(json_output)
        response.headers['Content-Disposition'] = 'attachment; filename=books.json'
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/get_all_books', methods=['GET'])
def get_all_books():
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM Inventory")
    rows = cursor.fetchall()
    cursor.close()
    
    books = [
        {
            "EntryID": row[0],
            "Title": row[1],
            "Author": row[2],
            "Genre": row[3],
            "PublicationDate": row[4].strftime("%Y-%m-%d") if isinstance(row[4], (datetime,)) else str(row[4]),
            "ISBN": row[5]
        } for row in rows
    ]
    return jsonify(books)

if __name__ == '__main__':
    app.run(debug=True)
