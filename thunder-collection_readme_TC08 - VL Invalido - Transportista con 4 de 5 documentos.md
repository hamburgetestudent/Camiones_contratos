# Thunder Client API Documentation

## Collection: TC08 - VL Invalido - Transportista con 4 de 5 documentos

**Base URL:** `http://127.0.0.1:8000`

### Requests (No Folder)

### POST /auth/registro
- **Name**: TC01 - CE Valida - Registro Dador de Carga exitoso

**Request Body** (json):

```json
{
  "nombre": "Empresa Logistica Sur",
  "email": "dador.fijo@logisticasur.cl",
  "rol": "DADOR_CARGA",
  "password": "password123",
  "perfil_tributario": {
    "rut_id_empresa": "11111111-1",
    "datos_facturacion": {
      "razon_social": "Logistica Sur SpA",
      "direccion": "Av. Brasil 1234, Valparaiso",
      "correo_facturacion": "facturacion@logisticasur.cl"
    }
  }
}
```

---

### POST /auth/registro
- **Name**: TC02 - CE Valida - Registro Transportista exitoso

**Request Body** (json):

```json
{
  "nombre": "Juan Perez",
  "email": "juan.transp4@correo.cl",
  "rol": "TRANSPORTISTA",
  "password": "miPasswordSegura",
  "documentos": [
    { "tipo": "LICENCIA_CONDUCIR", "archivo": "licencia.pdf" },
    { "tipo": "PADRON_VEHICULO", "archivo": "padron.jpg" },
    { "tipo": "REVISION_TECNICA", "archivo": "revision.jpeg" },
    { "tipo": "SEGURO_CARGA", "archivo": "seguro.png" },
    { "tipo": "ANTECEDENTES", "archivo": "antecedentes.pdf" }
  ]
}
```

---

### POST /auth/registro
- **Name**: TC03 - VL Inferior Valido - Password de 6 caracteres exactos

**Request Body** (json):

```json
{
  "nombre": "Transportes Limite",
  "email": "limite2@logisticasur.cl",
  "rol": "DADOR_CARGA",
  "password": "123456",
  "perfil_tributario": {
    "rut_id_empresa": "11111111-1",
    "datos_facturacion": {
      "razon_social": "Transportes Limite Ltda",
      "direccion": "Calle Prat 500",
      "correo_facturacion": "facturacion.limite2@logisticasur.cl"
    }
  }
}
```

---

### POST /auth/registro
- **Name**: TC04 - VL Inferior Invalido - Password de 5 caracteres

**Request Body** (json):

```json
{
  "nombre": "Usuario Password Corta",
  "email": "corta5@logisticasur.cl",
  "rol": "DADOR_CARGA",
  "password": "12345",
  "perfil_tributario": {
    "rut_id_empresa": "11111111-1",
    "datos_facturacion": {
      "razon_social": "Empresa Test",
      "direccion": "Calle 1",
      "correo_facturacion": "corta5@logisticasur.cl"
    }
  }
}
```

---

### POST /auth/registro
- **Name**: TC05 - Logica Negocio - Correo electronico duplicado

**Request Body** (json):

```json
{
  "nombre": "Intento Duplicado",
  "email": "dador.fijo@logisticasur.cl",
  "rol": "DADOR_CARGA",
  "password": "password123",
  "perfil_tributario": {
    "rut_id_empresa": "11111111-1",
    "datos_facturacion": {
      "razon_social": "Otra Empresa SpA",
      "direccion": "Av. Libertad 100",
      "correo_facturacion": "otro@logisticasur.cl"
    }
  }
}
```

---

### POST /auth/registro
- **Name**: TC06 - CE Invalida - Formato de email invalido

**Request Body** (json):

```json
{
  "nombre": "Usuario Correo Malo",
  "email": "correo_sin_arroba_ni_dominio",
  "rol": "DADOR_CARGA",
  "password": "password123",
  "perfil_tributario": {
    "rut_id_empresa": "11111111-1",
    "datos_facturacion": {
      "razon_social": "Empresa X",
      "direccion": "Calle X",
      "correo_facturacion": "facturacion@empresa.cl"
    }
  }
}
```

---

### POST /auth/registro
- **Name**: TC07 - CE Invalida - Rol no permitido

**Request Body** (json):

```json
{
  "nombre": "Usuario Rol Invalido",
  "email": "rolinvalido@correo.cl",
  "rol": "ADMINISTRADOR",
  "password": "password123",
  "perfil_tributario": {
    "rut_id_empresa": "11111111-1",
    "datos_facturacion": {
      "razon_social": "Empresa Rol",
      "direccion": "Calle Rol 123",
      "correo_facturacion": "rol@empresa.cl"
    }
  }
}
```

---

### POST /auth/registro
- **Name**: TC08 - VL Invalido - Transportista con 4 de 5 documentos

**Request Body** (json):

```json
{
  "nombre": "Pedro Incompleto",
  "email": "pedro.incompleto@correo.cl",
  "rol": "TRANSPORTISTA",
  "password": "password123",
  "documentos": [
    { "tipo": "LICENCIA_CONDUCIR", "archivo": "licencia.pdf" },
    { "tipo": "PADRON_VEHICULO", "archivo": "padron.pdf" },
    { "tipo": "REVISION_TECNICA", "archivo": "revision.pdf" },
    { "tipo": "SEGURO_CARGA", "archivo": "seguro.pdf" }
  ]
}
```

---

### POST /auth/registro
- **Name**: TC09 - CE Invalida - Formato de documento no permitido (.exe)

**Request Body** (json):

```json
{
  "nombre": "Carlos Archivo Malo",
  "email": "carlos.exe@correo.cl",
  "rol": "TRANSPORTISTA",
  "password": "password123",
  "documentos": [
    { "tipo": "LICENCIA_CONDUCIR", "archivo": "licencia.exe" },
    { "tipo": "PADRON", "archivo": "padron.pdf" },
    { "tipo": "REVISION_TECNICA", "archivo": "revision.pdf" },
    { "tipo": "SEGURO", "archivo": "seguro.pdf" },
    { "tipo": "ANTECEDENTES", "archivo": "antecedentes.pdf" }
  ]
}
```

---

### POST /auth/registro
- **Name**: TC10 - Logica Negocio - RUT con digito verificador invalido

**Request Body** (json):

```json
{
  "nombre": "Empresa RUT Malo",
  "email": "rutmalo@empresa.cl",
  "rol": "DADOR_CARGA",
  "password": "password123",
  "perfil_tributario": {
    "rut_id_empresa": "11111111-9",
    "datos_facturacion": {
      "razon_social": "Empresa RUT Malo SpA",
      "direccion": "Av. Espana 2000",
      "correo_facturacion": "facturacion@empresa.cl"
    }
  }
}
```

---

