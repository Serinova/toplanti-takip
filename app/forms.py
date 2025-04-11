from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateField, TimeField, IntegerField, FloatField, HiddenField, MultipleFileField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from flask_wtf.file import FileField, FileAllowed
from datetime import datetime

class LoginForm(FlaskForm):
    """Kullanıcı giriş formu"""
    eposta = EmailField('E-posta', validators=[
        DataRequired(message='E-posta adresi gereklidir'),
        Email(message='Geçerli bir e-posta adresi giriniz')
    ])
    sifre = PasswordField('Şifre', validators=[
        DataRequired(message='Şifre gereklidir')
    ])
    beni_hatirla = BooleanField('Beni hatırla')
    submit = SubmitField('Giriş Yap')

class RegisterForm(FlaskForm):
    """Kullanıcı kayıt formu"""
    ad = StringField('Ad Soyad', validators=[
        DataRequired(message='Ad Soyad gereklidir'),
        Length(min=3, max=100, message='Ad Soyad 3-100 karakter arasında olmalıdır')
    ])
    eposta = EmailField('E-posta', validators=[
        DataRequired(message='E-posta adresi gereklidir'),
        Email(message='Geçerli bir e-posta adresi giriniz')
    ])
    sifre = PasswordField('Şifre', validators=[
        DataRequired(message='Şifre gereklidir'),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır')
    ])
    sifre_tekrar = PasswordField('Şifre Tekrar', validators=[
        DataRequired(message='Şifre tekrarı gereklidir'),
        EqualTo('sifre', message='Şifreler eşleşmiyor')
    ])
    submit = SubmitField('Kayıt Ol')

class ForgotPasswordForm(FlaskForm):
    """Şifremi unuttum formu"""
    eposta = EmailField('E-posta', validators=[
        DataRequired(message='E-posta adresi gereklidir'),
        Email(message='Geçerli bir e-posta adresi giriniz')
    ])
    submit = SubmitField('Şifre Sıfırlama Bağlantısı Gönder')

class ResetPasswordForm(FlaskForm):
    """Şifre sıfırlama formu"""
    sifre = PasswordField('Yeni Şifre', validators=[
        DataRequired(message='Şifre gereklidir'),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır')
    ])
    sifre_tekrar = PasswordField('Şifre Tekrar', validators=[
        DataRequired(message='Şifre tekrarı gereklidir'),
        EqualTo('sifre', message='Şifreler eşleşmiyor')
    ])
    submit = SubmitField('Şifremi Sıfırla')

class ProfileForm(FlaskForm):
    """Kullanıcı profil formu"""
    ad = StringField('Ad Soyad', validators=[
        DataRequired(message='Ad Soyad gereklidir'),
        Length(min=3, max=100, message='Ad Soyad 3-100 karakter arasında olmalıdır')
    ])
    eposta = EmailField('E-posta', validators=[
        DataRequired(message='E-posta adresi gereklidir'),
        Email(message='Geçerli bir e-posta adresi giriniz')
    ])
    telefon = StringField('Telefon', validators=[Optional()])
    unvan = StringField('Ünvan', validators=[Optional()])
    departman = StringField('Departman', validators=[Optional()])
    profil_resmi = FileField('Profil Resmi', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Sadece resim dosyaları yüklenebilir')
    ])
    submit = SubmitField('Profili Güncelle')

class ChangePasswordForm(FlaskForm):
    """Şifre değiştirme formu"""
    mevcut_sifre = PasswordField('Mevcut Şifre', validators=[
        DataRequired(message='Mevcut şifre gereklidir')
    ])
    yeni_sifre = PasswordField('Yeni Şifre', validators=[
        DataRequired(message='Yeni şifre gereklidir'),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır')
    ])
    yeni_sifre_tekrar = PasswordField('Yeni Şifre Tekrar', validators=[
        DataRequired(message='Şifre tekrarı gereklidir'),
        EqualTo('yeni_sifre', message='Şifreler eşleşmiyor')
    ])
    submit = SubmitField('Şifreyi Değiştir')

