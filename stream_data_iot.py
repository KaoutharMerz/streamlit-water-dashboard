import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

# -----------------------------------------
# FONCTION POUR JAUGES (affichage par capteur)
# -----------------------------------------
def plot_gauge(title, value, min_val, max_val, unit=""):
    fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            delta={'reference': (min_val + max_val) / 2, 'increasing': {'color': "red"}},
            title={'text': f"<b>{title}</b>", 'font': {'size': 20}},  # <-- ici taille plus grande
            gauge={
                'shape': "angular",
                'axis': {'range': [min_val, max_val], 'tickwidth': 2, 'tickcolor': "darkblue"},
                'bar': {'color': "royalblue", 'thickness': 0.3},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [min_val, (min_val + max_val) / 2], 'color': "#e0f7fa"},
                    {'range': [(min_val + max_val) / 2, max_val], 'color': "#b2ebf2"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            },
            number={'suffix': f" {unit}", 'font': {'size': 24}},
            domain={'x': [0, 1], 'y': [0, 1]}
))

    fig.update_layout(margin=dict(t=50, b=0, l=0, r=0))
    return fig

# -----------------------------------------
# STREAMLIT UI - Simulation capteurs
# -----------------------------------------
st.set_page_config(layout="wide")
st.title("🌊 Interface Capteurs - Données simulées en temps réel")

if st.button("▶️ Lancer la visualisation en direct"):
    container = st.empty()

    for i in range(100):
        # Simulation aléatoire de données capteurs
        values = {
            "pH": round(np.random.uniform(6.5, 8.5), 2),
            "Température": round(np.random.uniform(15, 35), 2),
            "TSS": round(np.random.uniform(5, 50), 2),
            "Turbidité": round(np.random.uniform(0, 15), 2),
            "FC": round(np.random.uniform(0, 100), 2),
            "Oxygène": round(np.random.uniform(4, 12), 2),
            "Phosphates": round(np.random.uniform(0, 1), 2),
            "Nitrates": round(np.random.uniform(0, 1.5), 2),
        }

        with container.container():
            st.subheader(f"📡 Données simulées #{i+1}")

            # 2 lignes de 4 colonnes pour afficher les jauges
            gauges1 = st.columns(4)
            gauges2 = st.columns(4)

            gauges_1_params = [
                ("pH", values["pH"], "pH", 0, 14),
                ("Température", values["Température"], "°C", 0, 50),
                ("TSS", values["TSS"], "mg/L", 0, 100),
                ("Turbidité", values["Turbidité"], "NTU", 0, 20),
            ]

            gauges_2_params = [
                ("FC", values["FC"], "ufc/100mL", 0, 100),
                ("Oxygène", values["Oxygène"], "mg/L", 0, 14),
                ("Phosphates", values["Phosphates"], "mg/L", 0, 1),
                ("Nitrates", values["Nitrates"], "mg/L", 0, 1.5),
            ]

            for idx, (col, (label, val, unit, mini, maxi)) in enumerate(zip(gauges1, gauges_1_params)):
                with col:
                    st.plotly_chart(plot_gauge(label, val, mini, maxi, unit), use_container_width=True, key=f"g1_{i}_{idx}")

            for idx, (col, (label, val, unit, mini, maxi)) in enumerate(zip(gauges2, gauges_2_params)):
                with col:
                    st.plotly_chart(plot_gauge(label, val, mini, maxi, unit), use_container_width=True, key=f"g2_{i}_{idx}")

        time.sleep(2)

    st.success("✅ Visualisation terminée")
