from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Post, Likes
from django.utils import timezone
import json

# Models
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

# Views
class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.creator = User.objects.create_user(username='creatoruser', password='creatorpassword')
        self.post = Post.objects.create(user=self.creator, post='Test post')
        self.index_url = reverse('index')
        self.profile_url = reverse('profile_view', args=(self.creator.id,))
        self.following_url = reverse('following')
        self.edit_post_url = reverse('edit_post')
        self.like_post_url = reverse('like_post')

    def test_index_view_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'network/index.html')

    def test_profile_view_authenticated_user_follow(self):
        self.client.login(username='testuser', password='testpassword')
        self.assertFalse(self.creator.followers.filter(id=self.user.id).exists())

        response = self.client.post(self.profile_url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.creator.followers.filter(id=self.user.id).exists())

    def test_profile_view_authenticated_user_unfollow(self):
        self.creator.followers.add(self.user)
        self.client.login(username='testuser', password='testpassword')
        self.assertTrue(self.creator.followers.filter(id=self.user.id).exists())

        response = self.client.post(self.profile_url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.creator.followers.filter(id=self.user.id).exists())

    def test_following_view_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.following_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'network/following.html')

    def test_edit_post_view(self):
        self.client.login(username='testuser', password='testpassword')
        new_post_content = 'Edited content'

        response = self.client.post(
            self.edit_post_url,
            json.dumps({'id': self.post.id, 'post': new_post_content}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], new_post_content)
        self.post.refresh_from_db()
        self.assertEqual(self.post.post, new_post_content)

    def test_like_post(self):
        self.client.login(username='testuser', password='testpassword')
        
        initial_likes_count = Likes.objects.filter(post=self.post).count()

        response = self.client.post(
            self.like_post_url,
            json.dumps({'post_id': self.post.id, 'user_id': self.user.id}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['new_likes_count'], initial_likes_count + 1)
        self.assertEqual(response_data['like_btn_value'], 'Unlike')
        
    def test_unlike_post(self):
        self.client.login(username='testuser', password='testpassword')
        
        Likes.objects.create(post=self.post, user=self.user)

        initial_likes_count = Likes.objects.filter(post=self.post).count()

        response = self.client.post(
            self.like_post_url,
            json.dumps({'post_id': self.post.id, 'user_id': self.user.id}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['new_likes_count'], initial_likes_count - 1)
        self.assertEqual(response_data['like_btn_value'], 'Like')
        
    def test_unlike_post_after_liking(self):
        self.client.login(username='testuser', password='testpassword')
        Likes.objects.create(post=self.post, user=self.user)
        
        initial_likes_count = Likes.objects.filter(post=self.post).count()

        response = self.client.post(
            self.like_post_url,
            json.dumps({'post_id': self.post.id, 'user_id': self.user.id}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['new_likes_count'], initial_likes_count - 1)
        self.assertEqual(response_data['like_btn_value'], 'Like')
        

    def test_like_post_view_invalid_request(self):
        response = self.client.get(self.like_post_url)

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)

    def test_login_view_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })

        self.assertRedirects(response, reverse('index'))

    def test_login_view_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username and/or password.')

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('index'))

    def test_register_view_valid_data(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword',
            'confirmation': 'newpassword'
        })

        self.assertRedirects(response, reverse('index'))

    def test_register_view_passwords_do_not_match(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword',
            'confirmation': 'mismatchedpassword'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords must match.')

    def test_register_view_existing_username(self):
        User.objects.create_user(username='existinguser', password='existingpassword')

        response = self.client.post(reverse('register'), {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password': 'newpassword',
            'confirmation': 'newpassword'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username already taken.')