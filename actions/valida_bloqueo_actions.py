import logging
from typing import Any, Dict, Text
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

logger = logging.getLogger(__name__)

import re

def validar_rut_chileno(rut: str) -> bool:
    logger.debug(f"Validando RUT chileno: {rut}")
    rut = rut.replace(".", "").replace("-", "").upper()

    if not re.match(r"^\d{7,8}[0-9K]$", rut):
        logger.debug("RUT no cumple con el formato esperado.")  
        return False

    cuerpo = rut[:-1]
    dv = rut[-1]
    suma = 0
    factor = 2
    for c in reversed(cuerpo):
        suma += int(c) * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - (suma % 11)
    dv_calculado = {
        11: "0",
        10: "K"
    }.get(resto, str(resto))
    logger.debug(f"RUT calculado: {dv_calculado}, RUT ingresado: {dv}")
    logger.debug(f"RUT válido: {dv == dv_calculado}")
    return dv == dv_calculado


class ValidateBloquearTarjetaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_bloquear_tarjeta_form"

    def validate_rut(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if validar_rut_chileno(slot_value):
            return {"rut": slot_value}
        else:
            dispatcher.utter_message(text="El RUT parece inválido. Por favor, intenta nuevamente.")
            return {"rut": None}

    def validate_password(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if len(slot_value) == 4:
            return {"password": slot_value}
        else:
            dispatcher.utter_message(text="La contraseña debe tener exactamente 4 dígitos.")
            return {"password": None}