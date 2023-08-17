from django.test import TestCase
from django.urls import reverse
from .models import User, Post, Likes
from django.utils import timezone

class ModelsTestCase(TestCase):

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='testpassword1')
        self.user2 = User.objects.create_user(username='user2', password='testpassword2')

        # Create a test post
        self.post = Post.objects.create(user=self.user1, post='Test post content', timestamp=timezone.now())

        # Create a like
        self.like = Likes.objects.create(post=self.post, user=self.user2)

    def test_user_followers(self):
        self.user1.followers.add(self.user2)
        self.assertEqual(self.user1.followers.count(), 1)
        self.assertEqual(self.user2.following.count(), 1)

    def test_post_creation(self):
        self.assertEqual(self.post.user, self.user1)
        self.assertEqual(self.post.post, 'Test post content')

    def test_like_creation(self):
        self.assertEqual(self.like.post, self.post)
        self.assertEqual(self.like.user, self.user2)

    def test_user_unfollow(self):
        self.user1.followers.remove(self.user2)
        self.assertEqual(self.user1.followers.count(), 0)
        self.assertEqual(self.user2.following.count(), 0)

    def test_post_timestamp(self):
        self.assertIsNotNone(self.post.timestamp)


class ViewsTestCase(TestCase):
    def test_login_view(self):
        url = reverse("login")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        