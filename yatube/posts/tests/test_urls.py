from http import HTTPStatus
from django.urls import reverse

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        """ Создаем тестовые экземпляры постов."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='group',
            slug='slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='тестовый текст поста',
            group=cls.group,
        )

    def setUp(self):
        """Создаем авторизованного и неавторизованного клиента"""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_urls_guest(self):
        """Страница доступна любому пользователю."""
        urls = (reverse('posts:index'),
                reverse('posts:postsname',
                        kwargs={'slug': self.group.slug}),
                reverse('posts:profile',
                        kwargs={'username': self.user.username}),
                reverse('posts:post_detail', args=[self.post.id]),
                )
        for url in urls:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_url_post_create(self):
        """Страница create доступна только авторизованному пользователю."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_url_post_edit(self):
        """Страница create доступна только автору поста."""
        response = self.author_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_url_redirect_anonymous(self):
        """Страница перенаправит пользователся на login"""
        response = self.guest_client.get(
            reverse('posts:post_create')
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_urls_templates(self):
        """Тест на соотвецтвие адресов и шаблонов"""
        urls_templates = {
            'posts/index.html': '/',
            'posts/group_list.html': reverse('posts:postsname',
                                             kwargs={'slug': self.group.slug}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs=
                                          {'username': self.user.username}),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              kwargs={
                                                  'post_id': self.post.id}),
            'posts/create_post.html': reverse('posts:post_edit',
                                              kwargs={
                                                  'post_id': self.post.id}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, address in urls_templates.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)
