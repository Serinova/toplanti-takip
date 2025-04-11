from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models.toplanti import Toplanti
from app.models.gundem import Gundem
from app.models.not_dosya import Not
from app.models.gorev import Gorev
from app.services.ai_service import AIService
from app.forms import AIAssistantForm
from app.extensions import db

ai_bp = Blueprint('ai', __name__)
ai_service = AIService()

@ai_bp.route('/ai-features', methods=['GET'])
@login_required
def ai_features():
    """AI özellikleri sayfası"""
    return render_template('ai/ai_features.html')

@ai_bp.route('/toplanti-ozeti/<int:toplanti_id>', methods=['GET'])
@login_required
def toplanti_ozeti(toplanti_id):
    """Toplantı özetleme sayfası"""
    toplanti = Toplanti.query.get_or_404(toplanti_id)
    
    # Kullanıcının bu toplantıya erişim yetkisi var mı kontrol et
    if not toplanti.kullanici_erisimi_var_mi(current_user.id):
        return render_template('errors/403.html'), 403
    
    # Özet oluşturma isteği
    if request.args.get('generate') == 'true':
        sonuc = ai_service.toplanti_ozetle(toplanti_id)
        return jsonify(sonuc)
    
    return render_template('ai/toplanti_ozeti.html', toplanti=toplanti)

@ai_bp.route('/gorev-cikar/<int:toplanti_id>', methods=['GET'])
@login_required
def gorev_cikar(toplanti_id):
    """Toplantıdan görev çıkarma sayfası"""
    toplanti = Toplanti.query.get_or_404(toplanti_id)
    
    # Kullanıcının bu toplantıya erişim yetkisi var mı kontrol et
    if not toplanti.kullanici_erisimi_var_mi(current_user.id):
        return render_template('errors/403.html'), 403
    
    # Görev çıkarma isteği
    if request.args.get('generate') == 'true':
        sonuc = ai_service.gorev_cikar(toplanti_id)
        return jsonify(sonuc)
    
    return render_template('ai/gorev_cikar.html', toplanti=toplanti)

@ai_bp.route('/ai-asistan', methods=['GET', 'POST'])
@login_required
def ai_asistan_view():
    """Yapay zeka asistanı sayfası"""
    form = AIAssistantForm()
    cevap = None
    
    if form.validate_on_submit():
        sonuc = ai_service.ai_asistan(form.soru.data)
        if sonuc['success']:
            cevap = sonuc['answer']
        else:
            cevap = "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."
    
    return render_template('ai/ai_asistan.html', form=form, cevap=cevap)
