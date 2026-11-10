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
el codigo tiene varias funciones, pero no estan declaradas, por lo que no se sabe que hace la funcion proc.
por ejemplo, se podria declarar como calcular_valor_total, y las variables internas deberian tener nombres mas descriptivos.
tambien se deberia declarar una constante para el valor de 50000 o 4.33 que , y no usar numeros magicos en su lugar declararlos

4.33 son las semanas promedio de un mes, y 50000 es el valor a partir del cual se aplica un descuento del 10%

codigo duplicado, se repite la logica de calcular el valor total y aplicar el descuento, se deberia declarar una funcion para esto y llamarla desde proc.

nombres cripticos como "t", "p", "q", "h" y "n" deberian ser reemplazados por nombres mas descriptivos, como 
"tipo", "precio", "cantidad", "horas" y "nombre".
"""