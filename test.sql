CREATE OR REPLACE FUNCTION get_bet_result()
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
		iscorrectvalue, decisionvalue, player1oddsvalue, player2oddsvalue;

	IF iscorrectvalue = TRUE
		THEN 
			IF decisionvalue = 1
				THEN 
					IF player1oddsvalue >=0
						THEN betresultvalue = player1oddsvalue/100;
						ELSE betresultvalue = -100/player1oddsvalue;

					END IF;
			END IF;

			IF decisionvalue = 2
				THEN 
					IF player2oddsvalue >=0
						THEN betresultvalue = player2oddsvalue/100;
						ELSE betresultvalue = -100/player2oddsvalue;
					END IF;
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
	betresult = SELECT get_bet_result()
WHERE 
	player1name = 'Aleksandar Kovacevic';