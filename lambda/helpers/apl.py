from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

import os
import json

from helpers.dev import insertar_error
import traceback


def get_apl_directive(apl_docname, datasources, token):
    try:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apldocs"))
        apl_path = os.path.join(base_path, apl_docname)

        with open(apl_path, "r", encoding="utf-8") as apl_file:
            apl_document = json.load(apl_file)

        return RenderDocumentDirective(
            token=token,
            document=apl_document,
            datasources=datasources
        )

    except Exception:
        error_trace = traceback.format_exc()
        insertar_error(error_trace)
        return None