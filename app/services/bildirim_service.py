from app.models import Bildirim, KullaniciBildirimAyarlari, Kullanici
from app import db
from datetime import datetime
from flask_mail import Message
from app import mail

def get_kullanici_bildirimleri(kullanici_id, okunmamis_only=False):
    """Kullanıcının bildirimlerini döndürür."""
    query = Bildirim.query.filter_by(kullanici_id=kullanici_id)
    
    if okunmamis_only:
        query = query.filter_by(okundu=False)
    
    bildirimler = query.order_by(Bildirim.olusturulma_zamani.desc()).all()
    
    return bildirimler

def get_okunmamis_bildirim_sayisi(kullanici_id):
    """Kullanıcının okunmamış bildirim sayısını döndürür."""
    return Bildirim.query.filter_by(kullanici_id=kullanici_id, okundu=False).count()

def bildirim_olustur(kullanici_id, bildirim_tipi, mesaj, toplanti_id=None, gorev_id=None):
    """Yeni bildirim oluşturur."""
    bildirim = Bildirim(
        kullanici_id=kullanici_id,
        toplanti_id=toplanti_id,
        gorev_id=gorev_id,
        bildirim_tipi=bildirim_tipi,
        mesaj=mesaj
    )
    
    db.session.add(bildirim)
    db.session.commit()
    
    # Kullanıcının bildirim ayarlarını kontrol et ve e-posta gönder
    ayarlar = get_kullanici_bildirim_ayarlari(kullanici_id)
    
    if ayarlar:
        eposta_gonder = False
        
        if bildirim_tipi in ['yeni_toplanti_daveti', 'toplanti_guncellendi', 'toplanti_iptal_edildi'] and ayarlar.yeni_toplanti_eposta:
            eposta_gonder = True
        elif bildirim_tipi in ['atanan_yeni_gorev', 'gorev_son_tarihi_yaklasiyor'] and ayarlar.atanan_gorev_eposta:
            eposta_gonder = True
        elif bildirim_tipi in ['gorev_tamamlandi', 'puan_kazanildi', 'yeni_yorum_eklendi'] and ayarlar.hatirlatma_eposta:
            eposta_gonder = True
        
        if eposta_gonder:
            kullanici = Kullanici.query.get(kullanici_id)
            if kullanici:
                send_bildirim_email(kullanici, bildirim)
    
    return bildirim

def bildirim_okundu_isaretle(bildirim_id):
    """Bildirimi okundu olarak işaretler."""
    bildirim = Bildirim.query.get(bildirim_id)
    if not bildirim:
        return False
    
    bildirim.okundu = True
    db.session.commit()
    
    return True

def tum_bildirimleri_okundu_isaretle(kullanici_id):
    """Kullanıcının tüm bildirimlerini okundu olarak işaretler."""
    Bildirim.query.filter_by(kullanici_id=kullanici_id, okundu=False).update({'okundu': True})
    db.session.commit()
    
    return True

def get_kullanici_bildirim_ayarlari(kullanici_id):
    """Kullanıcının bildirim ayarlarını döndürür."""
    ayarlar = KullaniciBildirimAyarlari.query.filter_by(kullanici_id=kullanici_id).first()
    
    if not ayarlar:
        # Varsayılan ayarları oluştur
        ayarlar = KullaniciBildirimAyarlari(kullanici_id=kullanici_id)
        db.session.add(ayarlar)
        db.session.commit()
    
    return ayarlar

def bildirim_ayarlari_guncelle(kullanici_id, yeni_toplanti_uygulama_ici=None, yeni_toplanti_eposta=None,
                              atanan_gorev_uygulama_ici=None, atanan_gorev_eposta=None,
                              hatirlatma_uygulama_ici=None, hatirlatma_eposta=None, hatirlatma_suresi=None):
    """Kullanıcının bildirim ayarlarını günceller."""
    ayarlar = get_kullanici_bildirim_ayarlari(kullanici_id)
    
    if yeni_toplanti_uygulama_ici is not None:
        ayarlar.yeni_toplanti_uygulama_ici = yeni_toplanti_uygulama_ici
    if yeni_toplanti_eposta is not None:
        ayarlar.yeni_toplanti_eposta = yeni_toplanti_eposta
    if atanan_gorev_uygulama_ici is not None:
        ayarlar.atanan_gorev_uygulama_ici = atanan_gorev_uygulama_ici
    if atanan_gorev_eposta is not None:
        ayarlar.atanan_gorev_eposta = atanan_gorev_eposta
    if hatirlatma_uygulama_ici is not None:
        ayarlar.hatirlatma_uygulama_ici = hatirlatma_uygulama_ici
    if hatirlatma_eposta is not None:
        ayarlar.hatirlatma_eposta = hatirlatma_eposta
    if hatirlatma_suresi is not None:
        ayarlar.hatirlatma_suresi = hatirlatma_suresi
    
    db.session.commit()
    
    return ayarlar

def send_bildirim_email(kullanici, bildirim):
    """Bildirim e-postası gönderir."""
    from flask import current_app
    
    msg = Message(
        'Yeni Bildirim: ' + bildirim.bildirim_tipi.replace('_', ' ').title(),
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[kullanici.eposta]
    )
    
    msg.body = f'''Merhaba {kullanici.ad},

{bildirim.mesaj}

Bu bildirimi Toplantı Takip Programı üzerinden aldınız.
'''
    
    mail.send(msg)
    
    return True

def toplanti_bildirimleri_olustur(toplanti, bildirim_tipi, mesaj):
    """Toplantı katılımcılarına bildirim oluşturur."""
    from app.models import Katilimci
    
    # Katılımcıları al
    katilimcilar = Katilimci.query.filter_by(toplanti_id=toplanti.id).all()
    
    for katilimci in katilimcilar:
        # Toplantı sahibi hariç
        if katilimci.kullanici_id != toplanti.olusturan_kullanici_id:
            bildirim_olustur(
                kullanici_id=katilimci.kullanici_id,
                bildirim_tipi=bildirim_tipi,
                mesaj=mesaj,
                toplanti_id=toplanti.id
            )
    
    return True

def gorev_bildirimleri_olustur(gorev, bildirim_tipi, mesaj):
    """Görev ile ilgili bildirim oluşturur."""
    # Görevi oluşturan kişi, görevi atanan kişiye bildirim gönderir
    if gorev.atanan_kullanici_id != gorev.olusturan_kullanici_id:
        bildirim_olustur(
            kullanici_id=gorev.atanan_kullanici_id,
            bildirim_tipi=bildirim_tipi,
            mesaj=mesaj,
            gorev_id=gorev.id
        )
    
    return True
