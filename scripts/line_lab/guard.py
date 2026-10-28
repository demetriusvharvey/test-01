"""Conservative disagreement guard; no staking authorization without evidence."""

def assess_disagreement(model_home,retail_home,league):
    """Retail gap is descriptive; no untrained threshold is used to approve a bet."""
    return {'retail_gap':round(model_home-retail_home,6),'reference':'retail median, not sharp',
            'curve':'untrained','injury_status':'unknown','lineup_status':'unknown',
            'quarterback_status':'unknown' if league=='NFL' else 'not_applicable',
            'weather_status':'unknown' if league=='NFL' else 'not_applicable',
            'data_check':'limited','staking_allowed':False,'real_stake_units':0,
            'reason':'No preregistered sharp-market evidence and point-in-time news checks'}

def disagreement_curve(rows):
    """Descriptive observed win rates by signed model-minus-sharp gap.

    This function does not choose a threshold or authorize staking. Rows must be
    verified, settled, pregame model/sharp pairs and are empty until a sharp source
    and confirmed outcomes exist. Symmetric bins retain direction of disagreement.
    """
    bins={'below_-0.10':[],'-0.10_to_-0.05':[],'-0.05_to_-0.02':[],
          '-0.02_to_0.02':[],'0.02_to_0.05':[],'0.05_to_0.10':[],'above_0.10':[]}
    for row in rows:
        p=row.get('model_probability');sharp=row.get('sharp_probability');y=row.get('outcome')
        if not isinstance(p,(int,float)) or not isinstance(sharp,(int,float)) or y not in (0,1):continue
        d=p-sharp
        key='below_-0.10' if d<-.10 else '-0.10_to_-0.05' if d<-.05 else '-0.05_to_-0.02' if d<-.02 else '-0.02_to_0.02' if d<.02 else '0.02_to_0.05' if d<.05 else '0.05_to_0.10' if d<.10 else 'above_0.10'
        bins[key].append(y)
    return {key:{'games':len(values),'home_win_rate':sum(values)/len(values) if values else None} for key,values in bins.items()}
