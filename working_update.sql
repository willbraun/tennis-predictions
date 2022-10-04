CREATE OR REPLACE FUNCTION get_payout(odds INT)
RETURNS FLOAT
AS
$$
DECLARE
	payout FLOAT;
BEGIN
	IF odds >= 0
		THEN SELECT odds/100.0 INTO payout;
		ELSE SELECT -100.0/odds INTO payout;
	END IF;
	RETURN payout;
END
$$

LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_bet_result(winner VARCHAR(255), loser VARCHAR(255))
RETURNS FLOAT
AS
$$
DECLARE
	decisionvalue INT;
	dbplayer1namevalue VARCHAR(255);
	dbplayer2namevalue VARCHAR(255);
	dbplayer1oddsvalue INT;
	dbplayer2oddsvalue INT;
BEGIN
	SELECT 
		decision, player1name, player2name, player1odds, player2odds 
	FROM 
		matches_test 
	INTO 
		decisionvalue, dbplayer1namevalue, dbplayer2namevalue, dbplayer1oddsvalue, dbplayer2oddsvalue
	WHERE (player1name LIKE '%' || winner || '%' OR player2name LIKE '%' || winner || '%')
	AND (player1name LIKE '%' || loser || '%' OR player2name LIKE '%' || loser || '%')
	AND CAST(EXTRACT(epoch FROM NOW()) AS BIGINT)*1000 - startepoch < 345600000;
	
	IF decisionvalue = 0
		THEN RETURN 0;
	END IF;

	IF decisionvalue = 1	
		THEN 
			IF dbplayer1namevalue LIKE '%' || winner || '%'
				THEN RETURN get_payout(dbplayer1oddsvalue);
				ELSE RETURN -1;
			END IF;
	END IF;

	IF decisionvalue = 2	
		THEN 
			IF dbplayer2namevalue LIKE '%' || winner || '%'
				THEN RETURN get_payout(dbplayer2oddsvalue);
				ELSE RETURN -1;
			END IF;
	END IF;
END;
$$

LANGUAGE plpgsql;

UPDATE 
	matches_test 
SET 
	betresult = get_bet_result('Kygrios', 'Majchrzak')
WHERE (player1name LIKE '%Kygrios%' OR player2name LIKE '%Kygrios%')
AND (player1name LIKE '%Majchrzak%' OR player2name LIKE '%Majchrzak%')
AND CAST(EXTRACT(epoch FROM NOW()) AS BIGINT)*1000 - startepoch < 345600000;
