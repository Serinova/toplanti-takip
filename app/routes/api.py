from flask import Blueprint
from app.routes.api import api_bp

# API Blueprint'i oluştur
api_bp = Blueprint('api', __name__, url_prefix='/api')

# API rotalarını içe aktar
from app.routes.auth import api_login, api_register, api_refresh
from app.routes.toplanti import api_toplantilar, api_toplanti_olustur, api_toplanti_detay, api_toplanti_guncelle, api_toplanti_iptal, api_toplanti_ozet
from app.routes.gundem import api_notlar, api_not_ekle, api_not_guncelle, api_not_sil
from app.routes.gorev import api_gorevler, api_gorev_olustur, api_gorev_detay, api_gorev_guncelle, api_gorev_durum_guncelle, api_gorev_yorum_ekle
from app.routes.bildirim import api_bildirimler, api_okundu_isaretle, api_tumu_okundu, api_bildirim_ayarlari, api_bildirim_ayarlari_guncelle
from app.routes.urun import api_urunler, api_urun_olustur, api_urun_detay, api_urun_guncelle, api_urun_sil
from app.routes.rapor import api_dashboard, api_toplanti_raporu, api_gorev_raporu, api_kullanici_raporu
from app.routes.ai import api_toplanti_ozet_olustur, api_gundem_maddeleri_olustur, api_notlardan_gorev_cikar, api_ai_asistan
