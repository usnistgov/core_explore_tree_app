/**
* Js file dedicated to display and load tree and data
*/
var filesNames = [];
var text = "";
var current_node;
var xml_doc_id;


var removeHighlight = function() {
    var highlightClass = "highlight";
    $.each($("." + highlightClass), function(index, value) {
        $(value).removeClass(highlightClass);
    });
}

var showHighlight = function() {
    var highlightClass = "highlight";
    $("." + xml_doc_id).closest("span").addClass(highlightClass);
}


/**
* Shows a dialog to choose dialog options
*/
var downloadOptions_file = function(){
  $("banner_errors").hide();
  $("#select-download-options-modal").modal("show");
}

/**
* Download the displaying data into an XML document
*/
var download_xml_tree = function(){
  //create the file to write
  var link = document.createElement('a');
  // set the file with the displaying data
  link.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  // download the file
  link.setAttribute('download', filename);
  link.click();
}

/**
* Download the initial source file into an XML document
*/
var download_source_file = function(){
  $("banner_errors").hide();
  showLoadingSpinner();
  filename = filesNames[0];
  $.get({
      url: download_source_file_url,
      method: "GET",
      data: {
          file_name: filename,
          doc_id: xml_doc_id
      },
      success: function(data) {
        hideLoadingSpinner();
        var link = document.createElement('a');
        var parser = new XMLSerializer().serializeToString(data.documentElement);
        link.setAttribute('href','data:text/xml;charset=utf-8,' + parser);
        link.setAttribute('download', filename);
        link.click();
        $("#select-download-options-modal").modal("hide");
      },
      error: function() {
        errors="An error occured while downloading the data";
        $("#form_download_errors").html(errors);
        $("#banner_errors").show(500);
        hideLoadingSpinner();
      }
    })
}

/**
* Download the displayed data into an XML document
*/
var download_displayed_data = function(event){
  $("banner_errors").hide();
  showLoadingSpinner();
  filename = (filesNames[1]).replace(".","_");
  $.get({
      url: download_displayed_data_url,
      method: "GET",
      data: {
          file_name: filename,
          doc_id: xml_doc_id,
          current_node: current_node
      },
      success: function(data) {
        hideLoadingSpinner();
        var link = document.createElement('a');
        var parser = new XMLSerializer().serializeToString(data.documentElement);
        link.setAttribute('href','data:text/xml;charset=utf-8,' + parser);
        link.setAttribute('download', filename);
        link.click();
        $("#select-download-options-modal").modal("hide");
      },
      error: function() {
        errors="An error occured while downloading the data";
        $("#form_download_errors").html(errors);
        $("#banner_errors").show(500);
        hideLoadingSpinner();
      }
    })
}

/**
* Display a Document when we click on a leaf
*/
var displayLeafView = function(event) {
    event.preventDefault();
    removeHighlight();

    var nodeClasses = $(this).attr("class").split(" ");
    var documentId = nodeClasses[1];
    var nodeId = nodeClasses[2];
    var navigationId = $('.navigation_id').html();
    filename_displayed_data = this.childNodes[0].nodeValue;

    $(this).parents("span:first").addClass("highlight");

    xml_doc_id = documentId;
    showLoadingSpinner();

    $.ajax({
        url: load_view_url,
        method: "POST",
        data: {
            nav_id: navigationId,
            doc_id: documentId,
            node_id: nodeId,
        },
        success: function(data) {
            hideLoadingSpinner();
            showDataPanel(data);
            // set the filename in case the user wants to download it
            filename_source_file = data.substring(32,data.indexOf("<",32)); // remove the tag <h1 class="section-full-header">
            // retrieve the data in case the user wants to download the data
            filesNames = [filename_source_file,filename_displayed_data];
            text = data
            current_node = nodeId
            showHighlight(xml_doc_id);
        },
        error: function() {
            showErrorPanel();
        }
    })
};

var displayBranchView = function(event) {
    event.preventDefault();
    removeHighlight();

    var nodeClasses = $(this).attr("class").split(" ");
    var nodeId = nodeClasses[1];
    var navigationId = $.urlParam("nav_id");

    $(this).parents("span:first").addClass("highlight");

    $('#explorer-panel-transparent-bgd').show();
    $('#explore-panel-loading').show();
    $.ajax({
        url: "load_view",
        method: "POST",
        data: {
            nav_id: navigationId,
            node_id: nodeId
        },
        success: function(data) {
            showDataPanel(data);
        },
        error: function() {
            showErrorPanel();
        }
    })
};

var displayLinkView = function(event) {
    event.preventDefault();
    removeHighlight();
    var nodeClasses = $(this).attr("class").split(" ");
    var nodeId = nodeClasses[1];
    var documentId = nodeClasses[2];
    var navigationId = $('.navigation_id').html();
    xml_doc_id = documentId;
    filename_displayed_data = this.childNodes[0].nodeValue;
    showLoadingSpinner();

    $.ajax({
        url: load_view_url,
        method: "POST",
        data: {
            nav_id: navigationId,
            doc_id: documentId,
            ref_node_id: nodeId
        },
        success: function(data) {
            showDataPanel(data);
            var f = JSON.stringify(data)//String(data)
            // set the filename to the current name in case the user wants to download it
            filename_source_file = data.substring(32,data.indexOf("<",32));
            filesNames = [filename_source_file,filename_displayed_data];
            text = JSON.stringify(data)
            current_node = nodeId
            showHighlight(xml_doc_id);
        },
        error: function() {
            showErrorPanel();
        }
    })
};

var showDataPanel = function(data) {
    hideLoadingSpinner();
    // hide the error panel
    $("#explore-view-error").hide();
    // Make the http link clickable
    var http_index = data.indexOf("http");
    var sub_str= data.substr(http_index);
    var index = sub_str.indexOf("<");
    var link = data.substring(http_index,http_index+index);

    var html_link = "<a href="+"\'"+link+"\' target=\'_blank\'>"+link+"</a>";
    var final_data = data.replace(link, html_link);
    // show the data
    $("#explore-view").html(final_data);//data);
    $("#explore-view").show();
    // enable the download button
    $("#explore-view-download").prop('disabled', false);
}

var showErrorPanel = function() {
    hideLoadingSpinner();
    // disable the download button
    $("#explore-view-download").prop('disabled', true);
    $("#explore-view").hide();
    $("#explore-view-error").show();
}

var showLoadingSpinner = function() {
    $('#explorer-panel-transparent-bgd').show();
    $('#explore-panel-loading').show();
}

var hideLoadingSpinner = function() {
    $('#explorer-panel-transparent-bgd').hide();
    $('#explore-panel-loading').hide();
}

$(document).ready(function() {
    $("#explore-view-error").hide();
    $('#explorer-panel-transparent-bgd').hide();
    $('#explore-panel-loading').hide();
    $(document).on("click", ".projection", displayLeafView);
    $(document).on("click", ".branch", displayBranchView);
    $(document).on("click", ".link", displayLinkView);
});
