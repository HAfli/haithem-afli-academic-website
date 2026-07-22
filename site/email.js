(function(){
function addr(el){return el.getAttribute('data-u')+String.fromCharCode(64)+el.getAttribute('data-d');}
document.querySelectorAll('.email').forEach(function(el){
 var a=el.querySelector('[data-mailto]');
 if(a)a.addEventListener('click',function(e){e.preventDefault();window.location.href='mailto:'+addr(el);});
 var b=el.querySelector('.email-copy'),s=el.querySelector('.email-status');
 if(b)b.addEventListener('click',function(){var v=addr(el);
  function done(msg){if(s){s.textContent=' '+msg;}setTimeout(function(){if(s)s.textContent='';},4000);}
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(v).then(function(){done('Copied');},function(){done(v);});}
  else{done(v);}});
});
})();