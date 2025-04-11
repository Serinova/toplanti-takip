from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.toplanti import Toplanti
from app.models.gundem import Gundem
from app.models.katilimci import Katilimci
from app.models.not_dosya import Not, Dosya
from app.models.kullanici import Kullanici
from app.extensions import db
from datetime import datetime

api_toplanti_bp = Blueprint('api_toplanti', __name__)

@api_toplanti_bp.route('/toplantilar', methods=['GET'])
@jwt_required()
def get_toplantilar():
    """Kullanıcının toplantılarını getir"""
    kullanici_id = get_jwt_identity()
    
    # Oluşturduğu toplantılar
    olusturulan = Toplanti.query.filter_by(olusturan_kullanici_id=kullanici_id).all()
    
    # Katılımcı olduğu toplantılar
    katilimci_olduklari_ids = db.session.query(Katilimci.toplanti_id).filter_by(kullanici_id=kullanici_id).all()
    katilimci_olduklari_ids = [id[0] for id in katilimci_olduklari_ids]
    
    katilimci_olduklari = Toplanti.query.filter(Toplanti.id.in_(katilimci_olduklari_ids)).all()
    
    # Tüm toplantıları birleştir
    tum_toplantilar = olusturulan + katilimci_olduklari
    
    # Tekrarlanan toplantıları kaldır
    unique_toplantilar = []
    toplanti_ids = set()
    for toplanti in tum_toplantilar:
        if toplanti.id not in toplanti_ids:
            toplanti_ids.add(toplanti.id)
            unique_toplantilar.append(toplanti)
    
    # Toplantıları tarihe göre sırala
    unique_toplantilar.sort(key=lambda x: x.baslangic_zamani, reverse=True)
    
    return jsonify([t.to_dict() for t in unique_toplantilar]), 200

@api_toplanti_bp.route('/toplantilar/<int:toplanti_id>', methods=['GET'])
@jwt_required()
def get_toplanti(toplanti_id):
    """Belirli bir toplantının detaylarını getir"""
    kullanici_id = get_jwt_identity()
    
    toplanti = Toplanti.query.get_or_404(toplanti_id)
    
    # Kullanıcının bu toplantıya erişim yetkisi var mı kontrol et
    if toplanti.olusturan_kullanici_id != kullanici_id:
        katilimci = Katilimci.query.filter_by(toplanti_id=toplanti_id, kullanici_id=kullanici_id).first()
        if not katilimci:
            return jsonify({"msg": "Bu toplantıya erişim yetkiniz yok"}), 403
    
    # Toplantı detaylarını getir
    toplanti_dict = toplanti.to_dict(include_related=True)
    
    return jsonify(toplanti_dict), 200

