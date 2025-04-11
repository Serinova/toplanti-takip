import unittest
from app import create_app
from app.extensions import db
from app.models.kullanici import Kullanici
from app.models.toplanti import Toplanti
from app.models.gundem import Gundem
from app.models.katilimci import Katilimci
from app.models.not_dosya import Not, Dosya
from app.models.gorev import Gorev
from app.models.bildirim import Bildirim, BildirimAyarlari
from app.models.urun import Urun
from app.models.puan import Puan
from app.models.kisisel_not import KisiselNot
from datetime import datetime, timedelta
import os
import tempfile

class FlaskTestCase(unittest.TestCase):
    """Flask uygulaması için test sınıfı"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        # Test için geçici veritabanı oluştur
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Test yapılandırması
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{self.db_path}',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': 'test_secret_key',
            'WTF_CSRF_ENABLED': False,
            'SECURITY_PASSWORD_SALT': 'test_salt',
            'MAIL_DEFAULT_SENDER': 'test@example.com',
            'OPENAI_API_KEY': 'test_api_key',
            'FLASK_ENV': 'development'
        })
        
        # Test istemcisi
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Veritabanını oluştur
        db.create_all()
        
        # Test kullanıcısı oluştur
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        test_kullanici = Kullanici(
            ad='Test Kullanıcı',
            eposta='test@example.com',
            sifre_hash=auth_service.create_password_hash('test123'),
            rol='kullanici',
            aktif=True,
            kayit_tarihi=datetime.utcnow()
        )
        
        admin_kullanici = Kullanici(
            ad='Admin Kullanıcı',
            eposta='admin@example.com',
            sifre_hash=auth_service.create_password_hash('admin123'),
            rol='admin',
            aktif=True,
            kayit_tarihi=datetime.utcnow()
        )
        
        db.session.add(test_kullanici)
        db.session.add(admin_kullanici)
        db.session.commit()
    
    def tearDown(self):
        """Test sonrası temizlik"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def login(self, eposta, sifre):
        """Test için giriş yap"""
        return self.client.post('/login', data={
            'eposta': eposta,
            'sifre': sifre
        }, follow_redirects=True)
    
    def logout(self):
        """Test için çıkış yap"""
        return self.client.get('/logout', follow_redirects=True)
    
    def test_anasayfa(self):
        """Anasayfa testi"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Toplant\xc4\xb1 Takip Program\xc4\xb1', response.data)
    
    def test_login(self):
        """Giriş testi"""
        # Geçersiz giriş
        response = self.login('yanlis@example.com', 'yanlis123')
        self.assertIn(b'Ge\xc3\xa7ersiz e-posta veya \xc5\x9fifre', response.data)
        
        # Geçerli giriş
        response = self.login('test@example.com', 'test123')
        self.assertIn(b'Ba\xc5\x9far\xc4\xb1yla giri\xc5\x9f yapt\xc4\xb1n\xc4\xb1z', response.data)
        
        # Çıkış
        response = self.logout()
        self.assertIn(b'Ba\xc5\x9far\xc4\xb1yla \xc3\xa7\xc4\xb1k\xc4\xb1\xc5\x9f yapt\xc4\xb1n\xc4\xb1z', response.data)
    
    def test_register(self):
        """Kayıt testi"""
        response = self.client.post('/register', data={
            'ad': 'Yeni Kullanıcı',
            'eposta': 'yeni@example.com',
            'sifre': 'yeni123',
            'sifre_tekrar': 'yeni123'
        }, follow_redirects=True)
        
        self.assertIn(b'Hesab\xc4\xb1n\xc4\xb1z ba\xc5\x9far\xc4\xb1yla olu\xc5\x9fturuldu', response.data)
        
        # Aynı e-posta ile tekrar kayıt
        response = self.client.post('/register', data={
            'ad': 'Yeni Kullanıcı 2',
            'eposta': 'yeni@example.com',
            'sifre': 'yeni123',
            'sifre_tekrar': 'yeni123'
        }, follow_redirects=True)
        
        self.assertIn(b'Bu e-posta adresi zaten kullan\xc4\xb1l\xc4\xb1yor', response.data)
    
    def test_protected_routes(self):
        """Korumalı rotalar testi"""
        # Giriş yapmadan korumalı sayfaya erişim
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Bu sayfay\xc4\xb1 g\xc3\xb6r\xc3\xbcnt\xc3\xbclemek i\xc3\xa7in giri\xc5\x9f yapmal\xc4\xb1s\xc4\xb1n\xc4\xb1z', response.data)
        
        # Giriş yap
        self.login('test@example.com', 'test123')
        
        # Korumalı sayfaya erişim
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'G\xc3\xb6sterge Paneli', response.data)
    
    def test_admin_routes(self):
        """Admin rotaları testi"""
        # Normal kullanıcı ile admin sayfasına erişim
        self.login('test@example.com', 'test123')
        response = self.client.get('/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 403)
        
        # Çıkış yap
        self.logout()
        
        # Admin kullanıcı ile admin sayfasına erişim
        self.login('admin@example.com', 'admin123')
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Y\xc3\xb6netim Paneli', response.data)
    
    def test_toplanti_islemleri(self):
        """Toplantı işlemleri testi"""
        # Giriş yap
        self.login('test@example.com', 'test123')
        
        # Toplantı oluştur
        response = self.client.post('/toplantilar/yeni', data={
            'baslik': 'Test Toplantısı',
            'aciklama': 'Bu bir test toplantısıdır',
            'baslangic_tarihi': '2025-04-15',
            'baslangic_saati': '10:00',
            'bitis_tarihi': '2025-04-15',
            'bitis_saati': '11:00',
            'konum': 'Test Odası',
            'sanal_toplanti_linki': 'https://meet.example.com/test',
            'tekrar_sikligi': '',
            'hatirlatma': '15_dakika'
        }, follow_redirects=True)
        
        self.assertIn(b'Toplant\xc4\xb1 ba\xc5\x9far\xc4\xb1yla olu\xc5\x9fturuldu', response.data)
        
        # Toplantı listesi
        response = self.client.get('/toplantilar')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Toplant\xc4\xb1s\xc4\xb1', response.data)
        
        # Toplantı detayı
        toplanti = Toplanti.query.filter_by(baslik='Test Toplantısı').first()
        response = self.client.get(f'/toplantilar/{toplanti.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Toplant\xc4\xb1s\xc4\xb1', response.data)
        
        # Toplantı güncelle
        response = self.client.post(f'/toplantilar/{toplanti.id}/duzenle', data={
            'baslik': 'Güncellenmiş Test Toplantısı',
            'aciklama': 'Bu güncellenmiş bir test toplantısıdır',
            'baslangic_tarihi': '2025-04-16',
            'baslangic_saati': '11:00',
            'bitis_tarihi': '2025-04-16',
            'bitis_saati': '12:00',
            'konum': 'Güncellenmiş Test Odası',
            'sanal_toplanti_linki': 'https://meet.example.com/updated-test',
            'tekrar_sikligi': '',
            'hatirlatma': '30_dakika'
        }, follow_redirects=True)
        
        self.assertIn(b'Toplant\xc4\xb1 ba\xc5\x9far\xc4\xb1yla g\xc3\xbcncellendi', response.data)
        self.assertIn(b'G\xc3\xbcncellenmi\xc5\x9f Test Toplant\xc4\xb1s\xc4\xb1', response.data)
    
    def test_gundem_islemleri(self):
        """Gündem işlemleri testi"""
        # Giriş yap
        self.login('test@example.com', 'test123')
        
        # Test toplantısı oluştur
        toplanti = Toplanti(
            baslik='Gündem Test Toplantısı',
            aciklama='Gündem testi için toplantı',
            baslangic_zamani=datetime.utcnow() + timedelta(days=1),
            bitis_zamani=datetime.utcnow() + timedelta(days=1, hours=1),
            konum='Test Odası',
            olusturan_kullanici_id=1,
            olusturulma_zamani=datetime.utcnow(),
            guncelleme_zamani=datetime.utcnow()
        )
        db.session.add(toplanti)
        db.session.commit()
        
        # Gündem maddesi ekle
        response = self.client.post(f'/toplantilar/{toplanti.id}/gundem/yeni', data={
            'baslik': 'Test Gündem Maddesi',
            'aciklama': 'Bu bir test gündem maddesidir',
            'hedef': 'Test hedefi',
            'sure': 15,
            'toplanti_id': toplanti.id
        }, follow_redirects=True)
        
        self.assertIn(b'G\xc3\xbcndem maddesi ba\xc5\x9far\xc4\xb1yla eklendi', response.data)
        
        # Gündem maddesi listesi
        response = self.client.get(f'/toplantilar/{toplanti.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test G\xc3\xbcndem Maddesi', response.data)
        
        # Gündem maddesi güncelle
        gundem = Gundem.query.filter_by(baslik='Test Gündem Maddesi').first()
        response = self.client.post(f'/gundem/{gundem.id}/duzenle', data={
            'baslik': 'Güncellenmiş Test Gündem Maddesi',
            'aciklama': 'Bu güncellenmiş bir test gündem maddesidir',
            'hedef': 'Güncellenmiş test hedefi',
            'sure': 20,
            'toplanti_id': toplanti.id
        }, follow_redirects=True)
        
        self.assertIn(b'G\xc3\xbcndem maddesi ba\xc5\x9far\xc4\xb1yla g\xc3\xbcncellendi', response.data)
        self.assertIn(b'G\xc3\xbcncellenmi\xc5\x9f Test G\xc3\xbcndem Maddesi', response.data)
    
    def test_gorev_islemleri(self):
        """Görev işlemleri testi"""
        # Giriş yap
        self.login('test@example.com', 'test123')
        
        # Görev oluştur
        response = self.client.post('/gorevler/yeni', data={
            'baslik': 'Test Görevi',
            'aciklama': 'Bu bir test görevidir',
            'atanan_kullanici_id': 1,
            'son_teslim_tarihi': '2025-04-20',
            'oncelik': 'Normal',
            'durum': 'Yapılacak',
            'puan_degeri': 10
        }, follow_redirects=True)
        
        self.assertIn(b'G\xc3\xb6rev ba\xc5\x9far\xc4\xb1yla olu\xc5\x9fturuldu', response.data)
        
        # Görev listesi
        response = self.client.get('/gorevler')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test G\xc3\xb6revi', response.data)
        
        # Görev detayı
        gorev = Gorev.query.filter_by(baslik='Test Görevi').first()
        response = self.client.get(f'/gorevler/{gorev.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test G\xc3\xb6revi', response.data)
        
        # Görev güncelle
        response = self.client.post(f'/gorevler/{gorev.id}/duzenle', data={
            'baslik': 'Güncellenmiş Test Görevi',
            'aciklama': 'Bu güncellenmiş bir test görevidir',
            'atanan_kullanici_id': 1,
            'son_teslim_tarihi': '2025-04-25',
            'oncelik': 'Yüksek',
            'durum': 'Devam Ediyor',
            'puan_degeri': 15
        }, follow_redirects=True)
        
        self.assertIn(b'G\xc3\xb6rev ba\xc5\x9far\xc4\xb1yla g\xc3\xbcncellendi', response.data)
        self.assertIn(b'G\xc3\xbcncellenmi\xc5\x9f Test G\xc3\xb6revi', response.data)
        
        # Görev durumu güncelle
        response = self.client.post(f'/gorevler/{gorev.id}/durum', data={
            'durum': 'Tamamlandı'
        }, follow_redirects=True)
        
        self.assertIn(b'G\xc3\xb6rev durumu ba\xc5\x9far\xc4\xb1yla g\xc3\xbcncellendi', response.data)
        self.assertIn(b'Tamamland\xc4\xb1', response.data)
    
    def test_api_endpoints(self):
        """API uç noktaları testi"""
        # JWT token al
        response = self.client.post('/api/auth/login', json={
            'eposta': 'test@example.com',
            'sifre': 'test123'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('access_token', data)
        
        token = data['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Kullanıcı profili
        response = self.client.get('/api/auth/profile', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['eposta'], 'test@example.com')
        
        # Toplantı oluştur
        response = self.client.post('/api/toplantilar', json={
            'baslik': 'API Test Toplantısı',
            'aciklama': 'Bu bir API test toplantısıdır',
            'baslangic_zamani': '2025-04-15T10:00:00',
            'bitis_zamani': '2025-04-15T11:00:00',
            'konum': 'API Test Odası'
        }, headers=headers)
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('toplanti_id', data)
        
        toplanti_id = data['toplanti_id']
        
        # Toplantı detayı
        response = self.client.get(f'/api/toplantilar/{toplanti_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['baslik'], 'API Test Toplantısı')
        
        # Toplantı güncelle
        response = self.client.put(f'/api/toplantilar/{toplanti_id}', json={
            'baslik': 'Güncellenmiş API Test Toplantısı'
        }, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        
        # Toplantı listesi
        response = self.client.get('/api/toplantilar', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(len(data) > 0)
    
    def test_ai_integration(self):
        """AI entegrasyonu testi"""
        # Giriş yap
        self.login('test@example.com', 'test123')
        
        # Test toplantısı oluştur
        toplanti = Toplanti(
            baslik='AI Test Toplantısı',
            aciklama='AI testi için toplantı',
            baslangic_zamani=datetime.utcnow() - timedelta(days=1),
            bitis_zamani=datetime.utcnow() - timedelta(days=1, hours=-1),
            konum='Test Odası',
            olusturan_kullanici_id=1,
            olusturulma_zamani=datetime.utcnow(),
            guncelleme_zamani=datetime.utcnow()
        )
        db.session.add(toplanti)
        db.session.commit()
        
        # Gündem maddesi ekle
        gundem = Gundem(
            toplanti_id=toplanti.id,
            baslik='AI Test Gündem Maddesi',
            aciklama='AI testi için gündem maddesi',
            sira=1
        )
        db.session.add(gundem)
        db.session.commit()
        
        # Not ekle
        not_item = Not(
            gundem_id=gundem.id,
            kullanici_id=1,
            icerik='Bu bir test notudur. Proje planı tartışıldı ve görevler belirlendi.',
            olusturulma_zamani=datetime.utcnow()
        )
        db.session.add(not_item)
        db.session.commit()
        
        # Toplantı özeti
        response = self.client.get(f'/toplanti-ozeti/{toplanti.id}?generate=true')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('summary', data)
        
        # Görev çıkarma
        response = self.client.get(f'/gorev-cikar/{toplanti.id}?generate=true')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('tasks', data)
        
        # AI asistanı
        response = self.client.post('/ai-asistan', data={
            'soru': 'Etkili bir toplantı nasıl yönetilir?'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bu bir test yan\xc4\xb1t\xc4\xb1d\xc4\xb1r', response.data)

if __name__ == '__main__':
    unittest.main()
