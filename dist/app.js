(function(){'use strict';
  const $=id=>document.getElementById(id);
  const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const odds=n=>n>0?'+'+n:'−'+Math.abs(n);
  const etDate=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',weekday:'long',month:'long',day:'numeric'});
  const etTime=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',hour:'numeric',minute:'2-digit',hour12:true});
  const abbr=team=>team.replace(/[^a-zA-Z ]/g,'').trim().split(/\s+/).slice(-1)[0].slice(0,3).toUpperCase();
  function render(board){
    const accuracy=board.accuracy||{wins:0,losses:0};
    $('accuracy').textContent=accuracy.percent==null?'—':Number(accuracy.percent).toFixed(1)+'%';
    $('record').textContent=accuracy.wins+'W – '+accuracy.losses+'L · '+(accuracy.wins+accuracy.losses)+' settled';
    const now=new Date(), generated=new Date(board.generated_at); const validDate=Number.isFinite(generated.valueOf());
    $('date-full').textContent=etDate.format(now);
    const all=Array.isArray(board.picks)?board.picks:[];
    // A static deployment may remain visible after game time; never show its pregame prices as current.
    const upcoming=all.filter(p=>new Date(p.starts_at)>now);
    const times=upcoming.flatMap(p=>(p.books||[]).filter(b=>b.as_of).map(b=>new Date(b.as_of).valueOf())).filter(Number.isFinite);
    const oldest=times.length?Math.min(...times):null;
    const stale=!validDate || now.valueOf()-generated.valueOf()>95*60*1000 || generated.valueOf()-now.valueOf()>5*60*1000 || (oldest!=null && now.valueOf()-oldest>95*60*1000);
    const picks=stale?[]:upcoming;
    $('count').textContent=String(picks.length).padStart(2,'0');
    const freshness=$('freshness'); freshness.classList.toggle('stale',stale);
    freshness.textContent=stale?'DATA DELAYED · Waiting for a fresh update':oldest?'Odds snapshot · '+etTime.format(new Date(oldest))+' ET':validDate?'Board checked '+etTime.format(generated)+' ET':'Waiting for data';
    const target=$('picks');
    if(!picks.length){
      const incomplete=Array.isArray(board.errors)&&board.errors.length>0;
      target.innerHTML=stale||incomplete?'<div class="empty"><strong>Data update delayed.</strong><p>We’ll show picks when the necessary feeds are available.</p></div>':'<div class="empty"><strong>No active picks right now.</strong><p>New picks appear when the model finds a qualifying game.</p></div>';return;
    }
    target.innerHTML=picks.map(p=>{
      const best=Math.max(...p.books.map(b=>b.odds).filter(Number.isFinite));
      const books=p.books.map(b=>`<div class="book ${b.odds!=null&&b.odds===best?'best':''}"><span class="book-name">${escape(b.name)}</span>${b.odds!=null&&b.odds===best?'<span class="best-label">BEST</span>':''}<strong class="book-odds">${b.odds==null?'—':odds(b.odds)}</strong></div>`).join('');
      return `<article class="pick"><div class="pick-head"><div class="pick-team"><div class="team-logo">${escape(abbr(p.team))}</div><div class="team-info"><h3>${escape(p.team)} ML</h3><p>${escape(p.league)} · vs ${escape(p.opponent)} · ${etTime.format(new Date(p.starts_at))} ET</p></div></div><div class="pick-meta"><strong>${(p.probability*100).toFixed(1)}%</strong><small>MODEL CHANCE</small></div></div><div class="odds">${books}</div></article>`;
    }).join('');
  }
  async function refresh(){try{const r=await fetch('board.json?view='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('unavailable');render(await r.json());}catch(_){$('freshness').textContent='Board unavailable';$('picks').innerHTML='<div class="empty"><strong>Unable to load picks.</strong><p>Please try again shortly.</p></div>';}}
  refresh();setInterval(refresh,60000);
}());