@api_toplanti_bp.route('/toplantilar', methods=['POST'])
@jwt_required()
def create_toplanti():
    """Yeni toplantı oluştur"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    kullanici_id = get_jwt_identity()
    data = request.get_json()
    
    # Zorunlu alanları kontrol et
    required_fields = ['baslik', 'baslangic_zamani', 'bitis_zamani']
    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"{field} alanı gerekli"}), 400
    
    # Başlangıç ve bitiş zamanlarını kontrol et
    try:
        baslangic_zamani = datetime.fromisoformat(data['baslangic_zamani'])
        bitis_zamani = datetime.fromisoformat(data['bitis_zamani'])
    except ValueError:
        return jsonify({"msg": "Geçersiz tarih formatı. ISO 8601 formatı kullanın (YYYY-MM-DDTHH:MM:SS)"}), 400
    
    if bitis_zamani <= baslangic_zamani:
        return jsonify({"msg": "Bitiş zamanı başlangıç zamanından sonra olmalıdır"}), 400
    
    # Yeni toplantı oluştur
    yeni_toplanti = Toplanti(
        baslik=data['baslik'],
        aciklama=data.get('aciklama', ''),
        baslangic_zamani=baslangic_zamani,
        bitis_zamani=bitis_zamani,
        konum=data.get('konum', ''),
        sanal_toplanti_linki=data.get('sanal_toplanti_linki', ''),
        tekrar_sikligi=data.get('tekrar_sikligi', ''),
        tekrar_bitis_tarihi=datetime.fromisoformat(data['tekrar_bitis_tarihi']) if 'tekrar_bitis_tarihi' in data and data['tekrar_bitis_tarihi'] else None,
        hatirlatma=data.get('hatirlatma', ''),
        olusturan_kullanici_id=kullanici_id,
        olusturulma_zamani=datetime.utcnow(),
        guncelleme_zamani=datetime.utcnow(),
        iptal_edildi=False
    )
    
    db.session.add(yeni_toplanti)
    db.session.commit()
    
    # Oluşturan kişiyi otomatik olarak katılımcı olarak ekle
    katilimci = Katilimci(
        toplanti_id=yeni_toplanti.id,
        kullanici_id=kullanici_id,
        davet_durumu='Kabul Edildi',
        davet_zamani=datetime.utcnow()
    )
    db.session.add(katilimci)
    
    # Diğer katılımcıları ekle
    if 'katilimcilar' in data and isinstance(data['katilimcilar'], list):
        for k_id in data['katilimcilar']:
            if k_id != kullanici_id:  # Oluşturan kişiyi tekrar ekleme
                kullanici = Kullanici.query.get(k_id)
                if kullanici:
                    katilimci = Katilimci(
                        toplanti_id=yeni_toplanti.id,
                        kullanici_id=k_id,
                        davet_durumu='Bekliyor',
                        davet_zamani=datetime.utcnow()
                    )
                    db.session.add(katilimci)
    
    # Gündem maddelerini ekle
    if 'gundem_maddeleri' in data and isinstance(data['gundem_maddeleri'], list):
        for i, madde in enumerate(data['gundem_maddeleri']):
            gundem = Gundem(
                toplanti_id=yeni_toplanti.id,
                baslik=madde.get('baslik', ''),
                aciklama=madde.get('aciklama', ''),
                hedef=madde.get('hedef', ''),
                sure=madde.get('sure', 0),
                sira=i + 1
            )
            db.session.add(gundem)
    
    db.session.commit()
    
    return jsonify({"msg": "Toplantı başarıyla oluşturuldu", "toplanti_id": yeni_toplanti.id}), 201

@api_toplanti_bp.route('/toplantilar/<int:toplanti_id>', methods=['PUT'])
@jwt_required()
def update_toplanti(toplanti_id):
    """Toplantı bilgilerini güncelle"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    kullanici_id = get_jwt_identity()
    toplanti = Toplanti.query.get_or_404(toplanti_id)
    
    # Sadece toplantıyı oluşturan kişi güncelleyebilir
    if toplanti.olusturan_kullanici_id != kullanici_id:
        return jsonify({"msg": "Bu toplantıyı güncelleme yetkiniz yok"}), 403
    
    data = request.get_json()
    
    # Güncellenebilir alanlar
    if 'baslik' in data:
        toplanti.baslik = data['baslik']
    if 'aciklama' in data:
        toplanti.aciklama = data['aciklama']
    if 'baslangic_zamani' in data:
        try:
            toplanti.baslangic_zamani = datetime.fromisoformat(data['baslangic_zamani'])
        except ValueError:
            return jsonify({"msg": "Geçersiz başlangıç zamanı formatı"}), 400
    if 'bitis_zamani' in data:
        try:
            toplanti.bitis_zamani = datetime.fromisoformat(data['bitis_zamani'])
        except ValueError:
            return jsonify({"msg": "Geçersiz bitiş zamanı formatı"}), 400
    if 'konum' in data:
        toplanti.konum = data['konum']
    if 'sanal_toplanti_linki' in data:
        toplanti.sanal_toplanti_linki = data['sanal_toplanti_linki']
    if 'tekrar_sikligi' in data:
        toplanti.tekrar_sikligi = data['tekrar_sikligi']
    if 'tekrar_bitis_tarihi' in data and data['tekrar_bitis_tarihi']:
        try:
            toplanti.tekrar_bitis_tarihi = datetime.fromisoformat(data['tekrar_bitis_tarihi'])
        except ValueError:
            return jsonify({"msg": "Geçersiz tekrar bitiş tarihi formatı"}), 400
    if 'hatirlatma' in data:
        toplanti.hatirlatma = data['hatirlatma']
    if 'iptal_edildi' in data:
        toplanti.iptal_edildi = data['iptal_edildi']
    
    toplanti.guncelleme_zamani = datetime.utcnow()
    db.session.commit()
    
    return jsonify({"msg": "Toplantı başarıyla güncellendi", "toplanti": toplanti.to_dict()}), 200

