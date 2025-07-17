from datetime import datetime
import os
import re
import logging
import requests
from typing import Any, Dict, List, Optional, Text

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

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

# --- Validaciones auxiliares ---

def validar_rut_chileno(rut: str) -> bool:
    if not rut:
        return False
    return bool(re.match(r"^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$", rut.strip()))

def validar_rut_chileno_sin_puntos(rut: str) -> bool:
    rut = rut.replace(".", "").strip()
    return bool(re.match(r"^\d{7,8}-[\dkK]$", rut))

def autenticar_usuario(rut: str, password: str) -> Optional[List[str]]:
    archivo = "data/tarjetas.txt"
    if not os.path.exists(archivo):
        return None

    with open(archivo, "r") as f:
        contenido = f.read()

    bloques = contenido.strip().split("\n\n")
    for bloque in bloques:
        lineas = bloque.strip().split("\n")
        if not lineas:
            continue
        clave = lineas[0].strip(":").strip()
        if clave == f"{rut}|{password}":
            tarjetas = [linea.strip("- ").strip() for linea in lineas[1:] if linea.strip()]
            return tarjetas

    return None

# --- Validadores de formularios ---

class ValidateAutenticacionForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_autenticacion_form"

    def validate_rut(self, slot_value, dispatcher, tracker, domain):
        logger.info(f"Validando RUT: {slot_value}")
        # Si el slot_value no parece un RUT, asumimos que aún no se ha ingresado uno válido
        if not slot_value or not re.match(r"^[0-9.\-kK]+$", slot_value.strip()):
            return {"rut": None}
        
        if validar_rut_chileno(slot_value):
            return {"rut": slot_value}
        
        dispatcher.utter_message(response="utter_invalid_rut")
        return {"rut": None}

    def validate_password(self, slot_value, dispatcher, tracker, domain):
        intent = tracker.latest_message.get("intent", {}).get("name")
        logger.info(f"Intent al ingresar contraseña: {intent}")

        # Evitar capturar si el intent es irrelevante
        if intent in ["saludo", "pregunta_uf", "pregunta_hora"]:
            return {"password": None}

        if not slot_value:
            return {"password": None}

        rut = tracker.get_slot("rut")
        logger.info(f"Validando password para RUT: {rut} con password: {slot_value}")

        if not rut:
            dispatcher.utter_message(response="utter_ask_rut")
            logger.info("No hay RUT cargado en el tracker")
            return {"password": None}

        if len(str(slot_value)) == 4 and str(slot_value).isdigit():
            tarjetas = autenticar_usuario(rut, slot_value)
            if tarjetas:
                logger.info(f"Tarjetas encontradas: {tarjetas}")
                return {"password": slot_value}

        dispatcher.utter_message(response="utter_invalid_password")
        return {"password": None}


class ValidateSeleccionarTarjetaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_seleccionar_tarjeta_form"

    def validate_tarjeta(self, slot_value, dispatcher, tracker, domain):
        tarjetas = tracker.get_slot("tarjetas_disponibles") or []
        if slot_value in tarjetas:
            return {"tarjeta": slot_value}
        dispatcher.utter_message(
            response="utter_invalid_card_selection"
        )
        return {"tarjeta": None}

# --- Acciones personalizadas ---

class ActionMostrarTarjetas(Action):
    def name(self):
        return "action_mostrar_tarjetas"

    def run(self, dispatcher, tracker, domain):
        rut = tracker.get_slot("rut")
        password = tracker.get_slot("password")
        tarjetas = autenticar_usuario(rut, password)

        if not tarjetas:
            dispatcher.utter_message(text="No se encontraron tarjetas asociadas.")
            return [FollowupAction(None)]

        mensaje = "¿Cuál de estas tarjetas deseas bloquear? Ingresa el número exacto:\n"
        mensaje += "\n".join(f"- {t}" for t in tarjetas)

        dispatcher.utter_message(text=mensaje)
        return [SlotSet("tarjetas_disponibles", tarjetas), FollowupAction("seleccionar_tarjeta_form")]

class ActionProcesarBloqueo(Action):
    def name(self):
        return "action_procesar_bloqueo"

    def run(self, dispatcher, tracker, domain):
        rut = tracker.get_slot("rut")
        tarjeta = tracker.get_slot("tarjeta")
        dispatcher.utter_message(text=f"Procesando el bloqueo de la tarjeta {tarjeta} para el RUT {rut} 🔒")
        return []

class ActionResetBloqueoSlots(Action):
    def name(self):
        return "action_reset_bloqueo_slots"

    def run(self, dispatcher, tracker, domain):
        return [
            SlotSet("rut", None),
            SlotSet("password", None),
            SlotSet("tarjeta", None),
            SlotSet("tarjetas_disponibles", None)
        ]