class ToplantiForm(FlaskForm):
    """Toplantı oluşturma/düzenleme formu"""
    baslik = StringField('Başlık', validators=[
        DataRequired(message='Başlık gereklidir'),
        Length(min=3, max=200, message='Başlık 3-200 karakter arasında olmalıdır')
    ])
    aciklama = TextAreaField('Açıklama', validators=[Optional()])
    baslangic_tarihi = DateField('Başlangıç Tarihi', format='%Y-%m-%d', validators=[
        DataRequired(message='Başlangıç tarihi gereklidir')
    ])
    baslangic_saati = TimeField('Başlangıç Saati', format='%H:%M', validators=[
        DataRequired(message='Başlangıç saati gereklidir')
    ])
    bitis_tarihi = DateField('Bitiş Tarihi', format='%Y-%m-%d', validators=[
        DataRequired(message='Bitiş tarihi gereklidir')
    ])
    bitis_saati = TimeField('Bitiş Saati', format='%H:%M', validators=[
        DataRequired(message='Bitiş saati gereklidir')
    ])
    konum = StringField('Konum', validators=[Optional()])
    sanal_toplanti_linki = StringField('Sanal Toplantı Linki', validators=[Optional()])
    tekrar_sikligi = SelectField('Tekrar Sıklığı', choices=[
        ('', 'Tekrar Yok'),
        ('gunluk', 'Günlük'),
        ('haftalik', 'Haftalık'),
        ('iki_haftalik', 'İki Haftalık'),
        ('aylik', 'Aylık')
    ], validators=[Optional()])
    tekrar_bitis_tarihi = DateField('Tekrar Bitiş Tarihi', format='%Y-%m-%d', validators=[Optional()])
    hatirlatma = SelectField('Hatırlatma', choices=[
        ('', 'Hatırlatma Yok'),
        ('5_dakika', '5 dakika önce'),
        ('15_dakika', '15 dakika önce'),
        ('30_dakika', '30 dakika önce'),
        ('1_saat', '1 saat önce'),
        ('1_gun', '1 gün önce')
    ], validators=[Optional()])
    submit = SubmitField('Kaydet')

    def validate_bitis_tarihi(self, field):
        """Bitiş tarihinin başlangıç tarihinden sonra olmasını kontrol eder"""
        if self.baslangic_tarihi.data and field.data:
            if field.data < self.baslangic_tarihi.data:
                raise ValidationError('Bitiş tarihi başlangıç tarihinden önce olamaz')

    def validate_bitis_saati(self, field):
        """Bitiş saatinin başlangıç saatinden sonra olmasını kontrol eder"""
        if self.baslangic_tarihi.data and self.bitis_tarihi.data and self.baslangic_saati.data and field.data:
            if self.baslangic_tarihi.data == self.bitis_tarihi.data and field.data <= self.baslangic_saati.data:
                raise ValidationError('Bitiş saati başlangıç saatinden sonra olmalıdır')

class GundemForm(FlaskForm):
    """Gündem maddesi oluşturma/düzenleme formu"""
    baslik = StringField('Başlık', validators=[
        DataRequired(message='Başlık gereklidir'),
        Length(min=3, max=200, message='Başlık 3-200 karakter arasında olmalıdır')
    ])
    aciklama = TextAreaField('Açıklama', validators=[Optional()])
    hedef = TextAreaField('Hedef', validators=[Optional()])
    sure = IntegerField('Süre (dakika)', validators=[Optional()])
    sira = IntegerField('Sıra', validators=[Optional()])
    toplanti_id = HiddenField('Toplantı ID')
    submit = SubmitField('Kaydet')

class NotForm(FlaskForm):
    """Not ekleme formu"""
    icerik = TextAreaField('İçerik', validators=[
        DataRequired(message='İçerik gereklidir')
    ])
    gundem_maddesi_id = HiddenField('Gündem Maddesi ID')
    submit = SubmitField('Kaydet')

