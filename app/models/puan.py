from datetime import datetime
from app import db

class Puan(db.Model):
    """Puan modeli."""
    __tablename__ = 'puanlar'
    
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    gorev_id = db.Column(db.Integer, db.ForeignKey('gorevler.id'), nullable=True)
    puan = db.Column(db.Integer, nullable=False)
    verilme_zamani = db.Column(db.DateTime, default=datetime.utcnow)
    aciklama = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kullanici = db.relationship('Kullanici', backref=db.backref('puanlar', lazy=True))
    
    def to_dict(self):
        """Puan bilgilerini sözlük olarak döndürür."""
        return {
            'id': self.id,
            'kullanici_id': self.kullanici_id,
            'gorev_id': self.gorev_id,
            'puan': self.puan,
            'verilme_zamani': self.verilme_zamani.isoformat() if self.verilme_zamani else None,
            'aciklama': self.aciklama
        }
    
    def __repr__(self):
        return f'<Puan {self.id}>'
