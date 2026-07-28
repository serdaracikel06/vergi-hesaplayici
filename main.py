import streamlit as st

# Sayfa Başlığı ve Mobil Düzen Ayarları
st.set_page_config(page_title="Vergi Hesaplayıcı 2026", layout="centered", page_icon="📈")

# --- KESİN ÇÖZÜM: KODUN İÇİNE GÖMÜLÜ FİNANSAL GRAFİK RESMİ ---
# Bu yöntem internet linkine ihtiyaç duymadığı için kırık resim simgesi (0) tamamen kaybolacaktır.
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 800 300' width='100%25' height='auto'><rect width='100%25' height='100%25' fill='%23fafafa'/><path d='M100,250 L250,180 L400,210 L550,110 L700,60' fill='none' stroke='%234caf50' stroke-width='8' stroke-linecap='round' stroke-linejoin='round'/><path d='M700,60 L640,65 M700,60 L695,120' fill='none' stroke='%234caf50' stroke-width='8' stroke-linecap='round' stroke-linejoin='round'/><circle cx='100' cy='250' r='10' fill='%23e91e63'/><circle cx='250' cy='180' r='10' fill='%23ffeb3b'/><circle cx='400' cy='210' r='10' fill='%2300bcd4'/><circle cx='550' cy='110' r='10' fill='%233f51b5'/><circle cx='700' cy='60' r='12' fill='%234caf50'/><line x1='50' y1='250' x2='750' y2='250' stroke='%23cccccc' stroke-width='2'/><line x1='100' y1='50' x2='100' y2='270' stroke='%23cccccc' stroke-width='2'/></svg>" style="width: 100%; max-width: 650px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05);">
    </div>
    """,
    unsafe_allow_html=True
)

# Abaküs resmi (🧮) başlıktan tamamen kaldırıldı
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
