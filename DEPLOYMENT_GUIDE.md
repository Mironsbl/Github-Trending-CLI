# Руководство по развертыванию веб-приложения GitHub Trending на сервере с Coolify

В этом руководстве подробно описаны все шаги, команды и настройки, которые мы использовали для развертывания проекта **GitHub Trending Web UI** на удаленном Ubuntu-сервере под управлением **Coolify** и организации стабильного публичного доступа.

---

## 1. Подготовка сервера и установка Coolify

Если вы настраиваете чистый сервер, в первую очередь установите **Coolify v4**:

```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```
Панель управления будет доступна по адресу `http://<IP_сервера>:8000`. 
Зарегистрируйте аккаунт администратора при первом входе.

---

## 2. Настройка локального реестра Docker (Registry)

Поскольку проект разрабатывается локально и не имеет публичного Git-репозитория, мы настроили **приватный реестр Docker** прямо на самом сервере, чтобы загружать туда собранный образ.

1. Запустите приватный реестр на сервере (порт `5001`):
   ```bash
   docker run -d \
     --name local-registry \
     --restart unless-stopped \
     -p 5001:5000 \
     registry:2
   ```

2. Настройте Docker на сервере, чтобы он доверял этому локальному реестру (как небезопасному/HTTP-реестру). Добавьте адрес в файл `/etc/docker/daemon.json`:
   ```json
   {
     "insecure-registries": ["127.0.0.1:5001"]
   }
   ```
   *Затем перезапустите Docker:*
   ```bash
   sudo systemctl restart docker
   ```

---

## 3. Сборка и отправка Docker-образа

Все файлы проекта копируются с локального компьютера на удаленный сервер в папку `/home/miron/github-trending-web`.

Скрипт сборки и отправки образа в реестр:

```bash
# 1. Перейдите в папку с проектом на сервере
cd /home/miron/github-trending-web

# 2. Соберите Docker-образ из локального Dockerfile
docker build -t github-trending-web .

# 3. Добавьте тег для локального реестра
docker tag github-trending-web:latest 127.0.0.1:5001/github-trending:latest

# 4. Загрузите образ в приватный реестр
docker push 127.0.0.1:5001/github-trending:latest
```

---

## 4. Развертывание приложения в Coolify

1. Откройте панель Coolify (`http://<IP_сервера>:8000`).
2. Перейдите в раздел **Projects** -> Выберите проект (или создайте новый) -> **production**-окружение.
3. Нажмите **Add Resource** -> Выберите **Docker Image**.
4. Введите адрес вашего образа в реестре:
   ```text
   127.0.0.1:5001/github-trending:latest
   ```
5. В настройках приложения:
   * Укажите порт назначения (Destination Port): `5050`
   * В разделе **Environment Variables** (Переменные окружения) добавьте ваш токен для работы с API:
     * `GITHUB_TOKEN` = `ghp_FV3...` (ваш токен)
6. Нажмите **Deploy**. Coolify развернет приложение и запустит контейнер на порту `5050` хоста.

---

## 5. Настройка публичного доступа (туннель)

Чтобы обойти блокировки DPI провайдеров (например, Билайн в РФ), которые сбрасывают UDP-туннели Cloudflare (Argo), мы настроили туннелирование с помощью утилиты **localtunnel**. Это позволяет получить бесплатный и стабильный URL-адрес с фиксированным субдоменом.

### Шаг 5.1. Создание скрипта автозапуска туннеля
Создайте файл `/home/miron/github-trending-web/start-tunnel.sh`:

```bash
#!/bin/bash
# Удаляем старый записанный URL
rm -f /home/miron/github-trending-web/tunnel_url.txt

# Запускаем localtunnel с фиксированным субдоменом git-trends-miron
# Скрипт перехватывает вывод и сохраняет актуальную HTTPS-ссылку в файл
npx -y localtunnel --port 5050 --subdomain git-trends-miron 2>&1 | while read -r line; do
    echo "$line"
    if [[ "$line" =~ (https://[a-zA-Z0-9.-]+\.loca\.lt) ]]; then
        url="${BASH_REMATCH[1]}"
        echo "$url" > /home/miron/github-trending-web/tunnel_url.txt
        echo "TUNNEL_URL_FOUND: $url"
    fi
done
```

Сделайте скрипт исполняемым:
```bash
chmod +x /home/miron/github-trending-web/start-tunnel.sh
```

### Шаг 5.2. Создание службы systemd (для автозапуска)
Создайте файл службы `/etc/systemd/system/github-trending-tunnel.service`:

```ini
[Unit]
Description=GitHub Trending SSH Tunnel
After=network.target

[Service]
Type=simple
User=miron
WorkingDirectory=/home/miron/github-trending-web
ExecStart=/bin/bash /home/miron/github-trending-web/start-tunnel.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Активируйте и запустите службу:
```bash
sudo systemctl daemon-reload
sudo systemctl enable github-trending-tunnel
sudo systemctl start github-trending-tunnel
```

### Шаг 5.3. Как узнать текущую ссылку?
Вы можете прочитать ее из файла:
```bash
cat /home/miron/github-trending-web/tunnel_url.txt
```
Или посмотреть логи службы:
```bash
journalctl -u github-trending-tunnel -n 20
```

---

## 6. Как всё удалить (Очистка)

Если вам нужно полностью удалить проект с сервера:

```bash
# 1. Остановите и удалите службу туннеля
sudo systemctl stop github-trending-tunnel
sudo systemctl disable github-trending-tunnel
sudo rm -f /etc/systemd/system/github-trending-tunnel.service
sudo systemctl daemon-reload

# 2. Остановите и удалите контейнеры и образы
# (Имя контейнера Coolify можно узнать через 'docker ps')
docker rm -f <ИМЯ_КОНТЕЙНЕРА_COOLIFY>
docker rmi -f 127.0.0.1:5001/github-trending:latest

# 3. Удалите рабочую папку
rm -rf /home/miron/github-trending-web
```
