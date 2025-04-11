from app.models import Toplanti, Gorev, Kullanici, Urun, Katilimci, Not
from app import db
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta

def generate_toplanti_raporu(baslangic_tarihi, bitis_tarihi):
    """Toplantı raporunu oluşturur."""
    # Toplantı sayıları
    toplanti_sayisi = Toplanti.query.filter(
        and_(
            Toplanti.baslangic_zamani >= baslangic_tarihi,
            Toplanti.baslangic_zamani <= bitis_tarihi
        )
    ).count()
    
    aktif_toplanti_sayisi = Toplanti.query.filter(
        and_(
            Toplanti.baslangic_zamani >= baslangic_tarihi,
            Toplanti.baslangic_zamani <= bitis_tarihi,
            Toplanti.iptal_edildi == False
        )
    ).count()
    
    iptal_edilen_toplanti_sayisi = Toplanti.query.filter(
        and_(
            Toplanti.baslangic_zamani >= baslangic_tarihi,
            Toplanti.baslangic_zamani <= bitis_tarihi,
            Toplanti.iptal_edildi == True
        )
    ).count()
    
    # Toplantı oluşturan kullanıcılar
    toplanti_olusturanlar = db.session.query(
        Kullanici.id, Kullanici.ad, func.count(Toplanti.id).label('toplanti_sayisi')
    ).join(
        Toplanti, Kullanici.id == Toplanti.olusturan_kullanici_id
    ).filter(
        and_(
            Toplanti.baslangic_zamani >= baslangic_tarihi,
            Toplanti.baslangic_zamani <= bitis_tarihi
        )
    ).group_by(
        Kullanici.id
    ).order_by(
        func.count(Toplanti.id).desc()
    ).limit(10).all()
    
    # Katılımcı sayısına göre toplantılar
    katilimci_sayilari = db.session.query(
        Toplanti.id, Toplanti.baslik, func.count(Katilimci.id).label('katilimci_sayisi')
    ).join(
        Katilimci, Toplanti.id == Katilimci.toplanti_id
    ).filter(
        and_(
            Toplanti.baslangic_zamani >= baslangic_tarihi,
            Toplanti.baslangic_zamani <= bitis_tarihi
        )
    ).group_by(
        Toplanti.id
    ).order_by(
        func.count(Katilimci.id).desc()
    ).limit(10).all()
    
    # Günlere göre toplantı sayıları
    gun_farki = (bitis_tarihi - baslangic_tarihi).days
    gunluk_toplanti_sayilari = []
    
    for i in range(gun_farki + 1):
        gun = baslangic_tarihi + timedelta(days=i)
        gun_baslangic = datetime(gun.year, gun.month, gun.day, 0, 0, 0)
        gun_bitis = datetime(gun.year, gun.month, gun.day, 23, 59, 59)
        
        gun_toplanti_sayisi = Toplanti.query.filter(
            and_(
                Toplanti.baslangic_zamani >= gun_baslangic,
                Toplanti.baslangic_zamani <= gun_bitis
            )
        ).count()
        
        gunluk_toplanti_sayilari.append({
            'tarih': gun.strftime('%Y-%m-%d'),
            'toplanti_sayisi': gun_toplanti_sayisi
        })
    
    return {
        'toplanti_sayilari': {
            'toplam': toplanti_sayisi,
            'aktif': aktif_toplanti_sayisi,
            'iptal_edilen': iptal_edilen_toplanti_sayisi
        },
        'toplanti_olusturanlar': [
            {
                'kullanici_id': kullanici_id,
                'kullanici_ad': kullanici_ad,
                'toplanti_sayisi': toplanti_sayisi
            } for kullanici_id, kullanici_ad, toplanti_sayisi in toplanti_olusturanlar
        ],
        'katilimci_sayilari': [
            {
                'toplanti_id': toplanti_id,
                'toplanti_baslik': toplanti_baslik,
                'katilimci_sayisi': katilimci_sayisi
            } for toplanti_id, toplanti_baslik, katilimci_sayisi in katilimci_sayilari
        ],
        'gunluk_toplanti_sayilari': gunluk_toplanti_sayilari
    }

