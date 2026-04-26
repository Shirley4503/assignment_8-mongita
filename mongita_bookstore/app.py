from flask import Flask, render_template, request, redirect, url_for
from mongita import MongitaClientDisk
import json
import os

app = Flask(__name__)

# ------------------------------------------
# Mongita Setup
# ------------------------------------------
client = MongitaClientDisk("mongita_data")
db = client.bookstore

categories_col = db.categories
books_col = db.books


# ------------------------------------------
# Helper Functions
# ------------------------------------------
def get_categories():
    categories = list(categories_col.find())
    return sorted(categories, key=lambda category: category["name"])


def get_books():
    books = list(books_col.find())
    return sorted(books, key=lambda book: book["title"])


def get_next_book_id():
    books = list(books_col.find())

    if not books:
        return 1

    return max(book["id"] for book in books) + 1


def get_category_name(category_id):
    category = categories_col.find_one({"id": category_id})

    if category:
        return category["name"]

    return ""


def clean_for_json(document):
    clean_document = {}

    for key, value in document.items():
        if key == "_id":
            clean_document[key] = str(value)
        else:
            clean_document[key] = value

    return clean_document


def export_json_files():
    categories = [clean_for_json(category) for category in categories_col.find()]
    books = [clean_for_json(book) for book in books_col.find()]

    with open("categories.json", "w") as categories_file:
        json.dump(categories, categories_file, indent=2)

    with open("books.json", "w") as books_file:
        json.dump(books, books_file, indent=2)


# ------------------------------------------
# Home Page
# Required route: /
# ------------------------------------------
@app.route("/")
def home():
    categories = get_categories()
    return render_template("index.html", categories=categories)


# ------------------------------------------
# Read All Books
# Required route: /read
# ------------------------------------------
@app.route("/read")
def read():
    categories = get_categories()
    books = get_books()

    return render_template(
        "read.html",
        categories=categories,
        books=books,
        searchTerm=None,
        nothingFound=False,
        pageTitle="All Books"
    )


# ------------------------------------------
# Category Filter
# Extra route for category browsing
# ------------------------------------------
@app.route("/category", methods=["GET"])
def category():
    categories = get_categories()
    category_id = request.args.get("categoryId", type=int)

    selected_category = categories_col.find_one({"id": category_id})
    books = list(books_col.find({"categoryId": category_id}))
    books = sorted(books, key=lambda book: book["title"])

    if selected_category:
        page_title = selected_category["name"]
    else:
        page_title = "Category"

    return render_template(
        "read.html",
        categories=categories,
        books=books,
        searchTerm=None,
        nothingFound=(len(books) == 0),
        pageTitle=page_title
    )


# ------------------------------------------
# Search Books
# Extra route for search bar
# ------------------------------------------
@app.route("/search", methods=["POST"])
def search():
    categories = get_categories()
    search_term = request.form.get("search", "").strip()

    all_books = get_books()
    books = [
        book for book in all_books
        if search_term.lower() in book["title"].lower()
    ]

    return render_template(
        "read.html",
        categories=categories,
        books=books,
        searchTerm=search_term,
        nothingFound=(len(books) == 0),
        pageTitle="Search Results"
    )


# ------------------------------------------
# Book Detail
# Extra route for single book page
# ------------------------------------------
@app.route("/book", methods=["GET"])
def book_detail():
    categories = get_categories()
    book_id = request.args.get("id", type=int)

    book = books_col.find_one({"id": book_id})

    if not book:
        return render_template(
            "error.html",
            categories=categories,
            error="This book could not be found in the haunted shelves."
        ), 404

    return render_template(
        "book_detail.html",
        categories=categories,
        book=book
    )


# ------------------------------------------
# Create Book Form
# Required route: /create
# ------------------------------------------
@app.route("/create")
def create():
    categories = get_categories()
    return render_template("create.html", categories=categories)


# ------------------------------------------
# Create Book Post
# Required route: /create_post
# ------------------------------------------
@app.route("/create_post", methods=["POST"])
def create_post():
    category_id = request.form.get("categoryId", type=int)
    category_name = get_category_name(category_id)
    new_id = get_next_book_id()

    new_book = {
        "id": new_id,
        "categoryId": category_id,
        "categoryName": category_name,
        "title": request.form.get("title", "").strip(),
        "author": request.form.get("author", "").strip(),
        "isbn": request.form.get("isbn", "").strip(),
        "price": request.form.get("price", type=float),
        "image": request.form.get("image", "").strip(),
        "readNow": request.form.get("readNow", type=int) or 0
    }

    books_col.insert_one(new_book)
    export_json_files()

    return redirect(url_for("read"))


# ------------------------------------------
# Edit Book Form
# Required route: /edit/<id>
# ------------------------------------------
@app.route("/edit/<int:id>")
def edit(id):
    categories = get_categories()
    book = books_col.find_one({"id": id})

    if not book:
        return render_template(
            "error.html",
            categories=categories,
            error="This book could not be found in the haunted shelves."
        ), 404

    return render_template("edit.html", categories=categories, book=book)


# ------------------------------------------
# Edit Book Post
# Required route: /edit_post/<id>
# ------------------------------------------
@app.route("/edit_post/<int:id>", methods=["POST"])
def edit_post(id):
    category_id = request.form.get("categoryId", type=int)
    category_name = get_category_name(category_id)

    books_col.update_one(
        {"id": id},
        {
            "$set": {
                "categoryId": category_id,
                "categoryName": category_name,
                "title": request.form.get("title", "").strip(),
                "author": request.form.get("author", "").strip(),
                "isbn": request.form.get("isbn", "").strip(),
                "price": request.form.get("price", type=float),
                "image": request.form.get("image", "").strip(),
                "readNow": request.form.get("readNow", type=int) or 0
            }
        }
    )

    export_json_files()

    return redirect(url_for("read"))


# ------------------------------------------
# Delete Book
# Required route: /delete/<id>
# ------------------------------------------
@app.route("/delete/<int:id>")
def delete(id):
    books_col.delete_one({"id": id})
    export_json_files()

    return redirect(url_for("read"))


# ------------------------------------------
# Error Handler
# ------------------------------------------
@app.errorhandler(Exception)
def handle_error(error):
    categories = get_categories()

    return render_template(
        "error.html",
        categories=categories,
        error=str(error)
    ), 500


# ------------------------------------------
# Run App
# ------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
