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

CREATE OR REPLACE FUNCTION get_bet_result(winner INT)
RETURNS FLOAT
AS
$$
DECLARE
	iscorrectvalue BOOLEAN;
	decisionvalue INT;
	player1oddsvalue INT;
	player2oddsvalue INT;
	betresultvalue FLOAT;
BEGIN
	SELECT 
		iscorrect, decision, player1odds, player2odds 
	FROM 
		matches 
	INTO 
		iscorrectvalue, decisionvalue, player1oddsvalue, player2oddsvalue
	WHERE 
		player1name = 'Taro Daniel' AND player2name = 'Emilio Gomez' AND CAST(EXTRACT(epoch FROM NOW()) AS BIGINT)*1000 - startepoch < 86400000;

	IF decisionvalue = winner
		THEN 
			IF decisionvalue = 1
				THEN betresultvalue = get_payout(player1oddsvalue);
			END IF;

			IF decisionvalue = 2
				THEN betresultvalue = get_payout(player2oddsvalue);
			END IF;
		ELSE
			betresultvalue = -1;
	END IF;
	
	RETURN betresultvalue;
END;
$$

LANGUAGE plpgsql;

UPDATE 
	matches 
SET 
	iscorrect = (decision = 1),
	betresult = get_bet_result(1)
WHERE 
	player1name = 'Taro Daniel' AND player2name = 'Emilio Gomez' AND CAST(EXTRACT(epoch FROM NOW()) AS BIGINT)*1000 - startepoch < 86400000;