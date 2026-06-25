import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader 
from transformers import AutoTokenizer
from langchain_text_splitters import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# 1. Configuración de entorno
load_dotenv()

# 2. Carga y fragmentación de documentos
loader = DirectoryLoader('documentos', glob='*.pdf', loader_cls=PyPDFLoader)
pdfs = loader.load()

tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-m3')
splitter = CharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer=tokenizer, chunk_size=1250, chunk_overlap=150
)
fragmentos = splitter.split_documents(pdfs)

# 3. Base de datos vectorial local (FAISS + Ollama bge-m3:567m)
embeddings = OllamaEmbeddings(model='bge-m3:567m')
vector_store = FAISS.from_documents(documents=fragmentos, embedding=embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# 4. Diseño del Prompt del Sistema (Para la respuesta final concisa)
prompt_sistema = ChatPromptTemplate.from_template(
    "Eres un asistente que responde de forma concisa basándose ÚNICAMENTE en el siguiente contexto.\n\n"
    "CONTEXTO:\n{contexto}\n\n"
    "PREGUNTA:\n{query}\n\n"
    "RESPUESTA:"
)

# 5. Modelos de lenguaje locales
modelo_principal = OllamaLLM(
    model="llama3.2:1b", 
    temperature=0.0,
    num_predict=512,  # Le da soga para escribir hasta 512 tokens sin cortarse
    num_ctx=4096      # Ventana de contexto amplia para procesar los PDFs
)

query_model = OllamaLLM(
    model="llama3.2:1b", 
    temperature=0.0
)

# 6. MÓDULO: Multi-Query (Prompt ajustado para evitar aviones)
template_multipregunta = """
Tu única tarea es generar exactamente cinco versiones diferentes, alternativas y sinónimas de la pregunta original del usuario.
Estas variantes deben enfocarse ESTRICTAMENTE en el mismo tema central (por ejemplo: seguros, coberturas, trámites médicos). No inventes temas nuevos de viajes o transporte.
NO agregues introducciones, NO saludes, NO expliques nada.
Devuelve SOLO las 5 preguntas, una por línea, sin números y sin viñetas.

EJEMPLO:
Pregunta original: ¿Dónde atienden los médicos en Córdoba?
Variantes:
¿Cuál es la cartilla de centros médicos en Córdoba?
¿Qué clínicas disponibles hay en la zona de Córdoba?
¿Dónde puedo consultar los centros de atención médica de Córdoba?
¿Cuáles son los hospitales disponibles en Córdoba?
¿Cómo encuentro la lista de médicos en Córdoba?

Ahora genera las 5 variantes para la siguiente pregunta:
Pregunta original: {question}
Variantes:
"""
prompt_multipregunta = PromptTemplate.from_template(template_multipregunta)     
chain_multipregunta = prompt_multipregunta | query_model | StrOutputParser()

# --- FUNCIONES AUXILIARES (Declaradas arriba de la cadena para evitar NameError) ---

def formatear_documentos(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def recuperar_multi_query(inputs):
    pregunta_original = inputs["question"]
    
    # Generamos variantes con el modelo de 1b
    bloque_preguntas = chain_multipregunta.invoke({"question": pregunta_original})
    
    # Limpiamos y estructuramos
    lista_preguntas = [p.strip() for p in bloque_preguntas.split("\n") if p.strip() and "?" in p]
    
    print("\n📋 Las perspectivas reales generadas:")
    for i, pr in enumerate(lista_preguntas[:5], 1):
        print(f"  {i}. {pr}")
    print("")

    documentos_unicos = {}
    
    # 1. Buscamos primero con la original
    for doc in retriever.invoke(pregunta_original):
        documentos_unicos[doc.page_content] = doc
        
    # 2. Buscamos con las variantes aplicando filtro de seguridad
    for p in lista_preguntas[:5]:
        if "avión" in p.lower() or "aeropuerto" in p.lower() or "vuelo" in p.lower() or "boleto" in p.lower():
            continue
        for doc in retriever.invoke(p):
            documentos_unicos[doc.page_content] = doc
            
    lista_final_docs = list(documentos_unicos.values())
    return formatear_documentos(lista_final_docs)


# 7. Construcción de la LCEL RAG Chain Avanzada (Multi-Query)
rag_chain = (
    {
        "contexto": {"question": RunnablePassthrough()} | RunnableLambda(recuperar_multi_query),
        # Pasamos la pregunta original limpia
        "query": RunnablePassthrough()                 
    }
    | prompt_sistema 
    | modelo_principal 
    | StrOutputParser()
)

# 8. Ejecución Completa
pregunta_usuario = 'Cómo solicitar el seguro de viaje?'

print(f"🔄 Pregunta original: '{pregunta_usuario}'")
print("🤖 Ejecutando Multi-Query RAG...")

resultado = rag_chain.invoke(pregunta_usuario)

print("🤖 Respuesta final de llama3.2 (1b):")
print(resultado)