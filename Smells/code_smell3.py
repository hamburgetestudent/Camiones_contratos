def proc(d):
    res = []
    for i in d:
        if i["t"] == "c":
            v = i["p"] * i["q"]
            if v > 50000:
                v = v * 0.9
            res.append((i["n"], v))
        elif i["t"] == "s":
            v = i["p"] * i["h"] * 4.33
            if v > 50000:
                v = v * 0.9
            res.append((i["n"], v))
    return res

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
"""
