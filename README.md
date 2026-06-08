import streamlit as st
from datetime import datetime
import json
import os
import uuid

st.set_page_config(page_title="codexX", layout="wide", page_icon="🚀")

# ====================== FONDO ======================
st.markdown("""
    <style>
    .main {background: linear-gradient(135deg, #0e1117 0%, #1a1f2e 100%); background-attachment: fixed;}
    h1 {color: #00ff9d; font-size: 3rem; text-align: center;}
    .stButton>button {background-color: #00ff9d; color: black; font-weight: bold; border-radius: 8px;}
    .task-card {background-color: #1a1f2e; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid #00ff9d22;}
    .wallet-box {background-color: #16213e; padding: 20px; border-radius: 12px; border: 2px solid #00ff9d; text-align: center;}
    .counter {font-size: 1.1rem; font-weight: bold; color: #00ff9d;}
    </style>
""", unsafe_allow_html=True)

# ====================== CONFIG ======================
st.title("🚀 codexX")
st.markdown("Gana recompensas haciendo tareas en Twitter (X)")

TU_WALLET = "TU_CWALLET_ID_AQUI"      # ← Cambia esto
RED = "Solana / Tron / BSC"
MONEDA = "USDT"

DATA_FILE = "tareas_codex.json"

# ====================== CONTRASEÑA (Recomendado) ======================
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin12345")  
# ← Pon tu contraseña real en .streamlit/secrets.toml

def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

datos = cargar_datos()

def contar_pagos_pendientes():
    pendientes = 0
    for tarea in datos:
        if tarea.get("estado") == "Activa":
            for comp in tarea.get("completados", []):
                if not comp.get("pagado", False):
                    pendientes += 1
    return pendientes

# ====================== ADMIN MODE ======================
query_params = st.query_params
is_admin_mode = query_params.get("admin", [False])[0] == "true"

menu_options = ["🧑‍🤝‍🧑 Ver Tareas", "➕ Crear Tarea", "✅ Enviar Completado"]
if is_admin_mode:
    menu_options.append("🔐 Modo Admin")

rol = st.sidebar.selectbox("Menú Principal", menu_options)
st.sidebar.caption("codexX v1.7")

# ====================== WALLET ======================
st.sidebar.markdown("### 💰 Págame aquí")
st.sidebar.markdown(f"""
<div class="wallet-box">
    <strong>Wallet:</strong><br>
    <code>{TU_WALLET}</code><br><br>
    <strong>Red:</strong> {RED}<br>
    <strong>Moneda:</strong> {MONEDA}
</div>
""", unsafe_allow_html=True)

if is_admin_mode:
    pendientes = contar_pagos_pendientes()
    if pendientes > 0:
        st.sidebar.error(f"⛔ {pendientes} PAGOS PENDIENTES")
    else:
        st.sidebar.success("✅ Todo al día")

# ====================== MODO ADMIN ======================
if rol == "🔐 Modo Admin" and is_admin_mode:
    st.subheader("🔐 Panel de Administración")
    password = st.text_input("🔑 Contraseña de Administrador", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("✅ Acceso correcto")
        # ... (mantengo las pestañas anteriores, solo agrego el límite en crear tarea)
    elif password:
        st.error("❌ Contraseña incorrecta")

# ====================== CREAR TAREA (Con límite) ======================
elif rol == "➕ Crear Tarea":
    st.subheader("Crear Nueva Tarea")
    
    with st.form("nueva_tarea"):
        titulo = st.text_input("Título de la tarea")
        descripcion = st.text_area("Descripción detallada")
        recompensa = st.number_input("Recompensa por persona (USDT)", min_value=0.01, value=0.01, step=0.01)
        limite = st.number_input("Límite de participantes", min_value=1, value=50, step=1,
        help="0 = Sin límite")
        
        submitted = st.form_submit_button("Publicar Tarea")
        
        if submitted:
            if titulo and descripcion:
                nueva = {
                    "id": str(uuid.uuid4())[:8],
                    "titulo": titulo,
                    "descripcion": descripcion,
                    "recompensa": recompensa,
                    "limite": int(limite),
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "estado": "Activa",
                    "completados": []
                }
                datos.append(nueva)
                guardar_datos(datos)
                st.success("¡Tarea publicada correctamente!")
                st.rerun()
            else:
                st.error("Título y descripción son obligatorios")

# ====================== VER TAREAS (Con límite visible) ======================
elif rol == "🧑‍🤝‍🧑 Ver Tareas":
    st.subheader("Tareas Disponibles")
    activas = [t for t in datos if t.get("estado") == "Activa"]
    
    if not activas:
        st.info("No hay tareas activas.")
    else:
        for t in activas:
            completados = len(t.get("completados", []))
            limite = t.get("limite", 0)
            restantes = limite - completados if limite > 0 else "∞"
            
            status = "✅ Disponible" if (limite == 0 or completados < limite) else "🔴 Límite alcanzado"
            
            st.markdown(f"""
            <div class="task-card">
                <h3>{t['titulo']}</h3>
                <p>{t['descripcion']}</p>
                <p><strong>Recompensa:</strong> ${t['recompensa']} {MONEDA}</p>
                <p><strong>👥 {completados} / {limite if limite > 0 else '∞'} completados</strong></p>
                <p><strong>{status}</strong> | Quedan: <span class="counter">{restantes}</span></p>
                <small>Publicado: {t['fecha']}</small>
            </div>
            """, unsafe_allow_html=True)

# ====================== ENVIAR COMPLETADO (Con control de límite) ======================
elif rol == "✅ Enviar Completado":
    st.subheader("Enviar Prueba de Completado")
    
    activas = [t for t in datos if t.get("estado") == "Activa"]
    # Filtrar solo tareas con cupo disponible
    disponibles = [t for t in activas if t.get("limite", 0) == 0 or len(t.get("completados", [])) < t.get("limite", 0)]
    
    if not disponibles:
        st.warning("No hay tareas con cupo disponible en este momento.")
    else:
        tarea_seleccionada = st.selectbox(
            "Selecciona la tarea",
            options=disponibles,
            format_func=lambda x: f"#{x['id']} - {x['titulo']} ({len(x.get('completados', []))}/{x.get('limite','∞')})"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Tu usuario de X (@)")
        with col2:
            wallet = st.text_input("Tu Wallet / ccwallet")
        
        link = st.text_input("Enlace de tu publicación")
        comentario = st.text_area("Comentario adicional")

        if st.button("Enviar Completado", type="primary"):
            completados_actuales = len(tarea_seleccionada.get("completados", []))
            limite = tarea_seleccionada.get("limite", 0)
            
            if limite > 0 and completados_actuales >= limite:
                st.error("❌ Se alcanzó el límite de participantes para esta tarea.")
            elif username and link:
                completado = {
                    "usuario": username,
                    "wallet": wallet if wallet else "No proporcionado",
                    "link": link,
                    "comentario": comentario,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "pagado": False
                    }
                
                for t in datos:
                    if t["id"] == tarea_seleccionada["id"]:
                        if "completados" not in t:
                            t["completados"] = []
                        t["completados"].append(completado)
                        break
                
                guardar_datos(datos)
                st.success("✅ Completado registrado correctamente.")
                st.rerun()
            else:
                st.error("Usuario y enlace son obligatorios")

# ====================== BOTÓN ADMIN ======================
if not is_admin_mode:
    with st.sidebar.expander("🔑 Acceso Admin"):
        if st.button("Activar Modo Administrador"):
            st.query_params["admin"] = "true"
            st.rerun()
