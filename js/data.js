/**
 * data.js
 * ---------------------------------------------------------
 * Único responsable de traer los datos de productos/categorías.
 * Si en el futuro cambias de un archivo JSON a una API real,
 * SOLO tienes que tocar este archivo.
 * ---------------------------------------------------------
 */

const Datos = (() => {
  let cache = null;

  async function cargar() {
    if (cache) return cache;
    const res = await fetch('data/productos.json');
    if (!res.ok) {
      throw new Error('No se pudo cargar data/productos.json');
    }
    cache = await res.json();
    return cache;
  }

  return { cargar };
})();
