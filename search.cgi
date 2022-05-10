#!/usr/local/bin/python3

import mysql.connector
import jinja2
import cgi

# This line tells the template loader where to search for template files
templateLoader = jinja2.FileSystemLoader(searchpath="./templates")

# This creates your environment and loads a specific template
env = jinja2.Environment(loader=templateLoader)
template = env.get_template('searchresult.html')


# retrieves previously saved result by record ID
def main():
    form = cgi.FieldStorage()
    record_id = str(form.getfirst('record_id'))
    fasta_query = ""
    translated_query = list()
    analysed_seq = list()

    # Wrap up the database operation into try/except block
    try:
        # Connect to the database and create a cursor
        conn = mysql.connector.connect(user='lgalanz1', password='Dnjhybr!1',
                                       host='localhost', database='lgalanz1')
        curs = conn.cursor()
        qry = "SELECT r.id, r.nt_query FROM d2p_results r WHERE r.id=%s"
        curs.execute(qry, (record_id, ))

        for (id, nt_query) in curs:
            fasta_query = nt_query

        qry = """SELECT a.aa_seq, a.frame_id, rf.frame_name 
FROM d2p_aa_sequences a
LEFT JOIN d2p_reading_frames rf ON a.frame_id=rf.id
WHERE a.res_id=%s
ORDER BY a.frame_id"""
        curs.execute(qry, (record_id, ))

        for (aa_seq, frame_id, frame_name) in curs:
            translated_query.append({
                "frame_name": frame_name,
                "aa_seq": aa_seq
            })

        qry = """SELECT p.frame_id, rf.frame_name, p.molecular_weight, p.aromaticity, p.instability_index, p.isoelectric_point, s.helix, s.turn, s.sheet
FROM d2p_prot_info p
LEFT JOIN d2p_secondary_structure s ON p.secondary_structure_id=s.id
LEFT JOIN d2p_reading_frames rf ON p.frame_id=rf.id
WHERE p.res_id=%s
ORDER BY p.frame_id"""
        curs.execute(qry, (record_id, ))

        for (frame_id, frame_name, molecular_weight, aromaticity, instability_index, isoelectric_point, helix, turn, sheet) in curs:
            analysed_seq.append({
                "frame_name": frame_name,
                "molecular_weight": molecular_weight,
                "aromaticity": aromaticity,
                "instability_index": instability_index,
                "isoelectric_point": isoelectric_point,
                "helix": helix,
                "turn": turn,
                "sheet": sheet
            })

        # Close connection
        conn.close()

    except Exception as e:
        error = "There was a problem with database connection"
        print("Content-Type: text/html\n\n")
        print(template.render(error=error))

    print("Content-Type: text/html\n\n")
    print(template.render(translated_query=translated_query,
                          analysed_seq=analysed_seq,
                          fasta_query=fasta_query,
                          res_id=record_id))


if __name__ == '__main__':
    main()
