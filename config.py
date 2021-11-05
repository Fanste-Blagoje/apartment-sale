import os


class APPConfig(object):
    DEBUG = os.getenv('DEBUG', True)
    # LOG_PATH = os.getenv('LOG_PATH', 'apartment.log')
    # LOG_COUNT = os.getenv('LOG_COUNT', 10)
    # LOG_MAX_SIZE = os.getenv('LOG_MAX_SIZE', 4194304)
    # LOG_ENCODING = os.getenv('LOG_ENCODING', 'utf-8')
    # LOG_LEVEL = os.getenv('LOG_ENCODING', 20)
    # SESSION_TYPE = os.getenv('SESSION_TYPE', 'redis')
    # DB_POOL_RECYCLE = os.getenv('DB_POOL_RECYCLE', 3600)
    SQLALCHEMY = os.getenv('SQLALCHEMY', True)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'mysql+pymysql://root@localhost/apartment_sale?charset=utf8mb4&use_unicode=1'
    )
    # SQLALCHEMY_POOL_SIZE = os.getenv('SQLALCHEMY_POOL_SIZE', 10)
    # SQLALCHEMY_POOL_RECYCLE = os.getenv('SQLALCHEMY_POOL_RECYCLE', 10)
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    # SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', False)
    REPORTS_PATH = os.getenv('REPORTS_PATH', '/tmp/')
