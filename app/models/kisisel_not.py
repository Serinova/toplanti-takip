from datetime import datetime
from app import db

class KisiselNot(db.Model):
    """Kişisel Not modeli."""
    __tablename__ = 'kisisel_notlar'
    
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    baslik = db.Column(db.String(200), nullable=False)
    icerik = db.Column(db.Text, nullable=False)
    olusturulma_zamani = db.Column(db.DateTime, default=datetime.utcnow)
    guncelleme_zamani = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Kişisel not bilgilerini sözlük olarak döndürür."""
        return {
            'id': self.id,
            'kullanici_id': self.kullanici_id,
            'baslik': self.baslik,
            'icerik': self.icerik,
            'olusturulma_zamani': self.olusturulma_zamani.isoformat() if self.olusturulma_zamani else None,
            'guncelleme_zamani': self.guncelleme_zamani.isoformat() if self.guncelleme_zamani else None
        }
    
    def __repr__(self):
        return f'<KisiselNot {self.baslik}>'

class GundemSablonu(db.Model):
    """Gündem Şablonu modeli."""
    __tablename__ = 'gundem_sablonlari'
    
    id = db.Column(db.Integer, primary_key=True)
    olusturan_kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    ad = db.Column(db.String(200), nullable=False)
    maddeler = db.Column(db.Text, nullable=False)
    olusturulma_zamani = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    olusturan = db.relationship('Kullanici', backref=db.backref('gundem_sablonlari', lazy=True))
    
    def to_dict(self):
        """Gündem şablonu bilgilerini sözlük olarak döndürür."""
        return {
            'id': self.id,
            'olusturan_kullanici_id': self.olusturan_kullanici_id,
            'ad': self.ad,
            'maddeler': self.maddeler,
            'olusturulma_zamani': self.olusturulma_zamani.isoformat() if self.olusturulma_zamani else None
        }
    
    def __repr__(self):
        return f'<GundemSablonu {self.ad}>'
