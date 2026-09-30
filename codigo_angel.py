# -*- coding: utf-8 -*-
import requests

# =========================================================
# CONFIGURACIÓN DE META CLOUD API - CÓDIGO ÁNGEL (PERMANENTE)
# =========================================================
PHONE_NUMBER_ID = "1306330835896586"
ACCESS_TOKEN = "EAAV2b4P5qUEBSsvI1UvWHuUvl1uXpT2P6wNqNbF2JjzsQZAy07g3F3zm9jh9vnkIKTi3qPy1iMSJFiE5gaDSZAdjkBlzCLQsycIAWOQhgszJdStHve9mZAMoe1ywG7ZC2iKl0KKzTSn1zMZBfpXRsHmpZAZAmf058T70C2eLVZBeiZCsFjD06E9xiSKugOYHXpwZDZD"

def formatear_numero_venezuela(numero):
    """Limpia el número y garantiza el formato internacional 58XXXXXXXXXX."""
    if not numero:
        return None
    num_limpio = "".join(filter(str.isdigit, str(numero)))
    if not num_limpio:
        return None
    if num_limpio.startswith("0"):
        num_limpio = "58" + num_limpio[1:]
    elif not num_limpio.startswith("58"):
        num_limpio = "58" + num_limpio
    return num_limpio

def enviar_alerta_whatsapp(numero_destino, mensaje):
    """
    Función oficial para disparar alertas de emergencia por WhatsApp.
    Usa el Token Permanente del Usuario del Sistema (codgoangelbot).
    """
    num_limpio = formatear_numero_venezuela(numero_destino)
    if not num_limpio or len(num_limpio) < 11:
        print(f"[CÓDIGO ÁNGEL] Número inválido omitido: {numero_destino}")
        return False, "Número de teléfono inválido"

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": num_limpio,
        "type": "text",
        "text": {
            "body": mensaje
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        res_json = response.json()
        if response.status_code == 200 and "messages" in res_json:
            print(f"[CÓDIGO ÁNGEL] Alerta enviada con éxito a {num_limpio}")
            return True, res_json
        else:
            print(f"[CÓDIGO ÁNGEL] Error Meta ({response.status_code}): {response.text}")
            return False, response.text
    except Exception as e:
        print(f"[CÓDIGO ÁNGEL] Error de conexión: {e}")
        return False, str(e)
