import io
from Bio.Blast import NCBIXML
from Bio.Blast import NCBIWWW
from Bio.SeqUtils.ProtParam import ProteinAnalysis


class OrfUtil():
    def __init__(self, orf):
        self._orf = orf

    def get_orfs(self):
        return self._orf

    def get_blast_results(self, frame=0):
        if len(self._orf) > frame and frame < 3:
            result_handle = NCBIWWW.qblast("blastn", "nt", self._orf[frame], expect=0.05, hitlist_size=5)
            f = io.StringIO(result_handle.read())
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

            return homologs

    def get_analysed_sequence(self, frame=0):
        if len(self._orf) > frame and frame < 3:
            aseq = ProteinAnalysis(self._orf[frame])
            return {
                "molecular_weight": round(aseq.molecular_weight(), 2),
                "aromaticity": round(aseq.aromaticity(), 2),
                "instability_index": round(aseq.instability_index(), 2),
                "isoelectric_point": round(aseq.isoelectric_point(), 2),
                "secondary_structure_fraction": aseq.secondary_structure_fraction()
            }
