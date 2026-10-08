#Servicio de negocio para la gestion del ciclo de vida de los Contratos.

#Orquesta los modelos de dominio, la maquina de estados y la capa de persistencia.


from uuid import UUID

from dao.contrato_dao import ContratoDAO
from domain.maquina_estados import EstadoContrato, MaquinaEstadosContrato
from domain.modelos import ContratoCrear, ContratoModelo
from services.onboarding_service import OnboardingService, onboarding_service_instancia


class ServicioContrato:
    #Servicio que encapsula los casos de uso principales de Contratos.

    def __init__(
        self,
        dao: ContratoDAO,
        onboarding_service: OnboardingService | None = None,
    ) -> None:
        self.dao = dao
        self.onboarding_service = onboarding_service or onboarding_service_instancia

    def crear_contrato(self, datos: ContratoCrear) -> ContratoModelo:
        #Crea un nuevo contrato en estado BORRADOR y lo persiste via DAO.
        if not self.onboarding_service.es_dador_aprobado(datos.id_empresa_generadora):
            raise PermissionError(
                f"La empresa generadora {datos.id_empresa_generadora} no cuenta con su "
                "verificacion KYC/Onboarding en estado APROBADO."
            )

        nuevo_contrato = ContratoModelo(**datos.model_dump())
        return self.dao.guardar(nuevo_contrato)

    def obtener_contrato(self, contrato_id: UUID) -> ContratoModelo:
        #Recupera un contrato por su ID unico. Lanza ValueError si no existe.
        contrato = self.dao.obtener_por_id(contrato_id)
        if not contrato:
            raise ValueError(f"El contrato con ID {contrato_id} no fue encontrado")
        return contrato

    def listar_contratos(self) -> list[ContratoModelo]:
        #Obtiene la lista completa de todos los contratos registrados.
        return self.dao.obtener_todos()

    def cambiar_estado(
        self,
        contrato_id: UUID,
        nuevo_estado: EstadoContrato,
        id_transportista: UUID | None = None,
        id_camion: UUID | None = None,
    ) -> ContratoModelo:
        #Solicita un cambio de estado evaluando las reglas de la Maquina de Estados y persiste los cambios aplicados.
        
        contrato = self.obtener_contrato(contrato_id)

        contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
            contrato_data=contrato,
            nuevo_estado=nuevo_estado,
            id_transportista=id_transportista,
            id_camion=id_camion,
        )

        self.dao.actualizar(contrato_id, contrato_actualizado)
        return contrato_actualizado


# Alias para retrocompatibilidad
ContratoService = ServicioContrato


if __name__ == "__main__":
    import unittest
    from unittest.mock import MagicMock
    from uuid import uuid4
    from datetime import datetime, timedelta, UTC
    from domain.modelos import Moneda, TipoCarga

    class TestServicioContrato(unittest.TestCase):
        def setUp(self):
            # Mocks
            self.mock_dao = MagicMock()
            self.mock_onboarding_service = MagicMock()
            
            # SUT (System Under Test)
            self.servicio = ServicioContrato(
                dao=self.mock_dao,
                onboarding_service=self.mock_onboarding_service
            )
            
            # Datos base válidos para pruebas
            self.id_empresa = uuid4()
            ahora = datetime.now(UTC)
            datos_dict = {
                "id_empresa_generadora": self.id_empresa,
                "origen": "SANTIAGO",
                "destino": "VALPARAISO",
                "f_estimada_salida": ahora + timedelta(hours=48),
                "f_estimada_llegada": ahora + timedelta(hours=72),
                "f_cierre_postulaciones": ahora + timedelta(hours=24),
                "input_camionKG": 20000,
                "tipo_carga": TipoCarga.GENERAL,
                "peso_total": 15000,
                "moneda": Moneda.CLP,
                "monto_neto": 100000,
                "monto_iva": 19000,
                "monto_total": 119000
            }
            self.datos_validos = ContratoCrear(**datos_dict)

        def test_crear_contrato_exito_y_guardado(self):
            """Prueba que el contrato se crea y guarda exitosamente cuando la empresa está aprobada."""
            self.mock_onboarding_service.es_dador_aprobado.return_value = True
            
            self.servicio.crear_contrato(self.datos_validos)
            
            self.mock_onboarding_service.es_dador_aprobado.assert_called_once_with(self.id_empresa)
            self.mock_dao.guardar.assert_called_once()
            argumento_guardado = self.mock_dao.guardar.call_args[0][0]
            self.assertEqual(argumento_guardado.id_empresa_generadora, self.id_empresa)
            self.assertEqual(argumento_guardado.estado, "BORRADOR")
            
        def test_crear_contrato_falla_empresa_no_aprobada(self):
            """Prueba que la función lanza PermissionError cuando la validación KYC no está aprobada."""
            self.mock_onboarding_service.es_dador_aprobado.return_value = False
            
            with self.assertRaises(PermissionError) as context:
                self.servicio.crear_contrato(self.datos_validos)
                
            self.assertIn("no cuenta con su verificacion KYC/Onboarding en estado APROBADO", str(context.exception))
            self.mock_onboarding_service.es_dador_aprobado.assert_called_once_with(self.id_empresa)
            self.mock_dao.guardar.assert_not_called()

        def test_crear_contrato_falla_por_datos_inconsistentes(self):
            """Prueba que crear un contrato con datos inconsistentes (Entrada inválida 2 en a.md)
            arroja un ValidationError de Pydantic (ValueError).
            """
            from pydantic import ValidationError
            
            # Replicamos los datos, pero con un IVA que no corresponde al 19%
            datos_invalidos_dict = {
                "id_empresa_generadora": self.id_empresa,
                "origen": "SANTIAGO",
                "destino": "VALPARAISO",
                "f_estimada_salida": datetime.now(UTC) + timedelta(hours=48),
                "f_estimada_llegada": datetime.now(UTC) + timedelta(hours=72),
                "f_cierre_postulaciones": datetime.now(UTC) + timedelta(hours=24),
                "input_camionKG": 20000,
                "tipo_carga": TipoCarga.GENERAL,
                "peso_total": 15000,
                "moneda": Moneda.CLP,
                "monto_neto": 100000,
                "monto_iva": 0, # Error intencional: en CLP debería ser 19000
                "monto_total": 100000 # Error intencional
            }
            
            with self.assertRaises(ValidationError) as context:
                ContratoCrear(**datos_invalidos_dict)
                
            self.assertIn("no corresponde al", str(context.exception))

    unittest.main()
