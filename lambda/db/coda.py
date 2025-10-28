from bson.objectid import ObjectId
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from db.mongo import get_cliente
from db.config import USER_DB_NAME
from db.models import Usuario


# ================================= USUARIOS =================================
def insertar_usuario(usuario):
    cliente = get_cliente()
    db = cliente[USER_DB_NAME] 
    coleccion = db['usuarios']

    coleccion.create_index([('num_usuario', ASCENDING)], unique=True)

    if usuario.num_usuario is None:
        ultimo_usuario = coleccion.find_one(sort=[("num_usuario", -1)])
        if ultimo_usuario:
            usuario.num_usuario = ultimo_usuario["num_usuario"] + 1
        else:
            usuario.num_usuario = 1

    doc = {
        "num_usuario": usuario.num_usuario,
        "edad": usuario.edad,
        "profesion": usuario.profesion
    }

    try:
        resultado = coleccion.insert_one(doc)
        return str(resultado.inserted_id)
        
    except DuplicateKeyError:
        return None


def obtener_usuario_por_num_usuario(num_usuario):
    cliente = get_cliente()
    db = cliente[USER_DB_NAME]
    coleccion = db['usuarios']
    doc = coleccion.find_one({"num_usuario": num_usuario})
    if doc:
        usuario = Usuario(
            id=str(doc.get("_id")), 
            num_usuario=doc.get("num_usuario"),
            edad=doc.get("edad"),
            profesion=doc.get("profesion")
        )
        return usuario
    else:
        return None


# ================================= Sesión =================================
def insertar_sesion(sesion):
    cliente = get_cliente()
    if cliente:
        try:
            sesion_dict = {
                'id_usuario': sesion.id_usuario,
                'fecha_inicio': sesion.fecha_inicio,
                'hora_inicio': sesion.hora_inicio,
                'hora_fin': sesion.hora_fin,
                'juego': 'Coda Colores',
                'version_juego': 'v1'
            }
            resultado = cliente[USER_DB_NAME]['sesiones'].insert_one(sesion_dict)
            return str(resultado.inserted_id)  
        finally:
            cliente.close()  
    return None


def finalizar_sesion(id_sesion, hora_fin):
    cliente = get_cliente()
    if cliente:
        db = cliente[USER_DB_NAME]
        coleccion = db['sesiones']

        resultado = coleccion.update_one(
            {"_id": ObjectId(id_sesion)},
            {"$set": {"hora_fin": hora_fin}}
        )
        cliente.close()
        return resultado.modified_count == 1
    return False