import os

class Config:
    """Base configuration settings for the ITS application."""
    
    # Flask settings
    SECRET_KEY = 'geometry-its-secret-key-change-in-production'
    DEBUG = True
    TESTING = False
    
    # File paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    ONTOLOGY_PATH = os.path.join(BASE_DIR, 'ontology', 'geometry_ontology.owl')
    
    # Application settings
    MAX_QUESTION_ATTEMPTS = 3
    SHAPES = ['square', 'rectangle', 'triangle', 'circle']
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    SESSION_REFRESH_EACH_REQUEST = True


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'prod-key-must-be-set')


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}