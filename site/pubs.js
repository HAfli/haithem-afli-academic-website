(function(){
var q=document.getElementById('p-q'),y=document.getElementById('p-year'),
t=document.getElementById('p-type'),count=document.getElementById('p-count');
var PAGE=12,STEP=20;
var secs=[].slice.call(document.querySelectorAll('.pubcat'));
secs.forEach(function(s){s._page=PAGE;var b=s.querySelector('.show-more');
 if(b)b.addEventListener('click',function(){s._page+=STEP;apply();});});
function apply(){
 var qs=(q&&q.value||'').trim().toLowerCase(),yv=y&&y.value||'',tv=t&&t.value||'';
 var filtering=!!(qs||yv||tv),total=0;
 secs.forEach(function(s){
  var lis=[].slice.call(s.querySelectorAll('.pub')),m=0,shown=0;
  lis.forEach(function(li){
   var ok=(!yv||li.dataset.year===yv)&&(!tv||li.dataset.type===tv)&&(!qs||(li.dataset.search||'').indexOf(qs)>=0);
   if(ok){m++;
    if(filtering){li.style.display='';}
    else{shown++;li.style.display=(shown<=s._page)?'':'none';}
   } else {li.style.display='none';}
  });
  total+=m;
  s.style.display=m?'':'none';
  var badge=s.querySelector('.cat-count');if(badge)badge.textContent='('+m+')';
  var b=s.querySelector('.show-more');
  if(b){var more=(!filtering&&m>s._page);b.hidden=!more;
   if(more)b.textContent='Show '+Math.min(STEP,m-s._page)+' more';}
 });
 if(count)count.textContent=total+' result'+(total!==1?'s':'');
}
[q,y,t].forEach(function(el){if(el)el.addEventListener(el.tagName==='SELECT'?'change':'input',apply);});
apply();
})();