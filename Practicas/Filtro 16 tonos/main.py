# Filtro de 16 Tonos de Rosa para BMP

file = open('./images/volcan.bmp', 'rb')
fileo = open('./images/volcan_rosa.bmp', 'wb')

# 1. Copiar cabecera (metadata) sin cambios
metadata = file.read(54)
fileo.write(metadata)

# 2. Generar la "Paleta de 16 Rosas"
# Creamos una lista de 16 colores
# Formato BMP es BGR (Azul, Verde, Rojo)
# Un rosa típico tiene mucho Rojo, algo de Azul y poco Verde.
paleta_rosa = []
for i in range(16):
    # Proceso para crear los diferentes tonos
    rojo = 80 + (i * 11)   # De 80 a 245
    verde = 0 + (i * 15)   # De 0 a 225
    azul = 40 + (i * 12)   # De 40 a 220

    # Aseguramos que no se pase de 255
    if rojo > 255: rojo = 255
    if verde > 255: verde = 255
    if azul > 255: azul = 255

    # Guardamos en orden BGR (Blue, Green, Red) para BMP, ya que se voltea
    paleta_rosa.append([int(azul), int(verde), int(rojo)])

# 3. Procesar píxeles
file.seek(54, 0)
no_pix = 0

while True:
    pixel_data = file.read(3)
    if len(pixel_data) > 0:
        # Convertimos los bytes a enteros para poder sumar
        # Donde pixel_data[0] es Azul, [1] es Verde, [2] es Rojo
        b = pixel_data[0]
        g = pixel_data[1]
        r = pixel_data[2]

        # Paso A: Calcular el promedio de brillo (escala de grises)
        promedio = (r + g + b) // 3

        # Paso B: Determinar cual de los 16 tonos usar (Los condicionales)
        # Dividir el promedio (0-255) entre 16 nos da un índice de 0 a 15
        indice = promedio // 16

        # Protección por si el promedio sale 256 (muy raro pero posible)
        if indice > 15:
            indice = 15

        # Paso C: Escribir el color correspondiente de nuestra paleta
        color_nuevo = paleta_rosa[indice]
        fileo.write(bytes(color_nuevo))

        no_pix += 1
    else:
        break

print('Proceso terminado.')
print('Píxeles procesados: ' + str(no_pix))
file.close()
fileo.close()
