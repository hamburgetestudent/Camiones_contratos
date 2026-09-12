"""Prueba integrada del ciclo contrato, ofertas, revision y adjudicacion."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from dao.auditoria_dao import AuditoriaDAOSQLite
from dao.contrato_dao import ContratoDAOMemoria
from dao.postulacion_dao import PostulacionDAOMemoria
from domain.maquina_estados import EstadoContrato
from domain.modelos import ContratoCrear, Moneda, TipoCarga
from domain.postulacion import EstadoPostulacion, PostulacionCrear
from services.auditoria_service import ServicioAuditoria
from services.contrato_service import ServicioContrato
from services.subasta_service import ServicioSubasta


class OnboardingAprobado:
    """Doble de prueba que autoriza la creacion del contrato."""

    def es_dador_aprobado(self, usuario_id: UUID) -> bool:
        """Simula una empresa que ya completo el proceso KYC."""
        return bool(usuario_id)


def test_reconstruye_contrato_ofertas_revisor_y_bases() -> None:
    """El historial final contiene toda la evidencia exigida por CR-203."""
    auditoria_dao = AuditoriaDAOSQLite(":memory:")
    auditoria_service = ServicioAuditoria(auditoria_dao)
    contrato_dao = ContratoDAOMemoria()
    postulacion_dao = PostulacionDAOMemoria()
    contrato_service = ServicioContrato(
        dao=contrato_dao,
        onboarding_service=OnboardingAprobado(),
        auditoria_service=auditoria_service,
    )
    subasta_service = ServicioSubasta(
        contrato_dao=contrato_dao,
        postulacion_dao=postulacion_dao,
        auditoria_service=auditoria_service,
    )

    empresa_id = uuid4()
    revisor_id = uuid4()
    transportista_uno = uuid4()
    transportista_dos = uuid4()
    salida = datetime.now(UTC) + timedelta(days=2)
    contrato = contrato_service.crear_contrato(
        ContratoCrear(
            id_empresa_generadora=empresa_id,
            origen="San Felipe",
            destino="Santiago",
            f_estimada_salida=salida,
            f_estimada_llegada=salida + timedelta(hours=3),
            f_cierre_postulaciones=salida - timedelta(hours=4),
            input_camionKG=10_000,
            tipo_carga=TipoCarga.GENERAL,
            peso_total=5_000,
            moneda=Moneda.CLP,
            monto_neto=100_000,
            monto_iva=19_000,
            monto_total=119_000,
        )
    )
    contrato_service.cambiar_estado(
        contrato.id,
        EstadoContrato.PUBLICADO,
        actor_id=empresa_id,
    )
    oferta_uno = subasta_service.postular_a_carga(
        PostulacionCrear(
            carga_id=contrato.id,
            transportista_id=transportista_uno,
            precio_oferta=90_000,
            tiempo_entrega_horas=3,
        )
    )
    oferta_dos = subasta_service.postular_a_carga(
        PostulacionCrear(
            carga_id=contrato.id,
            transportista_id=transportista_dos,
            precio_oferta=85_000,
            tiempo_entrega_horas=4,
        )
    )

    subasta_service.adjudicar_subasta(
        carga_id=contrato.id,
        postulacion_id=oferta_dos.id,
        revisado_por=revisor_id,
    )
    reconstruccion = auditoria_service.reconstruir_estado(contrato.id)

    assert reconstruccion.contrato is not None
    assert reconstruccion.contrato["estado"] == EstadoContrato.ADJUDICADO.value
    assert len(reconstruccion.ofertas) == 2
    assert {oferta["estado"] for oferta in reconstruccion.ofertas} == {
        EstadoPostulacion.RECHAZADA.value,
        EstadoPostulacion.SELECCIONADA.value,
    }
    assert reconstruccion.revisiones[0]["actor_id"] == str(revisor_id)
    assert reconstruccion.decisiones[0]["actor_id"] == str(revisor_id)
    assert len(reconstruccion.decisiones[0]["informacion_utilizada"]["ofertas_consideradas"]) == 2
    assert reconstruccion.bases_aplicadas
    assert oferta_uno.id != oferta_dos.id
    assert auditoria_service.verificar_integridad().integra is True

    auditoria_dao.cerrar()
