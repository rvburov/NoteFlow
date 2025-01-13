import pytest
from notes.models import Note
from django.contrib.auth import get_user_model

@pytest.fixture
def user(db):
    # Создает пользователя для тестов. Если возникнет ошибка, проверьте:
    # 1. Миграции для модели User (auth_user).
    # 2. Наличие базы данных и корректную настройку тестовой БД.
    User = get_user_model()
    return User.objects.create(username="test_user")

@pytest.fixture
def author_client(client, user):
    # Логинит клиента под тестовым пользователем. Ошибки могут возникнуть, если:
    # 1. Пользователь не был создан.
    # 2. `client` неправильно настроен.
    client.force_login(user)
    return client

@pytest.fixture
def note(user):
    # Создает заметку для тестов. Ошибки могут быть связаны с:
    # 1. Отсутствием связанного пользователя (author).
    # 2. Нарушением ограничений модели Note (например, уникальность slug).
    return Note.objects.create(
        title="Test Note",
        text="Test Text",
        slug="test-note",
        author=user,
    )