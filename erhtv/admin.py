"""
Add the models and their settings to django admin.

More information at: http://docs.djangoproject.com/en/4.0/ref/contrib/admin/
"""
from django.contrib import admin
from django.contrib.admin import helpers
from django import forms
from json import dumps

import logging
logger = logging.getLogger(__name__)

from erhtv.filters.filters import ChoiceDropdownFilter, DropdownFilter, RelatedDropdownFilter, \
    BooleanDropdownFilter, generate_select2_filter, OverrideDropdownFilter, ERListFilter, ProjectRelatedByER, \
    MVPRelatedByProject, SorszamDropdownFilter, CsoportDropdownFilter
from erhtv.models.models import Project, Person, ForestReserve, Status, Permission, SamplingPoint, \
    Log, Action, Taxon, ErtTxn, Jegyzokonyv, PrMvpCsopKat, PrMvpCsop, PrMvpCsopElem
from erhtv.forms.forms import TaxonModAdminForm
from erhtv.admin_functions.actions import ertx_copy, prmvp_create, jvk_create, mvp_create_from_csv
from erhtv.admin_functions.functions import get_app_list

           
admin.AdminSite.get_app_list = get_app_list


def get_Forest_azo():
    """
    ('ert', OverrideDropdownFilter) szurot hasznalo modellek szamara (get_dropdown_settings)
    """
    ert_azon = ForestReserve.objects.exclude(ert_nev__contains='TESZT').order_by('ert_azo').values('ert_id', 'ert_azo')
    return 'ER azonosító', [(ert['ert_id'], ert['ert_azo']) for ert in ert_azon]

@admin.register(Taxon)
class TaxonAdmin(admin.ModelAdmin):
    """
    Admin model for 'Taxonok'
    """
    show_facets = admin.ShowFacets.NEVER # Szamok megjelenitese/elrejtese - ALWAYS, ALLOW, NEVER
    list_filter = (
        ('nn', DropdownFilter),
        ('csalad', DropdownFilter),
        ('taxonrang', DropdownFilter),
        ('genus', DropdownFilter),
        ('facsje', DropdownFilter)
    )
    search_fields = ['magyarnev', 'latinnev', 'erd_kod']
    fields = (
        'txn_id',
        'txn_azo',
        'erd_kod',
        'soossz',
        'kod532',
        'nn',
        'csalad',
        'taxonrang',
        'genus',
        'species',
        'auctor',
        'istax',
        'istax_auctor',
        'magyarnev',
        'latinnev',
        'megjegyzes',
        'facsje',
        'eletforma',
        'honos',
        'genusvalaszto',
        'latinnevvalaszto',
        'osztaly_fafajlatinnev_focsoport',
        'osztaly_fafajlatinnev_csoport',
        'osztaly_csjelatinnev_focsoport',
        'osztaly_csjelatinnev_csoport',
        'osztaly_gyszintlatinnev_focsoport',
        'osztaly_gyszintlatinnev_csoport'
    )
    list_display = ('latinnev','txn_id','soossz','kod532')
    readonly_fields = ('txn_id',)
    ordering = ['latinnev']
    form = TaxonModAdminForm
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

