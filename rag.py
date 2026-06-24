import os
from dotenv import load_dotenv
# Agregamos el loader específico para PDFs
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader 
from transformers import AutoTokenizer
from langchain_text_splitters import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# 1. Configuración de entorno
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# 2. Carga y fragmentación de documentos (Corregido el loader para PDFs)
loader = DirectoryLoader('documentos', glob='*.pdf', loader_cls=PyPDFLoader)
pdfs = loader.load()

tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-m3')
splitter = CharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer=tokenizer, chunk_size=1250, chunk_overlap=150
)
fragmentos = splitter.split_documents(pdfs)

# 3. Base de datos vectorial local (FAISS + Ollama bge-m3)
embeddings = OllamaEmbeddings(model='bge-m3')
vector_store = FAISS.from_documents(documents=fragmentos, embedding=embeddings)
retriever = vector_store.as_retriever()

# 4. Diseño del Prompt (Se mantiene tu estructura)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Responde usando exclusivamente el contenido que se incluye a continuación. Genera una respuesta concisa. \n\nContexto:\n{contexto}"),
    ("human", "{query}")
])

# 5. Modelo de lenguaje local (Ollama gemma3:4b)
modelo = OllamaLLM(model="gemma3:4b")

# Función auxiliar para formatear los documentos recuperados a texto plano
def formatear_documentos(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 6. Construcción de la LCEL RAG Chain (Corregida)
rag_chain = (
    {
        "contexto": retriever | formatear_documentos,  # Busca y formatea a string
        "query": RunnablePassthrough()                 # Pasa la pregunta directo
    }
    | prompt 
    | modelo 
    | StrOutputParser()
)

# 7. Ejecución
pregunta = 'Cómo solicitar el seguro de viaje?'
resultado = rag_chain.invoke(pregunta)

print("\n🤖 Respuesta de Gemma 3:")
print(resultado)