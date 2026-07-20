class ChatSession:

    def __init__(self):
        self.limpiar()

    def limpiar(self):

        self.genero = None
        self.plataforma = None
        self.presupuesto = None
        self.desarrolladora = None
        self.orden = None

    # --------------------------

    def actualizar_genero(self, genero):
        self.genero = genero

    def actualizar_plataforma(self, plataforma):
        self.plataforma = plataforma

    def actualizar_presupuesto(self, presupuesto):
        self.presupuesto = presupuesto

    def actualizar_desarrolladora(self, empresa):
        self.desarrolladora = empresa

    def actualizar_orden(self, orden):
        self.orden = orden

    # --------------------------

    def contexto(self):

        return {
            "genero": self.genero,
            "plataforma": self.plataforma,
            "presupuesto": self.presupuesto,
            "desarrolladora": self.desarrolladora,
            "orden": self.orden
        }


# sesión única
chat = ChatSession()