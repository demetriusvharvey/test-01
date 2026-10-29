import unittest
from datetime import datetime,timedelta,timezone
from scripts.line_lab.player_impact import fit_player_impact,predict_player_impact,eligible_player_rows


class PlayerImpactTests(unittest.TestCase):
    def rows(self):
        result=[]
        for year in (2023,2024,2025):
            for i in range(8):
                start=datetime(year,10,i+1,tzinfo=timezone.utc)
                result.append({'game_id':f'{year}-{i}','league':'NFL','season':str(year),
                    'home':'A','away':'B','rights_verified':True,'roster_verified':True,
                    'exposure_type':'pregame_expected_share','baseline_probability':.5,'home_win':i%2,
                    'feature_observed_at':(start-timedelta(hours=2)).isoformat(),
                    'forecast_at':(start-timedelta(hours=1)).isoformat(),'starts_at':start.isoformat(),
                    'final_observed_at':(start+timedelta(hours=4)).isoformat(),
                    'exposures':{'playerA':float(i%2),'playerB':-float((i+1)%2)},
                    'player_teams':{'playerA':'A','playerB':'B'}})
        return result

    def test_final_participation_future_reports_and_wrong_rosters_are_rejected(self):
        rows=self.rows();cutoff='2026-01-01T00:00:00+00:00'
        self.assertEqual(len(eligible_player_rows(rows,'NFL',cutoff)),24)
        rows[0]['exposure_type']='final_snap_share'
        rows[1]['player_teams']['playerA']='B'
        rows[2]['feature_observed_at']=rows[2]['final_observed_at']
        rows[3]['rights_verified']=False
        self.assertEqual(len(eligible_player_rows(rows,'NFL',cutoff)),20)

    def test_season_validation_does_not_refit_and_unknown_players_do_not_get_zero_value(self):
        fit=fit_player_impact(self.rows(),'NFL','2026-01-01T00:00:00+00:00',16,8,4)
        self.assertEqual(fit['training_games'],16);self.assertEqual(fit['validation_games'],8)
        self.assertFalse(fit['promoted'])
        self.assertIsNotNone(predict_player_impact(fit,.5,{'playerA':1},'2026-01-02T00:00:00+00:00','2026-01-01T23:00:00+00:00'))
        self.assertIsNone(predict_player_impact(fit,.5,{'newPlayer':1},'2026-01-02T00:00:00+00:00','2026-01-01T23:00:00+00:00'))
        self.assertIsNone(predict_player_impact(fit,.5,{'playerA':1},'2025-01-01T00:00:00+00:00','2024-12-31T23:00:00+00:00'))


if __name__=='__main__':unittest.main()
