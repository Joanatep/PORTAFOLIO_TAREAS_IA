import random
import matplotlib.pyplot as plt

TASA_APRENDIZAJE = 0.5
FACTOR_DESCUENTO = 1.0
PROBABILIDAD_EXPLORACION = 0.1
CANTIDAD_EPISODIOS = 500
PASOS_MAXIMOS = 200
SEMILLA_ALEATORIA = 42

random.seed(SEMILLA_ALEATORIA)

FILAS = 4
COLUMNAS = 12
CASILLA_INICIAL = (3, 0)
CASILLA_META = (3, 11)
LISTA_ACCIONES = ['N', 'E', 'S', 'W']

MAPA_MOVIMIENTOS = {
    'N': (-1, 0),
    'E': (0, 1),
    'S': (1, 0),
    'W': (0, -1)
}

def verificar_acantilado(posicion):
    r, c = posicion
    return r == 3 and 1 <= c <= 10

def ejecutar_accion(estado_actual, accion):
    fila, columna = estado_actual
    dfila, dcolumna = MAPA_MOVIMIENTOS[accion]
    nueva_fila, nueva_columna = fila + dfila, columna + dcolumna

    if not (0 <= nueva_fila < FILAS and 0 <= nueva_columna < COLUMNAS):
        nueva_fila, nueva_columna = fila, columna

    proximo_estado = (nueva_fila, nueva_columna)

    if proximo_estado == CASILLA_META:
        return proximo_estado, -1, True
    elif verificar_acantilado(proximo_estado):
        return CASILLA_INICIAL, -100, False
    else:
        return proximo_estado, -1, False

tabla_q = {
    (f, c): {acc: 0.0 for acc in LISTA_ACCIONES}
    for f in range(FILAS)
    for c in range(COLUMNAS)
}

def seleccionar_accion(estado, epsilon):
    if random.random() < epsilon:
        return random.choice(LISTA_ACCIONES)
    
    maximo_q = max(tabla_q[estado].values())
    for acc in LISTA_ACCIONES:
        if tabla_q[estado][acc] == maximo_q:
            return acc

historial_recompensas = []

for episodio in range(CANTIDAD_EPISODIOS):
    estado_actual = CASILLA_INICIAL
    recompensa_episodio = 0

    for _ in range(PASOS_MAXIMOS):
        accion_actual = seleccionar_accion(estado_actual, PROBABILIDAD_EXPLORACION)
        siguiente_estado, recompensa, es_terminal = ejecutar_accion(estado_actual, accion_actual)

        if es_terminal:
            q_siguiente_max = 0.0
        else:
            q_siguiente_max = max(tabla_q[siguiente_estado].values())

        blanco_td = recompensa + FACTOR_DESCUENTO * q_siguiente_max
        valor_actual = tabla_q[estado_actual][accion_actual]
        tabla_q[estado_actual][accion_actual] = valor_actual + TASA_APRENDIZAJE * (blanco_td - valor_actual)

        recompensa_episodio += recompensa
        estado_actual = siguiente_estado

        if es_terminal:
            break

    historial_recompensas.append(recompensa_episodio)

estado_eval = CASILLA_INICIAL
camino_greedy = [CASILLA_INICIAL]
acciones_greedy = []
retorno_greedy = 0

for _ in range(PASOS_MAXIMOS):
    accion_eval = seleccionar_accion(estado_eval, 0.0)
    siguiente_estado, recompensa, es_terminal = ejecutar_accion(estado_eval, accion_eval)

    acciones_greedy.append(accion_eval)
    camino_greedy.append(siguiente_estado)
    retorno_greedy += recompensa
    estado_eval = siguiente_estado

    if es_terminal:
        break

print(f"Retorno obtenido por la política greedy: {retorno_greedy}")
print(f"Total de pasos efectuados: {len(acciones_greedy)}")

print("\nVisualización de la política óptima:")
simbolos_flechas = {'N': '↑', 'E': '→', 'S': '↓', 'W': '←'}
for f in range(FILAS):
    cadena_fila = ""
    for c in range(COLUMNAS):
        pos = (f, c)
        if pos == CASILLA_META:
            cadena_fila += " G "
        elif verificar_acantilado(pos):
            cadena_fila += " C "
        else:
            mejor_accion = seleccionar_accion(pos, 0.0)
            cadena_fila += f" {simbolos_flechas[mejor_accion]} "
    print(cadena_fila)

def calcular_media_movil(datos, tam_ventana=10):
    return [
        sum(datos[indice : indice + tam_ventana]) / tam_ventana
        for indice in range(len(datos) - tam_ventana + 1)
    ]

recompensas_suavizadas = calcular_media_movil(historial_recompensas, 10)
plt.plot(historial_recompensas, alpha=0.3, color='orange', label='Recompensa por episodio')
plt.plot(range(9, len(historial_recompensas)), recompensas_suavizadas, color='green', label='Media móvil (10 ep)')
plt.ylim([-300, 0])
plt.title("Q-learning aplicado a Cliff Walking (Modificado)")
plt.xlabel("Episodios")
plt.ylabel("Retorno acumulado")
plt.legend()
plt.grid(True)
plt.savefig("Q-learning/ejercicios/solucion1/grafica.png")