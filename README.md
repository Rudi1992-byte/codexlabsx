import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(page_title="CODEX", layout="wide", page_icon="🚀")

# ====================== ESTILO MODERNO ======================
st.markdown("""
    <style>
    .main {background-color: #0e1117;}
    h1 {color: #00ff9d; font-size: 3rem;}
    .stButton>button {background-color: #00ff9d; color: black; font-weight: bold; border-radius: 8px;}
    .stButton>button:hover {background-color: #00cc7a;}
    .card {background-color: #1e1e2e; padding: 20px; border-radius: 12px; border: 1px solid #00ff9d;}
    </style>
""", unsafe_allow_html=True)

# ====================== CONFIGURACIÓN ======================
st.title("🚀 CODEX")
st.markdown("Gana recompensas haciendo tareas en Twitter (X)")
st.caption("Plataforma de bounties y tareas remuneradas")

PLATFORM_FEE = 3.0
REWARD_PER_PERSON = 0.01  # Fijo como pediste
TU_CWALLET = "TU_CWALLET_ID_AQUI"   # ← CAMBIA ESTO

DATA_FILE = "tareas_codex.json"

# Contraseña de Administrador (cámbiala por una segura)
ADMIN_PASSWORD = "codex2026"   # ← CAMBIA ESTA CONTRASEÑA

def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

datos = cargar_datos()

# Sidebar
rol = st.sidebar.selectbox("Menú Principal", 
    ["🧑‍🤝‍🧑 Ver Tareas", "➕ Crear Tarea", "✅ Enviar Completado", "🔐 Modo Admin"])

st.sidebar.divider()
st.sidebar.info(f"Recompensa fija: {REWARD_PER_PERSON} USDT por persona")
st.sidebar.info(f"Comisión plataforma: {PLATFORM_FEE} USDT")
st.sidebar.caption(f"Tu billetera: {TU_CWALLET}")

# ====================== VER TAREAS ======================
if rol == "🧑‍🤝‍🧑 Ver Tareas":
    st.subheader("Tareas Disponibles")
    st.markdown("---")
    
    tareas_activas = [t for t in datos if t.get("estado") == "Activa"]
    
    if tareas_activas:
        for t in tareas_activas:
            faltan = t["num_slots"] - t.get("slots_completados", 0)
            if faltan > 0:
                with st.container(border=True):
                    st.markdown(f"#{t['id']} - {t['descripcion']}")
                    st.write(f"💰 {t['reward_per']} USDT por persona")
                    st.write(f"👥 {faltan} de {t['num_slots']} slots disponibles")
                    st.caption(f"Creador: @{t.get('twitter_creador', 'Anónimo')}")
    else:
        st.info("No hay tareas disponibles en este momento.")

# ====================== CREAR TAREA ======================
elif rol == "➕ Crear Tarea":
    st.subheader("📢 Publicar Nueva Tarea")
    
    with st.form("crear_tarea"):
        desc = st.text_area("Descripción de la tarea", 
                           placeholder="Ejemplo: Dale Like + RT + comenta este tweet con tu opinión...")
        num_slots = st.number_input("Cantidad de personas (slots)", value=150, min_value=1, step=1)
        twitter = st.text_input("Tu Twitter @", placeholder="@tucuenta")
        
        # Cálculo automático
        recompensa_total = round(REWARD_PER_PERSON * num_slots, 3)
        total_a_pagar = round(recompensa_total + PLATFORM_FEE, 3)
        
        st.success(f"""
        Cálculo automático:
        - Recompensa total para participantes: {recompensa_total} USDT
        - Comisión plataforma: {PLATFORM_FEE} USDT
        - Total a pagar: {total_a_pagar} USDT
        """)
        
        if st.form_submit_button("🚀 Publicar Tarea"):
            if not desc or not twitter:
                st.error("Por favor completa la descripción y tu Twitter.")
            else:
                nueva = {
                    "id": len(datos) + 1,
                    "descripcion": desc,
                    "reward_per": REWARD_PER_PERSON,
                    "num_slots": num_slots,
                    "twitter_creador": twitter,
                    "estado": "Activa",
                    "slots_completados": 0,
                    "completados": []
                }
                datos.append(nueva)
                guardar_datos(datos)
                st.success("¡Tarea publicada con éxito!")
                st.rerun()

# ====================== ENVIAR COMPLETADO ======================
elif rol == "✅ Enviar Completado":
    st.subheader("📤 Enviar Prueba de Tarea")
    tarea_id = st.number_input("ID de la tarea", min_value=1, step=1)
    
    tarea = next((t for t in datos if t["id"] == tarea_id), None)
    if tarea:
        st.markdown(f"Tarea: {tarea['descripcion']}")
        tw = st.text_input("Tu Twitter @")
        link = st.text_input("Link del tweet que realizaste")
        cw = st.text_input("Tu CWallet ID (para recibir pago)")
        
        if st.button("Enviar Prueba"):
            completado = {
                "twitter": tw,
                "link": link,
                "cwallet": cw,
                "fecha": str(datetime.now())
            }
            tarea.setdefault("completados", []).append(completado)
            tarea["slots_completados"] = len(tarea["completados"])
            guardar_datos(datos)
            st.success("✅ Prueba enviada. Te pagaremos a tu CWallet una vez revisada.")
    else:
        st.error("Tarea no encontrada.")

# ====================== MODO ADMIN ======================
elif rol == "🔐 Modo Admin":
    st.subheader("🔐 Panel de Administración")
    
    password = st.text_input("Ingresa la contraseña de Administrador", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("✅ Acceso concedido - Bienvenido Admin")
        
        for i, t in enumerate(datos):
            if t.get("estado") == "Activa":
                with st.expander(f"#{t['id']} - {t['descripcion'][:70]}..."):
                    st.write(f"Progreso: {t.get('slots_completados',0)} / {t['num_slots']}")
                    st.write(f"Total a pagar en esta tarea: {round(t['reward_per'] * t.get('slots_completados',0), 3)} USDT")
                    
                    for comp in t.get("completados", []):
                        st.write(f"→ @{comp.get('twitter')} | {comp.get('cwallet')} | [Ver Tweet]({comp.get('link')})")
                    
                    if st.button("💰 Marcar como Pagada", key=f"pay_{i}"):
                        t["estado"] = "Finalizada"
                        guardar_datos(datos)
                        st.success("Tarea marcada como pagada")
    else:
        if password:
            st.error("❌ Contraseña incorrecta")

st.sidebar.success("CODEX v1.0 - Pagos Automáticos")
