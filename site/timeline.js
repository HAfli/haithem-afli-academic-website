(function(){
var T=function(s,n){var t=(window.I18N||{})[s]||s;return n==null?t:t.split('{n}').join(n);};
var chips=document.querySelectorAll('.filter-chips button'),count=document.getElementById('tl-count'),
list=document.getElementById('tl-list');
if(!list)return;
function apply(f){var n=0;
 list.querySelectorAll('li[data-f]').forEach(function(li){var ok=!f||li.getAttribute('data-f')===f;li.style.display=ok?'':'none';if(ok)n++;});
 list.querySelectorAll('.tl-year').forEach(function(h){var ul=h.nextElementSibling;
  var any=ul&&Array.prototype.some.call(ul.children,function(li){return li.style.display!=='none';});
  h.style.display=any?'':'none';if(ul)ul.style.display=any?'':'none';});
 if(count)count.textContent=T(n===1?'{n} item':'{n} items',n);}
chips.forEach(function(b){b.addEventListener('click',function(){
 chips.forEach(function(x){x.setAttribute('aria-pressed','false');});
 b.setAttribute('aria-pressed','true');apply(b.getAttribute('data-f'));});});
apply('');
})();