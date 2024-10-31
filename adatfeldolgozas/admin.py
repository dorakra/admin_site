from datetime import datetime

from django.contrib import admin
from django.urls import resolve
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_changelist_inline import (
    ChangelistInline,
    ChangelistInlineAdmin,
    ChangelistInlineModelAdmin,
)
import copy
from django.http import QueryDict
from project_creation.settings import STATIC_URL

from erhtv.filters.filters import ChoiceDropdownFilter, DropdownFilter, BooleanDropdownFilter, \
    generate_select2_filter, OverrideDropdownFilter, ERListFilter, ProjectRelatedByER, MVPRelatedByProject, \
    SorszamDropdownFilter, FelmeroDropdownFilter
from adatfeldolgozas.models.models import JegyzokonyvFAA, JegyzokonyvFAEazon, JegyzokonyvFAEadat, \
    JegyzokonyvFHF,FaaAdat, FaeAdat, FaeAzo, FhfAdat, JegyzokonyvUJCS, UcsAdat, JegyzokonyvANOV, FNovAdat
from adatfeldolgozas.forms.forms import JegyzokonyvModAdminForm, FaaAdatInlineForm, RadioSelect, \
    AnovAdatInlineForm
from erhtv.models.models import Project, Jegyzokonyv, Status, SamplingPoint, ErtTxn, Taxon, Person, \
    Permission, ForestReserve
from erhtv.admin import JegyzokonyvAltalanosAdmin
from adatfeldolgozas.actions.actions import update_keszultseg


def get_field_name(modeladmin, related_model):
    """ visszaadja annak a mezonek a nevet, ami a related_modelre mutat (pl. nov_txn) 
        related model pl: status, taxon
    """
    for f in modeladmin.model._meta.get_fields():
        try:
            if f.related_model._meta.model_name == related_model:
                return f.name
        except:
            pass

def get_txn_field(modeladmin):
    return get_field_name(modeladmin, 'taxon')

def get_sta_field(modeladmin):
    return get_field_name(modeladmin, 'status')

def get_mvp_txns(jkv_adat_id, modeladmin, obj_id = None):
    """ csak a mvp rezervatumaban elofordulo taxonokat mutassa ErtTxn alapjan
        ujcs, anov eseten mindegyiket csak egyszer lehet valasztani
    """
    mvp_id = Jegyzokonyv.objects.get(jkv_adat_id=jkv_adat_id).mvp.mvp_id
    ert_id = SamplingPoint.objects.get(mvp_id=mvp_id).ert.ert_id
    gyak_field = modeladmin.gyak_field # pl. gyakori_faasz
    txn_field = get_txn_field(modeladmin) # pl. fhf_txn
    gyak_field_gt = gyak_field + '__gt'

    # elofordulo taxonok
    erttxns = ErtTxn.objects.filter(ert_id=ert_id).filter(**{gyak_field_gt: -1}).values_list('txn_id', flat=True)

    # mar kivalasztott taxonok, kiveve a sajat taxon
    if txn_field in ['ucs_txn', 'nov_txn'] and obj_id is not None: # obj_id not None nem kell, ha changelist inline lesz
        jkvtxns = modeladmin.model.objects.filter(jkv_adat_id=jkv_adat_id).exclude(pk=obj_id).distinct().values_list(txn_field, flat=True)
    else:
        jkvtxns = []

    return Taxon.objects.filter(txn_id__in=erttxns).exclude(txn_id__in=jkvtxns).order_by('latinnev')

def get_collapsed_js():
    """ stacked-inline hasznalatakor, ha 1-nel tobb sor adhato """
    return ['https://code.jquery.com/jquery-3.7.1.min.js',
            'project_creation/js/collapsed-stacked-inlines.js']

class JKVInline(admin.StackedInline):
    """
    Általános model admin a beágyazott adatlapokhoz, ahol több elem adható
    """
    model = FaeAzo
    fk_name = "jkv_adat"
    classes = ['collapse']
    extra = 1

    # a taxonokra vonatkozo elofordulasi mezo az ErtTxn tablaban
    gyak_field = 'gyakori_faasz'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field_name = db_field.name

        # csak a taxon statuszokat mutassa
        if field_name[-10:] == 'txn_status':
            kwargs["queryset"] = Status.objects.filter(sta_tipus='taxon')

        # csak a rezervatumban elofordulo taxonokat mutassa
        if field_name[-3:] == 'txn':
            resolved = resolve(request.path_info)
            try:
                kwargs["queryset"] = get_mvp_txns(resolved.kwargs['object_id'], self)             
            except KeyError:
                pass

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

