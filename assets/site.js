(() => {
  'use strict';
  let currentSite = null;
  let currentResumes = [];
  let currentCertificates=[];
  let activeFilter = 'All';
  let searchTerm = ''; 
  const $ = (id) => document.getElementById(id);
  const safe = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const safeUrl = (s, fallback = '#') => { try { let u = new URL(String(s)); return ['http:', 'https:'].includes(u.protocol) ? u.href : fallback; } catch { return fallback; } };
  const safeMedia = (value) => {const s=String(value||'').trim();const p=s.replace(/^\//,'');if(p.startsWith('assets/')&&!p.includes('\\')&&!p.includes('\0')&&!/[?#<>"']/g.test(p)&&!p.split('/').includes('..'))return encodeURI(p);return safeUrl(s,'');};
  const icon = (symbol) => ({ terminal:'⌘', layout:'▦', spark:'✳', layers:'◈', cloud:'☁', brain:'✺' }[symbol] || '↗');
  const text = (id, value) => {const el = $(id); if(el) el.textContent = value || '';};
  const lines = (id, value) => {const el = $(id); if(el) el.innerHTML = safe(value || '').replace(/\n/g, '<br>');};
  const mailHref = (s) => 'mailto:' + String(s || '').replace(/[^a-zA-Z0-9@._+\-]/g, '');
  let toastTimer;
  function toast(message) { const e=$('toast'); e.textContent=message; e.classList.add('show'); clearTimeout(toastTimer); toastTimer=setTimeout(()=>e.classList.remove('show'),3200); }
  function visual(variant) {
    switch(variant){
      case 'code':return '<div class="mock-terminal"><div>● &nbsp; CODE AUDIT / RUNNING</div><div class="mcode"><i></i><i></i><i></i><i></i><i></i><i></i></div></div>';
      case 'vision':return '<div class="mock-vision"><div class="vision-face"></div><div class="vision-bracket"></div><span class="vision-approved">✓ REVIEW READY</span></div>';
      case 'agri':return '<div class="mock-agri"><div class="agri-line"></div><div class="agri-line"></div><div class="agri-sun"></div><span class="agri-tag">FIELD INTELLIGENCE</span><span class="agri-crop">✿</span></div>';
      case 'erp':return '<div class="mock-erp"><div class="erp-sidebar"><i></i><i></i><i></i><i></i></div><div class="erp-body"><i></i><i></i><i></i><i></i><i></i></div></div>';
      case 'data':return '<div class="mock-chart"><i></i><i></i><i></i><i></i><i></i></div>';
      case 'python':return '<div class="mock-python"><span>Py.</span></div>';
      default:return '<div class="mock-python"><span>DEV.</span></div>';
    }
  }
  function projectCard(p, index) {
    const variant=['code','vision','agri','erp','data','python'].includes(p.visual)?p.visual:'fallback';
    const repo=safeUrl(p.github), demo=safeUrl(p.demo, '');
    const projectTags=(Array.isArray(p.tags)?p.tags:[]).slice(0,6).map(x=>`<span class="tag">${safe(x)}</span>`).join('');
    const image=safeMedia(p.image);
    const caseNotes=[['THE PROBLEM',p.problem],['THE APPROACH',p.approach],['THE RESULT',p.outcome]].filter(x=>x[1]);
    const evidence=caseNotes.length?`<details class="project-details"><summary>Engineering notes & decisions</summary><div class="project-case-study">${caseNotes.map(([label,value])=>`<div><b>${label}</b> ${safe(value)}</div>`).join('')}</div></details>`:'';
    return `<article class="project-card reveal" aria-label="${safe(p.name)}">
      <div class="project-media media-${variant} ${image?'has-image':''}"><div class="media-caption">${safe(p.kicker || p.category)}</div>${image?`<img src="${safe(image)}" alt="Preview of ${safe(p.name)}" loading="lazy">`:visual(variant)}</div>
      <div class="project-detail"><div class="project-kicker"><span>PROJECT / ${String(index+1).padStart(2,'0')}</span><span>${safe(p.featured?'FEATURED':'EXPLORE')}</span></div>
      <h3>${safe(p.name)}</h3><p>${safe(p.description)}</p><div class="tag-list">${projectTags}</div>${evidence}
      <div class="project-links">${repo!=='#'?`<a href="${safe(repo)}" target="_blank" rel="noopener noreferrer">Source code <span aria-hidden="true">↗</span></a>`:''}${demo?`<a href="${safe(demo)}" target="_blank" rel="noopener noreferrer">Live demo <span aria-hidden="true">↗</span></a>`:''}</div></div></article>`;
  }
  function projectRender() {
    const raw=(Array.isArray(currentSite?.projects)?currentSite.projects:[]).filter(p=>p&&p.published!==false);
    const categories=['All',...new Set(raw.map(p=>p.category).filter(Boolean))];
    if(!categories.includes(activeFilter))activeFilter='All';
    const filters=$('project-filters');
    filters.innerHTML=categories.map(f=>`<button class="filter-chip ${f===activeFilter?'active':''}" type="button" data-filter="${safe(f)}" aria-pressed="${f===activeFilter}">${f==='All'?'All work':safe(f)}${f==='All'?` <span>${String(raw.length).padStart(2,'0')}</span>`:''}</button>`).join('');
    filters.querySelectorAll('button').forEach(button=>button.addEventListener('click',()=>{activeFilter=button.dataset.filter;projectRender();}));
    const shown=raw.filter(p=>(activeFilter==='All'||p.category===activeFilter) && (!searchTerm||[p.name,p.category,p.description,p.problem,p.approach,...(Array.isArray(p.tags)?p.tags:[])].join(' ').toLowerCase().includes(searchTerm)));
    text('project-showing',`${shown.length} project${shown.length===1?'':'s'} shown`);
    $('projects-grid').innerHTML=shown.length?shown.map(projectCard).join(''):'<p>No projects in this category yet.</p>';
    observeReveal();
  }
  function skillsRender(){
    $('skills-grid').innerHTML=(Array.isArray(currentSite.skills)?currentSite.skills:[]).filter(Boolean).map(s=>`<article class="skill-card reveal"><div class="skill-icon" aria-hidden="true">${safe(icon(s.icon))}</div><h3>${safe(s.title)}</h3><div class="skill-pills">${(Array.isArray(s.items)?s.items:[]).map(i=>`<span class="skill-pill">${safe(i)}</span>`).join('')}</div></article>`).join('');
  }
  function milestonesRender(){
    $('journey-list').innerHTML=(Array.isArray(currentSite.milestones)?currentSite.milestones:[]).filter(Boolean).map(m=>`<div class="journey-item reveal"><div class="journey-year">${safe(m.year)}</div><h3>${safe(m.label)}</h3><p>${safe(m.description)}</p></div>`).join('');
  }
  function certificatesRender(){
    const area=$('certificate-grid');
    if(!area)return;
    if(!Array.isArray(currentCertificates)||!currentCertificates.length){area.innerHTML='<div class="cert-empty">Certification records will appear after they are added and published in the private Admin Studio. Certificates appear when I publish their details and evidence.</div>';return;}
    area.innerHTML=currentCertificates.map((c,i)=>{
      const pic=safeMedia(c.image);
      const link=safeMedia(c.file)||safeUrl(c.url,'')||pic;
      return `<article class="cert-card reveal"><div class="cert-card-top"><span>LEARNING RECORD / ${String(i+1).padStart(2,'0')}</span><span>✳</span></div>${pic?`<img class="cert-figure" src="${safe(pic)}" loading="lazy" alt="Certificate issued by ${safe(c.issuer)}">`:''}<h3>${safe(c.title)}</h3><p>${safe(c.issuer)}${c.issued?' · '+safe(c.issued):''}</p>${c.description?`<p>${safe(c.description)}</p>`:''}${link?`<a href="${safe(link)}" target="_blank" rel="noopener noreferrer">View credential ↗</a>`:''}</article>`;
    }).join('');
    observeReveal();
  }
  function resumesRender(){
    const area=$('resume-list');
    if(!Array.isArray(currentResumes)||!currentResumes.length){area.innerHTML='<div class="resume-empty"><div class="resume-symbol">↧</div><h3>Resume coming soon</h3><p>Contact me for the latest version.</p></div>';return;}
    area.innerHTML=currentResumes.map(r=>`<div class="resume-item"><span class="res-icon">▤</span><div class="resume-item-info"><h3>${safe(r.label)}</h3><p>${safe(r.role||'Resume')} · ${safe(r.mime||'PDF')} · DOWNLOAD</p></div><a class="resume-download" href="${safe(safeMedia(r.file))}" download aria-label="Download ${safe(r.label)}" title="Download resume">↓</a></div>`).join('');
  }
  function updatePortrait(){
    const stored=safeMedia(currentSite?.profile?.avatar);
    const legacy=/^(?:.*\/)?(?:profile-portrait\.webp|harshad-passport-crop-1\.jpg|harshad-marathi-hero\.webp)$/i;
    const source=stored && !legacy.test(stored) ? stored : 'assets/uploads/images/harshad-portrait-v42.webp';
    for(const id of ['portrait-image','hero-avatar']){
      const image=$(id);if(!image)continue;
      image.onerror=()=>{image.style.visibility='hidden';};
      image.onload=()=>{image.style.visibility='visible';};
      image.src=source;
    }
  }
  function applyData(site,resumes,certificates=[]){
    currentSite=site;
    currentResumes=resumes||[];
    currentCertificates=certificates||[];
    const p=site?.profile||{};
    text('hero-fullname',p.name);text('hero-marathi',p.marathiName||'हर्षद माधव धुप्पे');
    text('hero-eyebrow',p.eyebrow);lines('hero-title',p.headline);text('hero-description',p.heroDescription);
    text('availability',p.availability);
    $('hero-email').href=mailHref(p.email);text('hero-email',p.email+' ↗');
    const rawPhone=(p.phone||'').replace(/[^+0-9]/g,'');const tel=rawPhone?'tel:'+rawPhone:'#contact';
    $('hero-phone').href=tel;text('hero-phone',(p.phone||'Contact me')+' ↗');
    $('contact-phone').href=tel;$('footer-phone').href=tel;text('hero-role',p.role);text('hero-location',String(p.location||'MAHARASHTRA, INDIA').toUpperCase());
    text('about-subtitle',p.aboutHeading);text('about-body',p.about);text('about-focus',p.focus);
    text('about-degree',`${p.degree} · ${p.graduation}`);$('college-logo').src=safeMedia(p.collegeLogo)||'assets/college-logo.png';text('college-signature-name',p.college);text('about-college',p.college);text('about-location',p.location);text('about-cgpa',p.cgpa);$('about-cgpa-row').hidden=!p.cgpa;
    lines('contact-heading',p.contactHeading);text('contact-description',p.contactDescription);
    text('footer-line',p.footerLine);text('copyright-name',p.name);text('copyright-year',String(new Date().getFullYear()));
    $('contact-email').href=mailHref(p.email);$('footer-email').href=mailHref(p.email);
    $('footer-github').href=safeUrl(p.github);$('github-all').href=safeUrl(p.github);
    $('footer-linkedin').href=safeUrl(p.linkedin);
    document.title=site?.seo?.title||`${p.name||'Harshad Madhav Dhuppe'} — Software Developer`;
    const desc=document.querySelector('meta[name="description"]');if(desc)desc.setAttribute('content',site?.seo?.description||p.heroDescription||'');
    const ogTitle=document.querySelector('meta[property="og:title"]'); if(ogTitle)ogTitle.content=document.title;
    const ogDesc=document.querySelector('meta[property="og:description"]'); if(ogDesc)ogDesc.content=site?.seo?.description||p.heroDescription||'';
    updatePortrait();projectRender();skillsRender();milestonesRender();resumesRender();certificatesRender();observeReveal();
  }
  async function load(){
    // A Pages deployment built directly from the branch may not have generated
    // site-data.json. V4.1 commits a content snapshot for that situation.
    // Normal GitHub Actions deployments overwrite it with fresh CMS content.
    const paths=['./site-data.json?v=42','./site-data.json'];
    let payload=null;let lastError=null;
    for(const path of paths){
      try {
        const response=await fetch(path, {cache:'no-store'});
        if(!response.ok)throw new Error(`HTTP ${response.status} for ${path}`);
        const candidate=await response.json();
        if(!candidate||!candidate.site||!candidate.site.profile||!Array.isArray(candidate.site.projects))throw Error('Invalid portfolio data structure');
        payload=candidate;
        break;
      }catch(error){lastError=error;console.warn('Portfolio data source unavailable:',path,error);}
    }
    if(!payload){
      console.error('Could not load portfolio content:',lastError);
      const section=$('projects-grid');
      if(section)section.innerHTML='<div class="v42-content-note">Project details could not be loaded from the deployment. <a href="https://github.com/Harshad8623" target="_blank" rel="noopener noreferrer">View my GitHub projects ↗</a> or use the contact links below.</div>';
      return;
    }
    try { applyData(payload.site,Array.isArray(payload.resumes)?payload.resumes:[],Array.isArray(payload.certificates)?payload.certificates:[]); }
    catch(error){
      console.error('Portfolio rendering error:',error);
      const section=$('projects-grid');if(section&&!section.children.length)section.innerHTML='<div class="v42-content-note">Some details are temporarily unavailable. Browse the <a href="https://github.com/Harshad8623" target="_blank" rel="noopener noreferrer">GitHub repositories ↗</a>.</div>';
    }
  }
  let revealObserver=null;
  function observeReveal(){
    if(window.matchMedia('(prefers-reduced-motion:reduce)').matches){document.querySelectorAll('.reveal').forEach(e=>e.classList.add('is-visible'));return;}
    if(!revealObserver){revealObserver=new IntersectionObserver((entries)=>entries.forEach(x=>{if(x.isIntersecting){x.target.classList.add('is-visible');revealObserver.unobserve(x.target);}}),{threshold:.08});}
    document.querySelectorAll('.reveal:not(.is-visible)').forEach(e=>revealObserver.observe(e));
  }
  function stripLinkTracking(){
    // ChatGPT and other sharing apps may append utm_source; remove it from the visible address.
    // Preserve normal query parameters and the current anchor (#top, #work, etc.).
    try {
      const url = new URL(window.location.href);
      let changed = false;
      for (const key of [...url.searchParams.keys()]) {
        if (key.toLowerCase().startsWith('utm_')) { url.searchParams.delete(key); changed = true; }
      }
      if (changed) history.replaceState(history.state, '', url.pathname + url.search + url.hash);
    } catch (_) { /* Some previews do not permit History API writes. */ }
  }
  function setup(){
    stripLinkTracking();
    $('menu-toggle').addEventListener('click',()=>{const n=$('mobile-nav');n.hidden=!n.hidden;$('menu-toggle').setAttribute('aria-expanded',String(!n.hidden));});
    $('mobile-nav').querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{$('mobile-nav').hidden=true;$('menu-toggle').setAttribute('aria-expanded','false');}));
    $('copy-email').addEventListener('click',async()=>{
      const email=currentSite?.profile?.email||'dhuppeh@gmail.com';
      if(!navigator.clipboard || !window.isSecureContext){toast('Email: '+email);return;}
      try{await navigator.clipboard.writeText(email);toast('Email address copied');}catch{toast('Email: '+email);}
    });
    const search=$('project-search');if(search)search.addEventListener('input',()=>{searchTerm=search.value.trim().toLowerCase();projectRender();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('mobile-nav').hidden){$('mobile-nav').hidden=true;$('menu-toggle').setAttribute('aria-expanded','false');$('menu-toggle').focus();}});
    const top=$('back-top');if(top)top.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));
    window.addEventListener('scroll',()=>{const h=document.documentElement;const prog=h.scrollTop/(h.scrollHeight-h.clientHeight||1);$('reading-line').style.width=`${Math.max(0,Math.min(1,prog))*100}%`;const b=$('back-top');if(b)b.classList.toggle('is-visible',h.scrollTop>600);},{passive:true});
    observeReveal();load();
  }
  window.Portfolio={reload:load,applyData,toast,getSite:()=>currentSite,getResumes:()=>currentResumes,safe};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup);else setup();
})();
