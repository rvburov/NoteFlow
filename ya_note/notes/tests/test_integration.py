from django.urls import reverse
from http import HTTPStatus
import pytest

@pytest.mark.django_db
def test_pages_availability(client):
    # Проверяет, что определенные страницы доступны. Возможные ошибки:
    # 1. Маршрут не настроен в `urls.py` (например, 'notes:home').
    # 2. Страницы возвращают неверный статус-код (например, 404).
    urls = (
        ('notes:home', None, 'GET'),
        ('users:login', None, 'GET'),
        ('users:logout', None, 'POST'),  # Изменяем метод на POST
        ('users:signup', None, 'GET'),
    )
    for name, args, method in urls:
        url = reverse(name, args=args)
        if method == 'GET':
            response = client.get(url)
        elif method == 'POST':
            response = client.post(url)
        else:
            raise ValueError(f"Неизвестный метод {method}")
        assert response.status_code == HTTPStatus.OK, (
            f"Страница {name} недоступна, код {response.status_code}"
        )

@pytest.mark.django_db
def test_redirect_for_anonymous_client(client):
    # Проверяет, что анонимные пользователи перенаправляются на страницу логина. Ошибки:
    # 1. Неправильный путь для LOGIN_URL в `settings.py`.
    # 2. Маршруты могут быть недоступны или настроены неправильно.
    login_url = reverse('users:login')
    urls = (
        ('notes:edit', ('test-note',)),
        ('notes:delete', ('test-note',)),
        ('notes:detail', ('test-note',)),
        ('notes:list', None),
        ('notes:add', None),
        ('notes:success', None),
    )
    for name, args in urls:
        url = reverse(name, args=args)
        response = client.get(url)
        # Проверяем, что анонимный пользователь перенаправлен.
        assert response.status_code == 302, f"Маршрут {name} не перенаправляет анонимного пользователя"
        assert response.url == f"{login_url}?next={url}", (
            f"Неверный URL перенаправления для {name}: ожидалось {login_url}?next={url}, "
            f"получено {response.url}"
        )

