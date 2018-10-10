/**
* Js file dedicated to display and load tree and data
*/
var filesNames = [];
var text = "";
var current_node;
var xml_doc_id;

$('#explorer-panel-transparent-bgd').css({
                  'position':'fixed',
                  'top':'0px',
                  'left':'0px',
                  'width':'100%',
                  'height':'100%',
                  'display':'block',
                  'background-color':'#000',
                  'z-index':'2147483645',
                  'opacity': '0.8',
                  'filter':'alpha(opacity=80)',
                  'display':'none'
            });

$('#explore-panel-loading').css({
                  'position':'fixed',
                  'top':'50%',
                  'left':'45%',
                  'display':'block',
                  'background-color':'#000',
                  'color':'#337ab7',
                  'z-index':'2147483647',
                  'display':'none',
                  'border-style':'solid',
                  'border-color':'#337ab7'
            });

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
downloadOptions_file = function(){
  $("#select-download-options-modal").modal("show");
}

/**
* Download the displaying data into an XML document
*/
download_xml_tree = function(){
  //create the file to write
  var link = document.createElement('a');
  // set the file with the displaying data
  link.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  // download the file
  link.setAttribute('download', filename);
  link.click();
}

/**
* Download the displaying data into an XML document
*/
download_source_file = function(){
  showLoadingSpinner();
  filename = filesNames[0];
  $.get({
      url: "download_source_file",
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
        console.error("An error occurred while downloading the xml document");
      }
    })
}

/**
* Download the displayed data into an XML document
*/
download_displayed_data = function(event){
  showLoadingSpinner();
  filename = filesNames[1];
  $.get({
      url: "download_displayed_data",
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
       console.error("An error occurred while downloading the displayed data");
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
    // show the data
    $("#explore-view").html(data);
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
