from enum import Enum

class Rol(Enum):
    Transportista = "Transportista"
    Dador_carga = "Dador de carga"
    Admin_Backoffice = "Admin Backoffice"

class EstadoValidacion(Enum):
    Pendiente = "Pendiente"
    Aprobado = "Aprobado"
    Rechazado = "Rechazado"

class TipoDocumento(Enum):
    LICENCIA_CONDUCIR = "LICENCIA_CONDUCIR"
    PADRON_VEHICULO = "PADRON_VEHICULO"
    REVISION_TECNICA = "REVISION_TECNICA"
    SEGURO_CARGA = "SEGURO_CARGA"
    ANTECEDENTES = "ANTECEDENTES"
