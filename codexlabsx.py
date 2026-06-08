import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(page_title="codexlabsX", layout="wide")
st.title("🚀 codexlabsX - Gana Recompensas haciendo tareas en Twitter")
st.markdown("Plataforma de bounties en X (Twitter)")

# Configuración
PLATFORM_FEE = 3.0
TU_CWALLET = "TU_CWALLET_ID_AQUI"   # ← Cambia esto

DATA_FILE = "tareas_codexlabsX.json"

def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

datos = cargar_datos()

# Selector de rol / vista
rol = st.sidebar.selectbox("¿Qué quieres hacer?", 
    ["🧑‍🤝‍🧑 Ver Tareas Públicas", "➕ Crear Tarea", "✅ Enviar Completado", "🔐 Modo Administrador"])

# ====================== VISTA PÚBLICA ======================
if rol == "🧑‍🤝‍🧑 Ver Tareas Públicas":
    st.subheader("Tareas Disponibles")
    st.caption("Elige una tarea, hazla en Twitter y envía tu prueba")
    
    tareas_activas = [t for t in datos if t.get("estado") == "Activa"]
    if tareas_activas:
        for t in tareas_activas:
            faltan = t["num_slots"] - t.get("slots_completados", 0)
            if faltan > 0:
                with st.container(border=True):
                    st.write(f"#{t['id']} - {t['descripcion']}")
                    st.write(f"💰 Recompensa: {t['reward_per']} USDT por persona")
                    st.write(f"👥 Slots disponibles: {faltan} de {t['num_slots']}")
                    st.caption(f"Creador: @{t.get('twitter_creador', 'Anónimo')}")
    else:
        st.info("No hay tareas disponibles en este momento.")

# ====================== CREAR TAREA ======================
elif rol == "➕ Crear Tarea":
    st.subheader("Publicar Nueva Tarea")
    st.warning(f"Debes pagarme primero {PLATFORM_FEE} USDT + las recompensas a: {TU_CWALLET}")
    
    with st.form("crear"):
        desc = st.text_area("Describe la tarea claramente")
        reward_per = st.number_input("Recompensa por persona (USDT)", value=0.01, step=0.001, format="%.3f")
        num_slots = st.number_input("Cuántas personas quieres", value=100, min_value=1)
        twitter = st.text_input("Tu Twitter @")
        
        total = round(reward_per * num_slots + PLATFORM_FEE, 3)
        st.success(f"Total a pagar: {total} USDT")
        
        if st.form_submit_button("Publicar Tarea"):
            nueva = {
                "id": len(datos) + 1,
                "descripcion": desc,
                "reward_per": reward_per,
                "num_slots": num_slots,
                "twitter_creador": twitter,
                "estado": "Activa",
                "slots_completados": 0,
                "completados": []
            }
            datos.append(nueva)
            guardar_datos(datos)
            st.success("¡Tarea publicada!")
            st.rerun()

# ====================== ENVIAR COMPLETADO ======================
elif rol == "✅ Enviar Completado":
    st.subheader("Enviar Prueba de Tarea")
    tarea_id = st.number_input("ID de la tarea", min_value=1, step=1)
    
    tarea = next((t for t in datos if t["id"] == tarea_id), None)
    if tarea:
        st.write(f"Tarea: {tarea['descripcion'][:100]}...")
        tw = st.text_input("Tu Twitter @")
        link = st.text_input("Link del tweet que hiciste")
        cw = st.text_input("Tu Cwallet ID o Email")
        
        if st.button("Enviar Prueba"):
            st.success("✅ Prueba enviada. El administrador la revisará y te pagará si está correcta.")
            # Aquí se podría agregar notificación futura
    else:
        st.error("Tarea no encontrada.")

# ====================== MODO ADMIN ====================== 
elif rol == "🔐 Modo Administrador":
    st.subheader("Panel de Control (Solo tú)")
    for i, t in enumerate(datos):
        if t.get("estado") == "Activa":
            with st.expander(f"Tarea #{t['id']} - {t['descripcion'][:50]}..."):
                st.write(f"Progreso: {t.get('slots_completados',0)}/{t['num_slots']}")
                for comp in t.get("completados", []):
                    st.write(f"→ @{comp.get('twitter')} - {comp.get('link')}")
                
                if st.button("Marcar como Pagada (Admin)", key=f"pay{i}"):
                    t["estado"] = "Finalizada"
                    guardar_datos(datos)
                    st.success("Tarea marcada como pagada")

st.sidebar.info("Cambia tu Cwallet en el código")