"""Features components for the picks pipeline."""


def recent_margin(margins, team):
    values = margins.get(team, [])
    return sum(values) / len(values) if values else 0.0

def record_margin(margins, home, away, difference):
    for team, value in ((home, difference), (away, -difference)):
        margins[team] = (margins.get(team, []) + [value])[-5:]
