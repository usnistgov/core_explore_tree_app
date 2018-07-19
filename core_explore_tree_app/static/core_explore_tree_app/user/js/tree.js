/**
* js file dedicated to the tree
*/

var $tree = null;

// Hide initially every nodes of the exploration tree
function hideNodes(){
    var $treeElement = $('#tree');
    var $treeElement1 = ($treeElement).children()
    var $a = $('#tree').find('li');

    for (i = 0; i < $a.length; i++) {
      var $myQuery = new jQuery.fn.init($a[i], "i.fa.fa-chevron-down" );

      if(isFolder($myQuery)) {
        var $icon = $myQuery.find("i.fa:first");
        var $subtree = $myQuery.find('ul:first');

        $icon.removeClass();
        $icon.addClass("fa fa-chevron-right");
        $subtree.hide();
        }
      }
};

var isFolder = function($treeElement) {
    return $treeElement.find('ul').length !== 0;
};

var operateTree = function($treeElement) {
    var $icon = $treeElement.find("i.fa:first");
    var $subtree = $treeElement.find('ul:first');
    $icon.removeClass();

    if($subtree.is(':hidden')) {
        $icon.addClass("fa fa-chevron-down");
        $subtree.show();
    } else {
        $icon.addClass("fa fa-chevron-right");
        $subtree.hide();
    }
};


$(window).on("scroll", function() {

});

$(document).ready(function() {
    $tree = $('#tree');
    hideNodes();
    $tree.on('click', 'li>span>i.fa', function(event) {
        event.preventDefault();
        event.stopPropagation();

        var $treeElement = $(this).parents("li:first");

        if(isFolder($treeElement)) {
            operateTree($treeElement);
        } else {

        }
    });
});



