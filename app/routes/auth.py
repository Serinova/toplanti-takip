from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime, timedelta
import uuid

from app.extensions import db, bcrypt
from app.forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from app.models.kullanici import Kullanici
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Kullanıcı giriş sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        kullanici = Kullanici.query.filter_by(eposta=form.eposta.data).first()
        if kullanici and bcrypt.check_password_hash(kullanici.sifre_hash, form.sifre.data):
            login_user(kullanici, remember=form.beni_hatirla.data)
            kullanici.son_giris_tarihi = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('dashboard.index')
            return redirect(next_page)
        else:
            flash('Geçersiz e-posta veya şifre', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Kullanıcı çıkış işlemi"""
    logout_user()
    flash('Başarıyla çıkış yaptınız', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Kullanıcı kayıt sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # E-posta adresi kontrolü
        existing_user = Kullanici.query.filter_by(eposta=form.eposta.data).first()
        if existing_user:
            flash('Bu e-posta adresi zaten kullanılıyor', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Yeni kullanıcı oluşturma
        sifre_hash = bcrypt.generate_password_hash(form.sifre.data).decode('utf-8')
        yeni_kullanici = Kullanici(
            ad=form.ad.data,
            eposta=form.eposta.data,
            sifre_hash=sifre_hash,
            rol='kullanici',
            aktif=True,
            kayit_tarihi=datetime.utcnow()
        )
        
        db.session.add(yeni_kullanici)
        db.session.commit()
        
        flash('Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Şifremi unuttum sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        kullanici = Kullanici.query.filter_by(eposta=form.eposta.data).first()
        if kullanici:
            # Şifre sıfırlama token'ı oluştur
            token = str(uuid.uuid4())
            kullanici.sifre_sifirlama_token = token
            kullanici.sifre_sifirlama_son_tarih = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # E-posta gönderme işlemi
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            auth_service.send_password_reset_email(kullanici.eposta, reset_url)
            
            flash('Şifre sıfırlama bağlantısı e-posta adresinize gönderildi', 'info')
        else:
            # Güvenlik için kullanıcı bulunamasa bile aynı mesajı göster
            flash('Şifre sıfırlama bağlantısı e-posta adresinize gönderildi', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Şifre sıfırlama sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # Token kontrolü
    kullanici = Kullanici.query.filter_by(sifre_sifirlama_token=token).first()
    if not kullanici or kullanici.sifre_sifirlama_son_tarih < datetime.utcnow():
        flash('Geçersiz veya süresi dolmuş şifre sıfırlama bağlantısı', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Şifre güncelleme
        sifre_hash = bcrypt.generate_password_hash(form.sifre.data).decode('utf-8')
        kullanici.sifre_hash = sifre_hash
        kullanici.sifre_sifirlama_token = None
        kullanici.sifre_sifirlama_son_tarih = None
        db.session.commit()
        
        flash('Şifreniz başarıyla güncellendi! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form, token=token)
