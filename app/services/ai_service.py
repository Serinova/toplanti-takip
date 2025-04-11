from app.extensions import current_app
import openai
import os
from datetime import datetime
import json
import re

class AIService:
    """Yapay zeka servisi"""
    
    def __init__(self):
        """OpenAI API anahtarını yapılandır"""
        self.api_key = os.environ.get('OPENAI_API_KEY', 'dummy_key_for_development')
        openai.api_key = self.api_key
    
    def toplanti_ozetle(self, toplanti_id):
        """Toplantı notlarını özetler"""
        from app.models.toplanti import Toplanti
        from app.models.gundem import Gundem
        from app.models.not_dosya import Not
        
        # Toplantı ve notları getir
        toplanti = Toplanti.query.get_or_404(toplanti_id)
        gundem_maddeleri = Gundem.query.filter_by(toplanti_id=toplanti_id).all()
        
        # Tüm notları birleştir
        tum_notlar = []
        for gundem in gundem_maddeleri:
            notlar = Not.query.filter_by(gundem_id=gundem.id).all()
            if notlar:
                tum_notlar.append(f"Gündem: {gundem.baslik}")
                for not_item in notlar:
                    tum_notlar.append(f"- {not_item.icerik}")
        
        if not tum_notlar:
            return {"success": False, "error": "Toplantıda özet oluşturmak için yeterli not bulunmuyor."}
        
        # OpenAI API'yi kullanarak özet oluştur
        try:
            prompt = f"""
            Aşağıdaki toplantı notlarını özetle:
            
            Toplantı: {toplanti.baslik}
            Tarih: {toplanti.baslangic_zamani.strftime('%d.%m.%Y')}
            
            {"".join(tum_notlar)}
            
            Lütfen toplantının ana noktalarını, alınan kararları ve önemli tartışmaları içeren kısa bir özet oluştur.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen profesyonel bir toplantı asistanısın. Toplantı notlarını özetleyerek ana noktaları, kararları ve önemli tartışmaları vurgulayacaksın."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            
            ozet = response.choices[0].message.content.strip()
            return {"success": True, "summary": ozet}
        
        except Exception as e:
            print(f"OpenAI API hatası: {str(e)}")
            # Geliştirme ortamında test için sahte yanıt
            if os.environ.get('FLASK_ENV') == 'development':
                return {
                    "success": True, 
                    "summary": "Bu bir test özetidir. Gerçek API bağlantısı olmadan oluşturulmuştur. Toplantıda alınan kararlar ve önemli noktalar burada özetlenecektir."
                }
            return {"success": False, "error": "Özet oluşturulurken bir hata oluştu."}
    
    def gorev_cikar(self, toplanti_id):
        """Toplantı notlarından görevleri çıkarır"""
        from app.models.toplanti import Toplanti
        from app.models.gundem import Gundem
        from app.models.not_dosya import Not
        
        # Toplantı ve notları getir
        toplanti = Toplanti.query.get_or_404(toplanti_id)
        gundem_maddeleri = Gundem.query.filter_by(toplanti_id=toplanti_id).all()
        
        # Tüm notları birleştir
        tum_notlar = []
        for gundem in gundem_maddeleri:
            notlar = Not.query.filter_by(gundem_id=gundem.id).all()
            if notlar:
                tum_notlar.append(f"Gündem: {gundem.baslik}")
                for not_item in notlar:
                    tum_notlar.append(f"- {not_item.icerik}")
        
        if not tum_notlar:
            return {"success": False, "error": "Toplantıda görev çıkarmak için yeterli not bulunmuyor."}
        
        # OpenAI API'yi kullanarak görevleri çıkar
        try:
            prompt = f"""
            Aşağıdaki toplantı notlarından görevleri çıkar:
            
            Toplantı: {toplanti.baslik}
            Tarih: {toplanti.baslangic_zamani.strftime('%d.%m.%Y')}
            
            {"".join(tum_notlar)}
            
            Lütfen toplantı notlarından çıkarılabilecek görevleri JSON formatında listele. Her görev için başlık ve açıklama içermelidir.
            Örnek format:
            [
                {{"title": "Görev başlığı 1", "description": "Görev açıklaması 1"}},
                {{"title": "Görev başlığı 2", "description": "Görev açıklaması 2"}}
            ]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen profesyonel bir toplantı asistanısın. Toplantı notlarından görevleri çıkararak JSON formatında listeleyeceksin."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            gorev_metni = response.choices[0].message.content.strip()
            
            # JSON formatını ayıkla
            json_match = re.search(r'\[\s*\{.*\}\s*\]', gorev_metni, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                gorevler = json.loads(json_str)
            else:
                # Alternatif olarak tüm metni JSON olarak parse etmeyi dene
                try:
                    gorevler = json.loads(gorev_metni)
                except:
                    # Geliştirme ortamında test için sahte yanıt
                    if os.environ.get('FLASK_ENV') == 'development':
                        return {
                            "success": True, 
                            "tasks": [
                                {"title": "Test Görevi 1", "description": "Bu bir test görevidir."},
                                {"title": "Test Görevi 2", "description": "Bu başka bir test görevidir."}
                            ]
                        }
                    return {"success": False, "error": "Görevler JSON formatında çıkarılamadı."}
            
            return {"success": True, "tasks": gorevler}
        
        except Exception as e:
            print(f"OpenAI API hatası: {str(e)}")
            # Geliştirme ortamında test için sahte yanıt
            if os.environ.get('FLASK_ENV') == 'development':
                return {
                    "success": True, 
                    "tasks": [
                        {"title": "Test Görevi 1", "description": "Bu bir test görevidir."},
                        {"title": "Test Görevi 2", "description": "Bu başka bir test görevidir."}
                    ]
                }
            return {"success": False, "error": "Görevler çıkarılırken bir hata oluştu."}
    
    def ai_asistan(self, soru):
        """Yapay zeka asistanı ile soru-cevap"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen Toplantı Takip Programı'nın yapay zeka asistanısın. Kullanıcılara toplantılar, görevler, projeler ve iş yönetimi konularında yardımcı oluyorsun."},
                    {"role": "user", "content": soru}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            cevap = response.choices[0].message.content.strip()
            return {"success": True, "answer": cevap}
        
        except Exception as e:
            print(f"OpenAI API hatası: {str(e)}")
            # Geliştirme ortamında test için sahte yanıt
            if os.environ.get('FLASK_ENV') == 'development':
                return {
                    "success": True, 
                    "answer": f"Bu bir test yanıtıdır. Gerçek API bağlantısı olmadan oluşturulmuştur. Sorunuz: {soru}"
                }
            return {"success": False, "error": "Cevap oluşturulurken bir hata oluştu."}
