(function(){
var chips=document.querySelectorAll('.filter-chips button'),count=document.getElementById('tl-count'),
list=document.getElementById('tl-list');
if(!list)return;
function apply(f){var n=0;
 list.querySelectorAll('li[data-f]').forEach(function(li){var ok=!f||li.getAttribute('data-f')===f;li.style.display=ok?'':'none';if(ok)n++;});
 list.querySelectorAll('.tl-year').forEach(function(h){var ul=h.nextElementSibling;
  var any=ul&&Array.prototype.some.call(ul.children,function(li){return li.style.display!=='none';});
  h.style.display=any?'':'none';if(ul)ul.style.display=any?'':'none';});
 if(count)count.textContent=n+' item'+(n!==1?'s':'');}
chips.forEach(function(b){b.addEventListener('click',function(){
 chips.forEach(function(x){x.setAttribute('aria-pressed','false');});
 b.setAttribute('aria-pressed','true');apply(b.getAttribute('data-f'));});});
apply('');
})();