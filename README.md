# Local LangChain RAG System 🚀

Este repositorio contiene un sistema completo de **Generación Aumentada por Recuperación (RAG)** avanzado, diseñado para funcionar de manera 100% local y eficiente. A través de un enfoque evolutivo, el proyecto implementa desde cargas básicas de información hasta pipelines con expansión de consultas (*Multi-Query*) y optimización de infraestructura local utilizando el ecosistema de **LangChain** y **Ollama**.

El sistema está preparado para indexar documentación técnica corporativa (en formato PDF) y responder consultas complejas basándose estrictamente en el contexto extraído, mitigando por completo las alucinaciones.

---

## 🗺️ Mapa de Desarrollo del Proyecto

El sistema fue construido de manera incremental, dividiéndose en cuatro grandes etapas de arquitectura:

### 📑 1. Ingesta y Fragmentación Semántica
* **Carga de Documentos:** Uso de `DirectoryLoader` y `PyPDFLoader` de LangChain para la lectura automatizada de archivos dentro de la carpeta `/documentos`.
* **Tokenización HuggingFace:** Implementación de `CharacterTextSplitter` basado en el tokenizador de `BAAI/bge-m3` para garantizar cortes semánticos precisos a lo largo del texto (Configurado con `chunk_size=1250` y `chunk_overlap=150`).

### 🗄️ 2. Vectorización e Indexación Local
* **Embeddings de Alta Performance:** Uso local del modelo `bge-m3:567m` a través de Ollama para la representación vectorial del texto.
* **Base de Datos Vectorial Local:** Integración con **FAISS (Facebook AI Similarity Search)** para el almacenamiento de vectores en memoria y la ejecución de búsquedas rápidas por similitud de coseno.

### ⛓️ 3. Orquestación con LangChain (LCEL)
* **Diseño de Prompts del Sistema:** Configuración de plantillas estructuradas e hiper-directas para blindar el comportamiento del modelo e instruirlo a responder utilizando exclusivamente los fragmentos provistos.
* **Pipeline Declarativo:** Construcción de la cadena utilizando **LCEL (LangChain Expression Language)** para conectar de punta a punta el flujo de entrada, el extractor (*retriever*), el prompt, el LLM y el formateador de salida.

### 🧠 4. Patrón Avanzado Multi-Query & Infraestructura Local
* **Generador de Perspectivas:** Uso de `llama3.2:1b` como un *Query Rewriter* optimizado mediante técnicas *Few-Shot* para generar 5 variantes sinónimas de la pregunta del usuario.
* **Filtros de Seguridad Antialucinación:** Lógica intermedia en Python integrada mediante `RunnableLambda` para sanitizar las variantes generadas, eliminando conceptos desviados antes de consultar a FAISS.
* **Bypass de Tokens en Ollama:** Optimización del backend en Windows configurando explícitamente `num_predict=512` y `num_ctx=4096` en la inicialización del `OllamaLLM` para evitar cortes de texto inesperados ante contextos densos.

---

## 🛠️ Stack Tecnológico y Modelos

* **Framework de Orquestación:** LangChain & LangChain Core (v3).
* **Base de Datos Vectorial:** FAISS (CPU).
* **Modelos de Lenguaje Locales (Ollama):**
  * `llama3.2:1b` (Orquestador de consultas y Cerebro principal de generación).
  * `bge-m3:567m` (Modelo de incrustaciones / embeddings).
* **Monitoreo:** Conexión nativa con **LangSmith** para el rastreo (*tracing*) y debug de cadenas en tiempo real.

---

## 🔑 Configuración del Entorno (`.env`)

Crea un archivo `.env` en la raíz del proyecto para habilitar las API keys de soporte y el sistema de trazas:

```env
GEMINI_API_KEY="tu_api_key_aquí"
LANGSMITH_TRACING="true"
LANGSMITH_API_KEY="tu_langsmith_api_key_aquí"
```
## 📦 Instalación y Uso
1. Clonar el repositorio e ingresar al directorio:
````
git clone [https://github.com/cris959/langchain-rag.git](https://github.com/cris959/langchain-rag.git)
cd langchain-rag
````
2. Instalar dependencias del entorno virtual:
````
pip install langchain-ollama langchain-community faiss-cpu transformers pydantic python-dotenv
````
3. Ejecutar el Pipeline RAG:
Asegúrate de tener corriendo tu servicio de Ollama local, coloca tus PDFs en **/documentos** y lanza el script principal:
```Bash
python rag.py
```
___
## 📝 Licencia
Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo LICENSE adjunto en este repositorio.

Copyright © 2026 Christian Garay - Backend Developer.

 
