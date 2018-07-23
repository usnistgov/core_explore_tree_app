/**
 * activate the ontology
 */
activateOntology = function(){
    var objectID = $(this).attr("objectid");
    activate_ontology(objectID);
}

/**
 * AJAX call, activate the ontology
 * @param objectID id of the object
 */
activate_ontology = function(objectID){
    $.ajax({
        url : activateOntologyUrl,
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
    $('.activate').on('click', activateOntology);
});