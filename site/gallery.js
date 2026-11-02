(function(){
var T=function(s,n){var t=(window.I18N||{})[s]||s;return n==null?t:t.split('{n}').join(n);};
var sel=document.getElementById('g-cat'),count=document.getElementById('g-count'),
grid=document.getElementById('gallery-grid');
if(!grid)return;
var figs=[].slice.call(grid.querySelectorAll('figure'));
function apply(){var v=sel&&sel.value||'',n=0;
 figs.forEach(function(f){var ok=!v||f.getAttribute('data-cat')===v;f.style.display=ok?'':'none';if(ok)n++;});
 if(count)count.textContent=T(n===1?'{n} photograph':'{n} photographs',n);}
if(sel)sel.addEventListener('change',apply);apply();
})();