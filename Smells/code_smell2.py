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
import os

# Constantes 
NOTA_MINIMA = 1.0
NOTA_MAXIMA = 7.0
NOTA_APROBATORIA = 4.0
ARCHIVO_ALUMNOS = "Smells/alumnos_smell_2.txt"

def guardar_registro_alumno(nombre, nota, estado):
    """Guarda el registro de un alumno en el archivo."""
    necesita_salto = False
    if os.path.exists(ARCHIVO_ALUMNOS) and os.path.getsize(ARCHIVO_ALUMNOS) > 0:
        with open(ARCHIVO_ALUMNOS, "rb") as f:
            f.seek(-1, os.SEEK_END)
            if f.read(1) != b"\n":
                necesita_salto = True

    with open(ARCHIVO_ALUMNOS, "a", encoding="utf-8") as f:
        prefijo = "\n" if necesita_salto else ""
        f.write(f"{prefijo}{nombre},{nota},{estado}\n")

def nota_valida(nota):
    """Verifica si la nota es válida según los límites definidos."""
    if NOTA_MINIMA <= nota <= NOTA_MAXIMA:
        return True
    else:
        return False

def calcular_estado(nota):
    """Determina si un estudiante aprueba o reprueba según su nota."""
    if nota >= NOTA_APROBATORIA:
        return "aprobado"
    else:
        return "reprobado"

def calcular_promedio():
    """Calcula el promedio de las notas de los alumnos."""
    with open(ARCHIVO_ALUMNOS, "r", encoding="utf-8") as f:
        lineas = [l.strip() for l in f if l.strip()]
    notas = [float(l.split(",")[1]) for l in lineas]
    if notas:
        promedio = sum(notas) / len(notas)
        return promedio
    else:
        return 0.0

def registrar_alumno(nombre, nota):
    """Registra un alumno, valida su nota, guarda el registro y calcula el promedio del curso."""
    if not nota_valida(nota):
        print(f"nota invalida {nombre}: {nota}")
        return

    estado = calcular_estado(nota)
    guardar_registro_alumno(nombre, nota, estado)
    print(f"{nombre}: {estado}")

registrar_alumno("Juan", 5)
registrar_alumno("Maria", 3)
registrar_alumno("Pedro", 8)  # Nota inválida
registrar_alumno("Ana", 6)
registrar_alumno("Luis", 4)

promedio_curso = calcular_promedio()
print(f"Promedio curso: {promedio_curso:.1f}")