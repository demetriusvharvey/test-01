"""Constants components for the picks pipeline."""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
ET = ZoneInfo('America/New_York')
BOOKS = [('fanduel','FanDuel'),('draftkings','DraftKings'),('betmgm','BetMGM'),('caesars','Caesars'),('fanatics','Fanatics'),('betrivers','BetRivers')]
NBA_SEASONS = ['2022-23','2023-24','2024-25','2025-26','2026-27']
NBA_TEAMS = {
 'atlanta hawks':'ATL','boston celtics':'BOS','brooklyn nets':'BKN','charlotte hornets':'CHA','chicago bulls':'CHI','cleveland cavaliers':'CLE','dallas mavericks':'DAL','denver nuggets':'DEN','detroit pistons':'DET','golden state warriors':'GSW','houston rockets':'HOU','indiana pacers':'IND','la clippers':'LAC','los angeles clippers':'LAC','los angeles lakers':'LAL','l.a. lakers':'LAL','memphis grizzlies':'MEM','miami heat':'MIA','milwaukee bucks':'MIL','minnesota timberwolves':'MIN','new orleans pelicans':'NOP','new york knicks':'NYK','oklahoma city thunder':'OKC','orlando magic':'ORL','philadelphia 76ers':'PHI','phoenix suns':'PHX','portland trail blazers':'POR','sacramento kings':'SAC','san antonio spurs':'SAS','toronto raptors':'TOR','utah jazz':'UTA','washington wizards':'WAS'}
NFL_TEAMS = {
 'arizona cardinals':'ARI','atlanta falcons':'ATL','baltimore ravens':'BAL','buffalo bills':'BUF','carolina panthers':'CAR','chicago bears':'CHI','cincinnati bengals':'CIN','cleveland browns':'CLE','dallas cowboys':'DAL','denver broncos':'DEN','detroit lions':'DET','green bay packers':'GB','houston texans':'HOU','indianapolis colts':'IND','jacksonville jaguars':'JAX','kansas city chiefs':'KC','las vegas raiders':'LV','los angeles chargers':'LAC','los angeles rams':'LA','miami dolphins':'MIA','minnesota vikings':'MIN','new england patriots':'NE','new orleans saints':'NO','new york giants':'NYG','new york jets':'NYJ','philadelphia eagles':'PHI','pittsburgh steelers':'PIT','san francisco 49ers':'SF','seattle seahawks':'SEA','tampa bay buccaneers':'TB','tennessee titans':'TEN','washington commanders':'WAS'}
ALIASES={'OAK':'LV','SD':'LAC','STL':'LA','LAR':'LA','JAC':'JAX','PHO':'PHX','NOH':'NOP','NJN':'BKN','CHO':'CHA'}


def team_code(name, league):
    name = ' '.join(str(name).strip().lower().split())
    return (NBA_TEAMS if league == 'NBA' else NFL_TEAMS).get(name)

def normalize_code(code): return ALIASES.get(code,code)

def game_id(league, game_date, away, home): return f'{league.lower()}:{game_date}:{normalize_code(away)}:{normalize_code(home)}'
