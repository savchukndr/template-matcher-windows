import psycopg2
import re


class PostgreSQL:

    def __init__(self):
        self.conn = psycopg2.connect(host="localhost",
                                     database="dyplomDB",
                                     user="savchukndr",
                                     password="savchukao22")

    def select_agreement_id(self, image_key):
        global row
        try:
            searchObj = re.search(r'[^_]+$', image_key)
            cur = self.conn.cursor()
            cur.execute(
                "SELECT id_agreement FROM agreement_data WHERE id_agreement_data = {}".format(searchObj.group()))
            row = cur.fetchone()
            print(row)

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        return row

    def select_product_title(self, image_key):
        global row
        try:
            searchObj = re.search(r'[^_]+$', image_key)
            cur = self.conn.cursor()
            cur.execute("SELECT id_product FROM agreement_data WHERE id_agreement_data = {}".format(searchObj.group()))
            row = cur.fetchone()
            cur = self.conn.cursor()
            cur.execute("SELECT title FROM product WHERE id_product = {}".format(row[0]))
            row = cur.fetchone()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        return row

    def select_product_type_tytle(self, title):
        global row
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT id_product_type FROM product WHERE title = '{}'".format(title))
            row = cur.fetchone()
            cur = self.conn.cursor()
            cur.execute("SELECT title FROM product_type WHERE id_product_type = {}".format(row[0]))
            row = cur.fetchone()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        return row

    def select_agreement_data(self, image_key):
        global row
        try:
            searchObj = re.search(r'[^_]+$', image_key)
            cur = self.conn.cursor()
            cur.execute(
                "SELECT product_count, product_shelf_position FROM agreement_data WHERE id_agreement_data = {}".format(
                    searchObj.group()))
            row = cur.fetchone()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        return row

    def insert_result(self, values):
        try:
            print(values)
            cur = self.conn.cursor()
            sql = """INSERT INTO image_processing_result(product_count,is_product_on_exposition,product_localization,is_product_visible,is_distributor_visible,date_result,image_proc_estimation,id_image,id_agreement_data) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
            cur.execute(sql, (
                values[0], values[1], values[2], values[3], values[4], values[5], values[6], values[7], values[8],))
            self.conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)


if __name__ == "__main__":
    p = PostgreSQL()
    p.select_agreement_id(2)
