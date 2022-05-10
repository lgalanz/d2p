#!/usr/local/bin/python3

import cgi, json
import mysql.connector


# saves the results of the sequence analysis in the database
def main():
    print("Content-Type: application/json\n\n")
    form = cgi.FieldStorage()
    nt_seq = form.getvalue("nt_seq")

    # validate the submitted data before writing it to the database
    if not validate(form):
        error = "No data provided or data is incomplete"
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


# validates the submitted data
def validate(form):
    if form.getvalue("nt_seq") is None:
        return False

    for i in range(3):
        frame_id = "frame" + str(i+1)
        if (form.getvalue(frame_id + "[aa_seq]") is None
                or form.getvalue(frame_id + "[prot_info][secondary_structure_fraction][helix]") is None
                or form.getvalue(frame_id + "[prot_info][secondary_structure_fraction][turn]") is None
                or form.getvalue(frame_id + "[prot_info][secondary_structure_fraction][sheet]") is None
                or form.getvalue(frame_id + "[prot_info][molecular_weight]") is None
                or form.getvalue(frame_id + "[prot_info][aromaticity]") is None
                or form.getvalue(frame_id + "[prot_info][instability_index]") is None
                or form.getvalue(frame_id + "[prot_info][isoelectric_point]") is None):
            return False
    return True


if __name__ == '__main__':
    main()

