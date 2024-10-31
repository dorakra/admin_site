/* FAE egyesfa adatlapok hasznalja (JegyzokonyvFAEadatAdmin) */
/* kiszuri azokat a fa-azonositokat, amiket mar egy masik elem hasznal, igy biztosan csak 1-szer hasznalunk 1 azonositot */

function waitAddRow2() {
    const el = document.querySelector('.inline-group div.add-row a');

    if (el != null) {
        $('.inline-group div.add-row a').click(function() {
            //collapseItems(); //collapsed-stacked-inlines.js-bol, mert most felulirtuk az ottani delay-t
            getSelects();
        });
        getDeleteLinks();
    } 
    else {
        setTimeout(waitAddRow2, 200); // try again in 200 milliseconds
    }
}


jQuery(function ($) {
    setFAoptions();
    getSelects();

    // getDeleteButtons(); mar mentett elemekre, nem hasznalom, mert hiaba nyomunk a torlesre, meg foglalt a fa-azonosito
    
    waitAddRow2();

});

// megkeresi az osszes fae-mezot, figyeli, ha a valtozik
function getSelects() {
    $('.field-fae select').each(function () {
        $(this).change(setFAoptions);
    });
}

// mik a kivalasztott fa-azonositok
function getSelFA() {
    var selFA = []
    $('.field-fae select').each(function () {
        var sel = (this.value);
        if (sel != '') {
            selFA.push(sel);
        }
    });
    return selFA
}

// kiszedi az opciok kozul, ami ki van valasztva, kiveve a sajatot
// visszarakja azt, ami mar nincs kivalasztva
function setFAoptions() {
    //console.log('FA');
    var selFA = getSelFA();
    $('.field-fae select').each(function (index, element) {

        var sel = ( this.value );
        //console.log(this.id);
        $('option', this).each(function (subindex, subelement) {
            //console.log(this.value);
            if($.inArray(this.value, selFA) !== -1 && this.value != sel) {
                $(this).hide();
            }
            else {
                $(this).show();
            }
        });

    });
}

// megkeresi az osszes torles-linket, figyeli
function getDeleteLinks() {
    $('.inline-deletelink').each(function () {
        $(this).click(setFAoptions);
    });
}

// megkeresi a torles-gombokat (mar mentett elemekre), nem hasznaljuk!
function getDeleteButtons() {
    $('.has_original span.delete input').each(function () {
        $(this).change(setFAoptions);
    });
}
