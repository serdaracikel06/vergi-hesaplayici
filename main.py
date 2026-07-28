import streamlit as st

# Sayfa Genişlik Ayarları
st.set_page_config(page_title="Vergi Hesaplayıcı 2026", layout="centered")

st.title("🧮 Gelir Vergisi Hesaplayıcı")
st.caption("2026 Yılı Güncel Marjinal Vergi Tarifesi")

# Durum Yönetimi (Tarifeyi Hafızada Tutmak İçin)
if "tarife" not in st.session_state:
    st.session_state.tarife = [
        {"oran": 15.0, "sinir": 190000.0},
        {"oran": 20.0, "sinir": 400000.0},
        {"oran": 27.0, "sinir": 1000000.0},
        {"oran": 35.0, "sinir": 5300000.0},
        {"oran": 40.0, "sinir": 99999999999.0}
    ]

# --- 1. BÖLÜM: MATRAH GİRİŞİ VE HESAPLAMA ---
st.subheader("1. Vergi Hesaplama")
taxinc = st.number_input("Hesaplanacak Vergi Matrahı (TL):", min_value=0.0, value=500000.0, step=1000.0)

# Kademeli Hesaplama Algoritması
tarife_list = st.session_state.tarife
tax = taxinc * (tarife_list[0]["oran"] / 100)

for i in range(1, len(tarife_list)):
    prev_limit = tarife_list[i-1]["sinir"]
    if taxinc > prev_limit:
        tax += (taxinc - prev_limit) * ((tarife_list[i]["oran"] - tarife_list[i-1]["oran"]) / 100)
    else:
        break

efektif_oran = (tax / taxinc) * 100 if taxinc > 0 else 0

# Sonuç Kartları
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Ödenecek Toplam Vergi", value=f"{tax:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
with col2:
    st.metric(label="Efektif Vergi Oranı", value=f"% {efektif_oran:.2f}".replace(".", ","))

st.divider()

# --- 2. BÖLÜM: TARİFE EKLEME VE TABLO ---
st.subheader("2. Vergi Tarifesi Düzenle")

with st.form("yeni_dilim", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        yeni_oran = st.number_input("Vergi Oranı (%)", min_value=0.0, max_value=100.0, value=15.0)
    with c2:
        yeni_sinir = st.number_input("Dilim Üst Sınırı (TL)", min_value=0.0, value=190000.0)
    
    if st.form_submit_button("Listeye Ekle"):
        st.session_state.tarife.append({"oran": yeni_oran, "sinir": yeni_sinir})
        st.session_state.tarife.sort(key=lambda x: x["sinir"])
        st.rerun()

# Mevcut Tarife Tablosu Gösterimi
st.write("**Mevcut Aktif Tarife:**")
for i, d in enumerate(st.session_state.tarife):
    sinir_str = "Sınırsız" if d["sinir"] > 9999999999 else f"{d['sinir']:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")
    st.write(f"• % {d['oran']:g} ➡️ {sinir_str}")

if st.button("Tabloyu Sıfırla (2026 Varsayılan)"):
    del st.session_state.tarife
    st.rerun()
