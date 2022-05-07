$(document).ready( function() {
    runBlast();
});

// this function executes BLAST request via an AJAX call
function runBlast() {
    $("ul.frames span.longest").each(function(x) {
       $.post({
            url: './blast_search.cgi',
            dataType: 'json',
            data: {
                "orf": $("ul.frames span.longest")[x].innerText
            },
            success: function(data) {
                $("#blast_results_" + (x + 1)).removeClass("waiting");
                processJSON(data, x);
            },
            error: function(errorThrown){
                if(errorThrown.status == 504) {
                    $("#blast_results_" + (x + 1))
                        .text("Could not retrieve results because of the server timeout")
                        .addClass("error");
                }
                $("#blast_results_" + (x + 1)).removeClass("waiting");
                console.log("Failed to perform blast search: " + errorThrown);
            }
        });
    });
}

function processJSON(data, x) {
    $("#blast_results_" + x).html("<ul></ul>");

    for(let i=0; i<data.length; i++) {
        $("#blast_results_" + x + " ul").html("<li>" + data[0].accession + " | " + data[0].definition
            + " Align Length: " + data[0].align_length + " Evalue: " + data[0].evalue + "</li>");
    }
}
