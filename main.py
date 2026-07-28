import streamlit as st

# Sayfa Başlığı ve Mobil Düzen Ayarları
st.set_page_config(page_title="Vergi Hesaplayıcı 2026", layout="centered", page_icon="🧮")

st.title("🧮 Gelir Vergisi Hesaplayıcı")
st.caption("2026 Yılı Güncel Marjinal Vergi Tarifesi (Efektif Oran Destekli)")

# Durum Yönetimi: Tarife Listesini Hafızada Tutma
if "tarife" not in st.session_state:
    st.session_state.tarife = [
        {"oran": 15.0, "sinir": 190000.0},
        {"oran": 20.0, "sinir": 400000.0},
        {"oran": 27.0, "sinir": 1000000.0},
        {"oran": 35.0, "sinir": 5300000.0},
        {"oran": 40.0, "sinir": 99999999999.0} # Son dilim ucu açık
    ]

# --- 1. BÖLÜM: MATRAH GİRİŞİ VE HESAPLAMA ---
st.subheader("1. Vergi Hesaplama Paneli")

# Kullanıcıdan Vergi Matrahı Alma
taxinc = st.number_input(
    "Hesaplanacak Vergi Matrahı (TL):", 
    min_value=0.0, 
    value=500000.0, 
    step=1000.0,
    format="%.2f"
)

# Kademeli Matematiksel Hesaplama Algoritması
tarife_list = st.session_state.tarife
tax = taxinc * (tarife_list[0]["oran"] / 100)

for i in range(1, len(tarife_list)):
    prev_limit = tarife_list[i-1]["sinir"]
    if taxinc > prev_limit:
        current_rate = tarife_list[i]["oran"] / 100
        prev_rate = tarife_list[i-1]["oran"] / 100
        # Marjinal oran farkı kümülatif olarak eklenir
        tax += (taxinc - prev_limit) * (current_rate - prev_rate)
    else:
        break

# Efektif Vergi Oranı Hesaplama (Toplam Vergi / Matrah * 100)
efektif_oran = (tax / taxinc) * 100 if taxinc > 0 else 0

# Sonuçları Büyük Göstergeler (Metric) Halinde Listeleme
col1, col2 = st.columns(2)
with col1:
    st.metric(
        label="Ödenecek Toplam Vergi", 
        value=f"{tax:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")
    )
with col2:
    st.metric(
        label="Efektif Vergi Oranı", 
        value=f"% {efektif_oran:.2f}".replace(".", ",")
    )

st.divider()

# --- 2. BÖLÜM: TARİFE EKLEME VE TABLO DÜZENLEME ---
st.subheader("2. Vergi Tarifesi Düzenle")

with st.form("yeni_dilim", clear_on_submit=True):
    st.write("Aşağıdan tarifeye yeni bir kademe/dilim ekleyebilirsiniz:")
    c1, c2 = st.columns(2)
    with c1:
        yeni_oran = st.number_input("Vergi Oranı (%)", min_value=0.0, max_value=100.0, value=15.0, step=1.0)
    with c2:
        yeni_sinir = st.number_input("Dilim Üst Sınırı (TL)", min_value=0.0, value=190000.0, step=10000.0)
    
    if st.form_submit_button("Listeye Ekle"):
        # Yeni dilimi ekle ve sınırlara göre küçükten büyüğe sırala
        st.session_state.tarife.append({"oran": yeni_oran, "sinir": yeni_sinir})
        st.session_state.tarife.sort(key=lambda x: x["sinir"])
        st.toast("Yeni vergi dilimi başarıyla eklendi!", icon="✅")
        st.rerun()

# Aktif Vergi Tarifesi Tablosu Gösterimi
st.write("**Mevcut Aktif Vergi Tarifesi:**")
for i, d in enumerate(st.session_state.tarife):
    sinir_str = "Sınırsız" if d["sinir"] > 9999999999 else f"{d['sinir']:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")
    st.write(f"• **% {d['oran']:g}** vergi oranı ➡️ **{sinir_str}** limitine kadar.")

# Tarifeyi İlk Haline Döndürme Butonu
if st.button("Tabloyu Sıfırla (2026 Varsayılan Tarifesi)"):
    if "tarife" in st.session_state:
        del st.session_state.tarife
    st.rerun()
