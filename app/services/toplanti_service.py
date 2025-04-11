from app.models import Toplanti, Katilimci, MisafirKatilimci, GundemMaddesi, Kullanici
from app import db
from sqlalchemy import and_

def get_toplanti_katilimcilar(toplanti_id):
    """Toplantının katılımcılarını döndürür."""
    # Kayıtlı kullanıcı katılımcılar
    katilimcilar = db.session.query(
        Katilimci, Kullanici
    ).join(
        Kullanici, Katilimci.kullanici_id == Kullanici.id
    ).filter(
        Katilimci.toplanti_id == toplanti_id
    ).all()
    
    # Misafir katılımcılar
    misafir_katilimcilar = MisafirKatilimci.query.filter_by(toplanti_id=toplanti_id).all()
    
    # Sonuçları birleştir
    sonuc = []
    for katilimci, kullanici in katilimcilar:
        sonuc.append({
            'id': katilimci.id,
            'kullanici_id': kullanici.id,
            'ad': kullanici.ad,
            'eposta': kullanici.eposta,
            'profil_resmi_url': kullanici.profil_resmi_url,
            'davet_durumu': katilimci.davet_durumu,
            'katildi': katilimci.katildi,
            'misafir': False
        })
    
    for misafir in misafir_katilimcilar:
        sonuc.append({
            'id': misafir.id,
            'eposta': misafir.eposta,
            'ad': misafir.ad or misafir.eposta.split('@')[0],
            'davet_durumu': 'Bekliyor',
            'katildi': False,
            'misafir': True
        })
    
    return sonuc

def get_toplanti_gundem_maddeleri(toplanti_id):
    """Toplantının gündem maddelerini döndürür."""
    return GundemMaddesi.query.filter_by(toplanti_id=toplanti_id).order_by(GundemMaddesi.sira).all()

def get_kullanici_toplantilar(kullanici_id):
    """Kullanıcının oluşturduğu ve katıldığı toplantıları döndürür."""
    # Kullanıcının oluşturduğu toplantılar
    olusturulan_toplantilar = Toplanti.query.filter_by(olusturan_kullanici_id=kullanici_id).all()
    
    # Kullanıcının katılımcı olduğu toplantılar
    katilimci_toplantilar = db.session.query(Toplanti).join(
        Katilimci, Toplanti.id == Katilimci.toplanti_id
    ).filter(
        Katilimci.kullanici_id == kullanici_id
    ).all()
    
    return {
        'olusturulan_toplantilar': olusturulan_toplantilar,
        'katilimci_toplantilar': katilimci_toplantilar
    }

def get_yaklasan_toplantilar(kullanici_id, gun_sayisi=7):
    """Kullanıcının yaklaşan toplantılarını döndürür."""
    from datetime import datetime, timedelta
    
    simdi = datetime.utcnow()
    bitis = simdi + timedelta(days=gun_sayisi)
    
    # Kullanıcının oluşturduğu yaklaşan toplantılar
    olusturulan_toplantilar = Toplanti.query.filter(
        and_(
            Toplanti.olusturan_kullanici_id == kullanici_id,
            Toplanti.baslangic_zamani >= simdi,
            Toplanti.baslangic_zamani <= bitis,
            Toplanti.iptal_edildi == False
        )
    ).order_by(Toplanti.baslangic_zamani).all()
    
    # Kullanıcının katılımcı olduğu yaklaşan toplantılar
    katilimci_toplantilar = db.session.query(Toplanti).join(
        Katilimci, Toplanti.id == Katilimci.toplanti_id
    ).filter(
        and_(
            Katilimci.kullanici_id == kullanici_id,
            Toplanti.baslangic_zamani >= simdi,
            Toplanti.baslangic_zamani <= bitis,
            Toplanti.iptal_edildi == False
        )
    ).order_by(Toplanti.baslangic_zamani).all()
    
    return {
        'olusturulan_toplantilar': olusturulan_toplantilar,
        'katilimci_toplantilar': katilimci_toplantilar
    }

def toplanti_katilimci_ekle(toplanti_id, kullanici_id, davet_durumu='Bekliyor'):
    """Toplantıya katılımcı ekler."""
    # Katılımcı zaten eklenmiş mi kontrol et
    katilimci = Katilimci.query.filter_by(
        toplanti_id=toplanti_id,
        kullanici_id=kullanici_id
    ).first()
    
    if katilimci:
        return katilimci
    
    # Yeni katılımcı ekle
    katilimci = Katilimci(
        toplanti_id=toplanti_id,
        kullanici_id=kullanici_id,
        davet_durumu=davet_durumu
    )
    
    db.session.add(katilimci)
    db.session.commit()
    
    return katilimci

def toplanti_misafir_ekle(toplanti_id, eposta, ad=None):
    """Toplantıya misafir katılımcı ekler."""
    # Misafir zaten eklenmiş mi kontrol et
    misafir = MisafirKatilimci.query.filter_by(
        toplanti_id=toplanti_id,
        eposta=eposta
    ).first()
    
    if misafir:
        return misafir
    
    # Yeni misafir ekle
    misafir = MisafirKatilimci(
        toplanti_id=toplanti_id,
        eposta=eposta,
        ad=ad
    )
    
    db.session.add(misafir)
    db.session.commit()
    
    return misafir

def toplanti_iptal_et(toplanti_id):
    """Toplantıyı iptal eder."""
    from datetime import datetime
    
    toplanti = Toplanti.query.get(toplanti_id)
    if not toplanti:
        return False
    
    toplanti.iptal_edildi = True
    toplanti.iptal_edilen_tarih = datetime.utcnow()
    db.session.commit()
    
    return True

def toplanti_davet_durumu_guncelle(katilimci_id, davet_durumu):
    """Katılımcının davet durumunu günceller."""
    katilimci = Katilimci.query.get(katilimci_id)
    if not katilimci:
        return False
    
    katilimci.davet_durumu = davet_durumu
    db.session.commit()
    
    return True

def toplanti_katildi_isaretle(katilimci_id, katildi=True):
    """Katılımcının katılım durumunu işaretler."""
    katilimci = Katilimci.query.get(katilimci_id)
    if not katilimci:
        return False
    
    katilimci.katildi = katildi
    db.session.commit()
    
    return True