def generate_gorev_raporu(baslangic_tarihi, bitis_tarihi):
    """Görev raporunu oluşturur."""
    # Görev sayıları
    gorev_sayisi = Gorev.query.filter(
        and_(
            Gorev.olusturulma_zamani >= baslangic_tarihi,
            Gorev.olusturulma_zamani <= bitis_tarihi
        )
    ).count()
    
    tamamlanan_gorev_sayisi = Gorev.query.filter(
        and_(
            Gorev.olusturulma_zamani >= baslangic_tarihi,
            Gorev.olusturulma_zamani <= bitis_tarihi,
            Gorev.durum == 'Tamamlandı'
        )
    ).count()
    
    devam_eden_gorev_sayisi = Gorev.query.filter(
        and_(
            Gorev.olusturulma_zamani >= baslangic_tarihi,
            Gorev.olusturulma_zamani <= bitis_tarihi,
            Gorev.durum == 'Devam Ediyor'
        )
    ).count()
    
    yapilacak_gorev_sayisi = Gorev.query.filter(
        and_(
            Gorev.olusturulma_zamani >= baslangic_tarihi,
            Gorev.olusturulma_zamani <= bitis_tarihi,
            Gorev.durum == 'Yapılacak'
        )
    ).count()
    
    # Görev oluşturan kullanıcılar
    gorev_olusturanlar = db.session.query(
        Kullanici.id, Kullanici.ad, func.count(Gorev.id).label('gorev_sayisi')
    ).join(
        Gorev, Kullanici.id == Gorev.olusturan_kullanici_id
    ).filter(
        and_(
            Gorev.olusturulma_zamani >= baslangic_tarihi,
            Gorev.olusturulma_zamani <= bitis_tarihi
        )
    ).group_by(
        Kullanici.id
    ).order_by(
        func.count(Gorev.id).desc()
    ).limit(10).all()
    
    # Görev atanan kullanıcılar
    gorev_atananlar = db.session.query(
        Kullanici.id, Kullanici.ad, func.count(Gorev.id).label('gorev_sayisi')
    ).join(
        Gorev, Kullanici.id == Gorev.atanan_kullanici_id
    ).filter(
        and_(
            Gorev.olusturulma_zamani >= baslangic_tarihi,
            Gorev.olusturulma_zamani <= bitis_tarihi
        )
    ).group_by(
        Kullanici.id
    ).order_by(
        func.count(Gorev.id).desc()
    ).limit(10).all()
    
    # Ürünlere göre görev sayıları
    urun_gorev_sayilari = db.session.query(
        Urun.id, Urun.ad, func.count(Gorev.id).label('gorev_sayisi')
    ).join(
        Gorev, Urun.id == Gorev.urun_id
    ).filter(
        and_(
            Gorev.olusturulma_zamani >= baslangic_tarihi,
            Gorev.olusturulma_zamani <= bitis_tarihi
        )
    ).group_by(
        Urun.id
    ).order_by(
        func.count(Gorev.id).desc()
    ).limit(10).all()
    
    # Günlere göre görev sayıları
    gun_farki = (bitis_tarihi - baslangic_tarihi).days
    gunluk_gorev_sayilari = []
    
    for i in range(gun_farki + 1):
        gun = baslangic_tarihi + timedelta(days=i)
        gun_baslangic = datetime(gun.year, gun.month, gun.day, 0, 0, 0)
        gun_bitis = datetime(gun.year, gun.month, gun.day, 23, 59, 59)
        
        gun_gorev_sayisi = Gorev.query.filter(
            and_(
                Gorev.olusturulma_zamani >= gun_baslangic,
                Gorev.olusturulma_zamani <= gun_bitis
            )
        ).count()
        
        gunluk_gorev_sayilari.append({
            'tarih': gun.strftime('%Y-%m-%d'),
            'gorev_sayisi': gun_gorev_sayisi
        })
    
    return {
        'gorev_sayilari': {
            'toplam': gorev_sayisi,
            'tamamlanan': tamamlanan_gorev_sayisi,
            'devam_eden': devam_eden_gorev_sayisi,
            'yapilacak': yapilacak_gorev_sayisi
        },
        'gorev_olusturanlar': [
            {
                'kullanici_id': kullanici_id,
                'kullanici_ad': kullanici_ad,
                'gorev_sayisi': gorev_sayisi
            } for kullanici_id, kullanici_ad, gorev_sayisi in gorev_olusturanlar
        ],
        'gorev_atananlar': [
            {
                'kullanici_id': kullanici_id,
                'kullanici_ad': kullanici_ad,
                'gorev_sayisi': gorev_sayisi
            } for kullanici_id, kullanici_ad, gorev_sayisi in gorev_atananlar
        ],
        'urun_gorev_sayilari': [
            {
                'urun_id': urun_id,
                'urun_ad': urun_ad,
                'gorev_sayisi': gorev_sayisi
            } for urun_id, urun_ad, gorev_sayisi in urun_gorev_sayilari
        ],
        'gunluk_gorev_sayilari': gunluk_gorev_sayilari
    }