class GorevForm(FlaskForm):
    """Görev oluşturma/düzenleme formu"""
    baslik = StringField('Başlık', validators=[
        DataRequired(message='Başlık gereklidir'),
        Length(min=3, max=200, message='Başlık 3-200 karakter arasında olmalıdır')
    ])
    aciklama = TextAreaField('Açıklama', validators=[Optional()])
    atanan_kullanici_id = SelectField('Atanan Kişi', coerce=int, validators=[
        DataRequired(message='Atanan kişi gereklidir')
    ])
    son_teslim_tarihi = DateField('Son Teslim Tarihi', format='%Y-%m-%d', validators=[
        DataRequired(message='Son teslim tarihi gereklidir')
    ])
    oncelik = SelectField('Öncelik', choices=[
        ('Düşük', 'Düşük'),
        ('Normal', 'Normal'),
        ('Yüksek', 'Yüksek'),
        ('Acil', 'Acil')
    ], validators=[DataRequired(message='Öncelik gereklidir')])
    durum = SelectField('Durum', choices=[
        ('Yapılacak', 'Yapılacak'),
        ('Devam Ediyor', 'Devam Ediyor'),
        ('Tamamlandı', 'Tamamlandı')
    ], validators=[DataRequired(message='Durum gereklidir')])
    puan_degeri = IntegerField('Puan Değeri', validators=[Optional()])
    toplanti_id = SelectField('İlgili Toplantı', coerce=int, validators=[Optional()], choices=[])
    urun_id = SelectField('İlgili Ürün', coerce=int, validators=[Optional()], choices=[])
    submit = SubmitField('Kaydet')

    def __init__(self, *args, **kwargs):
        super(GorevForm, self).__init__(*args, **kwargs)
        # Toplantı ve ürün seçenekleri dinamik olarak doldurulacak
        self.toplanti_id.choices = [(0, 'Seçiniz...')] + kwargs.get('toplanti_choices', [])
        self.urun_id.choices = [(0, 'Seçiniz...')] + kwargs.get('urun_choices', [])
        self.atanan_kullanici_id.choices = kwargs.get('kullanici_choices', [])

class GorevDurumForm(FlaskForm):
    """Görev durumu güncelleme formu"""
    durum = SelectField('Durum', choices=[
        ('Yapılacak', 'Yapılacak'),
        ('Devam Ediyor', 'Devam Ediyor'),
        ('Tamamlandı', 'Tamamlandı')
    ], validators=[DataRequired(message='Durum gereklidir')])
    submit = SubmitField('Güncelle')

class GorevYorumForm(FlaskForm):
    """Görev yorumu ekleme formu"""
    yorum = TextAreaField('Yorum', validators=[
        DataRequired(message='Yorum gereklidir')
    ])
    submit = SubmitField('Yorum Ekle')

class DosyaYukleForm(FlaskForm):
    """Dosya yükleme formu"""
    dosya = FileField('Dosya', validators=[
        DataRequired(message='Dosya gereklidir')
    ])
    aciklama = TextAreaField('Açıklama', validators=[Optional()])
    submit = SubmitField('Yükle')

class UrunForm(FlaskForm):
    """Ürün oluşturma/düzenleme formu"""
    kod = StringField('Ürün Kodu', validators=[
        DataRequired(message='Ürün kodu gereklidir'),
        Length(min=2, max=50, message='Ürün kodu 2-50 karakter arasında olmalıdır')
    ])
    ad = StringField('Ürün Adı', validators=[
        DataRequired(message='Ürün adı gereklidir'),
        Length(min=3, max=200, message='Ürün adı 3-200 karakter arasında olmalıdır')
    ])
    aciklama = TextAreaField('Açıklama', validators=[Optional()])
    kategori_id = SelectField('Kategori', coerce=int, validators=[
        DataRequired(message='Kategori gereklidir')
    ])
    fiyat = FloatField('Fiyat', validators=[Optional()])
    stok_miktari = IntegerField('Stok Miktarı', validators=[Optional()])
    durum = SelectField('Durum', choices=[
        ('Aktif', 'Aktif'),
        ('Pasif', 'Pasif')
    ], validators=[DataRequired(message='Durum gereklidir')])
    submit = SubmitField('Kaydet')

    def __init__(self, *args, **kwargs):
        super(UrunForm, self).__init__(*args, **kwargs)
        # Kategori seçenekleri dinamik olarak doldurulacak
        self.kategori_id.choices = kwargs.get('kategori_choices', [])

