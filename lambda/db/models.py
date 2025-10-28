# CODA MODELS ----------------------------------------------------------------
class Usuario:
    def __init__(self, id=None, num_usuario=None, edad=None, profesion=None):
        self.id = id
        self.num_usuario = num_usuario
        self.edad = edad
        self.profesion = profesion

class Sesion:
    def __init__(self, id=None, id_usuario=None, fecha_inicio=None, hora_inicio=None, hora_fin=None, version_juego=None, estado_sesion=None):
        self.id = id
        self.id_usuario = id_usuario
        self.fecha_inicio = fecha_inicio
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.version_juego = version_juego