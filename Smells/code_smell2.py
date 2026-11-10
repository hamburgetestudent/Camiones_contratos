# def registrar_alumno(nombre, nota):
#     # verifica si la nota es valida
#     if nota < 1 or nota > 7:
#         print("nota invalida")
#         return
#     # calcula si aprueba
#     if nota >= 4:
#         estado = "aprobado"
#     else:
#         estado = "reprobado"
#     # guarda en archivo
#     with open("alumnos.txt", "a") as f:
#         f.write(f"{nombre},{nota},{estado}\n")
#     # muestra mensaje
#     print(f"{nombre}: {estado}")
#     # calcula promedio del curso
#     with open("alumnos.txt", "r") as f:
#         lineas = f.readlines()
#     notas = [float(l.split(",")[1]) for l in lineas]
#     promedio = sum(notas) / len(notas)
#     print(f"Promedio curso: {promedio:.1f}")


"""
Funcion lineal, podria ser divida en varias funciones.

Se deben declarar constantes para los valores de las notas, y no usar numeros magicos.
por ejemplo nota_minima = 1 y nota_maxima = 7 y nota_aprobatoria = 4
"""

def guardar_archivo(nombre, nota, estado):
    with open("alumnos.txt", "a") as f:
        f.write(f"{nombre},{nota},{estado}\n")

def calcular_promedio():
    with open("alumnos.txt", "r") as f:
        lineas = f.readlines()
    notas = [float(l.split(",")[1]) for l in lineas]
    promedio = sum(notas) / len(notas)
    return promedio

def calcular_estado(nota):
    NOTA_APROVATORIA = 4
    if nota >= NOTA_APROVATORIA:
        return "aprobado"
    else:
        return "reprobado"

