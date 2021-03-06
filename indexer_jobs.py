import os
import sys
import cx_Oracle
import estools

if not 'T0_ORACLE_CONNECTION_STRING' in os.environ:
    print('Connection to ORACLE DB not configured. Please set variable: T0_ORACLE_CONNECTION_STRING ')
    sys.exit(-1)

if not 'T0_ORACLE_PASS' in os.environ or not 'T0_ORACLE_USER' in os.environ:
    print('Please set variables:T0_ORACLE_USER and T0_ORACLE_PASS.')
    sys.exit(-1)

if not len(sys.argv) == 3:
    print('Pleae provide Start and End times in YYYY-mm-DD HH:MM::SS format.')
    sys.exit(-1)

start_date = sys.argv[1]
end_date = sys.argv[2]

print('Start date:', start_date, '\t End date:', end_date)


def OutputTypeHandler(cursor, name, defaultType, size, precision, scale):
    if defaultType == cx_Oracle.CLOB:
        return cursor.var(cx_Oracle.LONG_STRING, arraysize=cursor.arraysize)

user = os.environ['T0_ORACLE_USER']
passw = os.environ['T0_ORACLE_PASS']
conn = os.environ['T0_ORACLE_CONNECTION_STRING'].replace('jdbc:oracle:thin:@//', '')

con = cx_Oracle.connect(user + '/' + passw + '@' + conn)
con.outputtypehandler = OutputTypeHandler
print(con.version)

cursor = con.cursor()

columns = [
    'JOBID', 'TASKFK', 'CTIME', 'MTIME', 
    'JOBNAME', 'PARTNR', 'CONTROLSTATUS', 'CURRENTSTATUS',
    'SUPERVISOR', 'LASTATTEMPT', 'MAXATTEMPT', 'PRIORITY', 'JOBLOGS',
    'JOBPARS', 'LOCKEDBY', 'TRANSINFO', 'USERNAME', 'INPUTEVENTS',
    'CONTROLPARAMS'
]

escolumns = [
    'JOBID', 'TASKID', 'CTIME', 'MTIME', 
    'JOBNAME', 'PARTNR', 'CONTROLSTATUS', 'CURRENTSTATUS',
    'SUPERVISOR', 'LASTATTEMPT', 'MAXATTEMPT', 'PRIORITY', 'JOBLOGS',
    'JOBPARS', 'LOCKEDBY', 'TRANSINFO', 'USERNAME', 'INPUTEVENTS',
    'CONTROLPARAMS'
]


sel = 'SELECT '
sel += ','.join(columns)
sel += ' FROM JOBS '
sel += "WHERE MTIME >= TO_DATE('" + start_date + \
    "','YYYY - MM - DD HH24: MI: SS') AND MTIME < TO_DATE('" + end_date + "','YYYY - MM - DD HH24: MI: SS') "

print(sel)

cursor.execute(sel)

es = estools.get_es_connection()

data = []
count = 0
for row in cursor:
    doc = {}
    for colName, colValue in zip(escolumns, row):
        # print(colName, colValue)
        doc[colName] = colValue

    if doc['CTIME']:
        doc['CTIME'] = str(doc['CTIME']).replace(' ', 'T')
    if doc['MTIME']:
        doc['MTIME'] = str(doc['MTIME']).replace(' ', 'T')
    doc["_index"] = "t0_jobs"
    doc["_id"] = doc['JOBID']

    data.append(doc)
    # print(doc)

    if not count % 500:
        print(count)
        res = estools.bulk_index(data, es)
        if res:
            del data[:]
    count += 1

estools.bulk_index(data, es)
print('final count:', count)

con.close()
