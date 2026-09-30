import sqlite3

# Función para crear la base de datos y la tabla de alertas
def inicializar_bd():
    conexion = sqlite3.connect('codigo_angel.db')
    cursor = conexion.cursor()
    
    # Creamos la tabla donde se guardarán los escaneos de emergencia
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id TEXT NOT NULL,
            fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            latitud REAL,
            longitud REAL,
            estado TEXT DEFAULT 'PENDIENTE'
        )
    ''')
    
    conexion.commit()
    conexion.close()
    print("¡Base de datos de Código Ángel creada con éxito!")

if __name__ == '__main__':
    inicializar_bd()