#!/usr/local/bin/python3

import cgi, json
import mysql.connector


def main():
    print("Content-Type: application/json\n\n")
    form = cgi.FieldStorage()
    nt_seq = form.getvalue("nt_seq")

    if nt_seq is None:
        error = "No data provided"
        print(json.dumps([error]))
        return

    try:
        # Connect to the database and create a cursor
        conn = mysql.connector.connect(user='lgalanz1', password='Dnjhybr!1',
                                       host='localhost', database='lgalanz1')
        curs = conn.cursor()
        qry = "INSERT INTO d2p_results (nt_query) VALUES (%s)"
        curs.execute(qry, (nt_seq, ))
        conn.commit()
        res_id = curs.lastrowid
        for i in range(3):
            qry = "INSERT INTO d2p_aa_sequences (res_id, aa_seq, frame_id) VALUES (%s, %s, %s)"
            curs.execute(qry, (res_id, form.getvalue("frame" + str(i+1) + "[aa_seq]"), i + 1))
            conn.commit()

            qry = "INSERT INTO d2p_secondary_structure (helix, turn, sheet) VALUES (%s, %s, %s)"
            curs.execute(qry, (form.getvalue("frame" + str(i+1) + "[prot_info][secondary_structure_fraction][helix]"),
                               form.getvalue("frame" + str(i+1) + "[prot_info][secondary_structure_fraction][turn]"),
                               form.getvalue("frame" + str(i+1) + "[prot_info][secondary_structure_fraction][sheet]")
                               ))
            conn.commit()
            sec_str_id = curs.lastrowid

            qry = """INSERT INTO d2p_prot_info 
                  (res_id, frame_id, molecular_weight, aromaticity, instability_index, isoelectric_point, secondary_structure_id) 
                  VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            curs.execute(qry, (res_id,
                               i + 1,
                               form.getvalue("frame" + str(i+1) + "[prot_info][molecular_weight]"),
                               form.getvalue("frame" + str(i+1) + "[prot_info][aromaticity]"),
                               form.getvalue("frame" + str(i+1) + "[prot_info][instability_index]"),
                               form.getvalue("frame" + str(i+1) + "[prot_info][isoelectric_point]"),
                               sec_str_id
                               ))
            conn.commit()
        conn.close()

    except Exception as e:
        error = "There was a problem with database connection"
        print(json.dumps([error, e]))

    print(json.dumps([res_id]))


if __name__ == '__main__':
    main()

