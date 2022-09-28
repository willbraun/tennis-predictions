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

CREATE OR REPLACE FUNCTION get_bet_result(p1_name VARCHAR(255), p2_name VARCHAR(255), winner VARCHAR(255))
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
		matches 
	INTO 
		decisionvalue, dbplayer1namevalue, dbplayer2namevalue, dbplayer1oddsvalue, dbplayer2oddsvalue
	WHERE 
		p1_name IN (player1name, player2name) AND p2_name IN (player1name, player2name) AND CAST(EXTRACT(epoch FROM NOW()) AS BIGINT)*1000 - startepoch < 172800000;
	
	IF decisionvalue = 0
		THEN RETURN 0;
	END IF;

	IF decisionvalue = 1	
		THEN 
			IF winner = dbplayer1namevalue
				THEN RETURN get_payout(dbplayer1oddsvalue);
				ELSE RETURN -1;
			END IF;
	END IF;

	IF decisionvalue = 2	
		THEN 
			IF winner = dbplayer2namevalue
				THEN RETURN get_payout(dbplayer2oddsvalue);
				ELSE RETURN -1;
			END IF;
	END IF;
END;
$$

LANGUAGE plpgsql;

UPDATE 
	matches 
SET 
	betresult = get_bet_result('Ugo Humbert', 'Dimitar Kuzmanov', 'Ugo Humbert')
WHERE 
	'Ugo Humbert' IN (player1name, player2name) AND 'Dimitar Kuzmanov' IN (player1name, player2name) AND CAST(EXTRACT(epoch FROM NOW()) AS BIGINT)*1000 - startepoch < 172800000;