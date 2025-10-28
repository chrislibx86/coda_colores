from db.mongo import get_cliente
from db.config import JUEGO_DB_NAME


def insertar_intento_usuario(intento):
    cliente = get_cliente()
    if cliente:
        db = cliente[JUEGO_DB_NAME]
        coleccion_sesiones = db['intentos']

        documento = {
            "id_sesion": intento.id_sesion,
            "id_usuario": intento.id_usuario,
            "es_acertado": intento.es_acertado,
            "hora_inicio": intento.hora_inicio,
            "hora_fin": intento.hora_fin,
            "respuesta_usuario": intento.respuesta_usuario,
            "respuesta_correcta": intento.respuesta_correcta,
            "tipo": intento.tipo,
            "num_intentos": intento.num_intentos
        }

        resultado = coleccion_sesiones.insert_one(documento)
        return resultado.acknowledged