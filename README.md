# Desafíos Clase 01: LangChain & RAG (Retrieval-Augmented Generation)

Este directorio contiene los desarrollos y desafíos resueltos correspondientes a la **Clase 01** del módulo de Inteligencia Artificial. El objetivo principal de esta sesión fue construir el pipeline de ingesta de datos y el circuito de recuperación semántica para un bot de asistencia inteligente utilizando documentos oficiales de Mastercard.

---

## 🛠️ Tecnologías y Frameworks Utilizados

*   **LangChain / LangChain Core:** Arquitectura de orquestación para LLMs y flujo LCEL (*LangChain Expression Language*).
*   **Google Gemini (gemini-2.5-flash):** Modelo de lenguaje de producción para la generación de respuestas contextualizadas.
*   **Hugging Face (bge-large-en-v1.5):** Modelo local y open-source para la generación eficiente de embeddings vectoriales.
*   **Pinecone:** Base de datos vectorial en la nube (Cloud Vector Store) para el almacenamiento e indexación de fragmentos.
*   **Google Colab:** Entorno de desarrollo interactivo basado en la nube.

---

## 🚀 Desafíos Resueltos & Arquitectura del Proyecto

### 1. Ingesta y Procesamiento de Documentos
*   Carga y procesamiento de PDFs institucionales (información de asistencia y contingencias de Mastercard).
*   Segmentación inteligente del texto en fragmentos (**chunks**) optimizados para la posterior búsqueda semántica.

### 2. El Bypass de Embeddings (Solución de Compatibilidad)
Ante un bloqueo de disponibilidad regional/versión en la API nativa de Google AI Studio (`text-embedding-004`), se diseñó un desvío técnico estratégico:
*   Se migró el backend de embeddings a **Hugging Face** de forma 100% local dentro del entorno de ejecución.
*   **Adaptador de Dimensiones (Padding Matemático):** El índice de Pinecone requería estrictamente vectores de **3072 dimensiones** (configuración estándar del curso). Como el modelo open-source genera por defecto vectores de **1024 dimensiones**, se implementó un *Wrapper* personalizado en Python (`AdaptadorEmbeddings3072`). Este componente procesa el texto e inyecta dinámicamente un acolchado (*padding*) de ceros al final del vector, estirándolo a las 3072 dimensiones requeridas sin corromper la semántica y logrando un bypass exitoso.

#### 📊 Evidencia de Indexación en Pinecone
A continuación se adjunta la captura de la consola de administración donde se valida la estructura y la correcta recepción de los vectores extendidos en la nube:

<img width="1912" height="1080" alt="pinecone-dashboard" src="https://github.com/user-attachments/assets/738b16c0-7d90-423b-825f-435e3e9144c9" />

<img width="1911" height="1080" alt="pinecone-indexes" src="https://github.com/user-attachments/assets/d0104a61-31ea-4af3-9345-15e6efae33ce" />



### 3. Recuperación e Integración de la Cadena (RAG)
*   Configuración del componente `Retriever` en LangChain conectado al índice en la nube (`mastercard-rag`).
*   Construcción de una plantilla de prompt del sistema estructurada bajo buenas prácticas de seguridad para evitar alucinaciones, restringiendo al modelo a responder **única y exclusivamente** con el contexto provisto.
*   Creación y validación de la cadena final unificada a través de operadores pipe: `prompt | modelo | parseador`.

---

## 🔍 Diagnóstico y Monitoreo

Para garantizar la transparencia del flujo de datos, se incorporó el sistema de depuración global de LangChain:
```python
from langchain.globals import set_debug
set_debug(True)
```
Esto permite auditar en tiempo real desde la consola de Google Colab los metadatos recuperados, el prompt final inyectado y los tokens exactos consumidos por la API de Gemini.

Nota de Seguridad: Las credenciales y claves de acceso (**PINECONE_API_KEY**; **GEMINI_API_KEY** y **GROQ_API_KEY**) se manejan de forma aislada mediante el gestor de secretos de Google Colab (**userdata.get()**) para mitigar riesgos de exposición en repositorios públicos.
___
## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](https://github.com/cris959/langchain-rag/blob/main/LICENSE.txt) adjunto en este repositorio.

Copyright © 2026 [Christian Garay](https://github.com//cris959/langchain-rag) - Backend Developer.
