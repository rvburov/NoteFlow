from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse
from news.forms import WARNING, BAD_WORDS
from news.models import Comment


def test_user_can_create_note(
        author_client,
        form_data,
        news_id,
        news,
        author
):
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, data=form_data)
    expected_url = f'{url}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, news_id, form_data):
    url = reverse('news:detail', args=news_id)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_author_can_edit_note(author_client, form_data, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    url_comment = reverse('news:detail', args=(comment.id,))
    assertRedirects(response, f'{url_comment}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_note(admin_client, form_data, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_note(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    url_comment = reverse('news:detail', args=(comment.id,))
    assertRedirects(response, f'{url_comment}#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_note(admin_client, form_data, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, news_id, bad_word):
    """Проверить работу фильтра запрещенных слов в тексте комментария."""
    url = reverse('news:detail', args=news_id)
    comments_count = Comment.objects.count()
    bad_words = {'text': f'Какой-то текст, {bad_word}, еще текст.'}
    response = author_client.post(url, data=bad_words)
    assert comments_count == 0
    assertFormError(response, form='form', field='text', errors=WARNING)
