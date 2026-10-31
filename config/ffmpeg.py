import shutil
import os

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 30000 -nostdin',
    'options': '-vn',
    'executable': os.getenv('FFMPEG_PATH') or shutil.which('ffmpeg') or '/usr/bin/ffmpeg'
}