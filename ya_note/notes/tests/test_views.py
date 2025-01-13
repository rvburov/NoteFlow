from django.urls import reverse
from http import HTTPStatus
import pytest
from notes.models import Note

@pytest.mark.django_db
def test_notes_list_view(author_client):
    # Проверяет, что авторизованный пользователь может просматривать список заметок. Ошибки:
    # 1. Пользователь не авторизован.
    # 2. Маршрут 'notes:list' отсутствует или недоступен.
    url = reverse('notes:list')
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f"Список заметок недоступен, статус: {response.status_code}"
    )

@pytest.mark.django_db
def test_anonymous_cannot_create_note(client):
    # Проверяет, что анонимный пользователь не может создать заметку. Ошибки:
    # 1. Неправильно настроен путь для LOGIN_URL.
    # 2. Маршрут 'notes:add' отсутствует или настроен неверно.
    url = reverse('notes:add')
    response = client.get(url)
    # Проверяем редирект на страницу логина.
    assert response.status_code == 302, "Анонимный пользователь не был перенаправлен на страницу логина"
    assert response.url.startswith(reverse('users:login')), (
        f"URL перенаправления неверный: {response.url}"
    )

@pytest.mark.django_db
def test_author_can_edit_note(author_client, note):
    # Проверяет, что автор заметки может её редактировать. Ошибки:
    # 1. Пользователь не авторизован или не является автором.
    # 2. Данные формы (new_data) некорректны.
    url = reverse('notes:edit', args=[note.slug])
    new_data = {"title": "Updated Title", "text": "Updated Text", "slug": note.slug}
    response = author_client.post(url, data=new_data)
    note.refresh_from_db()
    # Проверяем, что данные были обновлены.
    assert response.status_code == 302, "Редактирование заметки завершилось с ошибкой"
    assert note.title == "Updated Title", f"Название заметки не обновлено: {note.title}"
    assert note.text == "Updated Text", f"Текст заметки не обновлен: {note.text}"

@pytest.mark.django_db
def test_author_can_delete_note(author_client, note):
    # Проверяет, что автор может удалить свою заметку. Ошибки:
    # 1. Пользователь не авторизован.
    # 2. Маршрут 'notes:delete' отсутствует или недоступен.
    url = reverse('notes:delete', args=[note.slug])
    response = author_client.post(url)
    # Проверяем, что заметка была удалена.
    assert response.status_code == 302, "Удаление заметки завершилось с ошибкой"
    assert not Note.objects.filter(slug=note.slug).exists(), (
        f"Заметка с slug {note.slug} не была удалена"
    )

