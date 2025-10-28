from helpers.dev import insertar_error
import traceback

try:

    from ask_sdk_core.skill_builder import SkillBuilder
    from ask_sdk_core.utils import is_intent_name, is_request_type, request_util

    from handlers.colores import bienvenida, iniciar_sesion, registrar_usuario


    sb = SkillBuilder()


    @sb.request_handler(can_handle_func=is_request_type('LaunchRequest'))
    def launch_request_handler(handler_input):
        return bienvenida(handler_input)


    @sb.request_handler(can_handle_func=is_intent_name("LoginIntent"))
    def login_intent_handler(handler_input):
        return iniciar_sesion(handler_input)


    @sb.request_handler(can_handle_func=is_intent_name("RegisterIntent"))
    def register_intent_handler(handler_input):
        return registrar_usuario(handler_input)


    lambda_handler = sb.lambda_handler()

except Exception as e:
    error_trace = traceback.format_exc()
    insertar_error(error_trace)