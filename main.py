import psycopg2
conn = psycopg2.connect(dbname='postgres1', user='user',
                        password='pyro127', host='localhost',
                        port='5432')
cursor = conn.cursor()

cursor.execute('SELECT * FROM students')
records = cursor.fetchall()

print("id\tname\tpoints")
for line in records:
    print(*line, sep="\t")
cursor.close()
conn.close()
