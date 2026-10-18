
// BOTÓN DE INICIO DE SESIÓN
// =================================

const btnLogin = document.getElementById("btnLogin");

btnLogin.addEventListener("click", () => {

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    // Comprobamos que los campos no estén vacíos
    if (email === "" || password === "") {

        alert("Debes ingresar tu email y contraseña.");

        return;
    }

    // agregar funciones para que se conecte con back e inicie sesion

    alert("Intentando iniciar sesión con: " + email);

});



// INICIO GOOGLE
// =================================

const btnGoogle = document.getElementById("btnGoogle");

btnGoogle.addEventListener("click", () => {

    alert("Inicio de sesión con Google");

});


// INICIO MICROSOFT
// =================================

const btnMicrosoft = document.getElementById("btnMicrosoft");

btnMicrosoft.addEventListener("click", () => {

    alert("Inicio de sesión con Microsoft");

});



// INICIO APPLE
// =================================

const btnApple = document.getElementById("btnApple");

btnApple.addEventListener("click", () => {

    alert("Inicio de sesión con Apple");

});



// RECUPERAR CONTRASEÑA
// ================================

const recuperarContraseña =
    document.getElementById("recuperarContraseña");

recuperarContraseña.addEventListener("click", (event) => {

    event.preventDefault();

    alert("Aquí irá el sistema para recuperar la contraseña.");

});



// REGISTRO NUEVO USUARIO
// =================================

const btnRegistro = document.getElementById("btnRegistro");

btnRegistro.addEventListener("click", (event) => {

    event.preventDefault();

    window.location.href = "../Registrar_nuevoUsuario/registro.html";

});