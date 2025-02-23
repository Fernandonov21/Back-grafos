from flask import Flask, request, jsonify
from flask_cors import CORS
import networkx as nx

app = Flask(__name__)
CORS(app)  # Enable CORS

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

    return jsonify({"message": "Grafo construido correctamente"})

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

if __name__ == '__main__':
    app.run(debug=True)
