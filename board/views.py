from django.shortcuts import render, get_object_or_404, redirect
from .models import Board, Topic, Post
from django.contrib.auth.models import User
from .forms import NewTopicForm, ReplyForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class Home(ListView):
    model = Board
    template_name = 'board/home.html'
    context_object_name = 'boards'


"""
def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    queryset = board.topics.annotate(replies_count=Count('posts') - 1).order_by(
        '-last_updated')
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 10)

    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        topics = paginator.page(1)
    except EmptyPage:
        topics = paginator.page(paginator.num_pages)

    return render(request, 'board/board_topics.html', {'board': board, 'topics': topics})
"""


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'board/board_topics.html'
    paginate_by = 5

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.annotate(replies=Count('posts') - 1).order_by(
            '-last_updated')
        return queryset

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    user = User.objects.first()

    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.starter = request.user
            topic.board = board
            form.save()
            Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('board:view_topic', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'board/new_topic.html', {'board': board, 'form': form})


# def view_topic(request, pk, topic_pk):
#     topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
#     topic.views += 1
#     topic.save()
#     return render(request, 'board/view_topic.html', {'topic': topic})


class PostListView(ListView):
    model = Topic
    context_object_name = 'posts'
    template_name = 'board/view_topic.html'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        self.topic.views += 1
        self.topic.save()
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get(
            'pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            topic.last_updated = timezone.now()  # <- here
            topic.save()
            return redirect('board:view_topic', pk=pk, topic_pk=topic_pk)
    else:
        form = ReplyForm()
    return render(request, 'board/reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message',)
    template_name = 'board/edit_post.html'

    # TODO: pk_url_kwargs vs get_object(self)
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    # this means current logged in user can only update those posts that he/she created it
    def get_queryset(self):
        queryset = super().get_queryset()
        # ! queryset.objects.filter
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('board:view_topic', pk=post.topic.board.pk, topic_pk=post.topic.pk)


class AccountUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email')
    template_name = 'board/account.html'
    success_url = '/'

    def get_object(self):
        return self.request.user
