import unittest
from datetime import date,timedelta
from scripts.research_winner_accuracy import replay


class WinnerReplayTests(unittest.TestCase):
    def game(self,day,index,home='A',away='B',hs=100,score=90):
        return {'id':f'NBA:{day}:{index}','league':'NBA','season':'2024-25',
                'date':day,'home':home,'away':away,'home_score':hs,'away_score':score,'neutral':False}

    def test_same_day_outcomes_cannot_change_frozen_ranking(self):
        prior=[self.game(date(2023,1,1)+timedelta(days=i),i,hs=110,score=90) for i in range(220)]
        day=date(2024,1,1)
        slate=[self.game(day,500+i,hs=105+i,score=90) for i in range(4)]
        first=replay(prior+slate,bootstrap_draws=10)
        reversed_scores=[{**r,'home_score':1,'away_score':90} for r in slate]
        second=replay(prior+reversed_scores,bootstrap_draws=10)
        self.assertEqual(first['sample_game_ids'],second['sample_game_ids'])
        self.assertEqual(first['selected']['games'],3)
        self.assertEqual(first['selected_days'],1)
        self.assertNotEqual(first['selected']['accuracy'],second['selected']['accuracy'])
        self.assertEqual(sum(x['games'] for x in first['reliability']),3)
        self.assertIsNone(first['accuracy_day_block_interval'])

    def test_no_archived_games_does_not_invent_history(self):
        result=replay([],bootstrap_draws=10)
        self.assertEqual(result['selected']['games'],0)
        self.assertIsNone(result['selected']['accuracy'])


if __name__=='__main__':unittest.main()
