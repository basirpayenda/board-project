from django.test import TestCase
from django.urls import reverse, resolve, path
from board.models import Board, Topic, Post
from django.contrib.auth.models import User
from board.views import TopicListView, Home, new_topic
from board.forms import NewTopicForm


class HomeTest(TestCase):
    def test_home_reverse_status_code(self):
        url = reverse('board:home')
        view = self.client.get(url)
        self.assertEqual(view.status_code, 200)

    def test_home_url_resolve(self):
        url = resolve('/')
        self.assertEqual(url.func.view_class, Home)


class BoardTopicsTests(TestCase):
    def setUp(self):
        Board.objects.create(
            name='Django', description='I like this framework!')

    def test_board_topics_success_status_code(self):
        url = reverse('board:board_topics', kwargs={'pk': 1})
        view = self.client.get(url)
        self.assertEqual(view.status_code, 200)

    def test_board_topics_not_found_status_code(self):
        url = reverse('board:board_topics', kwargs={'pk': 999})
        view = self.client.get(url)
        self.assertEqual(view.status_code, 404)

    def test_board_topics_resolve_url(self):
        url = resolve('/board/1/')
        self.assertEqual(url.func.view_class, TopicListView)

    def test_board_topics_view_contains_navigation_links(self):
        board_topics_url = reverse('board:board_topics', kwargs={'pk': 1})
        homepage_url = reverse('board:home')

        new_topic_url = reverse('board:new_topic', kwargs={'pk': 1})

        response = self.client.get(board_topics_url)

        self.assertContains(response, 'href="{0}"'.format(homepage_url))
        self.assertContains(response, 'href="{0}"'.format(new_topic_url))


class HomeTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(
            name='Django', description='Django Board')
        url = reverse('board:home')
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_home_url_resolve(self):
        view = resolve('/')
        self.assertEqual(view.func.view_class, Home)

        # tests if there is href="/boards/1/" link to home page
    def test_home_view_contains_links_to_topic_pages(self):
        url = reverse('board:board_topics', kwargs={'pk': self.board.pk})
        self.assertContains(self.response, 'href="{0}"'.format(url))


class TestNewTopic(TestCase):
    def setUp(self):
        Board.objects.create(
            name='Python', description='I love Python!')
        user = User.objects.create_user(
            username='john', email='john@doe.com', password='123')
        self.client.login(username='john', password='123')

    def test_new_topic_success_status_code(self):
        url = reverse('board:new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_new_topic_not_found_status_code(self):
        url = reverse('board:new_topic', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_new_topic_url_resolver(self):
        view = resolve('/board/1/new/')
        self.assertEqual(view.func, new_topic)

    def test_new_topic_view_has_link_backto_board_topics_view(self):
        new_topic_url = reverse('board:new_topic', kwargs={'pk': 1})
        board_topics_url = reverse('board:board_topics', kwargs={'pk': 1})
        response = self.client.get(new_topic_url)
        self.assertContains(response, 'href="{0}"'.format(board_topics_url))

    def test_csrf(self):
        url = reverse('board:new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_new_topic_valid_post_data(self):
        url = reverse('board:new_topic', kwargs={'pk': 1})
        data = {
            'subject': 'Masty',
            'message': 'Masty Baig'
        }
        self.client.post(url, data)

        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_new_topic_invalid_post_data(self):
        url = reverse('board:new_topic', kwargs={'pk': 1})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)

    def test_new_topic_invalid_post_data_empty_fields(self):
        url = reverse('board:new_topic', kwargs={'pk': 1})
        data = {
            'subject': '',
            'topic': ''
        }
        self.client.post(url, data)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())

    def test_contains_forms(self):
        url = reverse('board:new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_new_topic_invalid_post_data(self):
        url = reverse('board:new_topic', kwargs={'pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.errors)
