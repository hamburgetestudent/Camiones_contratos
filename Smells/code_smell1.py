# def c(lst):
#     t = 0
#     for x in lst:
#         t = t + x
#     m = t / len(lst)
#     return m

# resultado = c([85, 90, 78, 92, 88])
# print(resultado)

"""
- Funcion, no declara su funcion: la cual es calcular_promedio, 
pero no tiene un nombre descriptivo.

# Variables no declaradas

1 - t : total
2 - x : numero
3 - m : promedio


"""
notas_pruebas = [85, 90, 78, 92, 88]

def calcular_promedio(lista):
    total = 0
    for numero in lista:
        total += numero
        promedio = total / len(lista)
    return promedio

resultado = calcular_promedio(notas_pruebas)
print(resultado)