@admin.register(ErtTxn)
class ErtTxnAdmin(admin.ModelAdmin):
    """
    Admin model for 'Taxonok ER-onként'
    """
    show_facets = admin.ShowFacets.NEVER
    search_fields = ['txn__latinnev']
    list_filter = (
        ('ert', OverrideDropdownFilter),
        generate_select2_filter(ErtTxn, 'ert'),
        generate_select2_filter(ErtTxn, 'txn'),
        ('gyakori_faasz', ChoiceDropdownFilter),
        ('gyakori_ujcs', ChoiceDropdownFilter),
        ('gyakori_anov', ChoiceDropdownFilter),
    )
    list_display = ('erttxn_id', 'get_ert', 'get_txn', 'gyakori_faasz', 'gyakori_ujcs', 'gyakori_anov')
    ordering = ['ert__ert_nev', 'txn__latinnev']
    
    # ezek azert kellenek, hogy ER terület és Taxon esetén ne kulcs (id), hanem érték (ert_nev/latinnev) szerint menjen a rendezes, ehhez a modelben ForeignKey-re kellett allitani a mezot integerrol
    def get_ert(self, obj):
        return obj.ert
    
    def get_txn(self, obj):
        return obj.txn
    
    get_ert.short_description = "ER terület"
    get_ert.admin_order_field = 'ert__ert_nev'
    get_txn.short_description = "Taxon"
    get_txn.admin_order_field = 'txn__latinnev'
    
    # ez OverrideDropdownFilter-hez kell
    def get_dropdown_settings(self):
        return get_Forest_azo()
    
    actions=[ertx_copy]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """
    Admin model for 'Személyek'
    """
    search_fields = ['szm_nev']
    ordering = ['szm_nev']
    fields = ('szm_id', 'szm_nev', 'szm_rnev', 'djangouser')
    readonly_fields = ('szm_id',)


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    search_fields = ['sta_leiras']
    fields = ('sta_id', 'sta_tipus', 'sta_rnev', 'sta_leiras')
    readonly_fields = ('sta_id',)

    # autocomplete filterben csak a projek-statusokat mutassa, a taxonokat ne
    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term,
        )
        if request.path[-20:] == '/admin/autocomplete/':
            queryset = self.model.objects.filter(sta_tipus='projekt').order_by('sta_id')
        return queryset, may_have_duplicates


