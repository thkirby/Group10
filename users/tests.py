from django.test import TestCase
from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.contrib.auth import authenticate
from feed.models import Post
from feed.models import timezone


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

# test that username was created and stored
    def test_post_name(self):
        post = Post.objects.get(pk=1)
        field = post._meta.get_field('username').verbose_name
        self.assertEquals(field, 'username')

    # test that username was created and stored
    def test_post_description(self):
        post = Post.objects.get(pk=1)
        field = post._meta.get_field('description').verbose_name
        self.assertEquals(field, 'description')
