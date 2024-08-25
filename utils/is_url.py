import re

def is_spotify_url(url):
    spotify_regex = re.compile(
        r'^https?:\/\/(open\.spotify\.com)\/.*'
    )
    return spotify_regex.match(url) is not None

def is_youtube_url(url):
    youtube_regex = re.compile(
        r'^(https?\:\/\/)?(www\.youtube\.com|music\.youtube\.com|youtu\.be)\/(watch\?v=|embed\/|v\/|.+\?v=|.+\/)?[A-Za-z0-9_-]{11}($|[?&])'
    )
    return youtube_regex.match(url) is not None

def is_youtube_playlist_url(url):
    playlist_regex = re.compile(
        r'^(https?\:\/\/)?(www\.youtube\.com|music\.youtube\.com)\/(playlist\?|.*[?&]list=)[A-Za-z0-9_-]+($|[?&])'
    )
    return playlist_regex.match(url) is not None and 'v=' not in url

def is_valid_url(url):
    url_regex = re.compile(
        r'^https?:\/\/'
    )
    return url_regex.match(url) is not None

def is_deezer_url(url):
    deezer_regex = re.compile(
        r'^https?:\/\/(www\.deezer\.com)\/.*'
    )
    return deezer_regex.match(url) is not None
