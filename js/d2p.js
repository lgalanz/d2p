$(document).ready( function() {
    runBlast();

    $(".save_results").click(function (e) {
        e.preventDefault();

        // replace the sutton with a loader
        $(".save_results").after("<div class='lds-ellipsis'><div></div><div></div><div></div><div></div></div>");
        $(".save_results").remove();

        // consolidate the data to be saved
        var dat = {
            "nt_seq": $(".fasta_query p:nth-child(2)").get(0).innerText
        };
        for (let i = 1; i <= 3; i++) {
            dat["frame" + i]= {
                "aa_seq": $("#frame_" + i + " p.frame_aa_seq").html(),
                "prot_info": {
                    "molecular_weight": $(".frame_" + i + " .molecular_weight").get(0).innerText,
                    "aromaticity": $(".frame_" + i + " .aromaticity").get(0).innerText,
                    "instability_index": $(".frame_" + i + " .instability_index").get(0).innerText,
                    "isoelectric_point": $(".frame_" + i + " .isoelectric_point").get(0).innerText ,
                    "secondary_structure_fraction": {
                        "helix": $(".frame_" + i + " .secondary_structure_fraction .helix").get(0).innerText,
                        "turn": $(".frame_" + i + " .secondary_structure_fraction .turn").get(0).innerText,
                        "sheet": $(".frame_" + i + " .secondary_structure_fraction .sheet").get(0).innerText,
                    }
                }
            }
        }

        // send an AJAX POST request
        $.post({
                url: './save_results.cgi',
                dataType: 'json',
                data: $.param(dat),
                success: function(data) {
                    // Inform the user about success and provide the record ID
                    $(".lds-ellipsis").after("<div class='result'>Please save the record ID that will allow you to retrieve the saved data from the database: <strong>" + data + "</strong></div>");
                    // remove the loader
                    $(".lds-ellipsis").remove();
                },
                error: function(errorThrown){
                    // Inform the user about the error
                    $(".lds-ellipsis").after("<div class='result_error'>Oops, something went wrong</div>");
                    // remove the loader
                    $(".lds-ellipsis").remove();
                    console.log("Failed to perform blast search: " + errorThrown);
                }
            });

    });
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
                // remove the animation (blinking) upon receiving results
                $("#blast_results_" + (x + 1)).removeClass("waiting");
                // parse the returned values
                processJSON(data, x);
            },
            error: function(errorThrown){
                if(errorThrown.status == 504) {
                    $("#blast_results_" + (x + 1))
                        .addClass("error")
                        .append("<p>Could not retrieve results because of the server timeout</p>" +
                        "<p>Alternatively, you can trigger the BLAST search by clicking " +
                        "<a target='_blank' href='https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastp&PAGE_TYPE=BlastSearch&LINK_LOC=blasthome&QUERY=" + $("ul.frames span.longest")[x].innerText + "'>this link</a></p>");
                }
                $("#blast_results_" + (x + 1)).removeClass("waiting");
                console.log("Failed to perform blast search: " + errorThrown);
            }
        });
    });
}

function processJSON(data, x) {
    $("#blast_results_" + (x + 1)).html("<p><strong>This is mocked data parsed from the XML previously generated by Bio.Blast.NCBIWWW.qblast. Your actual BLAST results could look similar but were not possible to retrieve due to the server timeout.</strong></p>" +
    "<p>Alternatively, you can trigger the BLAST search by clicking " +
    "<a target='_blank' href='https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastp&PAGE_TYPE=BlastSearch&LINK_LOC=blasthome&QUERY=" + $("ul.frames span.longest")[x].innerText + "'>this link</a></p><ul></ul>");

    for(let i=0; i<data.length; i++) {
        $("#blast_results_" + (x + 1) + " ul").append("<li><strong>" + data[i].accession + "</strong> | " + data[i].definition
            + " <strong>Align Length:</strong> " + data[i].align_length + " <strong>Evalue:</strong> " + data[i].evalue + "</li>");
    }
}
