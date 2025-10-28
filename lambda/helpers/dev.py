from db.mongo import get_cliente
from db.config import DEBUG_DB_NAME

def insertar_error(error_trace):
    cliente = get_cliente()
    if cliente:
        try:
            err_dict = {
                'err': error_trace
            }
            resultado = cliente[DEBUG_DB_NAME]['errores'].insert_one(err_dict)
            return str(resultado.inserted_id)  
        finally:
            cliente.close()  
    return None
"""
import traceback

def insertar_error():
    error_trace = traceback.format_exc()
    cliente = get_cliente()
    if cliente:
        try:
            err_dict = {
                'err': error_trace
            }
            resultado = cliente[DEBUG_DB_NAME]['errores'].insert_one(err_dict)
            return str(resultado.inserted_id)  
        finally:
            cliente.close()  
    return None"""