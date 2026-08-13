from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional

# =====================================================================
# INICIALIZACIÓN DE LA APLICACIÓN
# =====================================================================

# 'app' es el objeto central de nuestra aplicación FastAPI.
# Se encarga de recibir las peticiones HTTP y retornar las respuestas.
app = FastAPI(
    title="API de Contratos de Camiones",
    description="API y Panel de Control en tiempo real para gestionar contratos de fletes.",
    version="1.2.0"
)

# Configuración de CORS (Cross-Origin Resource Sharing).
# Permite que otros sistemas (como tu frontend de Electron o el navegador)
# realicen solicitudes a este backend sin restricciones de seguridad de origen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Permite todas las cabeceras
)

# =====================================================================
# MODELOS DE DATOS (ESQUEMAS PYDANTIC)
# =====================================================================

# Este modelo define la estructura de datos requerida para crear un nuevo contrato.
# Pydantic valida que los datos que entren cumplan con estas reglas.
class SolicitudContrato(BaseModel):
    # 'cantidad_carga' es el peso de la mercancía. gt=0 valida que sea mayor que cero.
    cantidad_carga: float = Field(
        ...,
        description="Cantidad de carga a transportar (en toneladas métricas)",
        gt=0
    )
    # 'fecha_limite' es la fecha tope de entrega de la carga.
    fecha_limite: date = Field(
        ...,
        description="Fecha límite para completar la entrega (Formato: YYYY-MM-DD)"
    )
    # 'origen' es el lugar de retiro de la mercancía.
    origen: str = Field(
        ...,
        min_length=3,
        description="Ciudad o punto de recolección/origen"
    )
    # 'destino' es el lugar donde se entregará la mercancía.
    destino: str = Field(
        ...,
        min_length=3,
        description="Ciudad o punto de entrega final/destino"
    )
    # 'tipo_material' describe la naturaleza del producto (madera, cobre, alimentos, etc.).
    tipo_material: str = Field(
        ...,
        min_length=2,
        description="Tipo de material o carga que se transporta"
    )
    # 'tarifa_propuesta' es el precio ofrecido por el transporte del flete (en CLP o USD).
    tarifa_propuesta: int = Field(
        ...,
        description="Monto en dinero ofrecido por realizar el servicio",
        gt=0
    )

# Este modelo sirve para recibir actualizaciones del estado de un contrato.
class ActualizacionEstado(BaseModel):
    # El nuevo estado del flete: Pendiente, Asignado, En Ruta, Entregado.
    estado: str = Field(
        ...,
        description="Nuevo estado que tomará el contrato"
    )

# Este modelo sirve para registrar la asignación de un camión a un flete.
class AsignacionCamion(BaseModel):
    # 'camion' representa la patente o placa del vehículo de transporte.
    camion: str = Field(
        ...,
        min_length=4,
        description="Identificación o patente del camión asignado al contrato"
    )

# =====================================================================
# BASE DE DATOS SIMULADA EN MEMORIA
# =====================================================================

# 'base_datos_contratos' almacena la lista de contratos activos de manera temporal.
# Al reiniciar el servidor de Python, esta lista vuelve a su estado inicial.
base_datos_contratos: List[dict] = [
    {
        "id_contrato": 1,
        "cantidad_carga": 28.5,
        "fecha_limite": "2026-08-20",
        "origen": "Santiago",
        "destino": "Valparaíso",
        "tipo_material": "Cátodos de Cobre",
        "tarifa_propuesta": 480000,
        "estado": "Asignado",
        "camion_asignado": "GH-JK-89"
    },
    {
        "id_contrato": 2,
        "cantidad_carga": 14.2,
        "fecha_limite": "2026-08-25",
        "origen": "Concepción",
        "destino": "Chillán",
        "tipo_material": "Madera Elaborada",
        "tarifa_propuesta": 290000,
        "estado": "Pendiente",
        "camion_asignado": None
    },
    {
        "id_contrato": 3,
        "cantidad_carga": 9.0,
        "fecha_limite": "2026-08-16",
        "origen": "Rancagua",
        "destino": "Santiago",
        "tipo_material": "Alimentos Perecibles",
        "tarifa_propuesta": 180000,
        "estado": "En Ruta",
        "camion_asignado": "XY-ZW-12"
    }
]

# 'contador_id' mantiene el número correlativo para asignar IDs únicos a nuevos contratos.
contador_id: int = 4


# =====================================================================
# ESTADO DEL SERVIDOR (HEALTH CHECK)
# =====================================================================

# Ruta principal ('/') que retorna un estado de confirmación del backend.
@app.get("/")
def check_estado():
    """
    Retorna un estado indicando que el backend está activo y la dirección de documentación.
    """
    return {
        "estado": "online",
        "mensaje": "Servidor backend de Contratos de Camiones activo.",
        "documentacion": "/docs"
    }


