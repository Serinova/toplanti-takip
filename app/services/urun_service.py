from app.models import Urun, Not, Gorev
from app import db

def get_urunler():
    """Tüm ürünleri döndürür."""
    return Urun.query.all()

def get_urun_by_id(urun_id):
    """ID'ye göre ürün döndürür."""
    return Urun.query.get(urun_id)

def get_urun_by_ad(ad):
    """Ada göre ürün döndürür."""
    return Urun.query.filter_by(ad=ad).first()

def get_urun_notlar(urun_id):
    """Ürüne ait notları döndürür."""
    return Not.query.filter_by(urun_id=urun_id).all()

def get_urun_gorevler(urun_id):
    """Ürüne ait görevleri döndürür."""
    return Gorev.query.filter_by(urun_id=urun_id).all()

def urun_olustur(ad, aciklama=None, gorsel_url=None):
    """Yeni ürün oluşturur."""
    # Aynı isimde ürün var mı kontrol et
    mevcut_urun = get_urun_by_ad(ad)
    if mevcut_urun:
        return None
    
    urun = Urun(
        ad=ad,
        aciklama=aciklama,
        gorsel_url=gorsel_url
    )
    
    db.session.add(urun)
    db.session.commit()
    
    return urun

def urun_guncelle(urun_id, ad=None, aciklama=None, gorsel_url=None):
    """Ürünü günceller."""
    urun = get_urun_by_id(urun_id)
    if not urun:
        return False
    
    # Eğer ad değişiyorsa, aynı isimde başka ürün var mı kontrol et
    if ad is not None and ad != urun.ad:
        mevcut_urun = get_urun_by_ad(ad)
        if mevcut_urun:
            return False
        urun.ad = ad
    
    if aciklama is not None:
        urun.aciklama = aciklama
    
    if gorsel_url is not None:
        urun.gorsel_url = gorsel_url
    
    db.session.commit()
    
    return urun

def urun_sil(urun_id):
    """Ürünü siler."""
    urun = get_urun_by_id(urun_id)
    if not urun:
        return False
    
    # İlişkili kayıtları kontrol et
    notlar_count = Not.query.filter_by(urun_id=urun_id).count()
    gorevler_count = Gorev.query.filter_by(urun_id=urun_id).count()
    
    if notlar_count > 0 or gorevler_count > 0:
        return False
    
    db.session.delete(urun)
    db.session.commit()
    
    return True

def urun_not_ekle(urun_id, kullanici_id, toplanti_id, icerik):
    """Ürüne not ekler."""
    not_obj = Not(
        urun_id=urun_id,
        kullanici_id=kullanici_id,
        toplanti_id=toplanti_id,
        icerik=icerik
    )
    
    db.session.add(not_obj)
    db.session.commit()
    
    return not_obj

def urun_gorev_ekle(urun_id, atanan_kullanici_id, olusturan_kullanici_id, baslik, son_teslim_tarihi, aciklama=None, toplanti_id=None, puan_degeri=0):
    """Ürüne görev ekler."""
    from app.services.gorev_service import gorev_olustur
    
    return gorev_olustur(
        atanan_kullanici_id=atanan_kullanici_id,
        olusturan_kullanici_id=olusturan_kullanici_id,
        baslik=baslik,
        son_teslim_tarihi=son_teslim_tarihi,
        aciklama=aciklama,
        toplanti_id=toplanti_id,
        urun_id=urun_id,
        puan_degeri=puan_degeri
    )
