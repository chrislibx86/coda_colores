from random import randint
from datetime import datetime as pokereloj

from helpers.apl import get_colores_apl_directive


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


def initialise_variables(session_attr):
    """Inicializar las variables para un nuevo juego."""
    # Indica si el juego se está llevando a cabo (igual a 1) o no (igual a 0)
    session_attr['estado_juego'] = 1
    # Indica el tamaño de la serie // TURNO -3
    session_attr['serie'] = 2
    # Almacena la secuencia oficial
    session_attr['secuencia'] = generador_secuencia(session_attr['serie'])
    # Almacena la puntuación del usuario
    session_attr["puntuacion"] = 0
    # Almacena el número de veces que ha pulsado el usuario
    session_attr["intentos"] = 0 
    # Almacena la secuencia del usuario
    session_attr["secuencia_intento"] = ""
    # Almacena la serie (1 o 2)
    session_attr["num_serie"] = 1
    # Almacena las veces que ha fallado
    session_attr["fallos"] = 0
    # Almacena el modo de juego (Directo o Indirecto)
    session_attr["modo"] = 0 # 0 -> directo , 1-> indirecto
    # Almacena el momento en el que comienza el turno
    session_attr["inicio_turno"] = ahora()
    return session_attr

"""
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
"""

def reproducir_secuencia(handler_input, secuencia, primeravez, modo, fallo = False):
    """Aleatoriamente reproduce la secuencia con la voz o visualmente."""

    response_builder = handler_input.response_builder

    speak_output = "<speak> <audio src='soundbank://soundlibrary/alarms/beeps_and_bloops/bell_01'/> <break time='1s'/>"
    if primeravez and modo == 0:
        speak_output = "<speak> ¡Genial! Comenzamos. <break time='1s'/>"
    if modo == 1 and primeravez:
        speak_output += " Hemos acabado. Ahora vamos a jugar a colores indirecto. Escuche con atención y, cuando termine, marque inmediatamente en la pantalla la imagen de los colores que se han dicho, de atrás para adelante, es decir, si yo le digo: azul <break time='500ms'/> verde <break time='500ms'/> amarillo  <break time='500ms'/> usted debería pulsar: amarillo <break time='500ms'/> verde <break time='500ms'/> azul. <break time='1s'/>"
        
    secuencia_hablada = secuencia.replace(" "," <break time='500ms'/> ")
    speak_output += " Escuche con atención. <break time='1s'/> Los colores son: <break time='1s'/> " + secuencia_hablada + ".<break time='0.500ms'/> Marca en la pantalla."
    speak_output += "</speak>"
    
    apl_directive = get_colores_apl_directive()
    if apl_directive:
        response_builder.add_directive(apl_directive )

    return speak_output


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


def hora_actual():
    return pokereloj.now().strftime("%H:%M:%S")