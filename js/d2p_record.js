$(document).ready( function() {
    addBlastLink();
});

function addBlastLink() {
    $(".blast").each(function(x) {
    $(this).html("<p>Please refer to the BLAST search by clicking " +
        "<a target='_blank' href='https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastp&PAGE_TYPE=BlastSearch&LINK_LOC=blasthome&QUERY=" + $("ul.frames span.longest")[x].innerText + "'>this link</a></p><ul></ul>");
    });
}
