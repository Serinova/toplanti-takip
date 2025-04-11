from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gorevler.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Gorev(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(100))
    aciklama = db.Column(db.String(200))
    tamamlandi = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route("/api/gorevler", methods=["GET"])
def listele():
    return jsonify([{
        "id": g.id,
        "baslik": g.baslik,
        "aciklama": g.aciklama,
        "tamamlandi": g.tamamlandi
    } for g in Gorev.query.all()])

@app.route("/api/gorev-ekle", methods=["POST"])
def ekle():
    data = request.get_json()
    yeni = Gorev(baslik=data["baslik"], aciklama=data["aciklama"])
    db.session.add(yeni)
    db.session.commit()
    return jsonify({"id": yeni.id})

@app.route("/api/gorev-sil/<int:id>", methods=["DELETE"])
def sil(id):
    g = Gorev.query.get(id)
    if g:
        db.session.delete(g)
        db.session.commit()
        return jsonify({"durum": "silindi"})
    return jsonify({"hata": "bulunamadı"})

@app.route("/api/gorev-tamamla/<int:id>", methods=["PUT"])
def tamamla(id):
    g = Gorev.query.get(id)
    if g:
        g.tamamlandi = not g.tamamlandi
        db.session.commit()
        return jsonify({"durum": "güncellendi"})
    return jsonify({"hata": "bulunamadı"})

@app.route("/")
def home():
    return "Görev Takip API (Veritabanlı)"

class Toplanti(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(100), nullable=False)
    aciklama = db.Column(db.String(200))
    tarih_saat = db.Column(db.String(50))  # ISO tarih formatı beklenebilir

with app.app_context():
    db.create_all()
@app.route("/api/toplanti-ekle", methods=["POST"])
def toplanti_ekle():
    data = request.get_json()
    yeni = Toplanti(
        baslik=data.get("baslik"),
        aciklama=data.get("aciklama"),
        tarih_saat=data.get("tarih_saat")
    )
    db.session.add(yeni)
    db.session.commit()
    return jsonify({"durum": "toplanti eklendi", "id": yeni.id})

@app.route("/api/toplantilar", methods=["GET"])
def toplanti_listele():
    toplantilar = Toplanti.query.order_by(Toplanti.tarih_saat).all()
    return jsonify([{
        "id": t.id,
        "baslik": t.baslik,
        "aciklama": t.aciklama,
        "tarih_saat": t.tarih_saat
    } for t in toplantilar])