import streamlit as st
from web3 import Web3
from datetime import datetime
import pandas as pd
import plotly.express as px

# --- 🔌 Connexion Blockchain Sepolia ---
st.set_page_config(page_title="🌊 Suivi Qualité de l'Eau", layout="wide")
st.markdown("## 💧 Tableau de bord – Surveillance de la Qualité de l'Eau via Blockchain")

w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/aa8cb41ffc394f94a83657992a27c11d"))
contract_address = Web3.to_checksum_address("0x52635f30d8ebbe2905777041b4a9705b9ad3bed0")

abi = [
    {
        "inputs": [],
        "name": "getRecordsCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "index", "type": "uint256"}],
        "name": "getRecord",
        "outputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "string", "name": "", "type": "string"},
            {"internalType": "uint256", "name": "", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

contract = w3.eth.contract(address=contract_address, abi=abi)

# --- 🔐 Vérification Connexion ---
if not w3.is_connected():
    st.error("❌ Impossible de se connecter au réseau Sepolia.")
    st.stop()

# --- 📥 Récupération des données ---
@st.cache_data(ttl=60)  # Cache pendant 1 min
def fetch_records():
    count = contract.functions.getRecordsCount().call()
    records = []
    for i in range(count):
        wqi, quality, timestamp = contract.functions.getRecord(i).call()
        date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        records.append({
            "ID": i + 1,
            "WQI": wqi,
            "Qualité": quality,
            "Horodatage": date_str
        })
    return pd.DataFrame(records)

try:
    df = fetch_records()
    st.success(f"✅ Nombre total d'enregistrements : {len(df)}")

    # --- 🧭 Navigation par onglets ---
    tab1, tab2, tab3 = st.tabs(["📋 Données", "📊 Statistiques", "ℹ️ À propos"])

    # --- 📋 Onglet 1 : Données brutes ---
    with tab1:
        with st.expander("🔍 Filtres avancés"):
            qual_filter = st.multiselect("Filtrer par qualité :", options=df["Qualité"].unique())
            date_range = st.date_input("Plage de dates :", [])

        filtered_df = df.copy()

        if qual_filter:
            filtered_df = filtered_df[filtered_df["Qualité"].isin(qual_filter)]

        if len(date_range) == 2:
            start = pd.to_datetime(date_range[0])
            end = pd.to_datetime(date_range[1])
            filtered_df = filtered_df[
                (pd.to_datetime(filtered_df["Horodatage"]) >= start) &
                (pd.to_datetime(filtered_df["Horodatage"]) <= end)
            ]

        st.dataframe(filtered_df, use_container_width=True)

        # ⬇️ Bouton Export
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger CSV", csv, file_name="water_quality_records.csv", mime="text/csv")

    # --- 📊 Onglet 2 : Statistiques ---
    with tab2:
        st.subheader("📈 Évolution du WQI dans le temps")
        fig = px.line(filtered_df, x="Horodatage", y="WQI", color="Qualité", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Histogramme des Qualités")
            fig_hist = px.histogram(filtered_df, x="Qualité", color="Qualité")
            st.plotly_chart(fig_hist, use_container_width=True)

        with col2:
            st.subheader("🥧 Répartition des Qualités (camembert)")
            quality_counts = filtered_df["Qualité"].value_counts().reset_index()
            quality_counts.columns = ["Qualité", "Nombre"]
            fig_pie = px.pie(quality_counts, names='Qualité', values='Nombre', title='Répartition des catégories')
            st.plotly_chart(fig_pie, use_container_width=True)

    # --- ℹ️ Onglet 3 : À propos ---
    with tab3:
        st.markdown("""
        ### 💡 À propos du projet

        Ce tableau de bord interactif affiche les données de qualité de l’eau collectées via un système IoT et stockées de manière immuable sur la blockchain **Sepolia Ethereum**.

        - 🔐 Transparence & traçabilité via smart contract  
        - 🌐 Visualisation dynamique avec Streamlit  
        - 👩‍💻 Projet de fin d'études – Master Big Data & IoT  

        **Kaouthar Merzouki**
        """)

except Exception as e:
    st.error(f"❌ Erreur lors du chargement des données : {e}")
