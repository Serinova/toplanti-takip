from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import current_user, login_required
from app.models import GundemMaddesi, Not, Toplanti
from app import db
from datetime import datetime
from app.forms.gundem_forms import NotForm

gundem_bp = Blueprint('gundem', __name__, url_prefix='/gundem')

# Web arayüzü rotaları
@gundem_bp.route('/<int:id>/notlar')
@login_required
def notlar(id):
    """Gündem maddesi notları sayfası."""
    gundem_maddesi = GundemMaddesi.query.get_or_404(id)
    toplanti = Toplanti.query.get_or_404(gundem_maddesi.toplanti_id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        katilimci = Katilimci.query.filter_by(
            toplanti_id=toplanti.id, 
            kullanici_id=current_user.id
        ).first()
        
        if not katilimci:
            abort(403)
    
    notlar = Not.query.filter_by(gundem_madde_id=id).all()
    
    return render_template('gundem/notlar.html', 
                          gundem_maddesi=gundem_maddesi,
                          toplanti=toplanti,
                          notlar=notlar)

@gundem_bp.route('/<int:id>/not/ekle', methods=['GET', 'POST'])
@login_required
def not_ekle(id):
    """Not ekleme sayfası."""
    gundem_maddesi = GundemMaddesi.query.get_or_404(id)
    toplanti = Toplanti.query.get_or_404(gundem_maddesi.toplanti_id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        katilimci = Katilimci.query.filter_by(
            toplanti_id=toplanti.id, 
            kullanici_id=current_user.id
        ).first()
        
        if not katilimci:
            abort(403)
    
    form = NotForm()
    if form.validate_on_submit():
        not_obj = Not(
            toplanti_id=toplanti.id,
            kullanici_id=current_user.id,
            gundem_madde_id=id,
            icerik=form.icerik.data
        )
        
        db.session.add(not_obj)
        db.session.commit()
        
        flash('Not başarıyla eklendi', 'success')
        return redirect(url_for('gundem.notlar', id=id))
    
    return render_template('gundem/not_ekle.html', 
                          form=form,
                          gundem_maddesi=gundem_maddesi,
                          toplanti=toplanti)

@gundem_bp.route('/not/<int:id>/duzenle', methods=['GET', 'POST'])
@login_required
def not_duzenle(id):
    """Not düzenleme sayfası."""
    not_obj = Not.query.get_or_404(id)
    
    # Erişim kontrolü
    if not_obj.kullanici_id != current_user.id:
        abort(403)
    
    gundem_maddesi = GundemMaddesi.query.get_or_404(not_obj.gundem_madde_id)
    toplanti = Toplanti.query.get_or_404(not_obj.toplanti_id)
    
    form = NotForm(obj=not_obj)
    if form.validate_on_submit():
        not_obj.icerik = form.icerik.data
        db.session.commit()
        
        flash('Not başarıyla güncellendi', 'success')
        return redirect(url_for('gundem.notlar', id=not_obj.gundem_madde_id))
    
    return render_template('gundem/not_duzenle.html', 
                          form=form,
                          not_obj=not_obj,
                          gundem_maddesi=gundem_maddesi,
                          toplanti=toplanti)

@gundem_bp.route('/not/<int:id>/sil', methods=['POST'])
@login_required
def not_sil(id):
    """Not silme işlemi."""
    not_obj = Not.query.get_or_404(id)
    
    # Erişim kontrolü
    if not_obj.kullanici_id != current_user.id:
        abort(403)
    
    gundem_madde_id = not_obj.gundem_madde_id
    
    db.session.delete(not_obj)
    db.session.commit()
    
    flash('Not başarıyla silindi', 'success')
    return redirect(url_for('gundem.notlar', id=gundem_madde_id))

# API rotaları
@gundem_bp.route('/api/gundem/<int:id>/notlar', methods=['GET'])
@login_required
def api_notlar(id):
    """API gündem maddesi notları endpoint'i."""
    gundem_maddesi = GundemMaddesi.query.get_or_404(id)
    toplanti = Toplanti.query.get_or_404(gundem_maddesi.toplanti_id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        katilimci = Katilimci.query.filter_by(
            toplanti_id=toplanti.id, 
            kullanici_id=current_user.id
        ).first()
        
        if not katilimci:
            return jsonify({'message': 'Bu gündem maddesine erişim izniniz yok', 'success': False}), 403
    
    notlar = Not.query.filter_by(gundem_madde_id=id).all()
    
    return jsonify({
        'gundem_maddesi': gundem_maddesi.to_dict(),
        'notlar': [n.to_dict() for n in notlar]
    }), 200

@gundem_bp.route('/api/gundem/<int:id>/notlar', methods=['POST'])
@login_required
def api_not_ekle(id):
    """API not ekleme endpoint'i."""
    gundem_maddesi = GundemMaddesi.query.get_or_404(id)
    toplanti = Toplanti.query.get_or_404(gundem_maddesi.toplanti_id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        katilimci = Katilimci.query.filter_by(
            toplanti_id=toplanti.id, 
            kullanici_id=current_user.id
        ).first()
        
        if not katilimci:
            return jsonify({'message': 'Bu gündem maddesine erişim izniniz yok', 'success': False}), 403
    
    data = request.get_json()
    
    if not data or 'icerik' not in data:
        return jsonify({'message': 'İçerik alanı zorunludur', 'success': False}), 400
    
    not_obj = Not(
        toplanti_id=toplanti.id,
        kullanici_id=current_user.id,
        gundem_madde_id=id,
        icerik=data['icerik']
    )
    
    db.session.add(not_obj)
    db.session.commit()
    
    return jsonify({
        'message': 'Not başarıyla eklendi',
        'success': True,
        'not': not_obj.to_dict()
    }), 201

@gundem_bp.route('/api/not/<int:id>', methods=['PUT'])
@login_required
def api_not_guncelle(id):
    """API not güncelleme endpoint'i."""
    not_obj = Not.query.get_or_404(id)
    
    # Erişim kontrolü
    if not_obj.kullanici_id != current_user.id:
        return jsonify({'message': 'Bu notu güncelleme izniniz yok', 'success': False}), 403
    
    data = request.get_json()
    
    if not data or 'icerik' not in data:
        return jsonify({'message': 'İçerik alanı zorunludur', 'success': False}), 400
    
    not_obj.icerik = data['icerik']
    db.session.commit()
    
    return jsonify({
        'message': 'Not başarıyla güncellendi',
        'success': True,
        'not': not_obj.to_dict()
    }), 200

@gundem_bp.route('/api/not/<int:id>', methods=['DELETE'])
@login_required
def api_not_sil(id):
    """API not silme endpoint'i."""
    not_obj = Not.query.get_or_404(id)
    
    # Erişim kontrolü
    if not_obj.kullanici_id != current_user.id:
        return jsonify({'message': 'Bu notu silme izniniz yok', 'success': False}), 403
    
    db.session.delete(not_obj)
    db.session.commit()
    
    return jsonify({
        'message': 'Not başarıyla silindi',
        'success': True
    }), 200
