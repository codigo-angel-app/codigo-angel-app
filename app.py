# -*- coding: utf-8 -*-
import os
import time
import re
import sqlite3
from flask import Flask, render_template_string, request, jsonify, redirect, url_for

# Importar la función de plantilla desde codigo_angel.py
try:
    from codigo_angel import enviar_alerta_whatsapp
except ImportError:
    def enviar_alerta_whatsapp(numero, nombre_usuario, codigo_qr):
        print(f"[ERROR CÓDIGO ÁNGEL] No se encontró codigo_angel.py. No se pudo enviar a {numero}")
        return False, "Falta archivo codigo_angel.py"

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "codigo_angel.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            codigo_qr TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            tipo_sangre TEXT NOT NULL,
            alergias TEXT,
            condiciones TEXT,
            contacto_emergencia TEXT NOT NULL,
            contacto_emergencia_2 TEXT,
            es_servidor_publico TEXT DEFAULT 'NO',
            rango TEXT,
            destacamento TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def limpiar_numero(num):
    if not num:
        return None
    solo_num = re.sub(r'\D', '', str(num))
    if len(solo_num) < 10:
        return None
    if solo_num.startswith('0'):
        solo_num = '58' + solo_num[1:]
    elif not solo_num.startswith('58'):
        solo_num = '58' + solo_num
    return solo_num

def despachar_alertas_plantilla(contactos_list, nombre_usuario, codigo_qr):
    """Envía la plantilla 'alerta_codigo_angel' aprobada por Meta a la lista de contactos."""
    numeros_unicos = []
    for num in contactos_list:
        numero_limpio = limpiar_numero(num)
        if numero_limpio and numero_limpio not in numeros_unicos:
            numeros_unicos.append(numero_limpio)

    for numero in numeros_unicos:
        try:
            exito, resp = enviar_alerta_whatsapp(numero, nombre_usuario, codigo_qr)
            if not exito:
                print(f"[CÓDIGO ÁNGEL] No se pudo entregar plantilla a {numero}: {resp}")
            else:
                print(f"[CÓDIGO ÁNGEL] Plantilla entregada con éxito a {numero}")
        except Exception as e:
            print(f"[CÓDIGO ÁNGEL] Excepción al despachar a {numero}: {e}")
        time.sleep(1)

