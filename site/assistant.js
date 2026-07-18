(function(){
var out=document.getElementById('asst-out'),form=document.getElementById('asst-form'),
q=document.getElementById('asst-q'),langSel=document.getElementById('asst-lang'),
bench=document.getElementById('asst-bench'),graphBox=document.getElementById('asst-graph'),
graphList=document.getElementById('asst-graph-list');
if(!form)return;
var IDX=null,curIntent=null;
var STOP={'the':1,'a':1,'an':1,'of':1,'in':1,'on':1,'and':1,'or':1,'to':1,'is':1,'are':1,'what':1,'who':1,
'how':1,'for':1,'with':1,'about':1,'do':1,'does':1,'your':1,'you':1,'i':1,'am':1,'me':1,'my':1,'que':1,'la':1,
'le':1,'les':1,'des':1,'el':1,'los':1,'der':1,'die':1,'das':1};
var INTENTS={
 phd:{q:'PhD supervision multilingual trustworthy human-centred research topics',
   note:'Prospective PhD students: supervision record, themes and how to apply.',
   links:[['supervision.html','Supervision & mentoring'],['research.html','Research themes'],['contact.html','Contact']]},
 industry:{q:'projects funding translation evaluation health industry collaboration patent',
   note:'Industry partners: applied projects, the patent, and collaboration routes.',
   links:[['projects.html','Projects & funding'],['innovation.html','Innovation & industry'],['contact.html','Contact']]},
 journalist:{q:'Rinn Artificial Intelligence leadership keynotes news impact',
   note:'Journalists: verified roles, a factual media overview and news.',
   links:[['showcase.html','Research showcase'],['news.html','News'],['rinn-ai.html','Rinn AI'],['contact.html','Contact']]},
 msc:{q:'teaching modules MSc masters supervision artificial intelligence',
   note:'Prospective MSc students: teaching, modules and MSc supervision.',
   links:[['teaching.html','Teaching'],['supervision.html','Supervision'],['contact.html','Contact']]},
 collab:{q:'publications research themes multilingual evaluation trustworthy collaboration',
   note:'Academic collaborators: research agenda, publications and themes.',
   links:[['research.html','Research'],['publications.html','Publications'],['collections.html','Collections'],['contact.html','Contact']]}};
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function tokens(s){return String(s||'').toLowerCase().replace(/[^\p{L}\p{N}\s]/gu,' ').split(/\s+/).filter(function(t){return t&&!STOP[t];});}
function detectLang(s){ // very small heuristic; only to pick a glossary, never to translate
 if(/[؀-ۿ]/.test(s))return /[پچگیک]/.test(s)?'fa':'ar';
 if(/[֐-׿]/.test(s))return 'he';
 if(/[Ѐ-ӿ]/.test(s))return 'ru';
 return 'en';}
function expand(toks,lang){ // map query terms via glossary to canonical theme keys (cross-language)
 var g=IDX.glossary||{},hits=[],extra=[];
 var maps=[g[lang]||{},g.en||{}];
 var raw=toks.join(' ');
 maps.forEach(function(m){for(var k in m){if(raw.indexOf(k)>=0){extra.push(m[k]);var nm=(IDX.theme_names||{})[m[k]];if(nm)extra=extra.concat(tokens(nm));}}});
 return {toks:toks.concat(extra),themeHits:extra};}
function score(docToks,queryToks){var set={},n=0;docToks.forEach(function(t){set[t]=(set[t]||0)+1;});
 var matched=[];queryToks.forEach(function(t){if(set[t]){n+=1;if(matched.indexOf(t)<0)matched.push(t);}
  else{for(var d in set){if(d.length>3&&(d.indexOf(t)===0||t.indexOf(d)===0)){n+=0.5;if(matched.indexOf(t)<0)matched.push(t);break;}}}});
 return {n:n,matched:matched};}
function typeLabel(t){return{publication:'Publication',project:'Project',talk:'Talk',supervision:'Supervision',page:'Section'}[t]||t;}
function render(query,lang){
 out.innerHTML='';graphBox.hidden=true;graphList.innerHTML='';
 if(!IDX){out.innerHTML='<p class="note">The knowledge index is still loading. Please try again in a moment.</p>';return;}
 var base=tokens(query),ex=expand(base,lang),qt=ex.toks;
 if(!qt.length){out.innerHTML='<p class="note">Please enter a question or pick one of the buttons above.</p>';return;}
 var ranked=IDX.docs.map(function(d){var s=score(tokens(d.text),qt);return{d:d,s:s.n,matched:s.matched};})
   .filter(function(r){return r.s>0;}).sort(function(a,b){return b.s-a.s;});
 var max=ranked.length?ranked[0].s:0;
 var showBench=bench&&bench.checked;
 if(!ranked.length||max<1){
  out.innerHTML='<div class="asst-answer none"><p><strong>I don’t have a confident answer to that from the verified records on this site.</strong> '
   +'I only answer from indexed publications, projects, talks, supervision and pages, and I won’t guess.</p>'
   +'<p class="asst-why">You may find it here: <a href="publications.html">publications</a>, '
   +'<a href="research.html">research themes</a>, <a href="projects.html">projects</a>, or please '
   +'<a href="contact.html">contact Dr Afli</a> directly.</p></div>';
  return;}
 var top=ranked.slice(0,6);
 var head='<p class="asst-meta">Retrieved '+top.length+' record'+(top.length>1?'s':'')+' from the verified index'
   +(ex.themeHits.length?' · matched theme'+(ex.themeHits.length>1?'s':'')+': '+esc(ex.themeHits.filter(function(v,i,a){return a.indexOf(v)===i;}).map(function(k){return (IDX.theme_names||{})[k]||k;}).join(', ')):'')
   +' · index built '+esc(IDX.generated)+'</p>';
 var html=top.map(function(r){var d=r.d,conf=Math.round(r.s/max*100);
  var confWord=conf>=75?'high':conf>=45?'moderate':'low';
  var terms=r.matched.slice(0,6).map(function(t){return '<span class="mt">'+esc(t)+'</span>';}).join('');
  var yr=d.year?(' · '+d.year):'';
  return '<div class="asst-answer"><div><a href="'+esc(d.url)+'"><strong>'+esc(d.title)+'</strong></a> '
   +'<span class="asst-conf">— '+esc(typeLabel(d.type))+yr+'</span></div>'
   +'<div class="asst-why">Why this: matched '+terms+' · confidence '+confWord
   +(showBench?' <span class="asst-score">(score '+r.s.toFixed(1)+' / '+conf+'%)</span>':'')+'</div></div>';
 }).join('');
 out.innerHTML=head+html
  +'<details class="asst-detail"><summary>Why these answers?</summary>'
  +'<p class="asst-why">Each record was ranked by how many of your query terms (after cross-language '
  +'glossary expansion) appear in its indexed text. Records are real entries from this site; each links to its '
  +'authoritative source. Confidence is relative to the best match for this query. Nothing was generated or paraphrased.</p></details>';
 // knowledge-graph style related records (same themes as the top hit)
 var themes=(top[0].d.themes)||[];
 if(themes.length){var rel=IDX.docs.filter(function(d){return d!==top[0].d&&(d.themes||[]).some(function(t){return themes.indexOf(t)>=0;});}).slice(0,6);
  if(rel.length){graphList.innerHTML=rel.map(function(d){return '<li><a href="'+esc(d.url)+'">'+esc(d.title)+'</a> <span class="muted">— '+esc(typeLabel(d.type))+'</span></li>';}).join('');graphBox.hidden=false;}}
}
function run(query){var lang=langSel&&langSel.value!=='auto'?langSel.value:detectLang(query);render(query,lang);}
form.addEventListener('submit',function(e){e.preventDefault();run(q.value);});
document.querySelectorAll('.chip').forEach(function(b){b.addEventListener('click',function(){
 var it=INTENTS[b.dataset.intent];if(!it)return;curIntent=b.dataset.intent;
 document.querySelectorAll('.chip').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false');});
 q.value=q.value||'';var lang=langSel&&langSel.value!=='auto'?langSel.value:'en';render(it.q,lang);
 out.insertAdjacentHTML('afterbegin','<p class="note">'+esc(it.note)+' Quick links: '
  +it.links.map(function(l){return '<a href="'+l[0]+'">'+esc(l[1])+'</a>';}).join(' · ')+'</p>');
}); });
fetch('data/assistant-index.json').then(function(r){return r.json();}).then(function(j){IDX=j;})
 .catch(function(){out.innerHTML='<p class="note">The assistant index could not be loaded. You can browse '
  +'<a href="publications.html">publications</a> and <a href="research.html">research</a> directly.</p>';});
})();