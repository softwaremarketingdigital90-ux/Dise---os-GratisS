/**
 * descarga.js
 * ---------------------------------------------------------
 * Pantalla de "espera" antes de descargar: aquí van los
 * espacios de anuncios (AdSense) y el aviso de suscripción
 * push (Outpush). Cuando tengas tus scripts reales, este es
 * el único archivo que necesitas tocar para conectar los
 * anuncios de verdad (reemplaza los <div class="ad-slot">
 * por tus bloques <ins class="adsbygoogle">).
 * ---------------------------------------------------------
 */

const Descarga = (() => {
  const SEGUNDOS_ESPERA = 5;

  function mostrarPantallaEspera(producto) {
    document.getElementById('modalCatLabel').textContent = 'DESCARGA';

    document.getElementById('modalBody').innerHTML = `
      <div class="wait-screen">
        <div class="ad-slot large">ESPACIO ANUNCIO — TOP (AdSense)</div>
        <p style="font-size:14px;color:var(--texto-tenue);margin:0 0 4px;">Preparando tu descarga de</p>
        <h3 id="modalTitle" style="margin:0 0 14px;">${producto.nombre}</h3>
        <div class="ad-slot small">ESPACIO ANUNCIO — INLINE 1</div>
        <div class="ad-slot small">ESPACIO ANUNCIO — INLINE 2</div>
        <div class="timer-row">
          <div class="timer-circle" id="timerCircle">${SEGUNDOS_ESPERA}</div>
          <div class="timer-text">El botón de descarga se habilita en unos segundos</div>
        </div>
        <button class="btn-primary" id="btnDescargar" disabled>Descargar ZIP</button>
        <p class="note">Al descargar aceptas recibir notificaciones con nuevos diseños</p>
      </div>
    `;

    iniciarTimer(producto);
  }

  function iniciarTimer(producto) {
    let restante = SEGUNDOS_ESPERA;
    const circulo = document.getElementById('timerCircle');
    const boton = document.getElementById('btnDescargar');

    const intervalo = setInterval(() => {
      restante--;
      if (restante <= 0) {
        clearInterval(intervalo);
        circulo.textContent = '✓';
        circulo.style.animation = 'none';
        circulo.style.borderColor = 'var(--neon)';
        circulo.style.color = 'var(--neon)';
        boton.disabled = false;
        boton.addEventListener('click', () => descargarArchivo(producto));
      } else {
        circulo.textContent = restante;
      }
    }, 1000);
  }

  function descargarArchivo(producto) {
    // Descarga real: crea un link temporal y lo dispara.
    // producto.link_descarga viene de data/productos.json
    // (reemplázalo por tu URL real de Cloudflare R2 / MediaFire / etc.)
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
