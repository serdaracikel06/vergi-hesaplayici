import streamlit as st

# Sayfa Başlığı Ayarları
st.set_page_config(page_title="Vergi Hesaplayıcı 2026", layout="centered")

# --- 🚀 GÜNCELLENDİ: PROTOKOLE UYGUN RESMİ BİLGİ PANELİ ---
# Müdürlük yazısı, Bakanlık yazısının tam altına hiyerarşik düzende yerleştirildi
st.info(
    "🏛️ **T.C. HAZİNE VE MALİYE BAKANLIĞI**\n\n"
    "**GELİR POLİTİKALARI İZLEME VE DEĞERLENDİRME MÜDÜRLÜĞÜ**\n\n"
    "193 Sayılı Gelir Vergisi Kanunu Madde 103 — 2026 Takvim Yılı Resmi Tarifesi"
)

# --- TAM SOLA YASLI BAŞLIK ---
st.title("Gelir Vergisi Hesaplayıcı")
st.caption("2026 Yılı Güncel Marjinal Vergi Tarifesi (Efektif Oran Destekli)")

# --- GELİR TÜRÜ SEÇİMİ ---
gelir_turu = st.radio(
    "Lütfen Gelir Türünü Seçiniz (Tarife otomatik güncellenir):",
    ["Ücret Dışı Gelirler (Esnaf, Kira, Şirket vb.)", "Ücret Gelirleri (Maaşlı Çalışanlar)"],
    horizontal=True
)

# Seçilen Gelir Türüne Göre Resmi 2026 Sabit Tarifeleri
if gelir_turu == "Ücret Gelirleri (Maaşlı Çalışanlar)":
    varsayilan_tarife = [
        {"oran": 15.0, "sinir": 190000.0},
        {"oran": 20.0, "sinir": 400000.0},
        {"oran": 27.0, "sinir": 1500000.0},  
        {"oran": 35.0, "sinir": 5300000.0},
        {"oran": 40.0, "sinir": 99999999999.0} 
    ]
else:
    varsayilan_tarife = [
        {"oran": 15.0, "sinir": 190000.0},
        {"oran": 20.0, "sinir": 400000.0},
        {"oran": 27.0, "sinir": 1000000.0},  
        {"oran": 35.0, "sinir": 5300000.0},
        {"oran": 40.0, "sinir": 99999999999.0} 
    ]

# Durum Yönetimi
if "son_secim" not in st.session_state or st.session_state.son_secim != gelir_turu:
    st.session_state.tarife = varsayilan_tarife.copy()
    st.session_state.son_secim = gelir_turu

# --- 1. BÖLÜM: MATRAH GİRİŞİ VE HESAPLAMA ---
st.subheader("1. Vergi Hesaplama Paneli")

# TÜRKÇE FORMATLI ANA MATRAH GİRİŞ SİSTEMİ
if "raw_input" not in st.session_state:
    st.session_state.raw_input = "500000"

user_text = st.text_input(
    "Hesaplanacak Vergi Matrahı (TL):",
    value=f"{float(st.session_state.raw_input.replace('.', '').replace(',', '.')):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    key="matrah_text_input",
    help="Sayıları düz yazabilirsiniz, sistem otomatik olarak nokta ve virgül ekleyecektir."
)

try:
    clean_val = user_text.replace(".", "").replace(",", ".")
    taxinc = float(clean_val)
    st.session_state.raw_input = clean_val
except ValueError:
    taxinc = 0.0

tarife_list = st.session_state.tarife

# Doğru Kademeli Matematiksel Hesaplama Algoritması
if taxinc > tarife_list[0]["sinir"]:
    tax = tarife_list[0]["sinir"] * (tarife_list[0]["oran"] / 100)
else:
    tax = taxinc * (tarife_list[0]["oran"] / 100)

for i in range(1, len(tarife_list)):
    prev_limit = tarife_list[i-1]["sinir"]
    current_limit = tarife_list[i]["sinir"]
    current_rate = tarife_list[i]["oran"] / 100
    
    if taxinc > prev_limit:
        usable_matrah = min(taxinc, current_limit) - prev_limit
        tax += usable_matrah * current_rate
    else:
        break

