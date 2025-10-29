from helpers.apl import get_apl_directive, get_colores_apl_directive
from db.coda import obtener_usuario_por_num_usuario, insertar_sesion, insertar_usuario
from db.colores import insertar_intento_usuario
from db.models import Sesion, Usuario, Intento
from helpers.utils import inicializar_variables, hora_actual, reproducir_secuencia, generador_secuencia, MAX_DIGITOS, ahora

import pytz


def bienvenida(handler_input):
    session_attributes = handler_input.attributes_manager.session_attributes
    session_attributes['primera_interaccion'] = True
    session_attributes['estado_juego'] = 0

    msj_bienvenida = "¡Bienvenido al Juego de Colores!"
    msj_instruccion = (
        "Di 'COLORES' seguido de tu número de usuario para buscar tu información, "
        "o di: '¡QUIERO REGISTRARME!'."
    )
    speech_text = f"{msj_bienvenida} {msj_instruccion}"

    directiva_apl = get_apl_directive('mensaje_simple.json', 
        {"mensaje": {"titulo": msj_bienvenida, "descripcion": msj_instruccion}}, "bienvenida")

    if directiva_apl:
        handler_input.response_builder.add_directive(directiva_apl)

    return handler_input.response_builder.speak(speech_text).ask(msj_instruccion).response


def iniciar_sesion(handler_input):
    session_attributes = handler_input.attributes_manager.session_attributes
    slot_data = handler_input.request_envelope.request.intent.slots.get('num_usuario')
    num_usuario = slot_data.value if slot_data and slot_data.value else None
    
    if num_usuario:
        usuario = obtener_usuario_por_num_usuario(int(num_usuario))

        if usuario:
            timestamp_utc = handler_input.request_envelope.request.timestamp
            zona_local = pytz.timezone("America/Guayaquil")
            fecha_hora_local = timestamp_utc.astimezone(zona_local)

            sesion = Sesion()
            sesion.id_usuario = usuario.id
            sesion.fecha_inicio = fecha_hora_local.strftime('%Y-%m-%d')
            sesion.hora_inicio = fecha_hora_local.strftime('%H:%M:%S')
            sesion.hora_fin = sesion.hora_inicio

            sesion.id = insertar_sesion(sesion)

            session_attributes['usuario_id'] = usuario.id
            session_attributes['sesion_id'] = sesion.id
            
            speech_text = (
                        f'Bienvenido, usuario número {usuario.num_usuario}, di: "PRESENTAR REGLAS", '
                        'para presentarte las reglas del juego, o "JUGAR" si ya conoces las reglas.'
                    )
            return handler_input.response_builder.speak(speech_text).ask(speech_text).response
            

        speech_text = (
            'No he podido localizar tu información, Di "SECUENCIA DIRECTA" seguido de tu número de usuario para buscar tu información, '
            'o si deseas registrarte di: "QUIERO REGISTRARME".'
        )
        
        return handler_input.response_builder.speak(speech_text).ask(speech_text).response


