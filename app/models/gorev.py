from datetime import datetime
from app import db

class Gorev(db.Model):
    """Görev modeli."""
    __tablename__ = 'gorevler'
    
    id = db.Column(db.Integer, primary_key=True)
    toplanti_id = db.Column(db.Integer, db.ForeignKey('toplantilar.id'), nullable=True)
    atanan_kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    olusturan_kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'), nullable=True)
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    son_teslim_tarihi = db.Column(db.DateTime, nullable=False)
    durum = db.Column(db.String(20), default='Yapılacak')  # 'Yapılacak', 'Devam Ediyor', 'Tamamlandı'
    puan_degeri = db.Column(db.Integer, default=0)
    olusturulma_zamani = db.Column(db.DateTime, default=datetime.utcnow)
    tamamlanma_zamani = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    yorumlar = db.relationship('GorevYorumu', backref='gorev', lazy=True, cascade='all, delete-orphan')
    puanlar = db.relationship('Puan', backref='gorev', lazy=True)
    
    def to_dict(self):
        """Görev bilgilerini sözlük olarak döndürür."""
        return {
            'id': self.id,
            'toplanti_id': self.toplanti_id,
            'atanan_kullanici_id': self.atanan_kullanici_id,
            'olusturan_kullanici_id': self.olusturan_kullanici_id,
            'urun_id': self.urun_id,
            'baslik': self.baslik,
            'aciklama': self.aciklama,
            'son_teslim_tarihi': self.son_teslim_tarihi.isoformat() if self.son_teslim_tarihi else None,
            'durum': self.durum,
            'puan_degeri': self.puan_degeri,
            'olusturulma_zamani': self.olusturulma_zamani.isoformat() if self.olusturulma_zamani else None,
            'tamamlanma_zamani': self.tamamlanma_zamani.isoformat() if self.tamamlanma_zamani else None
        }
    
    def __repr__(self):
        return f'<Gorev {self.baslik}>'

class GorevYorumu(db.Model):
    """Görev Yorumu modeli."""
    __tablename__ = 'gorev_yorumlari'
    
    id = db.Column(db.Integer, primary_key=True)
    gorev_id = db.Column(db.Integer, db.ForeignKey('gorevler.id'), nullable=False)
    yazan_kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    yorum = db.Column(db.Text, nullable=False)
    olusturulma_zamani = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    yazan = db.relationship('Kullanici', backref=db.backref('gorev_yorumlari', lazy=True))
    
    def to_dict(self):
        """Görev yorumu bilgilerini sözlük olarak döndürür."""
        return {
            'id': self.id,
            'gorev_id': self.gorev_id,
            'yazan_kullanici_id': self.yazan_kullanici_id,
            'yorum': self.yorum,
            'olusturulma_zamani': self.olusturulma_zamani.isoformat() if self.olusturulma_zamani else None
        }
    
    def __repr__(self):
        return f'<GorevYorumu {self.id}>'
