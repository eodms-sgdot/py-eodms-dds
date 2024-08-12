import psycopg2
import os

class EODMS_DB():

    def __init__(self, host=os.environ['PGHOST'],
                port=os.environ['PGPORT'], dbname=os.environ['PGDATABASE'],
                user=os.environ['PGUSER'], pwd=os.environ['PGPASSWORD']):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.pwd = pwd

        self.conn = psycopg2.connect(host=self.host, database=self.dbname,
                                     port=self.port, user=self.user,
                                     password=self.pwd)
        
    def map_results(self, cursor):
        out_rows = []
        names = [d[0] for d in cursor.description]
        indexes = range(len(names))
        for row in cursor:
            out_rows.append({names[i]: row[i] for i in indexes})
            
        return out_rows
        
    def print_records(self, records):
        
        for rec in records:
            print('---------------------------------------------------------')
            for k, v in rec.items():
                print(f' {k}: {v}')
                
    def execute(self, sql_command):

        curs = self.conn.cursor()
        curs.execute(sql_command)
        # items = curs.fetchall()
        
        res = self.map_results(curs)
            
        return res

    def select(self, sql_command):
        
        curs = self.conn.cursor()
        curs.execute(sql_command)
        res = self.map_results(curs)
        
        return res
        
    def update(self, sql_command):
        
        curs = self.conn.cursor()
        curs.execute(sql_command)
        
        updated_rows = curs.rowcount
        
        self.conn.commit()
        
        return updated_rows

    def close(self):
        self.conn.close()
        