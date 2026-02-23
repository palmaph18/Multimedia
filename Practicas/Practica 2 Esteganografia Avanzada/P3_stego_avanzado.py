import hashlib
import struct
import random

# Funcion para leer archivo BMP
def leer_bmp(filepath):
    """Retorna (header_bytes, pixels, width, height, row_size)"""
    with open(filepath, 'rb') as f:
        data = f.read()

        offset = struct.unpack_from('<I', data, 10)[0]
        width = struct.unpack_from('<i', data, 18)[0]
        height = struct.unpack_from('<i', data, 22)[0]
        
        row_size = ((width * 3 + 3) & ~3)
        
        header = bytearray(data[:offset])
        pixels = bytearray(data[offset:])
        
        return header, pixels, width, height, row_size

# Funcion para guardar archivo BMP
def guardar_bmp(filepath, header, pixels):
    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(pixels)

# Funciones para cifrado XOR con clave derivada de contraseña
def derivar_clave(password: str, longitud: int) -> bytes:
    """Genera una clave de longitud arbitraria usando SHA-256 en modo contador"""
    clave = b''
    contador = 0
    while len(clave) < longitud:
        # Concatenamos la contraseña y el contador, y sacamos el hash SHA-256
        bloque = hashlib.sha256(password.encode() + struct.pack('<I', contador)).digest()
        clave += bloque
        contador += 1
    return clave[:longitud]

# Funcion para cifrar
def cifrar_xor(mensaje: bytes, password: str) -> bytes:
    clave = derivar_clave(password, len(mensaje))
    # Aplicamos la operación XOR (^) byte por byte entre el mensaje y la clave
    return bytes([m ^ k for m, k in zip(mensaje, clave)])

# Funcion para descifrar
def descifrar_xor(cifrado: bytes, password: str) -> bytes:
    # El XOR es simétrico, aplicar la misma operación descifra el mensaje
    return cifrar_xor(cifrado, password)

# Funcion semilla_de_password
def semilla_de_password(password: str) -> int:
    """Convierte la contraseña en un entero para usar como semilla del generador aleatorio"""
    hash_bytes = hashlib.sha256(password.encode()).digest()
    # Tomamos los primeros 8 bytes del hash para crear un número entero grande
    return int.from_bytes(hash_bytes[:8], 'big')

# Funcion para seleccionar posiciones de bits en la imagen
def seleccionar_posiciones(total_bytes_imagen: int, n_bits: int, seed: int) -> list:
    """Selecciona n_bits índices únicos de forma reproducible e independiente de la longitud"""
    rng = random.Random(seed)
    
    # En lugar de sample y sorted, creamos una lista con todos los píxeles de la imagen,
    # la desordenamos aleatoriamente usando tu contraseña, y tomamos solo los que necesitamos.
    # Así garantizamos que los primeros 32 siempre sean exactamente los mismos.
    ruta_completa = list(range(total_bytes_imagen))
    rng.shuffle(ruta_completa)
    
    return ruta_completa[:n_bits]

# Función de incrustación segura
def embed_secure(src_path, dst_path, mensaje, password):
    header, pixels, width, height, row_size = leer_bmp(src_path)
    
    msg_bytes = mensaje.encode('utf-8')
    # 1. Cifrar el mensaje con la contraseña
    msg_cifrado = cifrar_xor(msg_bytes, password)
    
    # 2. Construir datos: 4 bytes de longitud (Little-Endian) + mensaje cifrado
    datos = struct.pack('<I', len(msg_bytes)) + msg_cifrado
    
    # 3. Convertir a flujo de bits
    bits = []
    for byte in datos:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
            
    n_bits = len(bits)
    if n_bits > len(pixels):
        raise ValueError('Mensaje demasiado grande para esta imagen')
        
    # 4. Seleccionar posiciones aleatorias basadas en la contraseña
    seed = semilla_de_password(password)
    posiciones = seleccionar_posiciones(len(pixels), n_bits, seed)
    
    # 5. Incrustar bits cifrados en las posiciones específicas
    pixels_mod = bytearray(pixels)
    for pos, bit in zip(posiciones, bits):
        pixels_mod[pos] = (pixels_mod[pos] & 0xFE) | bit
        
    guardar_bmp(dst_path, header, pixels_mod)
    print(f'[OK] {len(msg_bytes)} bytes cifrados e incrustados en {dst_path}')


