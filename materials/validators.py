import re

from rest_framework import serializers


def validate_youtube_only(value):
    """
    Проверяет, что если в тексте/ссылке есть URL, то он ведет исключительно на youtube.com или youtu.be.
    """
    if value:
        url_pattern = r"https?://[^\s]+"
        urls = re.findall(url_pattern, value)

        for url in urls:
            youtube_re = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
            if not re.match(youtube_re, url):
                raise serializers.ValidationError(
                    "Использование сторонних ссылок запрещено! Разрешены только ссылки на youtube.com."
                )
