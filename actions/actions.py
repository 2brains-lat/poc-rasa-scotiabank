
from datetime import datetime
from rasa_sdk import Action, Tracker, FormValidationAction, Action # type: ignore
from rasa_sdk.executor import CollectingDispatcher # type: ignore
import requests # type: ignore

from typing import Any, Dict, List, Text
#from rasa_sdk.types import DomainDict

#from rasa_sdk.types import DomainDict
import re
import logging

class ActionDarHora(Action):

    def name(self) -> str:
        return "action_dar_hora"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:

        hora_actual = datetime.now().strftime("%H:%M")
        mensaje = f"La hora actual es {hora_actual} ⏰"
        dispatcher.utter_message(text=mensaje)

        return []

class ActionConsultarUF(Action):

    def name(self) -> str:
        return "action_consultar_uf"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:

        # Obtener fecha actual del sistema en formato dd-mm-yyyy
        fecha_actual = datetime.now().strftime('%d-%m-%Y')
        
        # Construir la URL con la fecha actual
        url = f'https://mindicador.cl/api/uf/{fecha_actual}'
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Lanza error si el status code no es 200
            
            data = response.json()
            # Verificar que hay datos disponibles
            if "serie" in data and data["serie"]:
                uf_valor = data["serie"][0]["valor"]
                mensaje = f"Valor UF para {fecha_actual}: {uf_valor}"
            else:
                mensaje = f"No hay datos disponibles para la fecha {fecha_actual}"
                
        except requests.RequestException as e:
            mensaje = f"Error al consumir la API: {e}"

        dispatcher.utter_message(text=mensaje)

        return []

# class ActionProcesarBloqueo(Action):
#     def name(self) -> str:
#         return "action_procesar_bloqueo"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[str, Any]) -> List[Dict[str, Any]]:

#         rut = tracker.get_slot("rut")
#         password = tracker.get_slot("password")

#         # Simulación de lógica de bloqueo
#         print(f"[DEBUG] RUT recibido: {rut}")
#         print(f"[DEBUG] Contraseña recibida: {password}")

#         return []

# class ValidateFormularioBloqueoTarjeta(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_formulario_bloqueo_tarjeta"

#     def validate_rut(
#         self, slot_value: Any, dispatcher: CollectingDispatcher,
#         tracker: Tracker, domain: Dict[Text, Any]
#     ) -> Dict[Text, Any]:
#         # Solo validar si el último slot solicitado fue rut
#         if tracker.get_slot("requested_slot") != "rut":
#             return {"rut": slot_value}

#         if isinstance(slot_value, str) and len(slot_value.strip()) >= 8:
#             return {"rut": slot_value}

#         dispatcher.utter_message(text="El RUT parece inválido.")
#         return {"rut": None}

#     def validate_password(
#         self, slot_value: Any, dispatcher: CollectingDispatcher,
#         tracker: Tracker, domain: Dict[Text, Any]
#     ) -> Dict[Text, Any]:
#         # Solo validar si el último slot solicitado fue password
#         if tracker.get_slot("requested_slot") != "password":
#             return {"password": slot_value}

#         if isinstance(slot_value, str) and len(slot_value.strip()) == 4:
#             return {"password": slot_value}

#         dispatcher.utter_message(text="La contraseña debe tener exactamente 4 caracteres.")
#         return {"password": None}




logger = logging.getLogger(__name__)

def validar_rut_chileno(rut: str) -> bool:
    pattern = r'^\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]$'
    return re.match(pattern, rut) is not None

class ValidateBloquearTarjetaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_bloquear_tarjeta_form"

    def validate_rut(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        if validar_rut_chileno(slot_value):
            return {"rut": slot_value}
        dispatcher.utter_message(response="utter_invalid_rut")
        return {"rut": None}

    def validate_password(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        if len(slot_value) == 4 and slot_value.isdigit():
            return {"password": slot_value}
        dispatcher.utter_message(response="utter_invalid_password")
        return {"password": None}

class ActionProcesarBloqueo(Action):
    def name(self) -> Text:
        return "action_procesar_bloqueo"

    def run(self, dispatcher, tracker, domain):
        rut = tracker.get_slot("rut")
        password = tracker.get_slot("password")

        # Simulación del llamado al API dummy
        logger.info(f"Llamando API de bloqueo para RUT: {rut}, password: {password}")
        print(f"Simulación de API: Bloqueo solicitado para RUT {rut} con contraseña {password}")

        dispatcher.utter_message(response="utter_submit_bloqueo")
        return []
