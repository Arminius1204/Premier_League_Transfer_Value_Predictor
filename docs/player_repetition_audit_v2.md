# Player Repetition Audit

- Unique players: 693
- Total transfers: 781
- Repeated players (>= 2 transfers): 85
- Maximum transfers per player: 3
- Players appearing across multiple seasons: 85

*Implication: Since master_player_id is NOT a feature, the model cannot memorize identities. However, correlated traits (like position, demographics) might be seen. This is realistic.*