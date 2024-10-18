# graphql_models.py
"""
`mongoengine`
- An Object-Document Mapper (ODM) for MongoDB in Python.
- Provides a high-level abstraction over the MongoDB native query language, 
allowing you to interact with the database using Python classes.
"""
from mongoengine import (DateTimeField, Document, EmbeddedDocument,
                         EmbeddedDocumentField, IntField, ListField,
                         ObjectIdField, StringField)

"""
`EmbeddedDocument`
- Represents a document that is meant to be embedded within other documents.(sub-document)
- It cannot exist independently in the database.
- It is a reusable schema that can be embedded in multiple parent documents.
"""
class UserInfo(EmbeddedDocument):
    user_id = StringField(required=True)
    user_name = StringField(required=True)

"""
`Document`
- Define a document as a Python class that inherits from `mongoengine.Document`. 
- Each field in the document is represented as a class attribute.
"""
class Post(Document):
    """
    `meta`
    - The meta attribute in a MongoEngine Document class is used to 
    define various options and configurations for the document.
    - By default, MongoEngine uses the class name as the collection name, 
    but you can specify a different collection name using the meta attribute.
    """
    meta = {"collection": "post"}
    # Domestic
    post_title = StringField(required=True, min_length=3, max_length=200)
    post_url = StringField()
    post_date = DateTimeField(required=True)
    content = StringField(required=True, min_length=1, max_length=1000)
    upvote = IntField(default=0, max_value=1000000)
    downvote = IntField(default=0, max_value=1000000)
    # Foreign
    poster_user_info = EmbeddedDocumentField(UserInfo)  # Information about the user who created the post
    comment_ids = ListField(ObjectIdField())            # A list of ObjectIds that reference Comment documents related to the post.
    # comment_ids = ListField(ReferenceField(Comment))
    all_comment_ids = ListField(ObjectIdField())        # Comments and nested comments

"""
`ObjectIdField`
- This line creates a list of ObjectId fields that store the IDs of documents.
- This design allows flexibility, 
where ObjectIds can be used directly without creating dependencies between models.
`ReferenceField(<DOCUMENT>)`
- This line creates a list of ReferenceField objects, which explicitly reference Documents.
"""
class Comment(Document):
    meta = {"collection": "comment"}
    post_id = ObjectIdField(required=True)              # An ObjectId that references the Post to which the comment belongs.
    commenter_info = EmbeddedDocumentField(UserInfo)    # Information about the user who made the comment.
    content = StringField(required=True, min_length=1, max_length=1000)
    comment_ids = ListField(ObjectIdField())            # A list of ObjectIds that could reference other Comment documents, 
                                                        # potentially for nested comments or replies.


class User(Document):
    meta = {"collection": "user"}
    user_id = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True, min_length=5, max_length=100)
    display_name = StringField(required=True, min_length=1, max_length=50)
    password = StringField(required=True, min_length=128)
