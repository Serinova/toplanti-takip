from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import current_user, login_required
from app.models import Toplanti, Katilimci, MisafirKatilimci, GundemMaddesi, Not, Dosya
from app import db
from datetime import datetime
from app.forms.toplanti_forms import ToplantiForm, GundemMaddesiForm
from app.services.toplanti_service import get_toplanti_katilimcilar, get_toplanti_gundem_maddeleri
from app.services.ai_service import toplanti_ozetle, gundem_maddeleri_olustur

toplanti_bp = Blueprint('toplanti', __name__, url_prefix='/toplanti')

# Web arayüzü rotaları
@toplanti_bp.route('/')
@login_required
def liste():
    """Toplantı listesi sayfası."""
    # Kullanıcının oluşturduğu toplantılar
    olusturulan_toplantilar = Toplanti.query.filter_by(olusturan_kullanici_id=current_user.id).all()
    
    # Kullanıcının katılımcı olduğu toplantılar
    katilimci_toplantilar = db.session.query(Toplanti).join(
        Katilimci, Toplanti.id == Katilimci.toplanti_id
    ).filter(
        Katilimci.kullanici_id == current_user.id
    ).all()
    
    return render_template('toplanti/liste.html', 
                          olusturulan_toplantilar=olusturulan_toplantilar,
                          katilimci_toplantilar=katilimci_toplantilar)

@toplanti_bp.route('/yeni', methods=['GET', 'POST'])
@login_required
def yeni():
    """Yeni toplantı oluşturma sayfası."""
    form = ToplantiForm()
    if form.validate_on_submit():
        toplanti = Toplanti(
            olusturan_kullanici_id=current_user.id,
            baslik=form.baslik.data,
            aciklama=form.aciklama.data,
            baslangic_zamani=form.baslangic_zamani.data,
            bitis_zamani=form.bitis_zamani.data,
            konum=form.konum.data,
            sanal_toplanti_linki=form.sanal_toplanti_linki.data,
            tekrar_sikligi=form.tekrar_sikligi.data,
            tekrar_bitis_tarihi=form.tekrar_bitis_tarihi.data
        )
        
        db.session.add(toplanti)
        db.session.commit()
        
        # Katılımcıları ekle
        if form.katilimcilar.data:
            for kullanici_id in form.katilimcilar.data:
                katilimci = Katilimci(
                    toplanti_id=toplanti.id,
                    kullanici_id=kullanici_id,
                    davet_durumu='Bekliyor'
                )
                db.session.add(katilimci)
            
            db.session.commit()
        
        # Misafir katılımcıları ekle
        if form.misafir_katilimcilar.data:
            for misafir_data in form.misafir_katilimcilar.data.split(','):
                if '@' in misafir_data:
                    misafir = MisafirKatilimci(
                        toplanti_id=toplanti.id,
                        eposta=misafir_data.strip(),
                        ad=''
                    )
                    db.session.add(misafir)
            
            db.session.commit()
        
        # Yapay zeka ile gündem maddeleri oluştur
        if form.ai_gundem_olustur.data:
            gundem_maddeleri = gundem_maddeleri_olustur(toplanti.baslik, toplanti.aciklama)
            for i, madde in enumerate(gundem_maddeleri):
                gundem_maddesi = GundemMaddesi(
                    toplanti_id=toplanti.id,
                    baslik=madde['baslik'],
                    aciklama=madde.get('aciklama', ''),
                    sira=i
                )
                db.session.add(gundem_maddesi)
            
            db.session.commit()
        
        flash('Toplantı başarıyla oluşturuldu', 'success')
        return redirect(url_for('toplanti.detay', id=toplanti.id))
    
    return render_template('toplanti/yeni.html', form=form)

