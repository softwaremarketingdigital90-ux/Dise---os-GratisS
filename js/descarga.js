/**
 * descarga.js
 * ---------------------------------------------------------
 * Pantalla de descarga: por ahora no hay anuncios ni espera,
 * solo se muestra el botón de descarga animado. El archivo
 * se descarga directo al hacer clic.
 * ---------------------------------------------------------
 */

const Descarga = (() => {
  function mostrarPantallaEspera(producto) {
    document.getElementById('modalCatLabel').textContent = 'DESCARGA';

    document.getElementById('modalBody').innerHTML = `
      <div class="wait-screen">
        <p class="eyebrow">Tu diseño está listo</p>
        <h3 id="modalTitle" style="margin:0;">${producto.nombre}</h3>
        <button class="btn-download" id="btnDescargar">
          <span class="icono" aria-hidden="true">⬇</span>
          <span>Descargar ${producto.formato.includes('ZIP') ? 'ZIP' : 'archivo'}</span>
        </button>
        <p class="note">${producto.formato} · ${producto.peso}</p>
      </div>
    `;

    document.getElementById('btnDescargar').addEventListener('click', () => descargarArchivo(producto));
  }

  function descargarArchivo(producto) {
    // Descarga real: crea un link temporal y lo dispara.
    // producto.link_descarga viene de data/productos.json
    //
    // Nota: los navegadores no permiten forzar la descarga de enlaces
    // file:// (solo de http/https) por seguridad. En vista previa local
    // simplemente lo abrimos en una pestaña nueva.
    if (producto.link_descarga.startsWith('file://')) {
      window.open(producto.link_descarga, '_blank');
      return;
    }
    const a = document.createElement('a');
    a.href = producto.link_descarga;
    a.download = '';
    document.body.appendChild(a);
    a.click();
    a.remove();
  }

  return { mostrarPantallaEspera };
})();
