import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from langchain.agents import Tool
from langchain_experimental.tools import PythonAstREPLTool

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(
    api_key = GROQ_API_KEY,
    model_name = 'llama-3.3-70b-versatile', # 'llama-3.3-70b-specdec',  #'llama-3.1-70b-versatile', deprecada
    temperature = 0
)

# --- NOTA: Asegúrate de cargar o definir tu variable 'df' globalmente 
# o antes de instanciar/invocar las herramientas en tu flujo de Streamlit.

# Herramienta de informaciones
@tool
def informacion_df(pregunta: str) -> str:
    """
    Utiliza esta herramienta siempre que el usuario solicite informaciones generales sobre el
    DataFrame, incluyendo el número de columnas y filas, nombres de las columnas y sus tipos de 
    datos, conteo de datos nulos y duplicados para dar un panorama general sobre el archivo.
    """
    # Accedemos al df del contexto global o del estado de la app
    global df 
    
    shape = df.shape
    columns = df.dtypes
    nulos = df.isnull().sum()
    nans_str = df.apply(lambda col: col[~col.isna()].astype(str).str.strip().str.lower().eq('nan').sum())
    duplicados = df.duplicated().sum()

    plantilla_respuesta = PromptTemplate(
        template = """
        Eres un analista de datos encargado de presentar un resumen informativo sobre un **DataFrame** a partir de una {pregunta} hecha por el usuario.

        A continuación, encontrarás la información general de la base de datos:

        ================= INFORMACIÓN DEL DATAFRAME =================

        Dimensiones: {shape}

        Columnas y tipos de datos:
        {columns}

        Valores nulos por columna:
        {nulos}

        Cadenas 'nan' (en cualquier capitalización) por columna:
        {nans_str}

        Filas duplicadas: {duplicados}

        ============================================================

        Con base en esta información, redacta un resumen claro y organizado que contenga:

        1. Un título: ## Informe de información general sobre el dataset,
        2. La dimensión total del DataFrame;
        3. La descripción de cada columna (incluyendo nombre, tipo de dato y qué representa esa columna);
        4. Las columnas que contienen datos nulos, con la respectiva cantidad;
        5. Las columnas que contienen cadenas 'nan', con la respectiva cantidad;
        6. La existencia (o no) de datos duplicados;
        7. Un párrafo sobre los análisis que se pueden realizar con estos datos;
        8. Un párrafo sobre los tratamientos que se pueden aplicar a los datos.
        """,
        input_variables = ['pregunta','shape','columns','nulos','nans_str','duplicados']
    )

    cadena = plantilla_respuesta | llm | StrOutputParser()
    respuesta = cadena.invoke({
        "pregunta": pregunta,
        "shape": shape,
        "columns": columns,
        "nulos": nulos,
        "nans_str": nans_str,
        "duplicados": duplicados
    })    
    return respuesta

# Herramienta de resumen esatdístico
@tool
def resumen_estadistico(pregunta: str) -> str:
    """
    Utiliza esta herramienta siempre que el usuario solicite un resumen estadístico completo
    y descriptivo de la base de datos, incluyendo varias estadísticas (promedio, desvío típico, 
    mínimo, máximo, etc.).
    """
    global df

    resumen = df.describe(include='number').transpose().to_string()
    plantilla_respuesta = PromptTemplate(
        template = """
        Eres un analista de datos encargado de interpretar resultados estadísticos de una base de datos a partir de una {pregunta} realizada por el usuario.
        
        A continuación, encontrarás las estadísticas descriptivas de la base de datos:

        ================= ESTADÍSTICAS DESCRIPTIVAS =================

        {resumen}

        ============================================================
        
        Con base en estos datos, elabora un resumen explicativo con un lenguaje claro, accesible y fluido, destacando los principales puntos de los resultados. Incluye:
        
        1. Un título: ## Informe de estadísticas descriptivas;  
        2. Una visión general de las estadísticas de las columnas numéricas;  
        3. Un párrafo sobre cada una de las columnas, comentando información sobre sus valores;  
        4. Identificación de posibles valores atípicos con base en los valores mínimo y máximo;  
        5. Recomendaciones de próximos pasos en el análisis en función de los patrones identificados.          
        """,
        input_variables = ['pregunta','resumen']
    )

    cadena = plantilla_respuesta | llm | StrOutputParser()
    respuesta = cadena.invoke({
        "pregunta": pregunta,
        "resumen": resumen
    })
    return respuesta

