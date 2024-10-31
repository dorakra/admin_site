from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin.filters import (
    SimpleListFilter,
    AllValuesFieldListFilter,
    ChoicesFieldListFilter,
    RelatedFieldListFilter,
    RelatedOnlyFieldListFilter,
    BooleanFieldListFilter
)
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.utils import get_model_from_relation
from erhtv.models.models import Project, Person, PrMvpCsop, Jegyzokonyv #, ForestReserve


def generate_select2_filter(model, field_name):
    """
    A method to automatically generate a Select2 filter for a model
    :param model: The model to generate the field name filter for
    :param field_name: the field name to generate filter for
    :return:
    """
    title = model._meta.get_field(field_name).verbose_name
    filter_name = f'{type(model).__name__}{field_name.capitalize()}Filter'
    filter_class = type(filter_name, (AutocompleteFilter,), {
        'title': title,
        'field_name': field_name})
    return filter_class


# Below there are dropdown filters for different cases
# Based on https://github.com/mrts/django-admin-list-filter-dropdown
class SimpleDropdownFilter(SimpleListFilter):
    template = 'admin/dropdown_filter.html'


class DropdownFilter(AllValuesFieldListFilter):
    template = 'admin/dropdown_filter.html'


class ChoiceDropdownFilter(ChoicesFieldListFilter):
    template = 'admin/dropdown_filter.html'


class RelatedDropdownFilter(RelatedFieldListFilter):
    template = 'admin/dropdown_filter.html'


class RelatedOnlyDropdownFilter(RelatedOnlyFieldListFilter):
    template = 'admin/dropdown_filter.html'

class BooleanDropdownFilter(BooleanFieldListFilter):
    template = 'admin/dropdown_filter.html'


# custom filters
class AltalanosDropdownFilter(ChoiceDropdownFilter):
    """
    # legordulo szuro parameterben megadott mezore
    # valamiben valtozas van, ezert nem lehet a default-ot hasznalni
    # valtozas lehet: ER azonosito a nev helyett, hierarchikus szures miatti szukites

    """

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)

        self.field_name = field_path
        self.current_model = model
        lookup_choices = self.lookups(request, model_admin)
        if lookup_choices is None:
            lookup_choices = ()
        self.flatchoices = list(lookup_choices)
    

    def lookups(self, request, model_admin):
        # pass
        return self.field.flatchoices

    def choices(self, changelist):
        yield {
            "selected": self.lookup_val is None,
            "query_string": changelist.get_query_string(
                remove=[self.lookup_kwarg, self.lookup_kwarg_isnull]
            ),
            "display": _("All"),
        }
        none_title = ""

        # self.field.flatchoices helyett self.flatchoices
        for lookup, title in self.flatchoices:
            if lookup is None:
                none_title = title
                continue
            yield {
                "selected": self.lookup_val is not None
                and str(lookup) in self.lookup_val,
                "query_string": changelist.get_query_string(
                    {self.lookup_kwarg: lookup}, [self.lookup_kwarg_isnull]
                ),
                "display": title,
            }
        if none_title:
            yield {
                "selected": bool(self.lookup_val_isnull),
                "query_string": changelist.get_query_string(
                    {self.lookup_kwarg_isnull: "True"}, [self.lookup_kwarg]
                ),
                "display": none_title,
            }


# class CsoportDropdownFilter(AltalanosDropdownFilter):
    # """
    # PRJ-MVP csoportelemek "Csoport" szuroje
    # # azert lehet ra szukseg, mert nincs "Csoportok" model_admin, ezert a "generate_select2_filter" nem hasznalhato
    # """

    # def lookups(self, request, model_admin):
        # queryset = PrMvpCsop.objects.order_by('csoport_rnev')
        # results = [(str(res.csoport_id), res.csoport_rnev) for res in queryset]
        # return results

class CsoportDropdownFilter(RelatedDropdownFilter):
    """
    PRJ-MVP csoportelemek "Csoport" szuroje
    # azert lehet ra szukseg, mert nincs "Csoportok" model_admin, ezert a "generate_select2_filter" nem hasznalhato
    """

    def field_admin_ordering(field, request, model_admin):
        return ['csoport_rnev']


