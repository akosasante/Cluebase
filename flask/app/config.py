import os


class BaseConfig:
    """Base configuration"""
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "redis"
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_REDIS_HOST = "redis"
    RQ_DASHBOARD_PREFIX = "/rq"


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    DEBUG = True
    RQ_REDIS_URL = os.environ.get('REDIS_URL')


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')


class ProductionConfig(BaseConfig):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
