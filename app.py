import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.agents import create_react_agent
from langchain.agents import AgentExecutor
from herramientas import crear_herramientas
from streamlit_cookies_controller import CookieController

# Cargar variables de entorno
load_dotenv()

# Inicia la aplicación
st.set_page_config(page_title="Asistente de Análisis de Datos con IA", layout="centered")
st.title("🦜 Asistente de Análisis de Datos con IA")

# ==========================================
# CAPA 1: ANTI-BOTS (CAPTCHA NATIVO)
# ==========================================
if "bot_verificado" not in st.session_state:
    st.session_state["bot_verificado"] = False
    st.session_state["num1"] = random.randint(1, 10)
    st.session_state["num2"] = random.randint(1, 10)

if not st.session_state["bot_verificado"]:
    st.markdown("### 🤖 Verificación de Seguridad")
    st.write("Por favor, resuelve esta operación para verificar que no eres un bot y acceder:")
    n1, n2 = st.session_state["num1"], st.session_state["num2"]
    
    respuesta_usuario = st.number_input(f"¿Cuánto es {n1} + {n2}?", step=1, value=0)
    if st.button("Verificar ingreso"):
        if respuesta_usuario == (n1 + n2):
            st.session_state["bot_verificado"] = True
            st.success("¡Verificación exitosa!")
            st.rerun()
        else:
            st.error("Respuesta incorrecta. Inténtalo de nuevo.")
    st.stop()

# ==========================================
# CAPA 2: LÍMITE DE 5 PETICIONES DIARIAS (COOKIES)
# ==========================================
controller = CookieController()
hoy = datetime.now().strftime("%Y-%m-%d")

cookie_fecha = controller.get("fecha_peticiones")
cookie_contador = controller.get("contador_peticiones")

if cookie_fecha != hoy:
    peticiones_hoy = 0
else:
    peticiones_hoy = int(cookie_contador) if cookie_contador is not None else 0

LIMITE_DIARIO = 5

def registrar_peticion():
    global peticiones_hoy
    peticiones_hoy += 1
    controller.set("fecha_peticiones", hoy)
    controller.set("contador_peticiones", str(peticiones_hoy))

# ==========================================
# CAPA 3: FILTRO ANTI-INYECCIÓN DE PROMPTS
# ==========================================
def es_input_seguro(texto_usuario):
    palabras_prohibidas = [
        "ignore previous instructions", "ignora las instrucciones", 
        "system prompt", "delete", "drop table", "revela tu prompt", 
        "output everything", "cambia tus instrucciones"
    ]
    query_limpia = texto_usuario.lower()
    for palabra in palabras_prohibidas:
        if palabra in query_limpia:
            return False
    return True

# --- DESCRIPCIÓN DE LA INTERFAZ ---
st.info("🔒 Esta aplicación es pública. Cuenta con un límite de 5 consultas diarias por navegador y filtros de seguridad.")

# Upload de CSV
st.markdown("### 📁 Realiza la carga de tu archivo CSV")
archivo_cargado = st.file_uploader("Selecciona un archivo CSV", type="csv", label_visibility="collapsed")

