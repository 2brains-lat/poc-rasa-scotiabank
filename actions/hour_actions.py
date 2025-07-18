import logging
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime


logger = logging.getLogger(__name__)

class ActionDarHora(Action):
    def name(self) -> str:
        return "action_dar_hora"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        hora_actual = datetime.now().strftime("%H:%M")
        dispatcher.utter_message(text=f"La hora actual es {hora_actual} ⏰")
        logger.info(f"Hora actual: {hora_actual}")
        return []