from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.gorev import Gorev
from app.models.kullanici import Kullanici
from app.models.toplanti import Toplanti
from app.models.urun import Urun
from app.models.gorev_yorum import GorevYorum
from app.extensions import db
from datetime import datetime

api_gorev_bp = Blueprint('api_gorev', __name__)

@api_gorev_bp.route('/gorevler', methods=['GET'])
@jwt_required()
def get_gorevler():
    """Kullanıcının görevlerini getir"""
    kullanici_id = get_jwt_identity()
    
    # Filtreler
    durum = request.args.get('durum')
    oncelik = request.args.get('oncelik')
    toplanti_id = request.args.get('toplanti_id')
    
    # Atanan görevler
    query = Gorev.query.filter_by(atanan_kullanici_id=kullanici_id)
    
    # Filtreleri uygula
    if durum:
        query = query.filter_by(durum=durum)
    if oncelik:
        query = query.filter_by(oncelik=oncelik)
    if toplanti_id:
        query = query.filter_by(toplanti_id=toplanti_id)
    
    # Görevleri tarihe göre sırala
    gorevler = query.order_by(Gorev.son_teslim_tarihi).all()
    
    return jsonify([g.to_dict() for g in gorevler]), 200

@api_gorev_bp.route('/gorevler/olusturulan', methods=['GET'])
@jwt_required()
def get_olusturulan_gorevler():
    """Kullanıcının oluşturduğu görevleri getir"""
    kullanici_id = get_jwt_identity()
    
    # Filtreler
    durum = request.args.get('durum')
    oncelik = request.args.get('oncelik')
    toplanti_id = request.args.get('toplanti_id')
    
    # Oluşturulan görevler
    query = Gorev.query.filter_by(olusturan_kullanici_id=kullanici_id)
    
    # Filtreleri uygula
    if durum:
        query = query.filter_by(durum=durum)
    if oncelik:
        query = query.filter_by(oncelik=oncelik)
    if toplanti_id:
        query = query.filter_by(toplanti_id=toplanti_id)
    
    # Görevleri tarihe göre sırala
    gorevler = query.order_by(Gorev.son_teslim_tarihi).all()
    
    return jsonify([g.to_dict() for g in gorevler]), 200

@api_gorev_bp.route('/gorevler/<int:gorev_id>', methods=['GET'])
@jwt_required()
def get_gorev(gorev_id):
    """Belirli bir görevin detaylarını getir"""
    kullanici_id = get_jwt_identity()
    
    gorev = Gorev.query.get_or_404(gorev_id)
    
    # Kullanıcının bu göreve erişim yetkisi var mı kontrol et
    if gorev.olusturan_kullanici_id != kullanici_id and gorev.atanan_kullanici_id != kullanici_id:
        return jsonify({"msg": "Bu göreve erişim yetkiniz yok"}), 403
    
    # Görev detaylarını getir
    gorev_dict = gorev.to_dict(include_related=True)
    
    return jsonify(gorev_dict), 200

@api_gorev_bp.route('/gorevler', methods=['POST'])
@jwt_required()
def create_gorev():
    """Yeni görev oluştur"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    kullanici_id = get_jwt_identity()
    data = request.get_json()
    
    # Zorunlu alanları kontrol et
    required_fields = ['baslik', 'atanan_kullanici_id', 'son_teslim_tarihi', 'oncelik', 'durum']
    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"{field} alanı gerekli"}), 400
    
    # Atanan kullanıcı kontrolü
    atanan_kullanici = Kullanici.query.get(data['atanan_kullanici_id'])
    if not atanan_kullanici:
        return jsonify({"msg": "Atanan kullanıcı bulunamadı"}), 404
    
    # Toplantı kontrolü (opsiyonel)
    toplanti_id = data.get('toplanti_id')
    if toplanti_id:
        toplanti = Toplanti.query.get(toplanti_id)
        if not toplanti:
            return jsonify({"msg": "Toplantı bulunamadı"}), 404
    
    # Ürün kontrolü (opsiyonel)
    urun_id = data.get('urun_id')
    if urun_id:
        urun = Urun.query.get(urun_id)
        if not urun:
            return jsonify({"msg": "Ürün bulunamadı"}), 404
    
    # Son teslim tarihini kontrol et
    try:
        son_teslim_tarihi = datetime.fromisoformat(data['son_teslim_tarihi'])
    except ValueError:
        return jsonify({"msg": "Geçersiz tarih formatı. ISO 8601 formatı kullanın (YYYY-MM-DD)"}), 400
    
    # Yeni görev oluştur
    yeni_gorev = Gorev(
        baslik=data['baslik'],
        aciklama=data.get('aciklama', ''),
        atanan_kullanici_id=data['atanan_kullanici_id'],
        olusturan_kullanici_id=kullanici_id,
        son_teslim_tarihi=son_teslim_tarihi,
        oncelik=data['oncelik'],
        durum=data['durum'],
        puan_degeri=data.get('puan_degeri', 0),
        toplanti_id=toplanti_id,
        urun_id=urun_id,
        olusturulma_zamani=datetime.utcnow(),
        guncelleme_zamani=datetime.utcnow()
    )
    
    db.session.add(yeni_gorev)
    db.session.commit()
    
    return jsonify({"msg": "Görev başarıyla oluşturuldu", "gorev_id": yeni_gorev.id}), 201

@api_gorev_bp.route('/gorevler/<int:gorev_id>', methods=['PUT'])
@jwt_required()
def update_gorev(gorev_id):
    """Görev bilgilerini güncelle"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    kullanici_id = get_jwt_identity()
    gorev = Gorev.query.get_or_404(gorev_id)
    
    # Sadece görevi oluşturan kişi veya atanan kişi güncelleyebilir
    if gorev.olusturan_kullanici_id != kullanici_id and gorev.atanan_kullanici_id != kullanici_id:
        return jsonify({"msg": "Bu görevi güncelleme yetkiniz yok"}), 403
    
    data = request.get_json()
    
    # Atanan kullanıcı değişiyorsa kontrol et
    if 'atanan_kullanici_id' in data and data['atanan_kullanici_id'] != gorev.atanan_kullanici_id:
        # Sadece görevi oluşturan kişi atanan kişiyi değiştirebilir
        if gorev.olusturan_kullanici_id != kullanici_id:
            return jsonify({"msg": "Atanan kişiyi değiştirme yetkiniz yok"}), 403
        
        atanan_kullanici = Kullanici.query.get(data['atanan_kullanici_id'])
        if not atanan_kullanici:
            return jsonify({"msg": "Atanan kullanıcı bulunamadı"}), 404
    
    # Güncellenebilir alanlar
    if 'baslik' in data:
        gorev.baslik = data['baslik']
    if 'aciklama' in data:
        gorev.aciklama = data['aciklama']
    if 'atanan_kullanici_id' in data and gorev.olusturan_kullanici_id == kullanici_id:
        gorev.atanan_kullanici_id = data['atanan_kullanici_id']
    if 'son_teslim_tarihi' in data:
        try:
            gorev.son_teslim_tarihi = datetime.fromisoformat(data['son_teslim_tarihi'])
        except ValueError:
            return jsonify({"msg": "Geçersiz tarih formatı"}), 400
    if 'oncelik' in data:
        gorev.oncelik = data['oncelik']
    if 'durum' in data:
        gorev.durum = data['durum']
    if 'puan_degeri' in data and gorev.olusturan_kullanici_id == kullanici_id:
        gorev.puan_degeri = data['puan_degeri']
    
    gorev.guncelleme_zamani = datetime.utcnow()
    db.session.commit()
    
    return jsonify({"msg": "Görev başarıyla güncellendi", "gorev": gorev.to_dict()}), 200

