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
