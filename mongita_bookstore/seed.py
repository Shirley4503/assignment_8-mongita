from mongita import MongitaClientDisk
import json

client = MongitaClientDisk("mongita_data")
db = client.bookstore

categories_col = db.categories
books_col = db.books

# Reset collections
categories_col.delete_many({})
books_col.delete_many({})

# -----------------------------
# CATEGORIES
# -----------------------------
categories_col.insert_many([
    {
        "id": 1,
        "name": "Gothic Horror"
    },
    {
        "id": 2,
        "name": "Ghost Stories"
    },
    {
        "id": 3,
        "name": "Dark Fantasy"
    },
    {
        "id": 4,
        "name": "Mystery and Suspense"
    }
])

# -----------------------------
# BOOKS
# -----------------------------
books_col.insert_many([
    {
        "id": 1,
        "categoryId": 1,
        "categoryName": "Gothic Horror",
        "title": "Dracula",
        "author": "Bram Stoker",
        "isbn": "9780486411095",
        "price": 8.99,
        "image": "dracula.jpg",
        "readNow": 1
    },
    {
        "id": 2,
        "categoryId": 1,
        "categoryName": "Gothic Horror",
        "title": "Frankenstein",
        "author": "Mary Shelley",
        "isbn": "9780486282114",
        "price": 7.99,
        "image": "frankenstein.jpg",
        "readNow": 1
    },
    {
        "id": 3,
        "categoryId": 2,
        "categoryName": "Ghost Stories",
        "title": "The Turn of the Screw",
        "author": "Henry James",
        "isbn": "9780486266848",
        "price": 6.99,
        "image": "turn_of_the_screw.jpg",
        "readNow": 0
    },
    {
        "id": 4,
        "categoryId": 2,
        "categoryName": "Ghost Stories",
        "title": "The Haunting of Hill House",
        "author": "Shirley Jackson",
        "isbn": "9780143039983",
        "price": 12.99,
        "image": "hill_house.jpg",
        "readNow": 1
    },
    {
        "id": 5,
        "categoryId": 3,
        "categoryName": "Dark Fantasy",
        "title": "Coraline",
        "author": "Neil Gaiman",
        "isbn": "9780380807345",
        "price": 9.99,
        "image": "coraline.jpg",
        "readNow": 0
    },
    {
        "id": 6,
        "categoryId": 4,
        "categoryName": "Mystery and Suspense",
        "title": "Rebecca",
        "author": "Daphne du Maurier",
        "isbn": "9780380730407",
        "price": 10.99,
        "image": "rebecca.jpg",
        "readNow": 0
    },
    {
        "id": 7,
        "categoryId": 1,
        "categoryName": "Gothic Horror",
        "title": "The Picture of Dorian Gray",
        "author": "Oscar Wilde",
        "isbn": "9780486278070",
        "price": 6.00,
        "image": "dorian_gray.jpg",
        "readNow": 1
    },
    {
        "id": 8,
        "categoryId": 1,
        "categoryName": "Gothic Horror",
        "title": "The Strange Case of Dr. Jekyll and Mr. Hyde",
        "author": "Robert Louis Stevenson",
        "isbn": "9780486266886",
        "price": 4.00,
        "image": "jekyll_hyde.jpg",
        "readNow": 0
    }
])


def prepare_for_json(document):
    clean_document = {}

    for key, value in document.items():
        if key == "_id":
            clean_document[key] = str(value)
        else:
            clean_document[key] = value

    return clean_document


categories = [prepare_for_json(category) for category in categories_col.find()]
books = [prepare_for_json(book) for book in books_col.find()]

with open("categories.json", "w") as categories_file:
    json.dump(categories, categories_file, indent=2)

with open("books.json", "w") as books_file:
    json.dump(books, books_file, indent=2)

print("The Haunted Bookstore Mongita database has been created.")
print("categories.json and books.json have been exported.")
