from datetime import datetime
from app import db

class Toplanti(db.Model):
    """Toplantı modeli."""
    __tablename__ = 'toplantilar'
    
    id = db.Column(db.Integer, primary_key=True)
    olusturan_kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    baslangic_zamani = db.Column(db.DateTime, nullable=False)
    bitis_zamani = db.Column(db.DateTime, nullable=False)
    konum = db.Column(db.String(200))
    sanal_toplanti_linki = db.Column(db.String(255))
    iptal_edildi = db.Column(db.Boolean, default=False)
    iptal_edilen_tarih = db.Column(db.DateTime)
    tekrar_sikligi = db.Column(db.String(20), default=None)  # 'günlük', 'haftalık', 'aylık', None
    tekrar_bitis_tarihi = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    gundem_maddeleri = db.relationship('GundemMaddesi', backref='toplanti', lazy=True, cascade='all, delete-orphan')
    katilimcilar = db.relationship('Katilimci', backref='toplanti', lazy=True, cascade='all, delete-orphan')
    misafir_katilimcilar = db.relationship('MisafirKatilimci', backref='toplanti', lazy=True, cascade='all, delete-orphan')
    notlar = db.relationship('Not', backref='toplanti', lazy=True, cascade='all, delete-orphan')
    dosyalar = db.relationship('Dosya', backref='toplanti', lazy=True, cascade='all, delete-orphan')
    gorevler = db.relationship('Gorev', backref='toplanti', lazy=True)
    
    def to_dict(self):
        """Toplantı bilgilerini sözlük olarak döndürür."""
        return {
            'id': self.id,
            'olusturan_kullanici_id': self.olusturan_kullanici_id,
            'baslik': self.baslik,
            'aciklama': self.aciklama,
            'baslangic_zamani': self.baslangic_zamani.isoformat() if self.baslangic_zamani else None,
            'bitis_zamani': self.bitis_zamani.isoformat() if self.bitis_zamani else None,
            'konum': self.konum,
            'sanal_toplanti_linki': self.sanal_toplanti_linki,
            'iptal_edildi': self.iptal_edildi,
            'iptal_edilen_tarih': self.iptal_edilen_tarih.isoformat() if self.iptal_edilen_tarih else None,
            'tekrar_sikligi': self.tekrar_sikligi,
            'tekrar_bitis_tarihi': self.tekrar_bitis_tarihi.isoformat() if self.tekrar_bitis_tarihi else None
        }
    
    def __repr__(self):
        return f'<Toplanti {self.baslik}>'
