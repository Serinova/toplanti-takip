from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import current_user, login_required
from app.models import Toplanti, Gorev, Kullanici, Urun
from app import db
from datetime import datetime, timedelta
import json
from app.services.rapor_service import generate_toplanti_raporu, generate_gorev_raporu, generate_kullanici_raporu

rapor_bp = Blueprint('rapor', __name__, url_prefix='/rapor')

# Web arayüzü rotaları
@rapor_bp.route('/')
@login_required
def dashboard():
    """Rapor dashboard sayfası."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        flash('Bu sayfaya erişim izniniz yok', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Toplantı istatistikleri
    toplanti_sayisi = Toplanti.query.count()
    aktif_toplanti_sayisi = Toplanti.query.filter_by(iptal_edildi=False).count()
    iptal_edilen_toplanti_sayisi = Toplanti.query.filter_by(iptal_edildi=True).count()
    
    # Görev istatistikleri
    gorev_sayisi = Gorev.query.count()
    tamamlanan_gorev_sayisi = Gorev.query.filter_by(durum='Tamamlandı').count()
    devam_eden_gorev_sayisi = Gorev.query.filter_by(durum='Devam Ediyor').count()
    yapilacak_gorev_sayisi = Gorev.query.filter_by(durum='Yapılacak').count()
    
    # Kullanıcı istatistikleri
    kullanici_sayisi = Kullanici.query.count()
    admin_sayisi = Kullanici.query.filter_by(rol='admin').count()
    normal_kullanici_sayisi = Kullanici.query.filter_by(rol='normal').count()
    
    # Ürün istatistikleri
    urun_sayisi = Urun.query.count()
    
    return render_template('rapor/dashboard.html',
                          toplanti_sayisi=toplanti_sayisi,
                          aktif_toplanti_sayisi=aktif_toplanti_sayisi,
                          iptal_edilen_toplanti_sayisi=iptal_edilen_toplanti_sayisi,
                          gorev_sayisi=gorev_sayisi,
                          tamamlanan_gorev_sayisi=tamamlanan_gorev_sayisi,
                          devam_eden_gorev_sayisi=devam_eden_gorev_sayisi,
                          yapilacak_gorev_sayisi=yapilacak_gorev_sayisi,
                          kullanici_sayisi=kullanici_sayisi,
                          admin_sayisi=admin_sayisi,
                          normal_kullanici_sayisi=normal_kullanici_sayisi,
                          urun_sayisi=urun_sayisi)

@rapor_bp.route('/toplanti')
@login_required
def toplanti():
    """Toplantı raporu sayfası."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        flash('Bu sayfaya erişim izniniz yok', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Son 30 günlük toplantılar
    baslangic_tarihi = datetime.utcnow() - timedelta(days=30)
    bitis_tarihi = datetime.utcnow()
    
    # Rapor verilerini oluştur
    rapor_verileri = generate_toplanti_raporu(baslangic_tarihi, bitis_tarihi)
    
    return render_template('rapor/toplanti.html',
                          rapor_verileri=rapor_verileri,
                          baslangic_tarihi=baslangic_tarihi,
                          bitis_tarihi=bitis_tarihi)

@rapor_bp.route('/gorev')
@login_required
def gorev():
    """Görev raporu sayfası."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        flash('Bu sayfaya erişim izniniz yok', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Son 30 günlük görevler
    baslangic_tarihi = datetime.utcnow() - timedelta(days=30)
    bitis_tarihi = datetime.utcnow()
    
    # Rapor verilerini oluştur
    rapor_verileri = generate_gorev_raporu(baslangic_tarihi, bitis_tarihi)
    
    return render_template('rapor/gorev.html',
                          rapor_verileri=rapor_verileri,
                          baslangic_tarihi=baslangic_tarihi,
                          bitis_tarihi=bitis_tarihi)

@rapor_bp.route('/kullanici')
@login_required
def kullanici():
    """Kullanıcı raporu sayfası."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        flash('Bu sayfaya erişim izniniz yok', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Rapor verilerini oluştur
    rapor_verileri = generate_kullanici_raporu()
    
    return render_template('rapor/kullanici.html',
                          rapor_verileri=rapor_verileri)

