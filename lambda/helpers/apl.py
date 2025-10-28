from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

import os
import json


def get_apl_directive(apl_docname, datasources, token):
    try:
        apl_path = os.path.join(os.path.dirname(__file__), "apldocs", apl_docname)

        with open(apl_path, "r", encoding="utf-8") as apl_file:
            apl_document = json.load(apl_file)

        return RenderDocumentDirective(
            token=token,
            document=apl_document,
            datasources=datasources
        )

    except Exception:
        from helpers.dev import insertar_error
        insertar_error()
        return None