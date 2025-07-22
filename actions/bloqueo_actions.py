import logging
from pdb import Restart
from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet, Restarted

logger = logging.getLogger(__name__)

class ActionProcesarBloqueo(Action):
    def name(self) -> Text:
        return "action_procesar_bloqueo"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
        logger.info("Ejecutando acción de procesamiento de bloqueo.")
        intentos = tracker.get_slot("auth_fail_count")
        if intentos >= 3:
            logger.warning(f"Usuario ha fallado la autenticación {intentos} veces. Procediendo a cierre forzado.")
            #return [SlotSet("auth_fail_count", 0), SlotSet("tarjeta", None), SlotSet("opciones_tarjetas", None), Restart()]
            return [Restarted()]
        
        rut = tracker.get_slot("rut")
        if not rut:
            logger.error("RUT no encontrado en el tracker.")
            #dispatcher.utter_message(text="No se ha proporcionado un RUT válido.")
            return [Restarted()]
        password = tracker.get_slot("password")
        tarjeta = tracker.get_slot("tarjeta")
        logger.info(f"Datos recibidos: RUT={rut}, Tarjeta={tarjeta}, Intentos={intentos}")
        # Llamada al servicio dummy (aquí solo simulado)
        logger.info(f"Procesando bloqueo para RUT: {rut}, Tarjeta: {tarjeta}")
        dispatcher.utter_message(text="Estamos procesando tu bloqueo.")
        # Aquí podrías agregar lógica para interactuar con un servicio externo
        # o realizar alguna acción adicional.        
        return [
            SlotSet("tarjeta", None),
            SlotSet("opciones_tarjetas", None),
            SlotSet("auth_fail_count", 0),
        ]