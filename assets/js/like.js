/* ============================================================
   "Me gusta" de un articulo.
   Se conecta a cualquier bloque .post-like que tenga data-post
   (identificador unico del articulo).

   Reglas:
   - Un visitante puede marcar, pero NO puede quitar el me gusta.
   - La marca se recuerda en localStorage, por articulo y por
     navegador: al volver, el boton ya aparece marcado.

   El conteo total solo se muestra si el bloque trae un atributo
   data-api con la URL de un endpoint. Sin endpoint, el me gusta
   es local y no se pinta ningun numero (mejor eso que un numero
   que solo ve quien lo marco). Ver README, seccion "Me gusta".
   ============================================================ */
(function () {
  var PREFIJO = 'like:';   // localStorage: 'like:<id-del-post>' = '1'

  function yaMarcado(clave) {
    try { return localStorage.getItem(clave) === '1'; } catch (e) { return false; }
  }

  function recordar(clave) {
    try { localStorage.setItem(clave, '1'); } catch (e) { /* modo privado: solo no recuerda */ }
  }

  function conectar(caja) {
    var id = caja.getAttribute('data-post');
    if (!id) return;

    var btn      = caja.querySelector('.like-btn');
    var gracias  = caja.querySelector('.like-done');
    var contador = caja.querySelector('.like-count');
    var api      = caja.getAttribute('data-api') || '';
    var clave    = PREFIJO + id;

    /* El total solo se pinta si hay al menos un me gusta:
       un "0" pegado al boton invita menos a marcarlo. */
    function pintarTotal(total) {
      if (!contador || typeof total !== 'number' || isNaN(total) || total < 1) return;
      contador.textContent = total;
      contador.hidden = false;
    }

    /* Estado marcado: ya no se puede volver atras */
    function marcar() {
      btn.classList.add('is-liked');
      btn.disabled = true;
      btn.setAttribute('aria-pressed', 'true');
      btn.setAttribute('title', 'Ya marcaste este articulo como me gusta');
      if (gracias) gracias.hidden = false;
    }

    function pedirTotal() {
      if (!api || !window.fetch) return;
      fetch(api + '?post=' + encodeURIComponent(id))
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) { if (d) pintarTotal(d.total); })
        .catch(function () { /* sin red: el boton sigue sirviendo en local */ });
    }

    function enviarTotal() {
      if (!api || !window.fetch) return;
      fetch(api, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ post: id })
      })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) { if (d) pintarTotal(d.total); })
        .catch(function () { /* el me gusta local ya quedo guardado */ });
    }

    if (yaMarcado(clave)) marcar();

    btn.addEventListener('click', function () {
      if (btn.disabled) return;
      recordar(clave);
      marcar();
      enviarTotal();
    });

    pedirTotal();
  }

  var cajas = document.querySelectorAll('.post-like[data-post]');
  for (var i = 0; i < cajas.length; i++) conectar(cajas[i]);
})();
