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
