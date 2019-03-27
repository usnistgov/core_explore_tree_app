/**
* Js file dedicated to cache files from the tree
*/


var cache_all_tree_files = function() {
    $("#cache-all-tree-files-modal").modal("show");
    $("#banner_errors").hide();
	$("#banner_success").hide();
    $('#btn-display-data').on('click', cache_selected_files);
};

/**
 * Validate fields of the start caching
 */
var cache_selected_files = function(){
    $("#banner_errors").hide();
	$("#banner_success").hide();
    selected_option = $("#form_start_caching" ).find("input:radio[name='cache_form']:checked").val()

    if (selected_option == undefined){
		errors = "No option selected. Please check one radio button."
		showErrorPanel(errors);
	}else{
		if (selected_option == "specific node"){
			if ($( "#id_nodes" ).val() == ""){
				errors = "You selected the option to cache specific files from a node. Please select the node."
				showErrorPanel(errors);
			}else{
			     node_id = $("#id_nodes").val();
			     $("#banner_errors").hide();
			     cache_all_files_from_node(node_id);
			}
		}else {
		    if ($( "#id_navigation_root" ).val() == ""){
				errors = "You selected the option to cache all the files from the tree. Please click the button."
			    showErrorPanel(errors);
			}else{
			    root_node = selected_option
			    $("#banner_errors").hide();
			    cache_all_files_from_node(root_node);
			}

		}
	}
};

/**
 * Cache the files under the selected node
 */
var cache_all_files_from_node =function(node_id){
    showLoadingSpinner();
    $.ajax({
        url: "cache-all-files",
        method: "POST",
        data: {
            node_id: node_id,
        },
        success: function(data) {
            hideLoadingSpinner();
		    $("#form_cache_success").html(data.message);
		    $("#banner_success").show(500);
        },
        error: function(data) {
            hideLoadingSpinner();
            errors = "An error occurred when caching the files."
            showErrorPanel(errors);
        }
    })
};

/**
 * Clear the cache
 */
var clear_cache_options = function() {
    $("#clear-cache-modal").modal("show");
    $("#banner_errors").hide();
	$("#banner_success").hide();
    $('#btn-display-clear-data').on('click', clear_cache);
};

/**
 * Call ajax function that clear the cache
 */
var clear_cache = function(){
    $("#banner_errors").hide();
	$("#banner_success").hide();
    showLoadingSpinner();
    $.ajax({
        url: "clear-cache",
        method: "POST",
        data: {},
        success: function(data) {
            hideLoadingSpinner();
		    $("#clear_cache_text_success").html(data.message);
		    $("#clear_cache_banner_success").show(500);

        },
        error: function(data) {
            hideLoadingSpinner();
            errors = "An error occurred when deleting objects from the cache."
            $("#clear_cache_text_error").html(errors);
            $("#clear_cache_banner_errors").show(500);
        }
    })

}

var showErrorPanel = function(errors) {
    hideLoadingSpinner();
    $("#form_cache_errors").html(errors);
    $("#banner_errors").show(500);
}
var showLoadingSpinner = function() {
    document.getElementById("loading_background").style.visibility = "visible";
    $('#explorer-panel-transparent-bgd').show();
    $('#explore-panel-loading').show();
}

var hideLoadingSpinner = function() {
    document.getElementById("loading_background").style.visibility = "hidden";
    $('#explorer-panel-transparent-bgd').hide();
    $('#explore-panel-loading').hide();
}