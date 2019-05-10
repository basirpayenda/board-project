from django.test import TestCase
from django.urls import reverse, resolve
from board.models import Board, Topic
from django.contrib.auth.models import User
from board.views import PostListView


class RequiredLoginNewTopicTest(TestCase):
    def setUp(self):
        Board.objects.create(name='Python', description='Python Tutorial')
        self.new_topic_url = reverse('board:new_topic', kwargs={'pk': 1})
        self.response = self.client.get(self.new_topic_url)

    def test_redirections(self):
        login_url = reverse('signin')
        self.assertRedirects(
            self.response, "{0}?next={1}".format(login_url, self.new_topic_url))


class Test_view_topics(TestCase):
    def setUp(self):
        board = Board.objects.create(
            name='Python', description='Python Tutorial')
        user = User.objects.create(username='Johndoe',
                                   email='johndoe@gmail.com', password='testing123')
        topic = Topic.objects.create(subject='Python Basics',
                                     board=board, starter=user)  # board = 1 ! working
        url = reverse('board:view_topic', kwargs={'pk': 1, 'topic_pk': 1})
        self.response = self.client.get(url)

    def test_view_topic_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_topic_url_resolve(self):
        url = resolve('/board/1/topic/1/')
        self.assertEqual(url.func.view_class, PostListView)
