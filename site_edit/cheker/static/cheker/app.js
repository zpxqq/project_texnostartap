(function(){
  const $=(s,r=document)=>r.querySelector(s); const $$=(s,r=document)=>[...r.querySelectorAll(s)];
  function speak(text){
    if(!('speechSynthesis' in window)){alert('В этом браузере синтез речи недоступен.');return;}
    speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(text); u.lang='ru-RU';u.rate=.94;speechSynthesis.speak(u);
  }
  $$('.speak').forEach(b=>b.addEventListener('click',()=>speak(b.dataset.text||'')));
  const saved=localStorage.getItem('vedi_last_url'); if(saved) $$('[data-project-url]').forEach(el=>el.textContent=saved.replace(/^https?:\/\//,''));
  $$('.save-project').forEach(b=>b.addEventListener('click',()=>{localStorage.setItem('vedi_has_project','1');location.href='dashboard.html'}));
})();