@api_toplanti_bp.route('/toplantilar/<int:toplanti_id>/katilimcilar', methods=['POST'])
@jwt_required()
def add_katilimci(toplanti_id):
    """Toplantıya katılımcı ekle"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    kullanici_id = get_jwt_identity()
    toplanti = Toplanti.query.get_or_404(toplanti_id)
    
    # Sadece toplantıyı oluşturan kişi katılımcı ekleyebilir
    if toplanti.olusturan_kullanici_id != kullanici_id:
        return jsonify({"msg": "Bu toplantıya katılımcı ekleme yetkiniz yok"}), 403
    
    data = request.get_json()
    
    if 'kullanici_id' not in data:
        return jsonify({"msg": "kullanici_id alanı gerekli"}), 400
    
    # Kullanıcı kontrolü
    yeni_katilimci = Kullanici.query.get(data['kullanici_id'])
    if not yeni_katilimci:
        return jsonify({"msg": "Kullanıcı bulunamadı"}), 404
    
    # Zaten katılımcı mı kontrol et
    existing = Katilimci.query.filter_by(toplanti_id=toplanti_id, kullanici_id=data['kullanici_id']).first()
    if existing:
        return jsonify({"msg": "Bu kullanıcı zaten toplantıya davet edilmiş"}), 409
    
    # Yeni katılımcı ekle
    katilimci = Katilimci(
        toplanti_id=toplanti_id,
        kullanici_id=data['kullanici_id'],
        davet_durumu='Bekliyor',
        davet_zamani=datetime.utcnow()
    )
    db.session.add(katilimci)
    db.session.commit()
    
    return jsonify({"msg": "Katılımcı başarıyla eklendi"}), 201

@api_toplanti_bp.route('/toplantilar/<int:toplanti_id>/katilimcilar/<int:kullanici_id>', methods=['DELETE'])
@jwt_required()
def remove_katilimci(toplanti_id, kullanici_id):
    """Toplantıdan katılımcı çıkar"""
    current_user_id = get_jwt_identity()
    toplanti = Toplanti.query.get_or_404(toplanti_id)
    
    # Sadece toplantıyı oluşturan kişi katılımcı çıkarabilir
    if toplanti.olusturan_kullanici_id != current_user_id:
        return jsonify({"msg": "Bu toplantıdan katılımcı çıkarma yetkiniz yok"}), 403
    
    # Katılımcıyı bul
    katilimci = Katilimci.query.filter_by(toplanti_id=toplanti_id, kullanici_id=kullanici_id).first()
    if not katilimci:
        return jsonify({"msg": "Katılımcı bulunamadı"}), 404
    
    # Katılımcıyı sil
    db.session.delete(katilimci)
    db.session.commit()
    
    return jsonify({"msg": "Katılımcı başarıyla çıkarıldı"}), 200

@api_toplanti_bp.route('/toplantilar/<int:toplanti_id>/davet-durumu', methods=['PUT'])
@jwt_required()
def update_davet_durumu(toplanti_id):
    """Davet durumunu güncelle"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    kullanici_id = get_jwt_identity()
    data = request.get_json()
    
    if 'durum' not in data:
        return jsonify({"msg": "durum alanı gerekli"}), 400
    
    # Geçerli durumlar
    gecerli_durumlar = ['Kabul Edildi', 'Reddedildi', 'Bekliyor']
    if data['durum'] not in gecerli_durumlar:
        return jsonify({"msg": f"Geçersiz durum. Geçerli değerler: {', '.join(gecerli_durumlar)}"}), 400
    
    # Katılımcıyı bul
    katilimci = Katilimci.query.filter_by(toplanti_id=toplanti_id, kullanici_id=kullanici_id).first()
    if not katilimci:
        return jsonify({"msg": "Bu toplantı için davet bulunamadı"}), 404
    
    # Durumu güncelle
    katilimci.davet_durumu = data['durum']
    db.session.commit()
    
    return jsonify({"msg": "Davet durumu başarıyla güncellendi"}), 200