class UrunGorselForm(FlaskForm):
    """Ürün görseli yükleme formu"""
    gorsel = FileField('Görsel', validators=[
        DataRequired(message='Görsel gereklidir'),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Sadece resim dosyaları yüklenebilir')
    ])
    submit = SubmitField('Yükle')

class KategoriForm(FlaskForm):
    """Kategori oluşturma/düzenleme formu"""
    ad = StringField('Kategori Adı', validators=[
        DataRequired(message='Kategori adı gereklidir'),
        Length(min=2, max=100, message='Kategori adı 2-100 karakter arasında olmalıdır')
    ])
    aciklama = TextAreaField('Açıklama', validators=[Optional()])
    submit = SubmitField('Kaydet')

class RaporFilterForm(FlaskForm):
    """Rapor filtreleme formu"""
    baslangic_tarihi = DateField('Başlangıç Tarihi', format='%Y-%m-%d', validators=[
        DataRequired(message='Başlangıç tarihi gereklidir')
    ])
    bitis_tarihi = DateField('Bitiş Tarihi', format='%Y-%m-%d', validators=[
        DataRequired(message='Bitiş tarihi gereklidir')
    ])
    kullanici_id = SelectField('Kullanıcı', coerce=int, validators=[Optional()])
    submit = SubmitField('Filtrele')

    def __init__(self, *args, **kwargs):
        super(RaporFilterForm, self).__init__(*args, **kwargs)
        # Kullanıcı seçenekleri dinamik olarak doldurulacak
        self.kullanici_id.choices = [(0, 'Tüm Kullanıcılar')] + kwargs.get('kullanici_choices', [])

    def validate_bitis_tarihi(self, field):
        """Bitiş tarihinin başlangıç tarihinden sonra olmasını kontrol eder"""
        if self.baslangic_tarihi.data and field.data:
            if field.data < self.baslangic_tarihi.data:
                raise ValidationError('Bitiş tarihi başlangıç tarihinden önce olamaz')

class BildirimAyarForm(FlaskForm):
    """Bildirim ayarları formu"""
    toplanti_davet = BooleanField('Toplantı Davetleri')
    toplanti_guncelleme = BooleanField('Toplantı Güncellemeleri')
    toplanti_iptal = BooleanField('Toplantı İptalleri')
    toplanti_hatirlatma = BooleanField('Toplantı Hatırlatmaları')
    gorev_atama = BooleanField('Görev Atamaları')
    gorev_guncelleme = BooleanField('Görev Güncellemeleri')
    gorev_tamamlama = BooleanField('Görev Tamamlamaları')
    gorev_hatirlatma = BooleanField('Görev Hatırlatmaları')
    yorum_ekleme = BooleanField('Yorum Eklemeleri')
    eposta_bildirim = BooleanField('E-posta Bildirimleri')
    submit = SubmitField('Kaydet')

class KatilimciEkleForm(FlaskForm):
    """Toplantıya katılımcı ekleme formu"""
    katilimcilar = SelectField('Kullanıcılar', coerce=int, validators=[Optional()])
    misafir_katilimcilar = TextAreaField('Misafir Katılımcılar (E-posta)', validators=[Optional()])
    submit = SubmitField('Ekle')

    def __init__(self, *args, **kwargs):
        super(KatilimciEkleForm, self).__init__(*args, **kwargs)
        # Kullanıcı seçenekleri dinamik olarak doldurulacak
        self.katilimcilar.choices = kwargs.get('kullanici_choices', [])

class AIForm(FlaskForm):
    """AI özellikleri için form"""
    toplanti_id = SelectField('Toplantı', coerce=int, validators=[
        DataRequired(message='Toplantı gereklidir')
    ])
    submit = SubmitField('Oluştur')

    def __init__(self, *args, **kwargs):
        super(AIForm, self).__init__(*args, **kwargs)
        # Toplantı seçenekleri dinamik olarak doldurulacak
        self.toplanti_id.choices = kwargs.get('toplanti_choices', [])

class AIAssistantForm(FlaskForm):
    """AI asistanı için form"""
    soru = TextAreaField('Soru', validators=[
        DataRequired(message='Soru gereklidir')
    ])
    submit = SubmitField('Sor')
