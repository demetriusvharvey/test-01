# Injury and availability research

Registered as H016 before implementation. The active picks currently do not
use injury status or player impacts. The status-count challenger is a
separate candidate: it adjusts the pre-existing team forecast using learned
home-minus-away counts of reported out, doubtful and questionable players.
Counts are a coarse starting point, not a lineup or star-value model.

Only reports observed before a pregame forecast can be captured. Missing team
reports, stale or future observations, conflicts and unreviewed sources are
excluded; absence of a listed player does not prove health. The NBA adapter
publishes aggregate counts only and is disabled until a user configures their
provider key. NBA data remain ineligible for training pending upstream rights
review. The NFL adapter uses already observed nflverse reports, and its
collection is independent of the quarterback play-by-play fetch.

The weekly job records each training attempt. A candidate needs at least 500
earlier games, 100 games in a later prior validation season, and three seasons
of qualifying data. A forecast from such a candidate is logged separately and
compared with a frozen baseline from the same instant. It must still pass
independent seasonal replications, a later untouched holdout, and the other
registered checks before promotion. No player impact, expected improvement,
accuracy, edge or profitable return has been established by this work.
