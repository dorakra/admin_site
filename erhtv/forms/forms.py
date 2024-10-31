from django import forms

from erhtv.models.models import Taxon

class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
    csv_file.label = "CSV v. TXT file"

class TaxonModAdminForm(forms.ModelForm):
    """
    taxonvalaszto mezok (genus, csalad, ...)
    """
    class Meta:
        model = Taxon
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(TaxonModAdminForm, self).__init__(*args, **kwargs)
        def get_valuelist(field_name):
            all_values = Taxon.objects.exclude(**{field_name: None}).order_by(field_name).values(field_name).distinct()
            return [(v[field_name], v[field_name]) for v in all_values]
        
        choice_fields = ['csalad', 'genus', 'eletforma', 'genusvalaszto']
        for field_name in choice_fields:
            self.fields[field_name] = forms.ChoiceField(choices = get_valuelist(field_name))
