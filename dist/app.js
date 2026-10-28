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
  let board=null,selectedDay=dayString(),followToday=true,slateLimit=6;
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
    $('picks-title').textContent=isToday?'Today’s predicted winners':selectedDay===yesterday?'Yesterday’s predicted winners':displayDay(selectedDay);
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
    const available=books.map(b=>b.odds).filter(Number.isFinite),best=available.length>=2?Math.max(...available):null;
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
  function positionMarkup(context){
    if(!context||!context.teams)return '';
    return ['away','home'].map(side=>context.teams[side]).filter(Boolean).map(team=>{
      const entries=Object.entries(team.positions||{}).sort(([a],[b])=>a.localeCompare(b)).map(([position,counts])=>{
        const values=[['out','out'],['doubtful','doubtful'],['questionable','questionable'],['other','other listed']]
          .filter(([key])=>Number(counts[key])>0).map(([key,label])=>`${Number(counts[key])} ${label}`);
        return values.length?`${position==='UNKNOWN'?'position not reported':escape(position)}: ${values.join(', ')}`:'';
      }).filter(Boolean);
      return entries.length?`<p>${escape(team.team)} by position: ${entries.join(' · ')}.</p>`:'';
    }).join('');
  }
  function availabilityMarkup(p){
    if(p.league!=='NFL'){
      const link='<a href="https://official.nba.com/nba-injury-report-2026-27-season/" target="_blank" rel="noopener noreferrer">latest NBA player report</a>',c=p.nba_availability_context;
      if(!c||!c.teams)return `<p>NBA injuries and projected lineups are not included in this prediction. Check the ${link}; starters are unconfirmed.</p>`;
      const entries=['away','home'].map(side=>c.teams[side]).filter(Boolean).map(team=>`${escape(team.team)}: ${Number(team.counts.out)} out, ${Number(team.counts.questionable)} questionable or game-time decision, ${Number(team.counts.doubtful)} doubtful`).join(' · ');
      return `<p>Player-status counts from PropLine (ESPN), checked ${displayTime(c.observed_at)}: ${entries}. Reports may be incomplete and a missing name does not mean healthy. Check the ${link}; this information has not changed the prediction.</p>${positionMarkup(c)}`;
    }
    const current=p.nfl_provider_availability_context;
    const currentSummary=current&&current.teams?`<p>Player-status counts from PropLine (ESPN), checked ${displayTime(current.observed_at)}: ${['away','home'].map(side=>current.teams[side]).filter(Boolean).map(team=>`${escape(team.team)}: ${Number(team.counts.out)} out, ${Number(team.counts.questionable)} questionable or game-time decision, ${Number(team.counts.doubtful)} doubtful`).join(' · ')}. Reports may be incomplete; no listing does not mean healthy.</p>${positionMarkup(current)}`:'';
    const c=p.availability_context;
    if(!c||!c.teams)return `${currentSummary}<p>NFL starting quarterback and inactive list: unconfirmed. Injury information has not changed this prediction.</p>`;
    const entries=['away','home'].map(side=>c.teams[side]).filter(Boolean).map(team=>{
      const players=(team.entries||[]).map(x=>`${escape(x.name)}${x.position?' ('+escape(x.position)+')':''}: ${escape(x.report_status||x.practice_status||'unknown')}`);
      return `<p>${escape(team.team)} report: ${players.length?players.join(' · '):'no captured entries; health unknown'}${team.total_entries>players.length?' · '+(team.total_entries-players.length)+' more entries':''}.</p>`;
    }).join('');
    return `${currentSummary}<p>NFL report captured ${c.latest_observed_at?displayTime(c.latest_observed_at):'at an unavailable time'} from <a href="https://nflreadr.nflverse.com/reference/load_injuries.html" target="_blank" rel="noopener noreferrer">nflverse</a>. Starting QBs and inactive lists are unconfirmed; these reports may be incomplete. Injury information has not changed this prediction.</p>${entries}`;
  }
  function pickMarkup(p){
    const historical=!p.current;
    const statuses={win:'WON',loss:'LOST',void:'VOID',pending:'PENDING'};
    const status=Object.hasOwn(statuses,p.outcome)?p.outcome:'pending';
    const badge=historical&&status!=='pending'?`<span class="result-badge ${status}">${statuses[status]}</span>`:p.watching?'<span class="result-badge">WATCHING</span>':p.close_forecast?'<span class="result-badge">CLOSE CALL</span>':!historical&&p.rank?`<span class="result-badge">RANK #${Number(p.rank)}</span>`:'';
    const title=`<div class="pick-head"><div class="team-info"><h3>${escape(p.team)}<span>Moneyline</span></h3><p>${escape(p.league)} · vs ${escape(p.opponent)} · ${displayTime(p.starts_at)}</p></div><div class="pick-extra">${badge}</div></div>`;
    const injuryNotice=p.injury_report_after_forecast?'<p class="forecast-alert">Injury report updated after this winner was picked. This forecast did not account for that report; review the current status before relying on it.</p>':'';
    const context=`<details class="pick-context"><summary>Game details</summary>${availabilityMarkup(p)}${refereeMarkup(p)}${restMarkup(p.schedule_context)}${lineHistoryMarkup(p.line_history)}</details>`;
    if(!historical)return `<article class="pick">${title}${injuryNotice}${booksMarkup(p.books||[])}${context}</article>`;
    const recorded=Array.isArray(p.initial_books)?p.initial_books.filter(b=>Number.isFinite(b.odds)):[];
    if(recorded.length){const asofs=recorded.map(b=>new Date(b.as_of).valueOf()).filter(Number.isFinite);const stamp=asofs.length?' · '+displayTime(new Date(Math.min(...asofs))):'';return `<article class="pick">${title}<div class="price-caption">Odds at time of pick${stamp}</div>${booksMarkup(p.initial_books)}</article>`;}
    return `<article class="pick">${title}<div class="single-odds">Best odds recorded at time of pick${Number.isFinite(p.initial_best_odds)?' <strong>'+odds(p.initial_best_odds)+'</strong>':' unavailable'}</div></article>`;
  }
  function slateMarkup(g){
    const books=Object.entries(g.books||{});
    const best=side=>{
      const quotes=books.filter(([,b])=>Number.isFinite(b[side])).sort((a,b)=>b[1][side]-a[1][side]);
      if(!quotes.length)return 'Odds unavailable';
      const [name,b]=quotes[0];return `${odds(b[side])} · ${escape(name)} · observed ${displayTime(b.as_of)}`;
    };
    const gameDay=dayString(new Date(g.starts_at));
    const when=gameDay===today()?displayTime(g.starts_at):`${displayDay(gameDay)} · ${displayTime(g.starts_at)}`;
    return `<details class="slate-row"><summary><span class="slate-matchup"><strong>${escape(g.away)} at ${escape(g.home)}</strong><small>${escape(g.league)} · ${when}</small></span><span class="slate-winner">${g.predicted_winner?`Model: ${escape(g.predicted_winner)}${g.prediction_uncertain?' · close call':''}`:'Model unavailable'}</span></summary><div class="slate-row-detail"><p>${escape(g.away)}: ${best('away')}</p><p>${escape(g.home)}: ${best('home')}</p>${availabilityMarkup(g)}</div></details>`;
  }
  $('slate-filter').addEventListener('change',()=>{slateLimit=6;render();});
  $('slate-more').addEventListener('click',()=>{slateLimit+=6;render();});
  function render(){
    setDailyDetails();renderDates();renderFactors();if(!board)return;
    const gameSelect=$('manual-game'),prior=gameSelect.value;
    gameSelect.replaceChildren(new Option('Choose an upcoming game',''));
    for(const game of Array.isArray(board.games)?board.games:[]){
      if(new Date(game.starts_at)<=new Date())continue;
      for(const side of ['home','away'])gameSelect.add(new Option(`${game.league} · ${game.away} at ${game.home} · ${game[side]}`,`${game.id}|${side}`));
    }
    if([...gameSelect.options].some(o=>o.value===prior))gameSelect.value=prior;
    const accuracy=board.accuracy||{wins:0,losses:0};
    $('accuracy').textContent=accuracy.percent==null?'—':Number(accuracy.percent).toFixed(1)+'%';
    $('record').textContent=(accuracy.wins||0)+'W – '+(accuracy.losses||0)+'L · '+((accuracy.wins||0)+(accuracy.losses||0))+' settled'+(accuracy.pending?' · '+accuracy.pending+' pending':'');
    const now=new Date(),generated=new Date(board.generated_at),validDate=Number.isFinite(generated.valueOf());
    const all=Array.isArray(board.picks)?board.picks:[];
    const upcoming=all.filter(p=>new Date(p.starts_at)>now);
    const times=upcoming.flatMap(p=>(p.books||[]).filter(b=>b.as_of).map(b=>new Date(b.as_of).valueOf())).filter(Number.isFinite);
    const oldest=times.length?Math.min(...times):null;
    const stale=!validDate||now.valueOf()-generated.valueOf()>95*60*1000||generated.valueOf()-now.valueOf()>5*60*1000;
    const active=selectedDay===today()&&!stale?upcoming:[];
    const allHistory=(Array.isArray(board.history)?board.history:[]).filter(p=>p.pick_day===selectedDay);
    const earlier=[];
    const history=allHistory;
    const activeById=new Map(active.filter(p=>p.id).map(p=>[p.id,p]));
    const picks=history.map(p=>activeById.has(p.id)?Object.assign({},p,activeById.get(p.id),{current:true}):Object.assign({},p,{current:false}));
    for(const p of active)if(!p.id||!history.some(h=>h.id===p.id))picks.push(Object.assign({},p,{current:true}));
    picks.sort((a,b)=>{
      if(selectedDay===today()&&a.current&&b.current){
        const ar=Number.isFinite(a.rank)?a.rank:Infinity,br=Number.isFinite(b.rank)?b.rank:Infinity;
        if(ar!==br)return ar-br;
      }
      return new Date(a.starts_at)-new Date(b.starts_at);
    });
    $('count').textContent=picks.length===1?'1 pick':picks.length+' picks';
    const freshness=$('freshness');freshness.classList.toggle('stale',selectedDay===today()&&stale);
    freshness.textContent=selectedDay!==today()?'Saved picks and results · '+displayDay(selectedDay):stale?'Update delayed · saved picks shown':oldest?'Odds observed '+displayTime(new Date(oldest)):validDate?'Last checked '+displayTime(generated):'Waiting for data';
    if(!picks.length){
      $('picks').innerHTML=selectedDay!==today()?'<div class="empty"><strong>No saved winners for this day.</strong><p>The forecast history grows as each day is recorded.</p></div>':stale?'<div class="empty"><strong>Data update delayed.</strong><p>We’ll show picks when the necessary feeds are available.</p></div>':'<div class="empty"><strong>No unstarted games with usable model data right now.</strong><p>Predicted winners appear when the next slate and ratings are available.</p></div>';
    }else $('picks').innerHTML=picks.map(pickMarkup).join('');
    $('saved-section').hidden=!earlier.length;
    $('saved-list').innerHTML=earlier.map(p=>pickMarkup(Object.assign({},p,{current:false}))).join('');
    const shownIds=new Set(picks.filter(p=>p.current).map(p=>p.id));
    const allSlate=selectedDay===today()&&!stale?(Array.isArray(board.games)?board.games:[]).filter(g=>new Date(g.starts_at)>now&&!shownIds.has(g.id)):[];
    const filter=$('slate-filter').value;
    const slate=allSlate.filter(g=>filter==='today'?dayString(new Date(g.starts_at))===today():g.league===filter.toUpperCase());
    $('slate-section').hidden=!allSlate.length;
    $('slate-count').textContent=`${slate.length} game${slate.length===1?'':'s'}`;
    $('game-slate').innerHTML=slate.length?slate.slice(0,slateLimit).map(slateMarkup).join(''):'<p class="slate-empty">No games in this view.</p>';
    $('slate-more').hidden=slateLimit>=slate.length;
    const watched=selectedDay===today()&&!stale?(Array.isArray(board.watchlist)?board.watchlist:[]).filter(p=>{
      const stamps=(p.books||[]).filter(b=>Number.isFinite(b.odds)).map(b=>new Date(b.as_of).valueOf());
      return new Date(p.starts_at)>now&&!picks.some(x=>x.id===p.id)&&stamps.length>0&&stamps.every(t=>Number.isFinite(t)&&t<=now.valueOf()+5*60*1000&&now.valueOf()-t<=95*60*1000);
    }):[];
    $('watch-section').hidden=!watched.length;
    $('watchlist').innerHTML=watched.map(p=>pickMarkup(Object.assign({},p,{current:true,watching:true}))).join('');
  }
  async function refresh(){try{const r=await fetch('board.json?view='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('unavailable');board=await r.json();render();}catch(_){$('freshness').textContent='Board unavailable';$('picks').innerHTML='<div class="empty"><strong>Unable to load picks.</strong><p>Please try again shortly.</p></div>';}}
  const storageKey='pick-variable-ideas-v1';
  $('manual-odds-form').addEventListener('submit',e=>{
    e.preventDefault();
    const selected=$('manual-game').value,price=Number($('manual-price').value),stake=Number($('manual-stake').value);
    const split=selected.lastIndexOf('|'),id=selected.slice(0,split),side=selected.slice(split+1);
    const game=(Array.isArray(board?.games)?board.games:[]).find(g=>g.id===id&&new Date(g.starts_at)>new Date());
    const label=game?.[side];
    if(!game||!['home','away'].includes(side)||!label||!Number.isSafeInteger(price)||Math.abs(price)<100||!Number.isFinite(stake)||stake<=0||stake>1000000){
      $('manual-result').textContent='Select an upcoming game and enter valid American odds (at most -100 or at least +100) and a positive stake.';return;
    }
    const decimal=price<0?1+100/-price:1+price/100,breakEven=1/decimal;
    const observed=new Date().toISOString();
    try{
      const key='fanduel-manual-observations-v1';let saved=JSON.parse(localStorage.getItem(key)||'[]');
      if(!Array.isArray(saved))saved=[];
      saved.push({game_id:id,team:label,league:game.league,book:'FanDuel',source:'user entry',american_odds:price,stake,observed_at:observed});
      localStorage.setItem(key,JSON.stringify(saved.slice(-50)));
      $('manual-result').textContent=`Your FanDuel observation for ${label}: ${odds(price)}, saved ${displayTime(observed)}. Break-even: ${(breakEven*100).toFixed(2)}%. At $${stake.toFixed(2)}, winning profit $${(stake*(decimal-1)).toFixed(2)}; total payout $${(stake*decimal).toFixed(2)}. No validated edge is available to assess this price.`;
    }catch(_){$('manual-result').textContent='Browser storage unavailable; price was not saved.';}
  });
  function getIdeas(){try{const items=JSON.parse(localStorage.getItem(storageKey)||'[]');return Array.isArray(items)?items.slice(0,100):[];}catch(_){return [];}}
  function saveIdeas(items){try{localStorage.setItem(storageKey,JSON.stringify(items));return true;}catch(_){$('idea-message').textContent='Could not save on this device. Check your browser storage settings.';return false;}}
  function renderIdeas(){const ideas=getIdeas();$('ideas').innerHTML=ideas.map(item=>`<li><div><strong>${escape(item.name)}</strong><small>${escape(item.league)}${item.note?' · '+escape(item.note):''}</small></div><button type="button" class="remove-idea" data-idea="${escape(item.id)}" aria-label="Remove ${escape(item.name)}">Remove</button></li>`).join('');}
  $('idea-form').addEventListener('submit',e=>{e.preventDefault();const name=$('idea-name').value.trim();if(!name)return;const ideas=getIdeas();ideas.push({id:Date.now()+'-'+Math.random().toString(36).slice(2),name,league:$('idea-league').value,note:$('idea-note').value.trim()});if(saveIdeas(ideas)){$('idea-form').reset();renderIdeas();$('idea-message').textContent='Saved on this device. Ideas need data and testing before they can enter predictions.';}});
  $('ideas').addEventListener('click',e=>{const button=e.target.closest('[data-idea]');if(!button)return;if(saveIdeas(getIdeas().filter(x=>x.id!==button.dataset.idea)))renderIdeas();});
  setDailyDetails();renderIdeas();refresh();setInterval(refresh,60000);
}());
