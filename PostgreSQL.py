import psycopg2

class PostgreSQL:

    def __init__(self):
        self.conn = psycopg2.connect(host="localhost",
                                database="dyplomDB",
                                user="savchukndr",
                                password="savchukao22")

    def select_agreement_id(self, id_agreement_data):
        global row
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT id_agreement FROM agreement_data WHERE id_agreement_data = {}".format(id_agreement_data[-1:]))
            row = cur.fetchone()
            print(row)

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        return row

if __name__ == "__main__":
    p = PostgreSQL()
    p.select_agreement_id(2)