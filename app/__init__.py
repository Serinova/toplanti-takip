from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Uygulama bileşenleri
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
jwt = JWTManager()

def create_app(config_class='app.config.Config'):
    """Flask uygulamasını oluşturur ve yapılandırır."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Bileşenleri başlat
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    CORS(app)
    jwt.init_app(app)
    
    # Login yönlendirme ayarları
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Lütfen bu sayfaya erişmek için giriş yapın.'
    login_manager.login_message_category = 'info'
    
    # Blueprint'leri kaydet
    from app.routes.auth import auth_bp
    from app.routes.toplanti import toplanti_bp
    from app.routes.gundem import gundem_bp
    from app.routes.gorev import gorev_bp
    from app.routes.bildirim import bildirim_bp
    from app.routes.urun import urun_bp
    from app.routes.rapor import rapor_bp
    from app.routes.ai import ai_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(toplanti_bp)
    app.register_blueprint(gundem_bp)
    app.register_blueprint(gorev_bp)
    app.register_blueprint(bildirim_bp)
    app.register_blueprint(urun_bp)
    app.register_blueprint(rapor_bp)
    app.register_blueprint(ai_bp)
    
    # API Blueprint'lerini kaydet
    from app.routes.api import api_bp
    app.register_blueprint(api_bp)
    
    # Hata sayfalarını kaydet
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    """Hata sayfalarını kaydeder."""
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

# Kullanıcı yükleme fonksiyonu
from app.models.kullanici import Kullanici

@login_manager.user_loader
def load_user(user_id):
    return Kullanici.query.get(int(user_id))
