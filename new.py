import streamlit as st
from pymongo import MongoClient
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
from datetime import datetime
import numpy as np

# Konfigurasi halaman
st.set_page_config(page_title="Monitoring Artikel Kesehatan Ayam", layout="wide")

st.title("Monitoring Artikel Kesehatan Ayam dari PoultryIndonesia")

# Koneksi ke MongoDB
client = MongoClient("mongodb+srv://alvinmasterl4d2:fHyKAXo8pdZTB4sL@cluster0.knwgtz8.mongodb.net/monitoring_ayam?retryWrites=true&w=majority")
db = client["monitoring_ayam"]
collection = db["berita_kesehatan_poultryindonesia"]

# Daftar keyword untuk visualisasi stacked bar
keywords = ["penyakit", "disease", "virus", "Diagnosis"]

# Inisialisasi struktur data
artikel_per_tahun_keyword = defaultdict(lambda: defaultdict(int))
total_artikel_per_tahun = defaultdict(int)
keyword_counter = Counter()

documents = collection.find()

for doc in documents:
    judul = doc.get("judul", "").lower()
    tanggal = doc.get("tanggal", "")

    try:
        tahun = datetime.strptime(tanggal, "%d %B %Y").year
    except:
        continue

    total_artikel_per_tahun[tahun] += 1
    keyword_terdeteksi = False

    for keyword in keywords:
        if keyword.lower() in judul:
            artikel_per_tahun_keyword[tahun][keyword] += 1
            keyword_counter[keyword.lower()] += 1
            keyword_terdeteksi = True

    if not keyword_terdeteksi:
        artikel_per_tahun_keyword[tahun]["lainnya"] += 1

# Tambahkan 'lainnya' ke dalam daftar keywords terakhir
keywords_dengan_lainnya = keywords + ["lainnya"]
colors = ['orange', 'skyblue', 'green', 'red', 'blue','gray']

# === Grafik 1: Stacked Bar Artikel Berdasarkan Keyword ===
st.subheader("📊 Jumlah Artikel per Tahun berdasarkan Keyword dan Lainnya")

tahun_list = sorted(total_artikel_per_tahun.keys())
n_tahun = len(tahun_list)
n_keywords = len(keywords_dengan_lainnya)
bar_width = 0.15
x = np.arange(n_tahun)

fig1, ax1 = plt.subplots(figsize=(16, 6))

for i, keyword in enumerate(keywords_dengan_lainnya):
    jumlah_per_keyword = [artikel_per_tahun_keyword[tahun][keyword] for tahun in tahun_list]
    ax1.bar(x + i * bar_width, jumlah_per_keyword, width=bar_width, label=keyword.capitalize(), color=colors[i])

ax1.set_xlabel("Tahun")
ax1.set_ylabel("Jumlah Artikel")
ax1.set_title("Jumlah Artikel per Tahun berdasarkan Keyword dan Lainnya")
ax1.set_xticks(x + bar_width * (n_keywords - 1) / 2)
ax1.set_xticklabels(tahun_list)
ax1.legend()
plt.tight_layout()
st.pyplot(fig1)

# === Grafik 2: Top 4 Keyword Paling Sering Muncul ===
st.subheader("🏷️ 4 Keyword Terpopuler dalam Judul Artikel per Tahun")

# Kumpulkan top 4 keyword dari judul untuk setiap tahun
tahun_top_keywords = {}
for tahun in tahun_list:
    counter = Counter()
    for doc in collection.find():
        judul = doc.get("judul", "").lower()
        tanggal = doc.get("tanggal", "")
        try:
            doc_tahun = datetime.strptime(tanggal, "%d %B %Y").year
        except:
            continue
        if doc_tahun == tahun:
            for word in judul.split():
                counter[word] += 1
    top4 = counter.most_common(4)
    tahun_top_keywords[tahun] = top4

# Buat visualisasi
fig2, ax2 = plt.subplots(figsize=(16, 6))

bar_width = 0.15
x = np.arange(len(tahun_list))

for i in range(4):
    label = f"Top {i+1}"
    values = []
    labels = []
    for tahun in tahun_list:
        if i < len(tahun_top_keywords[tahun]):
            word, count = tahun_top_keywords[tahun][i]
            values.append(count)
            labels.append(word)
        else:
            values.append(0)
            labels.append("")
    bars = ax2.bar(x + i * bar_width, values, width=bar_width, label=label)

    # Tambahkan label kata kunci di atas setiap bar
    for bar, keyword in zip(bars, labels):
        height = bar.get_height()
        if keyword:
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.5,
                keyword,
                ha='center',
                va='bottom',
                fontsize=9,
                rotation=90  # Rotasi agar lebih mudah dibaca jika panjang
            )

ax2.set_xlabel("Tahun")
ax2.set_ylabel("Frekuensi Kemunculan")
ax2.set_title("Top 4 Keyword Terpopuler dalam Judul Artikel per Tahun")
ax2.set_xticks(x + bar_width * 1.5)
ax2.set_xticklabels(tahun_list)
ax2.legend(title="Peringkat")
plt.tight_layout()
st.pyplot(fig2)

# === Grafik 3: Histogram Jumlah Artikel per Tahun ===
st.subheader("📅 Jumlah Artikel per Tahun")

fig3, ax3 = plt.subplots(figsize=(10, 5))
tahun_keys = sorted(total_artikel_per_tahun.keys())
jumlah_artikel = [total_artikel_per_tahun[t] for t in tahun_keys]
ax3.bar(tahun_keys, jumlah_artikel, color='coral')
ax3.set_ylabel("Jumlah Artikel")
ax3.set_xlabel("Tahun")
ax3.set_title("Distribusi Artikel per Tahun")
st.pyplot(fig3)
