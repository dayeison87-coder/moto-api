from flask import Flask, jsonify, request
import json
import datetime
import os
import time

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


# Health Check para Railway
@app.route('/api/health', methods=['GET'])
def health_check():

    sistema_archivos_ok = os.path.exists('/tmp') or os.path.exists('.')

    if sistema_archivos_ok:
        return jsonify({
            "status": "healthy",
            "timestamp": int(time.time()),
            "environment": "production-cloud",
            "uptime_check": "passed"
        }), 200
    else:
        return jsonify({
            "status": "unhealthy",
            "reason": "Storage unreachable"
        }), 500


# Ruta peritajes (GET y POST)
@app.route('/api/peritajes', methods=['GET', 'POST'])
def manejar_peritajes():

    ruta_archivo = 'peritajes.json'

    # MÉTODO GET
    if request.method == 'GET':
        try:
            if not os.path.exists(ruta_archivo):
                return jsonify([]), 200

            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                motos = json.load(archivo)

            return jsonify(motos), 200

        except json.JSONDecodeError:
            return jsonify([]), 200

        except Exception as e:
            return jsonify({
                "error": f"Error al leer los datos: {str(e)}"
            }), 500

    # MÉTODO POST
    elif request.method == 'POST':
        try:
            nuevo_peritaje = request.get_json()

            if not nuevo_peritaje:
                return jsonify({
                    "error": "No se enviaron datos válidos"
                }), 400

            motos = []

            if os.path.exists(ruta_archivo):
                try:
                    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                        motos = json.load(archivo)

                    if not isinstance(motos, list):
                        motos = []

                except json.JSONDecodeError:
                    motos = []

            motos.append(nuevo_peritaje)

            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(
                    motos,
                    archivo,
                    indent=4,
                    ensure_ascii=False
                )

            return jsonify({
                "mensaje": "Peritaje guardado con éxito",
                "datos": nuevo_peritaje
            }), 201

        except Exception as e:
            return jsonify({
                "error": f"Error al guardar el peritaje: {str(e)}"
            }), 500


# Ruta DELETE
@app.route('/api/peritajes/<placa>', methods=['DELETE'])
def eliminar_peritaje(placa):

    ruta_archivo = 'peritajes.json'

    try:
        if not os.path.exists(ruta_archivo):
            return jsonify({
                "error": "No existen peritajes registrados"
            }), 404

        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            motos = json.load(archivo)

        moto_encontrada = None

        for moto in motos:
            if moto.get('placa') == placa:
                moto_encontrada = moto
                motos.remove(moto)
                break

        if moto_encontrada is None:
            return jsonify({
                "error": "Vehículo no encontrado"
            }), 404

        with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(
                motos,
                archivo,
                indent=4,
                ensure_ascii=False
            )

        return jsonify({
            "message": f"Vehículo {placa} entregado al cliente con éxito",
            "moto_removida": moto_encontrada
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Error al procesar la eliminación: {str(e)}"
        }), 500


# Ejecutar aplicación
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)