import logging
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

class ActionConsultarUF(Action):
    def name(self) -> str:
        return "action_consultar_uf"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        fecha_actual = datetime.now().strftime('%d-%m-%Y')
        url = f'https://mindicador.cl/api/uf/{fecha_actual}'
        logger.info(f"Consultando valor UF para la fecha: {fecha_actual}")  
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if "serie" in data and data["serie"]:
                uf_valor = data["serie"][0]["valor"]
                mensaje = f"Valor UF para {fecha_actual}: {uf_valor}"
            else:
                mensaje = f"No hay datos disponibles para la fecha {fecha_actual}"
            logger.info(mensaje)
        except requests.RequestException as e:
            mensaje = f"Error al consumir la API: {e}"
            logger.error(mensaje)

        dispatcher.utter_message(text=mensaje)
        return []