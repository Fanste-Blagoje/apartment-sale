import os


class APPConfig(object):
    DEBUG = os.getenv('DEBUG', True)
    SQLALCHEMY = os.getenv('SQLALCHEMY', True)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'mysql+pymysql://root@localhost/apartment_sale?charset=utf8mb4&use_unicode=1'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    CONTRACT_PATH = os.getenv('CONTRACT_PATH', '/tmp/')
