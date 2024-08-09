# graphql_api.py
from flask import Blueprint
from flask_graphql import GraphQLView
from graphql_schema import schema       # E: Using the schema defined in `graphql_schema.py`

graphql_api = Blueprint("graphql_api", __name__)

graphql_api.add_url_rule(
    # E: A request is sent to `/graphql`
    "/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True)
)
