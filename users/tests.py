from django.test import TestCase
from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.contrib.auth import authenticate
from feed.models import Post, Comment, Like
from feed.models import timezone
from users.models import FriendRequest, Profile
from users.views import *


# test cases for login/registration
class SigninTest(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='12test12', email='test@example.com')
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_correct(self):
        user = authenticate(username='test', password='12test12')
        self.assertTrue((user is not None) and user.is_authenticated)

    def test_wrong_username(self):
        user = authenticate(username='wrong', password='12test12')
        self.assertFalse(user is not None and user.is_authenticated)

    def test_wrong_pssword(self):
        user = authenticate(username='test', password='wrong')
        self.assertFalse(user is not None and user.is_authenticated)


# test cases for post creation
class TestPost(TestCase):
    def setUp(self):
        user = User(username='test')
        user.save()
        self.post = Post.objects.create(
            username=user,
            description='test post',
            pic=None,
            date_posted=timezone.now())

        self.post.save()

    def tearDown(self):
        self.post.delete()

    # test that post was created
    def test_post_valid(self):
        post_count = Post.objects.all().count()
        self.assertEqual(post_count, 1)

    # test that username field was created and stored
    def test_post_name(self):
        post = Post.objects.get(pk=1)
        field = post._meta.get_field('username').verbose_name
        self.assertEquals(field, 'username')

    # test that post description was created and stored
    def test_post_description(self):
        post = Post.objects.get(pk=1)
        description = post.description
        self.assertEquals(description, post.description)


# test cases for friend requests
class TestFriendRequest(TestCase):
    def setUp(self):
        self.user = User(username='test')
        self.user.save()
        self.user2 = User(username='test2')
        self.user2.save()

    def tearDown(self):
        self.user.delete()
        self.user2.delete()

    # test if friend request is valid
    def test_valid_fr(self):
        request = FriendRequest.objects.create(
            to_user=self.user2,
            from_user=self.user)
        sent = request.__str__()
        self.assertEquals(sent, "From test, to test2")

    # test if friend request is invalid
    def test_invalid_fr(self):
        request = FriendRequest.objects.create(
            to_user=self.user2,
            from_user=self.user)
        sent = request.__str__()
        self.assertFalse(sent is "From test, to test2")

    # test if friend request is accepted
    def test_accept_fr(self):
        accept_friend_request(self.request, self.request.id)
        self.assertEquals(self.user.profile.friends.count(), 1)
        self.assertEquals(self.user2.profile.friends.count(), 1)