class OverrideDropdownFilter(AltalanosDropdownFilter):
    """
    specialis ChoiceDropdownFilter, ahol bizonyos mezot jelenitunk meg a default helyett
    pl. ER azonosito (ER terulet helyett)
    """

    # az admin.py-ben a model_adminba be kell rakni a get_dropdown_settings() fv-t
    # a get_dropdown_settings() fv adja meg az uj title-t es choices-t

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.title, self.flatchoices = model_admin.get_dropdown_settings()


# -----------------------------------------------------------------
# osszetartozo filterek, egyutt "hierarchical select"-et hoznak letre
# valojaban nincs hierarchia, kolcsonos fuggesben vannak  egymastol
# pl. ER kivalasztasa leszukiti a projekteket, de PR kivalasztasa leszukiti az ER-okat
# a "parameter_name"-ek kerulnek a requestbe, a tobbi filterben ezek a "related_parameter_name"-ek
# a related_filter_parameters mutatja, h mely mas filterektol fugg az adott filter
# parameter names: ert, prj, mvp, felmerok, jkonyezok
# -----------------------------------------------------------------

parameter_names = {
    'ER': 'ert', 
    'PR': 'prj__prj_id__exact', 
    'MVP': 'mvp__mvp_id__exact', 
    'felmero': ['faasz_felmero__exact', 'ujcs_felmero__exact', 'anov_felmero__exact', 'foto_felmero__exact', 'megj_felmero__exact', 'tip_felmero__exact'], 
    'jkonyvezo': ['faasz_jkonyvezo__exact', 'ujcs_jkonyvezo__exact', 'anov_jkonyvezo__exact'], 
    'sorszam': ['faasz_adatlap_ssz__exact', 'ujcs_adatlap_ssz__exact', 'anov_adatlap_ssz__exact', 'foto_adatlap_ssz__exact', 'megj_adatlap_ssz__exact', 'tip_adatlapssz_ssz__exact' ]}

class ERListFilter(SimpleDropdownFilter):
    """
    ER-ok listaja szureshez ott, ahol nincs ert mezo, de prj van -> prj-en keresztul mukodik
    pl. Jegyzokonyv
    related filters: prj, , mvp, felmero, jkonyvezo, adatlap sorszama (ezek barmelyikenek kivalasztasa a szuroben megjeleno elemeket szukiti)
    dependent filters: prj, mvp, felmero, jkonyvezo, adatlap sorszama (ezek mindegyike valtozik a kivalasztott ER szerint)
    """
    # Human-readable title which will be displayed in the right admin sidebar just above the filter options.
    title = 'Erdőterület'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = parameter_names['ER']
    related_filter_parameters = {'PR': parameter_names['PR'], 'JK': parameter_names['felmero'] + parameter_names['jkonyvezo'] + parameter_names['sorszam'] + [parameter_names['MVP']]}

    def lookups(self, request, model_admin):
        """
        return list of tuples
        ebbol jon letre a sidebar admin filter tartalma
        """
        # megadni a kiindulasi listat, figyelembe veve a szerepkorok szerinti jogosultsagokat
        qs = model_admin.get_relevant_ERs(request)

        # beallitani a fuggeseket a tobbi szurotol
        qs = self.get_complex_filter(request, qs)
        res = [(x.pk, str(x)) for x in qs]
        
        return res
   
    def get_complex_filter(self, request, qs):

        # ha van valasztott projekt, csak az ahhoz tartozo ER-ot mutassa
        if self.related_filter_parameters['PR'] in request.GET:
            ert_id = Project.objects.get(pk=request.GET[self.related_filter_parameters['PR']]).prj_ert_id
            qs = qs.filter(pk=ert_id)

        # ER-ok szurese mvp, felmero, jegyzokonyvezo es sorszam alapjan prj-en keresztul (a Jegyzokonyvnek nincs ert-mezoje)
        if any(szm_parameter in request.GET for szm_parameter in self.related_filter_parameters['JK']):
            for szm_parameter in self.related_filter_parameters['JK']:
                if szm_parameter in request.GET:
                    szm_id = request.GET[szm_parameter]
                    szm_paramname = szm_parameter[:-7] # pl. anov_felmero
                    prj_ids = Jegyzokonyv.objects.filter(**{szm_paramname:szm_id}).distinct().values_list('prj_id', flat=True)
                    ert_ids = Project.objects.filter(pk__in=prj_ids).values_list('prj_ert_id', flat=True)
                    qs = qs.filter(pk__in=ert_ids)       
        return qs

    def queryset(self, request, queryset):
        """
        return queryset
        ez alapjan mukodik a filter az oldalon, ezzel szuri a fo listat
        """
        if self.value():
            # projektek a kivalasztott ER-rel
            prjs = Project.objects.filter(prj_ert=self.value()).values_list('prj_id', flat=True)
            # elemek, ahol a prj mezo erteke a prjs-ben van, vagyis a kivalasztott ER-hez tartozo elemek
            return queryset.filter(prj__in=prjs)
        return queryset

