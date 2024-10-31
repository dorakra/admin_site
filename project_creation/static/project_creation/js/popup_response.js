/*global opener */
// changelist_inline adatrekordokhoz, ld. js/admin/InlineRelatedObjectLooups.js
'use strict';
{
    const initData = JSON.parse(document.getElementById('django-admin-popup-response-constants').dataset.popupResponse);
    switch(initData.action) {
    case 'change':
        opener.dismissChangeRelatedObjectPopup(window, initData.value, initData.obj, initData.new_value);
        opener.updateChangeList();
        break;
    case 'delete':
        opener.dismissDeleteRelatedObjectPopup(window, initData.value);
        opener.updateChangeList();
        break;
    default:
        opener.dismissAddRelatedObjectPopupInline(window, initData.value, initData.obj);
        opener.updateChangeList();
        break;
    }
}
