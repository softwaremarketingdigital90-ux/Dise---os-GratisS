/**
 * ui.js
 * ---------------------------------------------------------
 * Todo lo que pinta cosas en pantalla: botones de categoría,
 * tarjetas del grid, y la ficha de producto dentro del modal.
 * No sabe nada de cómo se cargan los datos (eso es data.js)
 * ni de la lógica de descarga (eso es descarga.js).
 * ---------------------------------------------------------
 */

const UI = (() => {
  let categorias = [];
  let productos = [];
  let categoriaActiva = 'todos';
  let terminoBusqueda = '';

  const elGrid = () => document.getElementById('grid');
  const elCats = () => document.getElementById('cats');
  const elEmpty = () => document.getElementById('emptyState');

  function colorCategoria(idCategoria) {
    const cat = categorias.find(c => c.id === idCategoria);
    return cat ? cat.color : '#888';
  }

  function nombreCategoria(idCategoria) {
    const cat = categorias.find(c => c.id === idCategoria);
    return cat ? cat.nombre.toUpperCase() : idCategoria.toUpperCase();
  }

  function iniciales(nombre) {
    return nombre.split(' ').slice(0, 2).join(' ');
  }

  function renderStats() {
    document.getElementById('stat-total').textContent = productos.length;
    document.getElementById('stat-categorias').textContent = categorias.length;
  }

  function renderCategorias() {
    const cont = elCats();
    cont.innerHTML = '';

    const btnTodos = crearBotonCategoria('todos', 'Todos');
    cont.appendChild(btnTodos);

    categorias.forEach(cat => {
      cont.appendChild(crearBotonCategoria(cat.id, cat.nombre));
    });
  }

  function crearBotonCategoria(id, etiqueta) {
    const btn = document.createElement('button');
    btn.className = 'cat-btn' + (id === categoriaActiva ? ' active' : '');
    btn.textContent = etiqueta;
    btn.dataset.cat = id;
    btn.setAttribute('role', 'tab');
    btn.addEventListener('click', () => {
      categoriaActiva = id;
      renderCategorias();
      renderGrid();
    });
    return btn;
  }

  function coincideBusqueda(producto, termino) {
    if (!termino) return true;
    const t = termino.toLowerCase();
    return producto.nombre.toLowerCase().includes(t)
        || producto.descripcion.toLowerCase().includes(t)
        || nombreCategoria(producto.categoria).toLowerCase().includes(t);
  }

  function renderGrid() {
    const grid = elGrid();
    grid.innerHTML = '';

    const lista = productos.filter(p =>
      (categoriaActiva === 'todos' || p.categoria === categoriaActiva)
      && coincideBusqueda(p, terminoBusqueda)
    );

    elEmpty().hidden = lista.length > 0;
    elEmpty().textContent = terminoBusqueda
      ? `No hay diseños que coincidan con "${terminoBusqueda}".`
      : 'No hay diseños en esta categoría todavía.';

    lista.forEach(p => grid.appendChild(crearTarjeta(p)));
  }

  function crearTarjeta(producto) {
    const card = document.createElement('button');
    card.className = 'card';
    card.type = 'button';

    const thumbInterior = producto.thumb
      ? `<img src="${producto.thumb}" alt="" loading="lazy" style="width:100%;height:100%;object-fit:cover;">`
      : iniciales(producto.nombre);

    const thumbFondo = producto.thumb
      ? ''
      : `background:linear-gradient(135deg, ${colorCategoria(producto.categoria)}cc, ${colorCategoria(producto.categoria)}55)`;

    card.innerHTML = `
      <span class="card-thumb" style="${thumbFondo}">
        <span class="tag">${nombreCategoria(producto.categoria)}</span>
        ${thumbInterior}
      </span>
      <span class="card-info">
        <span class="name">${producto.nombre}</span>
        <span class="meta"><span>${producto.formato}</span><span>${producto.peso}</span></span>
      </span>
    `;
    card.addEventListener('click', () => abrirFichaProducto(producto));
    return card;
  }

  function abrirFichaProducto(producto) {
    document.getElementById('modalCatLabel').textContent = nombreCategoria(producto.categoria);
    const thumbGrande = producto.thumb
      ? `<img src="${producto.thumb}" alt="" style="width:100%;height:100%;object-fit:cover;">`
      : iniciales(producto.nombre);
    const fondoGrande = producto.thumb
      ? ''
      : `background:linear-gradient(135deg, ${colorCategoria(producto.categoria)}cc, ${colorCategoria(producto.categoria)}55)`;
    document.getElementById('modalBody').innerHTML = `
      <div class="modal-thumb" style="${fondoGrande}">
        ${thumbGrande}
      </div>
      <h3 id="modalTitle">${producto.nombre}</h3>
      <p class="desc">${producto.descripcion}</p>
      <div class="specs">
        <div class="spec"><b>${producto.formato}</b>contenido</div>
        <div class="spec"><b>${producto.peso}</b>peso del ZIP</div>
        <div class="spec"><b>Instantánea</b>entrega</div>
      </div>
      <button class="btn-primary" id="btnVerDescarga">Ver descarga</button>
    `;
    document.getElementById('btnVerDescarga').addEventListener('click', () => {
      Descarga.mostrarPantallaEspera(producto);
    });
    abrirModal();
  }

  function abrirModal() {
    document.getElementById('overlay').classList.add('show');
  }

  function cerrarModal() {
    document.getElementById('overlay').classList.remove('show');
  }

  async function iniciar() {
    const datos = await Datos.cargar();
    categorias = datos.categorias;
    productos = datos.productos;

    renderStats();
    renderCategorias();
    renderGrid();

    document.getElementById('btnCerrarModal').addEventListener('click', cerrarModal);
    document.getElementById('overlay').addEventListener('click', (e) => {
      if (e.target.id === 'overlay') cerrarModal();
    });

    const inputBuscador = document.getElementById('buscador');
    let temporizador = null;
    inputBuscador.addEventListener('input', (e) => {
      clearTimeout(temporizador);
      const valor = e.target.value;
      temporizador = setTimeout(() => {
        terminoBusqueda = valor.trim();
        renderGrid();
      }, 150);
    });
  }

  return { iniciar, cerrarModal, nombreCategoria, colorCategoria };
})();
