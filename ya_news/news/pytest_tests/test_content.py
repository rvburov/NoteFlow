from http import HTTPStatus
import pytest
from django.urls import reverse
from news.models import Comment


@pytest.mark.django_db
def test_home_page_news_count(client):
    response = client.get(reverse('news:home'))
    assert response.status_code == HTTPStatus.OK
    news_count = len(response.context['object_list'])
    assert news_count <= 10


@pytest.mark.django_db
def test_home_page_news_order(client):
    response = client.get(reverse('news:home'))
    assert response.status_code == HTTPStatus.OK
    news_list = response.context['object_list']
    dates = [news.date for news in news_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments(comment_id):
    all_comments = Comment.objects.filter(news_id=comment_id)
    sorted_created = sorted([comment.created for comment in all_comments],
                            reverse=False)
    assert [comment.created for comment in all_comments] == sorted_created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user, value',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_form(user, value, news_id):
    url = reverse('news:detail', args=news_id)
    response = user.get(url)
    assert ('form' in response.context) == value
