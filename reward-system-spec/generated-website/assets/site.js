(function(){
/* ── Theme toggle ── */
  window.toggleTheme=function(){
    var html=document.documentElement;
    var current=html.getAttribute('data-theme');
    var next=current==='dark'?'light':'dark';
    html.setAttribute('data-theme',next);
    try{ localStorage.setItem('spo-theme',next); }catch(e){}
    updateThemeIcon();
  };
  function updateThemeIcon(){
    var btn=document.querySelector('.theme-toggle');
    if(!btn) return;
    var isDark=document.documentElement.getAttribute('data-theme')==='dark';
    btn.textContent=isDark?'☀':'☾';
    btn.title=isDark?'Switch to light theme':'Switch to dark theme';
  }
  (function initTheme(){
    var saved;
    try{ saved=localStorage.getItem('spo-theme'); }catch(e){}
    if(saved) document.documentElement.setAttribute('data-theme',saved);
    updateThemeIcon();
  })();

  /* ── PDF export: expand everything, then print.
        beforeprint/afterprint also handle Ctrl+P so manual prints work too. ── */
  window.printAsPdf=function(){
    /* Expand all collapsed sections, obs-cards, TOC subtrees before printing.
       A tiny delay lets MathJax / Mermaid / layout settle. */
    window.print();
  };
  function expandAllForPrint(){
    var restore=[];
    document.querySelectorAll('.section-body.collapsed, .section-toggle.collapsed').forEach(function(el){
      el.classList.remove('collapsed');
      restore.push(el);
    });
    document.querySelectorAll('.section-body').forEach(function(el){
      el.style.maxHeight='none';
    });
    document.querySelectorAll('.obs-card.collapsed').forEach(function(el){
      el.classList.remove('collapsed');
      restore.push(el);
    });
    document.querySelectorAll('.toc-collapsed').forEach(function(el){
      el.classList.remove('toc-collapsed');
      el.setAttribute('data-was-toc-collapsed','1');
      restore.push(el);
    });
    document.querySelectorAll('.toc-toggle.collapsed').forEach(function(el){
      el.classList.remove('collapsed');
      el.setAttribute('data-was-toc-collapsed','1');
      restore.push(el);
    });
    window._printRestore=restore;
  }
  function restoreAfterPrint(){
    var restore=window._printRestore||[];
    restore.forEach(function(el){
      if(el.hasAttribute('data-was-toc-collapsed')){
        el.removeAttribute('data-was-toc-collapsed');
        if(el.classList.contains('toc-toggle')) el.classList.add('collapsed');
        else el.classList.add('toc-collapsed');
      }
    });
    window._printRestore=null;
  }
  window.addEventListener('beforeprint',expandAllForPrint);
  window.addEventListener('afterprint',restoreAfterPrint);

  /* ── Dropdown helpers ── */
  window.closeAllDd=function(except){
    document.querySelectorAll('.nav-dd-wrap.open').forEach(function(w){
      if(!w.contains(except)) w.classList.remove('open');
    });
  };
  document.addEventListener('click',function(){ closeAllDd(null); });

  /* ── Progress bar ── */
  const bar=document.getElementById('progress');
  function updateProgress(){
    const h=document.documentElement.scrollHeight-window.innerHeight;
    bar.style.width=h>0?((window.scrollY/h)*100)+'%':'0%';
  }

  /* ── Back to top ── */
  const btt=document.getElementById('btt');
  function updateBtt(){ btt.classList.toggle('visible',window.scrollY>400); }

  window.addEventListener('scroll',function(){ updateProgress(); updateBtt(); },{passive:true});
  updateProgress();

  /* ── Smooth scroll for anchor links ── */
  document.addEventListener('click',function(e){
    const a=e.target.closest('a[href^="#"]');
    if(!a) return;
    const id=a.getAttribute('href').slice(1);
    const el=document.getElementById(id);
    if(el){ e.preventDefault(); el.scrollIntoView({behavior:'smooth',block:'start'}); history.pushState(null,null,'#'+id); }
  });

  /* ── TOC floating panel ── */
  (function initTocPanel(){
    var inlineToc=document.querySelector('.content > .toc-nav')
      || document.querySelector('.content .toc-nav');
    if(!inlineToc) return;

    /* Mark body so CSS hides the inline block */
    document.body.classList.add('has-toc-panel');

    /* Build FAB */
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

    /* Build overlay */
    var overlay=document.createElement('div');
    overlay.className='toc-overlay';
    overlay.setAttribute('aria-hidden','true');
    document.body.appendChild(overlay);

    /* Build panel */
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
    /* Clone the inline TOC BEFORE other decorators (toc-toggle, section-toggle) touch it */
    var cloned=inlineToc.cloneNode(true);
    /* Strip any pre-existing decoration from the clone */
    cloned.querySelectorAll('.toc-toggle').forEach(function(el){
      el.classList.remove('toc-toggle','collapsed');
    });
    cloned.querySelectorAll('.toc-collapsed').forEach(function(el){
      el.classList.remove('toc-collapsed');
    });
    cloned.querySelectorAll('li.has-children').forEach(function(el){
      el.classList.remove('has-children');
    });
    body.appendChild(cloned);
    panel.appendChild(header);
    panel.appendChild(body);
    document.body.appendChild(panel);

    /* Open/close */
    function openPanel(){
      document.body.classList.add('toc-open');
      panel.setAttribute('aria-hidden','false');
      overlay.setAttribute('aria-hidden','false');
    }
    function closePanel(){
      document.body.classList.remove('toc-open');
      panel.setAttribute('aria-hidden','true');
      overlay.setAttribute('aria-hidden','true');
    }
    fab.addEventListener('click',function(e){ e.stopPropagation(); openPanel(); });
    overlay.addEventListener('click',closePanel);
    header.querySelector('.toc-panel-close').addEventListener('click',closePanel);
    document.addEventListener('keydown',function(e){
      if(e.key==='Escape' && document.body.classList.contains('toc-open')) closePanel();
    });

    /* Clicking a link inside the panel: expand any collapsed ancestor,
       close the panel, then let the global smooth-scroll handle the scroll. */
    cloned.querySelectorAll('a[href^="#"]').forEach(function(a){
      a.addEventListener('click',function(){
        var id=a.getAttribute('href').slice(1);
        var target=document.getElementById(id);
        if(target){
          /* Walk up and click every collapsed .section-toggle ancestor to expand it */
          var cur=target;
          var toExpand=[];
          while(cur && cur!==document.body){
            if(cur.classList && cur.classList.contains('section-body') && cur.classList.contains('collapsed')){
              var toggle=cur.previousElementSibling;
              if(toggle && toggle.classList.contains('section-toggle')) toExpand.push(toggle);
            }
            cur=cur.parentElement;
          }
          /* Expand from outermost inward */
          toExpand.reverse().forEach(function(t){ t.click(); });
        }
        setTimeout(closePanel,50);
      });
    });

    /* ── Scroll-spy: highlight the current section ── */
    var links=Array.from(cloned.querySelectorAll('a[href^="#"]'));
    var map=[]; /* [{id, link, el}] in document order */
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

  /* ── Collapsible TOC sub-lists (all levels) — inline only, not panel clone ── */
  document.querySelectorAll('.content .toc-nav li').forEach(function(li){
    var sub=li.querySelector(':scope > ul, :scope > ol');
    if(!sub) return;
    li.classList.add('has-children');
    var toggle=li.querySelector(':scope > .toc-num')||li.querySelector(':scope > a');
    if(!toggle) return;
    toggle.classList.add('toc-toggle');
    toggle.addEventListener('click',function(e){
      e.preventDefault();
      e.stopPropagation();
      toggle.classList.toggle('collapsed');
      sub.classList.toggle('toc-collapsed');
    });
  });

  /* ── Collapsible content sections (h2, h3, h4) ── */
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

  /* ── Wrap tables in scroll containers ── */
  document.querySelectorAll('.content table').forEach(function(tbl){
    if(tbl.parentElement.classList.contains('table-wrap')) return;
    var wrap=document.createElement('div');
    wrap.className='table-wrap';
    tbl.parentNode.insertBefore(wrap,tbl);
    wrap.appendChild(tbl);
  });

  /* ── Image lightbox ── */
  const overlay=document.getElementById('lightbox');
  const lbImg=document.getElementById('lb-img');
  document.querySelectorAll('.content img').forEach(function(img){
    img.addEventListener('click',function(){
      lbImg.src=img.src;
      lbImg.alt=img.alt||'';
      overlay.classList.add('active');
    });
  });
  overlay.addEventListener('click',function(){ overlay.classList.remove('active'); lbImg.src=''; });
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape' && overlay.classList.contains('active')){
      overlay.classList.remove('active'); lbImg.src='';
    }
  });

  /* ── Observation findings → navigate to section ── */
  document.querySelectorAll('.obs-link[data-section]').forEach(function(el){
    el.addEventListener('click',function(){
      var sec=el.getAttribute('data-section');
      /* Find heading whose id starts with the section number */
      var target=document.querySelector('h2[id^="'+sec+'-"],h3[id^="'+sec+'-"],h4[id^="'+sec+'-"],h5[id^="'+sec+'-"]');
      if(!target) target=document.getElementById(sec);
      if(target){
        /* Expand collapsed parent section if needed */
        var body=target.closest('.section-body.collapsed');
        if(body){
          var toggle=body.previousElementSibling;
          if(toggle && toggle.classList.contains('section-toggle')) toggle.click();
        }
        setTimeout(function(){ target.scrollIntoView({behavior:'smooth',block:'start'}); },150);
      }
    });
  });

  /* ── Mermaid zoom overlay ── */
  (function initMermaidZoom(){
    /* Build overlay once */
    var zoomOverlay=document.createElement('div');
    zoomOverlay.className='mermaid-zoom-overlay';
    zoomOverlay.setAttribute('aria-hidden','true');
    var stage=document.createElement('div');
    stage.className='mermaid-zoom-stage';
    var controls=document.createElement('div');
    controls.className='mermaid-zoom-controls';
    controls.innerHTML=
      '<button type="button" class="mermaid-zoom-btn" data-act="in" aria-label="Zoom in"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16" y2="16"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg></button>'+
      '<button type="button" class="mermaid-zoom-btn" data-act="out" aria-label="Zoom out"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16" y2="16"/><line x1="8" y1="11" x2="14" y2="11"/></svg></button>'+
      '<button type="button" class="mermaid-zoom-btn" data-act="reset" aria-label="Reset"><svg viewBox="0 0 24 24"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg></button>'+
      '<button type="button" class="mermaid-zoom-btn" data-act="close" aria-label="Close"><svg viewBox="0 0 24 24"><line x1="5" y1="5" x2="19" y2="19"/><line x1="19" y1="5" x2="5" y2="19"/></svg></button>';
    var hint=document.createElement('div');
    hint.className='mermaid-zoom-hint';
    hint.textContent='Scroll to zoom · drag to pan · Esc to close';
    zoomOverlay.appendChild(stage);
    zoomOverlay.appendChild(controls);
    zoomOverlay.appendChild(hint);
    document.body.appendChild(zoomOverlay);

    var scale=1, tx=0, ty=0, dragging=false, lastX=0, lastY=0;
    function apply(){
      var svg=stage.querySelector('svg');
      if(!svg) return;
      svg.style.transform='translate('+tx+'px,'+ty+'px) scale('+scale+')';
    }
    function reset(){ scale=1; tx=0; ty=0; apply(); }
    function open(srcSvg){
      /* Clone and strip size constraints so the SVG can grow */
      stage.innerHTML='';
      var clone=srcSvg.cloneNode(true);
      clone.removeAttribute('style');
      clone.style.maxWidth='none';
      clone.style.maxHeight='none';
      /* Respect intrinsic size; default to ~90% viewport on the longer axis */
      var vw=window.innerWidth, vh=window.innerHeight;
      var targetW=Math.min(vw*0.92, (clone.getBoundingClientRect().width||vw*0.9));
      clone.style.width=targetW+'px';
      clone.style.height='auto';
      stage.appendChild(clone);
      zoomOverlay.classList.add('active');
      zoomOverlay.setAttribute('aria-hidden','false');
      reset();
    }
    function close(){
      zoomOverlay.classList.remove('active');
      zoomOverlay.setAttribute('aria-hidden','true');
      stage.innerHTML='';
    }

    controls.addEventListener('click',function(e){
      var btn=e.target.closest('.mermaid-zoom-btn');
      if(!btn) return;
      e.stopPropagation();
      var act=btn.getAttribute('data-act');
      if(act==='in'){ scale=Math.min(scale*1.25, 8); apply(); }
      else if(act==='out'){ scale=Math.max(scale/1.25, 0.25); apply(); }
      else if(act==='reset'){ reset(); }
      else if(act==='close'){ close(); }
    });

    zoomOverlay.addEventListener('click',function(e){
      if(e.target===zoomOverlay || e.target===stage) close();
    });
    document.addEventListener('keydown',function(e){
      if(!zoomOverlay.classList.contains('active')) return;
      if(e.key==='Escape') close();
      else if(e.key==='+' || e.key==='=') { scale=Math.min(scale*1.25,8); apply(); }
      else if(e.key==='-') { scale=Math.max(scale/1.25,0.25); apply(); }
      else if(e.key==='0') reset();
    });

    /* Wheel zoom (cursor-anchored) */
    stage.addEventListener('wheel',function(e){
      if(!zoomOverlay.classList.contains('active')) return;
      e.preventDefault();
      var rect=stage.getBoundingClientRect();
      var cx=e.clientX-rect.left-rect.width/2;
      var cy=e.clientY-rect.top-rect.height/2;
      var factor=e.deltaY<0?1.15:1/1.15;
      var newScale=Math.max(0.25, Math.min(8, scale*factor));
      var k=newScale/scale;
      tx=cx-(cx-tx)*k;
      ty=cy-(cy-ty)*k;
      scale=newScale;
      apply();
    },{passive:false});

    /* Drag to pan */
    stage.addEventListener('mousedown',function(e){
      if(e.target.closest('.mermaid-zoom-controls')) return;
      dragging=true; lastX=e.clientX; lastY=e.clientY;
      stage.classList.add('dragging');
    });
    window.addEventListener('mousemove',function(e){
      if(!dragging) return;
      tx+=e.clientX-lastX; ty+=e.clientY-lastY;
      lastX=e.clientX; lastY=e.clientY; apply();
    });
    window.addEventListener('mouseup',function(){ dragging=false; stage.classList.remove('dragging'); });

    /* Touch: one-finger pan, pinch-to-zoom */
    var pinch={d0:0,s0:1};
    stage.addEventListener('touchstart',function(e){
      if(e.touches.length===1){
        dragging=true; lastX=e.touches[0].clientX; lastY=e.touches[0].clientY;
      } else if(e.touches.length===2){
        dragging=false;
        var dx=e.touches[0].clientX-e.touches[1].clientX;
        var dy=e.touches[0].clientY-e.touches[1].clientY;
        pinch.d0=Math.hypot(dx,dy); pinch.s0=scale;
      }
    },{passive:true});
    stage.addEventListener('touchmove',function(e){
      if(e.touches.length===1 && dragging){
        tx+=e.touches[0].clientX-lastX; ty+=e.touches[0].clientY-lastY;
        lastX=e.touches[0].clientX; lastY=e.touches[0].clientY; apply();
        e.preventDefault();
      } else if(e.touches.length===2 && pinch.d0>0){
        var dx=e.touches[0].clientX-e.touches[1].clientX;
        var dy=e.touches[0].clientY-e.touches[1].clientY;
        var d=Math.hypot(dx,dy);
        scale=Math.max(0.25, Math.min(8, pinch.s0*d/pinch.d0));
        apply();
        e.preventDefault();
      }
    },{passive:false});
    stage.addEventListener('touchend',function(){ dragging=false; pinch.d0=0; });

    /* Attach expand button once mermaid has rendered each diagram */
    function decorate(el){
      if(el.dataset.mmExpand==='1') return;
      var svg=el.querySelector('svg');
      if(!svg) return;
      el.dataset.mmExpand='1';
      el.classList.add('mm-ready');
      var btn=document.createElement('button');
      btn.type='button';
      btn.className='mermaid-expand';
      btn.setAttribute('aria-label','Expand diagram');
      btn.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg><span>Expand</span>';
      btn.addEventListener('click',function(e){
        e.stopPropagation();
        e.preventDefault();
        var s=el.querySelector('svg');
        if(s) open(s);
      });
      el.appendChild(btn);
      /* Whole container clickable (so users who don't hover still discover it) */
      el.addEventListener('click',function(e){
        if(e.target.closest('.mermaid-expand')) return;
        var s=el.querySelector('svg');
        if(s) open(s);
      });
    }
    function scanAll(){
      document.querySelectorAll('.mermaid').forEach(decorate);
    }
    /* Mermaid renders async; poll for a short window then observe */
    var tries=0;
    var poll=setInterval(function(){
      scanAll();
      if(++tries>20) clearInterval(poll);
    },300);
    /* Also observe DOM so late renders get the button */
    if(window.MutationObserver){
      var mo=new MutationObserver(function(){ scanAll(); });
      mo.observe(document.body,{childList:true,subtree:true});
    }
  })();

  /* ── Expand collapsed section on direct anchor navigation ── */
  if(window.location.hash){
    var target=document.querySelector(window.location.hash);
    if(target){
      var body=target.closest('.section-body.collapsed');
      if(body){
        var toggle=body.previousElementSibling;
        if(toggle && toggle.classList.contains('section-toggle')) toggle.click();
      }
      setTimeout(function(){ target.scrollIntoView({block:'start'}); },100);
    }
  }

  /* ── Observation overlay: hover tooltip + click side panel ── */
  (function initObsOverlay(){
    /* Skip refs with data-obs-src — those carry a cross-page source
       pointer handled by initCrossObsSource below. */
    var refs=document.querySelectorAll('.obs-ref[data-obs]:not([data-obs-src])');
    if(!refs.length) return;

    /* Build an in-memory index from the on-page obs-cards so the overlay
       can show title + summary without a network round-trip. */
    var index={};
    document.querySelectorAll('.obs-card[id]').forEach(function(card){
      var id=card.getAttribute('id');
      var num=(card.querySelector('.obs-card-num')||{}).textContent||'';
      var title=(card.querySelector('.obs-card-title')||{}).textContent||'';
      var summaryEl=card.querySelector('.obs-card-summary');
      var summary=summaryEl?summaryEl.innerHTML:'';
      var tier=card.getAttribute('data-tier')||'general';
      var tierEl=card.querySelector('.obs-tier');
      var tierLabel=tierEl?tierEl.textContent:tier;
      var section=card.getAttribute('data-section')||'';
      index[id]={num:num,title:title,summary:summary,tier:tier,tierLabel:tierLabel,section:section};
    });

    /* --- Tooltip (hover preview) --- */
    var tip=document.createElement('div');
    tip.className='obs-tooltip';
    tip.setAttribute('role','tooltip');
    document.body.appendChild(tip);
    var tipTimer=null, tipActive=false;

    function showTip(ref,x,y){
      var id=ref.getAttribute('data-obs');
      var data=index[id];
      if(!data) return;
      tip.innerHTML=
        '<div class="obs-tooltip-head">'+
          '<span class="obs-tooltip-num">'+data.num+'</span>'+
          '<span class="obs-tooltip-section">§'+data.section+'</span>'+
          '<span class="obs-tooltip-tier obs-tier obs-tier-'+data.tier+'">'+data.tierLabel+'</span>'+
        '</div>'+
        '<div class="obs-tooltip-title">'+data.title+'</div>'+
        '<div class="obs-tooltip-summary">'+data.summary+'</div>'+
        '<div class="obs-tooltip-hint">Click for full detail</div>';
      /* Position after sizing */
      tip.style.left='0px'; tip.style.top='0px';
      tip.classList.add('visible');
      positionTip(x,y);
      tipActive=true;
    }
    function positionTip(x,y){
      var r=tip.getBoundingClientRect();
      var vw=window.innerWidth, vh=window.innerHeight;
      var left=x+14, top=y+18;
      if(left+r.width>vw-12) left=Math.max(8,x-r.width-14);
      if(top+r.height>vh-12) top=Math.max(8,y-r.height-14);
      tip.style.left=left+'px';
      tip.style.top=top+'px';
    }
    function hideTip(){ tip.classList.remove('visible'); tipActive=false; }

    refs.forEach(function(ref){
      ref.addEventListener('mouseenter',function(e){
        clearTimeout(tipTimer);
        tipTimer=setTimeout(function(){ showTip(ref,e.clientX,e.clientY); },120);
      });
      ref.addEventListener('mousemove',function(e){
        if(tipActive) positionTip(e.clientX,e.clientY);
      });
      ref.addEventListener('mouseleave',function(){
        clearTimeout(tipTimer);
        hideTip();
      });
    });

    /* --- Side panel (click for full detail) --- */
    var overlay=document.createElement('div');
    overlay.className='obs-panel-overlay';
    document.body.appendChild(overlay);

    var panel=document.createElement('aside');
    panel.className='obs-panel';
    panel.setAttribute('role','dialog');
    panel.setAttribute('aria-label','Observation detail');
    panel.innerHTML=
      '<div class="obs-panel-header">'+
        '<span class="obs-panel-num"></span>'+
        '<span class="obs-panel-section-id"></span>'+
        '<span class="obs-panel-tier obs-tier"></span>'+
        '<button type="button" class="obs-panel-close" aria-label="Close">'+
          '<svg viewBox="0 0 24 24"><line x1="5" y1="5" x2="19" y2="19"/><line x1="19" y1="5" x2="5" y2="19"/></svg>'+
        '</button>'+
      '</div>'+
      '<div class="obs-panel-body">'+
        '<div class="obs-panel-title"></div>'+
        '<div class="obs-panel-summary"></div>'+
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

    function openPanel(id){
      var data=index[id];
      if(!data) return;
      panel.querySelector('.obs-panel-num').textContent=data.num;
      panel.querySelector('.obs-panel-section-id').textContent='§'+data.section+' · Mainnet Observation';
      var tierEl=panel.querySelector('.obs-panel-tier');
      tierEl.className='obs-panel-tier obs-tier obs-tier-'+data.tier;
      tierEl.textContent=data.tierLabel;
      panel.querySelector('.obs-panel-title').textContent=data.title;
      panel.querySelector('.obs-panel-summary').innerHTML=data.summary;
      panel.querySelector('.obs-panel-source').innerHTML=
        '<a href="#'+data.section.replace(/\./g,'')+'-mainnet-observations">§'+data.section+' Mainnet Observations</a>';
      var cta=panel.querySelector('.obs-panel-cta');
      cta.setAttribute('href','#'+id);
      cta.onclick=function(e){
        e.preventDefault();
        closePanel();
        var card=document.getElementById(id);
        if(!card) return;
        /* Expand any collapsed ancestor section */
        var collapsed=card.closest('.section-body.collapsed');
        if(collapsed){
          var toggle=collapsed.previousElementSibling;
          if(toggle&&toggle.classList.contains('section-toggle')) toggle.click();
        }
        setTimeout(function(){
          card.scrollIntoView({behavior:'smooth',block:'center'});
          card.classList.add('obs-card-highlight');
          setTimeout(function(){ card.classList.remove('obs-card-highlight'); },1600);
        },60);
      };
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
        var id=ref.getAttribute('data-obs');
        if(index[id]) openPanel(id);
      });
    });
  })();

  /* ── F# finding-ref overlay: hover tooltip + click side panel ──
     Mirrors initObsOverlay but for `.finding-ref[data-finding]` links
     produced on sub-report pages. Hydration reads the hidden
     `.findings-registry` > `.finding-detail` cards. */
  (function initFindingRefOverlay(){
    var refs=document.querySelectorAll('.finding-ref[data-finding]');
    if(!refs.length) return;
    var index={};
    document.querySelectorAll('.finding-detail[id]').forEach(function(card){
      var id=(card.getAttribute('data-finding')||'');
      if(!id) return;
      var summary=(card.querySelector('.finding-detail-summary')||{}).innerHTML||'';
      var insight=(card.querySelector('.finding-detail-insight')||{}).textContent||'';
      var src=(card.querySelector('.finding-detail-src')||{}).textContent||'';
      var group=card.getAttribute('data-group')||'';
      var href=card.getAttribute('data-href')||'';
      index[id]={id:id,summary:summary,insight:insight,src:src,group:group,href:href,domId:card.id};
    });

    var tip=document.createElement('div');
    tip.className='finding-tooltip';
    tip.setAttribute('role','tooltip');
    document.body.appendChild(tip);
    var tipTimer=null,tipActive=false;

    function showTip(ref,x,y){
      var id=ref.getAttribute('data-finding');
      var data=index[id];
      if(!data) return;
      tip.innerHTML=
        '<div class="finding-tooltip-head">'+
          '<span class="finding-tooltip-id finding-group-'+data.group+'">'+data.id+'</span>'+
          (data.src?'<span class="finding-tooltip-src">'+data.src+'</span>':'')+
        '</div>'+
        '<div class="finding-tooltip-summary">'+data.summary+'</div>'+
        (data.insight?'<div class="finding-tooltip-insight">'+data.insight+'</div>':'')+
        '<div class="finding-tooltip-hint">Click for full detail</div>';
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

    var overlay=document.createElement('div');
    overlay.className='finding-panel-overlay';
    document.body.appendChild(overlay);

    var panel=document.createElement('aside');
    panel.className='finding-panel';
    panel.setAttribute('role','dialog');
    panel.setAttribute('aria-label','Finding detail');
    panel.innerHTML=
      '<div class="finding-panel-header">'+
        '<span class="finding-panel-id"></span>'+
        '<span class="finding-panel-src"></span>'+
        '<button type="button" class="finding-panel-close" aria-label="Close">'+
          '<svg viewBox="0 0 24 24"><line x1="5" y1="5" x2="19" y2="19"/><line x1="19" y1="5" x2="5" y2="19"/></svg>'+
        '</button>'+
      '</div>'+
      '<div class="finding-panel-body">'+
        '<div class="finding-panel-summary"></div>'+
        '<div class="finding-panel-insight-wrap">'+
          '<div class="finding-panel-insight-label">Insight</div>'+
          '<div class="finding-panel-insight"></div>'+
        '</div>'+
        '<a class="finding-panel-cta" href="#">'+
          '<svg viewBox="0 0 24 24"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>'+
          '<span>Jump to source</span>'+
        '</a>'+
      '</div>';
    document.body.appendChild(panel);

    function openPanel(id){
      var data=index[id];
      if(!data) return;
      var idEl=panel.querySelector('.finding-panel-id');
      idEl.textContent=data.id;
      idEl.className='finding-panel-id finding-group-'+data.group;
      panel.querySelector('.finding-panel-src').textContent=data.src||'';
      panel.querySelector('.finding-panel-summary').innerHTML=data.summary;
      var insightEl=panel.querySelector('.finding-panel-insight');
      var insightWrap=panel.querySelector('.finding-panel-insight-wrap');
      if(data.insight){
        insightEl.textContent=data.insight;
        insightWrap.style.display='';
      } else {
        insightWrap.style.display='none';
      }
      var cta=panel.querySelector('.finding-panel-cta');
      if(data.href){
        cta.style.display='';
        cta.setAttribute('href',data.href);
        cta.onclick=function(e){
          e.preventDefault();
          closePanel();
          var target=document.querySelector(data.href);
          if(!target) return;
          var collapsed=target.closest && target.closest('.section-body.collapsed');
          if(collapsed){
            var toggle=collapsed.previousElementSibling;
            if(toggle&&toggle.classList.contains('section-toggle')) toggle.click();
          }
          setTimeout(function(){
            target.scrollIntoView({behavior:'smooth',block:'start'});
          },60);
        };
      } else {
        cta.style.display='none';
      }
      document.body.classList.add('finding-panel-open');
      panel.setAttribute('aria-hidden','false');
    }
    function closePanel(){
      document.body.classList.remove('finding-panel-open');
      panel.setAttribute('aria-hidden','true');
    }
    overlay.addEventListener('click',closePanel);
    panel.querySelector('.finding-panel-close').addEventListener('click',closePanel);
    document.addEventListener('keydown',function(e){
      if(e.key==='Escape'&&document.body.classList.contains('finding-panel-open')) closePanel();
    });

    refs.forEach(function(ref){
      ref.addEventListener('click',function(e){
        e.preventDefault();
        hideTip();
        var id=ref.getAttribute('data-finding');
        if(index[id]) openPanel(id);
      });
    });
  })();

  /* Findings page filter / search. Only wires up if the page markup
     is present — otherwise it's a no-op. */
  (function initFindingsPage(){
    var page=document.querySelector('.findings-page');
    if(!page) return;
    var chips=page.querySelectorAll('.findings-chip');
    var search=page.querySelector('.findings-search');
    var cards=page.querySelectorAll('.finding-card');
    var sections=page.querySelectorAll('.findings-section');
    var state={tier:'*',query:''};

    function norm(s){ return (s||'').toLowerCase(); }
    function cardMatches(card){
      var t=state.tier;
      var q=state.query;
      if(t!=='*'){
        var chipMatch=card.querySelector('.finding-obs-chip[data-tier="'+t+'"], .obs-card[data-tier="'+t+'"]');
        if(!chipMatch) return false;
      }
      if(q){
        var text=norm(card.textContent);
        if(text.indexOf(q)<0) return false;
      }
      return true;
    }
    function apply(){
      cards.forEach(function(card){
        if(cardMatches(card)) card.classList.remove('hidden');
        else card.classList.add('hidden');
      });
      sections.forEach(function(sec){
        var visible=sec.querySelectorAll('.finding-card:not(.hidden)').length;
        sec.style.display = visible ? '' : 'none';
      });
    }

    chips.forEach(function(chip){
      chip.addEventListener('click',function(){
        chips.forEach(function(c){ c.classList.remove('active'); });
        chip.classList.add('active');
        state.tier=chip.getAttribute('data-tier');
        apply();
      });
    });
    if(search){
      var deb;
      search.addEventListener('input',function(){
        clearTimeout(deb);
        deb=setTimeout(function(){
          state.query=norm(search.value.trim());
          apply();
        },120);
      });
    }
  })();
  /* ── Cross-page DIA source overlay ──
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
        'treasury.html':'Treasury & Pool Pots Distribution',
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
        ids.forEach(function(fid){
          var f=findingsIndex[fid];
          var li=document.createElement('li');
          li.className='obs-panel-finding';
          var idEl='<span class="obs-panel-finding-id">'+fid+'</span>';
          if(f){
            var body='<div class="obs-panel-finding-body">'+
              '<div class="obs-panel-finding-summary">'+f.summary+'</div>'+
              (f.insight ? '<div class="obs-panel-finding-insight">'+f.insight+'</div>' : '')+
            '</div>';
            var head='<div class="obs-panel-finding-head">'+idEl;
            if(f.href){
              head+='<a class="obs-panel-finding-jump" href="'+f.href+'" '+
                'aria-label="Jump to '+fid+'">'+
                '<svg viewBox="0 0 24 24" width="12" height="12">'+
                '<line x1="5" y1="12" x2="19" y2="12"/>'+
                '<polyline points="12 5 19 12 12 19"/></svg></a>';
            }
            head+='</div>';
            li.innerHTML=head+body;
          } else {
            li.innerHTML='<div class="obs-panel-finding-head">'+idEl+'</div>'+
              '<div class="obs-panel-finding-body">'+
              '<div class="obs-panel-finding-summary obs-panel-finding-missing">'+
              'Detail not bundled on this page.</div></div>';
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

  /* ── Reader feedback: analytics custom events + finding reactions ──
     Provider-agnostic: calls into `window.spoTrack(name, propsFlat)`,
     a global injected by the analytics head bridge that maps to either
     Plausible or Umami transparently. The script is a no-op when no
     analytics provider is configured (the body has no `data-analytics`
     attribute). Per-session idempotency via sessionStorage so hammering
     a button only counts once per (page, finding, sentiment) in a given
     session — keeps the dashboard signal clean. */
  (function initReaderFeedback(){
    function track(name,props){
      if(typeof window.spoTrack==='function'){
        try{window.spoTrack(name,props||{});}catch(e){}
      }
    }
    var body=document.body;
    if(!body) return;
    var hasReactions=body.getAttribute('data-reactions')==='1';
    var pageId=location.pathname.split('/').pop()||'index.html';

    /* Overlay engagement events — listener is cheap; the track() helper
       guards the call when no provider is configured. */
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

    /* Reaction buttons — injected once per .sro-finding, only when the
       page declares data-reactions="1". The dashboard records sentiment
       as a custom prop so the editor can sort findings by 👍/👎 weight. */
    if(!hasReactions) return;
    var findings=document.querySelectorAll('.sro-finding[data-finding]');
    if(!findings.length) return;
    var SK='spo:react:';

    function isSent(canon,sent){
      try{return sessionStorage.getItem(SK+canon+':'+sent)==='1';}
      catch(e){return false;}
    }
    function markSent(canon,sent){
      try{sessionStorage.setItem(SK+canon+':'+sent,'1');}catch(e){}
    }

    function makeBtn(canon,sent,label,svg){
      var b=document.createElement('button');
      b.type='button';
      b.className='feedback-react-btn feedback-react-'+sent;
      b.setAttribute('data-finding',canon);
      b.setAttribute('data-sentiment',sent);
      b.setAttribute('aria-label',label+' — '+canon);
      b.setAttribute('title',label);
      b.innerHTML=svg+'<span class="feedback-react-label">'+label+'</span>';
      if(isSent(canon,sent)) b.classList.add('is-active');
      b.addEventListener('click',function(ev){
        ev.preventDefault();ev.stopPropagation();
        if(isSent(canon,sent)){
          /* Already counted this session — visual confirm only. */
          b.classList.add('is-active');
          return;
        }
        track('Finding Reaction',{finding:canon,sentiment:sent,page:pageId});
        markSent(canon,sent);
        b.classList.add('is-active');
        b.classList.add('feedback-react-pulse');
        setTimeout(function(){b.classList.remove('feedback-react-pulse');},420);
      });
      return b;
    }

    var SVG_UP='<svg viewBox="0 0 16 16" aria-hidden="true">'
      +'<path d="M3 8.5h2.2L7 3.5c.7-.2 1.4.4 1.3 1.1L8 7.5h3.6c.8 0 1.4.7 1.2 1.5L12 12c-.2.7-.8 1.2-1.5 1.2H6L3 13"/>'
      +'</svg>';
    var SVG_DOWN='<svg viewBox="0 0 16 16" aria-hidden="true">'
      +'<path d="M3 7.5h2.2L7 12.5c.7.2 1.4-.4 1.3-1.1L8 8.5h3.6c.8 0 1.4-.7 1.2-1.5L12 4c-.2-.7-.8-1.2-1.5-1.2H6L3 3"/>'
      +'</svg>';

    findings.forEach(function(li){
      if(li.querySelector('.feedback-react')) return;
      var canon=li.getAttribute('data-finding');
      if(!canon) return;
      var meta=li.querySelector('.sro-meta');
      var host=document.createElement('div');
      host.className='feedback-react';
      host.setAttribute('role','group');
      host.setAttribute('aria-label','Reactions for '+canon);
      host.appendChild(makeBtn(canon,'up','Useful',SVG_UP));
      host.appendChild(makeBtn(canon,'down','Not useful',SVG_DOWN));
      if(meta){meta.appendChild(host);}else{li.appendChild(host);}
    });
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
      var react=li.querySelector('.feedback-react');
      var btn=makeBtn(canon,title.substring(0,140),title);
      if(react){react.appendChild(btn);}
      else if(meta){meta.appendChild(btn);}
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
  /* ── /Cross-page DIA source overlay ── */

})();
