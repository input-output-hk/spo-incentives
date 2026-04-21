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
  /* Apply bottom-up: h4 first, then h3, then h2 (so inner wrappers exist before outer ones) */
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
})();
