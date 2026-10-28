(function(){'use strict';
  const $=id=>document.getElementById(id);
  const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const odds=n=>n>0?'+'+n:'−'+Math.abs(n);
  const dateLong=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',weekday:'long',month:'long',day:'numeric'});
  const timeET=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',hour:'numeric',minute:'2-digit',hour12:true});
  const partsET=new Intl.DateTimeFormat('en-CA',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit'});
  const dayString=(d=new Date())=>{const p=Object.fromEntries(partsET.formatToParts(d).map(x=>[x.type,x.value]));return `${p.year}-${p.month}-${p.day}`;};
  const shiftDay=(s,n)=>{const d=new Date(s+'T12:00:00Z');d.setUTCDate(d.getUTCDate()+n);return d.toISOString().slice(0,10);};
  const displayDay=s=>dateLong.format(new Date(s+'T12:00:00Z'));
  const displayTime=s=>{const d=new Date(s);return Number.isFinite(d.valueOf())?timeET.format(d)+' ET':'Time unavailable';};
  const quotes=[
    'Big goals. Smart moves. One day at a time.',
    'Stay focused, stay patient, keep building.',
    'A clear mind makes room for bigger things.',
    'Good energy. Thoughtful moves. Bigger goals.',
    'Keep showing up for the life you’re building.',
    'Every day is another chance to move forward.',
    'Dream big, move with intention.',
    'Progress adds up. Keep going.',
    'Protect your peace and trust the process.',
    'Stay grounded and keep your goals in sight.',
    'A little patience can go a long way.',
    'Make space for the life you want.',
    'Small steps can lead to big things.',
    'Bring good energy to every new day.',
    'Work toward the future you picture.',
    'Keep your mindset positive and your decisions intentional.',
    'Your goals deserve your patience.',
    'Stay steady. Your progress matters.',
    'Build a little more, every day.',
    'Think long term. Move with purpose.',
    'Celebrate the progress, keep the vision.',
    'Keep your head clear and your goals close.',
    'Believe in what you’re building.',
    'Fresh day, fresh energy, clear goals.'
  ];
  let board=null,selectedDay=dayString(),followToday=true;
  const today=()=>dayString();
  function setDailyDetails(){
    const day=today();if(followToday)selectedDay=day;
    $('date-full').textContent=dateLong.format(new Date())+' · ET';
    $('pick-date').max=day;
    const index=Math.floor(Date.parse(day+'T00:00:00Z')/86400000)%quotes.length;
    $('daily-quote').textContent=quotes[(index+quotes.length)%quotes.length];
  }
  function setTab(name){
    for(const key of ['picks','variables']){
      const active=key===name, tab=$('tab-'+key);
      tab.classList.toggle('is-active',active);tab.setAttribute('aria-selected',String(active));tab.tabIndex=active?0:-1;
      $('panel-'+key).hidden=!active;
    }
  }
  for(const key of ['picks','variables'])$('tab-'+key).addEventListener('click',()=>setTab(key));
  document.querySelector('.tabs').addEventListener('keydown',e=>{
    if(!['ArrowRight','ArrowLeft'].includes(e.key))return;e.preventDefault();
    const next=$('tab-picks').getAttribute('aria-selected')==='true'?'variables':'picks';setTab(next);$('tab-'+next).focus();
  });
  function chooseDay(day){if(!day||day>today())return;selectedDay=day;followToday=day===today();render();}
  $('today-button').addEventListener('click',()=>chooseDay(today()));
  $('yesterday-button').addEventListener('click',()=>chooseDay(shiftDay(today(),-1)));
  $('pick-date').addEventListener('change',e=>chooseDay(e.target.value));
  function renderDates(){
    const nowDay=today(),yesterday=shiftDay(nowDay,-1),isToday=selectedDay===nowDay;
    $('picks-title').textContent=isToday?'Today’s picks':selectedDay===yesterday?'Yesterday’s picks':displayDay(selectedDay);
    $('today-button').classList.toggle('is-active',isToday);
    $('yesterday-button').classList.toggle('is-active',selectedDay===yesterday);
    $('pick-date').value=selectedDay;
  }
  function factorStatus(info,key){
    if(!info||!info.available)return ['Awaiting data',false];
    return info[key]?['In use',true]:['Being tested',false];
  }
  function renderFactors(){
    const details=(board&&board.model_details)||{};
    if(!details.NBA&&!details.NFL){$('dynamic-factors').innerHTML='<p class="muted">Model details will appear after the next data update.</p>';return;}
    $('dynamic-factors').innerHTML=['NBA','NFL'].map(league=>{
      const info=details[league],rest=factorStatus(info,'rest_weight'),form=factorStatus(info,'form_weight');
      const test=info&&info.available&&info.selection_season&&info.holdout_season?`Selection: ${escape(info.selection_season)} · holdout: ${escape(info.holdout_season)}${info.holdout_count?' · '+escape(info.holdout_count)+' holdout games':''}`:'Waiting for enough historical data to test.';
      return `<div class="factor-status"><div><strong>${league} · Rest between games</strong><span class="status-tag ${rest[1]?'on':''}">${rest[0]}</span></div><p>Compares each team’s days since its last game.</p></div><div class="factor-status"><div><strong>${league} · Recent scoring margin</strong><span class="status-tag ${form[1]?'on':''}">${form[0]}</span></div><p>Looks at point differences over the last five games.</p></div><p class="explanation">${test}</p>`;
    }).join('');
  }
  function booksMarkup(books){
    const available=books.map(b=>b.odds).filter(Number.isFinite),best=available.length?Math.max(...available):null;
    return `<div class="odds" aria-label="Sportsbook odds">${books.map(b=>`<div class="book ${b.odds!=null&&b.odds===best?'best':''}"><span class="book-name">${escape(b.name)}</span><div class="book-amount"><strong class="book-odds">${Number.isFinite(b.odds)?odds(b.odds):'—'}</strong>${b.odds!=null&&b.odds===best?'<span class="best-label">Best</span>':''}</div></div>`).join('')}</div>`;
  }
  function pickMarkup(p){
    const historical=!p.current;
    const statuses={win:'WON',loss:'LOST',void:'VOID',pending:'PENDING'};
    const status=Object.hasOwn(statuses,p.outcome)?p.outcome:'pending';
    const badge=historical?`<span class="result-badge ${status}">${statuses[status]}</span>`:'<span class="result-badge">OPEN PICK</span>';
    const title=`<div class="pick-head"><div class="team-info"><h3>${escape(p.team)}<span>Moneyline</span></h3><p>${escape(p.league)} · vs ${escape(p.opponent)} · ${displayTime(p.starts_at)}</p></div>${badge}</div>`;
    if(!historical)return `<article class="pick">${title}${booksMarkup(p.books||[])}</article>`;
    const recorded=Array.isArray(p.initial_books)?p.initial_books.filter(b=>Number.isFinite(b.odds)):[];
    if(recorded.length){const asofs=recorded.map(b=>new Date(b.as_of).valueOf()).filter(Number.isFinite);const stamp=asofs.length?' · '+displayTime(new Date(Math.min(...asofs))):'';return `<article class="pick">${title}<div class="price-caption">Odds at time of pick${stamp}</div>${booksMarkup(p.initial_books)}</article>`;}
    return `<article class="pick">${title}<div class="single-odds">Best odds recorded at time of pick${Number.isFinite(p.initial_best_odds)?' <strong>'+odds(p.initial_best_odds)+'</strong>':' unavailable'}</div></article>`;
  }
  function render(){
    setDailyDetails();renderDates();renderFactors();if(!board)return;
    const accuracy=board.accuracy||{wins:0,losses:0};
    $('accuracy').textContent=accuracy.percent==null?'—':Number(accuracy.percent).toFixed(1)+'%';
    $('record').textContent=(accuracy.wins||0)+'W – '+(accuracy.losses||0)+'L · '+((accuracy.wins||0)+(accuracy.losses||0))+' settled'+(accuracy.pending?' · '+accuracy.pending+' pending':'');
    const now=new Date(),generated=new Date(board.generated_at),validDate=Number.isFinite(generated.valueOf());
    const all=Array.isArray(board.picks)?board.picks:[];
    const upcoming=all.filter(p=>new Date(p.starts_at)>now);
    const times=upcoming.flatMap(p=>(p.books||[]).filter(b=>b.as_of).map(b=>new Date(b.as_of).valueOf())).filter(Number.isFinite);
    const oldest=times.length?Math.min(...times):null;
    const stale=!validDate||now.valueOf()-generated.valueOf()>95*60*1000||generated.valueOf()-now.valueOf()>5*60*1000||(oldest!=null&&now.valueOf()-oldest>95*60*1000);
    const active=selectedDay===today()&&!stale?upcoming:[];
    const history=(Array.isArray(board.history)?board.history:[]).filter(p=>p.pick_day===selectedDay);
    const activeById=new Map(active.filter(p=>p.id).map(p=>[p.id,p]));
    const picks=history.map(p=>activeById.has(p.id)?Object.assign({},p,activeById.get(p.id),{current:true}):Object.assign({},p,{current:false}));
    for(const p of active)if(!p.id||!history.some(h=>h.id===p.id))picks.push(Object.assign({},p,{current:true}));
    picks.sort((a,b)=>new Date(a.starts_at)-new Date(b.starts_at));
    $('count').textContent=picks.length===1?'1 pick':picks.length+' picks';
    const freshness=$('freshness');freshness.classList.toggle('stale',selectedDay===today()&&stale);
    freshness.textContent=selectedDay!==today()?'Saved picks and results · '+displayDay(selectedDay):stale?'Update delayed · saved picks shown':oldest?'Odds updated '+displayTime(new Date(oldest)):validDate?'Last checked '+displayTime(generated):'Waiting for data';
    if(!picks.length){
      const incomplete=Array.isArray(board.errors)&&board.errors.length>0;
      $('picks').innerHTML=selectedDay!==today()?'<div class="empty"><strong>No saved picks for this day.</strong><p>The archive grows as new picks are recorded.</p></div>':stale||incomplete?'<div class="empty"><strong>Data update delayed.</strong><p>We’ll show picks when the necessary feeds are available.</p></div>':'<div class="empty"><strong>No active picks right now.</strong><p>New picks appear when a game qualifies.</p></div>';
    }else $('picks').innerHTML=picks.map(pickMarkup).join('');
  }
  async function refresh(){try{const r=await fetch('board.json?view='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('unavailable');board=await r.json();render();}catch(_){$('freshness').textContent='Board unavailable';$('picks').innerHTML='<div class="empty"><strong>Unable to load picks.</strong><p>Please try again shortly.</p></div>';}}
  const storageKey='pick-variable-ideas-v1';
  function getIdeas(){try{const items=JSON.parse(localStorage.getItem(storageKey)||'[]');return Array.isArray(items)?items.slice(0,100):[];}catch(_){return [];}}
  function saveIdeas(items){try{localStorage.setItem(storageKey,JSON.stringify(items));return true;}catch(_){$('idea-message').textContent='Could not save on this device. Check your browser storage settings.';return false;}}
  function renderIdeas(){const ideas=getIdeas();$('ideas').innerHTML=ideas.map(item=>`<li><div><strong>${escape(item.name)}</strong><small>${escape(item.league)}${item.note?' · '+escape(item.note):''}</small></div><button type="button" class="remove-idea" data-idea="${escape(item.id)}" aria-label="Remove ${escape(item.name)}">Remove</button></li>`).join('');}
  $('idea-form').addEventListener('submit',e=>{e.preventDefault();const name=$('idea-name').value.trim();if(!name)return;const ideas=getIdeas();ideas.push({id:Date.now()+'-'+Math.random().toString(36).slice(2),name,league:$('idea-league').value,note:$('idea-note').value.trim()});if(saveIdeas(ideas)){$('idea-form').reset();renderIdeas();$('idea-message').textContent='Saved on this device. Ideas need data and testing before they can enter predictions.';}});
  $('ideas').addEventListener('click',e=>{const button=e.target.closest('[data-idea]');if(!button)return;if(saveIdeas(getIdeas().filter(x=>x.id!==button.dataset.idea)))renderIdeas();});
  setDailyDetails();renderIdeas();refresh();setInterval(refresh,60000);
}());
