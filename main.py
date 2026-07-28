import streamlit as st

# Sayfa Başlığı Ayarları
st.set_page_config(page_title="Vergi Hesaplayıcı 2026", layout="centered")

# CSS ile en tepedeki gereksiz boşlukları düzenliyoruz
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 🚀 GÖMÜLÜ FİNANSAL GRAFİK GÖRSELİ (KIRILMAZ/HER YERDE ÇALIŞIR) ---
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 25px; background-color: #ffffff; padding: 15px; border-radius: 12px; box-shadow: 0px 4px 12px rgba(0,0,0,0.05);">
        <svg xmlns="http://w3.org" viewBox="0 0 800 350" width="100%" height="auto">
            <!-- Arka Plan Grid Çizgileri -->
            <line x1="100" y1="50" x2="700" y2="50" stroke="#f0f0f0" stroke-width="1"/>
            <line x1="100" y1="110" x2="700" y2="110" stroke="#f0f0f0" stroke-width="1"/>
            <line x1="100" y1="170" x2="700" y2="170" stroke="#f0f0f0" stroke-width="1"/>
            <line x1="100" y1="230" x2="700" y2="230" stroke="#f0f0f0" stroke-width="1"/>
            <line x1="100" y1="290" x2="700" y2="290" stroke="#eceff1" stroke-width="2"/>
            
            <!-- Dikey Bar Grafikleri (Sırasıyla Yükselen Dilimler) -->
            <rect x="150" y="240" width="50" height="50" rx="4" fill="#ff8a80"/>
            <rect x="250" y="200" width="50" height="90" rx="4" fill="#ffd54f"/>
            <rect x="350" y="150" width="50" height="140" rx="4" fill="#4fc3f7"/>
            <rect x="450" y="100" width="50" height="190" rx="4" fill="#81c784"/>
            <rect x="550" y="60" width="50" height="230" rx="4" fill="#ba68c8"/>
            
            <!-- Büyüme ve Yükseliş Oku (Yeşil Ok) -->
            <path d="M 120 270 Q 320 220 620 75" fill="none" stroke="#2e7d32" stroke-width="8" stroke-linecap="round"/>
            <path d="M 620 75 L 580 75 M 620 75 L 610 115" fill="none" stroke="#2e7d32" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
            
            <!-- Pasta Grafik Analiz Simgesi (Sağ Alt Köşe) -->
            <circle cx="680" cy="240" r="45" fill="#4caf50"/>
            <path d="M 680 240 L 680 195 A 45 45 0 0 1 725 240 Z" fill="#e91e63"/>
            <path d="M 680 240 L 725 240 A 45 45 0 0 1 680 285 Z" fill="#ffeb3b"/>
        </svg>
    </div>
    """,
    unsafe_allow_html=True
)

# Ana Kurumsal Başlık
st.title("Gelir Vergisi Hesaplayıcı")
st.caption("193 Sayılı Kanun Madde 103 — 2026 Resmi Gelir Vergisi Tarifesi")

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

taxinc = st.number_input(
    "Hesaplanacak Vergi Matrahı (TL):", 
    min_value=0.0, 
    value=500000.0, 
    step=1000.0,
    format="%.2f"
)

tarife_list = st.session_state.tarife

if taxinc > tarife_list["sinir"]:
    tax = tarife_list["sinir"] * (tarife_list["oran"] / 100)
else:
    tax = taxinc * (tarife_list["oran"] / 100)

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
st.subheader("2. Vergi Tarifesi Düzenleme Paneli")

st.write(f"**Aktif Tarife ({gelir_turu}):**")
silme_secenekleri = {}

for i, d in enumerate(st.session_state.tarife):
    sinir_str = "Sınırsız" if d["sinir"] > 9999999999 else f"{d['sinir']:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")
    liste_metni = f"% {d['oran']:g} ➡️ {sinir_str} limitine kadar"
    st.write(f"• **{liste_metni}**")
    silme_secenekleri[liste_metni] = i

st.write("")

with st.form("yeni_dilim", clear_on_submit=True):
    st.write("**Mevcut Tarifeye Yeni Bir Kademe Ekle:**")
    c1, c2 = st.columns(2)
    with c1:
        yeni_oran = st.number_input("Vergi Oranı (%)", min_value=0.0, max_value=100.0, value=15.0, step=1.0)
    with c2:
        yeni_sinir = st.number_input("Dilim Üst Sınırı (TL)", min_value=0.0, value=190000.0, step=10000.0)
    
    if st.form_submit_button("Listeye Ekle"):
        st.session_state.tarife.append({"oran": yeni_oran, "sinir": yeni_sinir})
        st.session_state.tarife.sort(key=lambda x: x["sinir"])
        st.toast("Yeni vergi dilimi başarıyla eklendi!", icon="✅")
        st.rerun()

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