@api_toplanti_bp.route('/toplantilar/<int:toplanti_id>/gundem', methods=['GET'])
@jwt_required()
def get_gundem_maddeleri(toplanti_id):
    """Toplantının gündem maddelerini getir"""
    kullanici_id = get_jwt_identity()
    toplanti = Toplanti.query.get_or_404(toplanti_id)
    
    # Kullanıcının bu toplantıya erişim yetkisi var mı kontrol et
    if toplanti.olusturan_kullanici_id != kullanici_id:
        katilimci = Katilimci.query.filter_by(toplanti_id=toplanti_id, kullanici_id=kullanici_id).first()
        if not katilimci:
            return jsonify({"msg": "Bu toplantıya erişim yetkiniz yok"}), 403
    
    # Gündem maddelerini getir
    gundem_maddeleri = Gundem.query.filter_by(toplanti_id=toplanti_id).order_by(Gundem.sira).all()
    
    return jsonify([g.to_dict() for g in gundem_maddeleri]), 200

@api_toplanti_bp.route('/toplantilar/<int:toplanti_id>/gundem', methods=['POST'])
@jwt_required()
def add_gundem_maddesi(toplanti_id):
    """Toplantıya gündem maddesi ekle"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    kullanici_id = get_jwt_identity()
    toplanti = Toplanti.query.get_or_404(toplanti_id)
    
    # Sadece toplantıyı oluşturan kişi gündem maddesi ekleyebilir
    if toplanti.olusturan_kullanici_id != kullanici_id:
        return jsonify({"msg": "Bu toplantıya gündem maddesi ekleme yetkiniz yok"}), 403
    
    data = request.get_json()
    
    if 'baslik' not in data:
        return jsonify({"msg": "baslik alanı gerekli"}), 400
    
    # Son sıra numarasını bul
    son_sira = db.session.query(db.func.max(Gundem.sira)).filter_by(toplanti_id=toplanti_id).scalar() or 0
    
    # Yeni gündem maddesi ekle
    gundem = Gundem(
        toplanti_id=toplanti_id,
        baslik=data['baslik'],
        aciklama=data.get('aciklama', ''),
        hedef=data.get('hedef', ''),
        sure=data.get('sure', 0),
        sira=son_sira + 1
    )
    db.session.add(gundem)
    db.session.commit()
    
    return jsonify({"msg": "Gündem maddesi başarıyla eklendi", "gundem_id": gundem.id}), 201

@api_toplanti_bp.route('/gundem/<int:gundem_id>', methods=['PUT'])
@jwt_required()
def update_gundem_maddesi(gundem_id):
    """Gündem maddesini güncelle"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    kullanici_id = get_jwt_identity()
    gundem = Gundem.query.get_or_404(gundem_id)
    toplanti = Toplanti.query.get(gundem.toplanti_id)
    
    # Sadece toplantıyı oluşturan kişi gündem maddesini güncelleyebilir
    if toplanti.olusturan_kullanici_id != kullanici_id:
        return jsonify({"msg": "Bu gündem maddesini güncelleme yetkiniz yok"}), 403
    
    data = request.get_json()
    
    # Güncellenebilir alanlar
    if 'baslik' in data:
        gundem.baslik = data['baslik']
    if 'aciklama' in data:
        gundem.aciklama = data['aciklama']
    if 'hedef' in data:
        gundem.hedef = data['hedef']
    if 'sure' in data:
        gundem.sure = data['sure']
    if 'sira' in data:
        gundem.sira = data['sira']
    
    db.session.commit()
    
    return jsonify({"msg": "Gündem maddesi başarıyla güncellendi", "gundem": gundem.to_dict()}), 200

