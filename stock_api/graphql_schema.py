# graphql_schema.py
import graphene
from dateutil.parser import parse
from graphene import Boolean, Field, List, Mutation, ObjectType, String
from graphene_mongo import MongoengineObjectType
from graphql_models import Comment as CommentModel
from graphql_models import Post as PostModel
from graphql_models import User as UserModel
from graphql_models import UserInfo as UserInfoModel
from werkzeug.security import check_password_hash, generate_password_hash


class UserInfo(MongoengineObjectType):
    class Meta:
        model = UserInfoModel


class Post(MongoengineObjectType):
    class Meta:
        model = PostModel

    poster_user_info = Field(UserInfo)
    comment_ids = List(String)
    post_url = String()

    def resolve_poster_user_info(self, info):
        return self.poster_user_info

    def resolve_post_url(self, info):
        return self.post_url


class Comment(MongoengineObjectType):
    class Meta:
        model = CommentModel


class User(MongoengineObjectType):
    class Meta:
        model = UserModel


class RegisterUser(Mutation):
    class Arguments:
        user_id = String(required=True)
        email = String(required=True)
        display_name = String(required=True)
        password = String(required=True)

    user = Field(User)

    def mutate(self, info, user_id, email, display_name, password):
        hashed_password = generate_password_hash(password)
        user = UserModel(
            user_id=user_id,
            email=email,
            display_name=display_name,
            password=hashed_password,
        )
        user.save()
        return RegisterUser(user=user)


class Login(Mutation):
    class Arguments:
        user_id = String(required=True)
        password = String(required=True)

    user = Field(User)
    success = Boolean()

    def mutate(self, info, user_id, password):
        try:
            user = UserModel.objects.get(user_id=user_id)
            if check_password_hash(user.password, password):
                return Login(user=user, success=True)
            else:
                return Login(success=False)
        except UserModel.DoesNotExist:
            return Login(success=False)


class Query(ObjectType):
    posts = List(Post)
    post = Field(Post, id=String(required=True))
    comment = Field(Comment, id=String(required=True))

    posts_by_user = List(Post, user_id=String(required=True))

    def resolve_posts_by_user(self, info, user_id):
        return list(PostModel.objects(poster_user_info__user_id=user_id))

    def resolve_posts(self, info):
        return list(PostModel.objects.all().order_by("-post_date"))

    def resolve_post(self, info, id):
        return PostModel.objects.get(id=id)

    def resolve_comment(self, info, id):
        return CommentModel.objects.get(id=id)

    users = List(User)
    user = Field(User, id=String(required=True))

    def resolve_users(self, info):
        return list(UserModel.objects.all())

    def resolve_user(self, info, id):
        return UserModel.objects.get(user_id=id)

    is_user_registered = Field(
        Boolean,
        user_id=String(),
        email=String(),
        description="Check if a user with the given user_id or email is already registered",
    )

    def resolve_is_user_registered(self, info, user_id=None, email=None):
        if user_id:
            user_exists = UserModel.objects(user_id=user_id).first() is not None
        elif email:
            user_exists = UserModel.objects(email=email).first() is not None
        else:
            return False
        return user_exists

    comments = List(Comment, ids=List(String, required=True))

    def resolve_comments(self, info, ids):
        return list(CommentModel.objects(id__in=ids))


class UserInfoInput(graphene.InputObjectType):
    user_id = String(required=True)
    user_name = String(required=True)


class CreatePost(Mutation):
    class Arguments:
        userInfo = graphene.Argument(
            UserInfoInput, required=True
        )  # Use graphene.Argument instead of Field
        postDate = String(required=True)
        content = String(required=True)
        postTitle = String(required=True)
        postUrl = String()

    post = Field(Post)

    def mutate(self, info, userInfo, postDate, content, postTitle, postUrl):
        try:
            user_info = UserInfoModel(**userInfo)
            postDate = parse(postDate)
            post = PostModel(
                poster_user_info=user_info,
                post_date=postDate,
                content=content,
                post_title=postTitle,
                post_url=postUrl,
            )
            post.save()
            return CreatePost(post=post)
        except Exception as e:
            # Log the error
            print(f"Error creating post: {e}")
            raise


class CreateComment(Mutation):
    class Arguments:
        userInfo = graphene.Argument(UserInfoInput, required=True)
        content = String(required=True)
        targetId = String(required=True)
        postId = String(required=True)

    comment = Field(Comment)

    def mutate(self, info, userInfo, content, targetId, postId):
        user_info = UserInfoModel(**userInfo)
        comment = CommentModel(
            commenter_info=user_info, content=content, post_id=postId
        )
        comment.save()

        # Check if targetId is a Post id
        try:
            target_post = PostModel.objects.get(id=targetId)
            target_post.update(push__comment_ids=comment.id)
            target_post.reload()
        except PostModel.DoesNotExist:
            pass

        # Check if targetId is a Comment id
        try:
            target_comment = CommentModel.objects.get(id=targetId)
            target_comment.update(push__comment_ids=comment.id)
            target_comment.reload()
        except CommentModel.DoesNotExist:
            pass

        # Update post all comment ids
        try:
            target_post = PostModel.objects.get(id=postId)
            target_post.update(push__all_comment_ids=comment.id)
            target_post.reload()
        except PostModel.DoesNotExist:
            pass

        return CreateComment(comment=comment)


class UpvotePost(Mutation):
    class Arguments:
        post_id = String(required=True)

    post = Field(Post)

    def mutate(self, info, post_id):
        post = PostModel.objects.get(id=post_id)
        post.update(upvote=post.upvote + 1)
        post.reload()
        return UpvotePost(post=post)


class DeletePost(Mutation):
    class Arguments:
        post_id = String(required=True)
        user_id = String(required=True)

    success = Boolean()

    def mutate(self, info, post_id, user_id):
        post = PostModel.objects.get(id=post_id)
        if post.poster_user_info.user_id == user_id:
            post.delete()
            return DeletePost(success=True)
        else:
            return DeletePost(success=False)


class DownvotePost(Mutation):
    class Arguments:
        post_id = String(required=True)

    post = Field(Post)

    def mutate(self, info, post_id):
        post = PostModel.objects.get(id=post_id)
        post.update(downvote=post.downvote + 1)
        post.reload()
        return DownvotePost(post=post)


class Mutation(ObjectType):
    create_post = CreatePost.Field()
    create_comment = CreateComment.Field()
    upvote_post = UpvotePost.Field()
    downvote_post = DownvotePost.Field()
    register_user = RegisterUser.Field()
    login = Login.Field()
    delete_post = DeletePost.Field()

# E: Queries or mutations defined in the schema
# E: Tnteract with the models in `graphql_models.py` to fetch or modify data
schema = graphene.Schema(query=Query, mutation=Mutation)
