from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import current_user, login_required
from app.models import Gorev, GorevYorumu, Toplanti, Kullanici
from app import db
from datetime import datetime
from app.forms.gorev_forms import GorevForm, GorevYorumForm
from app.services.gorev_service import get_gorev_yorumlari, get_kullanici_gorevleri

gorev_bp = Blueprint('gorev', __name__, url_prefix='/gorev')

# Web arayüzü rotaları
@gorev_bp.route('/')
@login_required
def liste():
    """Görev listesi sayfası."""
    # Kullanıcıya atanan görevler
    atanan_gorevler = Gorev.query.filter_by(atanan_kullanici_id=current_user.id).all()
    
    # Kullanıcının oluşturduğu görevler
    olusturulan_gorevler = Gorev.query.filter_by(olusturan_kullanici_id=current_user.id).all()
    
    return render_template('gorev/liste.html', 
                          atanan_gorevler=atanan_gorevler,
                          olusturulan_gorevler=olusturulan_gorevler)

@gorev_bp.route('/yeni', methods=['GET', 'POST'])
@login_required
def yeni():
    """Yeni görev oluşturma sayfası."""
    form = GorevForm()
    
    # Kullanıcı listesini form için hazırla
    kullanicilar = Kullanici.query.all()
    form.atanan_kullanici_id.choices = [(k.id, k.ad) for k in kullanicilar]
    
    # Toplantı listesini form için hazırla
    toplantilar = Toplanti.query.filter_by(olusturan_kullanici_id=current_user.id).all()
    form.toplanti_id.choices = [(0, 'Toplantı Seçiniz')] + [(t.id, t.baslik) for t in toplantilar]
    
    if form.validate_on_submit():
        gorev = Gorev(
            toplanti_id=form.toplanti_id.data if form.toplanti_id.data != 0 else None,
            atanan_kullanici_id=form.atanan_kullanici_id.data,
            olusturan_kullanici_id=current_user.id,
            baslik=form.baslik.data,
            aciklama=form.aciklama.data,
            son_teslim_tarihi=form.son_teslim_tarihi.data,
            puan_degeri=form.puan_degeri.data
        )
        
        db.session.add(gorev)
        db.session.commit()
        
        flash('Görev başarıyla oluşturuldu', 'success')
        return redirect(url_for('gorev.detay', id=gorev.id))
    
    return render_template('gorev/yeni.html', form=form)

@gorev_bp.route('/<int:id>')
@login_required
def detay(id):
    """Görev detay sayfası."""
    gorev = Gorev.query.get_or_404(id)
    
    # Erişim kontrolü
    if gorev.atanan_kullanici_id != current_user.id and gorev.olusturan_kullanici_id != current_user.id:
        abort(403)
    
    yorumlar = get_gorev_yorumlari(gorev.id)
    
    return render_template('gorev/detay.html',
                          gorev=gorev,
                          yorumlar=yorumlar)

@gorev_bp.route('/<int:id>/duzenle', methods=['GET', 'POST'])
@login_required
def duzenle(id):
    """Görev düzenleme sayfası."""
    gorev = Gorev.query.get_or_404(id)
    
    # Erişim kontrolü
    if gorev.olusturan_kullanici_id != current_user.id:
        abort(403)
    
    form = GorevForm(obj=gorev)
    
    # Kullanıcı listesini form için hazırla
    kullanicilar = Kullanici.query.all()
    form.atanan_kullanici_id.choices = [(k.id, k.ad) for k in kullanicilar]
    
    # Toplantı listesini form için hazırla
    toplantilar = Toplanti.query.filter_by(olusturan_kullanici_id=current_user.id).all()
    form.toplanti_id.choices = [(0, 'Toplantı Seçiniz')] + [(t.id, t.baslik) for t in toplantilar]
    
    if form.validate_on_submit():
        gorev.toplanti_id = form.toplanti_id.data if form.toplanti_id.data != 0 else None
        gorev.atanan_kullanici_id = form.atanan_kullanici_id.data
        gorev.baslik = form.baslik.data
        gorev.aciklama = form.aciklama.data
        gorev.son_teslim_tarihi = form.son_teslim_tarihi.data
        gorev.puan_degeri = form.puan_degeri.data
        
        db.session.commit()
        
        flash('Görev başarıyla güncellendi', 'success')
        return redirect(url_for('gorev.detay', id=gorev.id))
    
    return render_template('gorev/duzenle.html', form=form, gorev=gorev)

