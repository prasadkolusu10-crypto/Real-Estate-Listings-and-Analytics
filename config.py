import os

class Config:
    """Base config class with defaults."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2025-realestate-analytics'

    DB_HOST = os.environ.get('localhost') 
    DB_USER = os.environ.get('root') 
    DB_PASSWORD = os.environ.get('Prasad@123') 
    DB_NAME = os.environ.get('real_estate') 

    @staticmethod
    def get_db_connection_kwargs():
        return {
            'host': Config.DB_HOST,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME,
            'port': Config.DB_PORT,
            'raise_on_warnings': True
        }


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
    SECRET_KEY = os.environ.get('SECRET_KEY')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}