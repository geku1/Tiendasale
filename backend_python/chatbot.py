import json
import os

RUTA_JSON = os.path.join(
    os.path.dirname(__file__),
    "..",
    "datos",
    "videojuegos.json"
)


class GameBot:

    def __init__(self):

        with open(RUTA_JSON, "r", encoding="utf-8") as archivo:
            self.juegos = json.load(archivo)

    # ----------------------------------------------------
    # Utilidades
    # ----------------------------------------------------

    def normalizar(self, texto):
        return texto.lower().strip()

    # ----------------------------------------------------
    # Buscar por género
    # ----------------------------------------------------

    def buscar_genero(self, genero):

        genero = self.normalizar(genero)

        return [
            juego for juego in self.juegos
            if self.normalizar(juego["genero"]) == genero
        ]

    # ----------------------------------------------------

    def buscar_plataforma(self, plataforma):

        plataforma = self.normalizar(plataforma)

        return [
            juego for juego in self.juegos
            if plataforma in self.normalizar(juego["plataforma"])
        ]

    # ----------------------------------------------------

    def buscar_desarrolladora(self, empresa):

        empresa = self.normalizar(empresa)

        return [
            juego for juego in self.juegos
            if empresa in self.normalizar(juego["desarrolladora"])
        ]

    # ----------------------------------------------------

    def buscar_presupuesto(self, presupuesto):

        return [
            juego for juego in self.juegos
            if float(juego["precio"]) <= presupuesto
        ]

    # ----------------------------------------------------

    def ordenar_precio(self, juegos):

        return sorted(
            juegos,
            key=lambda x: float(x["precio"])
        )

    # ----------------------------------------------------

    def ordenar_puntaje(self, juegos):

        return sorted(
            juegos,
            key=lambda x: float(x["puntaje"]),
            reverse=True
        )

    # ----------------------------------------------------

    def mejores(self, cantidad=5):

        return self.ordenar_puntaje(self.juegos)[:cantidad]

    # ----------------------------------------------------

    def baratos(self, cantidad=5):

        return self.ordenar_precio(self.juegos)[:cantidad]

    # ----------------------------------------------------
    # Convierte resultados en JSON para el frontend
    # ----------------------------------------------------

    def respuesta(self, titulo, juegos):

        return {
            "titulo": titulo,
            "cantidad": len(juegos),
            "juegos": juegos
        }


bot = GameBot()