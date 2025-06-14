#!/bin/bash

# Использование: ./build_deb.sh [PACKAGE_NAME]
# Если не указан, используется self-tracker-bot
PACKAGE_NAME="${1:-self-tracker-bot}"
PKGDIR="$PACKAGE_NAME"
PKGDEB="${PACKAGE_NAME}_1.0.0_all.deb"

# Проверяем наличие podman
if ! command -v podman &> /dev/null; then
    echo "Podman не установлен. Пожалуйста, установите podman."
    exit 1
fi

# Создаем временную директорию для сборки
BUILD_DIR="build"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

# Копируем debian структуру и заменяем плейсхолдеры
cp -r debian $BUILD_DIR/

# Заменяем __PKGNAME__ на $PACKAGE_NAME во всех шаблонах
for f in $BUILD_DIR/debian/DEBIAN/postinst $BUILD_DIR/debian/DEBIAN/prerm $BUILD_DIR/debian/DEBIAN/control $BUILD_DIR/debian/etc/systemd/system/self-tracker-bot.service; do
    sed "s/__PKGNAME__/$PACKAGE_NAME/g" "$f" > "$f.tmp" && mv "$f.tmp" "$f"
    # Для systemd unit-файла переименовываем
    if [[ "$f" == *self-tracker-bot.service ]]; then
        mv "$f" "$BUILD_DIR/debian/etc/systemd/system/${PACKAGE_NAME}.service"
    fi
    # Для DEBIAN/control переименовывать не нужно
    # postinst/prerm остаются
    # Остальные файлы не трогаем
    done

# Создаем директории bin и log под имя пакета
mkdir -p $BUILD_DIR/debian/usr/local/bin/$PACKAGE_NAME
mkdir -p $BUILD_DIR/debian/var/log/$PACKAGE_NAME

# Копируем исходники в структуру пакета
cp self_tracker_bot.py $BUILD_DIR/debian/usr/local/bin/$PACKAGE_NAME/
cp todoist_api.py $BUILD_DIR/debian/usr/local/bin/$PACKAGE_NAME/
cp requirements.txt $BUILD_DIR/debian/usr/local/bin/$PACKAGE_NAME/
cp yougile_api.py $BUILD_DIR/debian/usr/local/bin/$PACKAGE_NAME/
cp yandex_gpt.py $BUILD_DIR/debian/usr/local/bin/$PACKAGE_NAME/

# Делаем скрипты исполняемыми
chmod 755 $BUILD_DIR/debian/DEBIAN/postinst
chmod 755 $BUILD_DIR/debian/DEBIAN/prerm

# Собираем podman образ для сборки
echo "Собираем podman образ для сборки..."
podman build -t deb-builder -f Dockerfile.build .

# Собираем deb-пакет
podman run --rm -v "$(pwd)/$BUILD_DIR:/build" deb-builder bash -c "cd /build && DPKG_DEB_COMPRESSOR=gzip dpkg-deb --build debian $PKGDEB"

# Перемещаем собранный пакет в корневую директорию
mv $BUILD_DIR/$PKGDEB .

# Очищаем временные файлы
rm -rf $BUILD_DIR

echo "Deb-пакет собран: $PKGDEB"
echo "Для установки на Linux выполните: sudo dpkg -i $PKGDEB" 