def generate_kullanici_raporu():
    """Kullanıcı raporunu oluşturur."""
    # Kullanıcı sayıları
    kullanici_sayisi = Kullanici.query.count()
    admin_sayisi = Kullanici.query.filter_by(rol='admin').count()
    normal_kullanici_sayisi = Kullanici.query.filter_by(rol='normal').count()
    
    # En aktif kullanıcılar (toplantı oluşturma)
    aktif_toplanti_olusturanlar = db.session.query(
        Kullanici.id, Kullanici.ad, func.count(Toplanti.id).label('toplanti_sayisi')
    ).join(
        Toplanti, Kullanici.id == Toplanti.olusturan_kullanici_id
    ).group_by(
        Kullanici.id
    ).order_by(
        func.count(Toplanti.id).desc()
    ).limit(10).all()
    
    # En aktif kullanıcılar (görev tamamlama)
    aktif_gorev_tamamlayanlar = db.session.query(
        Kullanici.id, Kullanici.ad, func.count(Gorev.id).label('gorev_sayisi')
    ).join(
        Gorev, Kullanici.id == Gorev.atanan_kullanici_id
    ).filter(
        Gorev.durum == 'Tamamlandı'
    ).group_by(
        Kullanici.id
    ).order_by(
        func.count(Gorev.id).desc()
    ).limit(10).all()
    
    # En aktif kullanıcılar (not oluşturma)
    aktif_not_olusturanlar = db.session.query(
        Kullanici.id, Kullanici.ad, func.count(Not.id).label('not_sayisi')
    ).join(
        Not, Kullanici.id == Not.kullanici_id
    ).group_by(
        Kullanici.id
    ).order_by(
        func.count(Not.id).desc()
    ).limit(10).all()
    
    # Kayıt tarihine göre kullanıcı sayıları (son 12 ay)
    simdi = datetime.utcnow()
    aylik_kullanici_sayilari = []
    
    for i in range(12):
        ay_baslangic = datetime(simdi.year, simdi.month, 1, 0, 0, 0) - timedelta(days=30*i)
        ay_bitis = datetime(ay_baslangic.year, ay_baslangic.month + 1, 1, 0, 0, 0) - timedelta(seconds=1) if ay_baslangic.month < 12 else datetime(ay_baslangic.year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
        
        ay_kullanici_sayisi = Kullanici.query.filter(
            and_(
                Kullanici.kayit_tarihi >= ay_baslangic,
                Kullanici.kayit_tarihi <= ay_bitis
            )
        ).count()
        
        aylik_kullanici_sayilari.append({
            'ay': ay_baslangic.strftime('%Y-%m'),
            'kullanici_sayisi': ay_kullanici_sayisi
        })
    
    return {
        'kullanici_sayilari': {
            'toplam': kullanici_sayisi,
            'admin': admin_sayisi,
            'normal': normal_kullanici_sayisi
        },
        'aktif_toplanti_olusturanlar': [
            {
                'kullanici_id': kullanici_id,
                'kullanici_ad': kullanici_ad,
                'toplanti_sayisi': toplanti_sayisi
            } for kullanici_id, kullanici_ad, toplanti_sayisi in aktif_toplanti_olusturanlar
        ],
        'aktif_gorev_tamamlayanlar': [
            {
                'kullanici_id': kullanici_id,
                'kullanici_ad': kullanici_ad,
                'gorev_sayisi': gorev_sayisi
            } for kullanici_id, kullanici_ad, gorev_sayisi in aktif_gorev_tamamlayanlar
        ],
        'aktif_not_olusturanlar': [
            {
                'kullanici_id': kullanici_id,
                'kullanici_ad': kullanici_ad,
                'not_sayisi': not_sayisi
            } for kullanici_id, kullanici_ad, not_sayisi in aktif_not_olusturanlar
        ],
        'aylik_kullanici_sayilari': aylik_kullanici_sayilari
    }
