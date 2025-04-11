from datetime import datetime
from app import db

class Not(db.Model):
    """Not modeli."""
    __tablename__ = 'notlar'
    
    id = db.Column(db.Integer, primary_key=True)
    toplanti_id = db.Column(db.Integer, db.ForeignKey('toplantilar.id'), nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    gundem_madde_id = db.Column(db.Integer, db.ForeignKey('gundem_maddeleri.id'), nullable=True)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'), nullable=True)
    icerik = db.Column(db.Text, nullable=False)
    olusturulma_zamani = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Not bilgilerini sözlük olarak döndürür."""
        return {
            'id': self.id,
            'toplanti_id': self.toplanti_id,
            'kullanici_id': self.kullanici_id,
            'gundem_madde_id': self.gundem_madde_id,
            'urun_id': self.urun_id,
            'icerik': self.icerik,
            'olusturulma_zamani': self.olusturulma_zamani.isoformat() if self.olusturulma_zamani else None
        }
    
    def __repr__(self):
        return f'<Not {self.id}>'

class Dosya(db.Model):
    """Dosya modeli."""
    __tablename__ = 'dosyalar'
    
    id = db.Column(db.Integer, primary_key=True)
    toplanti_id = db.Column(db.Integer, db.ForeignKey('toplantilar.id'), nullable=False)
    yukleyen_kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    dosya_adi = db.Column(db.String(255), nullable=False)
    dosya_turu = db.Column(db.String(50), nullable=False)
    dosya_url = db.Column(db.String(255), nullable=False)
    yuklenme_zamani = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    yukleyen = db.relationship('Kullanici', backref=db.backref('yuklenen_dosyalar', lazy=True))
    
    def to_dict(self):
        """Dosya bilgilerini sözlük olarak döndürür."""
        return {
            'id': self.id,
            'toplanti_id': self.toplanti_id,
            'yukleyen_kullanici_id': self.yukleyen_kullanici_id,
            'dosya_adi': self.dosya_adi,
            'dosya_turu': self.dosya_turu,
            'dosya_url': self.dosya_url,
            'yuklenme_zamani': self.yuklenme_zamani.isoformat() if self.yuklenme_zamani else None
        }
    
    def __repr__(self):
        return f'<Dosya {self.dosya_adi}>'
