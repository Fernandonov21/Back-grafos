import google.generativeai as genai

# Configura la API de Gemini
genai.configure(api_key='AIzaSyBoZiEwHrIwEPg3AC0gpvn1pGyd8n4v6DU')

# Inicializa el modelo
model = genai.GenerativeModel('gemini-pro')

def interpretar_analisis_sensibilidad(resultados):
    """
    Función para interpretar los resultados del análisis de sensibilidad utilizando la API de Gemini.
    """
    # Construye el prompt para la IA
    prompt = (
        "A continuación se presentan los resultados de un análisis de sensibilidad sobre un grafo:\n"
        f"{resultados}\n"
        "Por favor, interpreta estos resultados y proporciona una explicación clara de cómo los cambios en los costos de las aristas afectan el costo mínimo entre los nodos."
    )

    # Envía el prompt a la API de Gemini
    response = model.generate_content(prompt)

    # Devuelve la interpretación generada por la IA
    return response.text