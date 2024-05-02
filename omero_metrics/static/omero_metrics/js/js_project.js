function openDataset(evt, datasetStatus) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(datasetStatus).style.display = "block";
    evt.currentTarget.className += " active";
  }

$(document).ready(function(){
    $("div#graph_line.dash-graph.loadContentli").click(function(){
        //var oid = $(this).data('oid');
        var oid = 59
        var inst = $.jstree.reference('#dataTree');
        inst.deselect_all(true);
        var selectedNode = inst.locate_node("dataset-" + oid);
        inst.select_node(selectedNode);
        
        // we also focus the node, so that hotkey events come from the node
        if (selectedNode) {
            $("#" + selectedNode.id).children('.jstree-anchor').trigger('focus');
        }
    });
});


$(document).ready(function(){
  $("div.dash-graph.loadContentli").click(function(){
      //var oid = $(this).data('oid');
      var oid = 59
      var inst = $.jstree.reference('#dataTree');
      inst.deselect_all(true);
      var selectedNode = inst.locate_node("dataset-" + oid);
      inst.select_node(selectedNode);
      
      // we also focus the node, so that hotkey events come from the node
      if (selectedNode) {
          $("#" + selectedNode.id).children('.jstree-anchor').trigger('focus');
      }
  });
});

