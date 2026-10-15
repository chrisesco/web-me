/* ============================================================
   ZONA DE BLOG — edita este archivo para publicar articulos.
   No hay que tocar el HTML ni el CSS.

   Cada post es un objeto con:
     title    -> titulo del articulo
     excerpt  -> 1-2 frases de resumen
     date     -> texto libre, ej. "Oct 2026"
     url      -> ruta DESDE LA RAIZ del sitio, ej. "blog/mi-post.html"
                 (cada pagina ajusta sola el prefijo ../ si hace falta)
     tag      -> etiqueta corta, ej. "SAP" o "Databricks"

   Para publicar: se crea el HTML dentro de blog/ y se agrega
   su objeto AL INICIO de este array (el mas reciente primero).

   Si POSTS esta vacio, se muestran las tarjetas de DRAFT_IDEAS
   como "Proximamente".
   ============================================================ */

const POSTS = [
  {
    title: "Cómo conectar Informix IBM a SAP Datasphere con una conexión Generic JDBC",
    excerpt: "Informix no tiene conector nativo en Datasphere. La ruta real pasa por el DP Agent, el adaptador CamelJdbcAdapter y una dependencia que casi nadie menciona.",
    date: "Oct 2026",
    url: "blog/informix-sap-datasphere-generic-jdbc.html",
    tag: "SAP",
  },
];

const DRAFT_IDEAS = [
  { tag: "SAP", title: "ACDOCA explicado para ingenieros de datos" },
  { tag: "Databricks", title: "Arquitectura medallion desde cero" },
  { tag: "SAP × Databricks", title: "Cuándo usar cada plataforma" },
];