#from django import forms
class FaaAdatInline(admin.StackedInline):
    """
    Model admin for 'Faállomány adatlap'
    """
    form = FaaAdatInlineForm
    model = FaaAdat
    fk_name = "jkv_adat"
    classes = ['collapse']
    max_num = 1


class FaeAzoInline(JKVInline):
    model = FaeAzo
    
    exclude = ('mvp', 'eov_dx', 'eov_dy', 'fae_szog', 'fae_adatokszama', 'fae_mvp_id')


class FaeAdatInline(JKVInline):
    model = FaeAdat

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field_name = db_field.name
        # csak a jegyzokonyvbe vitt fae azonositok kozul lehessen valasztani
        if field_name == 'fae':
            resolved = resolve(request.path_info)
            try:
                kwargs["queryset"] = FaeAzo.objects.filter(jkv_adat_id=resolved.kwargs['object_id'])
            except KeyError:
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class FhfAdatInline(JKVInline):
    model = FhfAdat


class JegyzokonyvAlt2Admin(JegyzokonyvAltalanosAdmin):
    """
    Az altalanos jegyzokonyv szukitese, modositasa - ez az alapja a tovabbi jegyzokonyv-változatoknak
    """

    form = JegyzokonyvModAdminForm

    basic_fields = ()
    second_fields = ()
    fieldsets = (basic_fields, second_fields)
    readonly_fields = ()

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('prj', 'mvp', 'anov_kesz', 'anov_modszertan', 'ujcs_kesz', 'ujcs_modszertan')
        return self.readonly_fields

    def has_add_permission(self, request, obj=None):
        """ 
        responsible for displaying a model in admin index
        false: eltunteti a balmenubol a modelt -> get_model_perms rakja vissza, ha van szerkesztheto jegyzokonyv
        """
        return False
        
    def get_prj_ids(self, username):
        """
        - az 'a_szrpkor' (Permission - Szerepkör) beaallitasai alapjan eldonti, h mely projektekre van a usernek jogosultsaga
        - returns list of prj_ids
        - beallitasok: user egyeztetese, datumok ellenorzese, szerk_kod ellenorzese
        - user egyeztetese: kozos mezo alapjan (Person.djangouser - User.username)
        """
        try:
            szemely = Person.objects.get(djangouser=username).szm_id
            szerk_kod = self.get_szerk_kod()
            perms = Permission.objects.filter(szm=szemely).values('prj', 'mikortol', 'meddig', szerk_kod)
            today = datetime.today()
            prj_ids = [perm['prj'] for perm in perms if perm['mikortol'] < today and today < perm['meddig'] and perm[szerk_kod] == 1]
            return prj_ids
        # ha nincs szemely, aki megfelel a usernek, ures listat ad vissza
        except Person.DoesNotExist:
            return []
    
    def get_relevant_prjs(self, request):
        """ filter.py hasznalja: relevans projektek listajat adja vissza
            relevans projekt: azok a projektek, amikhez a felhasznalonak van ervenyes datumu szerepkore """
        current_user = request.user
        if not current_user.is_superuser:
            prj_ids = self.get_prj_ids(current_user.username)
            return Project.objects.filter(prj_id__in=prj_ids)
        else:
            return Project.objects.all()

    def get_relevant_ERs(self, request):
        """ filter.py hasznalja: relevans erdorezervatumok listajat adja vissza ((id, nev) tuple-kent) """
        current_user = request.user
        queryset = ForestReserve.objects.exclude(ert_nev__contains='TESZT').order_by('ert_nev')
        if not current_user.is_superuser:
            ert_ids = self.get_relevant_prjs(request).values_list('prj_ert_id', flat=True)
            queryset = queryset.filter(pk__in=ert_ids)
            #erts = sorted([(str(ert.ert_id), ert.ert_nev) for ert in queryset], key=lambda tup: tup[1])
        return queryset
    
    def get_szerk_kod(self):
        """ 
        a model-re vonatkozo hozzaferesi mezo a Permission tablaban 
        default: faasz_szerk
        """
        return 'faasz_szerk'

    def get_queryset(self, request):
        """
        Return queryset filtered by relevant projects and szerk_kod.
        csak azok a jegyzokonyvek latszanak, amely projektekre van ervenyes szerkesztoi joga a felhasznalonak
        """
        qs = super(JegyzokonyvAlt2Admin, self).get_queryset(request)
        current_user = request.user
        if not current_user.is_superuser:
            prjs = self.get_prj_ids(current_user.username)
            qs = qs.filter(prj__in=prjs)
        return qs

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index, if no relevant projects.
        ha nincs a menuponthoz tartozo jegyzokonyv (vagyis nem volt semmire jogosultsaga a usernek), eltunik a menubol
        """
        perms = super(JegyzokonyvAlt2Admin, self).get_model_perms(request)
        current_user = request.user
        if not current_user.is_superuser:
            prjs = self.get_prj_ids(current_user.username)
            if len(prjs) == 0:
                return {}
        return perms

    def render_change_form(self, request, context, *args, **kwargs):
        """
            hozzaadjuk a "project_creation/js/admin/InlineRelatedObjectLookups.js"-t
        """
        self.change_form_template = 'admin/adatfeldolgozas/change_form_jegyzokonyv.html'
        return super().render_change_form(request, context, *args, **kwargs)

    class Media:
        js = get_collapsed_js()


@admin.register(JegyzokonyvFAA)
class JegyzokonyvFAAAdmin(JegyzokonyvAlt2Admin):
    """
    Admin model for 'Faállomány adatlap'
    """

    basic_fields = (None, {
        'fields': ('prj',
                   'mvp')
    })
    second_fields = ('FAÁSZ fejléc', {
        'classes': ('collapse',),
        'fields': ('faasz_adatlap_ssz',
                   'faasz_felmeresdatum',
                   'faasz_felmero',
                   'faasz_jkonyvezo')
    })
    fieldsets = (basic_fields, second_fields)
    
    list_filter = (
        (ERListFilter),
        ('prj', ProjectRelatedByER),
        ('mvp', MVPRelatedByProject),
        ('faasz_adatlap_ssz', SorszamDropdownFilter),
        ('faa_kesz', ChoiceDropdownFilter),
        ('faasz_felmero', FelmeroDropdownFilter),
        ('faasz_jkonyvezo', FelmeroDropdownFilter),
    )

    list_display = ('jkv_adat_id', 'get_prj', 'mvp', 'get_faasz_datum', 'get_faasz_sorszam', 'faa_kesz',)
    
    inlines = [FaaAdatInline]

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'title': 'FAÁSZ ' + self.model._meta.verbose_name + ' szerkesztése',
        })
        return super().render_change_form(request, context, add, change, form_url, obj)


@admin.register(JegyzokonyvFAEazon)
class JegyzokonyvFAEazonAdmin(JegyzokonyvFAAAdmin):
    """
    Admin model for 'Faegyed azonosító adatlap'
    """
    basic_fields = (None, {
        'fields': ('prj',
                   'mvp')
    })
    second_fields = ('FAÁSZ fejléc', {
        'classes': ('collapse',),
        'fields': ('faasz_adatlap_ssz',
                   'faasz_felmeresdatum',
                   'get_faasz_felmero',
                   'get_faasz_jkonyvezo')
    })
    fieldsets = (basic_fields, second_fields)


    list_filter = (
        (ERListFilter),
        ('prj', ProjectRelatedByER),
        ('mvp', MVPRelatedByProject),
        ('faasz_adatlap_ssz', SorszamDropdownFilter),
        ('fae_kesz', ChoiceDropdownFilter),
        ('faasz_felmero', FelmeroDropdownFilter),
        ('faasz_jkonyvezo', FelmeroDropdownFilter),
    )
    
    inlines = [FaeAzoInline]
    
    list_display = ('jkv_adat_id', 'get_prj', 'mvp', 'get_faasz_datum', 'get_faasz_sorszam', 'fae_kesz',)
    
    class Media:
        js = get_collapsed_js()

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('prj', 'mvp', 'get_faasz_felmero', 'get_faasz_jkonyvezo', 'faasz_felmeresdatum', 'faasz_adatlap_ssz')
        return self.readonly_fields

@admin.register(JegyzokonyvFAEadat)
class JegyzokonyvFAEadatAdmin(JegyzokonyvFAEazonAdmin):
    """
    Admin model for 'Faegyed adatlap'
    """
   
    inlines = [FaeAdatInline]
    class Media:
        js = get_collapsed_js() + ['project_creation/js/faasz_egyesfa.js']


@admin.register(JegyzokonyvFHF)
class JegyzokonyvFHFAdmin(JegyzokonyvFAAAdmin):
    """
    Admin model for 'Fekvő holtfa adatlap'
    """

    basic_fields = (None, {
        'fields': ('prj',
                   'mvp')
    })
    second_fields = ('FAÁSZ fejléc', {
        'classes': ('collapse',),
        'fields': ('faasz_adatlap_ssz',
                   'faasz_felmeresdatum',
                   'get_faasz_felmero',
                   'get_faasz_jkonyvezo')
    })
    fieldsets = (basic_fields, second_fields)
    
    list_filter = (
        (ERListFilter),
        ('prj', ProjectRelatedByER),
        ('mvp', MVPRelatedByProject),
        ('faasz_adatlap_ssz', SorszamDropdownFilter),
        ('fhf_kesz', ChoiceDropdownFilter),
        ('faasz_felmero', FelmeroDropdownFilter),
        ('faasz_jkonyvezo', FelmeroDropdownFilter),
    )
    
    inlines = [FhfAdatInline]
    
    list_display = ('jkv_adat_id', 'get_prj', 'mvp', 'get_faasz_datum', 'get_faasz_sorszam', 'fhf_kesz',)
    
    class Media:
        js = get_collapsed_js()


    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('prj', 'mvp', 'faasz_felmeresdatum', 'get_faasz_felmero', 'get_faasz_jkonyvezo', 'faasz_adatlap_ssz')
        return self.readonly_fields




# --------------------------------------------------------------------------------------------------------------------
# inline formset helyett a form ala rakott "view" az adatlapokhoz tartozo adatrekordok letrehozasara es szerkesztesere
# felhasznalja: django-changelist-inline modul es a django beepitett popup-kezeleset (RelatedObjectLookups.js modositasa)
# https://pypi.org/project/django-changelist-inline/ alapjan
# django_changelist_inline-1.0.3.dist-info/METADATA
# --------------------------------------------------------------------------------------------------------------------

class JKVAdatAdmin(admin.ModelAdmin):
    """ - altalanos lista a jegyzokonyv-adatrekordoknak, ami a fomenuben jelenne meg, de ott nem kell, csak beagyazva
        - eltuntetese a fomenubol: get_model_perms segitsegevel
        - azert kell, mert kulonben a beagyazott (inline) lista nem mukodik, ez a regisztralt modelAdmin, amit a beagyazott lista felhasznal
    """

    # a taxonokra vonatkozo elofordulasi mezo az ErtTxn tablaban (get_mvp_txns-hoz)
    gyak_field = 'gyakori_faasz'
    
    def get_jkv_id_from_request(self, request):
        """ a jkv_adat_id-t a felugro ablak url-jebe teszem a JKVChangelistModelAdminban, pl.:
            http://193.225.215.56/teszt/admin/adatfeldolgozas/fnovadat/add/?_popup=1&_parent=5256
            igy ki tudom szedni (egyebkent GET esetben a HTTP_REFERER-bol lehet kiszedni)
        """
        return request.GET.get('_parent')
        # REQUEST_URI.split.('=')[-1]

    def get_obj_id_from_request(self, request):
        """ obj_id (az adatrekord id) is a felugro ablak requestjebol szedheto ki """
        resolved = resolve(request.path_info)
        try:
            return resolved.kwargs['object_id']
        except KeyError:
            return None
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field_name = db_field.name
        # uj adatrekordnal inicializaljuk a jkv_adat_id-t a parent_id alapjan
        if field_name == 'jkv_adat':
            try:
                kwargs['initial'] = self.get_jkv_id_from_request(request)
                # making the field readonly - nem kell, css-ben letiltottam
                # kwargs['disabled'] = True                
            except (KeyError, ValueError):
                pass

        # csak a taxon statuszokat mutassa
        if field_name[-10:] == 'txn_status':
            kwargs["queryset"] = Status.objects.filter(sta_tipus='taxon')

        # csak a rezervatumban elofordulo taxonokat mutassa
        if field_name[-3:] == 'txn':
            # logger.warning('obj_id: '+str(self.get_obj_id_from_request(request)))
            try:
                kwargs["queryset"] = get_mvp_txns(self.get_jkv_id_from_request(request), self, self.get_obj_id_from_request(request))
            except:
                pass
                
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, *args, **kwargs):
        """ ne lehessen a formbol szerkeszteni a kapcsolt mezoket """
        formfield = super().formfield_for_dbfield(*args, **kwargs)
        try:
            formfield.widget.can_delete_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_add_related = False
            formfield.widget.can_view_related = False
        except AttributeError:
            pass
        return formfield

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


@admin.register(FNovAdat)
class AnovAdatAdmin(JKVAdatAdmin):
    """ lista az anov adatrekordoknak, ami a fomenuben jelenne meg, eltuntetese: get_model_perms segitsegevel
        azert kell, mert kulonben a beagyazott (inline) lista nem mukodik, ez a regisztralt modelAdmin, amit felhasznal
    """
    form = AnovAdatInlineForm

    exclude = ['nov_boritas', 'nov_ohjtszam', 'nov_van', 'adat_sta', 'nov_adatokszama']

    # a taxonokra vonatkozo elofordulasi mezo az ErtTxn tablaban (get_mvp_txns-hoz)
    gyak_field = 'gyakori_anov'
    
    def get_exclude(self, request, obj=None):
        jkv_id = self.get_jkv_id_from_request(request)
        anov_modszertan_id = Jegyzokonyv.objects.get(pk=jkv_id).anov_modszertan_id
        if anov_modszertan_id in [2, 3, 4, 5]:
            self.exclude = self.exclude + ['nov_gyakorisag']
        if anov_modszertan_id == 3:
            self.exclude = self.exclude + ['nov_van']
        return self.exclude

@admin.register(UcsAdat)
class UcsAdatAdmin(JKVAdatAdmin):
    """ lista az ujcs adatrekordoknak, ami a fomenuben jelenne meg, eltuntetese: get_model_perms segitsegevel
        azert kell, mert kulonben a beagyazott (inline) lista nem mukodik, ez a regisztralt modelAdmin, amit felhasznal
    """

    exclude = ['uju_van', 'cse_van', 'adat_sta', 'ucs_adatokszama']

    # a taxonokra vonatkozo elofordulasi mezo az ErtTxn tablaban (get_mvp_txns-hoz)
    gyak_field = 'gyakori_ujcs'


        
class JKVChangelistModelAdmin(ChangelistInlineModelAdmin):
    """ altalanos lista az adatrekordoknak, ami egy jegyzokonyv szerkesztesekor jelenik meg
        JKVAdatAdmin-hoz tartozo subclass, egy ChangelistInline-leszarmazottba agyazva ertelmes
        ez az inline lista
        self.sortable_by = () a django_changelist_inline/admin.py-ben, ezt ki kell kommentezni, hogy rendezheto legyen
    """

    # a taxonokra vonatkozo elofordulasi mezo az ErtTxn tablaban
    gyak_field = 'gyakori_anov'

    # taxonmezo neve a self.modelben
    txn_field = 'nov_txn'
    
    # taxonstatusz-mezo neve a self.modelben
    txnst_field = 'nov_txn_status'
    
    def get_txn_st(self, obj):
        txnst_field = get_sta_field(self)
        sta_leiras = getattr(obj, txnst_field)
        return Status.objects.get(sta_leiras=sta_leiras).sta_rnev
    
    def get_txn(self, obj):
        txn_field = get_txn_field(self)
        return getattr(obj, txn_field) # obj.nov_txn

    get_txn_st.short_description = "Taxon státusz"
    get_txn_st.admin_order_field = f'{txnst_field}__sta_rnev'        
    get_txn.short_description = "Taxon név"
    get_txn.admin_order_field = f'{txn_field}__latinnev'        

    list_display_links = None
    list_per_page = 15
    show_full_result_count = True


    
    def get_queryset(self, request):
        return self.model.objects.filter(jkv_adat=self.parent_instance)            
   
    def get_url_items(self, action_type, obj=None):
        """ a felugro ablakok linkjeit ezekbol a darabokbol allitjuk ossze """

        app_label=self.model._meta.app_label
        model_name=self.model._meta.model_name
        verbose_name=self.model._meta.verbose_name
        try:
            obj_pk=str(obj.pk)
            link_url = reverse('admin:{app_label}_{model_name}_{action_type}'.format(app_label=app_label, model_name=model_name, action_type=action_type), args=[obj.pk],)
            data_href_template = str(link_url).replace(obj_pk, "__fk__")
        except AttributeError:
            obj_pk=''
        popup = '?_popup=1'
        img_params = 'alt="" width="20" height="20"'
        parent = '&amp;_parent='+str(self.parent_instance.pk)
        url_class = f'related-widget-wrapper-link {action_type}-related'
        url_id = f'{action_type}_id_{model_name}_{obj_pk}'
        img_src = f'{STATIC_URL}admin/img/icon-{action_type}link.svg'
        if action_type == 'add':
            title=f'Újabb {verbose_name} hozzáadása'
            return url_class, url_id, popup, parent, title, img_src, img_params
        if action_type == 'change':
            title=f'Kiválasztott {verbose_name} szerkesztése'
        if action_type == 'delete':
            title=f'Kiválasztott {verbose_name} törlése'
        return link_url, url_class, url_id, data_href_template, popup, parent, title, img_src, img_params            
   
    @mark_safe
    def format_actions(self, obj=None):
        if obj is None:
            return None #self.empty_value_display

        urls = '<div class="related-widget-wrapper">'
        for action in ['change', 'delete']:
            link_url, url_class, url_id, data_href_template, popup, parent, title, img_src, img_params = self.get_url_items(action, obj)
            urls += f'<a class="{url_class}" id="{url_id}" data-popup="yes" data-href-template="{data_href_template}{popup}" title="{title}" href="{link_url}{popup}{parent}"><img src="{img_src}" {img_params}></a>'
        urls += '</div>'

        return urls

    format_actions.short_description = 'Műveletek'

    @property
    def no_results_message(self):
        return f'Nincs {self.model._meta.verbose_name} a jegyzőkönyvben.'

    def get_add_url(self, request):
        # ha elfogytak a valaszthato taxonok, ne lehessen tobbet hozzaadni
        if len(get_mvp_txns(self.parent_instance.pk, self, None)) == 0:
            return None

        result = super().get_add_url(request)

        if result is not None:
            url_class, url_id, popup, parent, title, img_src, img_params = self.get_url_items('add')
            add_url = f'<a class="{url_class}" id="{url_id}" data-popup="yes" title="{title}" href="{result}{popup}{parent}"><img src="{img_src}" {img_params}> {title}</a>'
            return add_url
        return result

    def get_show_all_url(self, request):
        return None


class JegyzokonyvChangelistInline(ChangelistInline):

    model = FNovAdat
    fk_name = "jkv_adat"

    def bind(self, request, parent_instance):
        """ site-packages/django_changelist_inline/admin.py ChangelistInline alapjan
            internal_request.GET = QueryDict(mutable=False) nem lehet, mert akkor a QueryDict ures marad
            -> nem mukodik az oszlopok rendezese es a lapozas
            https://django.readthedocs.io/en/1.6.x/ref/request-response.html
        """
        internal_request = copy.copy(request)

        # QueryDict empty and mutable -> _changelist_filters nem kerul a request.GETbe
        internal_request.GET = QueryDict(mutable=True)
        # ha van "mutassa mindet", rendezes vagy lapozas, az keruljon bele
        for param in ['all', 'o', 'p']:
            if request.GET.__contains__(param):
                value = request.GET.get(param, None)
                internal_request.GET.update({param:value})

        internal_request.POST = QueryDict(mutable=False)
        self.request = internal_request

        self.changelist_model_admin = self.ChangelistModelAdmin(
            parent_instance,
            self.model,
            self.admin_site,
        )

    class ChangelistModelAdmin(JKVChangelistModelAdmin):
        """ lista az anov adatrekordoknak, ami egy jegyzokonyv szerkesztesekor jelenik meg
            AnovAdatAdmin-hoz tartozo subclass
            ez az inline lista
            self.sortable_by = () a django_changelist_inline/admin.py-ben, ezt ki kell kommentezni, hogy rendezheto legyen
        """
        list_display = ('nov_adat_id', 'get_txn', 'get_txn_st', 'nov_gyakorisag', 'nov_elofordul', 'format_actions')
        ordering = ('nov_adat_id',)


class AnovAdatChangelistInline(JegyzokonyvChangelistInline):
    model = FNovAdat
    
class UcsAdatChangelistInline(JegyzokonyvChangelistInline):
    model = UcsAdat

    class ChangelistModelAdmin(JKVChangelistModelAdmin):
        """ lista az ujcs adatrekordoknak, ami egy jegyzokonyv szerkesztesekor jelenik meg
            UjcsAdatAdmin-hoz tartozo subclass
            ez az inline lista
        """
        list_display = ('ucs_adat_id', 'get_txn', 'get_txn_st', 'format_actions')
        ordering = ('ucs_adat_id',)

        # a taxonokra vonatkozo elofordulasi mezo az ErtTxn tablaban
        gyak_field = 'gyakori_ujcs'

        # taxonmezo neve a self.modelben
        txn_field = 'ucs_txn'
        
        # taxonstatusz-mezo neve a self.modelben
        txnst_field = 'ucs_txn_status' 
    

@admin.register(JegyzokonyvANOV)
class JegyzokonyvANOVAdmin(ChangelistInlineAdmin, JegyzokonyvAlt2Admin):
    """
    Admin model for 'ANOV adatlap'
    lista az anov adatlapoknak, ami a fomenuben jelenik meg
    amikor az egyes adatlapokat szerkesztjuk, a megnyitott adatlap-formba agyazzuk az inline listat
    """
    list_filter = (
        (ERListFilter),
        ('prj', ProjectRelatedByER),
        ('mvp', MVPRelatedByProject),
        ('anov_adatlap_ssz', SorszamDropdownFilter),
        ('anov_kesz', ChoiceDropdownFilter),
        ('anov_felmero', FelmeroDropdownFilter),
        ('anov_jkonyvezo', FelmeroDropdownFilter),
    )

    list_display = ('jkv_adat_id', 'get_prj', 'mvp', 'get_anov_datum', 'get_anov_sorszam', 'anov_kesz')

    basic_fields = (None, {
        'fields': ('prj',
                   'mvp',
                   'anov_kesz',
                   'anov_modszertan')
    })
    second_fields = ('ANOV fejléc', {
        'classes': ('collapse',),
        'fields': ('anov_adatlap_ssz',
                   'anov_felmeresdatum',
                   'anov_felmero',
                   'anov_jkonyvezo')
    })
    fieldsets = (basic_fields, second_fields)

    inlines = [AnovAdatChangelistInline]

    def get_szerk_kod(self):
        return 'anov_szerk'

    # kesz_update_settings: adatlap_nev, update_field, adatrekord_objects
    kesz_update_settings = 'ANÖV', 'anov_kesz', FNovAdat.objects
    actions = [update_keszultseg]

@admin.register(JegyzokonyvUJCS)
class JegyzokonyvUJCSAdmin(ChangelistInlineAdmin, JegyzokonyvAlt2Admin):
    """
    Admin model for 'UJCS adatlap'
    """
    
    list_filter = (
        (ERListFilter),
        ('prj', ProjectRelatedByER),
        ('mvp', MVPRelatedByProject),
        ('ujcs_adatlap_ssz', SorszamDropdownFilter),
        ('ujcs_kesz', ChoiceDropdownFilter),
        ('ujcs_felmero', FelmeroDropdownFilter),
        ('ujcs_jkonyvezo', FelmeroDropdownFilter),
    )

    list_display = ('jkv_adat_id', 'get_prj', 'mvp', 'get_ujcs_datum', 'get_ujcs_sorszam', 'ujcs_kesz')

    basic_fields = (None, {
        'fields': ('prj',
                   'mvp',
                   'ujcs_kesz',
                   'ujcs_modszertan')
    })
    second_fields = ('UJCS fejléc', {
        'classes': ('collapse',),
        'fields': ('ujcs_adatlap_ssz',
                   'ujcs_felmeresdatum',
                   'ujcs_felmero',
                   'ujcs_jkonyvezo')
    })
    fieldsets = (basic_fields, second_fields)

    inlines = [UcsAdatChangelistInline]
    
    def get_szerk_kod(self):
        return 'ujcs_szerk'

    # adatlap_nev, update_field, adatlap_objects
    kesz_update_settings = 'UJCS', 'ujcs_kesz', UcsAdat.objects
    actions = [update_keszultseg]


