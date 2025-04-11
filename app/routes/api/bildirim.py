from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.bildirim import Bildirim
from app.models.kullanici import Kullanici
from app.extensions import db
from datetime import datetime

api_bildirim_bp = Blueprint('api_bildirim', __name__)

@api_bildirim_bp.route('/bildirimler', methods=['GET'])
@jwt_required()
def get_bildirimler():
    """Kullanıcının bildirimlerini getir"""
    kullanici_id = get_jwt_identity()
    
    # Filtreler
    okundu = request.args.get('okundu')
    limit = request.args.get('limit', default=20, type=int)
    
    # Bildirimleri getir
    query = Bildirim.query.filter_by(kullanici_id=kullanici_id)
    
    # Okundu durumuna göre filtrele
    if okundu is not None:
        okundu_bool = okundu.lower() == 'true'
        query = query.filter_by(okundu=okundu_bool)
    
    # Tarihe göre sırala ve limitle
    bildirimler = query.order_by(Bildirim.olusturulma_zamani.desc()).limit(limit).all()
    
    return jsonify([b.to_dict() for b in bildirimler]), 200

@api_bildirim_bp.route('/bildirimler/okunmamis-sayisi', methods=['GET'])
@jwt_required()
def get_okunmamis_bildirim_sayisi():
    """Okunmamış bildirim sayısını getir"""
    kullanici_id = get_jwt_identity()
    
    # Okunmamış bildirim sayısını hesapla
    okunmamis_sayisi = Bildirim.query.filter_by(kullanici_id=kullanici_id, okundu=False).count()
    
    return jsonify({"okunmamis_sayisi": okunmamis_sayisi}), 200

@api_bildirim_bp.route('/bildirimler/<int:bildirim_id>/okundu', methods=['PUT'])
@jwt_required()
def mark_bildirim_okundu(bildirim_id):
    """Bildirimi okundu olarak işaretle"""
    kullanici_id = get_jwt_identity()
    bildirim = Bildirim.query.get_or_404(bildirim_id)
    
    # Sadece kendi bildirimlerini işaretleyebilir
    if bildirim.kullanici_id != kullanici_id:
        return jsonify({"msg": "Bu bildirimi işaretleme yetkiniz yok"}), 403
    
    # Bildirimi okundu olarak işaretle
    bildirim.okundu = True
    bildirim.okunma_zamani = datetime.utcnow()
    db.session.commit()
    
    return jsonify({"msg": "Bildirim okundu olarak işaretlendi"}), 200

@api_bildirim_bp.route('/bildirimler/tumunu-okundu-isaretle', methods=['PUT'])
@jwt_required()
def mark_all_bildirimler_okundu():
    """Tüm bildirimleri okundu olarak işaretle"""
    kullanici_id = get_jwt_identity()
    
    # Okunmamış bildirimleri bul
    okunmamis_bildirimler = Bildirim.query.filter_by(kullanici_id=kullanici_id, okundu=False).all()
    
    # Hepsini okundu olarak işaretle
    for bildirim in okunmamis_bildirimler:
        bildirim.okundu = True
        bildirim.okunma_zamani = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({"msg": "Tüm bildirimler okundu olarak işaretlendi", "islem_sayisi": len(okunmamis_bildirimler)}), 200

@api_bildirim_bp.route('/bildirimler/<int:bildirim_id>', methods=['DELETE'])
@jwt_required()
def delete_bildirim(bildirim_id):
    """Bildirimi sil"""
    kullanici_id = get_jwt_identity()
    bildirim = Bildirim.query.get_or_404(bildirim_id)
    
    # Sadece kendi bildirimlerini silebilir
    if bildirim.kullanici_id != kullanici_id:
        return jsonify({"msg": "Bu bildirimi silme yetkiniz yok"}), 403
    
    # Bildirimi sil
    db.session.delete(bildirim)
    db.session.commit()
    
    return jsonify({"msg": "Bildirim başarıyla silindi"}), 200

@api_bildirim_bp.route('/bildirimler/ayarlar', methods=['GET'])
@jwt_required()
def get_bildirim_ayarlar():
    """Bildirim ayarlarını getir"""
    kullanici_id = get_jwt_identity()
    
    # Bildirim ayarlarını getir
    from app.models.bildirim import BildirimAyarlari
    
    ayarlar = BildirimAyarlari.query.filter_by(kullanici_id=kullanici_id).first()
    if not ayarlar:
        # Varsayılan ayarlarla yeni bir kayıt oluştur
        ayarlar = BildirimAyarlari(kullanici_id=kullanici_id)
        db.session.add(ayarlar)
        db.session.commit()
    
    return jsonify(ayarlar.to_dict()), 200

@api_bildirim_bp.route('/bildirimler/ayarlar', methods=['PUT'])
@jwt_required()
def update_bildirim_ayarlar():
    """Bildirim ayarlarını güncelle"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    kullanici_id = get_jwt_identity()
    data = request.get_json()
    
    # Bildirim ayarlarını getir
    from app.models.bildirim import BildirimAyarlari
    
    ayarlar = BildirimAyarlari.query.filter_by(kullanici_id=kullanici_id).first()
    if not ayarlar:
        # Varsayılan ayarlarla yeni bir kayıt oluştur
        ayarlar = BildirimAyarlari(kullanici_id=kullanici_id)
        db.session.add(ayarlar)
    
    # Güncellenebilir alanlar
    if 'toplanti_davet' in data:
        ayarlar.toplanti_davet = data['toplanti_davet']
    if 'toplanti_guncelleme' in data:
        ayarlar.toplanti_guncelleme = data['toplanti_guncelleme']
    if 'toplanti_iptal' in data:
        ayarlar.toplanti_iptal = data['toplanti_iptal']
    if 'toplanti_hatirlatma' in data:
        ayarlar.toplanti_hatirlatma = data['toplanti_hatirlatma']
    if 'gorev_atama' in data:
        ayarlar.gorev_atama = data['gorev_atama']
    if 'gorev_guncelleme' in data:
        ayarlar.gorev_guncelleme = data['gorev_guncelleme']
    if 'gorev_tamamlama' in data:
        ayarlar.gorev_tamamlama = data['gorev_tamamlama']
    if 'gorev_hatirlatma' in data:
        ayarlar.gorev_hatirlatma = data['gorev_hatirlatma']
    if 'yorum_ekleme' in data:
        ayarlar.yorum_ekleme = data['yorum_ekleme']
    if 'eposta_bildirim' in data:
        ayarlar.eposta_bildirim = data['eposta_bildirim']
    
    db.session.commit()
    
    return jsonify({"msg": "Bildirim ayarları başarıyla güncellendi", "ayarlar": ayarlar.to_dict()}), 200
