from random import randint
from datetime import datetime as pokereloj


COLORES = {
    1: 'rojo',
    2: 'verde',
    3: 'gris',
    4: 'rosa',
    5: 'naranja',
    6: 'azul',
    7: 'amarillo',
    8: 'café'
}


COLORES_CONFIG ={
    'amarillo': {'ide':"id_uno", 'prop':"dark_uno", 'idtouch':"touch_uno"},
    'rojo': {'ide':"id_dos", 'prop':"dark_dos", 'idtouch':"touch_dos"},
    'gris': {'ide':"id_tres", 'prop':"dark_tres", 'idtouch':"touch_tres"},
    'rosa': {'ide':"id_cuatro", 'prop':"dark_cuatro", 'idtouch':"touch_cuatro"},
    'naranja': {'ide':"id_cinco", 'prop':"dark_cinco", 'idtouch':"touch_cinco"},
    'azul': {'ide':"id_seis", 'prop':"dark_seis", 'idtouch':"touch_seis"},
    'amarillo': {'ide':"id_siete", 'prop':"dark_siete", 'idtouch':"touch_siete"},
    'marron': {'ide':"id_ocho", 'prop':"dark_ocho", 'idtouch':"touch_ocho"}
}


MAX_DIGITOS = 8


def inicializar_variables(session_attr):
    session_attr['estado_juego'] = 1
    session_attr['serie'] = 2
    session_attr['secuencia'] = generador_secuencia(session_attr['serie'])
    session_attr["puntuacion"] = 0
    session_attr["intentos"] = 0 
    session_attr["secuencia_intento"] = ""
    session_attr["num_serie"] = 1
    session_attr["fallos"] = 0
    session_attr["modo"] = 0 
    session_attr["inicio_turno"] = ahora()
    return session_attr


def generador_secuencia(serie):
    secuencia = ""
    colores = list(COLORES.values())
    for i in range(serie):
        x = randint(0, 7-i)
        color = colores.pop(x)
        secuencia += color +' '
    return secuencia[:-1]


def ahora():
    return pokereloj.now().strftime("%Y-%m-%dT%H:%M:%S")