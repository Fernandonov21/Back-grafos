from flask import Flask, request, jsonify
from flask_cors import CORS
import networkx as nx
from ia import interpretar_analisis_sensibilidad  # Importa la función de interpretación

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)  # Enable CORS for all routes and methods

# Inicializar el grafo
grafo = nx.Graph()
dirigido = False

@app.route('/construir_grafo', methods=['POST'])
def construir_grafo():
    """
    Endpoint para construir el grafo.
    Recibe nodos y aristas en formato JSON.
    """
    global grafo, dirigido
    data = request.json
    nodos = data.get('nodos', [])
    aristas = data.get('aristas', [])

    # Limpiar el grafo actual
    grafo.clear()

    # Agregar nodos al grafo
    grafo.add_nodes_from(nodos)

    # Agregar aristas al grafo
    for arista in aristas:
        if len(arista) == 3:  # Formato: [A, B, 4]
            nodo1, nodo2, peso = arista
            grafo.add_edge(nodo1, nodo2, peso=int(peso), capacidad=int(peso))

    # Realizar análisis de sensibilidad
    resultados = []
    for arista in aristas:
        if len(arista) == 3:
            nodo1, nodo2, nuevo_costo = arista
            if grafo.has_edge(nodo1, nodo2):
                # Guardar el costo original
                costo_original_arista = grafo[nodo1][nodo2]['peso']

                # Modificar el costo
                grafo[nodo1][nodo2]['peso'] = nuevo_costo

                # Calcular el nuevo costo mínimo
                nuevo_costo_minimo = nx.dijkstra_path_length(grafo, nodo1, nodo2, weight='peso')
                resultados.append({
                    "arista": f"{nodo1}-{nodo2}",
                    "nuevo_costo": nuevo_costo,
                    "nuevo_costo_minimo": nuevo_costo_minimo
                })

                # Restaurar el costo original
                grafo[nodo1][nodo2]['peso'] = costo_original_arista

    # Interpretar los resultados utilizando la IA
    interpretacion = interpretar_analisis_sensibilidad(resultados)

    return jsonify({"message": "Grafo construido correctamente", "resultados": resultados, "interpretacion": interpretacion})

@app.route('/calcular_flujo_maximo', methods=['POST'])
def calcular_flujo_maximo():
    try:
        data = request.get_json()
        fuente = data.get('fuente')
        sumidero = data.get('sumidero')

        if not fuente or not sumidero:
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        # Crear una copia dirigida del grafo para el cálculo del flujo sin modificar el original
        grafo_dirigido = nx.DiGraph()
        grafo_dirigido.add_nodes_from(grafo.nodes())
        for u, v, data in grafo.edges(data=True):
            capacidad = data.get('capacidad', 0)
            grafo_dirigido.add_edge(u, v, capacity=capacidad)

        flujo_valor, _ = nx.maximum_flow(grafo_dirigido, fuente, sumidero, capacity='capacity')
        return jsonify({'flujo_maximo': flujo_valor})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calcular_costo_minimo', methods=['POST'])
def calcular_costo_minimo():
    """
    Endpoint para calcular el costo mínimo entre dos nodos.
    """
    try:
        data = request.get_json()
        origen = data.get('origen')
        destino = data.get('destino')

        if not origen or not destino:
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        costo = nx.dijkstra_path_length(grafo, origen, destino, weight='peso')
        return jsonify({"costo_minimo": costo})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/graficar_ruta_corta', methods=['POST'])
def graficar_ruta_corta():
    """
    Endpoint para calcular y devolver la ruta más corta entre dos nodos.
    """
    try:
        data = request.get_json()
        origen = data.get('origen')
        destino = data.get('destino')

        if not origen or not destino:
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        ruta = nx.dijkstra_path(grafo, origen, destino, weight='peso')
        return jsonify({"ruta": ruta})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/graficar_arbol_minimo', methods=['GET'])
def graficar_arbol_minimo():
    """
    Endpoint para calcular y devolver el árbol de expansión mínima.
    """
    try:
        if nx.is_directed(grafo):
            return jsonify({"error": "El árbol de expansión mínima no está definido para grafos dirigidos"}), 400
        arbol = nx.minimum_spanning_tree(grafo, weight='peso')
        return jsonify({"arbol": list(arbol.edges(data=True))})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/modificar_costo_arista', methods=['POST'])
def modificar_costo_arista():
    """
    Endpoint para modificar el costo de una arista.
    """
    try:
        data = request.get_json()
        nodo1 = data.get('nodo1')
        nodo2 = data.get('nodo2')
        nuevo_costo = data.get('nuevo_costo')

        if not nodo1 or not nodo2 or nuevo_costo is None:
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        if grafo.has_edge(nodo1, nodo2):
            grafo[nodo1][nodo2]['peso'] = nuevo_costo
            return jsonify({"message": f"Costo de la arista {nodo1}-{nodo2} modificado a {nuevo_costo}"})
        else:
            return jsonify({"error": f"No existe la arista {nodo1}-{nodo2}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analisis_sensibilidad_costo_minimo', methods=['POST', 'OPTIONS'])
def analisis_sensibilidad_costo_minimo():
    if request.method == 'OPTIONS':
        # Responder a la solicitud OPTIONS
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response, 200

    try:
        data = request.get_json()
        origen = data.get('origen')
        destino = data.get('destino')
        aristas_a_modificar = data.get('aristas_a_modificar', [])  # Lista de aristas y sus nuevos costos

        if not origen or not destino:
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        resultados = []

        # Calcular el costo mínimo original
        costo_original = nx.dijkstra_path_length(grafo, origen, destino, weight='peso')
        resultados.append({"costo_original": costo_original})

        # Modificar las aristas y calcular el nuevo costo mínimo
        for arista in aristas_a_modificar:
            nodo1, nodo2, nuevo_costo = arista
            if grafo.has_edge(nodo1, nodo2):
                # Guardar el costo original
                costo_original_arista = grafo[nodo1][nodo2]['peso']

                # Modificar el costo
                grafo[nodo1][nodo2]['peso'] = nuevo_costo

                # Calcular el nuevo costo mínimo
                nuevo_costo_minimo = nx.dijkstra_path_length(grafo, origen, destino, weight='peso')
                resultados.append({
                    "arista": f"{nodo1}-{nodo2}",
                    "nuevo_costo": nuevo_costo,
                    "nuevo_costo_minimo": nuevo_costo_minimo
                })

                # Restaurar el costo original
                grafo[nodo1][nodo2]['peso'] = costo_original_arista
            else:
                resultados.append({
                    "arista": f"{nodo1}-{nodo2}",
                    "error": "La arista no existe en el grafo"
                })

        # Interpretar los resultados utilizando la IA
        interpretacion = interpretar_analisis_sensibilidad(resultados)

        response = jsonify({"resultados": resultados, "interpretacion": interpretacion})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)