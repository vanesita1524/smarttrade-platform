// Seleccionamos el botón y el buscador móvil
const btnLupa = document.getElementById("btnLupa");
const searchBoxMobile = document.getElementById("searchBoxMobile");

// Evento clic para mostrar/ocultar
btnLupa?.addEventListener("click", () => {
  if (searchBoxMobile.style.display === "none" || searchBoxMobile.style.display === "") {
    searchBoxMobile.style.display = "block"; // mostrar
  } else {
    searchBoxMobile.style.display = "none"; // ocultar
  }
});

