(function(){var s=document.getElementById('f-topic');if(!s)return;
s.addEventListener('change',function(){var v=s.value;
document.querySelectorAll('#masters li').forEach(function(li){
var ok=!v||(' '+li.dataset.topics+' ').indexOf(' '+v+' ')>=0;li.style.display=ok?'':'none';});
document.querySelectorAll('#masters h3').forEach(function(h){var n=h.nextElementSibling;
var any=n&&Array.from(n.children).some(function(li){return li.style.display!=='none';});h.style.display=any?'':'none';});});})();