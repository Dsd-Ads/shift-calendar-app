[app]

# Название приложения
title = Календарь Смен

# Имя пакета (только латиница, без пробелов)
package.name = shiftcalendar

# Домен (обратный порядок)
package.domain = org.myapp

# Директория с исходниками
source.dir = .

# Расширения файлов для включения
source.include_exts = py,png,jpg,kv,atlas,json

# Версия приложения
version = 1.0

# Зависимости Python
requirements = python3,kivy==2.1.0

# Ориентация экрана (portrait - вертикальная, landscape - горизонтальная)
orientation = portrait

# Полноэкранный режим
fullscreen = 0

# Разрешения Android
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# Версия Android API
android.api = 31

# Минимальная версия Android API
android.minapi = 21

# Версия Android NDK
android.ndk = 25b

# Автоматическое принятие лицензий SDK
android.accept_sdk_license = True

# Архитектуры для сборки
android.archs = arm64-v8a,armeabi-v7a

# Иконка приложения (опционально)
# icon.filename = %(source.dir)s/icon.png

# Логотип загрузки (опционально)
# presplash.filename = %(source.dir)s/presplash.png

# Цвет фона загрузки
# android.presplash_color = #FFFFFF

[buildozer]

# Уровень логирования (0 = только ошибки, 2 = максимальный)
log_level = 2

# Предупреждения как ошибки
warn_on_root = 1
