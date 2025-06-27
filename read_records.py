"""
read_records.py
Tableau de bord Streamlit – Qualité de l’eau (mise à jour en temps réel)
Kaouthar Merzouki • PFE Master Big Data & IoT
"""

import streamlit as st
from web3 import Web3
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px

# ────────────────────────────── 1. CONFIG
st.set_page_config("🌊 Suivi Qualité de l'Eau", layout="wide")
st.title("💧 Suivi temps réel – Blockchain Sepolia")

# ────────────────────────────── 2. CONNEXION
w3 = Web3(Web3.HTTPProvider(
    "https://sepolia.infura.io/v3/aa8cb41ffc394f94a83657992a27c11d"))
contract_address = Web3.to_checksum_address(
    "0x52635f30d8ebbe2905777041b4a9705b9ad3bed0")

abi = [
    {"name": "getRecordsCount", "inputs": [], "outputs":
        [{"internalType": "uint256", "name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"name": "getRecord",
     "inputs": [{"internalType": "uint256", "name": "index", "type": "uint256"}],
     "outputs": [
        {"internalType": "uint256", "name": "", "type": "uint256"},
        {"internalType": "string",  "name": "", "type": "string"},
        {"internalType": "uint256", "name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"}
]
contract = w3.eth.contract(address=contract_address, abi=abi)
if not w3.is_connected():
    st.error("❌ Réseau Sepolia inaccessible"); st.stop()

# ────────────────────────────── 3. DATA
@st.cache_data(show_spinner=False, ttl=30)
def fetch_records() -> pd.DataFrame:
    n = contract.functions.getRecordsCount().call()
    rows = []
    for i in range(n):
        wqi, quality, ts = contract.functions.getRecord(i).call()
        rows.append({
            "ID": i+1, "WQI": wqi, "Qualité": quality,
            "Horodatage": datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        })
    return pd.DataFrame(rows)

df = fetch_records()
st.success(f"✅ {len(df)} enregistrements – Maj {datetime.now():%H:%M:%S}")

# ────────────────────────────── 4. LIVE REFRESH
if st.sidebar.toggle("🔄 Live 5 s", False):
    from streamlit_autorefresh import st_autorefresh   # pip install streamlit-autorefresh
    st_autorefresh(interval=5000, key="auto_refresh")
    df = fetch_records()

# ────────────────────────────── 5. UI TABS
tab_data, tab_stats, tab_info = st.tabs(["📋 Données", "📊 Statistiques", "ℹ️ À propos"])



with tab_data:
    st.subheader("📋 Données Blockchain")
    with st.expander("🔍 Filtres"):
        qual_filter = st.multiselect("Qualité :", sorted(df["Qualité"].unique()))
        date_min = pd.to_datetime(df["Horodatage"]).min().date()
        date_range = st.date_input("Plage de dates", (date_min, date.today()))

    filt = df.copy()
    if qual_filter:
        filt = filt[filt["Qualité"].isin(qual_filter)]



    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        d1 = pd.to_datetime(date_range[0])
        # inclure toute la journée finale (23:59:59)
        d2 = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        filt = filt[pd.to_datetime(filt["Horodatage"]).between(d1, d2)]
   
    # if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    #     d1, d2 = map(pd.to_datetime, date_range)
    #     filt = filt[pd.to_datetime(filt["Horodatage"]).between(d1, d2)]

    st.write(f"Nombre total lignes : {len(df)}")
    # st.write(f"Nombre lignes après filtres : {len(filt)}")

    if filt.empty:
        st.warning("Aucune donnée pour ces filtres.")
    else:
        # Augmenter hauteur à 800 pour voir plus de lignes d'un coup
        st.dataframe(filt, use_container_width=True, height=400)
    

    st.download_button("📥 CSV", filt.to_csv(index=False).encode(),
                       "water_quality_records.csv", "text/csv")




# # --------- Onglet DONNÉES
# with tab_data:
#     st.subheader("📋 Données Blockchain")
#     with st.expander("🔍 Filtres"):
#         qual_filter = st.multiselect("Qualité :", sorted(df["Qualité"].unique()))
#         date_min = pd.to_datetime(df["Horodatage"]).min().date()
#         date_range = st.date_input("Plage de dates", (date_min, date.today()))

#     filt = df.copy()
#     if qual_filter:
#         filt = filt[filt["Qualité"].isin(qual_filter)]
#     if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
#         d1, d2 = map(pd.to_datetime, date_range)
#         filt = filt[pd.to_datetime(filt["Horodatage"]).between(d1, d2)]

#     if filt.empty:
#         st.warning("Aucune donnée pour ces filtres.")
#     else:
#         st.dataframe(filt, use_container_width=True, height=400)

#     st.download_button("📥 CSV", filt.to_csv(index=False).encode(),
#                        "water_quality_records.csv", "text/csv")

# --------- Onglet STATISTIQUES
with tab_stats:
    if filt.empty:
        st.info("Pas de données pour les graphiques.")
    else:
        st.subheader("📈 WQI dans le temps")
        st.plotly_chart(px.line(filt, x="Horodatage", y="WQI",
                                color="Qualité", markers=True),
                        use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Histogramme des Qualités")
            st.plotly_chart(px.histogram(filt, x="Qualité", color="Qualité"),
                            use_container_width=True)
        with col2:
            st.subheader("🥧 Répartition par Qualité")
            counts = (filt["Qualité"]
                      .value_counts()
                      .reset_index(name="Nombre")
                      .rename(columns={"index": "Qualité"}))
            st.plotly_chart(px.pie(counts, names="Qualité", values="Nombre"),
                            use_container_width=True)

# --------- Onglet À PROPOS
with tab_info:
    st.markdown("""
### 💡 À propos
Tableau de bord **IoT → Blockchain → Streamlit**  
PFE Master Big Data & IoT  
**Étudiante :** Kaouthar Merzouki  
**Encadrant :** M. Abdelhak Mahmoudi
""")
