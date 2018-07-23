/**
 * disable the ontology
 */
disableOntology = function(){
    var objectID = $(this).attr("objectid");
    disable_ontology(objectID);
}

/**
 * AJAX call, disable the ontology
 * @param objectID id of the object
 */
disable_ontology = function(objectID){
    $.ajax({
        url : disableOntologyUrl,
        type : "POST",
        data: {
            id: objectID
        },
        success: function(data){
            location.reload();
        }
    });
}

$(document).ready(function() {
    $('.disable').on('click', disableOntology);
});