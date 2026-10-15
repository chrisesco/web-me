/* ============================================================
   /api/like — contador de "me gusta" de los articulos.

   Funcion serverless de Vercel, sin dependencias: habla con
   Upstash Redis por su API REST (fetch nativo de Node 18+).

   GET  /api/like?post=<id>   -> { post, total }
   POST /api/like  {"post":"<id>"}  -> { post, total, nuevo }

   Por cada articulo se guarda UN set de Redis: likes:<id>.
   Cada miembro del set es la huella de un visitante, asi que
   SADD sirve a la vez para contar (SCARD) y para no contar dos
   veces a la misma persona.

   La huella es sha256(IP + LIKE_SALT + id del post), recortada.
   Nunca se guarda la IP en claro: una IP es un dato personal, y
   asi lo que queda en Redis no permite reconstruirla.

   Variables de entorno (ver README):
     KV_REST_API_URL   / UPSTASH_REDIS_REST_URL
     KV_REST_API_TOKEN / UPSTASH_REDIS_REST_TOKEN
     LIKE_SALT         cadena aleatoria larga
   ============================================================ */

const crypto = require('crypto');

const REDIS_URL   = process.env.KV_REST_API_URL   || process.env.UPSTASH_REDIS_REST_URL   || '';
const REDIS_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN || '';
const SAL         = process.env.LIKE_SALT || '';

/* El id del post va dentro de la clave de Redis: se acota a lo que
   usan los nombres de archivo del blog, nada de claves arbitrarias. */
const ID_VALIDO = /^[a-z0-9][a-z0-9-]{0,79}$/;

/* Pipeline de Upstash: varios comandos en una sola ida y vuelta.
   Devuelve los resultados en el mismo orden. */
async function redis(comandos) {
  const r = await fetch(REDIS_URL.replace(/\/+$/, '') + '/pipeline', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + REDIS_TOKEN,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(comandos),
  });
  if (!r.ok) throw new Error('Upstash respondio ' + r.status);
  const datos = await r.json();
  return datos.map(function (d) { return d.result; });
}

function huella(req, post) {
  var reenviada = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  var ip = reenviada || String(req.headers['x-real-ip'] || '');
  return crypto.createHash('sha256').update(ip + '|' + SAL + '|' + post).digest('hex').slice(0, 32);
}

function cuerpo(req) {
  if (typeof req.body === 'string') {
    try { return JSON.parse(req.body); } catch (e) { return {}; }
  }
  return req.body || {};
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (req.method !== 'GET' && req.method !== 'POST') {
    res.setHeader('Allow', 'GET, POST');
    return res.status(405).json({ error: 'metodo no permitido' });
  }

  var post = String((req.method === 'POST' ? cuerpo(req).post : (req.query || {}).post) || '');
  if (!ID_VALIDO.test(post)) {
    return res.status(400).json({ error: 'identificador de post invalido' });
  }
  if (!REDIS_URL || !REDIS_TOKEN) {
    /* Sin almacen configurado el boton sigue funcionando en local:
       like.js ignora la respuesta y solo deja de mostrar el total. */
    return res.status(503).json({ error: 'almacen no configurado' });
  }

  var clave = 'likes:' + post;

  try {
    if (req.method === 'GET') {
      var leido = await redis([['SCARD', clave]]);
      return res.status(200).json({ post: post, total: Number(leido[0]) || 0 });
    }

    var escrito = await redis([
      ['SADD', clave, huella(req, post)],
      ['SCARD', clave],
    ]);
    return res.status(200).json({
      post: post,
      total: Number(escrito[1]) || 0,
      nuevo: Number(escrito[0]) === 1,   // 0 = esa huella ya habia marcado
    });
  } catch (e) {
    return res.status(502).json({ error: 'no se pudo leer el contador' });
  }
};