@api_gorev_bp.route('/gorevler/<int:gorev_id>/durum', methods=['PUT'])
@jwt_required()
def update_gorev_durum(gorev_id):
    """Görev durumunu güncelle"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    kullanici_id = get_jwt_identity()
    gorev = Gorev.query.get_or_404(gorev_id)
    
    # Sadece görevi oluşturan kişi veya atanan kişi durumu güncelleyebilir
    if gorev.olusturan_kullanici_id != kullanici_id and gorev.atanan_kullanici_id != kullanici_id:
        return jsonify({"msg": "Bu görevin durumunu güncelleme yetkiniz yok"}), 403
    
    data = request.get_json()
    
    if 'durum' not in data:
        return jsonify({"msg": "durum alanı gerekli"}), 400
    
    # Geçerli durumlar
    gecerli_durumlar = ['Yapılacak', 'Devam Ediyor', 'Tamamlandı']
    if data['durum'] not in gecerli_durumlar:
        return jsonify({"msg": f"Geçersiz durum. Geçerli değerler: {', '.join(gecerli_durumlar)}"}), 400
    
    # Durumu güncelle
    gorev.durum = data['durum']
    gorev.guncelleme_zamani = datetime.utcnow()
    
    # Eğer durum "Tamamlandı" ise tamamlanma tarihini güncelle
    if data['durum'] == 'Tamamlandı':
        gorev.tamamlanma_zamani = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({"msg": "Görev durumu başarıyla güncellendi"}), 200

@api_gorev_bp.route('/gorevler/<int:gorev_id>/yorumlar', methods=['GET'])
@jwt_required()
def get_gorev_yorumlar(gorev_id):
    """Göreve ait yorumları getir"""
    kullanici_id = get_jwt_identity()
    gorev = Gorev.query.get_or_404(gorev_id)
    
    # Kullanıcının bu göreve erişim yetkisi var mı kontrol et
    if gorev.olusturan_kullanici_id != kullanici_id and gorev.atanan_kullanici_id != kullanici_id:
        return jsonify({"msg": "Bu göreve erişim yetkiniz yok"}), 403
    
    # Yorumları getir
    yorumlar = GorevYorum.query.filter_by(gorev_id=gorev_id).order_by(GorevYorum.olusturulma_zamani).all()
    
    return jsonify([y.to_dict() for y in yorumlar]), 200

@api_gorev_bp.route('/gorevler/<int:gorev_id>/yorumlar', methods=['POST'])
@jwt_required()
def add_gorev_yorum(gorev_id):
    """Göreve yorum ekle"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    kullanici_id = get_jwt_identity()
    gorev = Gorev.query.get_or_404(gorev_id)
    
    # Kullanıcının bu göreve erişim yetkisi var mı kontrol et
    if gorev.olusturan_kullanici_id != kullanici_id and gorev.atanan_kullanici_id != kullanici_id:
        return jsonify({"msg": "Bu göreve yorum ekleme yetkiniz yok"}), 403
    
    data = request.get_json()
    
    if 'yorum' not in data:
        return jsonify({"msg": "yorum alanı gerekli"}), 400
    
    # Yeni yorum ekle
    yeni_yorum = GorevYorum(
        gorev_id=gorev_id,
        kullanici_id=kullanici_id,
        yorum=data['yorum'],
        olusturulma_zamani=datetime.utcnow()
    )
    db.session.add(yeni_yorum)
    db.session.commit()
    
    return jsonify({"msg": "Yorum başarıyla eklendi", "yorum_id": yeni_yorum.id}), 201