@api_toplanti_bp.route('/gundem/<int:gundem_id>', methods=['DELETE'])
@jwt_required()
def delete_gundem_maddesi(gundem_id):
    """Gündem maddesini sil"""
    kullanici_id = get_jwt_identity()
    gundem = Gundem.query.get_or_404(gundem_id)
    toplanti = Toplanti.query.get(gundem.toplanti_id)
    
    # Sadece toplantıyı oluşturan kişi gündem maddesini silebilir
    if toplanti.olusturan_kullanici_id != kullanici_id:
        return jsonify({"msg": "Bu gündem maddesini silme yetkiniz yok"}), 403
    
    db.session.delete(gundem)
    db.session.commit()
    
    return jsonify({"msg": "Gündem maddesi başarıyla silindi"}), 200

@api_toplanti_bp.route('/gundem/<int:gundem_id>/notlar', methods=['GET'])
@jwt_required()
def get_notlar(gundem_id):
    """Gündem maddesine ait notları getir"""
    kullanici_id = get_jwt_identity()
    gundem = Gundem.query.get_or_404(gundem_id)
    toplanti = Toplanti.query.get(gundem.toplanti_id)
    
    # Kullanıcının bu toplantıya erişim yetkisi var mı kontrol et
    if toplanti.olusturan_kullanici_id != kullanici_id:
        katilimci = Katilimci.query.filter_by(toplanti_id=toplanti.id, kullanici_id=kullanici_id).first()
        if not katilimci:
            return jsonify({"msg": "Bu toplantıya erişim yetkiniz yok"}), 403
    
    # Notları getir
    notlar = Not.query.filter_by(gundem_id=gundem_id).order_by(Not.olusturulma_zamani).all()
    
    return jsonify([n.to_dict() for n in notlar]), 200

@api_toplanti_bp.route('/gundem/<int:gundem_id>/notlar', methods=['POST'])
@jwt_required()
def add_not(gundem_id):
    """Gündem maddesine not ekle"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    kullanici_id = get_jwt_identity()
    gundem = Gundem.query.get_or_404(gundem_id)
    toplanti = Toplanti.query.get(gundem.toplanti_id)
    
    # Kullanıcının bu toplantıya erişim yetkisi var mı kontrol et
    if toplanti.olusturan_kullanici_id != kullanici_id:
        katilimci = Katilimci.query.filter_by(toplanti_id=toplanti.id, kullanici_id=kullanici_id).first()
        if not katilimci or katilimci.davet_durumu != 'Kabul Edildi':
            return jsonify({"msg": "Bu toplantıya not ekleme yetkiniz yok"}), 403
    
    data = request.get_json()
    
    if 'icerik' not in data:
        return jsonify({"msg": "icerik alanı gerekli"}), 400
    
    # Yeni not ekle
    yeni_not = Not(
        gundem_id=gundem_id,
        kullanici_id=kullanici_id,
        icerik=data['icerik'],
        olusturulma_zamani=datetime.utcnow()
    )
    db.session.add(yeni_not)
    db.session.commit()
    
    return jsonify({"msg": "Not başarıyla eklendi", "not_id": yeni_not.id}), 201
