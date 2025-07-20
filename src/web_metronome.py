import streamlit as st
import time

st.set_page_config(page_title="Web Metronome", layout="centered")
st.title("🕒 Métronome Web")

bpm = st.slider(
    "BPM (Battements Par Minute)",
    min_value=40,
    max_value=208,
    value=120,
)
start = st.button("Start / Stop")

# Pour garder l'état du métronome
if 'is_playing' not in st.session_state:
    st.session_state['is_playing'] = False

if start:
    st.session_state['is_playing'] = not st.session_state['is_playing']

placeholder = st.empty()

# Métronome principal
while st.session_state['is_playing']:
    delay = 60.0 / bpm
    # Affichage visuel du battement
    placeholder.markdown(
        "<h1 style='color:red; text-align:center;'>●</h1>",
        unsafe_allow_html=True,
    )
    time.sleep(delay/2)
    placeholder.markdown(
        "<h1 style='color:gray; text-align:center;'>●</h1>",
        unsafe_allow_html=True,
    )
    time.sleep(delay/2)
    # Pour permettre l'arrêt immédiat
    st.experimental_rerun()

if not st.session_state['is_playing']:
    placeholder.markdown(
        "<h1 style='color:gray; text-align:center;'>●</h1>",
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown(
    "**Astuce :** Pour arrêter le métronome, cliquez à nouveau "
    "sur 'Start / Stop'."
)
