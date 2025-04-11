from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import current_user, login_required
from app.models import Urun, Not, Gorev
from app import db
from datetime import datetime
from app.forms.urun_forms import UrunForm

urun_bp = Blueprint('urun', __name__, url_prefix='/urun')

# Web arayüzü rotaları
@urun_bp.route('/')
@login_required
def liste():
    """Ürün listesi sayfası."""
    urunler = Urun.query.all()
    return render_template('urun/liste.html', urunler=urunler)

@urun_bp.route('/yeni', methods=['GET', 'POST'])
@login_required
def yeni():
    """Yeni ürün oluşturma sayfası."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        flash('Bu işlem için yetkiniz yok', 'danger')
        return redirect(url_for('urun.liste'))
    
    form = UrunForm()
    if form.validate_on_submit():
        urun = Urun(
            ad=form.ad.data,
            aciklama=form.aciklama.data,
            gorsel_url=form.gorsel_url.data if form.gorsel_url.data else None
        )
        
        db.session.add(urun)
        db.session.commit()
        
        flash('Ürün başarıyla oluşturuldu', 'success')
        return redirect(url_for('urun.detay', id=urun.id))
    
    return render_template('urun/yeni.html', form=form)

@urun_bp.route('/<int:id>')
@login_required
def detay(id):
    """Ürün detay sayfası."""
    urun = Urun.query.get_or_404(id)
    notlar = Not.query.filter_by(urun_id=id).all()
    gorevler = Gorev.query.filter_by(urun_id=id).all()
    
    return render_template('urun/detay.html',
                          urun=urun,
                          notlar=notlar,
                          gorevler=gorevler)

@urun_bp.route('/<int:id>/duzenle', methods=['GET', 'POST'])
@login_required
def duzenle(id):
    """Ürün düzenleme sayfası."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        flash('Bu işlem için yetkiniz yok', 'danger')
        return redirect(url_for('urun.liste'))
    
    urun = Urun.query.get_or_404(id)
    form = UrunForm(obj=urun)
    
    if form.validate_on_submit():
        urun.ad = form.ad.data
        urun.aciklama = form.aciklama.data
        urun.gorsel_url = form.gorsel_url.data if form.gorsel_url.data else None
        
        db.session.commit()
        
        flash('Ürün başarıyla güncellendi', 'success')
        return redirect(url_for('urun.detay', id=urun.id))
    
    return render_template('urun/duzenle.html', form=form, urun=urun)

@urun_bp.route('/<int:id>/sil', methods=['POST'])
@login_required
def sil(id):
    """Ürün silme işlemi."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        flash('Bu işlem için yetkiniz yok', 'danger')
        return redirect(url_for('urun.liste'))
    
    urun = Urun.query.get_or_404(id)
    
    # İlişkili kayıtları kontrol et
    notlar_count = Not.query.filter_by(urun_id=id).count()
    gorevler_count = Gorev.query.filter_by(urun_id=id).count()
    
    if notlar_count > 0 or gorevler_count > 0:
        flash('Bu ürün ile ilişkili notlar veya görevler bulunduğu için silinemez', 'danger')
        return redirect(url_for('urun.detay', id=id))
    
    db.session.delete(urun)
    db.session.commit()
    
    flash('Ürün başarıyla silindi', 'success')
    return redirect(url_for('urun.liste'))

# API rotaları
@urun_bp.route('/api/urunler', methods=['GET'])
@login_required
def api_urunler():
    """API ürün listesi endpoint'i."""
    urunler = Urun.query.all()
    
    return jsonify({
        'urunler': [u.to_dict() for u in urunler]
    }), 200

@urun_bp.route('/api/urunler', methods=['POST'])
@login_required
def api_urun_olustur():
    """API ürün oluşturma endpoint'i."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        return jsonify({'message': 'Bu işlem için yetkiniz yok', 'success': False}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Veri bulunamadı', 'success': False}), 400
    
    # Zorunlu alanları kontrol et
    if 'ad' not in data:
        return jsonify({'message': 'Ad alanı zorunludur', 'success': False}), 400
    
    # Ürün oluştur
    urun = Urun(
        ad=data.get('ad'),
        aciklama=data.get('aciklama', ''),
        gorsel_url=data.get('gorsel_url')
    )
    
    db.session.add(urun)
    db.session.commit()
    
    return jsonify({
        'message': 'Ürün başarıyla oluşturuldu',
        'success': True,
        'urun': urun.to_dict()
    }), 201

@urun_bp.route('/api/urunler/<int:id>', methods=['GET'])
@login_required
def api_urun_detay(id):
    """API ürün detay endpoint'i."""
    urun = Urun.query.get_or_404(id)
    notlar = Not.query.filter_by(urun_id=id).all()
    gorevler = Gorev.query.filter_by(urun_id=id).all()
    
    return jsonify({
        'urun': urun.to_dict(),
        'notlar': [n.to_dict() for n in notlar],
        'gorevler': [g.to_dict() for g in gorevler]
    }), 200

@urun_bp.route('/api/urunler/<int:id>', methods=['PUT'])
@login_required
def api_urun_guncelle(id):
    """API ürün güncelleme endpoint'i."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        return jsonify({'message': 'Bu işlem için yetkiniz yok', 'success': False}), 403
    
    urun = Urun.query.get_or_404(id)
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Veri bulunamadı', 'success': False}), 400
    
    # Ürünü güncelle
    if 'ad' in data:
        urun.ad = data['ad']
    if 'aciklama' in data:
        urun.aciklama = data['aciklama']
    if 'gorsel_url' in data:
        urun.gorsel_url = data['gorsel_url']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Ürün başarıyla güncellendi',
        'success': True,
        'urun': urun.to_dict()
    }), 200

@urun_bp.route('/api/urunler/<int:id>', methods=['DELETE'])
@login_required
def api_urun_sil(id):
    """API ürün silme endpoint'i."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        return jsonify({'message': 'Bu işlem için yetkiniz yok', 'success': False}), 403
    
    urun = Urun.query.get_or_404(id)
    
    # İlişkili kayıtları kontrol et
    notlar_count = Not.query.filter_by(urun_id=id).count()
    gorevler_count = Gorev.query.filter_by(urun_id=id).count()
    
    if notlar_count > 0 or gorevler_count > 0:
        return jsonify({
            'message': 'Bu ürün ile ilişkili notlar veya görevler bulunduğu için silinemez',
            'success': False
        }), 400
    
    db.session.delete(urun)
    db.session.commit()
    
    return jsonify({
        'message': 'Ürün başarıyla silindi',
        'success': True
    }), 200