@gorev_bp.route('/<int:id>/durum-guncelle', methods=['POST'])
@login_required
def durum_guncelle(id):
    """Görev durumu güncelleme işlemi."""
    gorev = Gorev.query.get_or_404(id)
    
    # Erişim kontrolü
    if gorev.atanan_kullanici_id != current_user.id and gorev.olusturan_kullanici_id != current_user.id:
        abort(403)
    
    durum = request.form.get('durum')
    if durum not in ['Yapılacak', 'Devam Ediyor', 'Tamamlandı']:
        flash('Geçersiz durum', 'danger')
        return redirect(url_for('gorev.detay', id=gorev.id))
    
    gorev.durum = durum
    
    # Eğer durum "Tamamlandı" ise tamamlanma zamanını güncelle
    if durum == 'Tamamlandı':
        gorev.tamamlanma_zamani = datetime.utcnow()
    else:
        gorev.tamamlanma_zamani = None
    
    db.session.commit()
    
    flash('Görev durumu başarıyla güncellendi', 'success')
    return redirect(url_for('gorev.detay', id=gorev.id))

@gorev_bp.route('/<int:id>/yorum-ekle', methods=['POST'])
@login_required
def yorum_ekle(id):
    """Görev yorumu ekleme işlemi."""
    gorev = Gorev.query.get_or_404(id)
    
    # Erişim kontrolü
    if gorev.atanan_kullanici_id != current_user.id and gorev.olusturan_kullanici_id != current_user.id:
        abort(403)
    
    form = GorevYorumForm()
    if form.validate_on_submit():
        yorum = GorevYorumu(
            gorev_id=gorev.id,
            yazan_kullanici_id=current_user.id,
            yorum=form.yorum.data
        )
        
        db.session.add(yorum)
        db.session.commit()
        
        flash('Yorum başarıyla eklendi', 'success')
    
    return redirect(url_for('gorev.detay', id=gorev.id))

# API rotaları
@gorev_bp.route('/api/gorevler', methods=['GET'])
@login_required
def api_gorevler():
    """API görev listesi endpoint'i."""
    # Kullanıcıya atanan görevler
    atanan_gorevler = Gorev.query.filter_by(atanan_kullanici_id=current_user.id).all()
    
    # Kullanıcının oluşturduğu görevler
    olusturulan_gorevler = Gorev.query.filter_by(olusturan_kullanici_id=current_user.id).all()
    
    return jsonify({
        'atanan_gorevler': [g.to_dict() for g in atanan_gorevler],
        'olusturulan_gorevler': [g.to_dict() for g in olusturulan_gorevler]
    }), 200

@gorev_bp.route('/api/gorevler', methods=['POST'])
@login_required
def api_gorev_olustur():
    """API görev oluşturma endpoint'i."""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Veri bulunamadı', 'success': False}), 400
    
    # Zorunlu alanları kontrol et
    required_fields = ['atanan_kullanici_id', 'baslik', 'son_teslim_tarihi']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} alanı zorunludur', 'success': False}), 400
    
    # Görev oluştur
    gorev = Gorev(
        toplanti_id=data.get('toplanti_id'),
        atanan_kullanici_id=data.get('atanan_kullanici_id'),
        olusturan_kullanici_id=current_user.id,
        baslik=data.get('baslik'),
        aciklama=data.get('aciklama', ''),
        son_teslim_tarihi=datetime.fromisoformat(data.get('son_teslim_tarihi')),
        puan_degeri=data.get('puan_degeri', 0)
    )
    
    db.session.add(gorev)
    db.session.commit()
    
    return jsonify({
        'message': 'Görev başarıyla oluşturuldu',
        'success': True,
        'gorev': gorev.to_dict()
    }), 201

