(function(){
var v=['fluid','braid','braid-red','dots','overlap','zoom','zoom-full','ada','fluid-red'];var pick=v[Math.floor(Math.random()*v.length)];document.addEventListener('DOMContentLoaded',function(){var h=document.querySelector('.hero');if(h)h.setAttribute('data-banner',pick);});

  /* ── Theme toggle ──
     Inline onclick="toggleTheme()" on the header button. Persists the
     choice in localStorage; reads it back on every page load. */
  window.toggleTheme=function(){
    var html=document.documentElement;
    var current=html.getAttribute('data-theme')||'light';
    var next=current==='dark'?'light':'dark';
    html.setAttribute('data-theme',next);
    try{localStorage.setItem('theme',next);}catch(e){}
    var btn=document.querySelector('.theme-toggle');
    if(btn) btn.textContent=next==='dark'?'☾':'☀';
  };
  (function applyStoredTheme(){
    var stored;try{stored=localStorage.getItem('theme');}catch(e){}
    if(stored==='dark'||stored==='light'){
      document.documentElement.setAttribute('data-theme',stored);
    }
    document.addEventListener('DOMContentLoaded',function(){
      var html=document.documentElement;
      var t=html.getAttribute('data-theme')||'light';
      var btn=document.querySelector('.theme-toggle');
      if(btn) btn.textContent=t==='dark'?'☾':'☀';
    });
  })();

  /* ── PDF export ──
     Inline onclick="printAsPdf()" on the header button. Opens the native
     print dialogue; the page's print stylesheet handles layout. */
  window.printAsPdf=function(){ window.print(); };

  /* ── Figure-image lightbox ──
     Click any image inside `.content` (figures, inline images) to open the
     full-size view in the lightbox overlay; click the overlay or press
     Escape to close. The overlay div + CSS are shipped in the page shell;
     this just wires the interaction. */
  document.addEventListener('DOMContentLoaded',function(){
    var overlay=document.getElementById('lightbox');
    var lbImg=document.getElementById('lb-img');
    if(!overlay||!lbImg) return;
    function open(src,alt){
      lbImg.src=src;
      lbImg.alt=alt||'';
      overlay.classList.add('active');
      document.body.style.overflow='hidden';
    }
    function close(){
      overlay.classList.remove('active');
      document.body.style.overflow='';
      // Drop the src after the fade so memory is freed and the next open
      // doesn't briefly flash the previous image.
      setTimeout(function(){ if(!overlay.classList.contains('active')) lbImg.src=''; },300);
    }
    document.querySelectorAll('.content img').forEach(function(img){
      // Skip tiny chrome icons (badges, inline glyphs); only zoom real figures.
      if(img.closest('.no-zoom')) return;
      img.style.cursor='zoom-in';
      img.addEventListener('click',function(e){
        e.preventDefault();
        open(img.currentSrc||img.src, img.alt);
      });
    });
    overlay.addEventListener('click',close);
    document.addEventListener('keydown',function(e){
      if(e.key==='Escape' && overlay.classList.contains('active')) close();
    });
  });

  /* ── TOC floating panel ── */
  (function initTocPanel(){
    var inlineToc=document.querySelector('.content > .toc-nav')
      || document.querySelector('.content .toc-nav');
    if(!inlineToc) return;
    document.body.classList.add('has-toc-panel');

    var fab=document.createElement('button');
    fab.className='toc-fab';
    fab.type='button';
    fab.setAttribute('aria-label','Open table of contents');
    fab.title='Table of contents';
    fab.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true">'
      +'<line x1="8" y1="6" x2="21" y2="6"/>'
      +'<line x1="8" y1="12" x2="21" y2="12"/>'
      +'<line x1="8" y1="18" x2="21" y2="18"/>'
      +'<circle cx="4" cy="6" r="1.2" fill="currentColor" stroke="none"/>'
      +'<circle cx="4" cy="12" r="1.2" fill="currentColor" stroke="none"/>'
      +'<circle cx="4" cy="18" r="1.2" fill="currentColor" stroke="none"/>'
      +'</svg>';
    document.body.appendChild(fab);

    var overlay=document.createElement('div');
    overlay.className='toc-overlay';
    overlay.setAttribute('aria-hidden','true');
    document.body.appendChild(overlay);

    var panel=document.createElement('aside');
    panel.className='toc-panel';
    panel.setAttribute('aria-label','Table of contents');
    panel.setAttribute('aria-hidden','true');
    var header=document.createElement('div');
    header.className='toc-panel-header';
    header.innerHTML='<span class="toc-panel-title">Contents</span>'
      +'<button type="button" class="toc-panel-close" aria-label="Close">'
      +'<svg viewBox="0 0 24 24" aria-hidden="true"><line x1="5" y1="5" x2="19" y2="19"/><line x1="19" y1="5" x2="5" y2="19"/></svg>'
      +'</button>';
    var body=document.createElement('div');
    body.className='toc-panel-body';
    var cloned=inlineToc.cloneNode(true);
    cloned.querySelectorAll('.toc-toggle').forEach(function(el){ el.classList.remove('toc-toggle','collapsed'); });
    cloned.querySelectorAll('.toc-collapsed').forEach(function(el){ el.classList.remove('toc-collapsed'); });
    cloned.querySelectorAll('li.has-children').forEach(function(el){ el.classList.remove('has-children'); });
    body.appendChild(cloned);
    panel.appendChild(header);
    panel.appendChild(body);
    document.body.appendChild(panel);

    function openPanel(){ document.body.classList.add('toc-open'); panel.setAttribute('aria-hidden','false'); overlay.setAttribute('aria-hidden','false'); }
    function closePanel(){ document.body.classList.remove('toc-open'); panel.setAttribute('aria-hidden','true'); overlay.setAttribute('aria-hidden','true'); }
    fab.addEventListener('click',function(e){ e.stopPropagation(); openPanel(); });
    overlay.addEventListener('click',closePanel);
    header.querySelector('.toc-panel-close').addEventListener('click',closePanel);
    document.addEventListener('keydown',function(e){
      if(e.key==='Escape' && document.body.classList.contains('toc-open')) closePanel();
    });

    cloned.querySelectorAll('a[href^="#"]').forEach(function(a){
      a.addEventListener('click',function(){
        var id=a.getAttribute('href').slice(1);
        var target=document.getElementById(id);
        if(target){
          var cur=target, toExpand=[];
          while(cur && cur!==document.body){
            if(cur.classList && cur.classList.contains('section-body') && cur.classList.contains('collapsed')){
              var toggle=cur.previousElementSibling;
              if(toggle && toggle.classList.contains('section-toggle')) toExpand.push(toggle);
            }
            cur=cur.parentElement;
          }
          toExpand.reverse().forEach(function(t){ t.click(); });
        }
        setTimeout(closePanel,50);
      });
    });

    var links=Array.from(cloned.querySelectorAll('a[href^="#"]'));
    var map=[];
    links.forEach(function(a){
      var id=a.getAttribute('href').slice(1);
      if(!id) return;
      var el=document.getElementById(id);
      if(el) map.push({id:id,link:a,el:el});
    });
    function updateActive(){
      if(map.length===0) return;
      var y=window.scrollY+140;
      var current=map[0];
      for(var i=0;i<map.length;i++){
        var top=map[i].el.getBoundingClientRect().top+window.scrollY;
        if(top<=y) current=map[i]; else break;
      }
      links.forEach(function(a){ a.classList.remove('toc-active'); });
      if(current) current.link.classList.add('toc-active');
    }
    window.addEventListener('scroll',updateActive,{passive:true});
    updateActive();
  })();


  /* ── Collapsible content sections (h2 - h6) ──
     Wraps the content of each numbered heading in a .section-body
     div and toggles .collapsed on click. Restored after the
     April 30 site.js wipe (commit ff51a62) accidentally dropped it.
     Lives OUTSIDE the cross-obs marker block so the regenerator
     in build_site.py preserves it on every rebuild. */
  function makeCollapsible(heading, stopTags){
    if(/^objective$/i.test(heading.textContent.trim())) return;
    var startCollapsed=/^table of contents$/i.test(heading.textContent.trim());
    heading.classList.add('section-toggle');
    var wrapper=document.createElement('div');
    wrapper.className='section-body';
    var sib=heading.nextElementSibling;
    var nodes=[];
    while(sib && stopTags.indexOf(sib.tagName)===-1){
      nodes.push(sib);
      sib=sib.nextElementSibling;
    }
    if(nodes.length===0){ heading.classList.remove('section-toggle'); return; }
    heading.after(wrapper);
    nodes.forEach(function(n){ wrapper.appendChild(n); });
    if(startCollapsed){
      wrapper.style.maxHeight='0px';
      wrapper.classList.add('collapsed');
      heading.classList.add('collapsed');
    } else {
      wrapper.style.maxHeight='none';
    }
    heading.addEventListener('click',function(){
      heading.classList.toggle('collapsed');
      if(wrapper.classList.contains('collapsed')){
        wrapper.style.maxHeight=wrapper.scrollHeight+'px';
        wrapper.classList.remove('collapsed');
        wrapper.addEventListener('transitionend',function handler(){
          if(!wrapper.classList.contains('collapsed')) wrapper.style.maxHeight='none';
          wrapper.removeEventListener('transitionend',handler);
        });
      } else {
        wrapper.style.maxHeight=wrapper.scrollHeight+'px';
        requestAnimationFrame(function(){ wrapper.style.maxHeight='0px'; wrapper.classList.add('collapsed'); });
      }
    });
    wrapper.querySelectorAll('[id]').forEach(function(el){
      window.addEventListener('hashchange',function(){
        if(window.location.hash==='#'+el.id && wrapper.classList.contains('collapsed')){
          heading.click();
        }
      });
    });
  }
  /* Apply bottom-up: deepest first so inner wrappers exist before outer
     ones. Extends to h5 + h6 so deeply nested sections (e.g. 1.2.4.2.1
     and 1.2.4.2.1.1) get the same fold affordance as h2-h4. */
  document.querySelectorAll('.content h6[id]').forEach(function(h){ makeCollapsible(h,['H1','H2','H3','H4','H5','H6']); });
  document.querySelectorAll('.content h5[id]').forEach(function(h){ makeCollapsible(h,['H1','H2','H3','H4','H5']); });
  document.querySelectorAll('.content h4[id]').forEach(function(h){ makeCollapsible(h,['H1','H2','H3','H4']); });
  document.querySelectorAll('.content h3[id]').forEach(function(h){ makeCollapsible(h,['H1','H2','H3']); });
  document.querySelectorAll('.content h2[id]').forEach(function(h){ makeCollapsible(h,['H1','H2']); });
  /* H1 chapter-level fold: applied last so the H1 wrapper contains the
     already-built nested section-body wrappers. CSS suppresses the
     chevron on H1 (the user prefers no arrow at this level). */
  document.querySelectorAll('.content h1[id]').forEach(function(h){ makeCollapsible(h,['H1']); });


  /* ── Back-to-top FAB ──
     Floats above the bottom-right corner once the reader has
     scrolled past the hero. One round button with an upward
     chevron — click scrolls the window back to the top. Lives
     OUTSIDE the cross-obs marker block so it survives every
     rebuild. */
  (function initBackToTop(){
    if(document.querySelector('.back-to-top')) return;
    var btn=document.createElement('button');
    btn.className='back-to-top';
    btn.type='button';
    btn.setAttribute('aria-label','Back to top');
    btn.title='Back to top';
    btn.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true">'+
      '<path fill="none" stroke="currentColor" stroke-width="2" '+
      'stroke-linecap="round" stroke-linejoin="round" '+
      'd="M6 14l6-6 6 6"/></svg>';
    document.body.appendChild(btn);
    var threshold=320;
    function update(){
      if(window.scrollY>threshold) btn.classList.add('visible');
      else btn.classList.remove('visible');
    }
    btn.addEventListener('click',function(){
      try{ window.scrollTo({top:0,behavior:'smooth'}); }
      catch(e){ window.scrollTo(0,0); }
    });
    window.addEventListener('scroll',update,{passive:true});
    update();
  })();


  /* ── Cross-page synthesis-observation source overlay ──
     When an `.obs-ref` anchor carries `data-obs-src`, hydrate the overlay
     from the bundled `.sro-obs-detail` registry (the source card on the
     sub-report page) rather than from the local `.obs-card`. The panel
     CTA navigates cross-page via `data-obs-href`. */
  (function initCrossObsSource(){
    var refs=document.querySelectorAll('.obs-ref[data-obs-src]');
    if(!refs.length) return;

    /* Index by source canonical id (e.g. "OPE.O7"). */
    var srcIndex={};
    document.querySelectorAll('.sro-obs-detail[data-obs-canon]').forEach(function(card){
      var canon=card.getAttribute('data-obs-canon');
      var title=(card.querySelector('.sro-obs-detail-title')||{}).innerHTML||'';
      var summary=(card.querySelector('.sro-obs-detail-summary')||{}).innerHTML||'';
      var abstractEl=card.querySelector('.sro-obs-detail-abstract');
      var abstractHtml=abstractEl?abstractEl.innerHTML:'';
      var count=(card.querySelector('.sro-obs-detail-count')||{}).textContent||'';
      var page=card.getAttribute('data-page')||'';
      var href=card.getAttribute('data-href')||'';
      var findingIds=(card.getAttribute('data-findings')||'').split(',')
        .map(function(s){return s.trim();}).filter(Boolean);
      srcIndex[canon]={canon:canon,title:title,summary:summary,
        abstract:abstractHtml,count:count,
        page:page,href:href,findingIds:findingIds};
    });
    if(!Object.keys(srcIndex).length) return;

    /* Findings registry — index per canonical finding id (e.g. "OPE.O1.F1").
       We reuse the bundled .finding-detail cards on non-subreport pages so
       the source panel can list finding details inline rather than a count. */
    var findingsIndex={};
    document.querySelectorAll('.finding-detail[data-finding]').forEach(function(card){
      var canon=card.getAttribute('data-finding');
      var summary=(card.querySelector('.finding-detail-summary')||{}).innerHTML||'';
      var insight=(card.querySelector('.finding-detail-insight')||{}).innerHTML||'';
      var href=card.getAttribute('data-href')||'';
      var page=card.getAttribute('data-page')||'';
      findingsIndex[canon]={canon:canon,summary:summary,insight:insight,href:href,page:page};
    });

    /* Tooltip — mirrors the obs-tooltip styling but sources from srcIndex */
    var tip=document.createElement('div');
    tip.className='obs-tooltip obs-tooltip-src';
    tip.setAttribute('role','tooltip');
    document.body.appendChild(tip);
    var tipTimer=null,tipActive=false;

    function showTip(ref,x,y){
      var canon=ref.getAttribute('data-obs-src');
      var data=srcIndex[canon];
      if(!data) return;
      tip.innerHTML=
        '<div class="obs-tooltip-head">'+
          '<span class="obs-tooltip-num">'+data.canon+'</span>'+
          '<span class="obs-tooltip-section">source sub-report</span>'+
        '</div>'+
        '<div class="obs-tooltip-title">'+data.title+'</div>'+
        '<div class="obs-tooltip-summary">'+data.summary+'</div>'+
        '<div class="obs-tooltip-hint">'+data.count+' · click for detail</div>';
      tip.style.left='0px';tip.style.top='0px';
      tip.classList.add('visible');
      positionTip(x,y);
      tipActive=true;
    }
    function positionTip(x,y){
      var r=tip.getBoundingClientRect();
      var vw=window.innerWidth,vh=window.innerHeight;
      var left=x+14,top=y+18;
      if(left+r.width>vw-12) left=Math.max(8,x-r.width-14);
      if(top+r.height>vh-12) top=Math.max(8,y-r.height-14);
      tip.style.left=left+'px';tip.style.top=top+'px';
    }
    function hideTip(){ tip.classList.remove('visible'); tipActive=false; }

    refs.forEach(function(ref){
      ref.addEventListener('mouseenter',function(e){
        clearTimeout(tipTimer);
        tipTimer=setTimeout(function(){ showTip(ref,e.clientX,e.clientY); },120);
      });
      ref.addEventListener('mousemove',function(e){ if(tipActive) positionTip(e.clientX,e.clientY); });
      ref.addEventListener('mouseleave',function(){ clearTimeout(tipTimer); hideTip(); });
    });

    /* --- Side panel (click for full detail) ---
       Mirrors the local obs-panel but sources from the bundled source
       registry so the reader sees the defining sub-report card without
       navigating. The CTA then jumps cross-page to the source. */
    var overlay=document.createElement('div');
    overlay.className='obs-panel-overlay obs-panel-overlay-src';
    document.body.appendChild(overlay);

    var panel=document.createElement('aside');
    panel.className='obs-panel obs-panel-src';
    panel.setAttribute('role','dialog');
    panel.setAttribute('aria-label','Source observation detail');
    panel.setAttribute('aria-hidden','true');
    panel.innerHTML=
      '<div class="obs-panel-header">'+
        '<span class="obs-panel-num"></span>'+
        '<span class="obs-panel-section-id"></span>'+
        '<button type="button" class="obs-panel-close" aria-label="Close">'+
          '<svg viewBox="0 0 24 24"><line x1="5" y1="5" x2="19" y2="19"/><line x1="19" y1="5" x2="5" y2="19"/></svg>'+
        '</button>'+
      '</div>'+
      '<div class="obs-panel-body">'+
        '<div class="obs-panel-title"></div>'+
        '<div class="obs-panel-abstract"></div>'+
        '<div class="obs-panel-summary"></div>'+
        '<div class="obs-panel-findings-wrap">'+
          '<div class="obs-panel-findings-head">'+
            '<span class="obs-panel-findings-label">Findings</span>'+
            '<span class="obs-panel-findings-count"></span>'+
          '</div>'+
          '<ol class="obs-panel-findings"></ol>'+
        '</div>'+
        '<div class="obs-panel-meta">'+
          '<div class="obs-panel-meta-label">Source</div>'+
          '<div class="obs-panel-meta-val obs-panel-source"></div>'+
          '<a class="obs-panel-cta" href="#">'+
            '<svg viewBox="0 0 24 24"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>'+
            '<span>Jump to source</span>'+
          '</a>'+
        '</div>'+
      '</div>';
    document.body.appendChild(panel);

    function pageLabel(page){
      /* Turn "operator.html" → "The Operator's Cut". Falls back to the
         filename if the human title hasn't been indexed yet. */
      var map={
        'operator.html':"The Operator's Cut",
        'reserves.html':'Treasury & Pool Pots Distribution',
        'pools.html':'The Pools Pot Distribution Gaps',
        'census.html':'The Staking Census'
      };
      return map[page]||page;
    }
    function openPanel(ref){
      var canon=ref.getAttribute('data-obs-src');
      var data=srcIndex[canon];
      if(!data) return;
      panel.querySelector('.obs-panel-num').textContent=data.canon;
      panel.querySelector('.obs-panel-section-id').textContent='Source sub-report';
      panel.querySelector('.obs-panel-title').innerHTML=data.title;
      /* Abstract: an editorially-written reader-facing gloss of the whole
         observation. When present it replaces the auto-built summary. */
      var absEl=panel.querySelector('.obs-panel-abstract');
      if(data.abstract){
        absEl.style.display='';
        absEl.innerHTML=data.abstract;
      } else {
        absEl.style.display='none';
        absEl.innerHTML='';
      }
      /* The card summary is the first two findings concatenated — redundant
         with the findings list (or the abstract) when the panel is open.
         Keep the element for tooltip parity, but hide it here whenever we
         already have a richer source of signal. */
      var sumEl=panel.querySelector('.obs-panel-summary');
      var hasFindings=data.findingIds && data.findingIds.length;
      if(hasFindings || data.abstract){
        sumEl.innerHTML='';
        sumEl.style.display='none';
      } else {
        sumEl.style.display='';
        sumEl.innerHTML=data.summary;
      }
      panel.querySelector('.obs-panel-source').innerHTML=
        '<a href="'+data.href+'">'+pageLabel(data.page)+'</a>';

      /* Findings list: hydrate each finding from the bundled registry.
         If the registry entry is missing we still list the canonical id
         so the reader can see the coverage. */
      var list=panel.querySelector('.obs-panel-findings');
      list.innerHTML='';
      var ids=data.findingIds||[];
      panel.querySelector('.obs-panel-findings-count').textContent=
        ids.length ? ('('+ids.length+')') : '';
      if(!ids.length){
        var empty=document.createElement('li');
        empty.className='obs-panel-finding obs-panel-finding-empty';
        empty.textContent='No findings indexed for this observation.';
        list.appendChild(empty);
      } else {
        /* Stable hash → hue (0..359) so each insight/nature text always
           lands on the same colour across builds, matching the Python
           _nature_hue helper used by the Pro card on the main page.
           (Different hash function — md5 isn't available in the
           browser without async — but stable per-text and visually
           varied; the pill colour is a category cue, not a citation.) */
        function _panelHue(s){
          s=(s||'').trim().toLowerCase();
          var h=0;
          for(var i=0;i<s.length;i++){h=((h*31)+s.charCodeAt(i))|0;}
          return Math.abs(h)%360;
        }
        ids.forEach(function(fid,fi){
          var f=findingsIndex[fid];
          var li=document.createElement('li');
          li.className='obs-panel-finding';
          /* Two-line stack badge — \`#N\` ordinal + canonical ref —
             mirrors .sro-card-pro .sro-fid layout. The whole stack
             is wrapped in <a> when a source href is available so
             clicking the badge column navigates to the source. */
          var num='<span class="obs-panel-finding-num">#'+(fi+1)+'</span>';
          var ref='<span class="obs-panel-finding-id">'+fid+'</span>';
          var fid_html;
          if(f && f.href){
            fid_html='<a class="obs-panel-finding-fid" href="'+f.href+'" '+
              'aria-label="Jump to '+fid+'">'+num+ref+'</a>';
          } else {
            fid_html='<span class="obs-panel-finding-fid">'+num+ref+'</span>';
          }
          if(f){
            var insightTxt=(f.insight||'').replace(/<[^>]+>/g,'').trim();
            var hue=_panelHue(insightTxt);
            var insightPill=f.insight
              ? '<span class="obs-panel-finding-insight" style="--n-h:'+hue+'">'+f.insight+'</span>'
              : '';
            li.innerHTML=fid_html+
              '<div class="obs-panel-finding-body">'+
                '<div class="obs-panel-finding-summary">'+f.summary+'</div>'+
              '</div>'+
              insightPill;
          } else {
            li.innerHTML=fid_html+
              '<div class="obs-panel-finding-body">'+
                '<div class="obs-panel-finding-summary obs-panel-finding-missing">'+
                'Detail not bundled on this page.</div>'+
              '</div>';
          }
          list.appendChild(li);
        });
      }

      var cta=panel.querySelector('.obs-panel-cta');
      cta.setAttribute('href',data.href);
      document.body.classList.add('obs-panel-open');
      panel.setAttribute('aria-hidden','false');
    }
    function closePanel(){
      document.body.classList.remove('obs-panel-open');
      panel.setAttribute('aria-hidden','true');
    }
    overlay.addEventListener('click',closePanel);
    panel.querySelector('.obs-panel-close').addEventListener('click',closePanel);
    document.addEventListener('keydown',function(e){
      if(e.key==='Escape'&&document.body.classList.contains('obs-panel-open')) closePanel();
    });

    refs.forEach(function(ref){
      ref.addEventListener('click',function(e){
        e.preventDefault();
        hideTip();
        openPanel(ref);
      });
    });
  })();

  /* ── Reader feedback: overlay engagement events ──
     Provider-agnostic: calls into `window.spoTrack(name, propsFlat)`, a
     global injected by the analytics head bridge that maps to either
     Plausible or Umami transparently. No-op when no analytics provider
     is configured. The previous Useful / Not useful buttons on each
     finding row were dropped — discussion now happens on per-problem
     GitHub Discussion threads via the per-card "Discuss" CTA. */
  (function initReaderFeedback(){
    function track(name,props){
      if(typeof window.spoTrack==='function'){
        try{window.spoTrack(name,props||{});}catch(e){}
      }
    }
    var pageId=location.pathname.split('/').pop()||'index.html';
    document.addEventListener('click',function(ev){
      var t=ev.target;
      if(!t||!t.closest) return;
      var or=t.closest('.obs-ref, a.sro-obs-ref');
      if(or){
        var canon=or.getAttribute('data-obs')||or.getAttribute('data-obs-src')||
                   or.getAttribute('data-canon')||or.textContent.trim();
        track('Overlay Open',{kind:'observation',target:canon,page:pageId});
        return;
      }
      var fr=t.closest('.finding-ref');
      if(fr){
        var fid=fr.getAttribute('data-finding')||fr.textContent.trim();
        track('Overlay Open',{kind:'finding',target:fid,page:pageId});
      }
    },true);
  })();

  /* ── L1: Passive engagement events ──
     Captures scroll depth (25/50/75/100%), section dwell (>5s in
     viewport), and outbound link clicks. All routed through spoTrack so
     the analytics provider sees them as Plausible/Umami custom events.
     No-op when spoTrack is not defined. */
  (function initPassiveAnalytics(){
    function track(name,props){
      if(typeof window.spoTrack==='function'){
        try{window.spoTrack(name,props||{});}catch(e){}
      }
    }
    var pageId=location.pathname.split('/').pop()||'index.html';
    var ref=document.referrer||'(direct)';
    if(ref&&ref!=='(direct)'){
      try{ref=new URL(ref).hostname;}catch(e){}
    }

    /* Page view supplement — analytics scripts capture pageviews
       natively, but we add a "Page Entry" event with the referrer host
       so the dashboard can split editorial entries (Twitter/forum) from
       direct links and search engines. */
    track('Page Entry',{page:pageId,referrer:ref});

    /* Scroll depth — fire once per threshold, throttled. */
    var thresholds=[25,50,75,100];
    var hit={};
    function onScroll(){
      var doc=document.documentElement;
      var scrolled=(window.scrollY+window.innerHeight)/doc.scrollHeight*100;
      thresholds.forEach(function(t){
        if(!hit[t]&&scrolled>=t){
          hit[t]=true;
          track('Scroll Depth',{page:pageId,depth:t});
        }
      });
    }
    var raf=null;
    window.addEventListener('scroll',function(){
      if(raf) return;
      raf=requestAnimationFrame(function(){raf=null;onScroll();});
    },{passive:true});

    /* Section dwell — IntersectionObserver on every H2/H3, fires once
       per (page, sectionId) when the section has been ≥50% in viewport
       for 5 seconds cumulatively. */
    var DWELL_MS=5000;
    var dwell={};
    var sentDwell={};
    function tickDwell(){
      var now=Date.now();
      Object.keys(dwell).forEach(function(id){
        var d=dwell[id];
        if(d.visible){
          d.acc+=now-(d.lastTick||now);
          d.lastTick=now;
          if(!sentDwell[id]&&d.acc>=DWELL_MS){
            sentDwell[id]=true;
            track('Section Read',{page:pageId,section:id,
              ms:Math.round(d.acc)});
          }
        }
      });
    }
    setInterval(tickDwell,1500);
    if('IntersectionObserver' in window){
      var io=new IntersectionObserver(function(entries){
        entries.forEach(function(e){
          var id=e.target.id;
          if(!id) return;
          if(!dwell[id]) dwell[id]={acc:0,visible:false};
          if(e.isIntersecting){
            dwell[id].visible=true;
            dwell[id].lastTick=Date.now();
          }else{
            dwell[id].visible=false;
          }
        });
      },{threshold:0.5});
      document.querySelectorAll('h2[id], h3[id]').forEach(function(h){
        io.observe(h);
      });
    }

    /* Outbound link clicks — anything not on the same host. */
    document.addEventListener('click',function(ev){
      var a=ev.target&&ev.target.closest&&ev.target.closest('a[href]');
      if(!a) return;
      var href=a.getAttribute('href')||'';
      if(!/^https?:\/\//.test(href)) return;
      try{
        var u=new URL(href);
        if(u.host!==location.host){
          track('Outbound Click',{page:pageId,host:u.host,
            url:u.origin+u.pathname});
        }
      }catch(e){}
    },true);
  })();

  /* ── L3 + L4: Selection FAB — Highlight + Quote ──
     Floating action bar that appears when the reader selects ≥3
     characters of text inside `.content`. Two actions:
     - Highlight: persists in localStorage under spo:hl:<page>
     - Quote: copies a markdown blockquote with permalink to the
       clipboard and fires a Plausible custom event. */
  (function initSelectionFab(){
    var body=document.body;
    if(!body) return;
    var hlEnabled=body.getAttribute('data-highlights')==='1';
    var content=document.querySelector('.content');
    if(!content) return;

    var fab=document.createElement('div');
    fab.className='spo-selfab';
    fab.setAttribute('role','toolbar');
    fab.style.display='none';
    fab.innerHTML=
      '<button type="button" data-act="quote" title="Copy as Markdown quote">'
      +'<svg viewBox="0 0 16 16"><path d="M3 5h4v4H4v2H3V5zm6 0h4v4h-3v2H9V5z"/></svg>'
      +'<span>Quote</span></button>'
      +(hlEnabled?
        '<button type="button" data-act="hl" title="Highlight (saved in this browser)">'
        +'<svg viewBox="0 0 16 16"><path d="M2 12l3-3 5 5-3 3H2v-5zm5-5l5-5 4 4-5 5-4-4z"/></svg>'
        +'<span>Highlight</span></button>'
        :'');
    document.body.appendChild(fab);

    var pageId=location.pathname.split('/').pop()||'index.html';
    var HL_KEY='spo:hl:'+pageId;

    function track(name,props){
      if(typeof window.spoTrack==='function'){
        try{window.spoTrack(name,props||{});}catch(e){}
      }
    }

    function getSelText(){
      var s=window.getSelection();
      if(!s||s.rangeCount===0||s.isCollapsed) return null;
      var r=s.getRangeAt(0);
      if(!content.contains(r.commonAncestorContainer)) return null;
      var txt=s.toString().trim();
      if(txt.length<3) return null;
      return {sel:s,range:r,text:txt};
    }

    function findEnclosingFinding(node){
      while(node&&node!==document){
        if(node.classList&&node.classList.contains('sro-finding')){
          return node.getAttribute('data-finding');
        }
        if(node.tagName==='H2'||node.tagName==='H3'){
          return node.id||null;
        }
        node=node.parentNode;
      }
      return null;
    }

    function permalink(node){
      var anchor=findEnclosingFinding(node);
      var base=location.origin+location.pathname;
      return anchor?(base+'#'+anchor):base;
    }

    function showFab(){
      var info=getSelText();
      if(!info){fab.style.display='none';return;}
      var rect=info.range.getBoundingClientRect();
      fab.style.display='flex';
      var top=window.scrollY+rect.top-fab.offsetHeight-8;
      if(top<window.scrollY+8) top=window.scrollY+rect.bottom+8;
      var left=window.scrollX+rect.left+(rect.width/2)-(fab.offsetWidth/2);
      var maxLeft=window.scrollX+window.innerWidth-fab.offsetWidth-8;
      if(left<window.scrollX+8) left=window.scrollX+8;
      if(left>maxLeft) left=maxLeft;
      fab.style.top=top+'px';
      fab.style.left=left+'px';
    }

    document.addEventListener('mouseup',function(){setTimeout(showFab,1);});
    document.addEventListener('selectionchange',function(){
      if(window.getSelection().isCollapsed) fab.style.display='none';
    });
    document.addEventListener('scroll',function(){
      if(fab.style.display!=='none') showFab();
    },{passive:true});

    fab.addEventListener('mousedown',function(ev){ev.preventDefault();});

    fab.addEventListener('click',function(ev){
      var btn=ev.target.closest('button[data-act]');
      if(!btn) return;
      var info=getSelText();
      if(!info) return;
      var act=btn.getAttribute('data-act');
      var anchor=findEnclosingFinding(info.range.commonAncestorContainer);
      var url=permalink(info.range.commonAncestorContainer);

      if(act==='quote'){
        var citation=anchor?('— ['+anchor+']('+url+')'):('— ['+pageId+']('+url+')');
        var md='> '+info.text.replace(/\n/g,'\n> ')+'\n\n'+citation+'\n';
        if(navigator.clipboard&&navigator.clipboard.writeText){
          navigator.clipboard.writeText(md).then(function(){
            flashFab(btn,'Copied');
            track('Quote Copied',{page:pageId,anchor:anchor||'(none)',
              len:info.text.length});
          },function(){flashFab(btn,'Failed');});
        }else{flashFab(btn,'No clipboard');}
      }else if(act==='hl'){
        var rangeKey=anchor||'_';
        var store={};
        try{store=JSON.parse(localStorage.getItem(HL_KEY)||'{}');}catch(e){}
        if(!store[rangeKey]) store[rangeKey]=[];
        store[rangeKey].push({text:info.text,ts:Date.now()});
        try{localStorage.setItem(HL_KEY,JSON.stringify(store));}catch(e){}
        applyHighlight(info.range);
        flashFab(btn,'Saved');
        track('Highlight Saved',{page:pageId,anchor:anchor||'(none)',
          len:info.text.length});
      }
      window.getSelection().removeAllRanges();
      fab.style.display='none';
    });

    function flashFab(btn,label){
      var span=btn.querySelector('span');
      var prev=span.textContent;
      span.textContent=label;
      btn.classList.add('spo-selfab-flash');
      setTimeout(function(){
        span.textContent=prev;
        btn.classList.remove('spo-selfab-flash');
      },900);
    }

    function applyHighlight(range){
      try{
        var mark=document.createElement('mark');
        mark.className='spo-hl';
        range.surroundContents(mark);
      }catch(e){
        /* range crosses element boundaries — fall back to wrapping text
           runs individually via TreeWalker. Skipped here for brevity:
           the simple surroundContents covers single-paragraph picks. */
      }
    }

    /* Re-apply persisted highlights on load. We use a coarse text-match
       strategy rather than DOM-Range serialization: each saved snippet
       is searched for in the current text content of its anchor scope.
       Imperfect (skips duplicate matches, fails after edits) but
       privacy-clean and dependency-free. */
    if(hlEnabled){
      try{
        var saved=JSON.parse(localStorage.getItem(HL_KEY)||'{}');
        Object.keys(saved).forEach(function(anchorId){
          var scope=document;
          if(anchorId!=='_'){
            scope=document.querySelector(
              '[data-finding="'+anchorId+'"], #'+CSS.escape(anchorId)
            )||document;
          }
          (saved[anchorId]||[]).forEach(function(rec){
            highlightText(scope,rec.text);
          });
        });
      }catch(e){}
    }

    function highlightText(scope,needle){
      if(!needle||needle.length<3) return;
      var walker=document.createTreeWalker(scope,NodeFilter.SHOW_TEXT,null);
      var node;
      while((node=walker.nextNode())){
        var idx=node.nodeValue.indexOf(needle);
        if(idx>=0){
          var r=document.createRange();
          r.setStart(node,idx);
          r.setEnd(node,idx+needle.length);
          var mark=document.createElement('mark');
          mark.className='spo-hl';
          try{r.surroundContents(mark);}catch(e){}
          return;
        }
      }
    }
  })();

  /* ── L5: Bookmarks per .sro-finding ──
     Adds a "Save" button to each finding's reactions row. Clicking
     stores a record in localStorage; clicking again removes it. The
     /my-bookmarks.html page reads this storage on load and renders a
     consolidated list across all sub-reports. */
  (function initBookmarks(){
    var body=document.body;
    if(!body||body.getAttribute('data-bookmarks')!=='1') return;
    var BK_KEY='spo:bk';
    var pageId=location.pathname.split('/').pop()||'index.html';

    function load(){
      try{return JSON.parse(localStorage.getItem(BK_KEY)||'{}');}
      catch(e){return {};}
    }
    function save(s){try{localStorage.setItem(BK_KEY,JSON.stringify(s));}
      catch(e){}}

    function track(n,p){
      if(typeof window.spoTrack==='function'){
        try{window.spoTrack(n,p||{});}catch(e){}
      }
    }

    function isSaved(canon){
      var s=load(); return !!(s[canon]);
    }
    function toggleSave(canon,title,evidence){
      var s=load();
      if(s[canon]){delete s[canon];}
      else{
        s[canon]={page:pageId,title:title||'',evidence:evidence||'',
          ts:Date.now()};
      }
      save(s);
      return !!s[canon];
    }

    var SVG_BK='<svg viewBox="0 0 16 16" aria-hidden="true">'
      +'<path d="M3 2h10v12l-5-3-5 3V2z"/></svg>';

    function makeBtn(canon,title,evidence){
      var b=document.createElement('button');
      b.type='button';
      b.className='spo-bookmark-btn';
      b.setAttribute('data-finding',canon);
      b.setAttribute('aria-pressed',isSaved(canon)?'true':'false');
      b.innerHTML=SVG_BK+'<span>'+(isSaved(canon)?'Saved':'Save')+'</span>';
      if(isSaved(canon)) b.classList.add('is-active');
      b.addEventListener('click',function(ev){
        ev.preventDefault();ev.stopPropagation();
        var nowSaved=toggleSave(canon,title,evidence);
        b.classList.toggle('is-active',nowSaved);
        b.setAttribute('aria-pressed',nowSaved?'true':'false');
        b.querySelector('span').textContent=nowSaved?'Saved':'Save';
        track(nowSaved?'Bookmark Added':'Bookmark Removed',
          {page:pageId,finding:canon});
      });
      return b;
    }

    document.querySelectorAll('.sro-finding[data-finding]').forEach(function(li){
      if(li.querySelector('.spo-bookmark-btn')) return;
      var canon=li.getAttribute('data-finding');
      var title=(li.querySelector('.sro-evidence')||{}).textContent||'';
      var meta=li.querySelector('.sro-meta');
      var btn=makeBtn(canon,title.substring(0,140),title);
      if(meta){meta.appendChild(btn);}
      else{li.appendChild(btn);}
    });
  })();

  /* ── L6: Structured form — async submit + status feedback ──
     The form is a plain HTML POST so it works without JS; this layer
     just prevents the redirect, posts via fetch, and renders inline
     success/error feedback. */
  (function initStructuredForm(){
    var section=document.querySelector('.page-form[data-form-endpoint]');
    if(!section) return;
    var form=section.querySelector('form');
    var status=section.querySelector('.page-form-status');
    var pageInput=form.querySelector('input[name="_page"]');
    if(pageInput) pageInput.value=location.pathname.split('/').pop()||'index.html';

    function track(n,p){
      if(typeof window.spoTrack==='function'){
        try{window.spoTrack(n,p||{});}catch(e){}
      }
    }

    form.addEventListener('submit',function(ev){
      ev.preventDefault();
      var btn=form.querySelector('button[type=submit]');
      btn.disabled=true;
      status.textContent='Sending…';
      status.className='page-form-status';
      var data=new FormData(form);
      fetch(form.action,{method:'POST',body:data,
        headers:{'Accept':'application/json'}})
        .then(function(r){
          if(r.ok){
            status.textContent='Thanks — your feedback was sent.';
            status.classList.add('is-ok');
            form.reset();
            track('Form Submitted',{page:pageInput?pageInput.value:''});
          }else{
            status.textContent='Send failed — try again or post on Discussions.';
            status.classList.add('is-err');
          }
        }).catch(function(){
          status.textContent='Network error — your message was not sent.';
          status.classList.add('is-err');
        }).finally(function(){btn.disabled=false;});
    });
  })();

  /* ── L7: Q&A inline — Ask the authors per finding ──
     When data-qa-endpoint is set on body, attaches an "Ask the authors"
     button to each .sro-finding. Click opens an inline composer; submit
     POSTs to the configured Worker endpoint. The Worker stores the
     question in KV and emails the team. Any answers (manually approved)
     come back via GET and render inline below the finding. */
  (function initQA(){
    var body=document.body;
    if(!body) return;
    var endpoint=body.getAttribute('data-qa-endpoint');
    if(!endpoint) return;
    var pageId=location.pathname.split('/').pop()||'index.html';

    function track(n,p){
      if(typeof window.spoTrack==='function'){
        try{window.spoTrack(n,p||{});}catch(e){}
      }
    }

    function fetchAnswers(canon,host){
      fetch(endpoint.replace(/\/$/,'')+'/qa/'+encodeURIComponent(canon))
        .then(function(r){return r.ok?r.json():{answers:[]};})
        .then(function(data){
          var answers=(data&&data.answers)||[];
          if(!answers.length) return;
          var box=document.createElement('div');
          box.className='spo-qa-answers';
          box.innerHTML='<h4>Authors\' answers</h4>'+
            answers.map(function(a){
              return '<article class="spo-qa-answer">'
                +'<div class="spo-qa-answer-meta">'
                +(a.author||'IO Research')+' · '
                +(a.date||'')+'</div>'
                +'<div class="spo-qa-answer-body">'+(a.html||a.text||'')+'</div>'
                +'</article>';
            }).join('');
          host.appendChild(box);
        }).catch(function(){});
    }

    function attachComposer(canon,host){
      var open=document.createElement('button');
      open.type='button';
      open.className='spo-qa-open';
      open.innerHTML='<svg viewBox="0 0 16 16" aria-hidden="true">'
        +'<path d="M3 4h10v7H7l-3 3v-3H3V4zm2 2v1h6V6H5zm0 3v1h4V9H5z"/></svg>'
        +'<span>Ask the authors</span>';
      host.appendChild(open);
      open.addEventListener('click',function(){
        if(host.querySelector('.spo-qa-form')){return;}
        var form=document.createElement('form');
        form.className='spo-qa-form';
        form.innerHTML=
          '<label>Your question about this finding<textarea name="q" rows="3" required></textarea></label>'
          +'<label>Email <small>(optional, for the reply)</small><input type="email" name="email" autocomplete="off"></label>'
          +'<div class="spo-qa-actions">'
          +'<button type="button" class="spo-qa-cancel">Cancel</button>'
          +'<button type="submit" class="spo-qa-submit">Send question</button>'
          +'</div>'
          +'<p class="spo-qa-status" aria-live="polite"></p>';
        host.appendChild(form);
        form.querySelector('.spo-qa-cancel').addEventListener('click',
          function(){form.remove();});
        form.addEventListener('submit',function(ev){
          ev.preventDefault();
          var status=form.querySelector('.spo-qa-status');
          var btn=form.querySelector('.spo-qa-submit');
          btn.disabled=true;status.textContent='Sending…';
          var fd=new FormData(form);
          fd.append('finding',canon);
          fd.append('page',pageId);
          fetch(endpoint.replace(/\/$/,'')+'/qa',{
            method:'POST',body:fd,
            headers:{'Accept':'application/json'}
          }).then(function(r){
            if(r.ok){
              status.textContent='Thanks — we will reply on this finding.';
              status.classList.add('is-ok');
              form.querySelector('textarea').value='';
              track('QA Asked',{page:pageId,finding:canon});
            }else{
              status.textContent='Submit failed.';
              status.classList.add('is-err');
            }
          }).catch(function(){
            status.textContent='Network error.';
            status.classList.add('is-err');
          }).finally(function(){btn.disabled=false;});
        });
      });
    }

    document.querySelectorAll('.sro-finding[data-finding]').forEach(function(li){
      if(li.querySelector('.spo-qa-open')) return;
      var canon=li.getAttribute('data-finding');
      var host=document.createElement('div');
      host.className='spo-qa-host';
      li.appendChild(host);
      attachComposer(canon,host);
      fetchAnswers(canon,host);
    });
  })();

  /* ── Pro observation card — header collapse ──
     Click anywhere on the .sro-head row to fold/unfold the body
     (FINDINGS label + findings list; abstract stays visible).

     Default state = collapsed (the markup ships .collapsed on every
     card). localStorage tracks user overrides:
       state[id] === '0' → user explicitly expanded
       state[id] === '1' → user explicitly collapsed
       absent           → fall back to the default (collapsed)
     so the user's expansions persist but cards they never touched
     stay folded on every visit. */
  (function initCardCollapse(){
    var heads=document.querySelectorAll('.sro-card-pro > .sro-head');
    if(!heads.length) return;
    var KEY='spo:findings-collapsed';
    function load(){
      try{return JSON.parse(localStorage.getItem(KEY)||'{}');}
      catch(e){return {};}
    }
    function save(state){
      try{localStorage.setItem(KEY,JSON.stringify(state));}catch(e){}
    }
    var state=load();
    heads.forEach(function(head){
      var card=head.parentElement;
      if(!card||!card.classList.contains('sro-card-pro')) return;
      var id=card.id||card.getAttribute('data-obs')||'';
      head.setAttribute('role','button');
      head.setAttribute('tabindex','0');
      function apply(collapsed){
        card.classList.toggle('collapsed',collapsed);
        head.setAttribute('aria-expanded',collapsed?'false':'true');
      }
      /* Reconcile the markup default (collapsed) with any persisted
         user override. */
      if(id && state[id]==='0') apply(false);
      else apply(true);
      function toggle(ev){
        /* Don't toggle when the click lands on a link inside the
           header (the brand badge or any future header link). */
        if(ev && ev.target && ev.target.closest('a')) return;
        var willCollapse=!card.classList.contains('collapsed');
        apply(willCollapse);
        if(id){
          state[id]=willCollapse?'1':'0';
          save(state);
        }
      }
      head.addEventListener('click',toggle);
      head.addEventListener('keydown',function(e){
        if(e.key==='Enter'||e.key===' '){
          e.preventDefault();toggle(e);
        }
      });
    });
    /* When the page loads (or the hash changes) with a fragment that
       points at a .sro-finding inside a collapsed .sro-card-pro, force
       the parent card open so the target is visible. Persist the open
       state so the user-expanded card stays open after they've come
       in via a deep link. */
    function expandToHash(){
      var hash=location.hash;
      if(!hash||hash.length<2) return;
      var target;
      try{target=document.querySelector(hash);}catch(e){return;}
      /* If the link points at \`#finding-cen-o1-f1\` but no callout
         carries that id (the prose description hasn't been written
         yet), fall back to the visual Pro card row \`#cen-o1-f1\`
         and rewrite the URL silently so a refresh keeps working. */
      if(!target && hash.indexOf('#finding-')===0){
        var rowHash='#'+hash.slice('#finding-'.length);
        try{target=document.querySelector(rowHash);}catch(e){return;}
        if(target){
          try{history.replaceState(null,'',rowHash);}catch(e){}
        }
      }
      if(!target) return;
      var card=target.closest('.sro-card-pro');
      if(!card||!card.classList.contains('collapsed')) return;
      card.classList.remove('collapsed');
      var head2=card.querySelector('.sro-head');
      if(head2) head2.setAttribute('aria-expanded','true');
      var id=card.id||card.getAttribute('data-obs')||'';
      if(id){state[id]='0';save(state);}
      setTimeout(function(){
        try{target.scrollIntoView({block:'start'});}catch(e){}
      },10);
    }
    expandToHash();
    window.addEventListener('hashchange',expandToHash);
  })();
  /* ── /Pro observation card — header collapse ── */
  /* ── /Cross-page synthesis-observation source overlay ── */

/* ── Problem-statements page — carousel mode ── */
  (function(){
    document.addEventListener('DOMContentLoaded', function(){
      var list = document.querySelector('.findings-list');
      if (!list) return;
      var cards = Array.prototype.slice.call(list.querySelectorAll('.finding-card'));
      if (cards.length < 2) return;
      var indexLinks = Array.prototype.slice.call(document.querySelectorAll('.findings-toc-item'));
      list.classList.add('findings-list--carousel');

      var nav = document.createElement('div');
      nav.className = 'findings-carousel-nav';
      nav.setAttribute('role','navigation');
      nav.setAttribute('aria-label','Problem carousel');
      nav.innerHTML =
        '<button type="button" class="findings-carousel-btn findings-carousel-prev" aria-label="Previous problem">'+
          '<span class="findings-carousel-arrow" aria-hidden="true">&larr;</span> Prev'+
        '</button>'+
        '<div class="findings-carousel-meta" aria-live="polite">'+
          '<span class="findings-carousel-group"></span>'+
          '<span class="findings-carousel-counter"></span>'+
        '</div>'+
        '<button type="button" class="findings-carousel-btn findings-carousel-next" aria-label="Next problem">'+
          'Next <span class="findings-carousel-arrow" aria-hidden="true">&rarr;</span>'+
        '</button>';
      list.parentNode.insertBefore(nav, list);

      // Mirror the same nav below the cards so users can navigate without
      // scrolling back up after reading a long card.
      var navBottom = nav.cloneNode(true);
      navBottom.classList.add('findings-carousel-nav-bottom');
      list.parentNode.insertBefore(navBottom, list.nextSibling);

      var prevBtns = [nav.querySelector('.findings-carousel-prev'), navBottom.querySelector('.findings-carousel-prev')];
      var nextBtns = [nav.querySelector('.findings-carousel-next'), navBottom.querySelector('.findings-carousel-next')];
      var counterEls = [nav.querySelector('.findings-carousel-counter'), navBottom.querySelector('.findings-carousel-counter')];
      var groupEls = [nav.querySelector('.findings-carousel-group'), navBottom.querySelector('.findings-carousel-group')];
      var currentIdx = 0;

      function indexOfId(id){
        for (var i=0;i<cards.length;i++){ if(cards[i].id===id) return i; }
        return -1;
      }

      function activate(idx, opts){
        opts = opts || {};
        if (idx < 0 || idx >= cards.length) return;
        currentIdx = idx;
        cards.forEach(function(c){ c.classList.remove('is-active'); });
        var card = cards[idx];
        card.classList.add('is-active');

        // Highlight matching TOC item
        indexLinks.forEach(function(a){
          a.classList.toggle('is-active', a.getAttribute('href') === '#' + card.id);
        });

        // Update counter — show μ##/M## token + index/total
        var idLink = null;
        for (var i=0;i<indexLinks.length;i++){
          if (indexLinks[i].getAttribute('href') === '#' + card.id){ idLink = indexLinks[i]; break; }
        }
        var idTok = idLink ? (idLink.querySelector('.findings-toc-num') || {}).textContent : '';
        var counterHtml = '<span class="findings-carousel-counter-id">'+
          (idTok || '')+'</span><strong>'+(idx+1)+'</strong> / '+cards.length;
        counterEls.forEach(function(el){ if(el) el.innerHTML = counterHtml; });

        // Update group label from the enclosing section's title
        var section = card.closest('.findings-group');
        var groupTitle = section ? section.querySelector('.findings-group-title-text') : null;
        var groupText = groupTitle ? groupTitle.textContent : '';
        groupEls.forEach(function(el){ if(el) el.textContent = groupText; });

        // Buttons (top + bottom)
        prevBtns.forEach(function(b){ if(b) b.disabled = (idx === 0); });
        nextBtns.forEach(function(b){ if(b) b.disabled = (idx === cards.length - 1); });

        // Update hash without scroll-jump
        if (!opts.silent && card.id){
          try{ history.replaceState(null, '', '#' + card.id); }catch(e){}
        }

        // Scroll to nav when navigation came from outside the carousel
        if (opts.scroll){
          try{ nav.scrollIntoView({ block:'start', behavior:'smooth' }); }catch(e){
            try{ nav.scrollIntoView(); }catch(e2){}
          }
        }
      }

      prevBtns.forEach(function(b){
        if(b) b.addEventListener('click', function(){
          if(currentIdx>0) activate(currentIdx-1, { scroll:b===prevBtns[1] });
        });
      });
      nextBtns.forEach(function(b){
        if(b) b.addEventListener('click', function(){
          if(currentIdx<cards.length-1) activate(currentIdx+1, { scroll:b===nextBtns[1] });
        });
      });

      indexLinks.forEach(function(a){
        a.addEventListener('click', function(e){
          var href = a.getAttribute('href') || '';
          if (href[0] !== '#') return;
          var idx = indexOfId(href.slice(1));
          if (idx < 0) return;
          e.preventDefault();
          activate(idx, { scroll:true });
        });
      });

      document.addEventListener('keydown', function(e){
        if (e.target && /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName)) return;
        if (e.target && e.target.isContentEditable) return;
        if (e.metaKey || e.ctrlKey || e.altKey) return;
        if (e.key === 'ArrowLeft' && currentIdx > 0){ activate(currentIdx-1); }
        else if (e.key === 'ArrowRight' && currentIdx < cards.length-1){ activate(currentIdx+1); }
      });

      function syncHash(){
        var hash = (window.location.hash || '').replace('#','');
        if (!hash) return;
        var idx = indexOfId(hash);
        if (idx < 0) return;
        activate(idx, { silent:true });
      }

      // Inject a per-card "Discuss" CTA. The Discussion URL is baked
      // into the article's `data-discussion-href` attribute by
      // `build_site.py` via `scripts/bootstrap_giscus_discussions.py`'s
      // mapping JSON — no runtime fetch.
      var GH_OCTICON =
        '<svg class="finding-card-discuss-icon" viewBox="0 0 16 16" aria-hidden="true">'+
          '<path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 '+
          '5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49'+
          '-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 '+
          '1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78'+
          '-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08'+
          '-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 '+
          '1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 '+
          '2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 '+
          '1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58'+
          '-8-8-8z"/></svg>';

      cards.forEach(function(card){
        if (!card.id) return;
        if (card.querySelector('.finding-card-discuss')) return;
        var href = card.getAttribute('data-discussion-href');
        if (!href) return;
        var cta = document.createElement('a');
        cta.className = 'finding-card-discuss';
        cta.target = '_blank';
        cta.rel = 'noopener';
        cta.href = href;
        cta.innerHTML = GH_OCTICON +
          '<span class="finding-card-discuss-text">Discuss</span>'+
          '<span class="finding-card-discuss-arrow" aria-hidden="true">&#x2197;</span>';
        var bannerEl = card.querySelector('.finding-card-banner') || card.querySelector('.finding-card-content') || card;
        bannerEl.appendChild(cta);
        if (bannerEl.classList && bannerEl.classList.contains('finding-card-banner')) bannerEl.classList.add('has-discuss');
      });

      activate(0, { silent:true });
      syncHash();
      window.addEventListener('hashchange', syncHash);
    });
  })();
  /* ── /Problem-statements page — carousel mode ── */

})();
