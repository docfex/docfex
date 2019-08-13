from src.config.config import FLASK_SECRET_KEY, REDIS_URL
import redis

# Flask session settings
class SessionConfig(object):
    SECRET_KEY = FLASK_SECRET_KEY
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.from_url(REDIS_URL)
    SESSION_PERMANENT = True
    SESSION_KEY_PREFIX = 'DOCFEX'
