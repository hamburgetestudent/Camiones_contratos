document.getElementById("motivo").textContent = new URLSearchParams(location.search).get("motivo");
document.getElementById("reintentar").addEventListener("click", () => {
  location.assign("reintentar");
});
