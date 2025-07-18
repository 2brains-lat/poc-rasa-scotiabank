import logging
from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

logger = logging.getLogger(__name__)

class ActionProcesarBloqueo(Action):
    def name(self) -> Text:
        return "action_procesar_bloqueo"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
        logger.info("Ejecutando acción de procesamiento de bloqueo.")
        rut = tracker.get_slot("rut")
        password = tracker.get_slot("password")
        tarjeta = tracker.get_slot("tarjeta")
        # Llamada al servicio dummy (aquí solo simulado)
        logger.info(f"Procesando bloqueo para RUT: {rut}, Tarjeta: {tarjeta}")
        dispatcher.utter_message(text="Estamos procesando tu bloqueo.")
        return []