@gorev_bp.route('/api/gorevler/<int:id>', methods=['GET'])
@login_required
def api_gorev_detay(id):
    """API görev detay endpoint'i."""
    gorev = Gorev.query.get_or_404(id)
    
    # Erişim kontrolü
    if gorev.atanan_kullanici_id != current_user.id and gorev.olusturan_kullanici_id != current_user.id:
        return jsonify({'message': 'Bu göreve erişim izniniz yok', 'success': False}), 403
    
    yorumlar = get_gorev_yorumlari(gorev.id)
    
    return jsonify({
        'gorev': gorev.to_dict(),
        'yorumlar': yorumlar
    }), 200

@gorev_bp.route('/api/gorevler/<int:id>', methods=['PUT'])
@login_required
def api_gorev_guncelle(id):
    """API görev güncelleme endpoint'i."""
    gorev = Gorev.query.get_or_404(id)
    
    # Erişim kontrolü
    if gorev.olusturan_kullanici_id != current_user.id:
        return jsonify({'message': 'Bu görevi güncelleme izniniz yok', 'success': False}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Veri bulunamadı', 'success': False}), 400
    
    # Görevi güncelle
    if 'toplanti_id' in data:
        gorev.toplanti_id = data['toplanti_id']
    if 'atanan_kullanici_id' in data:
        gorev.atanan_kullanici_id = data['atanan_kullanici_id']
    if 'baslik' in data:
        gorev.baslik = data['baslik']
    if 'aciklama' in data:
        gorev.aciklama = data['aciklama']
    if 'son_teslim_tarihi' in data:
        gorev.son_teslim_tarihi = datetime.fromisoformat(data['son_teslim_tarihi'])
    if 'puan_degeri' in data:
        gorev.puan_degeri = data['puan_degeri']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Görev başarıyla güncellendi',
        'success': True,
        'gorev': gorev.to_dict()
    }), 200

@gorev_bp.route('/api/gorevler/<int:id>/durum', methods=['PUT'])
@login_required
def api_gorev_durum_guncelle(id):
    """API görev durumu güncelleme endpoint'i."""
    gorev = Gorev.query.get_or_404(id)
    
    # Erişim kontrolü
    if gorev.atanan_kullanici_id != current_user.id and gorev.olusturan_kullanici_id != current_user.id:
        return jsonify({'message': 'Bu görevi güncelleme izniniz yok', 'success': False}), 403
    
    data = request.get_json()
    
    if not data or 'durum' not in data:
        return jsonify({'message': 'Durum alanı zorunludur', 'success': False}), 400
    
    durum = data['durum']
    if durum not in ['Yapılacak', 'Devam Ediyor', 'Tamamlandı']:
        return jsonify({'message': 'Geçersiz durum', 'success': False}), 400
    
    gorev.durum = durum
    
    # Eğer durum "Tamamlandı" ise tamamlanma zamanını güncelle
    if durum == 'Tamamlandı':
        gorev.tamamlanma_zamani = datetime.utcnow()
    else:
        gorev.tamamlanma_zamani = None
    
    db.session.commit()
    
    return jsonify({
        'message': 'Görev durumu başarıyla güncellendi',
        'success': True,
        'gorev': gorev.to_dict()
    }), 200

@gorev_bp.route('/api/gorevler/<int:id>/yorumlar', methods=['POST'])
@login_required
def api_gorev_yorum_ekle(id):
    """API görev yorumu ekleme endpoint'i."""
    gorev = Gorev.query.get_or_404(id)
    
    # Erişim kontrolü
    if gorev.atanan_kullanici_id != current_user.id and gorev.olusturan_kullanici_id != current_user.id:
        return jsonify({'message': 'Bu göreve yorum ekleme izniniz yok', 'success': False}), 403
    
    data = request.get_json()
    
    if not data or 'yorum' not in data:
        return jsonify({'message': 'Yorum alanı zorunludur', 'success': False}), 400
    
    yorum = GorevYorumu(
        gorev_id=gorev.id,
        yazan_kullanici_id=current_user.id,
        yorum=data['yorum']
    )
    
    db.session.add(yorum)
    db.session.commit()
    
    return jsonify({
        'message': 'Yorum başarıyla eklendi',
        'success': True,
        'yorum': yorum.to_dict()
    }), 201