def registrar_usuario(handler_input):
    preguntas_registro = [
        "Pregunta 1. Responde a la siguiente pregunta diciendo por ejemplo: tengo 50 años. ¿Cuántos años tienes?",
        "Pregunta 2. Responde a la siguiente pregunta diciendo por ejemplo: soy Carpintero. ¿Cuál es tu profesión?"
    ]
    
    mensaje_inicio = f'Bienvenido al registro de usuarios. Deberás responder las siguientes preguntas: '
    speech_text = ''
    session_attributes = handler_input.attributes_manager.session_attributes
    slot_data = handler_input.request_envelope.request.intent.slots.get('data_registro')
    data_registro = slot_data.value if slot_data and slot_data.value else None
    
    if not data_registro and session_attributes['primera_interaccion']:
        session_attributes['primera_interaccion'] = False
        session_attributes['indice_preguntas'] = 0
        
        speech_text =  f'{mensaje_inicio} {preguntas_registro[0]}'
        
        return handler_input.response_builder.speak(speech_text).ask(f'{preguntas_registro[0]}').response
        
    elif data_registro and not session_attributes['primera_interaccion']:
        indice = session_attributes['indice_preguntas']
        if indice == 0:
            session_attributes['edad'] = int(data_registro) if data_registro.isdigit() else 0
            if session_attributes['edad'] > 0:
                session_attributes['indice_preguntas'] += 1
                speech_text = f'{preguntas_registro[1]}'
            else:
                speech_text = f'No pude entender tu edad: {preguntas_registro[0]}'
        elif indice == 1:
            session_attributes['profesion'] = data_registro
            
            usuario = Usuario()
            usuario.edad = session_attributes['edad']
            usuario.profesion = session_attributes['profesion']
            
            timestamp_utc = handler_input.request_envelope.request.timestamp
            zona_local = pytz.timezone("America/Guayaquil")
            fecha_hora_local = timestamp_utc.astimezone(zona_local)
            
            sesion = Sesion()
            sesion.fecha_inicio = fecha_hora_local.strftime('%Y-%m-%d')
            sesion.hora_inicio = fecha_hora_local.strftime('%H:%M:%S')
            sesion.hora_fin = sesion.hora_inicio
            usuario.id = insertar_usuario(usuario)
            sesion.id_usuario = usuario.id
            sesion.id = insertar_sesion(sesion)
            session_attributes['usuario_id'] = usuario.id
            session_attributes['sesion_id'] = sesion.id
            
            if usuario.id:
                speech_text =  f'¡Registro exitoso. Tu número de usuario es: {usuario.num_usuario}.'
                return handler_input.response_builder.speak(speech_text).ask(speech_text).response
            else:
                speech_text = '¡No se ha podido establecer la conexión con la base de datos!'
    else:
            
        speech_text = f"Vaya, no pude entender lo que dijiste: {preguntas_registro[session_attributes['indice_preguntas']]}"

    return handler_input.response_builder.speak(speech_text).ask(speech_text).response


def presentar_reglas(handler_input):
    session_attributes = handler_input.attributes_manager.session_attributes

    if session_attributes['usuario_id']:
        speech_text = (
            "¡Escuche con atención!: En este juego te voy a decir algunos colores, cuando haya terminado, "
            "marca inmediatamente en la pantalla los colores correspondientes en el mismo orden en que te los he dicho. "
            "Si necesitas que se repitan las instrucciones di: Alexa, dime las instrucciones. Si quieres jugar di: quiero jugar"
        )
        return handler_input.response_builder.speak(speech_text).ask(speech_text).response
    
    return get_msj_iniciar_sesion(handler_input)

def jugar(handler_input):
    session_attr = inicializar_variables(session_attr)
    session_attr['num_serie'] += 1
    
    speech = reproducir_secuencia(
        handler_input,
        session_attr['secuencia'],
        True,
        session_attr["modo"]
    )
    
    return (
        handler_input.response_builder
            .speak(speech)
            .response
    )


"""
def jugar(handler_input):
    session_attributes = handler_input.attributes_manager.session_attributes

    if session_attributes['usuario_id']:
        session_attributes = inicializar_variables(session_attributes)
        session_attributes['num_serie'] += 1

        speech_text = "<speak> <audio src='soundbank://soundlibrary/alarms/beeps_and_bloops/bell_01'/> <break time='1s'/>"
        
        if session_attributes['primera_interaccion'] and session_attributes["modo"] == 0:
            speech_text = "<speak> ¡Genial! Comenzamos. <break time='1s'/>"

        if session_attributes['primera_interaccion'] and session_attributes["modo"] == 1:
            speech_text += " Hemos acabado. Ahora vamos a jugar a colores indirecto. ¡Escucha con atención!: y, cuando termine, marque inmediatamente en la pantalla la imagen de los colores que se han dicho, de atrás para adelante, es decir, si yo le digo: azul <break time='500ms'/> verde <break time='500ms'/> amarillo  <break time='500ms'/> usted debería pulsar: amarillo <break time='500ms'/> verde <break time='500ms'/> azul. <break time='1s'/>"
            
        secuencia_hablada = session_attributes['secuencia'].replace(" "," <break time='500ms'/> ")
        speech_text += " ¡Escucha con atención!: <break time='1s'/> Los colores son: <break time='1s'/> " + secuencia_hablada + ".<break time='0.500ms'/> Marca en la pantalla."
        speech_text += "</speak>"

        directiva_apl = get_colores_apl_directive()

        if directiva_apl:
            handler_input.response_builder.add_directive(directiva_apl)

        return handler_input.response_builder.speak(speech_text).response
    
    return get_msj_iniciar_sesion(handler_input)
"""

