import struct
import math

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

# Función para incrustar mensaje usando LSB
def embed_lsb(src_path, dst_path, mensaje):
    header, pixels, width, height, row_size = leer_bmp(src_path)
    
    msg_bytes = mensaje.encode('utf-8')
    msg_len = len(msg_bytes)
    
    datos = struct.pack('<I', msg_len) + msg_bytes
    
    bits = []
    for byte in datos:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
            
    if len(bits) > len(pixels):
        raise ValueError('Mensaje demasiado largo para esta imagen')
        
    pixels_mod = bytearray(pixels)
    for idx, bit in enumerate(bits):
        # 0xFE en binario es 11111110. 
        # El operador '&' limpia el último bit, y '|' inserta nuestro bit secreto.
        pixels_mod[idx] = (pixels_mod[idx] & 0xFE) | bit 
        
    guardar_bmp(dst_path, header, pixels_mod)
    print(f'[OK] Mensaje de {msg_len} bytes incrustado exitosamente en {dst_path}')

# Función para extraer mensaje usando LSB
def extract_lsb(stego_path):
    _, pixels, _, _, _ = leer_bmp(stego_path)
    
    # 1. Leer los primeros 32 bits (4 bytes)
    len_bits = [pixels[i] & 1 for i in range(32)]
    
    # Reconstruimos los 4 bytes de la longitud primero
    len_bytes = bytearray()
    for i in range(0, 32, 8):
        byte = 0
        for bit in len_bits[i:i+8]:
            byte = (byte << 1) | bit
        len_bytes.append(byte)
        
    # Desempaquetamos respetando el Little-Endian ('<I') que se usó al guardar
    msg_len = struct.unpack('<I', len_bytes)[0]
        
    # 2. Leer los siguientes msg_len * 8 bits para obtener el mensaje
    total_bits = 32 + (msg_len * 8)
    msg_bits = [pixels[i] & 1 for i in range(32, total_bits)]
    
    # 3. Reconstruir los bytes a partir de los bits extraídos
    msg_bytes = bytearray()
    for i in range(0, len(msg_bits), 8):
        byte = 0
        for bit in msg_bits[i:i+8]:
            byte = (byte << 1) | bit
        msg_bytes.append(byte)
        
    # 4. Decodificar los bytes a texto
    return msg_bytes.decode('utf-8')

# Función para calcular PSNR entre dos imágenes BMP
def calcular_psnr(original_path, stego_path):
    # Leer ambas imágenes
    _, pix_orig, w, h, _ = leer_bmp(original_path)
    _, pix_steg, _, _, _ = leer_bmp(stego_path)
    
    # Calcular el Error Cuadrático Medio (MSE)
    # Comparamos byte a byte los pixeles de la imagen original vs la modificada
    mse = sum((a - b) ** 2 for a, b in zip(pix_orig, pix_steg)) / (w * h * 3)
    
    if mse == 0:
        print("Las imágenes son exactamente iguales.")
        return float('inf')
        
    # Calcular el PSNR en decibelios (dB)
    psnr = 10 * math.log10((255 ** 2) / mse)
    
    print(f'MSE: {mse:.6f}')
    print(f'PSNR: {psnr:.2f} dB (>40 dB: cambio imperceptible)')
    return psnr

# Invocación de funciones
archivo_original = 'imagen512.bmp'
archivo_stego = 'stego512_max.bmp'

# Mensajes
mensaje_500 = "A" * 500
mensaje_5000 = "B" * 5000
mensaje_max = "C" * 98300

mensaje_secreto = mensaje_max

print("--- Iniciando proceso de esteganografía ---")
# 1. Ocultar el mensaje
embed_lsb(archivo_original, archivo_stego, mensaje_secreto)

# 2. Extraer el mensaje de la nueva imagen
recuperado = extract_lsb(archivo_stego)
# print(f'Mensaje recuperado: "{recuperado}"')

# 3. Verificación automática
assert recuperado == mensaje_secreto, '¡Error en la extracción!'
print('Prueba exitosa. El mensaje se extrajo correctamente.')

# 4. Calcular PSNR para evaluar la degradación de la imagen
print("\n--- Analizando degradación de la imagen ---")
calcular_psnr(archivo_original, archivo_stego)