class DependentDropdownFilter(RelatedDropdownFilter):
    """
    "hierarchical select" also szint, be lehet allitani fuggest mas filterektol
    minta: https://medium.com/elements/getting-the-most-out-of-django-admin-filters-2aecbb539c9a

    """
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.related_model = get_model_from_relation(field)
        super().__init__(field, request, params, model, model_admin, field_path)
    
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'parameter_name'

    # Custom attributes, a parameter neve az url-ben es a request-ben, amitol fugg a szuro (ld. ERListFilter parameter_name)
    related_filter_parameter = ''

    def has_output(self):
        return True

    def field_choices(self, field, request, model_admin):
        """
        returns list of tuples
        beallitja a szuro lehetseges ertekeit
        """

        ordering = self.field_admin_ordering(field, request, model_admin)
        qs = self.get_default_qs(request, model_admin)
        if ordering:
            qs = qs.order_by(*ordering)
        
        # beallitani a fuggeseket a felsobb szuroktol
        qs = self.get_complex_filter(request, qs)
        res = [(x.pk, str(x)) for x in qs]

        # ha mar van kivalasztott elem a szuroben, mutassa
        # 24-09-27: mar felesleges, de vissza lehet tenni, ha kellene
        # res = self.show_selected_item(request, res)
        return res
    
    def get_default_qs(self, request, model_admin):
        return self.related_model._default_manager
    
    def get_complex_filter(self, request, qs):
        """
        modositja a query-t a fuggesek szerint
        """
        return qs.all()

    def show_selected_item(self, request, res):
        """
        ha van valasztott ertek, de mar nem relevans, beteszi az ertekek koze (kulonben nem latszik)
        mar sehol sem fordul elo, mert mindenki szur mindenkit, de meghagyom
        """
        if self.parameter_name in request.GET:
            selected_id = request.GET[self.parameter_name]
            selected_name = str(self.related_model._default_manager.get(pk=selected_id))
            if (int(selected_id), selected_name) not in res:
                res = [(int(selected_id), '(hibásan jelölt) ' + selected_name)] + res
        return res


class ProjectRelatedByER(DependentDropdownFilter):
    """
    projektek szuro-listaja Jegyzokonyveknel
    related filters: er, mvp, felmero, jkonyvezo, adatlap sorszama
    dependent filters: er, mvp, felmero, jkonyvezo, adatlap sorszama
    """
    parameter_name = parameter_names['PR']
    related_filter_parameters = {'ER': parameter_names['ER'], 'JK': parameter_names['felmero'] + parameter_names['jkonyvezo'] + parameter_names['sorszam'] + [parameter_names['MVP']]}
    
    def get_default_qs(self, request, model_admin):
        return model_admin.get_relevant_prjs(request)
    
    def get_complex_filter(self, request, qs):
        nincs_szuro = True
        
        # prj-ek szurese a kivalasztott ER alapjan
        if self.related_filter_parameters['ER'] in request.GET:
            nincs_szuro = False
            qs = qs.filter(prj_ert=request.GET[self.related_filter_parameters['ER']])

        # prj-ek szurese mvp, felmero, jegyzokonyvezo es sorszam alapjan
        if any(szm_parameter in request.GET for szm_parameter in self.related_filter_parameters['JK']):
            nincs_szuro = False
            for szm_parameter in self.related_filter_parameters['JK']:
                if szm_parameter in request.GET:
                    szm_id = request.GET[szm_parameter]
                    szm_paramname = szm_parameter[:-7] # pl. anov_felmero
                    prj_ids = Jegyzokonyv.objects.filter(**{szm_paramname:szm_id}).distinct().values_list('prj_id', flat=True)
                    qs = qs.filter(pk__in=prj_ids)
        if nincs_szuro:
            qs = qs.all()
        return qs


