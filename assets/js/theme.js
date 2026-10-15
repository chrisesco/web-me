/* ============================================================
   Modo claro / oscuro
   Se carga en el <head> de forma sincrona, ANTES de que se pinte
   la pagina: asi el tema guardado se aplica sin un destello blanco.
   ============================================================ */
(function () {
  var KEY = 'tema';           // 'light' | 'dark' | ausente = seguir al sistema
  var root = document.documentElement;

  function guardado() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function sistemaEsOscuro() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  function temaActual() {
    return guardado() || (sistemaEsOscuro() ? 'dark' : 'light');
  }

  function aplicar(tema) {
    root.setAttribute('data-theme', tema);
  }

  /* 1. Aplicar cuanto antes */
  aplicar(temaActual());

  /* 2. Si el visitante no ha elegido nada, seguir al sistema en vivo */
  if (window.matchMedia) {
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    var alCambiarSistema = function (e) {
      if (!guardado()) aplicar(e.matches ? 'dark' : 'light');
    };
    if (mq.addEventListener) mq.addEventListener('change', alCambiarSistema);
    else if (mq.addListener) mq.addListener(alCambiarSistema);
  }

  /* 3. Conectar el boton cuando exista el DOM */
  function conectarBoton() {
    var btn = document.getElementById('theme-toggle');
    if (!btn) return;

    function etiquetar() {
      var oscuro = root.getAttribute('data-theme') === 'dark';
      var texto = oscuro ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro';
      btn.setAttribute('aria-label', texto);
      btn.setAttribute('title', texto);
    }

    btn.addEventListener('click', function () {
      var nuevo = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      aplicar(nuevo);
      try { localStorage.setItem(KEY, nuevo); } catch (e) { /* modo privado: solo no recuerda */ }
      etiquetar();
    });

    etiquetar();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', conectarBoton);
  } else {
    conectarBoton();
  }
})();
