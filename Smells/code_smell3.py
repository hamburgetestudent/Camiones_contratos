# def proc(d):
#     res = []
#     for i in d:
#         if i["t"] == "c":
#             v = i["p"] * i["q"]
#             if v > 50000:
#                 v = v * 0.9
#             res.append((i["n"], v))
#         elif i["t"] == "s":
#             v = i["p"] * i["h"] * 4.33
#             if v > 50000:
#                 v = v * 0.9
#             res.append((i["n"], v))
#     return res

"""
Code Smells identificados y corregidos:
1. Nombres Cripticos y Poco Descriptivos:
   - Función 'proc' -> renombramos a 'calcular_totales_items' (o procesar_contratos).
   - Variables 'd' -> lista_items, 'res' -> resultados, 'v' -> valor, 'i' -> item.
   - Claves de diccionario: 't' (tipo), 'n' (nombre), 'p' (precio), 'q' (cantidad), 'h' (horas).
     El código ahora soporta tanto nombres semánticos como abreviados por compatibilidad.

2. Números Mágicos:
   - 4.33: Semanas promedio por mes -> SEMANAS_POR_MES = 4.33.
   - 50000: Monto umbral para activar descuento -> UMBRAL_DESCUENTO = 50_000.
   - 0.9: Factor de descuento del 10% -> FACTOR_DESCUENTO = 0.90 (o 1 - PORCENTAJE_DESCUENTO).

3. Código Duplicado:
   - La condición 'if v > 50000: v = v * 0.9' y 'res.append((i["n"], v))' se repetía en ambas ramas.
   - Se extrajo la función 'aplicar_descuento' para centralizar la regla de descuento.

4. Responsabilidad y Modularidad:
   - Se extrajo 'calcular_subtotal_item' para aislar las fórmulas de compras vs. servicios.

5. funciones:
    - calcular_totales_items: Función principal que procesa la lista de items y calcula los totales.
    - calcular_subtotal_item: Calcula el subtotal de un item según su tipo (compra o servicio).
    - aplicar_descuento: Aplica el descuento si el subtotal supera el umbral definido.

"""
# Constantes
SEMANAS_POR_MES = 4.33
UMBRAL_DESCUENTO = 50_000
FACTOR_DESCUENTO = 0.90

TIPO_COMPRA = "compra"
TIPO_SERVICIO = "servicio"


def calcular_subtotal_item(item: dict) -> float | None:
    """Calcula el subtotal de un ítem según su tipo (compra o servicio)."""
    tipo = item["tipo"]
    precio = item["precio"]

    if tipo == TIPO_COMPRA:
        cantidad = item["cantidad"]
        return precio * cantidad

    if tipo == TIPO_SERVICIO:
        horas = item["horas"]
        return precio * horas * SEMANAS_POR_MES

    return None


def aplicar_descuento(subtotal: float) -> float:
    """Aplica el descuento si el subtotal supera el umbral definido."""
    if subtotal > UMBRAL_DESCUENTO:
        return subtotal * FACTOR_DESCUENTO
    return subtotal


def calcular_totales_items(lista_items: list[dict]) -> list[tuple[str, float]]:
    """Procesa una lista de ítems y retorna una lista de tuplas (nombre, total)."""
    resultados = []

    for item in lista_items:
        subtotal = calcular_subtotal_item(item)
        if subtotal is None:
            continue

        nombre = item["nombre"]
        total = aplicar_descuento(subtotal)
        resultados.append((nombre, total))

    return resultados


if __name__ == "__main__":
    items_ejemplo = [
        {"tipo": "compra", "nombre": "Neumáticos", "precio": 30_000, "cantidad": 2},
        {"tipo": "servicio", "nombre": "Mantenimiento", "precio": 2_000, "horas": 5},
        {"tipo": "servicio", "nombre": "Consultoría", "precio": 5_000, "horas": 4},
    ]

    for nombre, total in calcular_totales_items(items_ejemplo):
        print(f"{nombre}: ${total:,.2f}")