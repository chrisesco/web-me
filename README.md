# Datapsulas

Sitio y blog sobre SAP, Databricks e Inteligencia Artificial — y sobre lo que
aparece cuando se unen los tres. Escrito por Christian Escobar Florez.

Sitio estático: HTML, CSS y JavaScript sin dependencias ni paso de build.
La única pieza de servidor es `api/like.js`, la función del contador de
me gusta, que corre como función serverless en Vercel.

## Estructura

```
index.html                  Portada
blog/                       Un archivo HTML por artículo
assets/
  css/styles.css            Estilos del sitio + tokens de tema (claro/oscuro)
  css/post.css              Estilos de artículo (solo se carga en blog/)
  js/theme.js               Modo claro/oscuro (se carga en el <head>)
  js/posts.js               Índice de artículos — el único archivo a editar para publicar
  js/main.js                Render del blog, artículos relacionados y animaciones
  img/                      Imágenes
  docs/                     PDFs descargables
api/like.js                 Contador de me gusta (función serverless de Vercel)
tools/generar_pdf.py        Genera el PDF imprimible del artículo
```

## Publicar un artículo

1. Crear el HTML dentro de `blog/`, tomando como base un artículo existente.
2. Agregar su objeto **al inicio** del array `POSTS` en `assets/js/posts.js`:

```js
{
  title: "Título del artículo",
  excerpt: "Una o dos frases de resumen.",
  date: "Oct 2026",
  url: "blog/mi-articulo.html",   // ruta desde la raíz del sitio
  tag: "SAP",
}
```

La portada y el bloque "Otros artículos" se actualizan solos. Si `POSTS` queda
vacío, se muestran las ideas de `DRAFT_IDEAS` como "Próximamente".

## Ver el sitio en local

Abrir `index.html` con doble clic. No hace falta servidor: los scripts son
clásicos (no módulos ES) justamente para que funcione desde el sistema de
archivos.

## Temas

Los colores salen de variables CSS en `:root` (modo claro) y
`:root[data-theme="dark"]` (modo oscuro), al inicio de `assets/css/styles.css`.
Para ajustar la paleta no hay que tocar ninguna otra regla.

## Me gusta de los artículos

Cada artículo puede llevar al final un botón de me gusta. El HTML es un bloque
`.post-like` con el identificador del artículo, y el script `assets/js/like.js`
se encarga del resto:

```html
<div class="post-like" data-post="mi-articulo">
  ...
</div>
<script src="../assets/js/like.js"></script>
```

Reglas: se puede marcar, no se puede quitar. La marca queda en `localStorage`
con la clave `like:<data-post>`, así que al volver a la página el botón ya
aparece marcado.

**Sobre el conteo y los likes repetidos.** Si el bloque no trae `data-api`,
el me gusta vive solo en el navegador del visitante: eso evita que la misma
persona marque dos veces en ese navegador, pero no hay total compartido y no se
muestra ningún número. Con `data-api` entra a jugar `api/like.js`, que además
bloquea el segundo like aunque el visitante borre los datos del sitio:

```html
<div class="post-like" data-post="mi-articulo" data-api="/api/like">
```

`like.js` hace `GET /api/like?post=<id>` al cargar y `POST /api/like` con
`{"post":"<id>"}` al marcar; las dos respuestas traen `{"total": 12}`. El total
solo se pinta si es mayor que cero. Si el endpoint no responde, el botón sigue
funcionando en modo local.

### Montar el contador en Vercel

1. En el proyecto de Vercel: **Storage → Create Database → Upstash Redis**, y
   conectarla al proyecto. Eso crea solas las variables `KV_REST_API_URL` y
   `KV_REST_API_TOKEN` (también sirven los nombres `UPSTASH_REDIS_REST_URL` y
   `UPSTASH_REDIS_REST_TOKEN`).
2. Agregar a mano una variable más, **`LIKE_SALT`**, con una cadena aleatoria
   larga (`openssl rand -hex 32`). Es la sal del hash de la IP: si cambia,
   los visitantes que ya marcaron pueden volver a marcar.
3. Volver a desplegar. No hay `package.json` ni dependencias: la función usa
   `fetch` y `crypto` de Node.

Cómo funciona el bloqueo: por cada artículo hay un set de Redis `likes:<id>`
cuyos miembros son `sha256(IP + LIKE_SALT + id)` recortado. `SADD` devuelve 0
si esa huella ya estaba, y `SCARD` da el total. **Nunca se guarda la IP en
claro** — una IP es un dato personal, y así lo almacenado no permite
reconstruirla.

Lo que este esquema no resuelve: varias personas detrás de la misma IP (una
oficina con NAT) comparten huella, así que solo cuenta el primer me gusta; y
alguien decidido puede marcar de nuevo desde otra red o con datos móviles.
Cerrar eso del todo exige pedir login, que para un botón de me gusta cuesta
más de lo que vale.

### Probar en local

`api/like.js` no corre al abrir el HTML con doble clic. Para probarlo hace
falta `vercel dev` (CLI de Vercel) con las variables de entorno puestas, o
desplegar a una preview. Sin endpoint, el botón se comporta en modo local.

## El PDF imprimible

`assets/docs/Guia_Conexion_Datasphere_Informix_Publica.pdf` no se edita a mano:
se genera con `tools/generar_pdf.py`, que tiene el contenido de la guía y los
estilos (A4, Helvetica, Courier para el código, azul #0a4a8c en los títulos).

```
pip install reportlab pillow
python tools/generar_pdf.py
```

Cuando cambie el artículo, se edita el script y se vuelve a generar, para que
el PDF y la página digan lo mismo.
