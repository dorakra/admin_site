/*global SelectBox, interpolate*/
// Handles related-objects functionality: lookup link for raw_id_fields
// and Add Another links.

// 2024-10-09 megjegyzesek
// admin/js/admin/RelatedObjectLookups.js alapjan
// csak a szukseges fv-eket tartottam meg
// changelist_inline eseten, vagyis ANOV, UJCS stb adatlap eseten
// azaz ahol inline formset helyett beagyazott lista van, ami popupkent nyilik
// uj elem hozzaadasakor az eredeti verzioban nem csukodik le a popup window mentes utan, mert nincs SelectBox
// ezert meg kellett valtoztatni a dismissAddRelatedObjectPopup fv-t -> dismissAddRelatedObjectPopupInline
// ahhoz, h ez ervenyesuljon, szukseg volt az static/project_creation/admin/js/popup_response.js megvaltoztatasara
// tovabbi valtoztatas: uj: function updateChangeList() -> mentes utani oldalfrissites
// updateChangeList is bekerult a popup_response.js-be minden action-hoz
// a js-eket a templates/admin/adatfeldolgozas/change_form_jegyzokonyv.html-be
// es a templates/admin/popup_response.html-be kellett berakni

'use strict';
{
    const $ = django.jQuery;
    let popupIndex = 0;
    const relatedWindows = [];

    //function setPopupIndex() {
        //if(document.getElementsByName("_popup").length > 0) {
            //const index = window.name.lastIndexOf("__") + 2;
            //popupIndex = parseInt(window.name.substring(index));   
        //} else {
            //popupIndex = 0;
        //}
    //}

    function addPopupIndex(name) {
        return name + "__" + (popupIndex + 1);
    }

    function removePopupIndex(name) {
        return name.replace(new RegExp("__" + (popupIndex + 1) + "$"), '');
    }

    function showAdminPopup(triggeringLink, name_regexp, add_popup) {
        const name = addPopupIndex(triggeringLink.id.replace(name_regexp, ''));
        // console.log(name);
        const href = new URL(triggeringLink.href);
        if (add_popup) {
            href.searchParams.set('_popup', 1);
        }
        const win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
        relatedWindows.push(win);
        win.focus();
        console.log('uj showAdminPopup');
        return false;
    }

    function showRelatedObjectPopup(triggeringLink) {
        return showAdminPopup(triggeringLink, /^(change|add|delete)_/, false);
    }

    function dismissAddRelatedObjectPopupInline(win, newId, newRepr) {
        const name = removePopupIndex(win.name);
        const elem = document.getElementById(name);
        if (elem) {
            const elemName = elem.nodeName.toUpperCase();
            if (elemName === 'SELECT') {
                elem.options[elem.options.length] = new Option(newRepr, newId, true, true);
                updateRelatedSelectsOptions(elem, win, null, newRepr, newId);
            } else if (elemName === 'INPUT') {
                if (elem.classList.contains('vManyToManyRawIdAdminField') && elem.value) {
                    elem.value += ',' + newId;
                } else {
                    elem.value = newId;
                }
            }
            // Trigger a change event to update related links if required.
            $(elem).trigger('change');
        } else {
            const toId = name + "_to";
            const o = new Option(newRepr, newId);
            // ellenorzi, h van-e SelectBox (ha nem mezohoz kapcsolt a window, akkor nincs - pl. uj adatrekord)
            if (typeof SelectBox != "undefined") {
                SelectBox.add_to_cache(toId, o);
                SelectBox.redisplay(toId);
            }
        }
        // console.log('uj');
        const index = relatedWindows.indexOf(win);
        if (index > -1) {
            relatedWindows.splice(index, 1);
        }
        win.close();
    }

    function updateChangeList() { 
        // mentes utan ujratolti a #changelist tartalmat -> megjelennek a frissitesek
        //setTimeout(function(){
            let href = $(location).attr("href");
            $.get(href, function(data, status){
                //console.log("Status: " + status);
                $("#changelist").html($(data).find("#changelist").html());
            });
            //location.reload(); //ez ujratolti az oldalt
        //}, 500);
    }

    window.dismissAddRelatedObjectPopupInline = dismissAddRelatedObjectPopupInline;
    window.updateChangeList = updateChangeList;


    $(document).ready(function() {
        //setPopupIndex();
        $('body').on('click', '.related-widget-wrapper-link[data-popup="yes"]', function(e) {
            e.preventDefault();
            if (this.href) {
                const event = $.Event('django:show-related', {href: this.href});
                $(this).trigger(event);
                if (!event.isDefaultPrevented()) {
                    showRelatedObjectPopup(this);
                }
            }
        });
    });
}
