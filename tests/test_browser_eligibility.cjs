'use strict';
const assert=require('node:assert/strict');
const {activePick,readiness,labels}=require('../dist/eligibility.js');
const now=new Date('2026-11-01T20:00:00Z');
const p={recommendation_eligible:true,starts_at:'2026-11-01T23:00:00Z',predicted_at:'2026-11-01T19:55:00Z',expires_at:'2026-11-01T20:05:00Z'};
assert.equal(activePick(p,now),true);
for(const change of [{expires_at:null},{expires_at:'2026-11-01T20:00:00Z'},{data_stale:true},{recommendation_eligible:false},{predicted_at:'2026-11-01T20:01:00Z'},{starts_at:'2026-11-02T23:00:00Z'}])assert.equal(activePick({...p,...change},now),false);
const game={starts_at:p.starts_at,books:{FanDuel:{as_of:p.predicted_at}},forecast:{predicted_at:p.predicted_at,decision:{eligible:false,reasons:['validation_insufficient']}}};
const b={games:[game,{...game,starts_at:'2026-11-02T23:00:00Z'}]};
assert.equal(readiness(b,now).games,1);
assert.equal(readiness(b,now).status,'validation_pending');
assert.equal(readiness({games:[{...game,forecast:{...game.forecast,decision:{eligible:false,reasons:['positive_edge_not_established']}}}]},now).status,'no_qualified_edge');
assert.equal(readiness({games:[{...game,forecast:undefined}]},now).status,'data_unavailable');
assert.equal(readiness({games:[]},now).status,'no_upcoming_games');
const later=new Date('2026-11-01T20:30:00Z');
assert.equal(readiness(b,later).blockers.odds_missing_stale_or_unverified,1);
assert.equal(readiness(b,later).blockers.forecast_not_fresh_pregame,1);
const approved={...game,forecast:{...game.forecast,decision:{eligible:true,reasons:[],expires_at:p.expires_at}}};
assert.equal(readiness({games:[approved]},now).qualified,1);
assert.equal(readiness({games:[approved]},later).qualified,0);
console.log('Browser eligibility: expiry, ET day, missing data, validation and no-edge cases passed.');

// Exercise the actual page renderer during a feed outage. A delayed source
// must keep its forecasts visible as expired research, with no promoted bet.
const fs=require('node:fs'),vm=require('node:vm');
class Clock extends Date {
  constructor(...args){super(...(args.length?args:[now]));}
  static now(){return +now;}
}
const elements=new Map();
function element(id){
  if(!elements.has(id))elements.set(id,{hidden:false,value:id==='slate-filter'?'today':'',textContent:'',innerHTML:'',
    classList:{toggle(){}},setAttribute(){},getAttribute(){return 'true';},addEventListener(){},focus(){}});
  return elements.get(id);
}
const delayed={generated_at:'2026-11-01T17:00:00Z',selection_policy:{},picks:[],history:[],games:[{
  ...game,league:'NBA',home:'Knicks',away:'Celtics',predicted_winner:'Knicks',
  forecast:{...game.forecast,model_version:'test-research',predicted_at:'2026-11-01T17:00:00Z'}}]};
vm.runInNewContext(fs.readFileSync(require.resolve('../dist/app.js'),'utf8'),{
  Intl,Date:Clock,PickEligibility:{readiness,activePick,labels},
  document:{getElementById:element,querySelector:()=>element('tabs')},localStorage:{getItem:()=>null},
  fetch:async()=>({ok:true,json:async()=>delayed}),setInterval(){}
});
setImmediate(()=>{
  assert.match(element('selection-status').textContent,/Update delayed/);
  assert.equal(element('slate-section').hidden,false);
  assert.equal(element('slate-section').open,true);
  assert.match(element('game-slate').innerHTML,/Model: Knicks/);
  assert.match(element('game-slate').innerHTML,/EXPIRED/);
  assert.equal(element('eligibility-details').hidden,false);
  assert.match(element('eligibility-reasons').innerHTML,/validation/);
  assert.equal(element('count').textContent,'0 recommendations · 0 saved forecasts');
  console.log('Delayed-board renderer: visible expired research, exact blockers and zero bets passed.');
});
