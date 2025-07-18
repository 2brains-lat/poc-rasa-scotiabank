import logging
from typing import Any, Dict, Text
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

logger = logging.getLogger(__name__)

class ValidateBloquearTarjetaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_bloquear_tarjeta_form"

    def validate_rut(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if len(slot_value) >= 8:  # Validación simple
            return {"rut": slot_value}
        else:
            dispatcher.utter_message(text="El RUT parece inválido. Por favor, intenta nuevamente.")
            return {"rut": None}

    def validate_password(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if len(slot_value) >= 4:
            return {"password": slot_value}
        else:
            dispatcher.utter_message(text="La contraseña es muy corta.")
            return {"password": None}