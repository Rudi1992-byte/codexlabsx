import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(page_title="CODEX", layout="wide", page_icon="🚀")

# ====================== ESTILO ======================
st.markdown("""
    <style>
    .main {background-color: #0e1117;}
    h1 {color: #00ff9d;}
    .stButton>button {background-color: #00ff9d; color: black; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# ====================== CONFIG ======================
st.title("🚀 CODEX")
st.markdown("Gana recompensas haciendo tareas en Twitter (X)")

PLATFORM_FEE = 3.0
REWARD_PER_PERSON = 0.01
TU_CWALLET = "TU_CWALLET_ID_AQUI"   # ← Cambia esto

# Contraseña desde Secrets (segura)
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "12345")  # valor por defecto si no hay secret

DATA_FILE = "tareas_codex.json"

def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

datos = cargar_datos()

rol = st.sidebar.selectbox("Menú Principal", 
    ["🧑‍🤝‍🧑 Ver Tareas", "➕ Crear Tarea", "✅ Enviar Completado", "🔐 Modo Admin"])

# ====================== MODO ADMIN (Protegido) ======================
if rol == "🔐 Modo Admin":
    st.subheader("🔐 Panel de Administración")
    
    password = st.text_input("🔑 Ingresa la contraseña de Administrador", type="password")
    
    if password == ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "default_password")
        st.success("✅ Acceso Correcto")
        # Aquí va todo el panel admin (lo mantengo corto por ahora)
        st.info("Panel de administración cargado correctamente.")
        for i, t in enumerate(datos):
            if t.get("estado") == "Activa":
                with st.expander(f"Tarea #{t['id']}"):
                    st.write(t['descripcion'])
                    if st.button("💰 Marcar como Pagada", key=f"pay{i}"):
                        t["estado"] = "Finalizada"
                        guardar_datos(datos)
                        st.success("Tarea marcada como pagada")
    else:
        if password != "":  
            st.error("❌ Contraseña incorrecta")

# ====================== Otras secciones (resumidas) ======================
else:
    st.info("Selecciona una opción del menú lateral.")

st.sidebar.caption("CODEX v1.0")
