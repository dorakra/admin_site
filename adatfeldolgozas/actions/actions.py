"""
admin.py-ben hasznalt action-ok
https://dev.to/ahmed__elboshi/introduction-to-custom-actions-and-bulk-actions-in-django-4bgd
admin/actions.py alapjan
"""
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from django.contrib import messages


import logging
logger = logging.getLogger(__name__)

#@admin.action(description="Kiválasztott adatlapok átállítása 'KÉSZ (1)'-re")
def update_keszultseg(modeladmin, request, queryset):
    """
        ez az action lehetove teszi, hogy a kivalasztott jegyzokonyvek keszultseget 1-re valtoztassuk
        koztes megerosito oldalt hasznal
        JegyzokonyvUJCSAdmin es JegyzokonyvANOVAdmin hasznalja
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    adatlap_nev, update_field, adatlap_objects = modeladmin.kesz_update_settings

    jkv_adat_ids = adatlap_objects.distinct().values_list('jkv_adat_id', flat=True)
    # logger.warning(len(jkv_adat_ids))
    queryset = queryset.order_by('jkv_adat_id')
    
    # ha megjott a megerosites
    if request.POST.get('post'):
        nemsiker1 = ', '.join([str(x.jkv_adat_id) for x in queryset.exclude(pk__in=jkv_adat_ids)])
        nemsiker2 = ', '.join([str(x) for x in queryset.filter(**{update_field:1}).values_list('jkv_adat_id', flat=True)])
        to_update = queryset.filter(pk__in=jkv_adat_ids).exclude(**{update_field:1})
        if len(to_update) > 0:
            siker = ', '.join([str(x.jkv_adat_id) for x in to_update])
            to_update.update(**{update_field:1})
            messages.success(request, 'A következő %s adatlapok frissültek: %s' % (adatlap_nev, siker))
        if len(nemsiker1) > 0:
            messages.warning(request, 'A következő %s adatlapok nem frissültek, mert nem tartozik hozzájuk adatrekord: %s' % (adatlap_nev, nemsiker1))
        if len(nemsiker2) > 0:
            messages.warning(request, "A következő %s adatlapok nem frissültek, mert már 'KÉSZ (1)'-en álltak: %s" % (adatlap_nev, nemsiker2))
        return None

    # ez fut le eloszor, elmegy az admin/adatfeldolgozas/update_selected_confirmation.html oldalra megerositesert
    context = {
        **modeladmin.admin_site.each_context(request),
        "updatable_objects": queryset.values_list('jkv_adat_id'),
        "queryset": queryset,
        "object_count": len(queryset),
        "opts": opts,
        "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
        "media": modeladmin.media,
        "adatlap_nev": adatlap_nev,
    }
    request.current_app = modeladmin.admin_site.name

    # Display the confirmation page
    return TemplateResponse(
        request,
        "admin/adatfeldolgozas/update_selected_confirmation.html",
        context,
    )

update_keszultseg.short_description="Kiválasztott adatlapok átállítása 'KÉSZ (1)'-re"
