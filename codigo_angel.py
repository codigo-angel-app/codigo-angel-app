# -*- coding: utf-8 -*-
import requests

# =========================================================
# CONFIGURACIÓN DE META CLOUD API - CÓDIGO ÁNGEL
# =========================================================
PHONE_NUMBER_ID = "1306330835896586"
ACCESS_TOKEN = "EAAV2b4P5qUEBSsvI1UvWHuUvl1uXpT2P6wNqNbF2JjzsQZAy07g3F3zm9jh9vnkIKTi3qPy1iMSJFiE5gaDSZAdjkBlzCLQsycIAWOQhgszJdStHve9mZAMoe1ywG7ZC2iKl0KKzTSn1zMZBfpXRsHmpZAZAmf058T70C2eLVZBeiZCsFjD06E9xiSKugOYHXpwZDZD"

def formatear_numero_venezuela(numero):
    """
    Limpia el número y garantiza el formato internacional 58XXXXXXXXXX (12 dígitos).
    Maneja formatos como: 0424..., 424..., +58424..., 580424...
    """
    if not numero:
        return None
    
    # Conservar únicamente dígitos
    num_limpio = "".join(filter(str.isdigit, str(numero)))
    if not num_limpio:
        return None

    # Si empieza con 580424... eliminar el 0 intermedio
    if num_limpio.startswith("580") and len(num_limpio) == 13:
        num_limpio = "58" + num_limpio[3:]

    # Si empieza con 0 (ej: 04241234567 -> 11 dígitos)
    elif num_limpio.startswith("0") and len(num_limpio) == 11:
        num_limpio = "58" + num_limpio[1:]

    # Si no tiene el 58 ni el 0 (ej: 4241234567 -> 10 dígitos)
    elif not num_limpio.startswith("58") and len(num_limpio) == 10:
        num_limpio = "58" + num_limpio

    # Validar que el resultado final tenga exactamente 12 dígitos (58 + 10 dígitos)
    if len(num_limpio) == 12 and num_limpio.startswith("58"):
        return num_limpio

    print(f"[CÓDIGO ÁNGEL] Advertencia: Formato de número desconocido o longitud incorrecta: {num_limpio}")
    return None


def enviar_alerta_whatsapp(numero_destino, nombre_paciente, url_ubicacion):
    """
    Dispara la alerta de emergencia por WhatsApp usando la Plantilla (Template)
    'alerta_codigo_angel' aprobada en Meta Cloud API.
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
        "type": "template",
        "template": {
            "name": "alerta_codigo_angel",
            "language": {
                "code": "es"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(nombre_paciente)},
                        {"type": "text", "text": str(url_ubicacion)}
                    ]
                }
            ]
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        res_json = response.json()
        
        # Imprime la respuesta exacta de Meta en el Log para monitoreo
        print(f"[CÓDIGO ÁNGEL] Respuesta Status HTTP: {response.status_code}")
        print(f"[CÓDIGO ÁNGEL] Respuesta JSON Meta: {res_json}")

        if response.status_code == 200 and "messages" in res_json:
            print(f"[CÓDIGO ÁNGEL] Alerta aceptada por Meta para {num_limpio}")
            return True, res_json
        else:
            print(f"[CÓDIGO ÁNGEL] Error Meta ({response.status_code}): {response.text}")
            return False, response.text
    except Exception as e:
        print(f"[CÓDIGO ÁNGEL] Error de conexión: {e}")
        return False, str(e)
