(function(){var t=document.getElementById('f-theme'),y=document.getElementById('f-type');
function f(){var th=t.value,ty=y.value;document.querySelectorAll('.pub').forEach(function(p){
var ok=(!th||(' '+p.dataset.themes+' ').indexOf(' '+th+' ')>=0)&&(!ty||p.dataset.type===ty);
p.style.display=ok?'':'none';});}
if(t)t.addEventListener('change',f);if(y)y.addEventListener('change',f);})();