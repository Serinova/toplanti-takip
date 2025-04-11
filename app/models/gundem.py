from datetime import datetime
from app import db

class GundemMaddesi(db.Model):
    """Gündem Maddesi modeli."""
    __tablename__ = 'gundem_maddeleri'
    
    id = db.Column(db.Integer, primary_key=True)
    toplanti_id = db.Column(db.Integer, db.ForeignKey('toplantilar.id'), nullable=False)
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    sira = db.Column(db.Integer, default=0)
    hedef = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    notlar = db.relationship('Not', backref='gundem_maddesi', lazy=True)
    
    def to_dict(self):
        """Gündem maddesi bilgilerini sözlük olarak döndürür."""
        return {
            'id': self.id,
            'toplanti_id': self.toplanti_id,
            'baslik': self.baslik,
            'aciklama': self.aciklama,
            'sira': self.sira,
            'hedef': self.hedef
        }
    
    def __repr__(self):
        return f'<GundemMaddesi {self.baslik}>'
