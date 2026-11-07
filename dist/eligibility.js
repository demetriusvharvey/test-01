(function(root){'use strict';
  const labels={
    validation_insufficient:'Model betting validation is still pending',
    availability_model_unvalidated:'Player injury adjustments have not passed validation',
    validated_uncertainty_unavailable:'Model uncertainty has not passed validation',
    injury_information_unverified:'Complete injury information is not verified',
    starting_lineups_unconfirmed:'NBA starting lineups are unconfirmed',
    starting_quarterbacks_unconfirmed:'NFL starting quarterbacks are unconfirmed',
    odds_missing_stale_or_unverified:'FanDuel prices are missing, expired or unverified',
    odds_identity_mismatch:'FanDuel prices do not match the game',
    forecast_not_fresh_pregame:'The forecast needs a fresh pregame update',
    forecast_game_mismatch:'Forecast identity does not match the game',
    invalid_or_missing_input:'Required model inputs are unavailable',
    positive_edge_not_established:'A conservative price advantage has not been established'
  };
  const validation=new Set(['validation_insufficient','availability_model_unvalidated','validated_uncertainty_unavailable']);
  const dateFormat=new Intl.DateTimeFormat('en-CA',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit'});
  const day=d=>{const p=Object.fromEntries(dateFormat.formatToParts(d).map(x=>[x.type,x.value]));return `${p.year}-${p.month}-${p.day}`;};
  function activePick(p,now){
    const current=+now,expires=Date.parse(p.expires_at),predicted=Date.parse(p.predicted_at);
    return p.recommendation_eligible===true&&!p.data_stale&&Date.parse(p.starts_at)>current&&
      day(new Date(p.starts_at))===day(now)&&Number.isFinite(expires)&&expires>current&&
      Number.isFinite(predicted)&&predicted<=current&&current-predicted<=20*60000;
  }
  function readiness(board,now){
    const games=(board.games||[]).filter(g=>Date.parse(g.scheduled_starts_at||g.starts_at)>+now&&day(new Date(g.scheduled_starts_at||g.starts_at))===day(now));
    const blockers={};let forecasts=0,qualified=0;
    for(const g of games){
      const f=g.forecast;if(!f)continue;forecasts++;
      const d=f.decision||{},reasons=new Set(d.reasons||[]);
      const predicted=Date.parse(f.predicted_at);
      if(!Number.isFinite(predicted)||predicted>+now||+now-predicted>20*60000)reasons.add('forecast_not_fresh_pregame');
      const price=g.books&&g.books.FanDuel,source=Date.parse(price&&price.as_of);
      if(!Number.isFinite(source)||source>+now||+now-source>20*60000)reasons.add('odds_missing_stale_or_unverified');
      if(d.eligible===true&&Date.parse(g.starts_at)>+now&&reasons.size===0&&Date.parse(d.expires_at)>+now)qualified++;
      for(const reason of reasons)blockers[reason]=(blockers[reason]||0)+1;
    }
    const pending=Object.keys(blockers).some(r=>validation.has(r));
    const data=forecasts<games.length||Object.keys(blockers).some(r=>!validation.has(r)&&r!=='positive_edge_not_established');
    return {games:games.length,forecasts,qualified,blockers,status:!games.length?'no_upcoming_games':qualified?'qualified':pending?'validation_pending':data?'data_unavailable':'no_qualified_edge'};
  }
  const api={labels,activePick,readiness};
  if(typeof module==='object'&&module.exports)module.exports=api;else root.PickEligibility=api;
})(typeof globalThis==='object'?globalThis:this);
