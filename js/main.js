/**
 * main.js
 * ---------------------------------------------------------
 * Punto de entrada. Solo arranca la interfaz cuando el DOM
 * está listo. No debería crecer mucho: la lógica real vive
 * en data.js, ui.js y descarga.js.
 * ---------------------------------------------------------
 */

document.addEventListener('DOMContentLoaded', () => {
  UI.iniciar().catch(err => {
    console.error(err);
    document.getElementById('grid').innerHTML =
      '<p style="color:var(--texto-tenue)">No se pudieron cargar los productos. Revisa data/productos.json</p>';
  });
});