@rapor_bp.route('/ozel', methods=['GET', 'POST'])
@login_required
def ozel():
    """Özel rapor oluşturma sayfası."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        flash('Bu sayfaya erişim izniniz yok', 'danger')
        return redirect(url_for('dashboard.index'))
    
    from app.forms.rapor_forms import OzelRaporForm
    
    form = OzelRaporForm()
    if form.validate_on_submit():
        rapor_tipi = form.rapor_tipi.data
        baslangic_tarihi = form.baslangic_tarihi.data
        bitis_tarihi = form.bitis_tarihi.data
        
        if rapor_tipi == 'toplanti':
            rapor_verileri = generate_toplanti_raporu(baslangic_tarihi, bitis_tarihi)
            return render_template('rapor/toplanti.html',
                                  rapor_verileri=rapor_verileri,
                                  baslangic_tarihi=baslangic_tarihi,
                                  bitis_tarihi=bitis_tarihi)
        elif rapor_tipi == 'gorev':
            rapor_verileri = generate_gorev_raporu(baslangic_tarihi, bitis_tarihi)
            return render_template('rapor/gorev.html',
                                  rapor_verileri=rapor_verileri,
                                  baslangic_tarihi=baslangic_tarihi,
                                  bitis_tarihi=bitis_tarihi)
    
    return render_template('rapor/ozel.html', form=form)

# API rotaları
@rapor_bp.route('/api/dashboard', methods=['GET'])
@login_required
def api_dashboard():
    """API rapor dashboard endpoint'i."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        return jsonify({'message': 'Bu işlem için yetkiniz yok', 'success': False}), 403
    
    # Toplantı istatistikleri
    toplanti_sayisi = Toplanti.query.count()
    aktif_toplanti_sayisi = Toplanti.query.filter_by(iptal_edildi=False).count()
    iptal_edilen_toplanti_sayisi = Toplanti.query.filter_by(iptal_edildi=True).count()
    
    # Görev istatistikleri
    gorev_sayisi = Gorev.query.count()
    tamamlanan_gorev_sayisi = Gorev.query.filter_by(durum='Tamamlandı').count()
    devam_eden_gorev_sayisi = Gorev.query.filter_by(durum='Devam Ediyor').count()
    yapilacak_gorev_sayisi = Gorev.query.filter_by(durum='Yapılacak').count()
    
    # Kullanıcı istatistikleri
    kullanici_sayisi = Kullanici.query.count()
    admin_sayisi = Kullanici.query.filter_by(rol='admin').count()
    normal_kullanici_sayisi = Kullanici.query.filter_by(rol='normal').count()
    
    # Ürün istatistikleri
    urun_sayisi = Urun.query.count()
    
    return jsonify({
        'toplanti_istatistikleri': {
            'toplanti_sayisi': toplanti_sayisi,
            'aktif_toplanti_sayisi': aktif_toplanti_sayisi,
            'iptal_edilen_toplanti_sayisi': iptal_edilen_toplanti_sayisi
        },
        'gorev_istatistikleri': {
            'gorev_sayisi': gorev_sayisi,
            'tamamlanan_gorev_sayisi': tamamlanan_gorev_sayisi,
            'devam_eden_gorev_sayisi': devam_eden_gorev_sayisi,
            'yapilacak_gorev_sayisi': yapilacak_gorev_sayisi
        },
        'kullanici_istatistikleri': {
            'kullanici_sayisi': kullanici_sayisi,
            'admin_sayisi': admin_sayisi,
            'normal_kullanici_sayisi': normal_kullanici_sayisi
        },
        'urun_istatistikleri': {
            'urun_sayisi': urun_sayisi
        }
    }), 200

@rapor_bp.route('/api/toplanti-raporu', methods=['GET'])
@login_required
def api_toplanti_raporu():
    """API toplantı raporu endpoint'i."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        return jsonify({'message': 'Bu işlem için yetkiniz yok', 'success': False}), 403
    
    # Tarih parametrelerini al
    try:
        baslangic_tarihi = datetime.fromisoformat(request.args.get('baslangic_tarihi', (datetime.utcnow() - timedelta(days=30)).isoformat()))
        bitis_tarihi = datetime.fromisoformat(request.args.get('bitis_tarihi', datetime.utcnow().isoformat()))
    except ValueError:
        return jsonify({'message': 'Geçersiz tarih formatı', 'success': False}), 400
    
    # Rapor verilerini oluştur
    rapor_verileri = generate_toplanti_raporu(baslangic_tarihi, bitis_tarihi)
    
    return jsonify({
        'rapor_verileri': rapor_verileri,
        'baslangic_tarihi': baslangic_tarihi.isoformat(),
        'bitis_tarihi': bitis_tarihi.isoformat()
    }), 200

@rapor_bp.route('/api/gorev-raporu', methods=['GET'])
@login_required
def api_gorev_raporu():
    """API görev raporu endpoint'i."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        return jsonify({'message': 'Bu işlem için yetkiniz yok', 'success': False}), 403
    
    # Tarih parametrelerini al
    try:
        baslangic_tarihi = datetime.fromisoformat(request.args.get('baslangic_tarihi', (datetime.utcnow() - timedelta(days=30)).isoformat()))
        bitis_tarihi = datetime.fromisoformat(request.args.get('bitis_tarihi', datetime.utcnow().isoformat()))
    except ValueError:
        return jsonify({'message': 'Geçersiz tarih formatı', 'success': False}), 400
    
    # Rapor verilerini oluştur
    rapor_verileri = generate_gorev_raporu(baslangic_tarihi, bitis_tarihi)
    
    return jsonify({
        'rapor_verileri': rapor_verileri,
        'baslangic_tarihi': baslangic_tarihi.isoformat(),
        'bitis_tarihi': bitis_tarihi.isoformat()
    }), 200

@rapor_bp.route('/api/kullanici-raporu', methods=['GET'])
@login_required
def api_kullanici_raporu():
    """API kullanıcı raporu endpoint'i."""
    # Admin kontrolü
    if current_user.rol != 'admin':
        return jsonify({'message': 'Bu işlem için yetkiniz yok', 'success': False}), 403
    
    # Rapor verilerini oluştur
    rapor_verileri = generate_kullanici_raporu()
    
    return jsonify({
        'rapor_verileri': rapor_verileri
    }), 200
