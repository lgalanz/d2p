import io
from Bio.Blast import NCBIXML
from Bio.Blast import NCBIWWW
from Bio.SeqUtils.ProtParam import ProteinAnalysis


class OrfUtil:
    def __init__(self, orf):
        self._orf = orf

    def get_orfs(self):
        return self._orf

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
