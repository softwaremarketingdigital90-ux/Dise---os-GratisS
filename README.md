# VectorGarage — Sitio de descargas

## Estructura del proyecto

```
vectorgarage/
├── index.html              → Estructura de la página (no lleva contenido de productos)
├── css/
│   ├── variables.css       → Colores, tipografías, radios (edita aquí el estilo global)
│   ├── base.css            → Reset y estilos base
│   ├── layout.css          → Header, hero, secciones
│   └── componentes.css     → Tarjetas, botones, modal, pantalla de descarga
├── js/
│   ├── data.js             → Carga data/productos.json
│   ├── ui.js                → Pinta categorías, tarjetas y ficha de producto
│   ├── descarga.js          → Pantalla de espera, anuncios, timer y descarga real
│   └── main.js              → Arranca la app
├── assets/
│   └── previews/            → PNG de vitrina (con marca de agua), generados con
│                               generar_previews.py. Se suben junto con el sitio
│                               (a GitHub, Netlify, etc.) porque son livianos.
└── data/
    └── productos.json       → TUS PRODUCTOS. Este es el único archivo que
                                necesitas editar para agregar diseños nuevos.
```

## Dónde vive cada tipo de archivo

Esta web separa dos cosas que NO deben ir en el mismo lugar:

- **Previews (PNG livianos, con marca de agua)** → viven DENTRO del proyecto,
  en `assets/previews/`. Se suben junto con el resto del sitio (mismo repo
  de GitHub, mismo hosting). Son ligeros porque ya vienen optimizados.
- **Archivo real de descarga (ZIP con SVG + PNG en alta calidad)** → vive
  en un servicio externo pensado para archivos pesados (GitHub Releases,
  Cloudflare R2, etc.), NO dentro de este proyecto. Solo guardas el link
  en `link_descarga` dentro de `productos.json`.

Así el sitio en sí pesa poco y carga rápido (solo trae las miniaturas),
mientras que los archivos grandes viven donde corresponde.

## Cómo agregar un producto nuevo

Abre `data/productos.json` y agrega un bloque como este dentro de la lista
`"productos"`:

```json
{
  "id": 9,
  "categoria": "moto",
  "nombre": "Nombre de tu diseño",
  "formato": "SVG + 5 PNG",
  "peso": "10.2 MB",
  "descripcion": "Descripción corta del diseño.",
  "thumb": "assets/previews/nombre-de-tu-diseno.png",
  "link_descarga": "https://tu-bucket.r2.dev/carpeta/archivo.zip"
}
```

- `id`: un número que no se repita
- `categoria`: debe coincidir con uno de los ids en `"categorias"` (`moto`, `dtf`, `temas`)
- `thumb`: ruta LOCAL dentro del proyecto (el PNG debe estar copiado en `assets/previews/`)
- `link_descarga`: la URL directa al ZIP, en un hosting externo (GitHub Releases, R2, MediaFire, etc.)

No necesitas tocar HTML, CSS ni JS para esto. La página se actualiza sola al
leer el JSON.

## Cómo agregar una categoría nueva

En el mismo archivo, agrega un bloque dentro de `"categorias"`:

```json
{ "id": "cascos", "nombre": "Cascos", "color": "#ffb020" }
```

El botón de filtro y el color de las tarjetas aparecen automáticamente.

## Conectar AdSense

1. Pega el script que te da Google AdSense dentro de `<head>` en `index.html`
   (ya hay un comentario marcando dónde va).
2. En `js/descarga.js`, dentro de `mostrarPantallaEspera`, reemplaza los
   `<div class="ad-slot">...</div>` por el bloque `<ins class="adsbygoogle">`
   que te da AdSense para cada ubicación de anuncio.

## Conectar Outpush

Pega el script de suscripción que te da tu cuenta de Outpush dentro de
`<head>` en `index.html` (también está comentado dónde va).

## Publicar el sitio

Es un sitio 100% estático (HTML/CSS/JS puro, sin backend). Puedes subir esta
carpeta completa a:

- Netlify (arrastrar y soltar la carpeta)
- Vercel
- GitHub Pages
- Cualquier hosting compartido normal (subes por FTP)

No necesitas configurar nada especial de servidor.

## Próximos pasos técnicos pendientes

- Conectar `link_descarga` de cada producto con los archivos reales subidos
  a Cloudflare R2 (o el proveedor que elijas).
- Generar `data/productos.json` automáticamente desde un script cuando subas
  los 40,000+ diseños en lote, en vez de escribirlo a mano.
