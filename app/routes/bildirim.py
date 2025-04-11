from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import current_user, login_required
from app.models import Bildirim
from app import db
from datetime import datetime

bildirim_bp = Blueprint('bildirim', __name__, url_prefix='/bildirim')

# Web arayüzü rotaları
@bildirim_bp.route('/')
@login_required
def liste():
    """Bildirim listesi sayfası."""
    bildirimler = Bildirim.query.filter_by(kullanici_id=current_user.id).order_by(Bildirim.olusturulma_zamani.desc()).all()
    
    return render_template('bildirim/liste.html', bildirimler=bildirimler)

@bildirim_bp.route('/<int:id>/okundu')
@login_required
def okundu_isaretle(id):
    """Bildirimi okundu olarak işaretleme."""
    bildirim = Bildirim.query.get_or_404(id)
    
    # Erişim kontrolü
    if bildirim.kullanici_id != current_user.id:
        abort(403)
    
    bildirim.okundu = True
    db.session.commit()
    
    return redirect(url_for('bildirim.liste'))

@bildirim_bp.route('/tumu-okundu')
@login_required
def tumu_okundu():
    """Tüm bildirimleri okundu olarak işaretleme."""
    Bildirim.query.filter_by(kullanici_id=current_user.id, okundu=False).update({'okundu': True})
    db.session.commit()
    
    flash('Tüm bildirimler okundu olarak işaretlendi', 'success')
    return redirect(url_for('bildirim.liste'))

@bildirim_bp.route('/ayarlar', methods=['GET', 'POST'])
@login_required
def ayarlar():
    """Bildirim ayarları sayfası."""
    from app.models import KullaniciBildirimAyarlari
    from app.forms.bildirim_forms import BildirimAyarlariForm
    
    # Kullanıcının bildirim ayarlarını al veya oluştur
    ayarlar = KullaniciBildirimAyarlari.query.filter_by(kullanici_id=current_user.id).first()
    if not ayarlar:
        ayarlar = KullaniciBildirimAyarlari(kullanici_id=current_user.id)
        db.session.add(ayarlar)
        db.session.commit()
    
    form = BildirimAyarlariForm(obj=ayarlar)
    if form.validate_on_submit():
        ayarlar.yeni_toplanti_uygulama_ici = form.yeni_toplanti_uygulama_ici.data
        ayarlar.yeni_toplanti_eposta = form.yeni_toplanti_eposta.data
        ayarlar.atanan_gorev_uygulama_ici = form.atanan_gorev_uygulama_ici.data
        ayarlar.atanan_gorev_eposta = form.atanan_gorev_eposta.data
        ayarlar.hatirlatma_uygulama_ici = form.hatirlatma_uygulama_ici.data
        ayarlar.hatirlatma_eposta = form.hatirlatma_eposta.data
        ayarlar.hatirlatma_suresi = form.hatirlatma_suresi.data
        
        db.session.commit()
        
        flash('Bildirim ayarları başarıyla güncellendi', 'success')
        return redirect(url_for('bildirim.ayarlar'))
    
    return render_template('bildirim/ayarlar.html', form=form)

# API rotaları
@bildirim_bp.route('/api/bildirimler', methods=['GET'])
@login_required
def api_bildirimler():
    """API bildirim listesi endpoint'i."""
    bildirimler = Bildirim.query.filter_by(kullanici_id=current_user.id).order_by(Bildirim.olusturulma_zamani.desc()).all()
    
    return jsonify({
        'bildirimler': [b.to_dict() for b in bildirimler],
        'okunmamis_sayisi': Bildirim.query.filter_by(kullanici_id=current_user.id, okundu=False).count()
    }), 200

@bildirim_bp.route('/api/bildirimler/<int:id>/okundu', methods=['PUT'])
@login_required
def api_okundu_isaretle(id):
    """API bildirimi okundu olarak işaretleme endpoint'i."""
    bildirim = Bildirim.query.get_or_404(id)
    
    # Erişim kontrolü
    if bildirim.kullanici_id != current_user.id:
        return jsonify({'message': 'Bu bildirimi işaretleme izniniz yok', 'success': False}), 403
    
    bildirim.okundu = True
    db.session.commit()
    
    return jsonify({
        'message': 'Bildirim okundu olarak işaretlendi',
        'success': True
    }), 200

@bildirim_bp.route('/api/bildirimler/tumu-okundu', methods=['PUT'])
@login_required
def api_tumu_okundu():
    """API tüm bildirimleri okundu olarak işaretleme endpoint'i."""
    Bildirim.query.filter_by(kullanici_id=current_user.id, okundu=False).update({'okundu': True})
    db.session.commit()
    
    return jsonify({
        'message': 'Tüm bildirimler okundu olarak işaretlendi',
        'success': True
    }), 200

@bildirim_bp.route('/api/bildirim-ayarlari', methods=['GET'])
@login_required
def api_bildirim_ayarlari():
    """API bildirim ayarları endpoint'i."""
    from app.models import KullaniciBildirimAyarlari
    
    ayarlar = KullaniciBildirimAyarlari.query.filter_by(kullanici_id=current_user.id).first()
    if not ayarlar:
        ayarlar = KullaniciBildirimAyarlari(kullanici_id=current_user.id)
        db.session.add(ayarlar)
        db.session.commit()
    
    return jsonify({
        'ayarlar': ayarlar.to_dict()
    }), 200

@bildirim_bp.route('/api/bildirim-ayarlari', methods=['PUT'])
@login_required
def api_bildirim_ayarlari_guncelle():
    """API bildirim ayarları güncelleme endpoint'i."""
    from app.models import KullaniciBildirimAyarlari
    
    ayarlar = KullaniciBildirimAyarlari.query.filter_by(kullanici_id=current_user.id).first()
    if not ayarlar:
        ayarlar = KullaniciBildirimAyarlari(kullanici_id=current_user.id)
        db.session.add(ayarlar)
        db.session.commit()
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Veri bulunamadı', 'success': False}), 400
    
    # Ayarları güncelle
    if 'yeni_toplanti_uygulama_ici' in data:
        ayarlar.yeni_toplanti_uygulama_ici = data['yeni_toplanti_uygulama_ici']
    if 'yeni_toplanti_eposta' in data:
        ayarlar.yeni_toplanti_eposta = data['yeni_toplanti_eposta']
    if 'atanan_gorev_uygulama_ici' in data:
        ayarlar.atanan_gorev_uygulama_ici = data['atanan_gorev_uygulama_ici']
    if 'atanan_gorev_eposta' in data:
        ayarlar.atanan_gorev_eposta = data['atanan_gorev_eposta']
    if 'hatirlatma_uygulama_ici' in data:
        ayarlar.hatirlatma_uygulama_ici = data['hatirlatma_uygulama_ici']
    if 'hatirlatma_eposta' in data:
        ayarlar.hatirlatma_eposta = data['hatirlatma_eposta']
    if 'hatirlatma_suresi' in data:
        ayarlar.hatirlatma_suresi = data['hatirlatma_suresi']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Bildirim ayarları başarıyla güncellendi',
        'success': True,
        'ayarlar': ayarlar.to_dict()
    }), 200