def evento_colores(handler_input):
    session_attr = handler_input.attributes_manager.session_attributes
    tecla_pulsada = handler_input.request_envelope.request.arguments[0]

    if session_attr['estado_juego'] == 1:
        # Si aún no se ha completado la secuencia
        if session_attr["intentos"] < session_attr["serie"] - 1:
            session_attr["intentos"] += 1
            session_attr["secuencia_intento"] += tecla_pulsada
            speech = ("<speak></speak>")
        else:
            session_attr["secuencia_intento"] += tecla_pulsada
            secuencia_oficial = ''.join(session_attr["secuencia"].split(' '))

            # Si el modo es indirecto se da la vuelta a la lista
            if session_attr["modo"] == 1:
                session_attr["secuencia_intento"] = ''.join(
                    list(reversed(session_attr["secuencia_intento"].split()))
                )
                secuencia_oficial = ''.join(
                    list(reversed(session_attr["secuencia"].split(' ')))
                )

            # Si ha fallado 
            if secuencia_oficial != session_attr["secuencia_intento"]:
                session_attr["fallos"] += 1
                pnt_turno = 0

                # Si ha fallado dos veces seguidas
                if session_attr["fallos"] == 2:
                    if session_attr["modo"] == 0:
                        
                        speech = (coloresIndirecto(handler_input))
                    else:
                        
                        speech = ("Hemos acabado. Gracias por jugar conmigo. ¡Hasta la próxima!")
                        session_attr['estado_juego'] = 0
                      
                        return handler_input.response_builder.speak(speech).set_should_end_session(True).response

                else:  # Si ha fallado solo una vez
                    # Si ha llegado al final
                    if session_attr['serie'] == MAX_DIGITOS and session_attr['num_serie'] > 2:
                        pnt_turno = 1
                        if session_attr["modo"] == 0:
                            
                            speech = (coloresIndirecto(handler_input))
                        else:
                            speech = ("<speak>Hemos acabado. ¡Hasta la proxima!</speak>")
                            session_attr['estado_juego'] = 0
                            handler_input.response_builder.set_should_end_session(True)
                            session_attr["estado_juego"] = 0
                            session_attr["secuencia_intento"] = ''
                            session_attr["intentos"] = 0

                            return handler_input.response_builder.speak(speech).set_should_end_session(True).response
                    else:
                        # Se reestablecen los parametros para la siguiente secuencia
                        if session_attr['num_serie'] > 2:  # si estamos en la serie 2
                            session_attr['serie'] += 1
                            session_attr['num_serie'] = 1
                            session_attr["fallos"] = 0
                        session_attr["secuencia_intento"] = ''
                        session_attr["intentos"] = 0
                        session_attr['secuencia'] = generador_secuencia(session_attr['serie'])
                        speech = reproducir_secuencia(
                            handler_input, session_attr['secuencia'], False, session_attr["modo"], True
                        )

            # Si ha acertado
            else:
                # Si ha llegado al final
                if session_attr['serie'] == MAX_DIGITOS and session_attr['num_serie'] > 2:
                    pnt_turno = 1
                    if session_attr["modo"] == 0:
                        
                        speech = (coloresIndirecto(handler_input))
                    else:
                        
                        speech = ("<speak>Hemos acabado. ¡Hasta la proxima!</speak>")
                        handler_input.response_builder.set_should_end_session(True)
                        session_attr["estado_juego"] = 0
                        session_attr["secuencia_intento"] = ''
                        session_attr["intentos"] = 0
                       
                        return handler_input.response_builder.speak(speech).set_should_end_session(True).response
                else:
                    if session_attr['num_serie'] > 2:  # si estamos en la serie 2
                       
                        session_attr['serie'] += 1
                        session_attr['num_serie'] = 1
                        session_attr["fallos"] = 0
                    pnt_turno = 1
                    session_attr['secuencia'] = generador_secuencia(session_attr['serie'])
                    session_attr["puntuacion"] = session_attr['serie']
                    # Aleatoriamente dice o muestra la secuencia
                    speech = reproducir_secuencia(
                        handler_input, session_attr['secuencia'], False, session_attr["modo"]
                    )

            # BBDD
            
            session_attr['num_serie'] += 1
            session_attr["inicio_turno"] = ahora()
            # Se reestablecen los parametros para la siguiente secuencia
            session_attr["secuencia_intento"] = ''
            session_attr["intentos"] = 0
    else:
        speech = ("<speak>Parece que quieres jugar. Di: Alexa, quiero jugar</speak>")

    return (
        handler_input.response_builder
            .speak(speech)
            .response
    )


