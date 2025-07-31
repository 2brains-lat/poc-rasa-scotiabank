import logging
from typing import Any, Dict, Text
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet, ActiveLoop, Restarted

logger = logging.getLogger(__name__)

import re
import os

TARJETAS_PATH = "data/tarjetas.txt"

def cargar_tarjetas():
    tarjetas = {}
    if not os.path.exists(TARJETAS_PATH):
        return tarjetas

    with open(TARJETAS_PATH, "r", encoding="utf-8") as file:
        contenido = file.read()

    bloques = contenido.strip().split("\n\n")
    for bloque in bloques:
        lineas = bloque.strip().split("\n")
        if not lineas:
            continue
        cabecera = lineas[0].strip().replace(":", "")
        tarjetas[cabecera] = [linea.strip("- ").strip() for linea in lineas[1:]]
    logger.debug(f"Tarjetas cargadas: {tarjetas}")  
    return tarjetas

def generar_clave_normalizada(rut: str, password: str) -> str:
    """
    Normaliza un RUT chileno (quita puntos y guión, deja DV separado con guión)
    y genera la clave en formato "12345678-9|password".
    """
    rut_limpio = rut.replace(".", "").replace("-", "").upper()
    
    if not rut_limpio or len(rut_limpio) < 2:
        return ""  # No es un RUT válido

    cuerpo = rut_limpio[:-1]
    dv = rut_limpio[-1]
    rut_normalizado = f"{cuerpo}-{dv}"
    
    return f"{rut_normalizado}|{password}"

def validar_rut_chileno(rut: str) -> bool:
    logger.debug(f"Validando RUT chileno: {rut}")
    rut = rut.replace(".", "").replace("-", "").upper()

    if not re.match(r"^\d{7,8}[0-9K]$", rut):
        logger.debug(f"RUT {rut} no cumple con el formato esperado.")
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
            #validación adicional para verificar si el RUT y la contraseña coinciden con un usuario registrado
            rut = tracker.get_slot("rut")
            password = slot_value
            fail_count = tracker.get_slot("auth_fail_count") or 0
            if rut and password:
                tarjetas = cargar_tarjetas()
                clave = generar_clave_normalizada(rut, password)
                if clave in tarjetas:
                    logger.debug(f"Clave encontrada: {clave}")
                    # Mostrar tarjetas disponibles
                    tarjetas_disponibles = tarjetas[clave]
                    if tarjetas_disponibles:
                        logger.info(f"Tarjetas disponibles para el RUT {rut}: {tarjetas_disponibles}")
                        # tarjetas_formateadas = "\n".join(f"- {t}" for t in tarjetas_disponibles)
                        # dispatcher.utter_message(text="¿Cuál de estas tarjetas deseas bloquear? Ingresa el número exacto:")
                        # dispatcher.utter_message(text=tarjetas_formateadas)
                        botones_tarjetas = [{"title": t, "payload": t} for t in tarjetas_disponibles]
                        logger.info(f"Botones de tarjetas: {botones_tarjetas}")
                        dispatcher.utter_message(
                            text="¿Cuál de estas tarjetas deseas bloquear?",
                            buttons=botones_tarjetas
                        )
                        return {
                            "rut": rut,
                            "password": slot_value,
                            "tarjeta": None,
                            "requested_slot": "tarjeta",
                            "auth_fail_count": 0,
                            "opciones_tarjetas": tarjetas_disponibles
                        }
                    else:
                        logger.info("No se encontraron tarjetas asociadas.")
                        dispatcher.utter_message(text="No tienes tarjetas asociadas a tu cuenta.")
                        return {
                            "rut": None,
                            "password": None,
                            "tarjeta": None,
                            "requested_slot": None,
                            "auth_fail_count": 0,
                            "opciones_tarjetas": None
                        }
                else:
                    keys = tarjetas.keys()
                    logger.debug(f"Claves disponibles: {keys}") 
                    if(clave in tarjetas.keys()):
                        logger.debug(f"Clave encontrada pero sin tarjetas: {clave}")
                        dispatcher.utter_message(text="No tienes tarjetas asociadas a tu cuenta.")
                        return {
                            "rut": None,
                            "password": None,
                            "tarjeta": None,
                            "requested_slot": None,
                            "auth_fail_count": 0,
                            "opciones_tarjetas": None
                        }
                    
                    logger.debug(f"Clave no encontrada: {clave}")
                    dispatcher.utter_message(text="El RUT o la contraseña no coinciden con nuestros registros.")
                    fail_count += 1
                    if fail_count >= 3:
                        dispatcher.utter_message(text="Has fallado 3 veces. Por favor, contacta a un agente para desbloquear tu tarjeta.")
                        return {
                            "rut": None,
                            "password": None,
                            "requested_slot": None,
                            "auth_fail_count": fail_count
                        }
                    else:
                        dispatcher.utter_message(text=f"Intento fallido {fail_count}/3. Por favor, intenta nuevamente.")
                    return {
                            "rut": rut,
                            "password": None,
                            "auth_fail_count": fail_count
                        }
        else:
            dispatcher.utter_message(text="La contraseña debe tener exactamente 4 dígitos.")
            return [SlotSet("password", None)]
    
    def validate_tarjeta(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        opciones = tracker.get_slot("opciones_tarjetas")
        logger.info(f"Tarjeta seleccionada: {slot_value}")
        logger.info(f"Opciones de tarjetas disponibles: {opciones}")
        if not opciones:
            logger.info("No hay tarjetas disponibles para bloquear.")  
            dispatcher.utter_message(text="No se encontraron tarjetas asociadas.")
            return {"tarjeta": None}

        if slot_value in opciones:
            logger.info(f"Tarjeta seleccionada: {slot_value}")
            return {
                "tarjeta": slot_value,
                "requested_slot": None  # Esto indica que el formulario está completo
            }

        dispatcher.utter_message(response="utter_invalid_card_selection")
        dispatcher.utter_message(text=f"Opciones válidas: {', '.join(opciones)}")
        return {"tarjeta": None}