//https://www.w3schools.com/howto/howto_js_cascading_dropdown.asp alapjan
//console.log(optionsObject);
//console.log(parentId);
//console.log(childIds);
window.onload = function() {
    var parentSel = document.getElementById(parentId);
    //var childSel = document.getElementById(childId);
    for (var x in optionsObject) {
        parentSel.options[parentSel.options.length] = new Option(optionsObject[x]['value'], optionsObject[x]['id']);
    }
    parentSel.onchange = function() {
        for (var i in childIds) {
            //console.log(childIds[i])
            var childSel = document.getElementById(childIds[i]);
            var SelectedValue = childSel.value; //ha szerkesztjuk, es mar volt kivalasztott
            //empty Csoport- dropdowns
            childSel.length = 1;
            //display correct values
            for (var x in optionsObject) {
                if (optionsObject[x]['id'] == this.value) {
                    for (var y in optionsObject[x][childIds[i]]) {
                        a = optionsObject[x][childIds[i]][y];
                        //console.log(a);
                        childSel.options[childSel.options.length] = new Option(a['value'], a['id']);
                    }
                    break;
                }
            }
            if (SelectedValue) {
                childSel.value = SelectedValue;
            }
        }
    }
}

