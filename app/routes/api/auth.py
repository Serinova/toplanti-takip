from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app.models.kullanici import Kullanici
from app.extensions import db, bcrypt
from datetime import timedelta

api_auth_bp = Blueprint('api_auth', __name__)

@api_auth_bp.route('/login', methods=['POST'])
def login():
    """API giriş uç noktası"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    data = request.get_json()
    eposta = data.get('eposta', None)
    sifre = data.get('sifre', None)
    
    if not eposta or not sifre:
        return jsonify({"msg": "E-posta ve şifre gerekli"}), 400
    
    kullanici = Kullanici.query.filter_by(eposta=eposta).first()
    if not kullanici or not bcrypt.check_password_hash(kullanici.sifre_hash, sifre):
        return jsonify({"msg": "Geçersiz e-posta veya şifre"}), 401
    
    # Kullanıcı giriş tarihini güncelle
    kullanici.son_giris_tarihi = db.func.now()
    db.session.commit()
    
    # JWT token oluştur
    expires = timedelta(days=1)
    access_token = create_access_token(
        identity=kullanici.id, 
        expires_delta=expires,
        additional_claims={"rol": kullanici.rol}
    )
    
    return jsonify({
        "access_token": access_token,
        "kullanici": kullanici.to_dict()
    }), 200

@api_auth_bp.route('/register', methods=['POST'])
def register():
    """API kayıt uç noktası"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    data = request.get_json()
    ad = data.get('ad', None)
    eposta = data.get('eposta', None)
    sifre = data.get('sifre', None)
    
    if not ad or not eposta or not sifre:
        return jsonify({"msg": "Ad, e-posta ve şifre gerekli"}), 400
    
    # E-posta kontrolü
    existing_user = Kullanici.query.filter_by(eposta=eposta).first()
    if existing_user:
        return jsonify({"msg": "Bu e-posta adresi zaten kullanılıyor"}), 409
    
    # Şifre uzunluğu kontrolü
    if len(sifre) < 6:
        return jsonify({"msg": "Şifre en az 6 karakter olmalıdır"}), 400
    
    # Yeni kullanıcı oluştur
    sifre_hash = bcrypt.generate_password_hash(sifre).decode('utf-8')
    yeni_kullanici = Kullanici(
        ad=ad,
        eposta=eposta,
        sifre_hash=sifre_hash,
        rol='kullanici',
        aktif=True,
        kayit_tarihi=db.func.now()
    )
    
    db.session.add(yeni_kullanici)
    db.session.commit()
    
    return jsonify({"msg": "Kullanıcı başarıyla oluşturuldu", "kullanici_id": yeni_kullanici.id}), 201

@api_auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Kullanıcı profil bilgilerini getir"""
    kullanici_id = get_jwt_identity()
    kullanici = Kullanici.query.get(kullanici_id)
    
    if not kullanici:
        return jsonify({"msg": "Kullanıcı bulunamadı"}), 404
    
    return jsonify(kullanici.to_dict()), 200

@api_auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Kullanıcı profil bilgilerini güncelle"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    kullanici_id = get_jwt_identity()
    kullanici = Kullanici.query.get(kullanici_id)
    
    if not kullanici:
        return jsonify({"msg": "Kullanıcı bulunamadı"}), 404
    
    data = request.get_json()
    
    # Güncellenebilir alanlar
    if 'ad' in data:
        kullanici.ad = data['ad']
    if 'telefon' in data:
        kullanici.telefon = data['telefon']
    if 'unvan' in data:
        kullanici.unvan = data['unvan']
    if 'departman' in data:
        kullanici.departman = data['departman']
    
    db.session.commit()
    
    return jsonify({"msg": "Profil başarıyla güncellendi", "kullanici": kullanici.to_dict()}), 200

@api_auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Şifre değiştirme"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    kullanici_id = get_jwt_identity()
    kullanici = Kullanici.query.get(kullanici_id)
    
    if not kullanici:
        return jsonify({"msg": "Kullanıcı bulunamadı"}), 404
    
    data = request.get_json()
    mevcut_sifre = data.get('mevcut_sifre', None)
    yeni_sifre = data.get('yeni_sifre', None)
    
    if not mevcut_sifre or not yeni_sifre:
        return jsonify({"msg": "Mevcut şifre ve yeni şifre gerekli"}), 400
    
    # Mevcut şifre kontrolü
    if not bcrypt.check_password_hash(kullanici.sifre_hash, mevcut_sifre):
        return jsonify({"msg": "Mevcut şifre yanlış"}), 401
    
    # Şifre uzunluğu kontrolü
    if len(yeni_sifre) < 6:
        return jsonify({"msg": "Şifre en az 6 karakter olmalıdır"}), 400
    
    # Şifreyi güncelle
    kullanici.sifre_hash = bcrypt.generate_password_hash(yeni_sifre).decode('utf-8')
    db.session.commit()
    
    return jsonify({"msg": "Şifre başarıyla değiştirildi"}), 200

@api_auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Şifremi unuttum"""
    if not request.is_json:
        return jsonify({"msg": "JSON verisi gerekli"}), 400
    
    data = request.get_json()
    eposta = data.get('eposta', None)
    
    if not eposta:
        return jsonify({"msg": "E-posta adresi gerekli"}), 400
    
    kullanici = Kullanici.query.filter_by(eposta=eposta).first()
    
    # Güvenlik için kullanıcı bulunamasa bile aynı mesajı döndür
    if kullanici:
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        # Şifre sıfırlama token'ı oluştur
        token = auth_service.generate_reset_token()
        kullanici.sifre_sifirlama_token = token
        kullanici.sifre_sifirlama_son_tarih = db.func.now() + timedelta(hours=1)
        db.session.commit()
        
        # E-posta gönderme işlemi
        reset_url = f"{request.host_url.rstrip('/')}/auth/reset-password/{token}"
        auth_service.send_password_reset_email(kullanici.eposta, reset_url)
    
    return jsonify({"msg": "Şifre sıfırlama bağlantısı e-posta adresinize gönderildi"}), 200

@api_auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Kullanıcı listesini getir (sadece admin)"""
    kullanici_id = get_jwt_identity()
    kullanici = Kullanici.query.get(kullanici_id)
    
    if not kullanici or not kullanici.is_admin():
        return jsonify({"msg": "Bu işlem için yetkiniz yok"}), 403
    
    kullanicilar = Kullanici.query.all()
    return jsonify([k.to_dict() for k in kullanicilar]), 200
