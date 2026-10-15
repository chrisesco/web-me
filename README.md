# Datapsulas

Sitio y blog sobre SAP, Databricks e Inteligencia Artificial — y sobre lo que
aparece cuando se unen los tres. Escrito por Christian Escobar Florez.

Sitio estático: HTML, CSS y JavaScript sin dependencias ni paso de build.

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
