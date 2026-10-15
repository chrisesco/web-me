/* ============================================================
   Christian Escobar Florez — lógica del sitio
   Depende de posts.js (POSTS y DRAFT_IDEAS), que se carga antes.
   Sirve igual para la portada y para las páginas de blog/:
   el prefijo de las rutas sale del atributo data-base del grid.
   ============================================================ */

/* Año del footer */
const elAnio = document.getElementById('year');
if (elAnio) elAnio.textContent = new Date().getFullYear();

/* Tarjeta de un post publicado */
function tarjetaPost(p, base) {
  return `
      <a href="${base}${p.url}" class="post-card is-published">
        <span class="soon mono">${p.tag} · ${p.date}</span>
        <h4>${p.title}</h4>
        <p>${p.excerpt}</p>
      </a>`;
}

/* Listado del blog en la portada */
function renderBlog() {
  const grid = document.getElementById('blog-grid');
  if (!grid) return;
  const emptyNote = document.getElementById('blog-empty-note');
  const base = grid.dataset.base || '';

  if (POSTS.length > 0) {
    grid.innerHTML = POSTS.map(p => tarjetaPost(p, base)).join('');
  } else {
    if (emptyNote) emptyNote.style.display = 'block';
    grid.innerHTML = DRAFT_IDEAS.map(d => `
      <div class="post-card">
        <span class="soon mono">Próximamente · ${d.tag}</span>
        <h4>${d.title}</h4>
        <p>Tema en borrador.</p>
      </div>
    `).join('');
  }
}

/* "Otros artículos" al final de cada post: los demás, hasta 3 */
function renderRelacionados() {
  const grid = document.getElementById('related-grid');
  if (!grid) return;
  const base = grid.dataset.base || '';
  const actual = grid.dataset.current || '';
  const otros = POSTS.filter(p => p.url !== actual).slice(0, 3);

  if (otros.length === 0) {
    grid.innerHTML = DRAFT_IDEAS.map(d => `
      <div class="post-card">
        <span class="soon mono">Próximamente · ${d.tag}</span>
        <h4>${d.title}</h4>
        <p>Tema en borrador.</p>
      </div>
    `).join('');
    return;
  }
  grid.innerHTML = otros.map(p => tarjetaPost(p, base)).join('');
}

/* Aparición progresiva al hacer scroll */
function initReveal() {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in'); });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
}

renderBlog();
renderRelacionados();
initReveal();
