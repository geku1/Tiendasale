from flask import Flask, jsonify, request
from flask_cors import CORS
from videojuegos import obtener_videojuegos
import subprocess
import os
from chatbot import bot
from chat_engine import ChatEngine
import re
from chat_session import chat

app = Flask(__name__)
CORS(app)

# ============================================================
#  CONFIGURACIÓN — SCALA
# ============================================================

SCALA_EXE     = r"C:\Program Files (x86)\scala\bin\scala.bat"
SCALA_PROJECT = r"C:\Users\USER\Desktop\TIENDAS SALES\motor_scala"


# ============================================================
#  HELPERS
# ============================================================

def ejecutar_scala(objeto, args=[]):
    cmd = [
        SCALA_EXE,
        "-classpath", SCALA_PROJECT,
        objeto
    ] + [str(a) for a in args]

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=SCALA_PROJECT,
        shell=False
    )


def consultar_prolog(goal):
    resultado = subprocess.run(
        [
            "swipl",
            "-s", "../motor_prolog/consultas.pl",
            "-g", goal,
            "-t", "halt"
        ],
        capture_output=True,
        text=True
    )
    return resultado.stdout.splitlines()

engine = ChatEngine(
    ejecutar_scala,
    consultar_prolog
)

def detectar_presupuesto(texto):

    numeros = re.findall(r'\d+\.?\d*', texto)

    if numeros:
        return float(numeros[0])

    return None


def contiene(texto, palabras):

    texto = texto.lower()

    return any(p in texto for p in palabras)


def respuesta_tarjetas(titulo, juegos):

    return jsonify({
        "success": True,
        "tipo": "cards",
        "titulo": titulo,
        "data": juegos
    })


def respuesta_texto(texto):

    return jsonify({
        "success": True,
        "tipo": "texto",
        "mensaje": texto
    })

# ============================================================
#  RUTAS GENERALES
# ============================================================

@app.route("/")
def inicio():
    return jsonify({"mensaje": "API funcionando"})


@app.route("/juegos")
def juegos():
    return jsonify(obtener_videojuegos())


