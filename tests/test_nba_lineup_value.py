import unittest
from datetime import date
from scripts.line_lab.nba_lineup_value import rotation_value,lineup_associations


class LineupValueTests(unittest.TestCase):
    def fixture(self):
        now='2026-10-29T12:00:00+00:00';players=[];rosters={};effects={}
        for team,offset in (('ATL',1),('CLE',11)):
            ids=[str(i+offset) for i in range(10)]
            rosters[team]={'team':team,'player_ids':ids,'source':'fixture','verified':True,'observed_at':now}
            for i,p in enumerate(ids):
                players.append({'player_id':p,'team':team,'date':date(2026,10,28),'minutes':24.,'points':10.})
                effects[p]=5. if team=='ATL' and i==0 else 0.
        model={'model_version':'nba-stint-ridge-v1','promoted':False,'features':list(effects),'weights':list(effects.values()),
               'player_training_minutes':dict.fromkeys(effects,200.),'exported_at':'2026-10-29T11:00:00+00:00',
               'trained_before_date':'2026-10-29','input_hash':'fixture-hash'}
        event={'home':'ATL','away':'CLE','starts_at':'2026-10-30T00:00:00+00:00'}
        payload={'sport':'basketball_nba','count':1,'players':[{'team_abbr':'ATL','player_id':'espn:1','status_code':'questionable','status_since':now}]}
        return model,event,players,rosters,payload,now

    def test_replacement_delta_uses_learned_values_and_has_no_win_probability(self):
        model,event,players,rosters,payload,now=self.fixture()
        result=lineup_associations(model,event,players,rosters,payload,now,now)
        self.assertEqual(result['status'],'lineup_associations_available')
        a,b=result['scenarios'];self.assertGreater(a['home_minus_away_association'],b['home_minus_away_association'])
        self.assertEqual(a['change_from_all_available_counterfactual'],0.)
        self.assertLess(b['change_from_all_available_counterfactual'],0.)
        self.assertNotIn('home_probability',a)
        self.assertFalse(result['used_in_public_picks'])

    def test_unknown_effect_and_future_model_are_not_zero_value(self):
        model,event,players,rosters,payload,now=self.fixture()
        model['player_training_minutes']['2']=1.
        self.assertEqual(lineup_associations(model,event,players,rosters,payload,now,now)['status'],'unknown_player_effect')
        model['exported_at']='2026-10-30T12:00:00+00:00'
        self.assertEqual(lineup_associations(model,event,players,rosters,payload,now,now)['status'],'lineup_model_unavailable')
        self.assertIsNone(rotation_value({'features':[],'weights':[],'player_training_minutes':{}},{'players':[{'player_id':'missing','minutes':24.}]}))
