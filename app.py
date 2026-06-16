from flask import Flask, jsonify, request
import json
import datetime
import os

app = Flask(__name__)

# Ruta principal
@app.route('/')
def inicio():
    return "Servidor Flask funcionando"

# Ruta registros
@app.route('/registros')
def get_repuestos():
    return jsonify({
        "status": "Online",
        "servidor": "Ubuntu de Martinez",
        "hora_servidor": str(datetime.datetime.now()),
        "inventario": [
            "Bujias de Iridio",
            "Filtro de aceite",
            "Aceite motul 7100"
        ]
    })

# Ruta peritajes (Soporta GET para leer y POST para guardar)
@app.route('/peritajes', methods=['GET', 'POST'])
def manejar_peritajes():
    ruta_archivo = '/var/www/html/peritajes.json'

    # --- MÉTODO GET: LEER PERITAJES ---
    if request.method == 'GET':
        try:
            if not os.path.exists(ruta_archivo):
                return jsonify([]), 200  # Si no existe el archivo, devolvemos una lista vacía

            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                motos = json.load(archivo)
            return jsonify(motos), 200
            
        except json.JSONDecodeError:
            return jsonify({"error": "El archivo JSON tiene un error de formato o está vacío"}), 500
        except Exception as e:
            return jsonify({"error": f"Error al leer los datos: {str(e)}"}), 500

    # --- MÉTODO POST: CREAR NUEVO PERITAJE ---
    elif request.method == 'POST':
        try:
            nuevo_peritaje = request.get_json()
            
            if not nuevo_peritaje:
                return jsonify({"error": "No se enviaron datos válidos en el cuerpo"}), 400

            motos = []
            if os.path.exists(ruta_archivo):
                try:
                    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                        motos = json.load(archivo)
                        if not isinstance(motos, list):
                            motos = []
                except json.JSONDecodeError:
                    motos = []  # Si estaba vacío o corrupto, empezamos de cero de forma segura

            motos.append(nuevo_peritaje)

            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(motos, archivo, indent=4, ensure_ascii=False)

            return jsonify({"mensaje": "Peritaje guardado con éxito", "datos": nuevo_peritaje}), 201

        except Exception as e:
            return jsonify({"error": f"Error al guardar el peritaje: {str(e)}"}), 500

# Ruta DELETE (Eliminar peritaje por placa)
@app.route('/api/peritajes/<placa>', methods=['DELETE'])
def eliminar_peritaje(placa):
    ruta_archivo = '/var/www/html/peritajes.json'
    
    try:
        if not os.path.exists(ruta_archivo):
            return jsonify({"error": "El archivo de peritajes no existe"}), 404

        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            motos = json.load(archivo)

        moto_encontrada = None

        for moto in motos:
            if moto.get('placa') == placa:
                moto_encontrada = moto
                motos.remove(moto)
                break

        if moto_encontrada is None:
            return jsonify({"error": "Vehículo no encontrado"}), 404

        with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(motos, archivo, indent=4, ensure_ascii=False)

        return jsonify({
            "message": f"Vehículo {placa} entregado al cliente con éxito",
            "moto_removida": moto_encontrada
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar la eliminación: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)