@app.route("/test")
def test():
    try:
        resultado = subprocess.run(
            ["where", "scala"],
            capture_output=True,
            text=True,
            shell=True
        )
        return jsonify({
            "stdout":              resultado.stdout,
            "stderr":              resultado.stderr,
            "returncode":          resultado.returncode,
            "scala_existe":        os.path.exists(SCALA_EXE),
            "motor_scala_existe":  os.path.exists(SCALA_PROJECT)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
#  RUTAS SCALA
# ============================================================

@app.route("/ranking")
def ranking():
    try:
        letra            = request.args.get("letra",      "")
        puntuacion_param = request.args.get("puntuacion", "0") or "0"
        precio_param     = request.args.get("precio",     "")  or ""

        resultado = ejecutar_scala("Ranking", [letra, puntuacion_param, precio_param])

        print("=== STDOUT ===", resultado.stdout)
        print("=== STDERR ===", resultado.stderr)
        print("=== CODE ===",   resultado.returncode)

        if resultado.returncode != 0:
            return jsonify({
                "success": False,
                "error":   "Error ejecutando Ranking.scala",
                "stderr":  resultado.stderr,
                "stdout":  resultado.stdout
            }), 500

        juegos = []

        for linea in resultado.stdout.strip().split("\n"):
            linea = linea.strip()
            if not linea:
                continue
            try:
                partes = linea.split(",")
                if len(partes) != 3:
                    print("Línea inválida:", linea)
                    continue
                juegos.append({
                    "nombre":     partes[0].strip(),
                    "puntuacion": float(partes[1].strip()),
                    "precio":     float(partes[2].strip())
                })
            except Exception as e:
                print("Error parseando línea:", linea, "->", str(e))

        return jsonify({
            "success":  True,
            "cantidad": len(juegos),
            "data":     juegos
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/estadisticas")
def estadisticas():
    try:
        resultado = ejecutar_scala("Estadisticas")

        print("=== STDOUT ===", resultado.stdout)
        print("=== STDERR ===", resultado.stderr)
        print("=== CODE ===",   resultado.returncode)

        if resultado.returncode != 0:
            return jsonify({
                "success": False,
                "error":   "Error ejecutando Estadisticas.scala",
                "stderr":  resultado.stderr
            }), 500

        stats = {}
        for linea in resultado.stdout.strip().split("\n"):
            if not linea:
                continue
            try:
                clave, valor = linea.split(",")
                stats[clave.strip().lower()] = float(valor)
            except:
                pass

        return jsonify({"success": True, "data": stats})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
#  RUTAS PROLOG — GÉNEROS
# ============================================================

@app.route("/prolog/shooter")
def prolog_shooter():
    return jsonify(consultar_prolog("es_shooter(X),write(X),nl,fail"))

@app.route("/prolog/rpg")
def prolog_rpg():
    return jsonify(consultar_prolog("es_rpg(X),write(X),nl,fail"))

@app.route("/prolog/sandbox")
def prolog_sandbox():
    return jsonify(consultar_prolog("es_sandbox(X),write(X),nl,fail"))

@app.route("/prolog/aventura")
def prolog_aventura():
    return jsonify(consultar_prolog("es_aventura(X),write(X),nl,fail"))

@app.route("/prolog/accion")
def prolog_accion():
    return jsonify(consultar_prolog("es_accion(X),write(X),nl,fail"))

@app.route("/prolog/deportes")
def prolog_deportes():
    return jsonify(consultar_prolog("es_deportes(X),write(X),nl,fail"))

@app.route("/prolog/metroidvania")
def prolog_metroidvania():
    return jsonify(consultar_prolog("es_metroidvania(X),write(X),nl,fail"))

@app.route("/prolog/genero")
def prolog_genero():
    genero = request.args.get("tipo", "").lower().strip()
    if not genero:
        return jsonify({"error": "Falta el parámetro ?tipo="}), 400
    return jsonify(consultar_prolog(f"juegos_de_genero({genero},X),write(X),nl,fail"))


# ============================================================
#  RUTAS PROLOG — PLATAFORMAS
# ============================================================

@app.route("/prolog/pc")
def prolog_pc():
    return jsonify(consultar_prolog("es_pc(X),write(X),nl,fail"))

@app.route("/prolog/playstation")
def prolog_playstation():
    return jsonify(consultar_prolog("es_playstation(X),write(X),nl,fail"))

@app.route("/prolog/multiplataforma")
def prolog_multiplataforma():
    return jsonify(consultar_prolog("multiplataforma(X),write(X),nl,fail"))

@app.route("/prolog/exclusivo-pc")
def prolog_exclusivo_pc():
    return jsonify(consultar_prolog("exclusivo_pc(X),write(X),nl,fail"))

@app.route("/prolog/exclusivo-playstation")
def prolog_exclusivo_ps():
    return jsonify(consultar_prolog("exclusivo_playstation(X),write(X),nl,fail"))

@app.route("/prolog/plataforma")
def prolog_plataforma():
    plat = request.args.get("tipo", "").lower().strip()
    if not plat:
        return jsonify({"error": "Falta el parámetro ?tipo="}), 400
    return jsonify(consultar_prolog(f"juegos_de_plataforma({plat},X),write(X),nl,fail"))


# ============================================================
#  RUTAS PROLOG — DESARROLLADORAS
# ============================================================

@app.route("/prolog/desarrolladoras")
def prolog_desarrolladoras():
    return jsonify(consultar_prolog("empresa(X),write(X),nl,fail"))

@app.route("/prolog/rockstar")
def prolog_rockstar():
    return jsonify(consultar_prolog("juego_rockstar(X),write(X),nl,fail"))

@app.route("/prolog/cdprojekt")
def prolog_cdprojekt():
    return jsonify(consultar_prolog("juego_cdprojekt(X),write(X),nl,fail"))

@app.route("/prolog/fromsoftware")
def prolog_fromsoftware():
    return jsonify(consultar_prolog("juego_fromsoftware(X),write(X),nl,fail"))

@app.route("/prolog/valve")
def prolog_valve():
    return jsonify(consultar_prolog("juego_valve(X),write(X),nl,fail"))

@app.route("/prolog/riot")
def prolog_riot():
    return jsonify(consultar_prolog("juego_riot(X),write(X),nl,fail"))

@app.route("/prolog/desarrolladora")
def prolog_desarrolladora():
    dev = request.args.get("nombre", "").lower().strip()
    if not dev:
        return jsonify({"error": "Falta el parámetro ?nombre="}), 400
    return jsonify(consultar_prolog(f"juegos_de_desarrolladora({dev},X),write(X),nl,fail"))


# ============================================================
#  RUTAS PROLOG — MULTIJUGADOR Y COMPETITIVO
# ============================================================

@app.route("/chat", methods=["POST"])
def chat():

    datos = request.get_json()

    mensaje = datos.get("mensaje","")

    respuesta = engine.responder(mensaje)

    return jsonify(respuesta)

# ============================================================

if __name__ == "__main__":
    app.run(debug=True)