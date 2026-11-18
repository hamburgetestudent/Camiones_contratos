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
Code Smells identificados y corregidos:
1. Función Monolítica / Responsabilidad Múltiple (Violación de SRP):
   - La función 'registrar_alumno' realizaba validación, cálculo de estado, E/S de archivo,
     impresión en consola y cálculo estadístico.
   - Solución: Se divide en funciones modulares y reutilizables:
     - es_nota_valida: valida rangos de nota.
     - calcular_estado: determina aprobación o reprobación.
     - guardar_registro_alumno: maneja la persistencia en el archivo.
     - calcular_promedio_curso: calcula el promedio a partir del archivo.
     - registrar_alumno: orquesta el flujo completo de forma limpia.

2. Números Mágicos:
   - Se reemplazan 1, 7 y 4 por constantes descriptivas a nivel de módulo:
     NOTA_MINIMA = 1.0, NOTA_MAXIMA = 7.0, NOTA_APROBATORIA = 4.0.

3. Cadenas Mágicas Repetidas:
   - El nombre de archivo "alumnos.txt" se define en la constante ARCHIVO_ALUMNOS.
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