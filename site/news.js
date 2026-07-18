(function(){var c=document.getElementById('n-cat'),h=document.getElementById('n-theme');
function f(){var cv=c?c.value:'',hv=h?h.value:'';document.querySelectorAll('.news>li').forEach(function(li){
var ok=(!cv||li.dataset.cat===cv)&&(!hv||(' '+li.dataset.themes+' ').indexOf(' '+hv+' ')>=0);
li.style.display=ok?'':'none';});}
if(c)c.addEventListener('change',f);if(h)h.addEventListener('change',f);})();