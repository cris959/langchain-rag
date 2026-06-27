# 🦜 Asistente de Análisis de Datos con IA

> 🌐 **Probá la aplicación en vivo aquí:** [Ir a la App en Streamlit Cloud](https://cris959-agent-final.streamlit.app/)


Un agente inteligente desarrollado con **LangChain** y **Streamlit** que permite a los usuarios cargar archivos CSV y realizar análisis avanzados de datos mediante consultas en lenguaje natural, utilizando el modelo de lenguaje **Llama 3.3 (70B) a través de Groq**.

## 🚀 Características y Funcionalidades
*   **Análisis Dinámico:** Carga de archivos CSV y generación de respuestas basadas en el contexto de los datos.
*   **Orquestación con LangChain:** Uso de agentes ReAct (`AgentExecutor`) para razonar y decidir qué herramientas utilizar según la consulta.
*   **Reportes Automatizados:** Botones de acceso rápido para generar análisis estadísticos descriptivos e informaciones generales del dataset.
*   **Visualización Interactiva:** Generación de gráficos basados en las peticiones del usuario.
## 📸 Capturas de Pantalla

![captcha app](/assets/captcha.png)

![dashboard app](/assets/dashboard.png)

## 🔒 Capas de Seguridad en Producción (Versión Pública)
Para proteger la infraestructura y asegurar un uso justo de los recursos, la aplicación cuenta con un entorno blindado:
1.  **Control Anti-Bots:** Sistema de validación (Captcha nativo matemático) que filtra accesos automatizados maliciosos.
2.  **Límite Estricto de Cuotas:** Restricción de consumo a un máximo de **5 consultas diarias por usuario** mediante persistencia de cookies en el navegador.
3.  **Filtro Anti-Inyección de Prompts:** Capa de sanitización de entradas que detecta y bloquea palabras clave asociadas a intentos de bypass o jailbreak del System Prompt.
4.  **Control de Carga:** Restricción de tamaño para archivos pesados (Máximo 5MB).

## 🛠️ Tecnologías Utilizadas
*   **Backend & Agente:** Python, LangChain, ChatGroq (Llama 3.3 70B Versatile).
*   **Procesamiento de Datos:** Pandas.
*   **Interfaz de Usuario:** Streamlit, Streamlit Cookies Controller.

## 💻 Instalación y Uso Local (Sin Límites)
Si deseas utilizar la aplicación localmente en tu entorno de desarrollo sin las restricciones de cuota públicas, sigue estos pasos:

* **Clonar el repositorio:**
   ```
   bash
   git clone [https://github.com/cris959/langchain-rag.git](https://github.com/cris959/langchain-rag.git)
   cd langchain-rag
   git checkout proyecto-final
   ```

   💡 **¿No tenés un archivo a mano?** Descargá nuestro [Dataset de Prueba de Ejemplo](https://github.com/cris959/langchain-rag/raw/refs/heads/proyecto-final/data/datos_ejemplo.csv) (Clic derecho y "Guardar enlace como...") para probar todas las funciones de la app.
___
1- Crear y activar el entorno virtual:

   ````
   Bash    
python -m venv .venv
# En Windows:
.venv\Scripts\activate
   `````
2- Instalar las dependencias:

   ````
   Bash
pip install -r requirements.txt
   ````
3- Configurar las variables de entorno:
Crea un archivo **.env** en la raíz del proyecto y añade tu API Key:
```
GROQ_API_KEY="tu_gsk_token_aquí"
```
4- Iniciar la aplicación:
```
Bash
streamlit run app.py
```

## 📝 Licencia
Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](https://github.com/cris959/langchain-rag/blob/main/LICENSE) adjunto en este repositorio.

Copyright © 2026 [Christian Garay](https://github.com//cris959/langchain-rag) - Backend Developer.