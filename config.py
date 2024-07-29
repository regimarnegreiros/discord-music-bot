FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 3000000 -nostdin',
    'options': '-vn', 'executable': 'C:/ffmpeg/ffmpeg.exe'
}

YDL_OPTIONS = {
    'quiet': True,
    'ignoreerrors': True,
    'format': 'bestaudio/best',
    'noplaylist': True
}

YDL_OPTIONS_FLAT = {
    'extract_flat': 'in_playlist',
    'quiet': True,
    'ignoreerrors': True,
    'format': 'bestaudio/best',
    'noplaylist': True
}

COLOR = {
    "RESET": "\033[0m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m",
    "BOLD_RED": "\033[1;31m",
    "BOLD_GREEN": "\033[1;32m",
    "BOLD_YELLOW": "\033[1;33m",
    "BOLD_BLUE": "\033[1;34m",
    "BOLD_MAGENTA": "\033[1;35m",
    "BOLD_CYAN": "\033[1;36m",
    "BOLD_WHITE": "\033[1;37m"
}