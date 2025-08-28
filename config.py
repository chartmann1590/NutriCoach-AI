import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'dev-csrf-key'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///nutricoach.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Session
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'nutricoach:'
    SESSION_SERIALIZATION_FORMAT = 'json'
    SESSION_COOKIE_NAME = 'nutricoach_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    
    # File Upload
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 8 * 1024 * 1024))  # 8MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
    
    # Ollama
    OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
    DEFAULT_CHAT_MODEL = os.environ.get('DEFAULT_CHAT_MODEL', 'llama2')
    DEFAULT_VISION_MODEL = os.environ.get('DEFAULT_VISION_MODEL', 'llava')
    
    # External APIs
    OPENFOODFACTS_API_URL = os.environ.get('OPENFOODFACTS_API_URL', 'https://world.openfoodfacts.org')
    WIKIPEDIA_API_URL = os.environ.get('WIKIPEDIA_API_URL', 'https://en.wikipedia.org')
    
    # Security
    OFFLINE_MODE = os.environ.get('OFFLINE_MODE', 'false').lower() == 'true'
    DISABLE_EXTERNAL_CALLS = os.environ.get('DISABLE_EXTERNAL_CALLS', 'false').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}