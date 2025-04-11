from app.extensions import login_manager, mail, bcrypt
from flask_mail import Message
from flask import current_app, render_template
from itsdangerous import URLSafeTimedSerializer
import uuid

class AuthService:
    """Kimlik doğrulama servisi"""
    
    def get_user_by_id(self, user_id):
        """Kullanıcı ID'sine göre kullanıcı bilgilerini getirir"""
        from app.models.kullanici import Kullanici
        return Kullanici.query.get(user_id)
    
    def get_user_by_email(self, email):
        """E-posta adresine göre kullanıcı bilgilerini getirir"""
        from app.models.kullanici import Kullanici
        return Kullanici.query.filter_by(eposta=email).first()
    
    def create_password_hash(self, password):
        """Şifre için hash oluşturur"""
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password_hash, password):
        """Şifre doğrulaması yapar"""
        return bcrypt.check_password_hash(password_hash, password)
    
    def generate_confirmation_token(self, email):
        """E-posta onayı için token oluşturur"""
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])
    
    def confirm_token(self, token, expiration=3600):
        """Token doğrulaması yapar"""
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = serializer.loads(
                token,
                salt=current_app.config['SECURITY_PASSWORD_SALT'],
                max_age=expiration
            )
            return email
        except:
            return False
    
    def generate_reset_token(self):
        """Şifre sıfırlama için token oluşturur"""
        return str(uuid.uuid4())
    
    def send_password_reset_email(self, email, reset_url):
        """Şifre sıfırlama e-postası gönderir"""
        msg = Message(
            'Şifre Sıfırlama İsteği',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email]
        )
        msg.html = render_template(
            'email/reset_password.html',
            reset_url=reset_url
        )
        mail.send(msg)
    
    def send_confirmation_email(self, email, confirm_url):
        """E-posta onayı için e-posta gönderir"""
        msg = Message(
            'E-posta Adresinizi Onaylayın',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email]
        )
        msg.html = render_template(
            'email/confirm_email.html',
            confirm_url=confirm_url
        )
        mail.send(msg)
    
    def send_notification_email(self, email, subject, template, **kwargs):
        """Bildirim e-postası gönderir"""
        msg = Message(
            subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email]
        )
        msg.html = render_template(
            template,
            **kwargs
        )
        mail.send(msg)

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login için kullanıcı yükleme fonksiyonu"""
    from app.models.kullanici import Kullanici
    return Kullanici.query.get(int(user_id))
