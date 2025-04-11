import os
from datetime import timedelta

class Config:
    """Uygulama yapılandırma ayarları."""
    # Genel ayarlar
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'toplanti-takip-gizli-anahtar'
    DEBUG = os.environ.get('FLASK_DEBUG') == '1'
    
    # Veritabanı ayarları
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///toplanti_takip.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT ayarları
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-gizli-anahtar'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # E-posta ayarları
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') != 'False'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'toplanti@example.com'
    
    # Dosya yükleme ayarları
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    
    # OpenAI API ayarları
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Oturum ayarları
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

class DevelopmentConfig(Config):
    """Geliştirme ortamı yapılandırması."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///toplanti_takip_dev.db'

class TestingConfig(Config):
    """Test ortamı yapılandırması."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///toplanti_takip_test.db'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Üretim ortamı yapılandırması."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# Yapılandırma sınıfları sözlüğü
config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Aktif yapılandırmayı belirle
config = config_dict[os.environ.get('FLASK_ENV', 'default')]
