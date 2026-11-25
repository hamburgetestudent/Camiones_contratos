"""Modulo centralizado de inyeccion de dependencias y singletons para los servicios.

Aqui se construyen los almacenes persistentes (DAO sobre SQLite) y se inyectan
en los servicios, de modo que todo el estado de negocio (usuarios, onboarding,
contratos y subastas) sobrevive a un reinicio de la aplicacion.
"""

from app.modules.contratos.dao import ContratoDAO, ContratoDAOSQLite
from app.modules.contratos.service import ServicioContrato
from app.modules.onboarding.dao import (
    DadorCargaDAO,
    DadorCargaDAOSQLite,
    DocumentoDAO,
    DocumentoDAOSQLite,
)
from app.modules.onboarding.service import OnboardingService
from app.modules.subastas.dao import PostulacionDAO, PostulacionDAOSQLite
from app.modules.subastas.service import ServicioSubasta
from app.modules.usuarios.dao import UsuarioDAO, UsuarioDAOSQLite
from app.modules.usuarios.service import UsuarioService

# Almacenes persistentes compartidos (usan la base de datos por defecto)
contrato_dao: ContratoDAO = ContratoDAOSQLite()
postulacion_dao: PostulacionDAO = PostulacionDAOSQLite()
usuario_dao: UsuarioDAO = UsuarioDAOSQLite()
documento_dao: DocumentoDAO = DocumentoDAOSQLite()
dador_dao: DadorCargaDAO = DadorCargaDAOSQLite()

# Usuarios y onboarding usan los mismos DAO compartidos
UsuarioService.dao = usuario_dao
servicio_onboarding = OnboardingService(
    documento_dao=documento_dao, dador_dao=dador_dao
)

# Instancias compartidas a nivel de aplicacion
servicio_contrato = ServicioContrato(
    dao=contrato_dao, onboarding_service=servicio_onboarding
)
servicio_subasta = ServicioSubasta(
    contrato_dao=contrato_dao, postulacion_dao=postulacion_dao
)


def obtener_contrato_dao() -> ContratoDAO:
    """Retorna el DAO persistente de contratos."""
    return contrato_dao


def obtener_postulacion_dao() -> PostulacionDAO:
    """Retorna el DAO persistente de postulaciones."""
    return postulacion_dao


def obtener_usuario_dao() -> UsuarioDAO:
    """Retorna el DAO persistente de usuarios."""
    return usuario_dao


def obtener_servicio_onboarding() -> OnboardingService:
    """Retorna el servicio de onboarding con sus DAO persistentes."""
    return servicio_onboarding


def obtener_servicio_contrato() -> ServicioContrato:
    """Retorna la instancia singleton del servicio de contratos."""
    return servicio_contrato


def obtener_servicio_subasta() -> ServicioSubasta:
    """Retorna la instancia singleton del servicio de subastas."""
    return servicio_subasta


# Alias para retrocompatibilidad
obt_servicio_contrato = obtener_servicio_contrato
obt_servicio_subasta = obtener_servicio_subasta
get_contrato_service = obtener_servicio_contrato
get_subasta_service = obtener_servicio_subasta
contrato_service = servicio_contrato
subasta_service = servicio_subasta
