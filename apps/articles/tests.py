# Python modules
from io import BytesIO

# Django modules
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

# Third-party modules
from rest_framework import status
from rest_framework.test import APITestCase

# Project modules
from apps.articles.models import Article, Comment

User = get_user_model()


class ArticleTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@test.com', username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@test.com', username='user2', password='password123')
        self.admin = User.objects.create_superuser(email='admin@test.com', username='admin', password='password123')

        self.article1 = Article.objects.create(
            title='First Article',
            content='Content for first article',
            author=self.user1
        )
        self.article2 = Article.objects.create(
            title='Second Article',
            content='Content for second article',
            author=self.user2
        )

        self.list_url = reverse('article-list')
        self.detail_url = reverse('article-detail', kwargs={'slug': self.article1.slug})

    def test_list_articles(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_retrieve_article(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'First Article')
        self.assertEqual(response.data['author']['username'], 'user1')

    def test_create_article_unauthorized(self):
        data = {'title': 'New Article', 'content': 'New Content'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_article_authorized(self):
        self.client.force_authenticate(user=self.user1)
        data = {'title': 'New Article', 'content': 'New Content'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 3)
        self.assertEqual(response.data['author']['username'], 'user1')

    def test_update_article_owner(self):
        self.client.force_authenticate(user=self.user1)
        data = {'title': 'Updated Title', 'content': 'Updated Content'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article1.refresh_from_db()
        self.assertEqual(self.article1.title, 'Updated Title')

    def test_update_article_not_owner(self):
        self.client.force_authenticate(user=self.user2)
        data = {'title': 'Updated Title', 'content': 'Updated Content'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_update_article_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {'title': 'Admin Updated Title', 'content': 'Admin Updated Content'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_article(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.count(), 1)


class CommentTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@test.com', username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@test.com', username='user2', password='password123')
        self.article = Article.objects.create(title='Test Article', content='Content', author=self.user1)
        
        self.comment1 = Comment.objects.create(article=self.article, user=self.user1, content='Comment 1')
        self.comment2 = Comment.objects.create(article=self.article, user=self.user2, content='Comment 2')

        self.comments_url = reverse('article-comments', kwargs={'slug': self.article.slug})
        self.comment1_url = reverse('comment-detail', kwargs={'pk': self.comment1.id})

    def test_list_comments(self):
        response = self.client.get(self.comments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_comment_unauthorized(self):
        data = {'content': 'New Comment'}
        response = self.client.post(self.comments_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment_authorized(self):
        self.client.force_authenticate(user=self.user2)
        data = {'content': 'New Comment'}
        response = self.client.post(self.comments_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 3)
        self.assertEqual(response.data['user']['username'], 'user2')
        self.assertEqual(response.data['content'], 'New Comment')

    def test_update_comment_owner(self):
        self.client.force_authenticate(user=self.user1)
        data = {'content': 'Updated Comment 1'}
        response = self.client.patch(self.comment1_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment1.refresh_from_db()
        self.assertEqual(self.comment1.content, 'Updated Comment 1')

    def test_update_comment_not_owner(self):
        self.client.force_authenticate(user=self.user2)
        data = {'content': 'Updated Comment 1'}
        response = self.client.patch(self.comment1_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_comment_owner(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.comment1_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 1)


class MediaUploadTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user1@test.com', username='user1', password='password123')
        self.list_url = reverse('article-list')

    def test_upload_media_success(self):
        self.client.force_authenticate(user=self.user)
        
        image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'file_content',
            content_type='image/jpeg'
        )
        
        video_file = SimpleUploadedFile(
            name='test_video.mp4',
            content=b'video_content',
            content_type='video/mp4'
        )
        
        data = {
            'title': 'Media Article',
            'content': 'Content',
            'cover': image_file,
            'media_file': video_file
        }
        
        response = self.client.post(self.list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('cover', response.data)
        self.assertIn('media_file', response.data)