HTML_FORMULARIO = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Código Ángel - Registro</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #eef2f5; padding: 20px; }
        .form-box { max-width: 450px; margin: 0 auto; background: #fff; padding: 25px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h2 { color: #0056b3; text-align: center; margin-top: 0; }
        .alerta-error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 12px; border-radius: 6px; margin-bottom: 15px; text-align: center; font-weight: bold; }
        label { font-weight: bold; display: block; margin-top: 10px; font-size: 14px; }
        input, select { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        .seccion-servidor { background: #f0f7ff; border: 1px dashed #0056b3; padding: 12px; border-radius: 6px; margin-top: 15px; display: none; }
        button { width: 100%; background: #0056b3; color: white; border: none; padding: 12px; margin-top: 20px; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 16px; }
        button:hover { background: #003d80; }
    </style>
</head>
<body>
    <div class="form-box">
        <h2>REGISTRO CÓDIGO ÁNGEL</h2>

        {% if error %}
        <div class="alerta-error">
            ⚠️ {{ error }}
        </div>
        {% endif %}

        <form action="/guardar" method="POST">
            <label>Código asignado (ej. ANGEL-001):</label>
            <input type="text" name="codigo_qr" required placeholder="ANGEL-XXX" value="{{ codigo_prellenado }}">

            <label>Nombre Completo:</label>
            <input type="text" name="nombre" required placeholder="Nombre y Apellido">

            <label>Tipo de Sangre:</label>
            <select name="tipo_sangre" required>
                <option value="">Seleccione...</option>
                <option value="O+">O+</option>
                <option value="O-">O-</option>
                <option value="A+">A+</option>
                <option value="A-">A-</option>
                <option value="B+">B+</option>
                <option value="B-">B-</option>
                <option value="AB+">AB+</option>
                <option value="AB-">AB-</option>
            </select>

            <label>Alergias:</label>
            <input type="text" name="alergias" placeholder="Ninguna / Medicamentos">

            <label>Condiciones Médicas:</label>
            <input type="text" name="condiciones" placeholder="Diabetes, Hipertensión, etc.">

            <label>Teléfono Principal de Emergencia (WhatsApp):</label>
            <input type="text" name="contacto_emergencia" required placeholder="Ej: 04249501774">

            <label>Teléfono Secundario de Emergencia (Opcional):</label>
            <input type="text" name="contacto_emergencia_2" placeholder="Ej: 04249112904">

            <label>¿Es Servidor Público? (Policía, Bomberos, FANB, Protección Civil):</label>
            <select name="es_servidor_publico" id="es_servidor_publico" onchange="toggleServidorPublico()">
                <option value="NO">NO</option>
                <option value="SI">SÍ</option>
            </select>

            <div class="seccion-servidor" id="seccion_servidor">
                <label>Rango / Jerarquía:</label>
                <input type="text" name="rango" placeholder="Ej: Sargento Primero, Oficial, Inspector">

                <label>Destacamento / Unidad / Base:</label>
                <input type="text" name="destacamento" placeholder="Ej: D-625, Estación N° 1">
            </div>

            <button type="submit">GUARDAR Y ACTIVAR CÓDIGO</button>
        </form>
    </div>

    <script>
    function toggleServidorPublico() {
        let val = document.getElementById('es_servidor_publico').value;
        let sec = document.getElementById('seccion_servidor');
        sec.style.display = (val === 'SI') ? 'block' : 'none';
    }
    </script>
</body>
</html>
"""

HTML_EXITO = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Código Ángel - Activado</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #eef2f5; padding: 20px; }
        .box { max-width: 400px; margin: 40px auto; background: #fff; padding: 30px; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-top: 6px solid #28a745; }
        h2 { color: #28a745; margin-top: 0; }
        p { font-size: 16px; color: #333; margin: 15px 0; }
        .codigo { font-size: 22px; font-weight: bold; color: #0056b3; background: #e9ecef; padding: 10px; border-radius: 5px; display: inline-block; margin: 10px 0; }
        .btn { display: block; width: 100%; background: #0056b3; color: white; padding: 12px 0; border-radius: 5px; text-decoration: none; font-weight: bold; margin-top: 20px; box-sizing: border-box; }
        .btn-ver { background: #6c757d; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>¡CÓDIGO ACTIVADO CON ÉXITO!</h2>
        <p>Se guardaron los datos para el código:</p>
        <div class="codigo">{{ codigo }}</div>
        <p><strong>Titular:</strong> {{ nombre }}</p>

        <a href="/" class="btn">REGISTRAR OTRO CÓDIGO ÁNGEL</a>
        <a href="/escaneo/{{ codigo }}" target="_blank" class="btn btn-ver">Probar vista previa de la ficha</a>
    </div>
</body>
</html>
"""

HTML_FICHA = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Código Ángel - Emergencia</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; }
        .card { max-width: 400px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-top: 6px solid #d9534f; }
        h2 { text-align: center; color: #d9534f; margin-top: 0; }
        .campo { margin-bottom: 15px; }
        .etiqueta { font-weight: bold; color: #555; display: block; font-size: 14px; }
        .valor { font-size: 18px; color: #222; margin-top: 2px; }
        .alerta-sangre { background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 22px; }
        .placa-servidor { background: #0056b3; color: white; padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; margin-bottom: 15px; }
        .btn-alerta { display: block; width: 100%; text-align: center; background: #25d366; color: white; padding: 14px 0; border-radius: 6px; text-decoration: none; font-weight: bold; margin-top: 15px; border: none; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h2>FICHA DE EMERGENCIA</h2>

        {% if usuario[7] == 'SI' %}
        <div class="placa-servidor">
            🛡️ SERVIDOR PÚBLICO<br>
            <small>{{ usuario[8] }} | {{ usuario[9] }}</small>
        </div>
        {% endif %}

        <div class="campo">
            <span class="etiqueta">TIPO DE SANGRE:</span>
            <div class="alerta-sangre">{{ usuario[2] }}</div>
        </div>
        <div class="campo">
            <span class="etiqueta">Nombre del Titular:</span>
            <div class="valor">{{ usuario[1] }}</div>
        </div>
        <div class="campo">
            <span class="etiqueta">Alergias:</span>
            <div class="valor">{{ usuario[3] or 'Ninguna registrada' }}</div>
        </div>
        <div class="campo">
            <span class="etiqueta">Condiciones Médicas:</span>
            <div class="valor">{{ usuario[4] or 'Ninguna registrada' }}</div>
        </div>

        <button onclick="notificarConUbicacion()" class="btn-alerta">
            ENVIAR UBICACIÓN GPS
        </button>
    </div>

    <script>
    function notificarConUbicacion() {
        let btn = document.querySelector('.btn-alerta');
        btn.innerText = "OBTENIENDO UBICACIÓN GPS...";
        btn.disabled = true;

        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    let lat = position.coords.latitude;
                    let lon = position.coords.longitude;

                    fetch('/enviar_gps', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            codigo_qr: "{{ usuario[0] }}",
                            lat: lat,
                            lon: lon
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if(data.status === 'ok') {
                            btn.innerText = "¡UBICACIÓN ENVIADA POR META!";
                            btn.style.background = "#28a745";
                        } else {
                            btn.innerText = "ERROR AL ENVIAR UBICACIÓN";
                            btn.style.background = "#dc3545";
                        }
                    })
                    .catch(error => {
                        btn.innerText = "ERROR DE CONEXIÓN";
                        btn.style.background = "#dc3545";
                    });
                },
                function(error) {
                    alert("Por favor, permite el permiso de ubicación en tu navegador para enviar el GPS.");
                    btn.innerText = "ENVIAR UBICACIÓN GPS";
                    btn.disabled = false;
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
        } else {
            alert("Su navegador no soporta geolocalización.");
            btn.innerText = "ENVIAR UBICACIÓN GPS";
            btn.disabled = false;
        }
    }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def formulario_registro():
    codigo_prellenado = request.args.get('codigo', '').strip().upper()

    if codigo_prellenado:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT codigo_qr FROM usuarios WHERE codigo_qr = ?', (codigo_prellenado,))
        registrado = cursor.fetchone()
        conn.close()
        if registrado:
            return redirect(url_for('ver_ficha', codigo_qr=codigo_prellenado))

    return render_template_string(HTML_FORMULARIO, codigo_prellenado=codigo_prellenado, error=None)

@app.route('/guardar', methods=['POST'])
def guardar_registro():
    codigo_qr = request.form['codigo_qr'].strip().upper()
    nombre = request.form['nombre'].strip()
    tipo_sangre = request.form['tipo_sangre']
    alergias = request.form['alergias'].strip()
    condiciones = request.form['condiciones'].strip()
    contacto_emergencia = request.form['contacto_emergencia'].strip()
    contacto_emergencia_2 = request.form.get('contacto_emergencia_2', '').strip()
    es_servidor_publico = request.form.get('es_servidor_publico', 'NO')
    rango = request.form.get('rango', '').strip()
    destacamento = request.form.get('destacamento', '').strip()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT nombre FROM usuarios WHERE codigo_qr = ?', (codigo_qr,))
    existente = cursor.fetchone()

    if existente:
        conn.close()
        msg_error = f"El código '{codigo_qr}' ya se encuentra registrado a nombre de: {existente[0]}. No es posible duplicarlo."
        return render_template_string(HTML_FORMULARIO, codigo_prellenado=codigo_qr, error=msg_error)

    cursor.execute('''
        INSERT INTO usuarios 
        (codigo_qr, nombre, tipo_sangre, alergias, condiciones, contacto_emergencia, contacto_emergencia_2, es_servidor_publico, rango, destacamento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (codigo_qr, nombre, tipo_sangre, alergias, condiciones, contacto_emergencia, contacto_emergencia_2, es_servidor_publico, rango, destacamento))
    conn.commit()
    conn.close()

    # Se despacha la plantilla de activación
    despachar_alertas_plantilla([contacto_emergencia, contacto_emergencia_2], nombre, codigo_qr)

    return render_template_string(HTML_EXITO, codigo=codigo_qr, nombre=nombre)

@app.route('/escaneo/<codigo_qr>')
def ver_ficha(codigo_qr):
    codigo_clean = codigo_qr.strip().upper()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE codigo_qr = ?', (codigo_clean,))
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        nombre = usuario[1]
        c1 = usuario[5]
        c2 = usuario[6] if len(usuario) > 6 else ""

        # Enviar notificación vía Plantilla Aprobada de Meta
        despachar_alertas_plantilla([c1, c2], nombre, codigo_clean)

        return render_template_string(HTML_FICHA, usuario=usuario)
    else:
        return redirect(url_for('formulario_registro', codigo=codigo_clean))

@app.route('/enviar_gps', methods=['POST'])
def enviar_gps():
    data = request.get_json()
    codigo_qr = data.get('codigo_qr')
    lat = data.get('lat')
    lon = data.get('lon')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT nombre, contacto_emergencia, contacto_emergencia_2 FROM usuarios WHERE codigo_qr = ?', (codigo_qr.upper(),))
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        nombre = usuario[0]
        c1 = usuario[1]
        c2 = usuario[2] if len(usuario) > 2 else ""

        # Despachar notificación de ubicación GPS
        despachar_alertas_plantilla([c1, c2], nombre, codigo_qr)
        return jsonify({"status": "ok", "message": "Ubicación enviada vía Meta API"})

    return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)