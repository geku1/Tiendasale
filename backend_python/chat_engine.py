import re

from chatbot import bot
from chat_session import chat


class ChatEngine:

    def __init__(self, ejecutar_scala, consultar_prolog):
        self.ejecutar_scala = ejecutar_scala
        self.consultar_prolog = consultar_prolog

    # =====================================================
    # UTILIDADES
    # =====================================================

    def detectar_numero(self, texto):

        numeros = re.findall(r"\d+\.?\d*", texto)

        if numeros:
            return float(numeros[0])

        return None

    def contiene(self, texto, palabras):

        texto = texto.lower()

        return any(p in texto for p in palabras)

    # =====================================================
    # PYTHON
    # =====================================================

    def buscar_python(self):

        juegos = bot.juegos

        if chat.genero:
            juegos = [
                j for j in juegos
                if j["genero"].lower() == chat.genero.lower()
            ]

        if chat.plataforma:
            juegos = [
                j for j in juegos
                if chat.plataforma.lower()
                in j["plataforma"].lower()
            ]

        if chat.desarrolladora:
            juegos = [
                j for j in juegos
                if chat.desarrolladora.lower()
                in j["desarrolladora"].lower()
            ]

        if chat.presupuesto:
            juegos = [
                j for j in juegos
                if float(j["precio"]) <= chat.presupuesto
            ]

        if chat.orden == "precio":
            juegos = bot.ordenar_precio(juegos)

        elif chat.orden == "puntaje":
            juegos = bot.ordenar_puntaje(juegos)

        return juegos

    # =====================================================
    # PROLOG
    # =====================================================

    def consultar_genero(self, genero):

        salida = self.consultar_prolog(
            f"juegos_de_genero({genero.lower()},X),write(X),nl,fail"
        )

        return salida

    def consultar_desarrolladora(self, empresa):

        empresa = empresa.lower().replace(" ", "")

        salida = self.consultar_prolog(
            f"juegos_de_desarrolladora({empresa},X),write(X),nl,fail"
        )

        return salida

    def similares(self, juego):

        juego = juego.lower().replace(" ", "_")

        salida = self.consultar_prolog(
            f"juegos_similares({juego},Y),write(Y),nl,fail"
        )

        return salida

    # =====================================================
    # SCALA
    # =====================================================

    def ranking(self):

        r = self.ejecutar_scala("Ranking")

        return r.stdout

    def estadisticas(self):

        r = self.ejecutar_scala("Estadisticas")

        return r.stdout

    # =====================================================
    # RESPUESTA
    # =====================================================

    def responder(self, mensaje):

        mensaje = mensaje.lower()

        # -------------------------
        # Presupuesto
        # -------------------------

        dinero = self.detectar_numero(mensaje)

        if dinero:

            chat.actualizar_presupuesto(dinero)

        # -------------------------
        # Géneros
        # -------------------------

        generos = [
            "rpg",
            "accion",
            "aventura",
            "sandbox",
            "shooter",
            "deportes",
            "metroidvania"
        ]

        for genero in generos:

            if genero in mensaje:

                chat.actualizar_genero(genero.capitalize())

                juegos = self.buscar_python()

                return {
                    "tipo": "cards",
                    "titulo": f"{genero.upper()} recomendados",
                    "juegos": juegos
                }

        # -------------------------
        # Plataforma
        # -------------------------

        if "pc" in mensaje:

            chat.actualizar_plataforma("PC")

            return {
                "tipo":"texto",
                "mensaje":"Perfecto, buscaré juegos para PC."
            }

        if "playstation" in mensaje:

            chat.actualizar_plataforma("PlayStation")

            return {
                "tipo":"texto",
                "mensaje":"Buscaré juegos para PlayStation."
            }

        # -------------------------
        # Ordenar
        # -------------------------

        if "precio" in mensaje:

            chat.actualizar_orden("precio")

            juegos = self.buscar_python()

            return {
                "tipo":"cards",
                "titulo":"Ordenados por precio",
                "juegos":juegos
            }

        if "puntaje" in mensaje:

            chat.actualizar_orden("puntaje")

            juegos = self.buscar_python()

            return {
                "tipo":"cards",
                "titulo":"Ordenados por puntaje",
                "juegos":juegos
            }

        # -------------------------
        # Ranking Scala
        # -------------------------

        if self.contiene(mensaje,[
            "ranking",
            "top"
        ]):

            return {
                "tipo":"scala",
                "contenido":self.ranking()
            }

        # -------------------------
        # Estadísticas Scala
        # -------------------------

        if "estadisticas" in mensaje:

            return {
                "tipo":"scala",
                "contenido":self.estadisticas()
            }

        # -------------------------
        # Juegos similares
        # -------------------------

        if "similar" in mensaje:

            partes = mensaje.split("a")

            if len(partes)>1:

                similares = self.similares(
                    partes[-1].strip()
                )

                return {
                    "tipo":"prolog",
                    "titulo":"Juegos similares",
                    "resultado":similares
                }

        # -------------------------
        # Desarrolladora
        # -------------------------

        empresas = [
            "rockstar",
            "riot",
            "valve",
            "mojang",
            "cd projekt",
            "fromsoftware",
            "team cherry"
        ]

        for empresa in empresas:

            if empresa in mensaje:

                chat.actualizar_desarrolladora(empresa)

                juegos = self.buscar_python()

                return {
                    "tipo":"cards",
                    "titulo":empresa,
                    "juegos":juegos
                }

        return {

            "tipo":"texto",

            "mensaje":
            "No entendí tu consulta.\n\n"
            "Puedes preguntarme por:\n"
            "- géneros\n"
            "- plataformas\n"
            "- desarrolladoras\n"
            "- ranking\n"
            "- juegos similares\n"
            "- presupuesto"
        }