class MVPRelatedByProject(DependentDropdownFilter):
    """
    mvp-k szuro-listaja Jegyzokonyveknel
    related filters: er, pr, felmero, jkonyvezo, adatlap sorszama
    dependent filters: er, pr, felmero, jkonyvezo, adatlap sorszama
    az mvp-nek nincs prj-mezoje, ezert a kozos ER-on keresztul kell szurni
    """

    parameter_name = parameter_names['MVP']
    related_filter_parameters = {'ER': parameter_names['ER'], 'PR': parameter_names['PR'], 'JK': parameter_names['felmero'] + parameter_names['jkonyvezo'] + parameter_names['sorszam']}

    
    def get_complex_filter(self, request, qs):
        nincs_szuro = True
        # ha van kivalasztott ER, arra szurjuk az mvp-ket
        if self.related_filter_parameters['ER'] in request.GET:
            ert_id=request.GET[self.related_filter_parameters['ER']]
            qs = qs.filter(ert=ert_id)
            nincs_szuro = False

        # ha csak prj van kivalasztva, a kozos ER-on keresztul kell szurni az mvp-ket, mert az mvp-nek nincs prj-mezoje
        if self.related_filter_parameters['ER'] not in request.GET and self.related_filter_parameters['PR'] in request.GET:
            ert_nev = Project.objects.get(pk=request.GET[self.related_filter_parameters['PR']]).prj_ert
            qs = qs.filter(ert=ert_nev)
            nincs_szuro = False

        # ha van kivalasztott felmero, jegyzokonyvezo vagy sorszam, arra is szurjuk az mvp-ket
        if any(szm_parameter in request.GET for szm_parameter in self.related_filter_parameters['JK']):
            nincs_szuro = False
            for szm_parameter in self.related_filter_parameters['JK']:
                if szm_parameter in request.GET:
                    szm_id = request.GET[szm_parameter]
                    szm_paramname = szm_parameter[:-7] # pl. anov_felmero
                    mvp_ids = Jegyzokonyv.objects.filter(**{szm_paramname:szm_id}).distinct().values_list('mvp_id', flat=True)
                    qs = qs.filter(pk__in=mvp_ids)
                    
        if nincs_szuro:
            qs = qs.all()
        return qs
    
    def get_default_qs(self, request, model_admin):
        # csak a relevans ER-okhoz tartozo MVP-ket mutassa
        ert_ids = model_admin.get_relevant_ERs(request).values_list('ert_id', flat=True)
        return self.related_model._default_manager.filter(ert__in=ert_ids).order_by('mvp_azo')

