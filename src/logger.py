import logging
from logging.handlers import TimedRotatingFileHandler


logging.basicConfig(format='%(asctime)s %(message)s', filemode='w')
log = logging.getLogger()
log.setLevel(logging.ERROR)

rotater = TimedRotatingFileHandler("logs/meme-robot.log", when="midnight", interval=1)
rotater.suffix = "%Y%m%d"
log.addHandler(rotater)

