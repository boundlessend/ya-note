from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, kwargs={'slug': self.note.slug})
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, kwargs={'slug': self.note.slug})
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_availability(self):
        public_urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
        )
        for name, kwargs in public_urls:
            with self.subTest(name=name):
                if kwargs:
                    url = reverse(name, kwargs=kwargs)
                else:
                    url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        self.client.force_login(self.author)
        private_urls = (
            ('notes:detail', {'slug': self.note.slug}),
        )
        for name, kwargs in private_urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
