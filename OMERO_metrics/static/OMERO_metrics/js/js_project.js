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


  function onclickListe(evt, listeStatus) {

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


document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('loadContentli').forEach(item => {
        item.addEventListener('click', function() {
            var oid = this.getAttribute('data-oid');
            var inst = document.querySelector('#dataTree').jstree(true); // Assuming jstree is initialized on #dataTree
            inst.deselect_all(true);
            var selectedNode = inst.locate_node("dataset-" + oid);
            inst.select_node(selectedNode);

            // Focus the node for hotkey events
            if (selectedNode) {
                document.getElementById(selectedNode.id).querySelector('.jstree-anchor').focus();
            }
        });
    });
});