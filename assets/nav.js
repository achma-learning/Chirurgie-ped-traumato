/*
 * Chirurgie pédiatrique — nav.js
 * Self-contained floating toggle + drawer for quick access to every
 * cas clinique from any page. Drop one <script src=".../assets/nav.js">
 * before </body> on any page; everything else is auto-injected.
 */
(function () {
  if (window.__cpNavLoaded) return;
  window.__cpNavLoaded = true;

  // --- Resolve base path back to the repo root --------------------------------
  // The site lives under <root>/FRACTURES MI/... and <root>/FRACTURES MS/...
  // We walk the URL pathname to count how many ".." we need to reach root.
  function computeBase() {
    var path = decodeURIComponent(window.location.pathname || "");
    var marker = path.match(/FRACTURES M[IS]\//);
    if (!marker) return "";
    var tail = path.substring(path.indexOf(marker[0]));
    var depth = tail.split("/").length - 1; // segments after the FRACTURES dir
    return new Array(depth + 1).join("../");
  }
  var BASE = computeBase();

  // --- Catalog ----------------------------------------------------------------
  // Mirrors the official casclinique.html in each folder. Numbers shown match
  // the printed Cas clinique number; "file" is the actual file on disk.
  var CATALOG = {
    ms: {
      title: "Membre supérieur",
      folder: "FRACTURES MS",
      accent: "#2563eb",
      groups: [
        { label: "Épaule",     cases: [["1","cas1.html"],["2","cas2.html"],["3","cas3.html"],["4","cas4.html"],["5","cas5.html"]] },
        { label: "Bras",       cases: [["1","cas6.html"]] },
        { label: "Coude",      cases: [["1","cas7.html"],["2","cas8.html"],["3","cas10.html"],["4","cas11.html"],["5","cas12.html"],["6","cas13.html"],["7","cas14.html"],["8","cas15.html"],["9","cas16.html"],["10","cas20.html"],["11","cas21.html"],["12","cas17.html"],["13","cas23.html"],["14","cas18.html"],["15","cas19.html"],["16","cas24.html"],["17","cas25.html"]] },
        { label: "Avant-bras", cases: [["1","cas26.html"],["2","cas27.html"],["3","cas28.html"]] },
        { label: "Poignet",    cases: [["1","cas29.html"],["2","cas30.html"]] }
      ]
    },
    mi: {
      title: "Membre inférieur",
      folder: "FRACTURES MI",
      accent: "#16a34a",
      groups: [
        { label: "Bassin",   cases: [["1","cas1.html"],["2","cas2.html"]] },
        { label: "Hanche",   cases: [["3","cas3.html"],["4","cas4.html"],["5","cas5.html"],["6","cas6.html"]] },
        { label: "Cuisse",   cases: [["7","cas7.html"],["8","cas8.html"],["9","cas0.html"]] },
        { label: "Genou",    cases: [["10","cas9.html"],["11","cas10.html"],["12","cas11.html"],["13","cas12.html"],["14","cas13.html"],["15","cas14.html"]] },
        { label: "Jambe",    cases: [["16","cas15.html"],["17","cas16.html"],["18","cas17.html"],["19","cas18.html"]] },
        { label: "Cheville", cases: [["20","cas19.html"],["21","cas20.html"],["22","cas21.html"],["23","cas22.html"]] }
      ]
    }
  };

  function caseUrl(book, file) { return BASE + book.folder + "/cas_clinique/" + file; }
  function homeUrl(book)       { return BASE + book.folder + "/" + (book === CATALOG.mi ? "index.htm" : "index.html"); }
  function rootUrl()            { return BASE + "index.html"; }

  // --- Styles -----------------------------------------------------------------
  var css = ''
    + '.cpnav-btn{position:fixed;top:14px;right:14px;z-index:99998;'
    + 'background:#111827;color:#fff;border:0;border-radius:999px;'
    + 'padding:10px 16px;font:600 14px/1 -apple-system,Segoe UI,Roboto,sans-serif;'
    + 'box-shadow:0 6px 20px rgba(0,0,0,.25);cursor:pointer;letter-spacing:.02em;'
    + 'transition:transform .15s ease,background .15s ease}'
    + '.cpnav-btn:hover{background:#1f2937;transform:translateY(-1px)}'
    + '.cpnav-btn:focus{outline:2px solid #60a5fa;outline-offset:2px}'
    + '.cpnav-overlay{position:fixed;inset:0;background:rgba(15,23,42,.55);'
    + 'opacity:0;visibility:hidden;transition:opacity .2s ease,visibility .2s;z-index:99998}'
    + '.cpnav-overlay.open{opacity:1;visibility:visible}'
    + '.cpnav-panel{position:fixed;top:0;right:0;height:100%;width:min(420px,92vw);'
    + 'background:#fff;color:#0f172a;z-index:99999;transform:translateX(100%);'
    + 'transition:transform .25s cubic-bezier(.2,.7,.2,1);box-shadow:-12px 0 40px rgba(0,0,0,.25);'
    + 'display:flex;flex-direction:column;font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}'
    + '.cpnav-panel.open{transform:translateX(0)}'
    + '.cpnav-head{padding:18px 20px;border-bottom:1px solid #e5e7eb;'
    + 'display:flex;align-items:center;justify-content:space-between;gap:8px}'
    + '.cpnav-head h2{margin:0;font:700 16px/1.2 -apple-system,Segoe UI,Roboto,sans-serif;color:#0f172a}'
    + '.cpnav-head a.cpnav-home{font-size:12px;color:#475569;text-decoration:none;border:1px solid #e5e7eb;border-radius:6px;padding:4px 8px}'
    + '.cpnav-head a.cpnav-home:hover{background:#f1f5f9;color:#0f172a}'
    + '.cpnav-close{background:transparent;border:0;font-size:22px;cursor:pointer;color:#64748b;line-height:1;padding:4px 8px}'
    + '.cpnav-close:hover{color:#0f172a}'
    + '.cpnav-search{padding:10px 20px;border-bottom:1px solid #e5e7eb;background:#fafafa}'
    + '.cpnav-search input{width:100%;padding:8px 10px;border:1px solid #d1d5db;border-radius:6px;font-size:13px;outline:none}'
    + '.cpnav-search input:focus{border-color:#2563eb;box-shadow:0 0 0 3px rgba(37,99,235,.15)}'
    + '.cpnav-body{overflow:auto;padding:8px 0 24px;flex:1}'
    + '.cpnav-book{padding:14px 20px 4px}'
    + '.cpnav-book h3{margin:0 0 6px;font:700 13px/1.2 -apple-system,Segoe UI,Roboto,sans-serif;'
    + 'text-transform:uppercase;letter-spacing:.06em;color:var(--c,#111827)}'
    + '.cpnav-book h3 a{color:inherit;text-decoration:none;border-bottom:1px dashed currentColor}'
    + '.cpnav-grp{margin:8px 0}'
    + '.cpnav-grp>summary{cursor:pointer;list-style:none;padding:6px 8px;border-radius:6px;'
    + 'font-weight:600;color:#0f172a;display:flex;justify-content:space-between;align-items:center}'
    + '.cpnav-grp>summary::-webkit-details-marker{display:none}'
    + '.cpnav-grp>summary:hover{background:#f1f5f9}'
    + '.cpnav-grp>summary .cpnav-count{font-weight:500;font-size:12px;color:#64748b;background:#e5e7eb;'
    + 'border-radius:999px;padding:1px 8px;margin-left:8px}'
    + '.cpnav-grp[open]>summary{background:#f8fafc}'
    + '.cpnav-cases{list-style:none;margin:4px 0 8px;padding:0 0 0 18px;'
    + 'border-left:2px solid #e5e7eb}'
    + '.cpnav-cases li{margin:0}'
    + '.cpnav-cases a{display:block;padding:5px 10px;color:#1e293b;text-decoration:none;'
    + 'border-radius:5px;font-size:13px}'
    + '.cpnav-cases a:hover{background:var(--c,#111827);color:#fff}'
    + '.cpnav-cases a.cpnav-current{background:#fde68a;color:#0f172a;font-weight:600}'
    + '.cpnav-empty{padding:20px;color:#64748b;font-style:italic;text-align:center}'
    + '@media print{.cpnav-btn,.cpnav-panel,.cpnav-overlay{display:none!important}}';

  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  // --- Build DOM --------------------------------------------------------------
  var btn = document.createElement('button');
  btn.className = 'cpnav-btn';
  btn.type = 'button';
  btn.setAttribute('aria-label', 'Ouvrir le menu des cas cliniques');
  btn.innerHTML = '☰ Cas cliniques';

  var overlay = document.createElement('div');
  overlay.className = 'cpnav-overlay';

  var panel = document.createElement('aside');
  panel.className = 'cpnav-panel';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-label', 'Navigation cas cliniques');

  var head = document.createElement('div');
  head.className = 'cpnav-head';
  head.innerHTML = '<h2>Cas cliniques</h2>'
    + '<div style="display:flex;gap:8px;align-items:center">'
    + '<a class="cpnav-home" href="' + rootUrl() + '">Accueil</a>'
    + '<button class="cpnav-close" type="button" aria-label="Fermer">&times;</button>'
    + '</div>';
  panel.appendChild(head);

  var search = document.createElement('div');
  search.className = 'cpnav-search';
  search.innerHTML = '<input type="search" placeholder="Filtrer (ex: coude, genou, 14)" autocomplete="off" />';
  panel.appendChild(search);

  var body = document.createElement('div');
  body.className = 'cpnav-body';

  var currentHref = decodeURIComponent(window.location.pathname).split('/').pop();

  function renderBook(key) {
    var book = CATALOG[key];
    var section = document.createElement('section');
    section.className = 'cpnav-book';
    section.style.setProperty('--c', book.accent);
    var h = document.createElement('h3');
    h.innerHTML = '<a href="' + homeUrl(book) + '">' + book.title + '</a>';
    section.appendChild(h);
    book.groups.forEach(function (g) {
      var det = document.createElement('details');
      det.className = 'cpnav-grp';
      det.open = false;
      var sum = document.createElement('summary');
      sum.innerHTML = '<span>' + g.label + '</span><span class="cpnav-count">' + g.cases.length + '</span>';
      det.appendChild(sum);
      var ul = document.createElement('ul');
      ul.className = 'cpnav-cases';
      g.cases.forEach(function (c) {
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.href = caseUrl(book, c[1]);
        a.textContent = 'Cas clinique ' + c[0];
        a.dataset.search = (book.title + ' ' + g.label + ' cas clinique ' + c[0]).toLowerCase();
        if (c[1] === currentHref) a.className = 'cpnav-current';
        li.appendChild(a);
        ul.appendChild(li);
        // open the group if it contains the current page
        if (c[1] === currentHref) det.open = true;
      });
      det.appendChild(ul);
      section.appendChild(det);
    });
    body.appendChild(section);
  }
  renderBook('ms');
  renderBook('mi');
  panel.appendChild(body);

  // --- Behavior ---------------------------------------------------------------
  function open()  { overlay.classList.add('open'); panel.classList.add('open'); var i = search.querySelector('input'); if (i) setTimeout(function(){ i.focus(); }, 100); }
  function close() { overlay.classList.remove('open'); panel.classList.remove('open'); }

  btn.addEventListener('click', open);
  overlay.addEventListener('click', close);
  head.querySelector('.cpnav-close').addEventListener('click', close);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });

  // Filter
  search.querySelector('input').addEventListener('input', function (e) {
    var q = e.target.value.trim().toLowerCase();
    var groups = body.querySelectorAll('.cpnav-grp');
    groups.forEach(function (g) {
      var any = false;
      g.querySelectorAll('.cpnav-cases a').forEach(function (a) {
        var match = !q || a.dataset.search.indexOf(q) !== -1;
        a.parentNode.style.display = match ? '' : 'none';
        if (match) any = true;
      });
      g.style.display = any ? '' : 'none';
      if (q) g.open = any;
    });
  });

  // Mount when DOM is ready
  function mount() {
    if (!document.body) return setTimeout(mount, 30);
    document.body.appendChild(btn);
    document.body.appendChild(overlay);
    document.body.appendChild(panel);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
})();
