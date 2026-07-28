import streamlit as st

# Sayfa Başlığı ve Mobil Düzen Ayarları
st.set_page_config(page_title="Vergi Hesaplayıcı 2026", layout="centered", page_icon="🧮")

st.title("🧮 Gelir Vergisi Hesaplayıcı")
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
        {"oran": 27.0, "sinir": 1500000.0},  # Ücretlilerde 3. dilim sınırı 1.5 Milyon TL
        {"oran": 35.0, "sinir": 5300000.0},
        {"oran": 40.0, "sinir": 99999999999.0} # Son dilim %40
    ]
else:
    varsayilan_tarife = [
        {"oran": 15.0, "sinir": 190000.0},
        {"oran": 20.0, "sinir": 400000.0},
        {"oran": 27.0, "sinir": 1000000.0},  # Ücret dışı gelirlerde 3. dilim sınırı 1 Milyon TL
        {"oran": 35.0, "sinir": 5300000.0},
        {"oran": 40.0, "sinir": 99999999999.0} # Son dilim %40
    ]

# Durum Yönetimi: Kullanıcı geçiş yaptığında tarifeyi bellekten yenile
if "son_secim" not in st.session_state or st.session_state.son_secim != gelir_turu:
    st.session_state.tarife = varsayilan_tarife.copy()
    st.session_state.son_secim = gelir_turu

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

# Efektif Vergi Oranı Hesaplama
efektif_oran = (tax / taxinc) * 100 if taxinc > 0 else 0

# Sonuçları Göstergeler (Metric) Halinde Listeleme
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

# Mevcut Tarife Tablosu Gösterimi
st.write(f"**Aktif Tarife ({gelir_turu}):**")
silme_secenekleri = []

for i, d in enumerate(st.session_state.tarife):
    sinir_str = "Sınırsız" if d["sinir"] > 9999999999 else f"{d['sinir']:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")
    liste_metni = f"% {d['oran']:g} ➡️ {sinir_str} limitine kadar"
    st.write(f"• **{liste_metni}**")
    # Tuple formatında (index, metin) ekliyoruz
    silme_secenekleri.append((i, liste_metni))

st.write("")

# Yeni Dilim Ekleme Formu
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

# --- HATA RİSKİ OLMAYAN GÜVENLİ SİLME ALANI ---
st.write("**Mevcut Tarifeden Bir Dilimi Kaldır:**")
secilen_eleman = st.selectbox(
    "Silmek istediğiniz vergi dilimini seçin:", 
    options=silme_secenekleri, 
    format_func=lambda x: x[1] # Ekranda sadece açıklama metni görünecek
)

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("Seçili Dilimi Sil", type="primary"):
        if len(st.session_state.tarife) > 1:
            # Seçilen tuple'ın ilk elemanı olan gerçek indeksi güvenle siliyoruz
            indeks_to_delete = secilen_eleman[0]
            st.session_state.tarife.pop(indeks_to_delete)
            st.toast("Seçili dilim tarifeden silindi!", icon="🗑️")
            st.rerun()
        else:
            st.error("Tarifede en az 1 vergi dilimi kalmalıdır!")

with col_btn2:
    if st.button("Mevcut Seçimi Sıfırla (Resmi Ayara Dön)"):
        st.session_state.tarife = varsayilan_tarife.copy()
        st.rerun()

