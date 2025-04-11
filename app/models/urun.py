from datetime import datetime
from app import db

class Urun(db.Model):
    """Ürün modeli."""
    __tablename__ = 'urunler'
    
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(200), nullable=False, unique=True)
    aciklama = db.Column(db.Text)
    gorsel_url = db.Column(db.String(255))
    eklenme_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    notlar = db.relationship('Not', backref='urun', lazy=True)
    gorevler = db.relationship('Gorev', backref='urun', lazy=True)
    
    def to_dict(self):
        """Ürün bilgilerini sözlük olarak döndürür."""
        return {
            'id': self.id,
            'ad': self.ad,
            'aciklama': self.aciklama,
            'gorsel_url': self.gorsel_url,
            'eklenme_tarihi': self.eklenme_tarihi.isoformat() if self.eklenme_tarihi else None
        }
    
    def __repr__(self):
        return f'<Urun {self.ad}>'
