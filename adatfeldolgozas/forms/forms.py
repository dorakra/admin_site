from django import forms
#from django.core.exceptions import ValidationError

from erhtv.models.models import Project, Person, Permission, Jegyzokonyv
from adatfeldolgozas.models.models import FaaAdat, FaeAdat, FaeAzo, FhfAdat, FNovAdat


class RadioSelect(forms.RadioSelect):
    pass

class JegyzokonyvModAdminForm(forms.ModelForm):
    """
    Jegyzokonyvek felmeroinek es jegyzokonyvezoinek szukitese projekt szerint, ill. csak a NEM adatfeldolgozokat mutassa
    NEM adatfelfolgozo: akinek nincs szerkesztesi joga semmire, de a projekthez tartozik
    """
    class Meta:
        model = Jegyzokonyv
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(JegyzokonyvModAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            prj_id = Project.objects.get(prj_nev=instance.prj).prj_id
            # a projekthez tartozo nem adatfeldolgozo szerepkorok szemelyei
            szerepkor_queryset = Permission.objects.filter(prj=prj_id, faasz_szerk=0, ujcs_szerk=0, anov_szerk=0, dfoto_szerk=0, megj_szerk=0, tterm_szerk=0, tip_szerk=0, mvp_szerk=0, tgdrk_szerk=0, prjerh_szerk=0, txnk_szerk=0, kesz_szerk=0).values('szm').distinct()
            szm_ids = [szerepkor['szm'] for szerepkor in szerepkor_queryset]
            persons = Person.objects.filter(pk=1).values('szm_id', 'szm_rnev') | Person.objects.filter(pk__in=szm_ids).order_by('szm_rnev').values('szm_id', 'szm_rnev')
            PERSON_CHOICES = [(person['szm_id'], person['szm_rnev']) for person in persons]
            for fieldname in self.fields:
                if fieldname[-7:] in ('felmero', 'onyvezo'):
                    self.fields[fieldname].widget.choices = PERSON_CHOICES

class FaaAdatInlineForm(forms.ModelForm):
    
    class Meta:
        model = FaaAdat
        fields = '__all__'
        widgets = {
            'lekesseg': forms.RadioSelect#(attrs={'class': 'radio horizontal'})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        zarodas_ossz = cleaned_data.get("zarodas_ossz") if cleaned_data.get("zarodas_ossz") else 0
        boritas_flkszint = cleaned_data.get("boritas_flkszint") if cleaned_data.get("boritas_flkszint") else 0
        boritas_alkszint = cleaned_data.get("boritas_alkszint") if cleaned_data.get("boritas_alkszint") else 0

        if zarodas_ossz < boritas_flkszint + boritas_alkszint:
            msg = "A felső és az alsó lomkoronaszint borításának összege nem haladhatja meg a záródást."
            self.add_error("zarodas_ossz", msg)
            self.add_error("boritas_flkszint", '')
            self.add_error("boritas_alkszint", '')
    
    # tovabbi validalas a models.py-ben

class AnovAdatInlineForm(forms.ModelForm):
    
    class Meta:
        model = FNovAdat
        fields = '__all__'
   
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('jkv_adat') and cleaned_data.get('nov_gyakorisag'):
            if cleaned_data.get('jkv_adat').anov_modszertan_id == 1 and cleaned_data.get('nov_gyakorisag') > 30:
                self.add_error("nov_gyakorisag", 'GY-30 módszertan esetén az alminta-gyakoriság maximuma 30')
            if cleaned_data.get('jkv_adat').anov_modszertan_id == 6 and cleaned_data.get('nov_gyakorisag') > 8:
                self.add_error("nov_gyakorisag", 'GY-08 módszertan esetén az alminta-gyakoriság maximuma 8')
    
