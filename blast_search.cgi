#!/usr/local/bin/python3

import io
import json
from Bio.Blast import NCBIWWW, NCBIXML
import cgi


# using NCBIWWW from Bio.Blast, find 5 homologous sequences to the target query
def main():
    print("Content-Type: application/json\n\n")
    form = cgi.FieldStorage()
    orf = form.getvalue('orf')
    """ result_handle = NCBIWWW.qblast("blastp", "nr", orf[1:5], expect=0.05, hitlist_size=5)
    f = io.StringIO(result_handle.read()) """

    # using a fallback mocked data due to the server timeout that does not allow to run the blast search
    f = open("blastp_human_output.xml")
    results = NCBIXML.parse(f)
    records = list(results)

    homologs = []
    if len(records) != 0:
        for r in records[0].alignments:
            homologs.append({
                'align_length': r.hsps[0].align_length,
                'evalue': r.hsps[0].expect,
                'accession': r.accession,
                'definition': r.hit_def
            })
    print(json.dumps(homologs))


if __name__ == '__main__':
    main()
