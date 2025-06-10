#!/bin/bash

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "Docker не установлен. Пожалуйста, установите Docker Desktop для macOS."
    exit 1
fi

# Создаем временную директорию для сборки
BUILD_DIR="build"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

# Копируем файлы в структуру deb-пакета
cp -r debian $BUILD_DIR/
cp todoist_bot.py $BUILD_DIR/debian/usr/local/bin/todoist-bot/
cp todoist_api.py $BUILD_DIR/debian/usr/local/bin/todoist-bot/
cp requirements.txt $BUILD_DIR/debian/usr/local/bin/todoist-bot/

# Делаем скрипты исполняемыми
chmod 755 $BUILD_DIR/debian/DEBIAN/postinst
chmod 755 $BUILD_DIR/debian/DEBIAN/prerm

# Собираем Docker образ для сборки
echo "Собираем Docker образ для сборки..."
docker build -t deb-builder -f Dockerfile.build .

# Запускаем сборку в контейнере с явным указанием сжатия gzip
echo "Собираем deb-пакет в Docker контейнере..."
docker run --rm -v "$(pwd)/$BUILD_DIR:/build" deb-builder bash -c "cd /build && DPKG_DEB_COMPRESSOR=gzip dpkg-deb --build debian todoist-bot_1.0.0_all.deb"

# Перемещаем собранный пакет в корневую директорию
mv $BUILD_DIR/todoist-bot_1.0.0_all.deb .

# Очищаем временные файлы
rm -rf $BUILD_DIR

echo "Deb-пакет собран: todoist-bot_1.0.0_all.deb"
echo "Для установки на Linux выполните: sudo dpkg -i todoist-bot_1.0.0_all.deb" 