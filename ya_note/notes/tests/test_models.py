import pytest
from django.contrib.auth import get_user_model
from notes.models import Note

@pytest.mark.django_db
def test_note_creation():
    # Проверяет создание заметки. Возможные ошибки:
    # 1. Пользователь не был создан (auth_user).
    # 2. Ограничения модели Note нарушены (например, уникальность slug).
    User = get_user_model()
    user = User.objects.create(username="test_user")
    note = Note.objects.create(
        title="Тестовая заметка",
        text="Тестовый текст",
        slug="test-slug",
        author=user
    )
    # Проверяем, что заметка создана.
    assert Note.objects.count() == 1, "Заметка не была создана"
    assert note.title == "Тестовая заметка", f"Название заметки неверное: {note.title}"
    assert note.slug == "test-slug", f"Slug заметки неверный: {note.slug}"

