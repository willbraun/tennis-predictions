INSERT INTO matches (Id, Player1Name, Player2Name, Player1Prob, Player1Odds, Player2Odds, Player1Total, Player2Total, Decision, StartEpoch, MatchId) 
VALUES (DEFAULT, 'Test1', 'Test2', 60.4, -120, 130, -200, 100, 2, 1231231234, 99999)
ON CONFLICT(MatchId) DO NOTHING;