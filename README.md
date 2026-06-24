# Pipeline RAG Local con LangChain, Ollama y FAISS 🚀

Este proyecto implementa una arquitectura de **Generación Aumentada por Recuperación (RAG)** ejecutada de forma 100% local. El sistema es capaz de leer documentos PDF empotrados en una carpeta, procesar su contenido semántico mediante embeddings vectoriales y responder consultas precisas utilizando un Modelo de Lenguaje (LLM) local, garantizando la privacidad absoluta de los datos.

---

## 🛠️ Stack Tecnológico & Dependencias

El entorno virtual (`.venv`) utiliza las siguientes librerías core de Python:

* **`langchain-ollama`**: Integración oficial para conectar LangChain con el servidor local de Ollama.
* **`langchain-community`**: Módulos comunitarios que proveen los cargadores de documentos del sistema de archivos.
* **`pypdf`**: Motor interno requerido para la extracción y parseo de texto desde archivos PDF.
* **`transformers` & `huggingface-hub`**: Utilizados exclusivamente para descargar y ejecutar el tokenizador optimizado en español.
* **`faiss-cpu`**: Biblioteca de Facebook AI Similarity Search optimizada para CPU, utilizada como base de datos vectorial en memoria.
* **`python-dotenv`**: Gestor de variables de entorno para credenciales seguras.

---

## 🏗️ Arquitectura del Código e Importaciones (`rag.py`)

El script principal se estructura bajo los siguientes componentes y librerías importadas:

```python
import os
from dotenv import load_dotenv
```

### 1. Carga de Documentos
```
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader 
```

### 2. Tokenización y Fragmentación (Text Splitting)
```
from transformers import AutoTokenizer
from langchain_text_splitters import CharacterTextSplitter
```
### 3. Modelos de Ollama e Infraestructura Vectorial
```
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import FAISS
```
### 4. Orquestación de Cadenas (LCEL) y Prompts
```
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
```

## 📋 Flujo de Ejecución del Pipeline:
1- Ingesta: **DirectoryLoader** + **PyPDFLoader** escanean la carpeta **./documentos/** y extraen el texto crudo de los archivos **.pdf**.

2- Fragmentación: Se descarga el tokenizador de código abierto **BAAI/bge-m3** vía **transformers** para picar los textos en fragmentos balanceados de 1250 tokens con un solapamiento (overlap) de 150 tokens.

3- Indexación (Embeddings): Los fragmentos de texto se envían al modelo local **bge-m3** en Ollama para transformarlos en vectores numéricos, los cuales se indexan inmediatamente dentro de la base de datos FAISS.

4- Recuperación y Síntesis: Al realizar una consulta, la base de datos recupera los fragmentos con mayor similitud de coseno, los formatea a texto plano e inyecta el contexto junto con la pregunta en un **ChatPromptTemplate**. El LLM local **gemma3:4b** procesa el prompt y genera una respuesta precisa y compacta.

## ⚙️ Configuración del Entorno (.env)
Para activar el rastreo detallado de los componentes de la cadena en la plataforma web de desarrollo, se requiere configurar las siguientes variables de entorno:

````
LANGSMITH_TRACING="true"
LANGSMITH_API_KEY="tu_api_key_de_langsmith_aqui"
LANGSMITH_PROJECT="clase-04-rag-local"
````
## 🚀 Instrucciones para Ejecución Local
1- Asegurar los Modelos en Ollama:
Antes de correr el script, el servidor local de Ollama debe tener descargados ambos modelos corriendo los comandos:

```Bash
ollama pull bge-m3
ollama pull gemma3:4b
```

2- Ejecutar el Script:
Con el entorno virtual activo, lanzar el pipeline desde la consola:
```Bash
python rag.py
```
## 📊 Monitoreo y Trazabilidad con LangSmith

Para validar el comportamiento de la arquitectura LCEL y comprobar los tiempos de respuesta de los modelos locales, se integró el rastreo de **LangSmith**. A continuación se detallan las capturas de la traza de ejecución del pipeline:

### 1. Historial de Ejecuciones del Proyecto
Muestra el registro de cada llamada realizada desde la terminal de VS Code, el estado de éxito de la cadena y la latencia total del proceso RAG.
___
![alt text](langsmith_dashboard.png)

### 2. Configuración de la API Key
Interfaz dentro del menú *Settings > API Keys* donde se generan y administran los tokens de acceso seguros necesarios para vincular el archivo `.env` con la plataforma.
___
![alt text](langsmith_apikey.png)
___
## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](https://github.com/cris959/langchain-rag/blob/main/LICENSE) adjunto en este repositorio.

Copyright © 2026 [Christian Garay](https://github.com//cris959/langchain-rag) - Backend Developer.