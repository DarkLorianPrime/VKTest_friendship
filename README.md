# About the Project
Сервис, имитирующий систему друзей Вконтакте, с использованием `django-rest-framework` и `openapi["swagger"]`
#### Проект написан без /api/..., потому что планируется его использование с доменом api.domain.ru, где наличие api.domain.ru/api/ - не желательно.
# Built with
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
# RoadMap
- [x] Начать проект
- [x] Сделать основной функционал
- [x] Написать unittest
- [x] Написать ReadMe
- [x] Написать OpenApi спецификацию
- [ ] Написать полноценную документацию для проекта

# Examples
В этом разделе мы рассмотрим несколько основных примеров использования API, созданного с использованием Django REST Framework в рамках этого проекта.

### Регистрация пользователя
```
POST /registration/
{
    "username": "darklorian",
    "password": "baselorian_password"
}
```
В случае успеха ответ будет:
```
HTTP/1.1 201 Created
{
    "id": 1,
    "date_joined": datetime.now(),
    "username": "darklorian"
}
```
### Авторизация пользователя
```
POST /token/
{
    "username": "darklorian",
    "password": "baselorian_password"
}
```
В случае успеха ответ будет:
```
HTTP/1.1 200 OK
{
    "token": "ce1ab5d44a5517e25865a35335848fc85fdf3f92"
}
```
### Отправка запроса в друзья существующему пользователю
При отправке запроса вам нужно указать имя пользователя и ваш токен авторизации
```
POST /friends/request/bestlorian/
Authorization: Token ce1ab5d44a5517e25865a35335848fc85fdf3f92
```
В случае успеха ответ будет:
```
HTTP/1.1 201 Created
{
    "status": "ok"
}
```
Больше примеров описано в `/backend/app/friends/tests.py`
# Install
### Предполагается, что docker, compose, nginx и их зависимости уже установлены
- Создаем директорию для проекта
```bash
$ mkdir friendship
$ cd friendship
```
- Клонируем репозиторий с github
```bash
$ git clone https://github.com/DarkLorianPrime/VKTest_friendship .
$ ls
├── backend
│   ├── app
│   │   ├── authserver
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── __init__.py
│   │   │   ├── migrations
│   │   │   │   ├── 0001_initial.py
│   │   │   │   └── __init__.py
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── tests.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   ├── core
│   │   │   ├── asgi.py
│   │   │   ├── __init__.py
│   │   │   ├── settings.py
│   │   │   ├── urls.py
│   │   │   └── wsgi.py
│   │   ├── friends
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── __init__.py
│   │   │   ├── migrations
│   │   │   │   ├── 0001_initial.py
│   │   │   │   ├── 0002_remove_friendrequest_status_and_more.py
│   │   │   │   ├── 0003_friendrequest_answered_on.py
│   │   │   │   ├── 0004_alter_friendrequest_answered_on.py
│   │   │   │   └── __init__.py
│   │   │   ├── models.py
│   │   │   ├── tests.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   ├── manage.py
│   │   ├── poetry.lock
│   │   └── pyproject.toml
│   ├── Dockerfile
│   └── entrypoint.sh
├── docker-compose.yaml
├── example.env
└── README.md
```
- Устанавливаем переменные окружения
```bash
$ mv example.env .env
$ nano .env

--.env--
PG_USER=      ->  troot
PG_PASSWORD=  ->  troot_password
PG_NAME=      ->  troot # PG_NAME=PG_USER
PG_HOST=      ->  database #compose_database_name

SECRET_KEY=   -> blabla123_please_save_yes_save_my_passwords
--------

```
- Запускаем docker-compose
### !important 
В docker-compose стоит волум на папку с проектом для применения изменений в реалтайме. Не добавляйте в папку "backend" лишнего, если не хотите чтобы оно оказалось в контейнере
```bash
$ docker-compose up -d --build
```
Первый запуск будет долгим. Применятся миграции, пройдут все тесты, создастся scheme для openapi 

Если вы видите данные надписи:
```
Creating friendship_backend_1  ... done
Creating friendship_database_1 ... done
```
Запуск прошел успешно. Можно проверять (если установлен curl)
```bash
$ docker-compose logs backend
---
backend_1   | .............. # (не должно быть E\F. Количество точек - N)
backend_1   | ----------------------------------------------------------------------
backend_1   | Ran N tests in 19.192s # N=количество тестов
---

$ curl http://127.0.0.1:5006/token/ -X post 
---
{"username":["This field is required."],"password":["This field is required."]}
---
```
Сервис запущен и готов к работе. Можно подключать к nginx и зарабатывать миллионы лисобаксов.

# Contacts
Grand developer - [@darklorianprime](https://vk.com/darklorianprime) - kasimov.alexander.ul@gmail.com