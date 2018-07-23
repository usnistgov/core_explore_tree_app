/**
 * restore the ontology
 */
restoreOntology = function(){
    var objectID = $(this).attr("objectid");
    restore_ontology(objectID);
}

/**
 * AJAX call, restore the ontology
 * @param objectID id of the object
 */
restore_ontology = function(objectID){
    $.ajax({
        url : restoreOntologyUrl,
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
    $('.restore').on('click', restoreOntology);
});