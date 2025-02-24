from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

app = Flask(__name__)

# Ganti dengan URL MongoDB Atlas kamu
MONGO_URI = "mongodb+srv://nabil:123@cluster0.vco9w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")  # Tes koneksi ke MongoDB
    db = client["wokwo"]  # Nama database
    collection = db["wokwi"]  # Nama koleksi
    print("Koneksi ke MongoDB berhasil!")
except ConnectionFailure:
    print("Koneksi ke MongoDB gagal!")
    collection = None  # Pastikan collection tetap None jika gagal

@app.route('/')
def home():
    return "Flask API berjalan!"

@app.route('/sensor', methods=['POST'])
def receive_data():
    global collection  # Pastikan menggunakan variabel global

    if collection is None:
        return jsonify({"error": "Database tidak terhubung!"}), 500

    data = request.json  # Terima data dari ESP32
    if data:
        try:
            collection.insert_one(data)  # Simpan ke MongoDB
            return jsonify({"message": "Data berhasil disimpan!"}), 201
        except Exception as e:
            return jsonify({"error": f"Gagal menyimpan data: {e}"}), 500
    return jsonify({"error": "Data tidak valid!"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)