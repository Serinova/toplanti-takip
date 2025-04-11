from app.models import GundemMaddesi, Not
from app import db

def get_gundem_maddesi_notlar(gundem_madde_id):
    """Gündem maddesine ait notları döndürür."""
    return Not.query.filter_by(gundem_madde_id=gundem_madde_id).order_by(Not.olusturulma_zamani).all()

def get_toplanti_gundem_maddeleri_with_notlar(toplanti_id):
    """Toplantının gündem maddelerini ve her maddeye ait notları döndürür."""
    gundem_maddeleri = GundemMaddesi.query.filter_by(toplanti_id=toplanti_id).order_by(GundemMaddesi.sira).all()
    
    sonuc = []
    for madde in gundem_maddeleri:
        notlar = get_gundem_maddesi_notlar(madde.id)
        sonuc.append({
            'gundem_maddesi': madde,
            'notlar': notlar
        })
    
    return sonuc

def gundem_maddesi_ekle(toplanti_id, baslik, aciklama=None, sira=None, hedef=None):
    """Toplantıya gündem maddesi ekler."""
    # Sıra numarasını belirle
    if sira is None:
        son_sira = db.session.query(db.func.max(GundemMaddesi.sira)).filter_by(toplanti_id=toplanti_id).scalar()
        sira = 0 if son_sira is None else son_sira + 1
    
    gundem_maddesi = GundemMaddesi(
        toplanti_id=toplanti_id,
        baslik=baslik,
        aciklama=aciklama,
        sira=sira,
        hedef=hedef
    )
    
    db.session.add(gundem_maddesi)
    db.session.commit()
    
    return gundem_maddesi

def gundem_maddesi_guncelle(gundem_madde_id, baslik=None, aciklama=None, sira=None, hedef=None):
    """Gündem maddesini günceller."""
    gundem_maddesi = GundemMaddesi.query.get(gundem_madde_id)
    if not gundem_maddesi:
        return False
    
    if baslik is not None:
        gundem_maddesi.baslik = baslik
    if aciklama is not None:
        gundem_maddesi.aciklama = aciklama
    if sira is not None:
        gundem_maddesi.sira = sira
    if hedef is not None:
        gundem_maddesi.hedef = hedef
    
    db.session.commit()
    
    return gundem_maddesi

def gundem_maddesi_sil(gundem_madde_id):
    """Gündem maddesini siler."""
    gundem_maddesi = GundemMaddesi.query.get(gundem_madde_id)
    if not gundem_maddesi:
        return False
    
    # İlişkili notları sil
    Not.query.filter_by(gundem_madde_id=gundem_madde_id).delete()
    
    # Gündem maddesini sil
    db.session.delete(gundem_maddesi)
    db.session.commit()
    
    return True

def gundem_maddesi_not_ekle(gundem_madde_id, kullanici_id, icerik):
    """Gündem maddesine not ekler."""
    # Gündem maddesini kontrol et
    gundem_maddesi = GundemMaddesi.query.get(gundem_madde_id)
    if not gundem_maddesi:
        return False
    
    # Not ekle
    not_obj = Not(
        toplanti_id=gundem_maddesi.toplanti_id,
        kullanici_id=kullanici_id,
        gundem_madde_id=gundem_madde_id,
        icerik=icerik
    )
    
    db.session.add(not_obj)
    db.session.commit()
    
    return not_obj

def gundem_maddesi_sirala(toplanti_id, gundem_madde_siralama):
    """Gündem maddelerini yeniden sıralar."""
    # gundem_madde_siralama: [{'id': 1, 'sira': 0}, {'id': 2, 'sira': 1}, ...]
    for item in gundem_madde_siralama:
        gundem_maddesi = GundemMaddesi.query.get(item['id'])
        if gundem_maddesi and gundem_maddesi.toplanti_id == toplanti_id:
            gundem_maddesi.sira = item['sira']
    
    db.session.commit()
    
    return True