# =====================================================================
# RUTAS DE LA API REST (CRUD Y LOGICA DE NEGOCIO)
# =====================================================================

# Ruta GET para obtener el listado completo de solicitudes de contrato.
@app.get("/solicitudes/", response_model=List[dict])
def obtener_solicitudes():
    """
    Retorna la lista de todas las solicitudes de contratos guardadas.
    """
    return base_datos_contratos


# Ruta POST para ingresar un nuevo contrato.
@app.post("/solicitudes/", status_code=status.HTTP_201_CREATED)
def crear_solicitud(solicitud: SolicitudContrato):
    """
    Recibe una solicitud de contrato de flete, le asigna un ID único correlativo
    e inicializa su estado como 'Pendiente' sin camión asignado.
    """
    global contador_id
    
    # Convertimos el esquema de Pydantic a un diccionario de Python
    nuevo_flete = solicitud.model_dump()
    
    # Asignamos el ID único autoincrementado
    nuevo_flete["id_contrato"] = contador_id
    # Estado por defecto de una nueva solicitud
    nuevo_flete["estado"] = "Pendiente"
    # Por defecto, no tiene camión asignado
    nuevo_flete["camion_asignado"] = None
    
    # Insertar en la lista (nuestra simulación de base de datos)
    base_datos_contratos.append(nuevo_flete)
    
    # Incrementar el contador para el próximo registro
    contador_id += 1
    
    return {
        "mensaje": "Solicitud de contrato de flete creada con éxito.",
        "datos": nuevo_flete
    }


# Ruta PUT para asignar un camión a un contrato específico.
@app.put("/solicitudes/{id_contrato}/camion/")
def asignar_camion_flete(id_contrato: int, asignacion: AsignacionCamion):
    """
    Asigna un camión (patente) a un contrato existente por su ID.
    Al asignar un camión, el estado del flete cambia automáticamente a 'Asignado'.
    """
    for contrato in base_datos_contratos:
        if contrato["id_contrato"] == id_contrato:
            # Validamos que el flete no haya finalizado ya
            if contrato["estado"] == "Entregado":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede asignar un camión a un flete ya completado."
                )
            
            # Asignamos la patente del camión
            contrato["camion_asignado"] = asignacion.camion
            # Transición automática de estado
            contrato["estado"] = "Asignado"
            
            return {
                "mensaje": f"Camión '{asignacion.camion}' asignado exitosamente al contrato {id_contrato}.",
                "contrato": contrato
            }
            
    # Si recorre toda la lista y no lo encuentra, lanza error 404
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No se encontró ningún contrato con el ID {id_contrato}."
    )


# Ruta PUT para cambiar el estado del contrato (ej. de 'Asignado' a 'En Ruta' o 'Entregado').
@app.put("/solicitudes/{id_contrato}/estado/")
def actualizar_estado_flete(id_contrato: int, actualizacion: ActualizacionEstado):
    """
    Actualiza manualmente el estado de un flete a uno válido:
    'Pendiente', 'Asignado', 'En Ruta', 'Entregado'.
    """
    estados_validos = ["Pendiente", "Asignado", "En Ruta", "Entregado"]
    
    if actualizacion.estado not in estados_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Los estados permitidos son: {', '.join(estados_validos)}"
        )
        
    for contrato in base_datos_contratos:
        if contrato["id_contrato"] == id_contrato:
            # Validar que si cambia a 'Asignado' o 'En Ruta', tenga un camión asignado
            if actualizacion.estado in ["Asignado", "En Ruta"] and not contrato["camion_asignado"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede cambiar a este estado sin un camión asignado previamente."
                )
                
            # Asignamos el nuevo estado
            contrato["estado"] = actualizacion.estado
            return {
                "mensaje": f"Estado del contrato {id_contrato} actualizado a '{actualizacion.estado}'.",
                "contrato": contrato
            }
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No se encontró el contrato con ID {id_contrato}."
    )


# Ruta DELETE para remover un contrato de la lista.
@app.delete("/solicitudes/{id_contrato}")
def eliminar_contrato_flete(id_contrato: int):
    """
    Elimina un contrato de la base de datos simulada por su ID único.
    """
    for indice, contrato in enumerate(base_datos_contratos):
        if contrato["id_contrato"] == id_contrato:
            # Quitamos el elemento de la lista por su índice
            base_datos_contratos.pop(indice)
            return {"mensaje": f"Contrato #{id_contrato} eliminado correctamente."}
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No se pudo eliminar: No existe un contrato con el ID {id_contrato}."
    )