# Herramienta de generar gráficos
@tool
def generar_grafico(pregunta: str) -> str:
    """
    Utiliza esta herramienta siempre que el usuario solicite un gráfico a partir de un DataFrame
    pandas (`df`) con base en una instrucción del usuario.
    """
    global df

    columnas_info = '\n'.join([f"- {col} ({dtype})" for col, dtype in df.dtypes.items()])
    muestra_datos = df.head(3).to_dict(orient='records')

    plantilla_respuesta = PromptTemplate( 
        template = """
        Eres un especialista en visualización de datos. Tu tarea es generar **únicamente el código Python** para graficar con base en la solicitud del usuario.

        ## Solicitud del usuario:
        "{pregunta}"

        ## Metadatos del DataFrame:
        {columnas}

        ## Muestra de los datos (3 primeras filas):
        {muestra}

        ## Instrucciones obligatorias:
        1. Usa las bibliotecas `matplotlib.pyplot` (como `plt`) y `seaborn` (como `sns`);
        2. Define el tema con `sns.set_theme()`;
        3. Asegúrate de que todas las columnas mencionadas en la solicitud existan en el DataFrame llamado `df`;
        4. Elige el tipo de gráfico adecuado según el análisis solicitado:
        - **Distribución de variables numéricas**: `histplot`, `kdeplot`, `boxplot` o `violinplot`
        - **Distribución de variables categóricas**: `countplot`
        - **Comparación entre categorías**: `barplot`
        - **Relación entre variables**: `scatterplot`
        - **Series temporales**: `lineplot`, con el eje X formateado como fechas
        5. Configura el tamaño del gráfico con `figsize=(8, 4)`;
        6. Añade título y etiquetas (`labels`) apropiadas a los ejes;
        7. Posiciona el título a la izquierda con `loc='left'`, deja el `pad=20` y usa `fontsize=14`;
        8. Mantén los ticks del eje X sin rotación con `plt.xticks(rotation=0)`;
        9. Elimina los bordes superior y derecho del gráfico con `sns.despine()`;
        10. Finaliza el código CON la creación del objeto gráfico, no uses bloques de muestra adicionales.

        Devuelve ÚNICAMENTE el código Python puro, sin bloques de código markdown (```python), sin texto adicional ni explicaciones.

        Código Python:
        """,
        input_variables = ['pregunta','columnas','muestra']
    )

    cadena = plantilla_respuesta | llm | StrOutputParser()
    script_bruto = cadena.invoke({
        "pregunta": pregunta,
        "columnas": columnas_info,
        "muestra": muestra_datos
    })
    
    # Limpieza estricta del string generado
    script_limpio = script_bruto.replace("```python", "").replace("```", "").strip()
    
    # Evitamos que plt.show() bloquee la app web
    script_limpio = script_limpio.replace("plt.show()", "")

    exec_globals = {"df": df, "plt": plt, "sns": sns}
    exec_locals = {}

    # Ejecución y renderizado seguro en Streamlit
    try:
        # Forzar reinicio de figura para evitar solapamientos
        plt.figure(figsize=(8, 4)) 
        
        exec(script_limpio, exec_globals, exec_locals)
        fig = plt.gcf()
        st.pyplot(fig)
        plt.close(fig) # Liberación de memoria obligatoria
    except Exception as e:
        return f"Error al generar el gráfico de forma dinámica: {str(e)}"

    return "Gráfico generado y mostrado con éxito en la interfaz."


def crear_herramientas(df_usuario):
    # Asignamos el df recibido al contexto global para que las funciones @tool lo vean al ser invocadas por el agente
    global df
    df = df_usuario

    herramienta_informacion_df = Tool(
        name = 'Informaciones DF',
        func = lambda pregunta: informacion_df.run(pregunta), # Pasamos solo el string de la pregunta
        description = """
                     Utilice esta herramienta siempre que el usuario solicite informaciones generales sobre el dataframe, 
                     incluyendo el número de columnas y filas, nombres de las columnas, y sus tipos de datos, 
                     conteo de datos nulos, y duplicados para dar un panorama general sobre el archivo.
                      """,
        return_direct = True
    )

    herramienta_resumen_estadístico = Tool(
        name = 'Resumen Estadístico',
        func = lambda pregunta: resumen_estadistico.run(pregunta),
        description = """
                    Utilice esta herramienta siempre que el usuario solicite un resumen estadístico completo 
                    y descriptivo de la base de datos, incluyendo varias estadísticas (promedio, desvío típico, 
                    mínimo, máximo, etc.). No utilice esta herramienta para calcular una única métrica como 
                    por ejemplo: 'Cuál es el promedio de x?' o 'Cuál es la correlación de las variables?'; 
                    en estos casos utiliza la herramienta_codigos_python.
                    """,
        return_direct = True
    )

    herramienta_generar_grafico = Tool(
        name = 'Generar Gráfico',
        func = lambda pregunta: generar_grafico.run(pregunta),
        description = """
                    Utilice esta herramienta siempre que el usuario solicite una gráfica a partir de un DataFrame pandas (`df`) 
                    con base en una instrucción del usuario. Las palabras-clave que indican el uso de esta herramienta incluyen: 
                    'crea un gráfico', 'realiza un plot', 'plotea', 'visualiza', 'muestra la distribución', 'representa graficamente'.
                    """,
        return_direct = True
    )

    herramienta_codigos_python = Tool(
        name = 'Herramienta Códigos de Python',
        func = lambda q: str(PythonAstREPLTool(locals={"df": df}).run(q.strip().replace("```python", "").replace("```", ""))),
        description = """
                    Utilice esta herramienta ÚNICAMENTE para ejecutar una sola línea de código de Pandas/Python sobre el DataFrame `df`.
                    NO uses 'print()', NO importes librerías, NO generes bloques multilínea.
                    Si quieres el promedio, escribe exactamente esto en el Action Input: df['tiempo_entrega'].mean()
                    La respuesta de la herramienta será el valor directo. Cuando lo obtengas, pasa inmediatamente a 'Final Answer:'.
                    """,
        return_direct = False
    )

    return [herramienta_informacion_df, herramienta_resumen_estadístico, herramienta_generar_grafico, herramienta_codigos_python]