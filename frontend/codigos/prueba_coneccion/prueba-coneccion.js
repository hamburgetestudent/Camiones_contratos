async function probarConexion() {
    try {
        const respuesta = await fetch(
            "http://127.0.0.1:8000/docs"
        );

        if (!respuesta.ok) {
            throw new Error(`Error HTTP: ${respuesta.status}`);
        }

        const datos = await respuesta.json();

        console.log("Conexión exitosa");
        console.log("Respuesta del backend:", datos);

    } catch (error) {
        console.error("Falló la conexión:", error.message);
    }
}

probarConexion();