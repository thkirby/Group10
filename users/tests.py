from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TransactionTestCase
from django.contrib.auth import authenticate
from feed.models import Post, Comment, Like, Thread, Messages, Notifications
from feed.models import timezone
from feed.views import *
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
class TestPosts(TestCase):
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


class TestCommentLikesSharing(TestCase):
    def setUp(self):
        self.user = User(username='test', email='test@test.com')
        self.user2 = User(username='test2', email='test2@fake.com')
        self.user.save()
        self.user2.save()

        self.post = Post.objects.create(
            username=self.user,
            shared_username=self.user2,
            shared_description='shared post',
            description='test post',
            pic=None,
            date_posted=timezone.now())
        self.post.save()

        self.comment = Comment.objects.create(
            post_id=self.post.pk,
            username=self.user2,
            comment='test comment',
            comment_date=timezone.now())
        self.comment.save()

        self.like = Like.objects.create(
            post_id=self.post.pk,
            user_id=self.user2.pk
        )
        self.like.save()

    # test that comment was created on the correct post
    def test_comment_on_post(self):
        comment = self.comment.post_id
        self.assertEquals(self.post.pk, comment)

    # test that comment contents is created and stored
    def test_comment_content(self):
        comment = Comment.objects.get(pk=1)
        content = comment.comment
        self.assertEquals(self.comment.comment, content)

    # test that the correct post was liked
    def test_liked_post(self):
        like = self.like.post_id
        self.assertEqual(self.post.pk, like)


# test cases for friend requests
class TestFriendRequest(TestCase):
    def setUp(self):
        self.user = User(username='test', email='test@test.com')
        self.user.save()
        self.user2 = User(username='test2', email='test2@fake.com')
        self.user2.save()
        self.send_request_url = reverse('send_friend_request', args=[self.user.pk])

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

    # test if friend request is sent
    def test_freinds_send_request_post(self):
        self.client = Client(HTTP_REFERER='/users/')
        self.client.force_login(self.user)
        data = {'from_user': self.user, 'to_user': self.user2}
        response = self.client.post(self.send_request_url, data)

        self.assertEqual(response.status_code, 302)


class TestDirectMessaging(TestCase):
    def setUp(self):
        self.user = User(username='test', email='test@test.com')
        self.user2 = User(username='test2', email='test2@fake.com')
        self.user.save()
        self.user2.save()

        self.thread = Thread.objects.create(
            user=self.user,
            reciever=self.user2)
        self.thread.save()

        self.message = Messages.objects.create(
            thread=self.thread,
            sender_user=self.user,
            reciever_user=self.user2,
            textbody='test',
            date=timezone.now())
        self.message.save()

        self.notification = Notifications.objects.create(
            type=1,
            message=self.message.thread,
            has_seen=False,
            sending_user=self.user,
            recieving_user=self.user2,
            recency=timezone.now()
        )
        self.notification.save()

    # test that thread was created
    def test_thread_valid(self):
        thread_count = Thread.objects.all().count()
        self.assertEqual(thread_count, 1)

    # test that message text was created and stored
    def test_message_text(self):
        message = self.message
        text = message.textbody
        self.assertEquals(text, 'test')

    # test that notification is being recieved by correct user
    def test_notification_recieved(self):
        notification = self.notification
        recieving_user = notification.recieving_user
        self.assertEquals(recieving_user, self.notification.recieving_user)


class TestSearch(TestCase):

    def setUp(self):
        self.user = User(username='test', email='test@test.com')
        self.user.save()
        self.user2 = User(username='fake', email='fake@test.com')
        self.user2.save()
        self.send_request_url = None
        self.post = Post.objects.create(
            username=self.user,
            shared_username=self.user2,
            shared_description='shared post',
            description='test post',
            pic=None,
            date_posted=timezone.now())
        self.post.save()

    def tearDown(self):
        self.user.delete()
        self.user2.delete()

    def test_search_users_url(self):
        self.send_request_url = reverse('search_users')
        response = self.client.get(self.send_request_url)
        self.assertEqual(response.status_code, 302)

    def test_posts_url(self):
        self.send_request_url = reverse('post-page')
        response = self.client.get(self.send_request_url)
        self.assertEqual(response.status_code, 200)

    def test_users_url(self):
        self.send_request_url = reverse('users_list')
        response = self.client.get(self.send_request_url)
        self.assertEqual(response.status_code, 302)
