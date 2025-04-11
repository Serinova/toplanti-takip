from flask_login import UserMixin
from datetime import datetime
from app.extensions import db

class Kullanici(db.Model, UserMixin):
    """Kullanıcı modeli"""
    __tablename__ = 'kullanicilar'
    
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    eposta = db.Column(db.String(100), unique=True, nullable=False)
    sifre_hash = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(20), default='kullanici')  # kullanici, admin
    aktif = db.Column(db.Boolean, default=True)
    profil_resmi_url = db.Column(db.String(255))
    telefon = db.Column(db.String(20))
    unvan = db.Column(db.String(100))
    departman = db.Column(db.String(100))
    kayit_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    son_giris_tarihi = db.Column(db.DateTime)
    eposta_onaylandi = db.Column(db.Boolean, default=False)
    sifre_sifirlama_token = db.Column(db.String(100))
    sifre_sifirlama_son_tarih = db.Column(db.DateTime)
    
    # İlişkiler
    olusturulan_toplantilar = db.relationship('Toplanti', backref='olusturan', lazy='dynamic', 
                                             foreign_keys='Toplanti.olusturan_kullanici_id')
    katilimci_olduklari = db.relationship('Katilimci', backref='kullanici', lazy='dynamic')
    olusturulan_gorevler = db.relationship('Gorev', backref='olusturan_kullanici', lazy='dynamic',
                                          foreign_keys='Gorev.olusturan_kullanici_id')
    atanan_gorevler = db.relationship('Gorev', backref='atanan_kullanici', lazy='dynamic',
                                     foreign_keys='Gorev.atanan_kullanici_id')
    bildirimler = db.relationship('Bildirim', backref='kullanici', lazy='dynamic')
    puanlar = db.relationship('Puan', backref='kullanici', lazy='dynamic')
    kisisel_notlar = db.relationship('KisiselNot', backref='kullanici', lazy='dynamic')
    
    def __repr__(self):
        return f'<Kullanici {self.eposta}>'
    
    def to_dict(self):
        """Kullanıcı bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'ad': self.ad,
            'eposta': self.eposta,
            'rol': self.rol,
            'aktif': self.aktif,
            'profil_resmi_url': self.profil_resmi_url,
            'telefon': self.telefon,
            'unvan': self.unvan,
            'departman': self.departman,
            'kayit_tarihi': self.kayit_tarihi.isoformat() if self.kayit_tarihi else None,
            'son_giris_tarihi': self.son_giris_tarihi.isoformat() if self.son_giris_tarihi else None,
            'eposta_onaylandi': self.eposta_onaylandi
        }
    
    def is_admin(self):
        """Kullanıcının admin olup olmadığını kontrol eder"""
        return self.rol == 'admin'
    
    def get_toplam_puan(self):
        """Kullanıcının toplam puanını hesaplar"""
        from app.models.puan import Puan
        puanlar = Puan.query.filter_by(kullanici_id=self.id).all()
        return sum(puan.deger for puan in puanlar)
    
    def get_tamamlanan_gorev_sayisi(self):
        """Kullanıcının tamamladığı görev sayısını hesaplar"""
        from app.models.gorev import Gorev
        return Gorev.query.filter_by(atanan_kullanici_id=self.id, durum='Tamamlandı').count()
    
    def get_bekleyen_gorev_sayisi(self):
        """Kullanıcının bekleyen görev sayısını hesaplar"""
        from app.models.gorev import Gorev
        return Gorev.query.filter(
            Gorev.atanan_kullanici_id == self.id,
            Gorev.durum.in_(['Yapılacak', 'Devam Ediyor'])
        ).count()
    
    def get_okunmamis_bildirim_sayisi(self):
        """Kullanıcının okunmamış bildirim sayısını hesaplar"""
        from app.models.bildirim import Bildirim
        return Bildirim.query.filter_by(kullanici_id=self.id, okundu=False).count()
    
    def get_yaklasan_toplantilar(self, gun_sayisi=7):
        """Kullanıcının yaklaşan toplantılarını getirir"""
        from app.models.toplanti import Toplanti
        from app.models.katilimci import Katilimci
        from sqlalchemy import and_
        from datetime import datetime, timedelta
        
        simdi = datetime.utcnow()
        bitis_tarihi = simdi + timedelta(days=gun_sayisi)
        
        # Oluşturduğu toplantılar
        olusturulan = Toplanti.query.filter(
            Toplanti.olusturan_kullanici_id == self.id,
            Toplanti.baslangic_zamani >= simdi,
            Toplanti.baslangic_zamani <= bitis_tarihi,
            Toplanti.iptal_edildi == False
        ).all()
        
        # Katılımcı olduğu toplantılar
        katilimci_olduklari_ids = db.session.query(Katilimci.toplanti_id).filter(
            Katilimci.kullanici_id == self.id,
            Katilimci.davet_durumu == 'Kabul Edildi'
        ).all()
        
        katilimci_olduklari_ids = [id[0] for id in katilimci_olduklari_ids]
        
        katilimci_olduklari = Toplanti.query.filter(
            Toplanti.id.in_(katilimci_olduklari_ids),
            Toplanti.baslangic_zamani >= simdi,
            Toplanti.baslangic_zamani <= bitis_tarihi,
            Toplanti.iptal_edildi == False
        ).all()
        
        # Birleştir ve tarihe göre sırala
        tum_toplantilar = olusturulan + katilimci_olduklari
        tum_toplantilar.sort(key=lambda x: x.baslangic_zamani)
        
        return tum_toplantilar
