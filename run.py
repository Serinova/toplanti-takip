from flask import Flask

app = Flask(__name__)

from flask import Flask, request, jsonify

app = Flask(__name__)

gorevler = []

@app.route("/api/gorevler", methods=["GET"])
def gorevleri_listele():
    return jsonify(gorevler)

@app.route("/api/gorev-ekle", methods=["POST"])
def gorev_ekle():
    data = request.get_json()
    yeni_gorev = {
        "id": len(gorevler) + 1,
        "baslik": data.get("baslik"),
        "aciklama": data.get("aciklama"),
        "tamamlandi": False
    }
    gorevler.append(yeni_gorev)
    return jsonify({"durum": "eklendi", "gorev": yeni_gorev})