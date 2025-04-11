from datetime import datetime
from app import db

class Katilimci(db.Model):
    """Katılımcı modeli."""
    __tablename__ = 'katilimcilar'
    
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    toplanti_id = db.Column(db.Integer, db.ForeignKey('toplantilar.id'), nullable=False)
    davet_durumu = db.Column(db.String(20), default='Bekliyor')  # 'Katılacak', 'Belki', 'Katılmayacak', 'Bekliyor'
    katildi = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kullanici = db.relationship('Kullanici', backref=db.backref('katilimci_toplantilar', lazy=True))
    
    # Bileşik anahtar
    __table_args__ = (db.UniqueConstraint('kullanici_id', 'toplanti_id', name='_kullanici_toplanti_uc'),)
    
    def to_dict(self):
        """Katılımcı bilgilerini sözlük olarak döndürür."""
        return {
            'id': self.id,
            'kullanici_id': self.kullanici_id,
            'toplanti_id': self.toplanti_id,
            'davet_durumu': self.davet_durumu,
            'katildi': self.katildi
        }
    
    def __repr__(self):
        return f'<Katilimci {self.kullanici_id} - {self.toplanti_id}>'

class MisafirKatilimci(db.Model):
    """Misafir Katılımcı modeli."""
    __tablename__ = 'misafir_katilimcilar'
    
    id = db.Column(db.Integer, primary_key=True)
    toplanti_id = db.Column(db.Integer, db.ForeignKey('toplantilar.id'), nullable=False)
    eposta = db.Column(db.String(100), nullable=False)
    ad = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Misafir katılımcı bilgilerini sözlük olarak döndürür."""
        return {
            'id': self.id,
            'toplanti_id': self.toplanti_id,
            'eposta': self.eposta,
            'ad': self.ad
        }
    
    def __repr__(self):
        return f'<MisafirKatilimci {self.eposta}>'