if archivo_cargado:
    # CAPA EXTRA: CONTROL DE TAMAÑO DEL ARCHIVO (Máximo 5MB)
    MAX_FILE_SIZE_MB = 10
    if archivo_cargado.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"❌ El archivo excede el límite máximo de {MAX_FILE_SIZE_MB}MB permitido en la versión pública.")
        st.stop()

    df = pd.read_csv(archivo_cargado)
    st.success("Archivo cargado exitosamente!")
    
    # Barra lateral con estado de la cuota del usuario
    st.sidebar.markdown("### 📊 Tu Cuota Diaria")
    st.sidebar.progress(peticiones_hoy / LIMITE_DIARIO)
    st.sidebar.write(f"Consultas hoy: **{peticiones_hoy} de {LIMITE_DIARIO}**")

    st.markdown("### 🔍 Primeras filas de tu conjunto de datos")
    st.dataframe(df.head())

    # 1. Inicialización del LLM
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile", 
        temperature=0
    )

    # 2. Inicialización de herramientas
    tools = crear_herramientas(df)

    # 3. Muestra del DF
    df_head = df.head().to_markdown()

    # 4. Construcción dinámica del prompt (Evita bloqueos de renderizado)
    partes_prompt = [
        "Eres un asistente de análisis de datos que responde obligatoriamente en castellano.\n",
        "Tienes acceso a un dataframe pandas llamado `df`.\n",
        "Aquí están las primeras filas del DataFrame:\n{df_head}\n\n",
        "Responde a la pregunta de entrada de la mejor manera posible.\n",
        "Tienes acceso a las siguientes herramientas:\n{tools}\n\n",
        "Usa estrictamente el siguiente formato:\n\n",
        "Question: La pregunta de entrada que debes responder\n",
        "Thought: Debes siempre pensar en lo que debes hacer\n",
        "Action: La acción que será ejecutada, debe ser una de las [{tool_names}]\n",
        "Action Input: La entrada exacta para la acción\n",
        "Observation: El resultado de la acción\n",
        "... (este ciclo se puede repetir)\n",
        "Thought: Ya tengo el resultado final.\n",
        "Final Answer: La respuesta final detallada en castellano.\n\n",
        "¡No repitas la pregunta dentro del Thought! Si obtienes el resultado, ve directo a Final Answer.\n\n",
        "Comienza!\n\n",
        "Question: {input}\n",
        "Thought: {agent_scratchpad}"
    ]
    
    prompt_react_es = PromptTemplate(
        input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
        partial_variables={"df_head": df_head},
        template="".join(partes_prompt)
    )

    # 5. Orquestación del Agente
    agente = create_react_agent(llm=llm, tools=tools, prompt=prompt_react_es)
    orquestador = AgentExecutor(agent=agente, tools=tools, verbose=True, handle_parsing_errors=True)

    # --- INTERFAZ DE ACCIONES RÁPIDAS ---
    st.markdown("---")
    st.markdown("## ⚡ Acciones rápidas")

    # Reporte de Informaciones Generales
    if st.button("📄 Reporte de Informaciones Generales", key="boton_reporte_general"):
        if peticiones_hoy >= LIMITE_DIARIO:
            st.error("Límite diario alcanzado.")
        else:
            with st.spinner("Generando Reporte 🦜"):
                respuesta = orquestador.invoke({"input": "Quiero un reporte con información sobre los datos"})
                st.session_state['reporte_general'] = respuesta["output"]
                registrar_peticion()
                st.rerun()

    if 'reporte_general' in st.session_state:
        with st.expander("Resultado: Reporte de Informaciones Generales"):
            st.markdown(st.session_state['reporte_general'])

    # Reporte de estadísticas descriptivas
    if st.button("📄 Reporte de estadísticas descriptivas", key="boton_reporte_estadisticas"):
        if peticiones_hoy >= LIMITE_DIARIO:
            st.error("Límite diario alcanzado.")
        else:
            with st.spinner("Generando Reporte 🦜"):
                respuesta = orquestador.invoke({"input": "Quiero un Reporte de estadísticas descriptivas"})
                st.session_state['reporte_estadisticas'] = respuesta["output"]
                registrar_peticion()
                st.rerun()

    if 'reporte_estadisticas' in st.session_state:
        with st.expander("Resultado: Reporte de estadísticas descriptivas"):
            st.markdown(st.session_state['reporte_estadisticas'])
   
    # --- SECCIÓN DE PREGUNTAS ABIERTAS ---
    st.markdown("---")
    st.markdown("## 🔎 Preguntas sobre los datos")
    pregunta_sobre_datos = st.text_input("Realiza una pregunta sobre los datos", max_chars=150)
    
    if st.button("Responder pregunta", key="responder_pregunta_datos"):
        if not pregunta_sobre_datos:
            st.warning("Por favor, escribe una pregunta.")
        elif not es_input_seguro(pregunta_sobre_datos):
            st.error("🚨 Actividad sospechosa detectada. Consulta bloqueada por motivos de seguridad.")
        elif peticiones_hoy >= LIMITE_DIARIO:
            st.error("Has agotado tus 5 preguntas de hoy.")
        else:
            with st.spinner("Analizando los datos 🦜"):
                respuesta = orquestador.invoke({"input": pregunta_sobre_datos})
                st.markdown(respuesta["output"])
                registrar_peticion()
                st.rerun()

    # --- SECCIÓN DE GRÁFICOS INTERACTIVOS ---
    st.markdown("---")
    st.markdown("## 📊 Crear gráfico con base en una pregunta")

    pregunta_grafico = st.text_input("¿Qué deseas visualizar?", max_chars=150)
    if st.button("Generar gráfico", key="generar_grafico"):
        if not pregunta_grafico:
            st.warning("Por favor, describe el gráfico.")
        elif not es_input_seguro(pregunta_grafico):
            st.error("🚨 Consulta bloqueada por seguridad.")
        elif peticiones_hoy >= LIMITE_DIARIO:
            st.error("Has agotado tus cuotas de hoy.")
        else:
            with st.spinner("Generando el gráfico 🦜"):
                palabras_clave = pregunta_grafico.lower()
                if "clima" in palabras_clave and "tiempo" in palabras_clave:
                    st.markdown("### 📈 Promedio de tiempo de entrega por clima")
                    data_grafico = df.groupby('clima')['tiempo_entrega'].mean().reset_index()
                    st.bar_chart(data=data_grafico, x='clima', y='tiempo_entrega', use_container_width=True)
                    registrar_peticion()
                else:
                    respuesta = orquestador.invoke({"input": pregunta_grafico})
                    st.markdown(respuesta["output"])
                    registrar_peticion()