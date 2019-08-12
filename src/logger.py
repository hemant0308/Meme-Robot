import sys
import os

import logging
from logging.handlers import TimedRotatingFileHandler


logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger()
log.setLevel(logging.ERROR)


formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

log = logging.getLogger("meme-robot")

log.setLevel(logging.DEBUG)

screen_handler = logging.StreamHandler(stream=sys.stdout)
screen_handler.setFormatter(formatter)
#log.addHandler(screen_handler)

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
filename = os.path.join(dir_path,'logs','meme-robot.log')

handler = logging.FileHandler(filename, mode='a+')
handler.setFormatter(formatter)
log.addHandler(handler)

rotater = TimedRotatingFileHandler(filename, when="midnight", interval=1)
rotater.suffix = "%Y%m%d"
log.addHandler(rotater)
