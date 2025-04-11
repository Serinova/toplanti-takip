from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.kullanici import Kullanici
from app.forms import ProfileForm, ChangePasswordForm, BildirimAyarForm
from app.services.auth_service import AuthService
from werkzeug.utils import secure_filename
import os
from datetime import datetime

profile_bp = Blueprint('profile', __name__)
auth_service = AuthService()

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    """Kullanıcı profil sayfası"""
    form = ProfileForm()
    
    if form.validate_on_submit():
        # Profil bilgilerini güncelle
        current_user.ad = form.ad.data
        current_user.telefon = form.telefon.data
        current_user.unvan = form.unvan.data
        current_user.departman = form.departman.data
        
        # Profil resmi yükleme
        if form.profil_resmi.data:
            filename = secure_filename(form.profil_resmi.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            upload_folder = os.path.join(current_app.static_folder, 'uploads', 'profile_images')
            os.makedirs(upload_folder, exist_ok=True)
            
            filepath = os.path.join(upload_folder, filename)
            form.profil_resmi.data.save(filepath)
            
            # Veritabanında profil resmi URL'sini güncelle
            current_user.profil_resmi_url = f'/static/uploads/profile_images/{filename}'
        
        db.session.commit()
        flash('Profil bilgileriniz başarıyla güncellendi', 'success')
        return redirect(url_for('profile.view_profile'))
    
    # Form alanlarını mevcut değerlerle doldur
    if request.method == 'GET':
        form.ad.data = current_user.ad
        form.eposta.data = current_user.eposta
        form.telefon.data = current_user.telefon
        form.unvan.data = current_user.unvan
        form.departman.data = current_user.departman
    
    # Kullanıcı istatistiklerini hesapla
    toplam_puan = current_user.get_toplam_puan()
    tamamlanan_gorev_sayisi = current_user.get_tamamlanan_gorev_sayisi()
    bekleyen_gorev_sayisi = current_user.get_bekleyen_gorev_sayisi()
    
    return render_template('profile/view_profile.html', 
                          form=form, 
                          toplam_puan=toplam_puan,
                          tamamlanan_gorev_sayisi=tamamlanan_gorev_sayisi,
                          bekleyen_gorev_sayisi=bekleyen_gorev_sayisi)

@profile_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Şifre değiştirme sayfası"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Mevcut şifre kontrolü
        if auth_service.check_password(current_user.sifre_hash, form.mevcut_sifre.data):
            # Yeni şifre hash'i oluştur
            sifre_hash = auth_service.create_password_hash(form.yeni_sifre.data)
            current_user.sifre_hash = sifre_hash
            db.session.commit()
            
            flash('Şifreniz başarıyla değiştirildi', 'success')
            return redirect(url_for('profile.view_profile'))
        else:
            flash('Mevcut şifreniz yanlış', 'danger')
    
    return render_template('profile/change_password.html', form=form)

@profile_bp.route('/notification-settings', methods=['GET', 'POST'])
@login_required
def notification_settings():
    """Bildirim ayarları sayfası"""
    # Kullanıcının bildirim ayarlarını getir
    from app.models.bildirim import BildirimAyarlari
    
    ayarlar = BildirimAyarlari.query.filter_by(kullanici_id=current_user.id).first()
    if not ayarlar:
        # Varsayılan ayarlarla yeni bir kayıt oluştur
        ayarlar = BildirimAyarlari(kullanici_id=current_user.id)
        db.session.add(ayarlar)
        db.session.commit()
    
    form = BildirimAyarForm()
    
    if form.validate_on_submit():
        # Bildirim ayarlarını güncelle
        ayarlar.toplanti_davet = form.toplanti_davet.data
        ayarlar.toplanti_guncelleme = form.toplanti_guncelleme.data
        ayarlar.toplanti_iptal = form.toplanti_iptal.data
        ayarlar.toplanti_hatirlatma = form.toplanti_hatirlatma.data
        ayarlar.gorev_atama = form.gorev_atama.data
        ayarlar.gorev_guncelleme = form.gorev_guncelleme.data
        ayarlar.gorev_tamamlama = form.gorev_tamamlama.data
        ayarlar.gorev_hatirlatma = form.gorev_hatirlatma.data
        ayarlar.yorum_ekleme = form.yorum_ekleme.data
        ayarlar.eposta_bildirim = form.eposta_bildirim.data
        
        db.session.commit()
        flash('Bildirim ayarlarınız başarıyla güncellendi', 'success')
        return redirect(url_for('profile.notification_settings'))
    
    # Form alanlarını mevcut değerlerle doldur
    if request.method == 'GET':
        form.toplanti_davet.data = ayarlar.toplanti_davet
        form.toplanti_guncelleme.data = ayarlar.toplanti_guncelleme
        form.toplanti_iptal.data = ayarlar.toplanti_iptal
        form.toplanti_hatirlatma.data = ayarlar.toplanti_hatirlatma
        form.gorev_atama.data = ayarlar.gorev_atama
        form.gorev_guncelleme.data = ayarlar.gorev_guncelleme
        form.gorev_tamamlama.data = ayarlar.gorev_tamamlama
        form.gorev_hatirlatma.data = ayarlar.gorev_hatirlatma
        form.yorum_ekleme.data = ayarlar.yorum_ekleme
        form.eposta_bildirim.data = ayarlar.eposta_bildirim
    
    return render_template('profile/notification_settings.html', form=form)
