"""
admin.py-ben hasznalt action-ok
https://dev.to/ahmed__elboshi/introduction-to-custom-actions-and-bulk-actions-in-django-4bgd
admin/actions.py alapjan
"""
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from django.contrib import messages
from django.db import IntegrityError
from django.utils.safestring import mark_safe
from json import dumps
import csv

from erhtv.models.models import ForestReserve, Taxon, ErtTxn, Project, PrMvpCsopKat, PrMvpCsop, PrMvpCsopElem, SamplingPoint, Jegyzokonyv
from erhtv.forms.forms import CSVImportForm

import logging
logger = logging.getLogger(__name__)


def ertx_copy(modeladmin, request, queryset):
    """
        ez az action lehetove teszi, hogy a kivalasztott taxonokat uj ER-hez rendeljuk
        koztes oldalon kell kivalasztani az ER-t
        ErtTxnAdmin hasznalja
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    # logger.warning(app_label)
    # logger.warning(queryset)
    # logger.warning(len(queryset))
    
    # ha megjott a kivalasztott rezervatum
    if request.POST.get('post'):
        copy_selected_txns_2er(request, queryset)
        # Return None to display the change list page again.
        return None
    
    # ez fut le eloszor, elmegy az admin/erhtv/rezerv_select.html oldalra es bekeri az ER-t
    ert_queryset = ForestReserve.objects.exclude(ert_nev__contains='TESZT').order_by('ert_nev').values('ert_id', 'ert_nev')
    ert_values = [(ert['ert_id'], ert['ert_nev']) for ert in ert_queryset]
    context = {
        **modeladmin.admin_site.each_context(request),
        "ert_values": ert_values,
        "queryset": queryset,
        "object_count": len(queryset),
        "opts": opts,
        "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
        "media": modeladmin.media,
    }

    request.current_app = modeladmin.admin_site.name

    # Display the confirmation page
    return TemplateResponse(
        request,
        "admin/erhtv/rezerv_select.html",
        context,
    )

def copy_selected_txns_2er(request, queryset):
    """
        ertx_copy tenyleges muveletet vegzi
    """
    masolando_objects = queryset.values()
    ert_id = request.POST.get('ert_id')
    ert_nev = ForestReserve.objects.get(ert_id=ert_id).ert_nev
    objs = []
    for masolando in masolando_objects:
        objs.append(ErtTxn(ert_id=ert_id, txn_id=masolando['txn_id'], gyakori_faasz=masolando['gyakori_faasz'], gyakori_ujcs=masolando['gyakori_ujcs'], gyakori_anov=masolando['gyakori_anov']))
    #logger.warning(objs)
    success_list = []
    error_list = []
    for obj in objs:
        try:
            obj.save()
            success_list.append(obj.txn_id)
        except IntegrityError:
            error_list.append(obj.txn_id)
    messages.info(request, 'Taxonok másolása ebbe az erdőrezervátumba: %s' % ert_nev)
    if len(success_list) > 0:
        faj_queryset = Taxon.objects.filter(txn_id__in=success_list).values('latinnev')
        fajok = ', '.join([faj['latinnev'] for faj in faj_queryset])
        messages.success(request, 'A következő taxonok létrejöttek: %s' % fajok)
    if len(error_list) > 0:
        faj_queryset = Taxon.objects.filter(txn_id__in=error_list).values('latinnev')
        fajok = ', '.join([faj['latinnev'] for faj in faj_queryset])
        messages.warning(request, 'A következő taxonok létrehozása sikertelen, mert már léteznek: %s' % fajok)

ertx_copy.short_description="Kiválasztott taxonok másolása új ER-be"





def prmvp_create(modeladmin, request, queryset):
    """
        ez az action lehetove teszi, hogy a kivalasztott mintaveteli pontokat MVP-PRJ projekthez és csoporthoz rendeljuk
        a masik action jegyzokonyvet hoz letre a prj-mvp parokhoz
        SamplingPointAdmin hasznalja
    """

    opts = modeladmin.model._meta
    
    # ha megjott a kivalasztott csoport
    if request.POST.get('post'):
        create_selected_mvps(request, queryset)
        # Return None to display the change list page again.
        return None
    
    # ez fut le eloszor, elmegy az admin/erhtv/kat_csoport_select.html oldalra es bekeri a prj-et, csoportot
    mvp_objects = queryset.values()
    ert_id = mvp_objects[0]['ert_id']

    # ha nem azonosak a rezervatumok, nem megy tovabb
    for mvp_object in mvp_objects:
        if mvp_object['ert_id'] != ert_id:
            messages.error(request, 'A kiválasztott mintavételi pontok nem azonos rezervátumhoz tartoznak!' )
            return None
    prj_queryset = Project.objects.filter(prj_ert=ert_id).order_by('prj_nev').values('prj_id', 'prj_nev')
    prj_values = [(prj['prj_id'], prj['prj_nev']) for prj in prj_queryset]
    #logger.warning(prj_values)
    csopkat_queryset = PrMvpCsopKat.objects.order_by('csopprj_nev').values('csopprj_id', 'csopprj_nev')
    csop_list = []
    for csopkat in csopkat_queryset:
        csopkat_dict = {"id": csopkat['csopprj_id'], "value": csopkat['csopprj_nev']}
        csoport_queryset = PrMvpCsop.objects.filter(csopprj=csopkat['csopprj_id']).order_by('csoport_nev').values('csoport_id', 'csoport_nev')
        #csopkat_dict["childOptions"] = [{"id": csoport['csoport_id'], "value": csoport['csoport_nev']} for csoport in csoport_queryset]
        # a kulcs: a select tag id-ja
        csopkat_dict["csoport_id"] = [{"id": csoport['csoport_id'], "value": csoport['csoport_nev']} for csoport in csoport_queryset]
        csop_list.append(csopkat_dict)
    csopkatJSON = dumps(csop_list) 

    context = {
        **modeladmin.admin_site.each_context(request),
        "prj_values": prj_values,
        "csopkatJSON": csopkatJSON,
        "queryset": queryset,
        "object_count": len(queryset),
        "opts": opts,
        "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
        "media": modeladmin.media,
    }

    request.current_app = modeladmin.admin_site.name

    # Display the confirmation page
    return TemplateResponse(
        request,
        "admin/erhtv/kat_csoport_prj_select.html",
        context,
    )

def create_selected_mvps(request, queryset):
    """
        prmvp_create tenyleges muveletet vegzi
    """
    mvp_objects = queryset.values()
    prj_id = request.POST.get('prj_id')
    prj_nev = Project.objects.get(prj_id=prj_id).prj_rnev
    csoport_id = request.POST.get('csoport_id')
    csoport_nev = PrMvpCsop.objects.get(csoport_id=csoport_id).csoport_rnev
    objs = []
    for mvp_object in mvp_objects:
        objs.append(PrMvpCsopElem(prj_id=prj_id, mvp_id=mvp_object['mvp_id'], csoport_id=csoport_id))       
    (success_list, error_list) = save_objs(objs)
    messages.info(request, 'Mintavételi pontok másolása, projekt: %s, csoport: %s' % (prj_nev, csoport_nev))
    check_in_list(request, success_list, 'A következő mintavételi pontok hozzárendelése sikerült: ', True)
    check_in_list(request, error_list, 'A következő mintavételi pontok hozzárendelése sikertelen, mert már léteznek a kiválasztott kombinációk: ', False)

def save_objs(objs):
    """
        elvegzi a create_selected_mvps, create_jvks-ben a mentest, visszaadja a success- és error-listat
    """
    success_list = []
    error_list = []
    for obj in objs:
        try:
            obj.save()
            success_list.append(obj.mvp_id)
        except IntegrityError:
            error_list.append(obj.mvp_id)
    return success_list, error_list

def check_in_list(request, check_list, msg, success=True):
    """
        a success- és error-lista alapjan kiirja az uzenetet
    """    
    if len(check_list) > 0:
        mvp_queryset = SamplingPoint.objects.filter(mvp_id__in=check_list).values('mvp_azo')
        mvps = ', '.join([mvp['mvp_azo'] for mvp in mvp_queryset])
        if success:
            messages.success(request, msg+'%s' % mvps)
        else:
            messages.warning(request, msg+'%s' % mvps)

prmvp_create.short_description="Kiválasztott MVP-ok PRJ-MVP csoporthoz rendelése" 


       

#@admin.action(description='Kiválasztott MVP-okhoz tartozó jegyzőkönyvek létrehozása')
def jvk_create(modeladmin, request, queryset):
    """
        ez az action jegyzokonyvet hoz letre a prj-mvp parokhoz
        SamplingPointAdmin hasznalja
    """
    opts = modeladmin.model._meta
    
    # ha megjott a kivalasztott projekt
    if request.POST.get('post'):
        create_jvks(request, queryset)
        return None
    
    # ez fut le eloszor, elmegy az admin/erhtv/prj_select.html oldalra es bekeri a prj-et, csoportot
    mvp_objects = queryset.values()
    ert_id = mvp_objects[0]['ert_id']

    # ha nem azonosak a rezervatumok, nem megy tovabb
    for mvp_object in mvp_objects:
        if mvp_object['ert_id'] != ert_id:
            messages.error(request, 'A kiválasztott mintavételi pontok nem azonos rezervátumhoz tartoznak!' )
            return None
    prj_queryset = Project.objects.filter(prj_ert=ert_id).order_by('prj_nev').values('prj_id', 'prj_nev')
    prj_values = [(prj['prj_id'], prj['prj_nev']) for prj in prj_queryset]
    #logger.warning(prj_values)
    context = {
        **modeladmin.admin_site.each_context(request),
        "prj_values": prj_values,
        "queryset": queryset,
        "object_count": len(queryset),
        "opts": opts,
        "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
        "media": modeladmin.media,
    }

    request.current_app = modeladmin.admin_site.name

    # Display the confirmation page
    return TemplateResponse(
        request,
        "admin/erhtv/prj_select.html",
        context,
    )

def create_jvks(request, queryset):
    mvp_objects = queryset.values()
    prj_id = request.POST.get('prj_id')
    prj = Project.objects.get(prj_id=prj_id)
    objs = []
    for mvp_object in mvp_objects:
        objs.append(Jegyzokonyv(prj_id=prj_id, mvp_id=mvp_object['mvp_id'], faa_modszertan=prj.prj_tmd_faa, fae_modszertan=prj.prj_tmd_fae, fhf_modszertan=prj.prj_tmd_fhf, ujcs_modszertan=prj.prj_tmd_ujcs, anov_modszertan=prj.prj_tmd_anov, term_modszertan=prj.prj_tmd_term, foto_modszertan=prj.prj_tmd_foto, megj_modszertan=prj.prj_tmd_megj, tip_modszertani=prj.prj_tmd_tipi, mvpk_modszertan=prj.prj_tmd_mvpk))
    (success_list, error_list) = save_objs(objs)
    messages.info(request, 'Jegyzőkönyvek létrehozása mintavételi pontokhoz, projekt: %s' % (prj.prj_rnev,))
    check_in_list(request, success_list, 'A következő mintavételi pontokhoz sikerült létrehozni jegyzőkönyvet: ', True)
    check_in_list(request, error_list, 'A következő mintavételi pontokhoz nem sikerült létrehozni jegyzőkönyvet, mert már léteznek a kiválasztott kombinációk: ', False)

jvk_create.short_description="Kiválasztott MVP-okhoz tartozó jegyzőkönyvek létrehozása"




def mvp_create_from_csv(modeladmin, request, queryset):
    """
        ez az action lehetove teszi, h csv-bol importalni lehessen mintaveteli pontokat
        az eredeti valtozat kulon IMPORT gombot hasznalt es nem action volt:
            https://stackoverflow.com/questions/67313273/how-to-add-custom-view-page-to-django-admin#67319243
            https://studygyaan.com/django/import-data-from-csv-sheets-into-databases-using-django
        SamplingPointAdmin hasznalja
    """
    # ha submit
    if request.POST.get('post'):
        import_csv(request)
        # Return to display the change list page again.
        return None

    opts = modeladmin.model._meta
    form = CSVImportForm(request.POST, request.FILES)

    context = {
        **modeladmin.admin_site.each_context(request),
        "opts": opts,
        "media": modeladmin.media,
        "form": form,
        # "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
    }

    # Display the confirmation page
    return TemplateResponse(
        request,
        "admin/erhtv/mvp_import.html",
        context,
    )

def import_csv(request):
    #logger.warning('row')
    try:
        csv_file = request.FILES['csv_file'].read().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(csv_file, delimiter='\t')

        success_list = []
        errors = {'azo': {'error_list':[], 'msg':'Az mvp_azo mező kötelező! '},
                  'eov_y': {'error_list':[], 'msg':'<br/> - mvp_eov_y <= 400000: '},
                  'eov_x': {'error_list':[], 'msg':'<br/> - mvp_eov_x >= 400000: '},
                  'wgs84': {'error_list':[], 'msg':'<br/> - mvp_wgs84_fi < mvp_wgs84_lambda: '},
                  'hosszu': {'error_list':[], 'msg':'<br/> - az mvp_azo, mvp_mtvz vagy a megjegyzes mező hosszabb 25 karakternél: '},
                  'ert': {'error_list':[], 'msg':'<br/> - az erdőterület kódja (ert_id) még nincs beállítva (Először az ER rekordot kell létrehozni!) : '},
                  'hiany': {'error_list':[], 'msg':'<br/> - a kötelező mezők (ert_id, mvp_azo, mvp_eov_y, mvp_eov_x, mvp_wgs84_fi, mvp_wgs84_lambda) valamelyike hiányzik: '},
                  'other':{'error_list':[], 'msg':'-s ER-hez ezek már léteznek: ', 'ert': '<br/> - a &lt;'}}

        for row in csv_reader:
            #logger.warning(row)
            if check_csv_row(row):
                for err in check_csv_row(row):
                    if err == 'azo':
                        messages.warning(request, errors[err]['msg'])
                        return
                    try:
                        if row['mvp_azo'] not in errors[err]['error_list']:
                            errors[err]['error_list'].append(row['mvp_azo'])
                    except KeyError:
                        messages.warning(request, errors['azo']['msg'])
                        return
            else:
                new_mvp = {fieldname:value for fieldname, value in row.items()}
                try:
                    SamplingPoint.objects.create(
                        **new_mvp
                    )
                    success_list.append(row['mvp_azo'])
                except IntegrityError:
                    errors['other']['error_list'].append(row['mvp_azo'])
                    errors['other']['ert'] += row['ert_id'] + '&gt;'
                    errors['other']['msg'] = errors['other']['ert'] + errors['other']['msg']
                except TypeError:
                    messages.warning(request, 'A mvp-ok importálása sikertelen, mert a fejléc vagy a fájlformátum hibás')
                    break
        
        if len(success_list) > 0:
            mvps = ', '.join(success_list)
            messages.success(request, 'A következő mvp-k létrejöttek: %s' % mvps)
        for v in errors.values():
            if len(v['error_list']) > 0:
                mvps = ', '.join(v['error_list'])
                try:
                    msg += v['msg'] + mvps
                except:
                    msg = v['msg'] + mvps
        try:
            messages.warning(request, mark_safe('A következő mvp-ok létrehozása sikertelen, mert' + msg))
        except:
            pass
    except UnicodeDecodeError:
        messages.warning(request, 'A mvp-ok importálása sikertelen, mert a fájl nem utf-8 kódolású')

def check_csv_row(row):
    errors = []
    try:
        if len(row['mvp_azo']) > 25:
           errors.append('hosszu')
        if len(row['mvp_azo']) == 0:
           errors.append('azo')
    except KeyError:
        errors.append('azo')
    try:
        if not ForestReserve.objects.filter(pk=row['ert_id']).exists():
            errors.append('ert')
    except (KeyError, ValueError):
        errors.append('hiany')
    try:
        if float(row['mvp_eov_y']) <= 400000:
            errors.append('eov_y')
    except (KeyError, ValueError):
        errors.append('hiany')
    try:
        if float(row['mvp_eov_x']) >= 400000:
           errors.append('eov_x')
    except (KeyError, ValueError):
        errors.append('hiany')
    try:
        if float(row['mvp_wgs84_fi']) <= float(row['mvp_wgs84_lambda']):
            errors.append('wgs84')
    except (KeyError, ValueError):
        errors.append('hiany')
    try:
        if len(row['megjegyzes']) > 25:
           errors.append('hosszu')
    except (KeyError, ValueError):
        pass
    try:
        if len(row['mvp_mtvz']) > 25:
           errors.append('hosszu')
    except (KeyError, ValueError):
        pass

    if len(errors) > 0:
        return errors



mvp_create_from_csv.short_description="Mintavételi pontok importja fájlból"
