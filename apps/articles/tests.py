# Django modules
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Third-party modules
from rest_framework import status
from rest_framework.test import APITestCase

# Project modules
from apps.articles.models import Comment, Question
from apps.courses.models import Category

User = get_user_model()


class QuestionModelTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(email='author@test.com', username='author', password='password123')

    def test_slug_keeps_cyrillic_instead_of_going_blank(self):
        question = Question.objects.create(title='Почему падает миграция?', author=self.author)
        self.assertEqual(question.slug, 'почему-падает-миграция')

    def test_duplicate_title_gets_a_suffixed_slug(self):
        first = Question.objects.create(title='Как дебажить N+1?', author=self.author)
        second = Question.objects.create(title='Как дебажить N+1?', author=self.author)

        self.assertEqual(first.slug, 'как-дебажить-n1')
        self.assertEqual(second.slug, 'как-дебажить-n1-2')


class QuestionTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@test.com', username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@test.com', username='user2', password='password123')
        self.admin = User.objects.create_superuser(email='admin@test.com', username='admin', password='password123')

        self.question1 = Question.objects.create(
            title='First Question',
            content='Content for first question',
            author=self.user1
        )
        self.question2 = Question.objects.create(
            title='Second Question',
            content='Content for second question',
            author=self.user2
        )

        self.list_url = reverse('question-list')
        self.detail_url = reverse('question-detail', kwargs={'slug': self.question1.slug})

    def test_list_questions(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_by_category_slug(self):
        category = Category.objects.create(name='Python')
        self.question1.category = category
        self.question1.save(update_fields=['category'])

        response = self.client.get(self.list_url, {'category': category.slug})

        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids, [self.question1.id])

    def test_filter_by_category_id(self):
        category = Category.objects.create(name='Python')
        self.question1.category = category
        self.question1.save(update_fields=['category'])

        response = self.client.get(self.list_url, {'category': category.id})

        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids, [self.question1.id])

    def test_list_response_includes_nested_category(self):
        category = Category.objects.create(name='Python')
        self.question1.category = category
        self.question1.save(update_fields=['category'])

        response = self.client.get(self.list_url, {'category': category.slug})

        self.assertEqual(response.data['results'][0]['category']['slug'], category.slug)
        self.assertEqual(response.data['results'][0]['category']['name'], category.name)

    def test_retrieve_question(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'First Question')
        self.assertEqual(response.data['author']['username'], 'user1')

    def test_create_question_unauthorized(self):
        data = {'title': 'New Question', 'content': 'New Content'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_question_authorized(self):
        self.client.force_authenticate(user=self.user1)
        data = {'title': 'New Question', 'content': 'New Content'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 3)
        self.assertEqual(response.data['author']['username'], 'user1')

    def test_update_question_owner(self):
        self.client.force_authenticate(user=self.user1)
        data = {'title': 'Updated Title', 'content': 'Updated Content'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.question1.refresh_from_db()
        self.assertEqual(self.question1.title, 'Updated Title')

    def test_update_question_not_owner(self):
        self.client.force_authenticate(user=self.user2)
        data = {'title': 'Updated Title', 'content': 'Updated Content'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_question_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {'title': 'Admin Updated Title', 'content': 'Admin Updated Content'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_question(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Question.objects.count(), 1)


class CommentTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@test.com', username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@test.com', username='user2', password='password123')
        self.question = Question.objects.create(title='Test Question', content='Content', author=self.user1)

        self.comment1 = Comment.objects.create(question=self.question, user=self.user1, content='Comment 1')
        self.comment2 = Comment.objects.create(question=self.question, user=self.user2, content='Comment 2')

        self.comments_url = reverse('question-comments', kwargs={'slug': self.question.slug})
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
