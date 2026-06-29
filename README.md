# Sistema RAG Avanzado con Estrategia Multi-Query

Este proyecto implementa un sistema de **Generación Aumentada por Recuperación (RAG)** avanzado y completamente local. Su objetivo principal es superar las limitaciones de la búsqueda por similitud tradicional mediante el uso de un patrón de expansión de consultas conocido como **Multi-Query (Multi-consulta)**.

## 🚀 Características del Proyecto

* **Generador de Perspectivas (Multi-Query):** Integración de un modelo ágil (`llama3.2:1b`) encargado de reescribir la consulta original del usuario en 5 preguntas sinónimas y alternativas para ampliar el espectro de búsqueda semántica.
* **Filtro Semántico de Emergencia:** Lógica personalizada en Python que detecta y omite automáticamente aquellas consultas derivadas que alucinen o desvíen el foco del tema central (evitando ruidos informativos sobre pasajes, vuelos, etc.).
* **Consolidación de Contexto Único:** Eliminación de fragmentos de documentos duplicados recuperados por las múltiples consultas en FAISS, optimizando y reduciendo la carga de contexto enviada al LLM.
* **Optimización de Parámetros (Bypass de Bloqueo):** Configuración explícita de la ventana de contexto y límite de tokens para evitar que el motor local de Ollama en Windows trunque las respuestas largas al procesar información densa.

## 🛠️ Modelos Utilizados (Ollama)

Para ejecutar este script de forma fluida, es necesario contar con los siguientes modelos descargados localmente:

* **Modelo Principal y Query Rewriter:** `llama3.2:1b` (Configurado en ambos bloques debido a su estabilidad con strings largos y velocidad de respuesta en local).
* **Modelo de Embeddings:** `bge-m3:567m` (Para la indexación y búsquedas semánticas eficientes en FAISS).

---

## 🏗️ Guía de Configuración e Implementación

### 1. Requisitos e Instalación de Dependencias
Asegúrate de inicializar tu entorno virtual e instalar los paquetes base necesarios para el ecosistema:
```bash
pip install langchain-ollama langchain-community faiss-cpu transformers pydantic python-dotenv
```

2. Configuración del Entorno (.env)
Crea un archivo **.env** en la raíz de tu espacio de trabajo para habilitar el sistema de trazas y monitoreo en LangSmith:

````
Fragmento de código
GEMINI_API_KEY="tu_api_key_aquí"
LANGSMITH_TRACING="true"
LANGSMITH_API_KEY="tu_langsmith_api_key_aquí"
````

⚠️ Nota de seguridad: Este archivo contiene credenciales sensibles y ya se encuentra excluido mediante el archivo **.gitignore**.

3. Configuración y Bypass de los Modelos (Sección 5)
Para evitar que el backend local corte la generación en la primera palabra tras recibir el contexto extendido, aplicamos los parámetros **num_predict** y **num_ctx** directo en la inicialización:

````Python
# 5. Modelos de lenguaje locales (Configurados con bypass de tokens)
modelo_principal = OllamaLLM(
    model="llama3.2:1b", 
    temperature=0.0,
    num_predict=512,  # Fuerza al modelo a generar respuestas completas (hasta 512 tokens)
    num_ctx=4096      # Amplía la memoria de contexto para procesar múltiples fragmentos de FAISS
)

query_model = OllamaLLM(
    model="llama3.2:1b", 
    temperature=0.0
)
````
4. Estructura del Pipeline (LCEL)
La cadena de ejecución avanzada conecta de forma declarativa el expansor de consultas utilizando **RunnableLambda** para asegurar la total compatibilidad de tipos en el flujo de datos:

````Python
rag_chain = (
    {
        "contexto": {"question": RunnablePassthrough()} | RunnableLambda(recuperar_multi_query),
        "query": RunnablePassthrough()                 
    }
    | prompt_sistema 
    | modelo_principal 
    | StrOutputParser()
)
````

## 🖥️ Ejecución del Sistema
1- Crea un directorio llamado **/documentos** en la raíz del proyecto y coloca allí tus archivos PDF de soporte.

2- Lanza el pipeline completo ejecutando el script principal desde tu terminal:

````Bash
python rag.py
````

El sistema desplegará en la consola las 5 perspectivas limpias procesadas por el rewriter antes de consolidar la respuesta final estructurada extraída de la base de datos vectorial.

## 📝 Licencia
Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](https://github.com/cris959/langchain-rag/blob/main/LICENSE.txt) adjunto en este repositorio.

Copyright © 2026 [Christian Garay](https://github.com//cris959/langchain-rag) - Backend Developer.