class JegyzokonyvDropdownFilter(AltalanosDropdownFilter):
    """
    jegyzokony-mezok (adatlap sorszama, felmero, jkonyvezo) szuro-listaja Jegyzokonyveknel
    related filters: er, pr, mvp (+ {felmero, jkonyvezo, sorszam}-bol 2)

    # csak azokat a jegyzokonyveket (ill. a beallitott mezo ertekeit) mutatja a szuroben, amik egy kivalasztott projekthez es/vagy mvp-hez tartoznak
    # pl. FAÁSZ adatlap sorszáma szerinti szuro
    # ha nincs kivalasztott prj/mvp, de van ert, szurunk ER-ra prj-en keresztul (jegyzokonyv: nincs ert-mezo, csak prj)
    """
    
    # a hierarchiaban levo felsobb filterek, amiket vizsgalunk
    related_ER_parameter = parameter_names['ER']
    related_filter_parameters = [parameter_names['PR'], parameter_names['MVP']]

    def get_default_qs(self, request, model_admin):
        """ beallitjuk a filterben megjeleno kezdo listat, relevans projektekre szurve
            self.current_model: Jegyzokonyv
        """
        prjs = model_admin.get_relevant_prjs(request).values_list('prj_id', flat=True)
        return self.current_model.objects.order_by(self.field_name).filter(prj__in=prjs)
    
    def get_filter_settings(self, request, model_admin, queryset):
        """ a felsobb filterek beallitasaival szurjuk a querysetet """
        ER_kell = True
        
        if 'ssz' in self.field_path:
            related_filter_parameters = self.related_filter_parameters + parameter_names['felmero'] + parameter_names['jkonyvezo']
        elif 'felmero' in self.field_path:
            related_filter_parameters = self.related_filter_parameters + parameter_names['sorszam'] + parameter_names['jkonyvezo']
        elif 'jkonyvezo' in self.field_path:
            related_filter_parameters = self.related_filter_parameters + parameter_names['sorszam'] + parameter_names['felmero']

        for related_filter_parameter in related_filter_parameters:
            if related_filter_parameter in request.GET:
                ER_kell = False
                try:
                    kwargs.update({related_filter_parameter: request.GET[related_filter_parameter]})
                except UnboundLocalError:
                    kwargs = {related_filter_parameter: request.GET[related_filter_parameter]}
                queryset = queryset.filter(**kwargs)
        
        # ha nincs prj v mvp beallitva, ER szerinti projektek alapjan szuri a jegyzokonyveket
        if ER_kell:
            if self.related_ER_parameter in request.GET:
                prjs = model_admin.get_relevant_prjs(request).values_list('prj_id', flat=True).filter(prj_ert=request.GET[self.related_ER_parameter])
                queryset = queryset.filter(prj__in=prjs)

        return queryset

        
    
class SorszamDropdownFilter(JegyzokonyvDropdownFilter):
    """
    adatlap-sorszam szuro-listaja Jegyzokonyveknel
    related filters: er, pr, mvp, felmero, jkonyvezo
    dependent filters: er, pr, mvp, felmero, jkonyvezo

    # csak azokat a sorszamokat mutatja a szuroben, amik egy kivalasztott projekthez es/vagy mvp-hez ill. ert-hez tartoznak
    # felmero es jkonyvezo is leszuri
    # pl. FAÁSZ adatlap sorszáma szerinti szuro
    """
    
    #related_filter_parameters = [parameter_names['PR'], parameter_names['MVP']] + parameter_names['felmero'] + parameter_names['jkonyvezo']

    def lookups(self, request, model_admin):
        # sorszamok a relevans jegyzokonyvekben
        queryset = self.get_default_qs(request, model_admin).values(self.field_name).distinct()

        # itt vizsgaljuk a felsobb filterek beallitasait
        queryset = self.get_filter_settings(request, model_admin, queryset)

        # letrehozzuk a listat, ami a szuroben latszik
        results = [(v[self.field_name], 'Nincs') if v[self.field_name]=="" else (v[self.field_name], v[self.field_name]) for v in queryset]
        return results


class FelmeroDropdownFilter(JegyzokonyvDropdownFilter):
    """
    felmero, jkonyvezo szuro-listaja Jegyzokonyveknel
    related filters: er, pr, mvp, sorszam + felmero/jkonyvezo
    dependent filters: er, pr, mvp + felmero/jkonyvezo

    # csak azokat a szemelyeket mutatja a szuroben, akik egy kivalasztott projekthez es/vagy mvp-hez ill. ert-hez tartoznak
    # adatlap sorszama es felmero/jkonyvezo is leszuri
    # pl. FAÁSZ felmérő szerinti szuro
    """

    #related_filter_parameters = [parameter_names['PR'], parameter_names['MVP']] + parameter_names['sorszam']
    
    def lookups(self, request, model_admin):
        # szemely idk a relevans jegyzokonyvekben
        queryset = self.get_default_qs(request, model_admin).values_list(self.field_name, flat=True)

        # itt vizsgaljuk a felsobb filterek beallitasait
        queryset = self.get_filter_settings(request, model_admin, queryset)

        # letrehozzuk a listat, ami a szuroben latszik
        persons = Person.objects.order_by('szm_rnev').values('szm_id', 'szm_rnev').filter(szm_id__in=queryset)
        PERSON_CHOICES = [(person['szm_id'], person['szm_rnev']) for person in persons]
        return PERSON_CHOICES

