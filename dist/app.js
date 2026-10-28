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
    return info[key]?['In use',true]:['Not in use',false];
  }
  function renderFactors(){
    const details=(board&&board.model_details)||{};
    if(!details.NBA&&!details.NFL){$('dynamic-factors').innerHTML='<p class="muted">Model details will appear after the next data update.</p>';return;}
    $('dynamic-factors').innerHTML=['NBA','NFL'].map(league=>{
      const info=details[league],rest=factorStatus(info,'rest_weight'),form=factorStatus(info,'form_weight');
      const test=info&&info.available&&info.candidate_testing==='disabled'?'These factors stay out of picks while weekly research collects enough data to test them.':info&&info.available&&info.selection_season&&info.holdout_season?`Selection: ${escape(info.selection_season)} · holdout: ${escape(info.holdout_season)}${info.holdout_count?' · '+escape(info.holdout_count)+' holdout games':''}`:'Waiting for model details.';
      return `<div class="factor-status"><div><strong>${league} · Rest between games</strong><span class="status-tag ${rest[1]?'on':''}">${rest[0]}</span></div><p>Compares each team’s days since its last game.</p></div><div class="factor-status"><div><strong>${league} · Recent scoring margin</strong><span class="status-tag ${form[1]?'on':''}">${form[0]}</span></div><p>Looks at point differences over the last five games.</p></div><p class="explanation">${test}</p>`;
    }).join('');
  }
  function booksMarkup(books){
    const available=books.map(b=>b.odds).filter(Number.isFinite),best=available.length?Math.max(...available):null;
    return `<div class="odds" aria-label="Sportsbook odds">${books.map(b=>{const isBest=b.odds!=null&&b.odds===best,price=Number.isFinite(b.odds)?odds(b.odds):'unavailable';return `<div role="group" aria-label="${escape(b.name)}: ${price}${isBest?' — best odds':''}" class="book ${isBest?'best':''}"><span class="book-name">${escape(b.name)}</span><div class="book-amount"><strong class="book-odds">${Number.isFinite(b.odds)?price:'—'}</strong>${isBest?'<span class="best-label">Best</span>':''}</div></div>`;}).join('')}</div>`;
  }
  function lineHistoryMarkup(history){
    const points=history&&Array.isArray(history.points)?history.points.filter(p=>Number.isFinite(p.implied)&&Number.isFinite(p.odds)&&Number.isFinite(new Date(p.as_of).valueOf())):[];
    if(points.length<2)return '<p>Observed price movement: not enough matching snapshots.</p>';
    const values=points.map(p=>p.implied),low=Math.min(...values),high=Math.max(...values),range=high-low||1;
    const coords=points.map((p,i)=>`${(3+124*i/(points.length-1)).toFixed(1)},${(31-26*(p.implied-low)/range).toFixed(1)}`).join(' ');
    const first=points[0],last=points[points.length-1];
    return `<div class="line-history"><svg viewBox="0 0 130 36" role="img" aria-label="Observed implied price over time"><polyline points="${coords}" fill="none" stroke="currentColor" stroke-width="2"/></svg><p>${escape(history.book)} observed ${odds(first.odds)} at ${displayTime(first.as_of)} → ${odds(last.odds)} at ${displayTime(last.as_of)}. Snapshot history is not a verified opening or closing line.</p></div>`;
  }
  function restMarkup(context){
    if(!context||!context.teams)return '<p>Rest, travel and time-zone changes: unavailable.</p>';
    const labels=['away','home'].map(side=>context.teams[side]).filter(Boolean).map(team=>`${escape(team.team)}: ${Number(team.rest_days)} day${team.rest_days===1?'':'s'} rest${team.back_to_back?' (back-to-back)':''}`);
    return `<p>Rest from available completed-game data: ${labels.length?labels.join(' · '):'unavailable'}. Data may be incomplete; travel and time-zone changes are unknown. The market may already reflect schedule factors.</p>`;
  }
  function refereeMarkup(p){
    if(p.league!=='NBA')return '<p>NFL officiating crew: unconfirmed.</p>';
    const ref=p.referee_assignment;
    const label='<a href="https://official.nba.com/referee-assignments/" target="_blank" rel="noopener noreferrer">official NBA assignments</a>';
    if(!ref||!ref.crew_chief||!ref.referee||!ref.umpire)return `<p>NBA officiating crew: unconfirmed. Check ${label} closer to tipoff.</p>`;
    return `<p>NBA crew, observed ${displayTime(ref.observed_at)}: ${escape(ref.crew_chief)} (chief), ${escape(ref.referee)}, ${escape(ref.umpire)}. Assignments can change; no referee effect is used. Source: ${label}.</p>`;
  }
  function availabilityMarkup(p){
    if(p.league!=='NFL'){
      const link='<a href="https://official.nba.com/nba-injury-report-2026-27-season/" target="_blank" rel="noopener noreferrer">latest NBA player report</a>',c=p.nba_availability_context;
      if(!c||!c.teams)return `<p>NBA injuries and projected lineups are not included in this prediction. Check the ${link}; starters are unconfirmed.</p>`;
      const entries=['away','home'].map(side=>c.teams[side]).filter(Boolean).map(team=>`${escape(team.team)}: ${Number(team.counts.out)} out, ${Number(team.counts.questionable)} questionable or game-time decision, ${Number(team.counts.doubtful)} doubtful`).join(' · ');
      return `<p>Player-status counts from PropLine (ESPN), checked ${displayTime(c.observed_at)}: ${entries}. Reports may be incomplete and a missing name does not mean healthy. Check the ${link}; this information has not changed the prediction.</p>`;
    }
    const c=p.availability_context;
    if(!c||!c.teams)return '<p>NFL injury report, starting quarterback and inactive list: unavailable or unconfirmed.</p>';
    const entries=['away','home'].map(side=>c.teams[side]).filter(Boolean).map(team=>{
      const players=(team.entries||[]).map(x=>`${escape(x.name)}${x.position?' ('+escape(x.position)+')':''}: ${escape(x.report_status||x.practice_status||'unknown')}`);
      return `<p>${escape(team.team)} report: ${players.length?players.join(' · '):'no captured entries; health unknown'}${team.total_entries>players.length?' · '+(team.total_entries-players.length)+' more entries':''}.</p>`;
    }).join('');
    return `<p>NFL report captured ${c.latest_observed_at?displayTime(c.latest_observed_at):'at an unavailable time'} from <a href="https://nflreadr.nflverse.com/reference/load_injuries.html" target="_blank" rel="noopener noreferrer">nflverse</a>. Starting QBs and inactive lists are unconfirmed; these reports may be incomplete.</p>${entries}`;
  }
  function pickMarkup(p){
    const historical=!p.current;
    const statuses={win:'WON',loss:'LOST',void:'VOID',pending:'PENDING'};
    const status=Object.hasOwn(statuses,p.outcome)?p.outcome:'pending';
    const badge=historical&&status!=='pending'?`<span class="result-badge ${status}">${statuses[status]}</span>`:p.watching?'<span class="result-badge">WATCHING</span>':'';
    const title=`<div class="pick-head"><div class="team-info"><h3>${escape(p.team)}<span>Moneyline</span></h3><p>${escape(p.league)} · vs ${escape(p.opponent)} · ${displayTime(p.starts_at)}</p></div><div class="pick-extra">${badge}</div></div>`;
    const context=`<details class="pick-context"><summary>Game details</summary>${availabilityMarkup(p)}${refereeMarkup(p)}${restMarkup(p.schedule_context)}${lineHistoryMarkup(p.line_history)}</details>`;
    if(!historical)return `<article class="pick">${title}${booksMarkup(p.books||[])}${context}</article>`;
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
    const watched=selectedDay===today()&&!stale?(Array.isArray(board.watchlist)?board.watchlist:[]).filter(p=>{
      const stamps=(p.books||[]).filter(b=>Number.isFinite(b.odds)).map(b=>new Date(b.as_of).valueOf());
      return new Date(p.starts_at)>now&&!picks.some(x=>x.id===p.id)&&stamps.length>0&&stamps.every(t=>Number.isFinite(t)&&t<=now.valueOf()+5*60*1000&&now.valueOf()-t<=95*60*1000);
    }):[];
    $('watch-section').hidden=!watched.length;
    $('watchlist').innerHTML=watched.map(p=>pickMarkup(Object.assign({},p,{current:true,watching:true}))).join('');
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