"""
def evento(handler_input): 
    session_attr = handler_input.attributes_manager.session_attributes
    tecla_pulsada = handler_input.request_envelope.request.arguments[0]
    
    # Si la partida está activa
    if session_attr['estado_juego'] == 1:

        # Guardamos hora de inicio del turno si aún no existe
        if "inicio_turno" not in session_attr:
            session_attr["inicio_turno"] = hora_actual()

        # Si aún no se ha completado la secuencia
        if session_attr["intentos"] < session_attr["serie"] - 1:
            session_attr["intentos"] += 1
            session_attr["secuencia_intento"] += tecla_pulsada
            speech = "<speak></speak>"
        
        else:
            # Último intento de la secuencia actual
            session_attr["secuencia_intento"] += tecla_pulsada
            secuencia_oficial = ''.join(session_attr["secuencia"].split(' '))

            # Si el modo es indirecto, invertir secuencias
            if session_attr["modo"] == 1:
                session_attr["secuencia_intento"] = ''.join(list(reversed(session_attr["secuencia_intento"].split())))
                secuencia_oficial = ''.join(list(reversed(session_attr["secuencia"].split(' '))))

            # Comparar si acertó o falló
            acierto = (secuencia_oficial == session_attr["secuencia_intento"])

            # Generar registro de intento (MongoDB)
            intento = Intento(
                id_sesion=session_attr.get('game_id'),
                id_usuario=session_attr.get('email'),
                es_acertado=acierto,
                hora_inicio=session_attr.get("inicio_turno"),
                hora_fin=hora_actual(),
                respuesta_usuario=session_attr.get("secuencia_intento"),
                respuesta_correcta=secuencia_oficial,
                tipo="directo" if session_attr.get("modo") == 0 else "indirecto",
                num_intentos=session_attr.get("serie")
            )
            insertar_intento_usuario(intento)

            # Reiniciar hora de inicio para el siguiente intento
            session_attr["inicio_turno"] = hora_actual()

            # --- Lógica del juego ---
            if not acierto:
                session_attr["fallos"] += 1
                pnt_turno = 0

                # Si ha fallado dos veces seguidas
                if session_attr["fallos"] == 2:
                    if session_attr["modo"] == 0: 
                        logger.info("INFO: Ha fallado 2 veces seguidas la misma serie en el modo DIRECTO")
                        # Reiniciar juego en modo directo
                        session_attr['game_id'] = str(datetime.now().timestamp())  # Simulamos nuevo id
                        speech = coloresIndirecto(handler_input)
                    else:
                        logger.info("INFO: Ha fallado 2 veces seguidas la misma serie en el modo INDIRECTO")
                        speech = "Hemos acabado. Gracias por jugar conmigo. ¡Hasta la próxima!"
                        session_attr['estado_juego'] = 0
                        return handler_input.response_builder.speak(speech).set_should_end_session(True).response

                else:
                    # Si ha fallado una vez pero no se acabó
                    if session_attr['serie'] == data.MAX_DIGITOS and session_attr['num_serie'] > 2:
                        pnt_turno = 1
                        if session_attr["modo"] == 0:
                            logger.info("INFO: Ha completado el modo DIRECTO")
                            session_attr['game_id'] = str(datetime.now().timestamp())
                            speech = coloresIndirecto(handler_input)
                        else:
                            logger.info("INFO: Ha completado el modo INDIRECTO")
                            speech = "<speak>Hemos acabado. ¡Hasta la próxima!</speak>"
                            session_attr['estado_juego'] = 0
                            return handler_input.response_builder.speak(speech).set_should_end_session(True).response
                    else:
                        if session_attr['num_serie'] > 2:
                            session_attr['serie'] += 1
                            session_attr['num_serie'] = 1
                            session_attr["fallos"] = 0
                        session_attr["secuencia_intento"] = ''
                        session_attr["intentos"] = 0
                        session_attr['secuencia'] = utils.generador_secuencia(session_attr['serie'])
                        speech = utils.reproducir_secuencia(handler_input, session_attr['secuencia'], False, session_attr["modo"], True)
            
            else:
                # Si acertó
                if session_attr['serie'] == data.MAX_DIGITOS and session_attr['num_serie'] > 2:
                    pnt_turno = 1
                    if session_attr["modo"] == 0:
                        logger.info("INFO: Ha completado el modo DIRECTO")
                        session_attr['game_id'] = str(datetime.now().timestamp())
                        speech = coloresIndirecto(handler_input)
                    else:
                        logger.info("INFO: Ha completado el modo INDIRECTO")
                        speech = "<speak>Hemos acabado. ¡Hasta la próxima!</speak>"
                        session_attr['estado_juego'] = 0
                        return handler_input.response_builder.speak(speech).set_should_end_session(True).response
                else:
                    if session_attr['num_serie'] > 2:
                        session_attr['serie'] += 1
                        session_attr['num_serie'] = 1
                        session_attr["fallos"] = 0
                    pnt_turno = 1
                    session_attr['secuencia'] = utils.generador_secuencia(session_attr['serie'])
                    session_attr["puntuacion"] = session_attr['serie']
                    speech = utils.reproducir_secuencia(handler_input, session_attr['secuencia'], False, session_attr["modo"])

            # Actualizar variables de sesión
            session_attr['num_serie'] += 1
            session_attr["secuencia_intento"] = ''
            session_attr["intentos"] = 0

    else:
        speech = "<speak>Parece que quieres jugar. Di: Alexa, quiero jugar</speak>"

    return handler_input.response_builder.speak(speech).response



def evento_colores(handler_input):

    session_attributes = handler_input.attributes_manager.session_attributes
    

    if session_attributes['usuario_id']:
        hora_inicio = hora_actual()
        intento = Intento()
        intento.id_sesion = session_attributes['sesion_id']
        intento.id_usuario = session_attributes['usuario_id']

        session_attributes = handler_input.attributes_manager.session_attributes
        tecla_pulsada = handler_input.request_envelope.request.arguments[0]

        if session_attributes['estado_juego'] == 1:
            if session_attributes["intentos"] < session_attributes["serie"] - 1:
                session_attributes["intentos"] += 1
                session_attributes["secuencia_intento"] += tecla_pulsada
                speech_text = ("<speak></speak>")
            
            else:
                session_attributes["secuencia_intento"] += tecla_pulsada
                secuencia_oficial = ''.join(session_attributes["secuencia"].split(' '))

                if session_attributes["modo"] == 1:
                    session_attributes["secuencia_intento"] = ''.join(list(reversed(session_attributes["secuencia_intento"].split())))
                    secuencia_oficial = ''.join(list(reversed(session_attributes["secuencia"].split(' ')))) 

                if secuencia_oficial != session_attributes["secuencia_intento"]:
                    session_attributes["fallos"] += 1
                    pnt_turno = 0
                    if session_attributes["fallos"] == 2:
                        if session_attributes["modo"] == 0: 
                            
                            intento.es_acertado =
                            intento.hora_inicio = hora_inicio
                            intento.hora_fin = hora_fin
                            intento.respuesta_usuario = respuesta_usuario
                            intento.respuesta_correcta = respuesta_correcta
                            intento.tipo = tipo
                            intento.num_intentos = num_intentos


    return get_msj_iniciar_sesion(handler_input)"""


# EXTRAS: --------------------------------------------------------------------------------------------------
def coloresIndirecto(handler_input):
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr["modo"] = 1
    session_attr["fallos"] = 0
    session_attr['num_serie'] = 1
    session_attr["secuencia_intento"] = ''
    session_attr['serie'] = 2
    session_attr["intentos"] = 0 
    session_attr['secuencia'] = generador_secuencia(session_attr['serie'])
    # Aleatoriamente dice o muestra la secuencia
    speech = reproducir_secuencia(handler_input, session_attr['secuencia'], True, session_attr["modo"])
    return speech


def get_msj_iniciar_sesion(handler_input):
    speech_text = (
        "No haz iniciado sesión aún: "
        "Di 'COLORES' seguido de tu número de usuario para buscar tu información, "
        "o di: '¡QUIERO REGISTRARME!'."
    )

    return handler_input.response_builder.speak(speech_text).ask(speech_text).response