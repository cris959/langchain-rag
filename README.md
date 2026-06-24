## 🚀 Pipeline RAG - Estrategia de Ingesta y Base Vectorial (Clase 02)   
Este módulo contiene el desarrollo práctico de la Clase 02, enfocado en la construcción de la primera etapa de un sistema RAG (Retrieval-Augmented Generation): la extracción, fragmentación (chunking), adaptación matemática e inyección de documentos en una base de datos vectorial en la nube.   
## 🛠️ Desafíos Técnicos Superados   
Durante el laboratorio se resolvieron múltiples retos de arquitectura y despliegue en el entorno de Google Colab:
* Migración de Dependencias de Conectores: Adaptación inmediata a los cambios de la API de Pinecone unificando el ecosistema bajo **langchain-pinecone** y la librería nativa unificada **pinecone**.
* Optimización de Recursos (CPU Bypass): Implementación de un adaptador personalizado (**AdaptadorSimulado3072Corregido**) para evitar la degradación y congelamiento del entorno de Colab al procesar modelos pesados en entornos locales de desarrollo.
* Control Estricto de Tipos de Datos (API Gateways): Resolución de conflictos de precisión numérica en la nube (**float64** a **float nativo**) asegurando la compatibilidad de vectores con la arquitectura estricta de Pinecone.
* Despliegue Independiente de Infraestructura Vectorial: Creación dinámica de un índice serverless remoto (**langchain-rag-cristian**) configurado a 3072 dimensiones con métrica de similitud coseno.   
## 🍓 La Frutilla del Postre: El Valor de la Discrepancia de Datos   
El hito más enriquecedor del proyecto surgió al contrastar las pruebas de recuperación semántica contra el entorno del instructor (**búsqueda del concepto "Robo de la tarjeta"**)

## 📊 Tabla Comparativa de Resultados   
| Métrica / Atributo | Entorno del Instructor | Nuestro Entorno (Christian) |
| :--- | :--- | :--- |
| **Score de Similitud** | `0.850714743` (Muy alto) | `0.046606019` (Bajo/Azar) |
| **Contenido Devuelto** | Bloque específico de emergencias y teléfonos de contacto en México. | Bloque genérico introductorio de la guía de beneficios generales. |
| **Origen Semántico** | Embeddings reales de Hugging Face. | Vectores simulados uniformes para optimización de CPU. |
| **Contexto del Documento** | Contrato Mastercard exclusivo para México. | Contrato consolidado Mastercard para Colombia/Latam. |


## 💡 Lección Aprendida y Sostenimiento del Conocimiento   
Esta divergencia no representó un error de código, sino una validación real de cómo opera la arquitectura de datos:   
1- Diferencia de Datos Base: El escaneo manual por texto plano demostró que la información de robos sí existía en nuestro entorno (**e.g., Fragmento #128 referente a pérdida de documentos en viajes o Fragmento #34 sobre robos en cajeros**), pero la redacción exacta difería por tratarse de contratos de distintas regiones geográficas (**México vs. Colombia/Latam**).   
2- Impacto de los Embeddings: Al utilizar un adaptador matemático simulado para resguardar la estabilidad del Colab, se evidenció empíricamente que la base de datos pierde la **"comprensión del lenguaje"** y recupera registros por pura lotería de distancias matemáticas. 

🧠 Conclusión del Analista: Resolver esta discrepancia nos obligó a auditar la base de datos celda por celda. Esto cimentó el conocimiento real del pipeline: ahora no solo sabemos cómo estructurar el código de memoria, sino que entendemos con precisión quirúrgica cómo influyen los datos de origen y los modelos matemáticos en las respuestas finales del RAG.   
## 📦 Tecnologías Utilizadas   
* LangChain Core / LangChain Pinecone   
* Pinecone Vector Database (Serverless AWS)   
* Python (Numpy, Regex)
___
## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](https://github.com/cris959/langchain-rag/blob/main/LICENSE) adjunto en este repositorio.

Copyright © 2026 [Christian Garay](https://github.com//cris959/langchain-rag) - Backend Developer.
