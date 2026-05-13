/* ──────────────────────────────────────────────────────────────
   site-mobile.js — companion to site-mobile.css.

   Responsibilities:
   - Inject a hamburger button into `.nav-brand-right`.
   - Build a fullscreen drawer mirroring `.nav-pages` so every
     zone and sub-page reachable on desktop is reachable on mobile.
   - Wire open/close, scrim, Escape, and a "tap a link → close"
     behaviour.

   Safety:
   - The hamburger is hidden via CSS (display:none) on desktop, so
     this JS can run on every page-load regardless of viewport.
     The drawer markup is built once at DOMContentLoaded; nothing
     here mutates state visible to desktop users.
   - Walking the live nav DOM keeps the mobile menu in sync with
     whatever the page's nav happens to be — no duplicated source
     of truth.

   Last synced with nav structure: 2026/05/13.
   ────────────────────────────────────────────────────────────── */
(function(){
  'use strict';

  function ready(fn){
    if(document.readyState === 'loading'){
      document.addEventListener('DOMContentLoaded', fn);
    } else { fn(); }
  }

  function el(tag, attrs, children){
    var node = document.createElement(tag);
    if(attrs){
      Object.keys(attrs).forEach(function(k){
        if(k === 'class') node.className = attrs[k];
        else if(k === 'html') node.innerHTML = attrs[k];
        else if(k === 'text') node.textContent = attrs[k];
        else node.setAttribute(k, attrs[k]);
      });
    }
    (children || []).forEach(function(c){ if(c) node.appendChild(c); });
    return node;
  }

  /* Extract a "leaf" link from a desktop dropdown anchor — preserves
     href, label, and the secondary citation line if present. */
  function extractDropdownLink(srcAnchor){
    var href = srcAnchor.getAttribute('href') || '#';
    var titleEl = srcAnchor.querySelector('.nav-dd-ref-title');
    var citeEl  = srcAnchor.querySelector('.nav-dd-ref-cite');
    var label   = titleEl ? titleEl.textContent.trim()
                          : (srcAnchor.textContent || '').trim();
    var a = el('a', {
      href: href,
      class: 'mobile-drawer-link'
    });
    a.appendChild(el('span', {text: label}));
    if(citeEl){
      // Strip any inline ".nav-dd-ref-stage" / ".nav-dd-ref-tag" pills:
      // they're decorative on desktop and noisy in the mobile list.
      var citeText = '';
      citeEl.childNodes.forEach(function(n){
        if(n.nodeType === 3) citeText += n.textContent;
      });
      citeText = citeText.trim();
      if(citeText){
        a.appendChild(el('span', {
          class: 'mobile-drawer-link-cite',
          text: citeText
        }));
      }
    }
    return a;
  }

  /* Build one drawer section from a desktop `.nav-zone`. */
  function sectionFromZone(zone){
    // Case 1: zone contains a single direct tab link.
    var directTab = zone.querySelector(':scope > .nav-tab-implementation, :scope > .nav-tab-roadmap, :scope > .nav-tab-problems, :scope > .nav-tab-problems-big, :scope > .nav-tab-diag, :scope > .nav-tab-diag-big, :scope > a.nav-tab');
    if(directTab && !zone.querySelector('.nav-dd-wrap')){
      var section = el('div', {class: 'mobile-drawer-section'});
      var link = el('a', {
        href: directTab.getAttribute('href') || '#',
        class: 'mobile-drawer-link'
      });
      // Add the active state if this is the page we're on.
      if(directTab.classList.contains('active')) link.classList.add('active');
      var titleSpan = el('span', {
        class: 'mobile-drawer-section-title',
        text: (directTab.textContent || '').trim()
      });
      link.appendChild(titleSpan);
      section.appendChild(link);
      return section;
    }

    // Case 2: zone contains a dropdown.
    var dd = zone.querySelector('.nav-dd-wrap');
    if(!dd) return null;
    var btn = dd.querySelector('button.nav-dd-btn-light, button.nav-dd-btn-solution, button[class*="nav-dd-btn"]');
    var panel = dd.querySelector('.nav-dd-panel-light, [class*="nav-dd-panel"]');
    if(!btn || !panel) return null;

    var section = el('div', {class: 'mobile-drawer-section'});

    // Header (label + chevron) — collapsible toggle.
    var head = el('button', {
      class: 'mobile-drawer-section-head',
      type: 'button',
      'aria-expanded': 'false'
    });
    // Strip the inline SVG chevron from the desktop button text.
    var btnLabel = '';
    btn.childNodes.forEach(function(n){
      if(n.nodeType === 3) btnLabel += n.textContent;
    });
    btnLabel = btnLabel.trim() || (btn.textContent || '').trim();
    head.appendChild(el('span', {class: 'mobile-drawer-section-title', text: btnLabel}));
    head.insertAdjacentHTML('beforeend',
      '<svg class="mobile-drawer-section-chev" viewBox="0 0 12 8" aria-hidden="true">' +
      '<path d="M2 2.5 L6 6 L10 2.5" stroke="currentColor" stroke-width="1.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' +
      '</svg>');
    section.appendChild(head);

    var body = el('div', {class: 'mobile-drawer-section-body'});

    // Stratum meta line (the small grey explanatory text on desktop).
    var meta = panel.querySelector('.nav-dd-stratum-meta');
    if(meta){
      body.appendChild(el('span', {
        class: 'mobile-drawer-stratum-meta',
        text: (meta.textContent || '').trim()
      }));
    }

    // Walk panel children in order — preserves group-label / anchor
    // sequencing so the mobile list reads like the desktop one.
    var stratum = panel.querySelector('.nav-dd-stratum') || panel;
    Array.prototype.forEach.call(stratum.children, function(child){
      if(child.classList && child.classList.contains('nav-dd-ref-group-label')){
        body.appendChild(el('div', {
          class: 'mobile-drawer-group-label',
          text: (child.textContent || '').trim()
        }));
      } else if(child.tagName === 'A' && child.classList.contains('nav-dd-ref')){
        body.appendChild(extractDropdownLink(child));
      }
      // Skip .nav-dd-stratum-head (already extracted via meta lookup)
      // and anything else we don't recognise.
    });

    section.appendChild(body);

    // Wire the toggle.
    head.addEventListener('click', function(e){
      e.preventDefault();
      e.stopPropagation();
      var open = section.classList.toggle('open');
      head.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    return section;
  }

  function buildDrawer(){
    var nav = document.querySelector('.site-nav');
    if(!nav) return null;
    var brandRight = nav.querySelector('.nav-brand-right');
    var pages = nav.querySelector('.nav-pages');
    if(!brandRight || !pages) return null;

    /* ── Hamburger button ─────────────────────────────────── */
    var hamburger = el('button', {
      class: 'mobile-hamburger',
      type: 'button',
      'aria-label': 'Open navigation',
      'aria-expanded': 'false',
      'aria-controls': 'mobileDrawer'
    });
    hamburger.innerHTML =
      '<svg width="18" height="14" viewBox="0 0 18 14" aria-hidden="true">' +
      '<path d="M1 1h16M1 7h16M1 13h16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>' +
      '</svg>';
    // Insert as the first child of nav-brand-right so it sits left of
    // the PDF + theme buttons, mirroring the typical mobile pattern.
    brandRight.insertBefore(hamburger, brandRight.firstChild);

    /* ── Drawer + scrim ───────────────────────────────────── */
    var scrim  = el('div',   {class: 'mobile-drawer-scrim', 'aria-hidden': 'true'});
    var drawer = el('aside', {
      class: 'mobile-drawer',
      id: 'mobileDrawer',
      role: 'dialog',
      'aria-modal': 'true',
      'aria-label': 'Site navigation',
      tabindex: '-1'
    });

    var head = el('div', {class: 'mobile-drawer-head'});
    head.appendChild(el('span', {class: 'mobile-drawer-title', text: 'Navigation'}));
    var closeBtn = el('button', {
      class: 'mobile-drawer-close',
      type: 'button',
      'aria-label': 'Close navigation'
    });
    closeBtn.innerHTML = '×';
    head.appendChild(closeBtn);
    drawer.appendChild(head);

    var body = el('nav', {class: 'mobile-drawer-body', 'aria-label': 'Main'});
    Array.prototype.forEach.call(pages.children, function(zone){
      if(!zone.classList || !zone.classList.contains('nav-zone')) return;
      var sec = sectionFromZone(zone);
      if(sec) body.appendChild(sec);
    });
    drawer.appendChild(body);

    document.body.appendChild(scrim);
    document.body.appendChild(drawer);

    /* ── Open / close wiring ──────────────────────────────── */
    function open(){
      drawer.classList.add('open');
      scrim.classList.add('open');
      document.body.classList.add('mobile-drawer-open');
      hamburger.setAttribute('aria-expanded', 'true');
      // Move focus into the drawer for screen-reader users.
      setTimeout(function(){ closeBtn.focus(); }, 50);
    }
    function close(){
      drawer.classList.remove('open');
      scrim.classList.remove('open');
      document.body.classList.remove('mobile-drawer-open');
      hamburger.setAttribute('aria-expanded', 'false');
      hamburger.focus();
    }

    hamburger.addEventListener('click', function(e){
      e.preventDefault();
      e.stopPropagation();
      if(drawer.classList.contains('open')) close(); else open();
    });
    closeBtn.addEventListener('click', function(e){
      e.preventDefault();
      close();
    });
    scrim.addEventListener('click', close);
    document.addEventListener('keydown', function(e){
      if(e.key === 'Escape' && drawer.classList.contains('open')) close();
    });
    // Tap a link → close (after the navigation handler fires).
    drawer.addEventListener('click', function(e){
      var a = e.target.closest && e.target.closest('a.mobile-drawer-link');
      if(a) close();
    });

    return {drawer: drawer, open: open, close: close};
  }

  ready(buildDrawer);
})();