efektif_oran = (tax / taxinc) * 100 if taxinc > 0 else 0

# Türk finans standartlarında çıktı formatlama
sonuc_formatli = f"{tax:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
efektif_formatli = f"{efektif_oran:.2f}".replace(".", ",")

# Sonuç Göstergeleri
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Ödenecek Toplam Vergi", value=f"{sonuc_formatli} TL")
with col2:
    st.metric(label="Efektif Vergi Oranı", value=f"% {efektif_formatli}")

st.divider()

# --- 2. BÖLÜM: TARİFE EKLEME VE TABLO DÜZENLEME ---
st.subheader("2. Vergi Tarifesi Düzenleme Paneli")

st.write(f"**Aktif Tarife ({gelir_turu}):**")
silme_secenekleri = {}

for i, d in enumerate(st.session_state.tarife):
    sinir_str = "Sınırsız" if d["sinir"] > 9999999999 else f"{d['sinir']:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")
    liste_metni = f"% {d['oran']:g} ➡️ {sinir_str} limitine kadar"
    st.write(f"• **{liste_metni}**")
    silme_secenekleri[liste_metni] = i

st.write("")

# Yeni Dilim Ekleme Alanındaki Sayı Girişi
if "raw_yeni_sinir" not in st.session_state:
    st.session_state.raw_yeni_sinir = "190000"

with st.form("yeni_dilim", clear_on_submit=True):
    st.write("**Mevcut Tarifeye Yeni Bir Kademe Ekle:**")
    c1, c2 = st.columns(2)
    with c1:
        yeni_oran = st.number_input("Vergi Oranı (%)", min_value=0.0, max_value=100.0, value=15.0, step=1.0)
    with c2:
        yeni_sinir_text = st.text_input(
            "Dilim Üst Sınırı (TL)", 
            value=f"{float(st.session_state.raw_yeni_sinir.replace('.', '').replace(',', '.')):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
    
    if st.form_submit_button("Listeye Ekle"):
        try:
            clean_yeni_sinir = yeni_sinir_text.replace(".", "").replace(",", ".")
            yeni_sinir = float(clean_yeni_sinir)
            st.session_state.raw_yeni_sinir = clean_yeni_sinir
            
            if yeni_oran >= 0 and yeni_sinir > 0:
                st.session_state.tarife.append({"oran": yeni_oran, "sinir": yeni_sinir})
                st.session_state.tarife.sort(key=lambda x: x["sinir"])
                st.toast("Yeni vergi dilimi başarıyla eklendi!", icon="✅")
                st.rerun()
        except ValueError:
            st.error("Lütfen geçerli bir sınır değeri giriniz!")

st.write("**Mevcut Tarifeden Bir Dilimi Kaldır:**")
secilen_metin = st.selectbox(
    "Silmek istediğiniz vergi dilimini seçin:", 
    options=list(silme_secenekleri.keys())
)

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("Seçili Dilimi Sil", type="primary"):
        if len(st.session_state.tarife) > 1:
            indeks_to_delete = silme_secenekleri[secilen_metin]
            st.session_state.tarife.pop(indeks_to_delete)
            st.toast("Seçili dilim tarifeden silindi!", icon="🗑️")
            st.rerun()
        else:
            st.error("Tarifede en az 1 vergi dilimi kalmalıdır!")

with col_btn2:
    if st.button("Mevcut Seçimi Sıfırla (Resmi Ayara Dön)"):
        st.session_state.tarife = varsayilan_tarife.copy()
        st.rerun()

# --- RESMİ GELİŞTİRİCİ İMZASI ---
st.write("")
st.write("")
st.divider()
st.markdown(
    "<div style='text-align: center; color: #555555; font-size: 0.9em; font-family: sans-serif;'>"
    "💻 Bu mobil uygulama <b><a href='mailto:serdar.acikel@gelirler.gov.tr' "
    "style='color: #d32f2f; text-decoration: none; font-weight: bold;'>Serdar AÇIKEL</a></b> "
    "tarafından geliştirilmiştir. | © 2026"
    "</div>", 
    unsafe_allow_html=True
)
