$(document).ready( function() {
    runBlast();

    $(".save_results").click(function (e) {
        e.preventDefault();
        $(".save_results").after("<div class='lds-ellipsis'><div></div><div></div><div></div><div></div></div>");
        $(".save_results").remove();
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

        $.post({
                url: './save_results.cgi',
                dataType: 'json',
                data: $.param(dat),
                success: function(data) {
                    $(".lds-ellipsis").after("<div class='result'>Please save the record ID that will allow you to retrieve the saved data from the database: <strong>" + data + "</strong></div>");
                    $(".lds-ellipsis").remove();
                },
                error: function(errorThrown){
                    $(".lds-ellipsis").after("<div class='result_error'>Oops, something went wrong</div>");
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