@toplanti_bp.route('/<int:id>')
@login_required
def detay(id):
    """Toplantı detay sayfası."""
    toplanti = Toplanti.query.get_or_404(id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        katilimci = Katilimci.query.filter_by(
            toplanti_id=toplanti.id, 
            kullanici_id=current_user.id
        ).first()
        
        if not katilimci:
            abort(403)
    
    katilimcilar = get_toplanti_katilimcilar(toplanti.id)
    gundem_maddeleri = get_toplanti_gundem_maddeleri(toplanti.id)
    notlar = Not.query.filter_by(toplanti_id=toplanti.id).all()
    dosyalar = Dosya.query.filter_by(toplanti_id=toplanti.id).all()
    
    return render_template('toplanti/detay.html',
                          toplanti=toplanti,
                          katilimcilar=katilimcilar,
                          gundem_maddeleri=gundem_maddeleri,
                          notlar=notlar,
                          dosyalar=dosyalar)

@toplanti_bp.route('/<int:id>/duzenle', methods=['GET', 'POST'])
@login_required
def duzenle(id):
    """Toplantı düzenleme sayfası."""
    toplanti = Toplanti.query.get_or_404(id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        abort(403)
    
    form = ToplantiForm(obj=toplanti)
    if form.validate_on_submit():
        toplanti.baslik = form.baslik.data
        toplanti.aciklama = form.aciklama.data
        toplanti.baslangic_zamani = form.baslangic_zamani.data
        toplanti.bitis_zamani = form.bitis_zamani.data
        toplanti.konum = form.konum.data
        toplanti.sanal_toplanti_linki = form.sanal_toplanti_linki.data
        toplanti.tekrar_sikligi = form.tekrar_sikligi.data
        toplanti.tekrar_bitis_tarihi = form.tekrar_bitis_tarihi.data
        
        db.session.commit()
        
        flash('Toplantı başarıyla güncellendi', 'success')
        return redirect(url_for('toplanti.detay', id=toplanti.id))
    
    return render_template('toplanti/duzenle.html', form=form, toplanti=toplanti)

@toplanti_bp.route('/<int:id>/iptal', methods=['POST'])
@login_required
def iptal(id):
    """Toplantı iptal etme işlemi."""
    toplanti = Toplanti.query.get_or_404(id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        abort(403)
    
    toplanti.iptal_edildi = True
    toplanti.iptal_edilen_tarih = datetime.utcnow()
    db.session.commit()
    
    flash('Toplantı başarıyla iptal edildi', 'success')
    return redirect(url_for('toplanti.liste'))

@toplanti_bp.route('/<int:id>/gundem/yeni', methods=['GET', 'POST'])
@login_required
def gundem_ekle(id):
    """Gündem maddesi ekleme sayfası."""
    toplanti = Toplanti.query.get_or_404(id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        abort(403)
    
    form = GundemMaddesiForm()
    if form.validate_on_submit():
        # Sıra numarasını belirle
        son_sira = db.session.query(db.func.max(GundemMaddesi.sira)).filter_by(toplanti_id=id).scalar()
        sira = 0 if son_sira is None else son_sira + 1
        
        gundem_maddesi = GundemMaddesi(
            toplanti_id=id,
            baslik=form.baslik.data,
            aciklama=form.aciklama.data,
            sira=sira,
            hedef=form.hedef.data
        )
        
        db.session.add(gundem_maddesi)
        db.session.commit()
        
        flash('Gündem maddesi başarıyla eklendi', 'success')
        return redirect(url_for('toplanti.detay', id=id))
    
    return render_template('toplanti/gundem_ekle.html', form=form, toplanti=toplanti)

@toplanti_bp.route('/<int:toplanti_id>/gundem/<int:gundem_id>/duzenle', methods=['GET', 'POST'])
@login_required
def gundem_duzenle(toplanti_id, gundem_id):
    """Gündem maddesi düzenleme sayfası."""
    toplanti = Toplanti.query.get_or_404(toplanti_id)
    gundem_maddesi = GundemMaddesi.query.get_or_404(gundem_id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        abort(403)
    
    form = GundemMaddesiForm(obj=gundem_maddesi)
    if form.validate_on_submit():
        gundem_maddesi.baslik = form.baslik.data
        gundem_maddesi.aciklama = form.aciklama.data
        gundem_maddesi.hedef = form.hedef.data
        
        db.session.commit()
        
        flash('Gündem maddesi başarıyla güncellendi', 'success')
        return redirect(url_for('toplanti.detay', id=toplanti_id))
    
    return render_template('toplanti/gundem_duzenle.html', form=form, toplanti=toplanti, gundem_maddesi=gundem_maddesi)

@toplanti_bp.route('/<int:toplanti_id>/gundem/<int:gundem_id>/sil', methods=['POST'])
@login_required
def gundem_sil(toplanti_id, gundem_id):
    """Gündem maddesi silme işlemi."""
    toplanti = Toplanti.query.get_or_404(toplanti_id)
    gundem_maddesi = GundemMaddesi.query.get_or_404(gundem_id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        abort(403)
    
    db.session.delete(gundem_maddesi)
    db.session.commit()
    
    flash('Gündem maddesi başarıyla silindi', 'success')
    return redirect(url_for('toplanti.detay', id=toplanti_id))

@toplanti_bp.route('/<int:id>/ozet')
@login_required
def ozet(id):
    """Toplantı özeti sayfası."""
    toplanti = Toplanti.query.get_or_404(id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        katilimci = Katilimci.query.filter_by(
            toplanti_id=toplanti.id, 
            kullanici_id=current_user.id
        ).first()
        
        if not katilimci:
            abort(403)
    
    # Yapay zeka ile toplantı özetini oluştur
    ozet = toplanti_ozetle(id)
    
    return render_template('toplanti/ozet.html', toplanti=toplanti, ozet=ozet)

# API rotaları
@toplanti_bp.route('/api/toplantilar', methods=['GET'])
@login_required
def api_toplantilar():
    """API toplantı listesi endpoint'i."""
    # Kullanıcının oluşturduğu toplantılar
    olusturulan_toplantilar = Toplanti.query.filter_by(olusturan_kullanici_id=current_user.id).all()
    
    # Kullanıcının katılımcı olduğu toplantılar
    katilimci_toplantilar = db.session.query(Toplanti).join(
        Katilimci, Toplanti.id == Katilimci.toplanti_id
    ).filter(
        Katilimci.kullanici_id == current_user.id
    ).all()
    
    return jsonify({
        'olusturulan_toplantilar': [t.to_dict() for t in olusturulan_toplantilar],
        'katilimci_toplantilar': [t.to_dict() for t in katilimci_toplantilar]
    }), 200

@toplanti_bp.route('/api/toplantilar', methods=['POST'])
@login_required
def api_toplanti_olustur():
    """API toplantı oluşturma endpoint'i."""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Veri bulunamadı', 'success': False}), 400
    
    # Zorunlu alanları kontrol et
    required_fields = ['baslik', 'baslangic_zamani', 'bitis_zamani']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} alanı zorunludur', 'success': False}), 400
    
    # Toplantı oluştur
    toplanti = Toplanti(
        olusturan_kullanici_id=current_user.id,
        baslik=data.get('baslik'),
        aciklama=data.get('aciklama', ''),
        baslangic_zamani=datetime.fromisoformat(data.get('baslangic_zamani')),
        bitis_zamani=datetime.fromisoformat(data.get('bitis_zamani')),
        konum=data.get('konum', ''),
        sanal_toplanti_linki=data.get('sanal_toplanti_linki', ''),
        tekrar_sikligi=data.get('tekrar_sikligi'),
        tekrar_bitis_tarihi=datetime.fromisoformat(data.get('tekrar_bitis_tarihi')) if data.get('tekrar_bitis_tarihi') else None
    )
    
    db.session.add(toplanti)
    db.session.commit()
    
    # Katılımcıları ekle
    if 'katilimcilar' in data and isinstance(data['katilimcilar'], list):
        for kullanici_id in data['katilimcilar']:
            katilimci = Katilimci(
                toplanti_id=toplanti.id,
                kullanici_id=kullanici_id,
                davet_durumu='Bekliyor'
            )
            db.session.add(katilimci)
        
        db.session.commit()
    
    # Misafir katılımcıları ekle
    if 'misafir_katilimcilar' in data and isinstance(data['misafir_katilimcilar'], list):
        for misafir_data in data['misafir_katilimcilar']:
            if isinstance(misafir_data, dict) and 'eposta' in misafir_data:
                misafir = MisafirKatilimci(
                    toplanti_id=toplanti.id,
                    eposta=misafir_data['eposta'],
                    ad=misafir_data.get('ad', '')
                )
                db.session.add(misafir)
        
        db.session.commit()
    
    # Yapay zeka ile gündem maddeleri oluştur
    if data.get('ai_gundem_olustur'):
        gundem_maddeleri = gundem_maddeleri_olustur(toplanti.baslik, toplanti.aciklama)
        for i, madde in enumerate(gundem_maddeleri):
            gundem_maddesi = GundemMaddesi(
                toplanti_id=toplanti.id,
                baslik=madde['baslik'],
                aciklama=madde.get('aciklama', ''),
                sira=i
            )
            db.session.add(gundem_maddesi)
        
        db.session.commit()
    
    return jsonify({
        'message': 'Toplantı başarıyla oluşturuldu',
        'success': True,
        'toplanti': toplanti.to_dict()
    }), 201

@toplanti_bp.route('/api/toplantilar/<int:id>', methods=['GET'])
@login_required
def api_toplanti_detay(id):
    """API toplantı detay endpoint'i."""
    toplanti = Toplanti.query.get_or_404(id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        katilimci = Katilimci.query.filter_by(
            toplanti_id=toplanti.id, 
            kullanici_id=current_user.id
        ).first()
        
        if not katilimci:
            return jsonify({'message': 'Bu toplantıya erişim izniniz yok', 'success': False}), 403
    
    katilimcilar = get_toplanti_katilimcilar(toplanti.id)
    gundem_maddeleri = get_toplanti_gundem_maddeleri(toplanti.id)
    notlar = Not.query.filter_by(toplanti_id=toplanti.id).all()
    dosyalar = Dosya.query.filter_by(toplanti_id=toplanti.id).all()
    
    return jsonify({
        'toplanti': toplanti.to_dict(),
        'katilimcilar': katilimcilar,
        'gundem_maddeleri': [g.to_dict() for g in gundem_maddeleri],
        'notlar': [n.to_dict() for n in notlar],
        'dosyalar': [d.to_dict() for d in dosyalar]
    }), 200

@toplanti_bp.route('/api/toplantilar/<int:id>', methods=['PUT'])
@login_required
def api_toplanti_guncelle(id):
    """API toplantı güncelleme endpoint'i."""
    toplanti = Toplanti.query.get_or_404(id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        return jsonify({'message': 'Bu toplantıyı güncelleme izniniz yok', 'success': False}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Veri bulunamadı', 'success': False}), 400
    
    # Toplantıyı güncelle
    if 'baslik' in data:
        toplanti.baslik = data['baslik']
    if 'aciklama' in data:
        toplanti.aciklama = data['aciklama']
    if 'baslangic_zamani' in data:
        toplanti.baslangic_zamani = datetime.fromisoformat(data['baslangic_zamani'])
    if 'bitis_zamani' in data:
        toplanti.bitis_zamani = datetime.fromisoformat(data['bitis_zamani'])
    if 'konum' in data:
        toplanti.konum = data['konum']
    if 'sanal_toplanti_linki' in data:
        toplanti.sanal_toplanti_linki = data['sanal_toplanti_linki']
    if 'tekrar_sikligi' in data:
        toplanti.tekrar_sikligi = data['tekrar_sikligi']
    if 'tekrar_bitis_tarihi' in data:
        toplanti.tekrar_bitis_tarihi = datetime.fromisoformat(data['tekrar_bitis_tarihi']) if data['tekrar_bitis_tarihi'] else None
    
    db.session.commit()
    
    return jsonify({
        'message': 'Toplantı başarıyla güncellendi',
        'success': True,
        'toplanti': toplanti.to_dict()
    }), 200

@toplanti_bp.route('/api/toplantilar/<int:id>/iptal', methods=['PUT'])
@login_required
def api_toplanti_iptal(id):
    """API toplantı iptal endpoint'i."""
    toplanti = Toplanti.query.get_or_404(id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        return jsonify({'message': 'Bu toplantıyı iptal etme izniniz yok', 'success': False}), 403
    
    toplanti.iptal_edildi = True
    toplanti.iptal_edilen_tarih = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Toplantı başarıyla iptal edildi',
        'success': True
    }), 200

@toplanti_bp.route('/api/toplantilar/<int:id>/ozet', methods=['GET'])
@login_required
def api_toplanti_ozet(id):
    """API toplantı özeti endpoint'i."""
    toplanti = Toplanti.query.get_or_404(id)
    
    # Erişim kontrolü
    if toplanti.olusturan_kullanici_id != current_user.id:
        katilimci = Katilimci.query.filter_by(
            toplanti_id=toplanti.id, 
            kullanici_id=current_user.id
        ).first()
        
        if not katilimci:
            return jsonify({'message': 'Bu toplantıya erişim izniniz yok', 'success': False}), 403
    
    # Yapay zeka ile toplantı özetini oluştur
    ozet = toplanti_ozetle(id)
    
    return jsonify({
        'toplanti': toplanti.to_dict(),
        'ozet': ozet
    }), 200
