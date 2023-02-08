import os
import util


file_name = os.path.basename(__file__)
db_table = util.set_db_table(file_name)
conn = util.set_conn()
cur = conn.cursor()

get_result_statement = f"""
	SELECT 
		SUM(betresult) AS payout,
		COUNT(betresult) AS dollars_bet,
		SUM(betresult)*100/COUNT(betresult) AS rate_of_return
	FROM 
		{db_table}
	WHERE
		betresult != 0 AND betresult IS NOT NULL;
"""

util.sql_command(cur, conn, get_result_statement)

data = cur.fetchall()[0]
formatted = list(map(lambda x: round(x, 2), data))

print("Payout ($), Dollars Bet ($), Rate of Return (%)")
print(formatted)

cur.close()
conn.close()