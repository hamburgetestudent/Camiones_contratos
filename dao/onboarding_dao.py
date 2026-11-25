"""DAO de onboarding en memoria."""

from dao.base_dao import DAOMemoria


class DadorCargaDAOInMemory(DAOMemoria):
    """Implementación DAO en memoria para Dador de Carga."""

    pass


class DocumentoDAOInMemory(DAOMemoria):
    """Implementación DAO en memoria para Documentos."""

    pass


class OnboardingDAO(DAOMemoria):
    """Implementación DAO en memoria para Onboarding general."""

    pass