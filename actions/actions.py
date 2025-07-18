from datetime import datetime
import os
import re
import logging
import requests
from typing import Any, Dict, List, Optional, Text

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.types import DomainDict


logger = logging.getLogger(__name__)

# --- Acciones simples ---

class ActionDarHora(Action):
    def name(self) -> str:
        return "action_dar_hora"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        hora_actual = datetime.now().strftime("%H:%M")
        dispatcher.utter_message(text=f"La hora actual es {hora_actual} ⏰")
        return []

class ActionConsultarUF(Action):
    def name(self) -> str:
        return "action_consultar_uf"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        fecha_actual = datetime.now().strftime('%d-%m-%Y')
        url = f'https://mindicador.cl/api/uf/{fecha_actual}'

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if "serie" in data and data["serie"]:
                uf_valor = data["serie"][0]["valor"]
                mensaje = f"Valor UF para {fecha_actual}: {uf_valor}"
            else:
                mensaje = f"No hay datos disponibles para la fecha {fecha_actual}"

        except requests.RequestException as e:
            mensaje = f"Error al consumir la API: {e}"

        dispatcher.utter_message(text=mensaje)
        return []


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

class ActionProcesarBloqueo(Action):
    def name(self) -> Text:
        return "action_procesar_bloqueo"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
        rut = tracker.get_slot("rut")
        password = tracker.get_slot("password")

        # Llamada al servicio dummy (aquí solo simulado)
        print(f"Llamando servicio dummy con rut: {rut} y password: {password}")

        dispatcher.utter_message(text="Estamos procesando tu bloqueo.")
        return []