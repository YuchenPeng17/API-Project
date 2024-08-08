## GraphQL

```python
# Python library for GraphQL APIs
import graphene
# lightweight web framework for Python
from flask import Flask
#  an extension for Flask that integrates GraphQL
from flask_graphql import GraphQLView
```

### 1. GraphQL Basics

GraphQL is a query language for APIs and a runtime for executing those queries by using a type system you define for your data. It allows clients to request <u>only the data they need</u>, making it more efficient than traditional REST APIs.

### 2. Defining Types

- In GraphQL, Types define the structure of the data objects that can be queried or mutated.
- Examples include `Blog`, `Comment`, `User`, etc.
- Each type specifies its fields and their data types, such as `id`, `title`, `content`, `author`, etc.

For example, we define a `Book` type:

```python
class Book(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    author = graphene.String()
```

By inheriting from `graphene.ObjectType`, you're telling `graphene` that the `Book` class is a GraphQL object that can have fields and can be part of the GraphQL schema.



### 3. Query Type

- The `Query` type is used to define how clients can read data from the API. 

- Each query corresponds to a resolver function that returns the requested data.
- **Field Name**: The name you give to the query field in the `Query` class. This is what clients use to query the data.
- **Resolver Function**: The function that fetches the data for the field. It follows the convention `resolve_FIELDNAME`, where `FIELDNAME` is the name of the field.

For example, here are the queries for the `book` type defined above.

- **`books`**: Returns a list of all books.
- **`book`**: Returns a single book based on the provided `id`.

```python
class Query(graphene.ObjectType):
    books = graphene.List(Book)
    book = graphene.Field(Book, id=graphene.Int())

    def resolve_books(self, info):
        print(f"Request context: {info.context}")
        print(f"Request headers: {info.context.headers}")
        return books

    def resolve_book(self, info, id):
        return next((book for book in books if book["id"] == id), None)
```

- Sample Queries

```
1. Get All Books
query {
  books {
    id
    title
    author
  }
}

2. Get a Book by ID
query {
  book(id: 1) {
    id
    title
    author
  }
}
```



### 4. Mutation Type

- Mutations define how clients can modify data on the server.
- Each mutation has <u>input arguments</u> and a <u>resolver function</u> that <u>performs the mutation</u> and <u>returns the result</u>.

- Using `lambda` allows you to reference types that might be defined later. 
- Returning the Class Itself: Provides the result of the mutation, allowing clients to see the output.

For example:

- **`CreateBook`**: Adds a new book to the list.

```python
class CreateBook(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        author = graphene.String()

    book = graphene.Field(lambda: Book)

    def mutate(self, info, title, author):
        new_book = {"id": len(books) + 1, "title": title, "author": author}
        books.append(new_book)
        return CreateBook(book=new_book)
```



### 5. Mutation Registration

- Register each mutation operation with the GraphQL schema.

For example:

```python
class Mutation(graphene.ObjectType):
    create_book = CreateBook.Field()
    update_book = UpdateBook.Field()
    delete_book = DeleteBook.Field()
```

- Naming conventions in GraphQL mutations

Using `snake_case` in the `Mutation` class fields in `graphene` is intentional to follow Python's naming conventions. 

When these are exposed in the GraphQL schema, they are converted to `camelCase`, making them align with standard GraphQL naming practices.

Example Queries:

```
3. Create a new book
mutation{
    createBook(title: "The Great Gatsby", author: "F. Scott Fitzgerald"){
        book{
            id
            title
            author
        }
    }
}

4. Update a book
mutation{
    updateBook(id: 3, title: "GraphQL Guide", author: "Alice Johnson"){
        book{
            id
            title
            author
        }
    }
}

5. Delete a book
mutation{
    deleteBook(id: 3){
        ok
    }
}
```



### 6. Schema Definition

- Combine the `Query` and `Mutation` classes to create a `graphene.Schema` object.

```python
schema = graphene.Schema(query=Query, mutation=Mutation)
```



### 7. Flask Integration

The Flask application serves the GraphQL endpoint at `/graphql`. 

The `GraphQLView` enables the GraphiQL interface for interactive queries:

```python
app = Flask(__name__)

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql", schema=schema, graphiql=True  # Enable the GraphiQL interface
    ),
)
```

**`app.add_url_rule("/graphql", ...)`:**

- Registers a new route (`/graphql`) in the Flask app.

**`GraphQLView.as_view(...)`:**

- Creates a view function for handling GraphQL requests.

**Parameters**:

- `"graphql"`: Name of the view.
- `schema=schema`: Specifies the GraphQL schema to use.
- `graphiql=True`: Enables the GraphiQL interface, an in-browser tool for testing GraphQL queries.



### 8. Running the Application

Finally, the application runs in debug mode, allowing developers to test the API locally:

```python
if __name__ == "__main__":
    app.run(debug=True)
```

