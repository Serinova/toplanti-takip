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

@app.route("/api/gorev-sil/<int:gorev_id>", methods=["DELETE"])
def gorev_sil(gorev_id):
    global gorevler
    gorevler = [g for g in gorevler if g["id"] != gorev_id]
    return jsonify({"durum": "silindi", "id": gorev_id})

@app.route("/api/gorev-tamamla/<int:gorev_id>", methods=["PUT"])
def gorev_tamamla(gorev_id):
    for g in gorevler:
        if g["id"] == gorev_id:
            g["tamamlandi"] = not g["tamamlandi"]
            return jsonify({"durum": "güncellendi", "gorev": g})
    return jsonify({"hata": "görev bulunamadı"}), 404

@app.route("/")
def home():
    return "Hello, Render!"

if __name__ == "__main__":
    app.run()