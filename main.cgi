#!/usr/local/bin/python3

from OrfUtil import OrfUtil
import jinja2
import cgi

# This line tells the template loader where to search for template files
templateLoader = jinja2.FileSystemLoader(searchpath="./templates")

# This creates your environment and loads a specific template
env = jinja2.Environment(loader=templateLoader)


# main() function controls the main page of the web app
def main():
    form = cgi.FieldStorage()

    # if the form was submitted run the analysis of the sequence
    if form.getvalue("submitted") == "1":
        if form.getvalue("fasta_query"):
            run_analysis(form.getvalue("fasta_query"))
        else:
            template = env.get_template('index.html')
            error = "Please enter a nucleotide sequence"
            print("Content-Type: text/html\n\n")
            print(template.render(error=error, debug=3))
    # otherwise load the default page with the text area
    else:
        template = env.get_template('index.html')
        print("Content-Type: text/html\n\n")
        print(template.render(debug=1))


def run_analysis(fasta_data):
    fasta_query = get_nc_seq_from_fasta(fasta_data)

    # validate the submitted query
    if not is_valid_nc_seq(fasta_query):
        template = env.get_template('index.html')
        error = "Please enter a nucleotide sequence"
        print("Content-Type: text/html\n\n")
        print(template.render(error=error, debug=4))

    translated_query = []
    frame_coords = []
    longest_orf = []
    orf = []
    # analyse three reading frames in 5'3' direction
    for i in range(3):
        frame_coords.append(parse_fasta_query(fasta_query, i))  # identify the ORF coordinates in the sequence
        longest_orf.append(get_longest_orf(frame_coords[i]))  # identify the coordinated of the longest ORF that will be analyzed further
        orf.append(fasta_query[longest_orf[i][0]:longest_orf[i][1]])  # save the longest ORFs in a list
        # translate the entire query
        translated_query.append(highlight_substring(
            translate_to_aa_seq(fasta_query, i),
            frame_coords[i],
            longest_orf[i]
        ))

    orf_util = OrfUtil(orf)
    analysed_seq = []
    for i in range(3):
        analysed_seq.append(orf_util.get_analysed_sequence(i))  # calculate the properties of the potential protein coded by the longest ORF

    template = env.get_template('result.html')
    print("Content-Type: text/html\n\n")
    print(template.render(translated_query=translated_query,
                          analysed_seq=analysed_seq,
                          fasta_query=fasta_query,
                          debug=2))


# identify the coordinates of the longest ORF
def get_longest_orf(coordinates):
    max_len = 0
    start = 0
    stop = 0
    if isinstance(coordinates, list):
        for c in coordinates:
            try:
                if c['stop'] - c['start'] > max_len:
                    max_len = c['stop'] - c['start']
                    start = c['start']
                    stop = c['stop']
            except:
                start = 0
                stop = 0
    return start, stop


# parses the submitted sequence by removing the first descriptive live
def get_nc_seq_from_fasta(query):
    if query.startswith('>'):
        lines = query.splitlines()
        lines.pop(0)
        return "".join(lines)
    else:
        return query


# validate the nucleotide sequence
def is_valid_nc_seq(query):
    return set(query.upper()) <= set('ACTG')


# identify the coordinates of the ORFs in the sequence
def parse_fasta_query(query, frame_count):
    query = query.upper()
    start_codon = 'ATG'
    stop_codons = ['TAA', 'TAG', 'TGA']

    coordinates = []

    j = 0
    for i in range(frame_count, len(query) - (len(query) - frame_count) % 3, 3):
        if query[i:i + 3] == start_codon and i > j:
            start = i
            for j in range(i, len(query), 3):
                if query[j:j + 3] in stop_codons:
                    stop = j
                    break
            if stop is None:
                stop = j

            coordinates.append({
                "start": start,
                "stop": stop
            })

    return coordinates


# translate a sequence of the nucleotides into the amino acid sequence
def translate_to_aa_seq(query, frame_count):
    query = query.upper()
    translate_table = {
        'ATA': 'I', 'ATC': 'I', 'ATT': 'I', 'ATG': 'M',
        'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACT': 'T',
        'AAC': 'N', 'AAT': 'N', 'AAA': 'K', 'AAG': 'K',
        'AGC': 'S', 'AGT': 'S', 'AGA': 'R', 'AGG': 'R',                
        'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L',
        'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCT': 'P',
        'CAC': 'H', 'CAT': 'H', 'CAA': 'Q', 'CAG': 'Q',
        'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R',
        'GTA': 'V', 'GTC': 'V', 'GTG': 'V', 'GTT': 'V',
        'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A',
        'GAC': 'D', 'GAT': 'D', 'GAA': 'E', 'GAG': 'E',
        'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGT': 'G',
        'TCA': 'S', 'TCC': 'S', 'TCG': 'S', 'TCT': 'S',
        'TTC': 'F', 'TTT': 'F', 'TTA': 'L', 'TTG': 'L',
        'TAC': 'Y', 'TAT': 'Y',
        'TGC': 'C', 'TGT': 'C', 'TGG': 'W'
    }
    stop_codons = ['TAA', 'TAG', 'TGA']

    translated = ""
    for i in range(frame_count, len(query) - (len(query) - frame_count) % 3, 3):
        if query[i:i + 3] in stop_codons:
            translated = translated + '-'
        else:
            translated = translated + translate_table[query[i:i + 3]]

    return translated


# highlights the longest ORF by adding a span tag around it
def highlight_substring(str, frame_coords, longest_orf):
    if isinstance(frame_coords, list):
        index_offset = 0
        for c in frame_coords:
            aa_start_index = int((c['start'] - c['start'] % 3)/3) + index_offset
            aa_stop_index = int((c['stop'] - c['stop'] % 3)/3) + index_offset
            if longest_orf[0] == c['start'] and longest_orf[1] == c['stop']:
                substr = "<span class='longest'>" + str[aa_start_index:aa_stop_index] + "</span>"
                index_offset = index_offset + len("<span class='longest'></span>")
            else:
                substr = "<span>" + str[aa_start_index:aa_stop_index] + "</span>"
                index_offset = index_offset + len("<span></span>")
            str = str[:aa_start_index] + substr + str[aa_stop_index:]
    return str


if __name__ == '__main__':
    main()
