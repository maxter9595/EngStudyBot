# 📚 EngStudyBot - Telegram-бот для изучения английского языка

<img src="./demo/1-intro/1.gif" width="100%">

## 1. Лимиты внешних API и прочие ограничения

### Oxford Dictionary
- **Аудио**: запись произношения (MP3) недоступна для всех слов. В некоторых случаях бот не способен найти аудио или скачать его.  
- **Частота запросов**: слишком интенсивный парсинг может привести к блокировке IP-адреса. В скрипте реализованы задержки между запросами для снижения риска блокировки.  

### Promt
- **Качество перевода**: переводы и примеры предложений формируются автоматизированным сервисом. По этой причине могут возникнуть стилистические неточности.
- **Определение частей речи**: алгоритм иногда ошибается при работе с многозначными словами или сложными грамматическими случаями.  

### Telegram
- **Размер сообщений**: одно сообщение (включая текст и примеры предложений) не должно превышать **4096 символов**.  
- **Размер аудиофайлов**: загружаемые MP3-файлы не должны превышать **50 МБ** (ограничение Telegram API).  

### Прочие ограничения
- **Поддерживаемые части речи**: бот обрабатывает только существительные (*noun*), глаголы (*verb*) и прилагательные (*adjective*). Остальные части речи определяются как *unidentified*.  
- **Спецсимволы**: в словах недопустимы следующие символы: `<, >, :, ", /, \, |, ?, *`. При создании имени аудиофайла они автоматически удаляются.  
- **Регистр букв**: регистр не играет роли при вводе слов для добавления или удаления (все слова приводятся к нижнему регистру).  

## 2. Особенности работы приложения

### 2.1. Запуск чат-бота

- После подключения к чат-боту Telegram нажимается кнопка ```Start```
- Отгадывается правильный перевод английского слова

<img src="./demo/2-functionality/1.gif" width="100%">

### 2.2. Выбор варианта ответа и клавиша "Дальше"

- При выборе неправильного варианта ответа появляется крестик
- При выборе корректного варианта ответа появляется сообщение о верном ответе
- Для продолжения викторины нажимается клавиша "Дальше"

<img src="./demo/2-functionality/2.gif" width="100%">

### 2.3. Клавиша "Добавить слово"

- После нажатия на клавишу "Добавить слово" чат-бот попросит пользователя ввести английское слово, которое необходимо добавить в базу данных (БД)
- Ввод команд "Дальше", "Добавить слово", "Удалить слово" невозможен после выбора команды "Добавить слово"
- При добавлении существующего английского слова чат-бот сообщит о его наличии в БД

<img src="./demo/2-functionality/3-1.gif" width="100%">

- При вводе нового английского слова, существующего в БД онлайн-словарей (Oxford, Promt.One), чат-бот автоматически добавит его в БД пользователя Telegram
- При вводе нового английского слова, отсутствующего в БД онлайн-словарей, чат-бот попросит пользователя ввести перевод английского слова

<img src="./demo/2-functionality/3-2.gif" width="100%">

- В случае ввода слова на некорректном языке (русский вместо английского или наоборот) Telegram-бот попросит нажать на кнопку «Добавить слово» и повторить попытку

<img src="./demo/2-functionality/3-3.gif" width="100%">

### 2.4. Клавиша "Удалить слово"

- Для удаления английского слова из БД пользователя Telegram необходимо нажать на клавишу "Удалить слово"
- Непредусмотренное нажатие клавиш, содержащих команды "Дальше", "Добавить слово" и "Удалить слово", приведет к невозможности обработки их чат-ботом
- При отсутствии английского слова в БД пользователя Telegram чат-бот известит его о невозможности выполнить запрошенную операцию

<img src="./demo/2-functionality/4-1.gif" width="100%">

- При наличии введенного английского слова в БД пользователя Telegram-бот его удалит
- При вводе русского слова вместо английского чат-бот попросит пользователя Telegram нажать на клавишу "Удалить слово" и повторить попытку

<img src="./demo/2-functionality/4-2.gif" width="100%">

## 3. Инструкция по локальному запуску проекта

### 3.1. Клонирование репозитория

* Клонирование репозитория:

```bash
git clone https://github.com/maxter9595/EngStudyBot.git
cd EngStudyBot
```

<img src="./demo/3-local-setup/1.gif" width="100%">

### 3.2. Настройка переменных окружения с установкой Telegram-токена

