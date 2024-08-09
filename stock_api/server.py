from mongoengine import connect

# Define the MongoDB connection settings
MONGODB_SETTINGS = {"db": "StockInfoDB", "host": "mongodb://localhost:27017"}

# Connect to the MongoDB database using the connection settings
connect(**MONGODB_SETTINGS)

from flask import Flask
from flask_cors import CORS
from graphql_api import graphql_api
from rest_api import rest_api

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(rest_api, url_prefix="/api")
app.register_blueprint(graphql_api)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
