from helpers.apl import get_apl_directive
from db.coda import obtener_usuario_por_num_usuario, insertar_sesion, insertar_usuario
from db.models import Sesion, Usuario

import pytz


def bienvenida(handler_input):
    session_attributes = handler_input.attributes_manager.session_attributes
    session_attributes['primera_interaccion'] = True

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