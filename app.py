from flask import Flask, request, jsonify
import networkx as nx

app = Flask(__name__)

# Inicializar el grafo
grafo = nx.Graph()
dirigido = False

@app.route('/construir_grafo', methods=['POST'])
def construir_grafo():
    global grafo, dirigido
    data = request.json
    nodos = data.get('nodos', [])
    aristas = data.get('aristas', [])

    grafo.clear()
    grafo.add_nodes_from(nodos)

    for arista in aristas:
        if len(arista) == 3:  # Formato: [A, B, 4]
            nodo1, nodo2, peso = arista
            grafo.add_edge(nodo1, nodo2, peso=int(peso), capacidad=int(peso))

    return jsonify({"message": "Grafo construido correctamente"})

@app.route('/cambiar_tipo_grafo', methods=['POST'])
def cambiar_tipo_grafo():
    global grafo, dirigido
    dirigido = not dirigido
    if dirigido:
        grafo = nx.DiGraph()
        return jsonify({"message": "El grafo ahora es DIRIGIDO"})
    else:
        grafo = nx.Graph()
        return jsonify({"message": "El grafo ahora es NO DIRIGIDO"})

@app.route('/calcular_flujo_maximo', methods=['POST'])
def calcular_flujo_maximo():
    data = request.json
    fuente = data.get('fuente')
    sumidero = data.get('sumidero')

    try:
        flujo_valor = nx.maximum_flow(grafo, fuente, sumidero, capacity='capacidad')[0]
        return jsonify({"flujo_maximo": flujo_valor})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/calcular_costo_minimo', methods=['POST'])
def calcular_costo_minimo():
    data = request.json
    origen = data.get('origen')
    destino = data.get('destino')

    try:
        costo = nx.dijkstra_path_length(grafo, origen, destino, weight='peso')
        return jsonify({"costo_minimo": costo})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/graficar_arbol_minimo', methods=['GET'])
def graficar_arbol_minimo():
    try:
        if nx.is_directed(grafo):
            return jsonify({"error": "El árbol de expansión mínima no está definido para grafos dirigidos"}), 400
        arbol = nx.minimum_spanning_tree(grafo, weight='peso')
        return jsonify({"arbol": list(arbol.edges(data=True))})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/graficar_ruta_corta', methods=['POST'])
def graficar_ruta_corta():
    data = request.json
    origen = data.get('origen')
    destino = data.get('destino')

    try:
        ruta = nx.dijkstra_path(grafo, origen, destino, weight='peso')
        return jsonify({"ruta": ruta})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)