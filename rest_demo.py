from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample data
books = [
    {"id": 1, "title": "Python Essentials", "author": "Jane Doe"},
    {"id": 2, "title": "Flask for Beginners", "author": "John Smith"},
]


# GET all books
@app.route("/books", methods=["GET"])
def get_books():
    return jsonify({"books": books})


# GET a single book by ID
@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = next((book for book in books if book["id"] == book_id), None)
    return jsonify({"book": book}) if book else ("", 404)


# POST a new book
@app.route("/books", methods=["POST"])
def add_book():
    new_book = request.get_json()
    books.append(new_book)
    return jsonify({"message": "Book added successfully", "book": new_book}), 201


# PUT to update a book by ID
@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = next((book for book in books if book["id"] == book_id), None)
    if book:
        data = request.get_json()
        book.update(data)
        return jsonify({"message": "Book updated successfully", "book": book})
    return ("", 404)


# DELETE a book by ID
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    global books
    books = [book for book in books if book["id"] != book_id]
    return jsonify({"message": "Book deleted successfully"}), 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)
