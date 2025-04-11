from datetime import datetime
from app import db

class Bildirim(db.Model):
    """Bildirim modeli."""
    __tablename__ = 'bildirimler'
    
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    toplanti_id = db.Column(db.Integer, db.ForeignKey('toplantilar.id'), nullable=True)
    gorev_id = db.Column(db.Integer, db.ForeignKey('gorevler.id'), nullable=True)
    bildirim_tipi = db.Column(db.String(50), nullable=False)
    mesaj = db.Column(db.String(255), nullable=False)
    olusturulma_zamani = db.Column(db.DateTime, default=datetime.utcnow)
    okundu = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Bildirim bilgilerini sözlük olarak döndürür."""
        return {
            'id': self.id,
            'kullanici_id': self.kullanici_id,
            'toplanti_id': self.toplanti_id,
            'gorev_id': self.gorev_id,
            'bildirim_tipi': self.bildirim_tipi,
            'mesaj': self.mesaj,
            'olusturulma_zamani': self.olusturulma_zamani.isoformat() if self.olusturulma_zamani else None,
            'okundu': self.okundu
        }
    
    def __repr__(self):
        return f'<Bildirim {self.id}>'

class KullaniciBildirimAyarlari(db.Model):
    """Kullanıcı Bildirim Ayarları modeli."""
    __tablename__ = 'kullanici_bildirim_ayarlari'
    
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False, unique=True)
    yeni_toplanti_uygulama_ici = db.Column(db.Boolean, default=True)
    yeni_toplanti_eposta = db.Column(db.Boolean, default=False)
    atanan_gorev_uygulama_ici = db.Column(db.Boolean, default=True)
    atanan_gorev_eposta = db.Column(db.Boolean, default=False)
    hatirlatma_uygulama_ici = db.Column(db.Boolean, default=True)
    hatirlatma_eposta = db.Column(db.Boolean, default=False)
    hatirlatma_suresi = db.Column(db.Integer, default=15)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kullanici = db.relationship('Kullanici', backref=db.backref('bildirim_ayarlari', uselist=False, lazy=True))
    
    def to_dict(self):
        """Kullanıcı bildirim ayarları bilgilerini sözlük olarak döndürür."""
        return {
            'id': self.id,
            'kullanici_id': self.kullanici_id,
            'yeni_toplanti_uygulama_ici': self.yeni_toplanti_uygulama_ici,
            'yeni_toplanti_eposta': self.yeni_toplanti_eposta,
            'atanan_gorev_uygulama_ici': self.atanan_gorev_uygulama_ici,
            'atanan_gorev_eposta': self.atanan_gorev_eposta,
            'hatirlatma_uygulama_ici': self.hatirlatma_uygulama_ici,
            'hatirlatma_eposta': self.hatirlatma_eposta,
            'hatirlatma_suresi': self.hatirlatma_suresi
        }
    
    def __repr__(self):
        return f'<KullaniciBildirimAyarlari {self.kullanici_id}>'