* Документация по Telegram Bot API: [https://core.telegram.org/bots/api](https://core.telegram.org/bots/api)

* Указание переменных окружения с учетом валидного Telegram-токена:

```bash
# 7...O4 - Telegram-токен, заменяющий фразу "your_token"
bash -c "cp .env_example .env && sed -i 's/your_token/7...O4/g' .env"
```

<img src="./demo/3-local-setup/2.png" width="100%">

### 3.3. Запуск Docker

* Запуск Docker Desktop. Его наличие необходимо для запуска Docker-контейнеров

* Сборка и запуск Docker:

```bash
docker compose build
docker compose up -d
```

<img src="./demo/3-local-setup/3.gif" width="100%">

### 3.4. Тестирование приложения

* Проверка наличия Docker-контейнеров и запуск тестирования функционала приложения:

```bash
docker-compose ps
docker-compose run test
```

<img src="./demo/3-local-setup/4.gif" width="100%">

### 3.5. Подключение к административной панели СУБД PostgreSQL

* Ссылка для подключения: [http://localhost:5050/](http://localhost:5050/)

* Данные администратора БД для входа в административную панель PostgreSQL:

```
Почта: admin@example.com
Пароль: admin123
```

* `Register...` ➝ `Server...`. Данные соединения:

```
Host: db
Port: 5432
Maintenance database: EngStudyBot
Username: postgres
Password: postgres
```

<img src="./demo/3-local-setup/5.gif" width="100%">

### 3.6. Проверка работы приложения

* Проверка работы Telegram-бота

<img src="./demo/3-local-setup/6.gif" width="100%">

## 4. Инструкция по деплою проекта на сервере

### 4.1. Покупка сервера и подключение к нему

* Рег.RU - Облачный сервер с предустановленным Docker: [https://www.reg.ru/cloud/docker](https://www.reg.ru/cloud/docker)

* Пример IP-адреса и информация о сервере для покупки:

```
- IP-адрес: 91.197.99.158
- Предустановленный Docker: да 
- Образ: Ubuntu
- Тарифы и конфигурации: производительный
- Тариф: HP C2-M2-D40
- Регион размещения: Москва
- Плавающий (публичный) IP-адрес: да
- Резервное копирование: да
```

* Вход на сервер после его приобретения:

```bash
ssh root@91.197.99.158
```

<img src="./demo/4-server-deploy/1.gif" width="100%">

### 4.2. Подготовка сервера для деплоя

* Создание пользователя и добавление его в группу sudo:

```bash
adduser myclouduser
usermod -aG sudo myclouduser
```

* Установка зависимостей:

```bash
apt update && apt upgrade -y
apt install -y git nginx ufw
```

* Настройка firewall:

```bash
sudo ufw allow 5432
sudo ufw allow 5050
sudo ufw allow 22
ufw allow 80
ufw enable
```

* Запуск Docker:

```bash
# На выбранном сервере Docker уже предустановлен
systemctl enable docker
systemctl start docker
```

* Добавление пользователя в группу docker и его переподключение на сервер для утверждения прав:

```bash
usermod -aG docker myclouduser
exit

# Вход по паролю, заданному пользователю через adduser myclouduser
ssh myclouduser@91.197.99.158
```

<img src="./demo/4-server-deploy/2.gif" width="100%">

### 4.3. Клонирование репозитория. Подготовка переменных окружения

* Клонирование репозитория:

```bash
git clone https://github.com/maxter9595/EngStudyBot.git
cd EngStudyBot
```

<img src="./demo/4-server-deploy/3-1.gif" width="100%">

* Указание переменных окружения с учетом валидного Telegram-токена:

```bash
# 7...O4 - Telegram-токен, заменяющий фразу "your_token"
cp .env_example .env && sed -i "s/your_token/7...O4/g" .env
```

<img src="./demo/4-server-deploy/3-2.png" width="100%">

### 4.4. Запуск Docker

* Сборка и запуск Docker:

```bash
cd ~/MyCloudApp
docker compose build
docker compose up -d
```

* Проверка наличия Docker контейнеров и запуск тестов:

```bash
docker compose ps
docker compose run test
```

<img src="./demo/4-server-deploy/4.gif" width="100%">

### 4.5. Настройка админской панели СУБД PostgreSQL

* Админка PostgreSQL (через PGAdmin): [http://91.197.99.158:5050/](http://91.197.99.158:5050/)

* Данные администратора БД для входа в административную панель СУБД PostgreSQL:

```
Почта: admin@example.com
Пароль: admin123
```

* `Register...` ➝ `Server...`. Данные соединения к БД в СУБД PostgreSQL:

```
Host: db
Port: 5432
Maintenance database: EngStudyBot
Username: postgres
Password: postgres
```

<img src="./demo/4-server-deploy/5.gif" width="100%">

### 4.6. Проверка работы приложения

* Проверка работы Telegram-бота

<img src="./demo/4-server-deploy/6.gif" width="100%">

## 5. Настройка автодеплоя проекта (CI/CD)

### 5.1. Генерация SSH-ключа на локальном ПК

* Генерация SSH-ключа на локальном ПК:

```bash
ssh-keygen -t ed25519 -C "max.t95@bk.ru"
```

* Вывод SSH-ключа из локального ПК для копирования:

```bash
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

```bash
# Копируем SSH-ключ
ssh-ed25519 AAAA...g5 max.t95@bk.ru
```

<img src="./demo/5-ci-cd/1.png" width="100%">

### 5.2. Генерация SSH-ключа на сервере

* Вход на сервер:

```bash
ssh myclouduser@91.197.99.158
```

* Генерация SSH-ключа на сервере:

```bash
ssh-keygen -t ed25519 -C "max.t95@bk.ru"
```

* Вывод SSH-ключа из сервера для просмотра:

```bash
ssh-keygen -y -f ~/.ssh/id_ed25519
```

```bash
# SSH-ключ из сервера понадобится для удаленного подключения к GitHub
ssh-ed25519 AAAA...hc max.t95@bk.ru
```

<img src="./demo/5-ci-cd/2.png" width="100%">

### 5.3. Добавление SSH-ключей из локального ПК и сервера в список авторизованных ключей сервера

* Ввод SSH-ключа из сервера в список авторизированных ключей:

```bash
ssh-keygen -y -f ~/.ssh/id_ed25519 >> ~/.ssh/authorized_keys
```

* Ввод SSH-ключа из локального ПК в список авторизированных ключей:

```bash
echo "ssh-ed25519 AAAA...g5 max.t95@bk.ru" >> ~/.ssh/authorized_keys
```

* Просмотр списка авторизированных ключей:

```bash
cat ~/.ssh/authorized_keys
```

```bash
# В результате должно быть два SSH-ключа в списке авторизованных ключей
ssh-ed25519 AAAA...hc max.t95@bk.ru
ssh-ed25519 AAAA...g5 max.t95@bk.ru
```

<img src="./demo/5-ci-cd/3.png" width="100%">

### 5.4. Настройка sudo без пароля для CI/CD

* Настройка прав для authorized_keys:

```bash
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

* Вход в visudo и добавление параметров для обхода паролей пользователя при деплое:  

```bash
sudo visudo
```

```bash
# Добавляем в конце файла следующее:
myclouduser ALL=(ALL) NOPASSWD: ALL
```

* Выход из сервера и проверка входа на сервер без пароля:

```bash
exit
ssh myclouduser@91.197.99.158
# Если всё ок — войдём без пароля
```

<img src="./demo/5-ci-cd/4.gif" width="100%">

### 5.5. Привязка SSH-ключа к GitHub

* Вывод публичного SSH-ключа для интеграции с GitHub:

```bash
cat ~/.ssh/id_ed25519.pub
```

```bash
# Копируем все, что будет выведено
ssh-ed25519 AAAA...hc max.t95@bk.ru
```

* Привязка публичного ключа к GitHub:

   * ```Сайт GitHub``` → ```Settings``` → ```SSH and GPG keys``` → ```New SSH key```. Заполняем параметры SHH-ключа:

     * Тип ключа: ```Authentication Key``` 
  
     * Имя ключа: ```VM-server```

     * В поле ```Key``` добавляем содержимое SSH-ключа. Пример - ```ssh-ed25519 AAAA...hc max.t95@bk.ru```

  * После добавления параметров SSH-ключа нажимаем ```Add SSH key```

<img src="./demo/5-ci-cd/5.png" width="100%">

### 5.6.Настройка файла SSH-конфигурации. Проверка подключения к GitHub

* Внесение GitHub в список известных хостов сервера:

```bash
ssh-keyscan -H github.com >> ~/.ssh/known_hosts
```

* Настройка конфигурации для SSH:

```bash
nano ~/.ssh/config
```

```
----- ~/.ssh/config -----
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
----- ~/.ssh/config -----
```

* Установка прав для файла SSH-конфигурации:

```bash
chmod 600 ~/.ssh/config
```

* Проверка взаимодействия с GitHub:

```bash
ssh -T git@github.com
# Если всё ок — увидим следующее сообщение:
# Hi <логин>! You've successfully authenticated ...
```

<img src="./demo/5-ci-cd/6.gif" width="100%">

### 5.7. Установка значений secret-параметров GitHub-репозитория для автодеплоя

* Ввод команды на сервере для получения ```SSH_PRIVATE_KEY```:

```bash
cat ~/.ssh/id_ed25519
```

```bash
# Копируем все вместе с комментариями BEGIN и END
-----BEGIN OPENSSH PRIVATE KEY----- 
b3...= 
-----END OPENSSH PRIVATE KEY-----
```

* Ввод secrets для автодеплоя GitHub-репозитория:

  * SSH_HOST: ```91.197.99.158``` (или другой IP-адрес сервера)

  * SSH_USER: ```myappuser```

  * SSH_PRIVATE_KEY: результат команды ```cat ~/.ssh/id_ed25519``` на сервере

  * TG_TOKEN: Telegram-токен

<img src="./demo/5-ci-cd/7-1.png" width="100%">

* После установки secrets проверяем функционал автодеплоя

<img src="./demo/5-ci-cd/7-2.gif" width="100%">
