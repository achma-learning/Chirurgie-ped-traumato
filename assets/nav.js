/*
 * Chirurgie pédiatrique — nav.js
 * Permanent, always-visible MkDocs-style left sidebar for the whole site.
 * Drop one <script src=".../assets/nav.js"></script> before </body> on any page;
 * the sidebar, the content offset and the mobile toggle are all auto-injected.
 *
 * - Desktop (>= 1240px): sidebar is fixed & permanent, page content is shifted right.
 * - Narrow screens      : sidebar is off-canvas, opened by a ☰ toggle (like MkDocs).
 * - The current page is highlighted, its section expanded and scrolled into view.
 * - Book-aware highlighting (cas1.html exists in both books) via full-path match.
 */
(function () {
  if (window.__cpNavLoaded) return;
  window.__cpNavLoaded = true;

  // --- Resolve base path back to the repo root --------------------------------
  function computeBase() {
    var path = decodeURIComponent(window.location.pathname || "");
    var marker = path.match(/FRACTURES M[IS]\//);
    if (!marker) return null; // we are at the repository root -> no sidebar here
    var tail = path.substring(path.indexOf(marker[0]));
    var depth = tail.split("/").length - 1;
    return new Array(depth + 1).join("../");
  }
  var BASE = computeBase();
  if (BASE === null) return; // keep the custom landing page (index.html) untouched

  // --- Catalog (mirrors casclinique.html; numbers = printed Cas clinique n°) ---
  var CATALOG = {
    ms: {
      title: "Membre supérieur", folder: "FRACTURES MS", home: "index.html", accent: "#2563eb",
      groups: [
        { label: "Épaule",     cases: [["1","cas1.html"],["2","cas2.html"],["3","cas3.html"],["4","cas4.html"],["5","cas5.html"]] },
        { label: "Bras",       cases: [["1","cas6.html"]] },
        { label: "Coude",      cases: [["1","cas7.html"],["2","cas8.html"],["3","cas10.html"],["4","cas11.html"],["5","cas12.html"],["6","cas13.html"],["7","cas14.html"],["8","cas15.html"],["9","cas16.html"],["10","cas20.html"],["11","cas21.html"],["12","cas17.html"],["13","cas23.html"],["14","cas18.html"],["15","cas19.html"],["16","cas24.html"],["17","cas25.html"]] },
        { label: "Avant-bras", cases: [["1","cas26.html"],["2","cas27.html"],["3","cas28.html"]] },
        { label: "Poignet",    cases: [["1","cas29.html"],["2","cas30.html"]] }
      ]
    },
    mi: {
      title: "Membre inférieur", folder: "FRACTURES MI", home: "index.htm", accent: "#16a34a",
      groups: [
        { label: "Bassin",   cases: [["1","cas1.html"],["2","cas2.html"]] },
        { label: "Hanche",   cases: [["3","cas3.html"],["4","cas4.html"],["5","cas5.html"],["6","cas6.html"]] },
        { label: "Cuisse",   cases: [["7","cas7.html"],["8","cas8.html"],["9","cas0.html"]] },
        { label: "Genou",    cases: [["10","cas9.html"],["11","cas10.html"],["12","cas11.html"],["13","cas12.html"],["14","cas13.html"],["15","cas14.html"]] },
        { label: "Jambe",    cases: [["16","cas15.html"],["17","cas16.html"],["18","cas17.html"],["19","cas18.html"]] },
        { label: "Cheville", cases: [["21","cas20.html"],["22","cas21.html"],["23","cas22.html"]] }
      ]
    }
  };
  // Auxiliary (non-case) pages of each book, in reading order.
  var AUX = [
    ["Introduction",  "introduction/introduction.html"],
    ["Prérequis",     "prerequis/prerequis.html"],
    ["Cas cliniques", "cas_clinique/casclinique.html"],
    ["Résumé",        "resume/resume.html"],
    ["Conclusion",    "conclusion/conclusion.html"],
    ["Bibliographie", "bibliographie/bibliographie.html"]
  ];

  function bookUrl(book, rel) { return BASE + book.folder + "/" + rel; }
  function caseUrl(book, file) { return bookUrl(book, "cas_clinique/" + file); }
  function rootUrl() { return BASE + "index.html"; }

  // --- Styles -----------------------------------------------------------------
  var W = "290px";       // sidebar width
  var BP = "1300px";     // permanent breakpoint (sidebar 290 + 960 grid + scrollbar/breathing)
  var css = ''
    + ':root{--cpnav-w:' + W + '}'
    + '.cpnav-side{position:fixed;top:0;left:0;bottom:0;width:var(--cpnav-w);z-index:100000;'
    +   'background:#0f172a;color:#e2e8f0;display:flex;flex-direction:column;'
    +   'font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Inter,sans-serif;'
    +   'box-shadow:2px 0 18px rgba(2,6,23,.28);transform:translateX(-100%);'
    +   'transition:transform .24s cubic-bezier(.2,.7,.2,1)}'
    + '.cpnav-side.cpnav-open{transform:none}'
    + '.cpnav-head{padding:16px 18px 12px;border-bottom:1px solid #1e293b;flex:0 0 auto}'
    + '.cpnav-head a.cpnav-title{display:block;color:#fff;text-decoration:none;'
    +   'font:800 16px/1.2 -apple-system,Segoe UI,Roboto,sans-serif;letter-spacing:-.01em}'
    + '.cpnav-head .cpnav-sub{display:block;margin-top:3px;color:#94a3b8;font-size:11.5px;'
    +   'text-transform:uppercase;letter-spacing:.09em}'
    + '.cpnav-search{padding:12px 16px;flex:0 0 auto}'
    + '.cpnav-search input{width:100%;padding:9px 11px;border:1px solid #334155;border-radius:8px;'
    +   'background:#111a2e;color:#e2e8f0;font-size:13px;outline:none}'
    + '.cpnav-search input::placeholder{color:#64748b}'
    + '.cpnav-search input:focus{border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,.25)}'
    + '.cpnav-body{overflow:auto;padding:4px 10px 28px;flex:1 1 auto;-webkit-overflow-scrolling:touch}'
    + '.cpnav-body::-webkit-scrollbar{width:10px}'
    + '.cpnav-body::-webkit-scrollbar-thumb{background:#334155;border-radius:8px;border:3px solid #0f172a}'
    + '.cpnav-book{margin:10px 0 6px}'
    + '.cpnav-book>a.cpnav-bh{display:flex;align-items:center;gap:8px;padding:7px 8px;border-radius:8px;'
    +   'color:#fff;text-decoration:none;font:700 13px/1.2 -apple-system,Segoe UI,Roboto,sans-serif;'
    +   'text-transform:uppercase;letter-spacing:.05em}'
    + '.cpnav-book>a.cpnav-bh:hover{background:#1e293b}'
    + '.cpnav-book>a.cpnav-bh .cpnav-dot{width:9px;height:9px;border-radius:50%;background:var(--c);flex:0 0 auto}'
    + '.cpnav-aux{list-style:none;margin:2px 0 6px;padding:0 0 0 6px}'
    + '.cpnav-aux a{display:block;padding:5px 10px;border-radius:6px;color:#cbd5e1;text-decoration:none;font-size:13px}'
    + '.cpnav-aux a:hover{background:#1e293b;color:#fff}'
    + '.cpnav-grp{margin:1px 0}'
    + '.cpnav-grp>summary{cursor:pointer;list-style:none;padding:6px 10px;border-radius:6px;'
    +   'font-weight:600;color:#e2e8f0;display:flex;justify-content:space-between;align-items:center;gap:8px}'
    + '.cpnav-grp>summary::-webkit-details-marker{display:none}'
    + '.cpnav-grp>summary:hover{background:#1e293b}'
    + '.cpnav-grp>summary .cpnav-chev{transition:transform .18s ease;color:#64748b;font-size:11px}'
    + '.cpnav-grp[open]>summary .cpnav-chev{transform:rotate(90deg)}'
    + '.cpnav-grp>summary .cpnav-count{margin-left:auto;font-weight:500;font-size:11px;color:#94a3b8;'
    +   'background:#1e293b;border-radius:999px;padding:1px 8px}'
    + '.cpnav-cases{list-style:none;margin:2px 0 6px;padding:0 0 0 14px;border-left:1px solid #1e293b;margin-left:12px}'
    + '.cpnav-cases a{display:block;padding:5px 10px;color:#cbd5e1;text-decoration:none;border-radius:6px;font-size:13px}'
    + '.cpnav-cases a:hover{background:#1e293b;color:#fff}'
    + '.cpnav-current{background:var(--c)!important;color:#fff!important;font-weight:600}'
    + '.cpnav-empty{padding:16px;color:#64748b;font-style:italic;text-align:center}'
    // toggle button + scrim (mobile / narrow)
    + '.cpnav-toggle{position:fixed;top:12px;left:12px;z-index:100001;background:#0f172a;color:#fff;'
    +   'border:0;border-radius:10px;width:44px;height:44px;font-size:20px;line-height:1;cursor:pointer;'
    +   'box-shadow:0 6px 18px rgba(2,6,23,.35)}'
    + '.cpnav-toggle:hover{background:#1e293b}'
    + '.cpnav-toggle:focus{outline:2px solid #60a5fa;outline-offset:2px}'
    + '.cpnav-scrim{position:fixed;inset:0;z-index:99999;background:rgba(2,6,23,.5);'
    +   'opacity:0;visibility:hidden;transition:opacity .2s ease,visibility .2s}'
    + '.cpnav-scrim.cpnav-open{opacity:1;visibility:visible}'
    // permanent mode on wide screens
    + '@media (min-width:' + BP + '){'
    +   'html.cpnav-has-side body{margin-left:var(--cpnav-w)!important}'
    +   '.cpnav-side{transform:none!important}'
    +   '.cpnav-toggle{display:none}'
    +   '.cpnav-scrim{display:none}'
    + '}'
    + '@media print{.cpnav-side,.cpnav-toggle,.cpnav-scrim{display:none!important}'
    +   'html.cpnav-has-side body{margin-left:0!important}}';

  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  // --- Build DOM --------------------------------------------------------------
  var side = document.createElement('aside');
  side.className = 'cpnav-side';
  side.setAttribute('aria-label', 'Navigation du site');

  var head = document.createElement('div');
  head.className = 'cpnav-head';
  head.innerHTML = '<a class="cpnav-title" href="' + rootUrl() + '">Fractures de l’enfant'
    + '<span class="cpnav-sub">Traumato-orthopédie pédiatrique</span></a>';
  side.appendChild(head);

  var search = document.createElement('div');
  search.className = 'cpnav-search';
  search.innerHTML = '<input type="search" placeholder="Filtrer (coude, genou, 14…)" autocomplete="off" aria-label="Filtrer la navigation" />';
  side.appendChild(search);

  var body = document.createElement('nav');
  body.className = 'cpnav-body';

  var links = []; // all <a> for search + current detection

  function mkLink(href, text, cls, searchStr) {
    var a = document.createElement('a');
    a.href = href; a.textContent = text;
    if (cls) a.className = cls;
    a.dataset.search = (searchStr || text).toLowerCase();
    links.push(a);
    return a;
  }

  Object.keys(CATALOG).forEach(function (key) {
    var book = CATALOG[key];
    var sec = document.createElement('section');
    sec.className = 'cpnav-book';
    sec.style.setProperty('--c', book.accent);

    var bh = mkLink(bookUrl(book, book.home), book.title, 'cpnav-bh', book.title);
    bh.insertAdjacentHTML('afterbegin', '<span class="cpnav-dot"></span>');
    sec.appendChild(bh);

    // auxiliary pages
    var aux = document.createElement('ul');
    aux.className = 'cpnav-aux';
    AUX.forEach(function (p) {
      var li = document.createElement('li');
      li.appendChild(mkLink(bookUrl(book, p[1]), p[0], null, book.title + ' ' + p[0]));
      aux.appendChild(li);
    });
    sec.appendChild(aux);

    // case groups
    book.groups.forEach(function (g) {
      var det = document.createElement('details');
      det.className = 'cpnav-grp';
      var sum = document.createElement('summary');
      sum.innerHTML = '<span class="cpnav-chev">▶</span><span>' + g.label
        + '</span><span class="cpnav-count">' + g.cases.length + '</span>';
      det.appendChild(sum);
      var ul = document.createElement('ul');
      ul.className = 'cpnav-cases';
      g.cases.forEach(function (c) {
        var li = document.createElement('li');
        li.appendChild(mkLink(caseUrl(book, c[1]), 'Cas clinique ' + c[0], null,
          book.title + ' ' + g.label + ' cas ' + c[0]));
        ul.appendChild(li);
      });
      det.appendChild(ul);
      det.dataset.group = g.label;
      sec.appendChild(det);
    });
    body.appendChild(sec);
  });
  side.appendChild(body);

  // --- Current page detection (book-aware, by resolved full path) -------------
  var here = decodeURIComponent(window.location.pathname);
  var current = null;
  links.forEach(function (a) {
    if (decodeURIComponent(a.pathname) === here) current = a;
  });
  if (current) {
    current.classList.add('cpnav-current');
    var det = current.closest('details.cpnav-grp');
    if (det) det.open = true;
  }

  // --- Toggle + scrim (narrow screens) ----------------------------------------
  var toggle = document.createElement('button');
  toggle.className = 'cpnav-toggle';
  toggle.type = 'button';
  toggle.setAttribute('aria-label', 'Ouvrir/fermer le menu');
  toggle.innerHTML = '☰';

  var scrim = document.createElement('div');
  scrim.className = 'cpnav-scrim';

  function openSide()  { side.classList.add('cpnav-open'); scrim.classList.add('cpnav-open'); }
  function closeSide() { side.classList.remove('cpnav-open'); scrim.classList.remove('cpnav-open'); }
  function toggleSide(){ side.classList.contains('cpnav-open') ? closeSide() : openSide(); }

  toggle.addEventListener('click', toggleSide);
  scrim.addEventListener('click', closeSide);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeSide();
    if (e.key === '/' && document.activeElement !== search.querySelector('input')) {
      e.preventDefault(); openSide(); search.querySelector('input').focus();
    }
  });
  // close the off-canvas menu after picking a link (narrow screens only)
  body.addEventListener('click', function (e) {
    if (e.target.tagName === 'A' && !matchMedia('(min-width:' + BP + ')').matches) closeSide();
  });

  // --- Search / filter --------------------------------------------------------
  search.querySelector('input').addEventListener('input', function (e) {
    var q = e.target.value.trim().toLowerCase();
    body.querySelectorAll('.cpnav-book').forEach(function (sec) {
      var bookVisible = false;
      sec.querySelectorAll('.cpnav-aux a').forEach(function (a) {
        var m = !q || a.dataset.search.indexOf(q) !== -1;
        a.parentNode.style.display = m ? '' : 'none'; if (m) bookVisible = true;
      });
      sec.querySelectorAll('.cpnav-grp').forEach(function (g) {
        var any = false;
        g.querySelectorAll('.cpnav-cases a').forEach(function (a) {
          var m = !q || a.dataset.search.indexOf(q) !== -1;
          a.parentNode.style.display = m ? '' : 'none'; if (m) any = true;
        });
        g.style.display = any ? '' : 'none';
        if (q) g.open = any; else g.open = g.querySelector('.cpnav-current') != null;
        if (any) bookVisible = true;
      });
      sec.style.display = bookVisible ? '' : 'none';
    });
  });

  // --- Mount ------------------------------------------------------------------
  function mount() {
    if (!document.body) return setTimeout(mount, 30);
    document.documentElement.classList.add('cpnav-has-side');
    document.body.appendChild(side);
    document.body.appendChild(scrim);
    document.body.appendChild(toggle);
    // (permanent mode is handled by CSS; the .cpnav-open class only drives the
    //  off-canvas drawer on narrow screens.)
    // scroll current item into view
    if (current) setTimeout(function () {
      try { current.scrollIntoView({ block: 'center' }); } catch (e) { current.scrollIntoView(); }
    }, 60);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