# Función de extracción segura
def extract_secure(stego_path, password):
    _, pixels, _, _, _ = leer_bmp(stego_path)
    
    seed = semilla_de_password(password)
    
    # 1. Leer las posiciones para los primeros 32 bits (longitud)
    pos_longitud = seleccionar_posiciones(len(pixels), 32, seed)
    len_bits = [pixels[p] & 1 for p in pos_longitud]
    
    len_bytes = bytearray()
    for i in range(0, 32, 8):
        byte = 0
        for bit in len_bits[i:i+8]:
            byte = (byte << 1) | bit
        len_bytes.append(byte)
        
    msg_len = struct.unpack('<I', len_bytes)[0]
    
    # 2. Leer las posiciones para el resto del mensaje
    total_bits = 32 + (msg_len * 8)
    
    # Regenerar todas las posiciones (con la misma semilla obtenemos la misma secuencia)
    todas_pos = seleccionar_posiciones(len(pixels), total_bits, seed)
    
    # Tomar los bits que corresponden al mensaje cifrado (descartando los primeros 32 de longitud)
    msg_bits = [pixels[p] & 1 for p in todas_pos[32:]]
    
    # 3. Reconstruir los bytes cifrados
    cifrado = bytearray()
    for i in range(0, len(msg_bits), 8):
        byte = 0
        for bit in msg_bits[i:i+8]:
            byte = (byte << 1) | bit
        cifrado.append(byte)
        
    # 4. Descifrar con XOR y decodificar a texto
    return descifrar_xor(bytes(cifrado), password).decode('utf-8')

# Función para análisis de chi-cuadrado en LSBs
def chi_cuadrado_lsb(filepath):
    # Solo necesitamos extraer los píxeles
    _, pixels, _, _, _ = leer_bmp(filepath)
    
    # Contar cuántos LSBs son 0
    ceros = sum(1 for b in pixels if (b & 1) == 0)
    # El resto lógicamente serán 1
    unos = len(pixels) - ceros
    
    # Si la distribución fuera perfectamente aleatoria (como el ruido de un cifrado), 
    # esperaríamos exactamente la mitad de 0s y la mitad de 1s.
    esperado = len(pixels) / 2
    
    # Fórmula del estadístico Chi-cuadrado
    chi2 = ((ceros - esperado) ** 2 + (unos - esperado) ** 2) / esperado
    
    print(f'Archivo: {filepath}')
    print(f'LSBs=0: {ceros} | LSBs=1: {unos} | x²: {chi2:.4f}')
    
    # Un valor muy alto indica una imagen natural. Un valor cercano a 0 
    # indica que la imagen probablemente tiene datos ocultos.
    if chi2 < 100:
         print('--> ¡ALERTA! Distribución sospechosamente uniforme. Posible esteganografía.')
    else:
         print('--> Distribución natural. Sin sospecha evidente.')
    print('-' * 50)
    
    return chi2

# Main

if __name__ == '__main__':
    CLAVE = 'Telematica@2025'
    MENSAJE = 'Datos confidenciales de la red 10.0.1.0/24'
    
    # Asegúrate de usar una imagen que exista en tu carpeta
    archivo_original = 'imagen512.bmp' 
    archivo_stego_seguro = 'stego_seguro.bmp'

    print("--- Incrustando con seguridad ---")
    embed_secure(archivo_original, archivo_stego_seguro, MENSAJE, CLAVE)

    print("\n--- Extrayendo con clave correcta ---")
    resultado = extract_secure(archivo_stego_seguro, CLAVE)
    print(f'Clave correcta: "{resultado}"')
    
    # Verificación automática
    assert resultado == MENSAJE, "Error en la extracción con clave correcta."

    print("\n--- Extrayendo con clave incorrecta ---")
    try:
        basura = extract_secure(archivo_stego_seguro, 'claveWrong')
        print(f'Clave incorrecta: "{basura[:30]}..." (texto ilegible esperado)')
    except UnicodeDecodeError:
        # Frecuentemente, al descifrar con la clave incorrecta, los bytes resultantes 
        # no forman caracteres UTF-8 válidos, lo cual también es un éxito de seguridad.
        print("Clave incorrecta -> Error: Imposible decodificar. (El cifrado funcionó)")
    except Exception as e:
        print(f'Clave incorrecta -> Error inesperado: {e}')
"""
if __name__ == '__main__':
    img_original = 'imagen512.bmp'
    stego_secuencial = 'stego512_5000.bmp' # La que se genero en P2_lsb_stego.py
    stego_aleatorio = 'stego_seguro.bmp'    
    
    print("\n=== INICIANDO ESTEGOANÁLISIS CHI-CUADRADO ===")
    
    try:
        print('=== Imagen original ===')
        chi_cuadrado_lsb(img_original)
        
        print('=== Stego LSB secuencial (Práctica 1) ===')
        chi_cuadrado_lsb(stego_secuencial)
        
        print('=== Stego LSB aleatorio (Práctica 2) ===')
        chi_cuadrado_lsb(stego_aleatorio)
    except FileNotFoundError as e:
        print(f"Error: No se encontró el archivo para analizar. {e}")
"""
