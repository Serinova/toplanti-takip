from app.models import Gorev, GorevYorumu, Kullanici, Puan
from app import db
from sqlalchemy import and_
from datetime import datetime

def get_gorev_yorumlari(gorev_id):
    """Göreve ait yorumları döndürür."""
    yorumlar = db.session.query(
        GorevYorumu, Kullanici
    ).join(
        Kullanici, GorevYorumu.yazan_kullanici_id == Kullanici.id
    ).filter(
        GorevYorumu.gorev_id == gorev_id
    ).order_by(GorevYorumu.olusturulma_zamani).all()
    
    sonuc = []
    for yorum, kullanici in yorumlar:
        sonuc.append({
            'id': yorum.id,
            'gorev_id': yorum.gorev_id,
            'yazan_kullanici_id': yorum.yazan_kullanici_id,
            'yazan_kullanici_ad': kullanici.ad,
            'yazan_kullanici_profil_resmi': kullanici.profil_resmi_url,
            'yorum': yorum.yorum,
            'olusturulma_zamani': yorum.olusturulma_zamani
        })
    
    return sonuc

def get_kullanici_gorevleri(kullanici_id):
    """Kullanıcıya atanan ve kullanıcının oluşturduğu görevleri döndürür."""
    # Kullanıcıya atanan görevler
    atanan_gorevler = Gorev.query.filter_by(atanan_kullanici_id=kullanici_id).all()
    
    # Kullanıcının oluşturduğu görevler
    olusturulan_gorevler = Gorev.query.filter_by(olusturan_kullanici_id=kullanici_id).all()
    
    return {
        'atanan_gorevler': atanan_gorevler,
        'olusturulan_gorevler': olusturulan_gorevler
    }

def get_yaklasan_gorevler(kullanici_id, gun_sayisi=7):
    """Kullanıcının yaklaşan görevlerini döndürür."""
    from datetime import datetime, timedelta
    
    simdi = datetime.utcnow()
    bitis = simdi + timedelta(days=gun_sayisi)
    
    # Kullanıcıya atanan yaklaşan görevler
    gorevler = Gorev.query.filter(
        and_(
            Gorev.atanan_kullanici_id == kullanici_id,
            Gorev.son_teslim_tarihi >= simdi,
            Gorev.son_teslim_tarihi <= bitis,
            Gorev.durum != 'Tamamlandı'
        )
    ).order_by(Gorev.son_teslim_tarihi).all()
    
    return gorevler

def gorev_olustur(atanan_kullanici_id, olusturan_kullanici_id, baslik, son_teslim_tarihi, 
                 aciklama=None, toplanti_id=None, urun_id=None, puan_degeri=0):
    """Yeni görev oluşturur."""
    gorev = Gorev(
        toplanti_id=toplanti_id,
        atanan_kullanici_id=atanan_kullanici_id,
        olusturan_kullanici_id=olusturan_kullanici_id,
        urun_id=urun_id,
        baslik=baslik,
        aciklama=aciklama,
        son_teslim_tarihi=son_teslim_tarihi,
        puan_degeri=puan_degeri
    )
    
    db.session.add(gorev)
    db.session.commit()
    
    return gorev

def gorev_guncelle(gorev_id, baslik=None, aciklama=None, son_teslim_tarihi=None, 
                  atanan_kullanici_id=None, toplanti_id=None, urun_id=None, puan_degeri=None):
    """Görevi günceller."""
    gorev = Gorev.query.get(gorev_id)
    if not gorev:
        return False
    
    if baslik is not None:
        gorev.baslik = baslik
    if aciklama is not None:
        gorev.aciklama = aciklama
    if son_teslim_tarihi is not None:
        gorev.son_teslim_tarihi = son_teslim_tarihi
    if atanan_kullanici_id is not None:
        gorev.atanan_kullanici_id = atanan_kullanici_id
    if toplanti_id is not None:
        gorev.toplanti_id = toplanti_id
    if urun_id is not None:
        gorev.urun_id = urun_id
    if puan_degeri is not None:
        gorev.puan_degeri = puan_degeri
    
    db.session.commit()
    
    return gorev

def gorev_durum_guncelle(gorev_id, durum):
    """Görev durumunu günceller."""
    gorev = Gorev.query.get(gorev_id)
    if not gorev:
        return False
    
    if durum not in ['Yapılacak', 'Devam Ediyor', 'Tamamlandı']:
        return False
    
    gorev.durum = durum
    
    # Eğer durum "Tamamlandı" ise tamamlanma zamanını güncelle
    if durum == 'Tamamlandı':
        gorev.tamamlanma_zamani = datetime.utcnow()
        
        # Puan ekle
        if gorev.puan_degeri > 0:
            puan = Puan(
                kullanici_id=gorev.atanan_kullanici_id,
                gorev_id=gorev.id,
                puan=gorev.puan_degeri,
                aciklama=f'"{gorev.baslik}" görevi tamamlandı'
            )
            db.session.add(puan)
    else:
        gorev.tamamlanma_zamani = None
    
    db.session.commit()
    
    return gorev

def gorev_yorum_ekle(gorev_id, yazan_kullanici_id, yorum):
    """Göreve yorum ekler."""
    gorev_yorumu = GorevYorumu(
        gorev_id=gorev_id,
        yazan_kullanici_id=yazan_kullanici_id,
        yorum=yorum
    )
    
    db.session.add(gorev_yorumu)
    db.session.commit()
    
    return gorev_yorumu

def gorev_yorum_sil(yorum_id):
    """Görev yorumunu siler."""
    yorum = GorevYorumu.query.get(yorum_id)
    if not yorum:
        return False
    
    db.session.delete(yorum)
    db.session.commit()
    
    return True

def get_kullanici_puanlari(kullanici_id):
    """Kullanıcının puanlarını döndürür."""
    puanlar = Puan.query.filter_by(kullanici_id=kullanici_id).order_by(Puan.verilme_zamani.desc()).all()
    toplam_puan = sum(puan.puan for puan in puanlar)
    
    return {
        'puanlar': puanlar,
        'toplam_puan': toplam_puan
    }