@admin.register(SamplingPoint)
class SamplingPointAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.NEVER
    search_fields = ['mvp_azo']
    list_filter = (
        ('ert', OverrideDropdownFilter),
        generate_select2_filter(SamplingPoint, 'ert'),
        ('mvp_mtvz', DropdownFilter),
        ('mvp_tszfm', DropdownFilter)
    )
    fields = (
        'mvp_id',
        'ert',
        'mvp_azo',
        'mvp_eov_x',
        'mvp_eov_y',
        'mvp_tszfm',
        'mvp_pontossag',
        'mvp_lejtesirany',
        'mvp_lejtoszog',
        'mvp_wgs84_fi',
        'mvp_wgs84_lambda',
        'mvp_maxfa',
        'mvp_mtvz',
        'megjegyzes'
    )
    autocomplete_fields = ['ert']
    readonly_fields = ('mvp_id',)
    list_display = ('ert','mvp_azo')
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_dropdown_settings(self):
        return get_Forest_azo()

    actions=[prmvp_create, jvk_create, mvp_create_from_csv]
    
    def changelist_view(self, request, extra_context=None):
        """ azert kell, h az mvp_create_from_csv mukodjon mvp-k kivalasztasa nelkul is
            a postba betesz egy kamu kerest
        """
        if 'action' in request.POST and request.POST['action'] == 'mvp_create_from_csv':
            if not request.POST.getlist(helpers.ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                post.update({helpers.ACTION_CHECKBOX_NAME: '1'})
                request._set_post(post)
        return super(SamplingPointAdmin, self).changelist_view(request, extra_context)


@admin.register(Action)
class AkcAdmin(admin.ModelAdmin):
    search_fields = ['akc_azo']
    ordering = ['akc_azo']
    fields = ('akc_id', 'akc_azo', 'akc_megj')
    readonly_fields = ('akc_id',)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.NEVER
    list_filter = (
        ('naplo_szerepkor_id', DropdownFilter),
        generate_select2_filter(Log, 'naplo_akc'),
        ('naplo_mvp_id', DropdownFilter)
    )
    fields = (
        'naplo_id',
        'naplo_datum',
        'naplo_szerepkor_id',
        'naplo_akc',
        'naplo_mvp_id'
    )
    readonly_fields = ('naplo_id',)
    ordering = ['-naplo_id']


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.NEVER
    list_filter = (
        generate_select2_filter(Permission, 'prj'),
        generate_select2_filter(Permission, 'szm'),
        ('felhasznalo', DropdownFilter),
        ('faasz_szerk', BooleanDropdownFilter),
        ('ujcs_szerk', BooleanDropdownFilter),
        ('anov_szerk', BooleanDropdownFilter),
        ('dfoto_szerk', BooleanDropdownFilter),
        ('megj_szerk', BooleanDropdownFilter),
        ('tip_szerk', BooleanDropdownFilter),
        ('mvp_szerk', BooleanDropdownFilter),
        ('prjerh_szerk', BooleanDropdownFilter),
        ('txnk_szerk', BooleanDropdownFilter),
        ('kesz_szerk', BooleanDropdownFilter)
    )
    fields = ('szerepkor_id',
              'prj',
              'szm',
              'szerepkor',
              'felhasznalo',
              'jelszo',
              'mikortol',
              'meddig',
              'faasz_szerk',
              'ujcs_szerk',
              'anov_szerk',
              'dfoto_szerk',
              'megj_szerk',
              'tip_szerk',
              'mvp_szerk',
              'prjerh_szerk',
              'txnk_szerk',
              'kesz_szerk')
    ordering = ['szerepkor']
    autocomplete_fields = ['prj', 'szm']
    readonly_fields = ('szerepkor_id',)


@admin.register(ForestReserve)
class ForestAdmin(admin.ModelAdmin):
    """
    Admin model for 'Erdőrezervátumok'
    """
    show_facets = admin.ShowFacets.NEVER
    search_fields = ['ert_nev']
    list_filter = (('ert_orszag', ChoiceDropdownFilter),
                   ('egnagytaj', ChoiceDropdownFilter))
    fields = ('ert_id',
              'ert_azo',
              'ert_ssz',
              'ert_nev',
              'ert_orszag',
              'ert_url',
              'ert_lat_n_fok',
              'ert_lat_n_perc',
              'ert_lat_n_mperc',
              'ert_lon_e_fok',
              'ert_lon_e_perc',
              'ert_lon_e_mperc',
              'egnagytaj')
              
    ordering = ['ert_nev']
    readonly_fields = ('ert_id',)
    
    list_display = ('ert_azo', 'ert_nev')

    def get_queryset(self, request):
        qs = ForestReserve.objects.exclude(ert_nev__contains='TESZT')
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin model for 'Projektek'
    """
    show_facets = admin.ShowFacets.NEVER
    search_fields = ['prj_nev']
    list_filter = (
        ('prj_ert', OverrideDropdownFilter),
        generate_select2_filter(Project, 'prj_ert'),
        generate_select2_filter(Project, 'prj_vez'),
        generate_select2_filter(Project, 'prj_sta'),
        ('prj_ev', DropdownFilter),
        ('prj_hanyadikfelmeres', DropdownFilter),
        ('prj_kovetkezo_ev', DropdownFilter),
        ('prj_mindkesz', ChoiceDropdownFilter),
        ('prj_faa_kesz', ChoiceDropdownFilter),
        ('prj_fae_kesz', ChoiceDropdownFilter),
        ('prj_fhf_kesz', ChoiceDropdownFilter),
        ('prj_ucs_kesz', ChoiceDropdownFilter),
        ('prj_nov_kesz', ChoiceDropdownFilter),
        ('prj_fot_kesz', ChoiceDropdownFilter),
        ('prj_mgj_kesz', ChoiceDropdownFilter),
        ('prj_tip_kesz', ChoiceDropdownFilter),
    )
    autocomplete_fields = ['prj_ert', 'prj_vez']

    basic_fields = (None, {
        'fields': ('prj_id',
                   'prj_nev',
                   'prj_rnev',
                   'prj_ert',
                   'prj_vez',
                   'prj_leiras',
                   'prj_ev',
                   'prj_hanyadikfelmeres',
                   'prj_kovetkezo_ev')
    })
    secondary_fields = ('Másodlagos', {
    
        'fields': ('prj_sta',
                   'prj_url',
                   'prj_ert_dszog',
                   'prj_ert_ddatum')
    })
    advanced_fields = ('Alapértelmezettek', {
        'classes': ('collapse',),
        'fields': ('prj_tmd_faa',
                   'prj_tmd_fae',
                   'prj_tmd_fhf',
                   'prj_tmd_ujcs',
                   'prj_tmd_anov',
                   'prj_tmd_foto',
                   'prj_tmd_megj',
                   'prj_tmd_tipi')

    })
    rest_of_the_fields = ('Maradék', {
        'classes': ('collapse',),
        'fields': ('prj_elozo_prj_id',
                   'prj_elozo_faaprj_id',
                   'prj_elozo_faeprj_id',
                   'prj_elozo_fhfprj_id',
                   'prj_elozo_ucsprj_id',
                   'prj_elozo_novprj_id',
                   'prj_elozo_fotprj_id',
                   'prj_elozo_mgjprj_id',
                   'prj_elozo_tipprj_id',
                   'prj_erh_terv_kesz',
                   'prj_flm_terv_kesz',
                   'prj_mindkesz',
                   'prj_faa_kesz',
                   'prj_fae_kesz',
                   'prj_fhf_kesz',
                   'prj_ucs_kesz',
                   'prj_nov_kesz',
                   'prj_fot_kesz',
                   'prj_fot_fokonyvtar',
                   'prj_mgj_fsz_kesz',
                   'prj_mgj_ucs_kesz',
                   'prj_mgj_nov_kesz',
                   'prj_mgj_kesz',
                   'prj_tip_kesz',)
    })
    fieldsets = (basic_fields, secondary_fields, advanced_fields, rest_of_the_fields)
    
    ordering = ['prj_nev']
    readonly_fields = ('prj_id', 'prj_sta')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filter field values for foreign keys
        :param db_field:
        :param request:
        :param kwargs:
        :return:
        """
        field_name = db_field.name
        if field_name == 'prj_vez':
            kwargs["queryset"] = Person.objects.exclude(szm_nev__contains='TESZT')
        elif field_name == 'prj_ert':
            kwargs["queryset"] = ForestReserve.objects.exclude(ert_nev__contains='TESZT')
        elif field_name == 'prj_sta':
            kwargs["queryset"] = Status.objects.filter(sta_tipus='projekt')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
        
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(ProjectAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'prj_leiras':
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield

    def get_dropdown_settings(self):
        return get_Forest_azo()


class JegyzokonyvAltalanosAdmin(admin.ModelAdmin):
    """
    Minden jegyzokonyv alapja (adatfeldolgozas app hasznalja)
    """
    show_facets = admin.ShowFacets.NEVER  
    list_filter = (
        (ERListFilter),
        ('prj', ProjectRelatedByER),
        ('mvp', MVPRelatedByProject),
        ('faasz_adatlap_ssz', SorszamDropdownFilter),
        ('anov_adatlap_ssz', SorszamDropdownFilter),
        ('foto_adatlap_ssz', SorszamDropdownFilter),
        ('megj_adatlap_ssz', SorszamDropdownFilter),
        ('tip_adatlapssz_ssz', SorszamDropdownFilter),
        ('faa_kesz', ChoiceDropdownFilter),
        ('fae_kesz', ChoiceDropdownFilter),
        ('fhf_kesz', ChoiceDropdownFilter),
        ('ujcs_kesz', ChoiceDropdownFilter),
        ('anov_kesz', ChoiceDropdownFilter),
        ('foto_kesz', ChoiceDropdownFilter),
        ('megj_fsz_kesz', ChoiceDropdownFilter),
        ('megj_ucs_kesz', ChoiceDropdownFilter),
        ('megj_nov_kesz', ChoiceDropdownFilter),
        ('tip_kesz', ChoiceDropdownFilter),

    )

    list_display = ('jkv_adat_id', 'get_prj', 'mvp', 'get_faasz_datum', 'get_faasz_sorszam', 'get_ujcs_datum', 'get_ujcs_sorszam', 'get_anov_datum', 'get_anov_sorszam', 'get_foto_datum', 'get_foto_sorszam', 'get_megj_datum', 'get_megj_sorszam', 'get_tip_datum', 'get_tip_sorszam')
    basic_fields = (None, {
        'fields': ('jkv_adat_id',
                    'prj',
                    'mvp')
    })
    faasz_fields = ('FAA', {
        'classes': ('collapse',),
        'fields': ('faasz_felmeresdatum',
                   'get_faasz_felmero',
                   'get_faasz_jkonyvezo',
                   'faa_modszertan',
                   'fae_modszertan',
                   'fhf_modszertan',
                   'faasz_adatlap_ssz',
                   'faa_kesz',
                   'fae_kesz',
                   'fhf_kesz')
    })
    ujcs_fields = ('UJCS', {
        'classes': ('collapse',),
        'fields': ('ujcs_felmeresdatum',
                   'get_ujcs_felmero',
                   'get_ujcs_jkonyvezo',
                   'ujcs_modszertan',
                   'ujcs_adatlap_ssz',
                   'ujcs_kesz')
    })
    anov_fields = ('ANOV', {
        'classes': ('collapse',),
        'fields': ('anov_felmeresdatum',
                   'get_anov_felmero',
                   'get_anov_jkonyvezo',
                   'anov_modszertan',
                   'anov_adatlap_ssz',
                   'anov_boritas',
                   'anov_kesz')
    })
    foto_fields = ('Foto', {
        'classes': ('collapse',),
        'fields': ('foto_felmeresdatum',
                   'get_foto_felmero',
                   'foto_modszertan',
                   'foto_adatlap_ssz',
                   'foto_kesz')
    })
    megj_fields = ('MEGJ', {
        'classes': ('collapse',),
        'fields': ('megj_felmeresdatum',
                   'get_megj_felmero',
                   'megj_modszertan',
                   'megj_adatlap_ssz',
                   'megj_fsz_kesz',
                   'megj_ucs_kesz',
                   'megj_nov_kesz')
    })
    tip_fields = ('TIP', {
        'classes': ('collapse',),
        'fields': ('tip_felmeresdatum',
                'get_tip_felmero',
                'tip_modszertani',
                'tip_adatlapssz_ssz',
                'tip_kesz')
    })
    kesz_fields = ('KESZ', {
        'classes': ('collapse',),
        'fields': ('erht_kesz',
                'flmt_kesz')
    })

    fieldsets = (basic_fields, faasz_fields, ujcs_fields, anov_fields, foto_fields, megj_fields, tip_fields, kesz_fields)
    readonly_fields = ('jkv_adat_id',)

    def get_prj(self, obj):
        return Project.objects.get(prj_nev=obj.prj).prj_rnev
    get_prj.short_description = "Projekt"
    get_prj.admin_order_field = 'prt__prj_rnev'

    def get_faasz_datum(self, obj):
        try:
            return obj.faasz_felmeresdatum.strftime("%Y-%m-%d")
        except AttributeError:
            return obj.faasz_felmeresdatum
    get_faasz_datum.admin_order_field = 'faasz_felmeresdatum'
    get_faasz_datum.short_description = 'FAASZ dátum'
    def get_faasz_sorszam(self, obj):
            return obj.faasz_adatlap_ssz
    get_faasz_sorszam.admin_order_field = 'faasz_adatlap_ssz'
    get_faasz_sorszam.short_description = 'FAASZ sszám'

    def get_ujcs_datum(self, obj):
        try:
            return obj.ujcs_felmeresdatum.strftime("%Y-%m-%d")
        except AttributeError:
            return obj.ujcs_felmeresdatum
    get_ujcs_datum.admin_order_field = 'ujcs_felmeresdatum'
    get_ujcs_datum.short_description = 'UJCS dátum'
    def get_ujcs_sorszam(self, obj):
            return obj.ujcs_adatlap_ssz
    get_ujcs_sorszam.admin_order_field = 'ujcs_adatlap_ssz'
    get_ujcs_sorszam.short_description = 'UJCS sszám'

    def get_anov_datum(self, obj):
        try:
            return obj.anov_felmeresdatum.strftime("%Y-%m-%d")
        except AttributeError:
            return obj.anov_felmeresdatum
    get_anov_datum.admin_order_field = 'anov_felmeresdatum'
    get_anov_datum.short_description = 'ANOV dátum'
    def get_anov_sorszam(self, obj):
            return obj.anov_adatlap_ssz
    get_anov_sorszam.admin_order_field = 'anov_adatlap_ssz'
    get_anov_sorszam.short_description = 'ANOV sszám'

    def get_foto_datum(self, obj):
        try:
            return obj.foto_felmeresdatum.strftime("%Y-%m-%d")
        except AttributeError:
            return obj.foto_felmeresdatum
    get_foto_datum.admin_order_field = 'foto_felmeresdatum'
    get_foto_datum.short_description = 'foto dátum'
    def get_foto_sorszam(self, obj):
            return obj.foto_adatlap_ssz
    get_foto_sorszam.admin_order_field = 'foto_adatlap_ssz'
    get_foto_sorszam.short_description = 'foto sszám'

    def get_megj_datum(self, obj):
        try:
            return obj.megj_felmeresdatum.strftime("%Y-%m-%d")
        except AttributeError:
            return obj.megj_felmeresdatum
    get_megj_datum.admin_order_field = 'megj_felmeresdatum'
    get_megj_datum.short_description = 'megj dátum'
    def get_megj_sorszam(self, obj):
            return obj.megj_adatlap_ssz
    get_megj_sorszam.admin_order_field = 'megj_adatlap_ssz'
    get_megj_sorszam.short_description = 'megj sszám'

    def get_tip_datum(self, obj):
        try:
            return obj.tip_felmeresdatum.strftime("%Y-%m-%d")
        except AttributeError:
            return obj.tip_felmeresdatum
    get_tip_datum.admin_order_field = 'tip_felmeresdatum'
    get_tip_datum.short_description = 'tip dátum'
    def get_tip_sorszam(self, obj):
            return obj.tip_adatlapssz_ssz
    get_tip_sorszam.admin_order_field = 'tip_adatlapssz_ssz'
    get_tip_sorszam.short_description = 'tip sszám'

    # ezeket azert csinaljuk, hogy a readonly fieldsben a szemely rovid neve latszon
    def get_faasz_felmero(self, obj):
        return obj.faasz_felmero.szm_rnev
    get_faasz_felmero.short_description = Jegyzokonyv.faasz_felmero.__dict__['field'].verbose_name
    def get_faasz_jkonyvezo(self, obj):
        return obj.faasz_jkonyvezo.szm_rnev
    get_faasz_jkonyvezo.short_description = Jegyzokonyv.faasz_jkonyvezo.__dict__['field'].verbose_name

    def get_faasz_felmero(self, obj):
        return obj.faasz_felmero.szm_rnev
    get_faasz_felmero.short_description = Jegyzokonyv.faasz_felmero.__dict__['field'].verbose_name
    def get_faasz_jkonyvezo(self, obj):
        return obj.faasz_jkonyvezo.szm_rnev
    get_faasz_jkonyvezo.short_description = Jegyzokonyv.faasz_jkonyvezo.__dict__['field'].verbose_name
    
    def get_ujcs_felmero(self, obj):
        return obj.ujcs_felmero.szm_rnev
    get_ujcs_felmero.short_description = Jegyzokonyv.ujcs_felmero.__dict__['field'].verbose_name
    def get_ujcs_jkonyvezo(self, obj):
        return obj.ujcs_jkonyvezo.szm_rnev
    get_ujcs_jkonyvezo.short_description = Jegyzokonyv.ujcs_jkonyvezo.__dict__['field'].verbose_name
    
    def get_anov_felmero(self, obj):
        return obj.anov_felmero.szm_rnev
    get_anov_felmero.short_description = Jegyzokonyv.anov_felmero.__dict__['field'].verbose_name
    def get_anov_jkonyvezo(self, obj):
        return obj.anov_jkonyvezo.szm_rnev
    get_anov_jkonyvezo.short_description = Jegyzokonyv.anov_jkonyvezo.__dict__['field'].verbose_name

    def get_foto_felmero(self, obj):
        return obj.foto_felmero.szm_rnev
    get_foto_felmero.short_description = Jegyzokonyv.foto_felmero.__dict__['field'].verbose_name

    def get_megj_felmero(self, obj):
        return obj.megj_felmero.szm_rnev
    get_megj_felmero.short_description = Jegyzokonyv.megj_felmero.__dict__['field'].verbose_name

    def get_tip_felmero(self, obj):
        return obj.tip_felmero.szm_rnev
    get_tip_felmero.short_description = Jegyzokonyv.tip_felmero.__dict__['field'].verbose_name


    def get_relevant_ERs(self, request):
        """ filter.py hasznalja: erdorezervatumok listajat adja vissza """
        return ForestReserve.objects.exclude(ert_nev__contains='TESZT').order_by('ert_nev')

    def get_relevant_prjs(self, request):
        """ filter.py hasznalja: relevans projektek listajat adja vissza """
        return Project.objects.all()

@admin.register(Jegyzokonyv)
class JegyzokonyvAdmin(JegyzokonyvAltalanosAdmin):

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['prj'].widget.can_change_related = False
        form.base_fields['prj'].widget.can_add_related = False
        form.base_fields['prj'].widget.can_delete_related = False
        form.base_fields['prj'].widget.can_view_related = False
        form.base_fields['mvp'].widget.can_change_related = False
        form.base_fields['mvp'].widget.can_add_related = False
        form.base_fields['mvp'].widget.can_delete_related = False
        form.base_fields['mvp'].widget.can_view_related = False
        return form

    def render_change_form(self, request, context, *args, **kwargs):
        # csak a kivalasztott prj-hez tartozo mvp-ket mutassa a szerkesztesben
        self.change_form_template = 'admin/erhtv/change_form_jegyzokonyv.html'
        prj_queryset = Project.objects.order_by('prj_nev').values('prj_id', 'prj_nev', 'prj_ert')
        prj_list = []
        for prj in prj_queryset:
            prj_dict = {"id": prj['prj_id'], "value": prj['prj_nev']}
            mvp_queryset = SamplingPoint.objects.filter(ert=prj['prj_ert']).values('mvp_id', 'mvp_azo')
            # a kulcs: a html select tag id-ja
            prj_dict["id_mvp"]=[{"id": mvp['mvp_id'], "value": mvp['mvp_azo']} for mvp in mvp_queryset]
            prj_list.append(prj_dict)
        prjJSON = dumps(prj_list)
        extra = {'prjJSON': prjJSON,}
        context.update(extra)
        return super(JegyzokonyvAdmin, self).render_change_form(request, context, *args, **kwargs)
    
    readonly_fields = ('jkv_adat_id', 'get_faasz_felmero', 'get_faasz_jkonyvezo', 'get_ujcs_felmero', 'get_ujcs_jkonyvezo', 'get_anov_felmero', 'get_anov_jkonyvezo', 'get_foto_felmero', 'get_megj_felmero', 'get_tip_felmero', 'faasz_felmeresdatum', 'faasz_adatlap_ssz', 'ujcs_felmeresdatum', 'ujcs_adatlap_ssz', 'anov_felmeresdatum', 'anov_adatlap_ssz', 'foto_felmeresdatum', 'foto_adatlap_ssz', 'megj_felmeresdatum', 'megj_adatlap_ssz', 'tip_felmeresdatum', 'tip_adatlapssz_ssz')


class PrMvpCsopInline(admin.TabularInline):
    model = PrMvpCsop
    fields = ('csoport_id', 'csopprj', 'csoport_rnev', 'csoport_nev', 'csoport_leiras')
    readonly_fields = ('csoport_id',)
    extra = 1
    classes = ['collapse']


@admin.register(PrMvpCsopKat)
class PrMvpCsopKatAdmin(admin.ModelAdmin):
    search_fields = ['csopprj_rnev']
    list_display = ('csopprj_nev',)
    fields = ('csopprj_id', 'csopprj_rnev', 'csopprj_nev', 'csopprj_vez', 'csopprj_ev', 'csopprj_leiras', 'csopprj_url',)
    readonly_fields = ('csopprj_id',)
    inlines = [PrMvpCsopInline]


@admin.register(PrMvpCsopElem)
class PrMvpCsopElemAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.NEVER
    list_filter = (
        generate_select2_filter(PrMvpCsopElem, 'prj'),
        generate_select2_filter(PrMvpCsopElem, 'mvp'),
        ('csoport', RelatedDropdownFilter),
    )
    list_display = ('csoport_adatix_id','get_prj', 'mvp','get_cso')
    fields = ('csoport_adatix_id', 'prj', 'mvp', 'csoport')
    ordering = ['csoport_adatix_id']
    readonly_fields = ('csoport_adatix_id',)

    # ezek azert kellenek, hogy Projekt és Csoport esetén ne kulcs (id), hanem érték (rnev) szerint menjen a rendezes
    def get_prj(self, obj):
        return Project.objects.get(prj_nev=obj.prj).prj_rnev
    
    def get_cso(self, obj):
        return obj.csoport
    
    get_prj.short_description = "Projekt"
    get_prj.admin_order_field = 'prj__prj_rnev'
    get_cso.short_description = "Csoport"
    get_cso.admin_order_field = 'csoport__csoport_rnev'

