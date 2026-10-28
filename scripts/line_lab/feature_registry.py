"""Versioned definitions for the active market-independent feature snapshot."""

FEATURE_REGISTRY_VERSION='pure-elo-input-v1.1'
FEATURES={
    'home_rating':'Home team rating from previously observed completed games',
    'away_rating':'Away team rating from previously observed completed games',
    'home_advantage':'League-level home adjustment fixed by the current model',
    'neutral':'Verified schedule neutral-site flag; otherwise false for NBA',
    'rest_weight':'Model coefficient; currently zero pending validation',
    'form_weight':'Model coefficient; currently zero pending validation',
    'home_last':'Most recent game date used in the frozen rating snapshot',
    'away_last':'Most recent game date used in the frozen rating snapshot',
    'home_margins':'Earlier game margins; current form weight is zero',
    'away_margins':'Earlier game margins; current form weight is zero',
    'source_text_sha256':'Hashes of raw data files observed before this snapshot',
}
