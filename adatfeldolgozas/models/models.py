from django.db import models
from django.core.validators import  MinValueValidator, MaxValueValidator

from decimal import Decimal

from erhtv.models.models import Jegyzokonyv, Taxon, Status, SamplingPoint
from adatfeldolgozas.models.seged_models import XLek, XSzh, XEga, XKrh, XVzh, XAdatSta

import logging
logger = logging.getLogger(__name__)

def get_taxonnev(latinnev):
    """
    auktor nelkuli taxonnevet adja vissza
    """
    txn = Taxon.objects.get(latinnev=latinnev)
    return f'{txn.genus} {txn.species}'
    

class JegyzokonyvFAA(Jegyzokonyv):
    def __str__(self):
        return f'FAÁSZ jegyzőkönyv (ID: {self.jkv_adat_id}) - FAA'
    class Meta:
        proxy = True
        verbose_name = "FAA adatok"
        verbose_name_plural = 'FAA adatlapok'

class JegyzokonyvFAEazon(Jegyzokonyv):
    def __str__(self):
        return f'FAÁSZ jegyzőkönyv (ID: {self.jkv_adat_id}) - FAE AZON'
    class Meta:
        proxy = True
        verbose_name = "FAE AZON adatok"
        verbose_name_plural = 'FAE AZON fák azonosítása'

class JegyzokonyvFAEadat(Jegyzokonyv):
    def __str__(self):
        return f'FAÁSZ jegyzőkönyv (ID: {self.jkv_adat_id}) - FAE egyesfa'
    class Meta:
        proxy = True
        verbose_name = "FAE egyesfa adatok"
        verbose_name_plural = 'FAE egyesfa adatlapok'

class JegyzokonyvFHF(Jegyzokonyv):
    def __str__(self):
        return f'FAÁSZ jegyzőkönyv (ID: {self.jkv_adat_id}) - FHF'
    class Meta:
        proxy = True
        verbose_name = "FHF adatok"
        verbose_name_plural = 'FHF adatlapok'

class JegyzokonyvUJCS(Jegyzokonyv):
    def __str__(self):
        return f'UJCS jegyzőkönyv (ID: {self.jkv_adat_id})'
    class Meta:
        proxy = True
        verbose_name = "UJCS adatok"
        verbose_name_plural = 'UJCS adatlapok'

class JegyzokonyvANOV(Jegyzokonyv):
    def __str__(self):
        return f'ANOV jegyzőkönyv (ID: {self.jkv_adat_id})'
    class Meta:
        proxy = True
        verbose_name = "ANOV adatok"
        verbose_name_plural = 'ANOV adatlapok'

class FaaAdat(models.Model):
    jkv_adat = models.ForeignKey(Jegyzokonyv, models.DO_NOTHING)
    faa_adat_id = models.AutoField(primary_key=True)
    zarodas_ossz = models.SmallIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Záródás (%)')
    boritas_flkszint = models.SmallIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Felső koronaszint borítása (%)')
    boritas_alkszint = models.SmallIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Alsó koronaszint borítása (%)')
    boritas_csjszint = models.SmallIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Cserjeszint borítás (%)')
    boritas_gyszint = models.SmallIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Gyepszint borítás (%)')
    lekesseg = models.ForeignKey('XLek', models.DO_NOTHING, limit_choices_to=~models.Q(lek_id__in = [8]), verbose_name='Lékesség')
    faa_adat_kieg = models.CharField(max_length=500, blank=True, verbose_name='Megyjegyzések')

    def __str__(self):
        return str(self.faa_adat_id)

    class Meta:
        managed = False
        db_table = 'd_faa_adat'
        verbose_name = "FAA adatlap"
        verbose_name_plural = 'FAA adatlapok'

class FaeAdat(models.Model):
    jkv_adat = models.ForeignKey(Jegyzokonyv, models.DO_NOTHING)
    fae = models.ForeignKey('FaeAzo', models.DO_NOTHING, verbose_name="A faegyed azonosítója")
    fae_adat_id = models.AutoField(primary_key=True)
    txn = models.ForeignKey(Taxon, models.DO_NOTHING, verbose_name="A faegyed fajneve")
    fae_txn_status = models.ForeignKey(Status, models.DO_NOTHING, verbose_name="A meghatározás státusza", default=3)
    dvkvt = models.CharField(max_length=5, blank=True, null=True)
    d130 = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    kerulet = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True, verbose_name="Kerület")
    toatmero = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True, verbose_name="Tőátmérő")
    famagassag = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    csonkmagassag = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    szochelyzet = models.ForeignKey('XSzh', models.DO_NOTHING)
    pluszertek = models.BooleanField()
    egeszseg = models.ForeignKey('XEga', models.DO_NOTHING, verbose_name="Egészségi állapot")
    korhadtsag = models.ForeignKey('XKrh', models.DO_NOTHING, verbose_name="Korhadtság")
    vizhajtasossag = models.ForeignKey('XVzh', models.DO_NOTHING)
    ts_eredet = models.BooleanField()
    or_alak = models.BooleanField()
    df_alak = models.BooleanField()
    fae_adat_kieg = models.CharField(max_length=250, blank=True, null=True)
    transzparencia = models.SmallIntegerField()
    legujabb = models.SmallIntegerField()
    prj_id_aktu = models.IntegerField(blank=True, null=True)
    prj_id_prev = models.IntegerField(blank=True, null=True)
    adat_sta = models.ForeignKey('XAdatSta', models.DO_NOTHING)

    def __str__(self):
        return f'{self.fae_adat_id} - {get_taxonnev(self.txn)}/{self.fae.fae_id}({self.fae.fae_mvp_id})'

    class Meta:
        managed = False
        db_table = 'd_fae_adat'
        verbose_name = "FAE egyesfa"
        verbose_name_plural = 'FAE egyesfák'

class FaeAzo(models.Model):
    mvp = models.ForeignKey(SamplingPoint, models.DO_NOTHING)
    jkv_adat = models.ForeignKey(Jegyzokonyv, models.DO_NOTHING)
    fae_id = models.AutoField(primary_key=True)
    fae_mvp_id = models.SmallIntegerField()
    fae_vtav = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Vízszintes távolság (m)")
    fae_dszog = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Mágneses elhajlás (fok)")
    fae_mdatum = models.DateField(verbose_name="Azonosításkori dátum (é.h.n.)")
    fae_mszog = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True, verbose_name="Mért irányszög (fok)")
    fae_szog = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    fae_txn = models.ForeignKey(Taxon, models.DO_NOTHING, verbose_name="A faegyed fajneve")
    fae_txn_status = models.ForeignKey(Status, models.DO_NOTHING, verbose_name="A meghatározás státusza", default=3)
    d130_azonositaskor = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Átmérő (cm)", help_text="Átmérő helyett mindig a <strong>kerületet</strong> adjuk meg cm-ben! (Az átmérő értéke mentéskor automatikusan számítódik a kerületből.)")
    eov_dy = models.FloatField(blank=True, null=True)
    eov_dx = models.FloatField(blank=True, null=True)
    nincsrfi = models.SmallIntegerField(verbose_name="Lokalizálatlan fa", default=0)
    indoklas = models.CharField(max_length=500, blank=True, verbose_name="Indoklás")
    fae_adatokszama = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'(ID: {self.fae_id}) - Ssz: {self.fae_mvp_id}, {get_taxonnev(self.fae_txn)}'
    
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self._meta.local_fields = [f for f in self._meta.local_fields if f.name not in ('fae_szog', 'eov_dy', 'eov_dx', 'fae_adatokszama')]
        if not self.mvp_id:
            self.mvp_id = self.jkv_adat.mvp_id
        if not self.fae_mvp_id:
            self.fae_mvp_id = FaeAzo.objects.filter(jkv_adat=self.jkv_adat).order_by('-fae_mvp_id').values('fae_mvp_id')[0]['fae_mvp_id'] + 1
        # atmero helyett a bevitt adat a kerulet
        # ha uj elem, vagy valtozott az atmero, at kell szamolni
        if not self.fae_id or FaeAzo.objects.get(fae_id=self.fae_id).d130_azonositaskor != self.d130_azonositaskor:
            self.d130_azonositaskor = self.d130_azonositaskor/Decimal('3.141592653589793')
        super(FaeAzo, self).save(force_insert, force_update, using, update_fields)
    
    class Meta:
        managed = False
        db_table = 'd_fae_azo'
        unique_together = (('mvp', 'fae_mvp_id'),)
        verbose_name = "FAE"
        verbose_name_plural = 'FAE azonosítók'

class FhfAdat(models.Model):
    jkv_adat = models.ForeignKey(Jegyzokonyv, models.DO_NOTHING)
    fhf_adat_id = models.AutoField(primary_key=True)
    fhf_txn = models.ForeignKey(Taxon, models.DO_NOTHING, verbose_name="A fekvő holtfa fajneve")
    fhf_txn_status = models.ForeignKey(Status, models.DO_NOTHING, verbose_name="A meghatározás státusza", default=3)
    atmero = models.SmallIntegerField(verbose_name="Átmérő (cm)")
    korhadtsag = models.ForeignKey('XKrh', models.DO_NOTHING, verbose_name="Korhadtság")
    fhf_adat_megj = models.CharField(max_length=250, blank=True, verbose_name="Megjegyzés")

    def __str__(self):
        return f'{self.fhf_adat_id} - {get_taxonnev(self.fhf_txn)} / {self.atmero}cm'

    class Meta:
        managed = False
        db_table = 'd_fhf_adat'
        verbose_name = "FHF adatrekord"
        verbose_name_plural = 'FHF adatrekordok'

class UcsAdat(models.Model):
    jkv_adat = models.ForeignKey(Jegyzokonyv, models.DO_NOTHING)
    ucs_adat_id = models.AutoField(primary_key=True)
    ucs_txn = models.ForeignKey(Taxon, models.DO_NOTHING, verbose_name="Taxon név")
    ucs_txn_status = models.ForeignKey(Status, models.DO_NOTHING, verbose_name="Taxon státusz", default=3)
    uju_ohjtszam = models.SmallIntegerField(verbose_name="UJU (50-130 cm) összes hajtás")
    uju_rhjtszam = models.SmallIntegerField(verbose_name="UJU ... ebből rágott hajtás")
    uju_adatsor = models.CharField(max_length=250, verbose_name="UJU kiegészítés")
    uju_van = models.BooleanField(default=True, verbose_name="UJU szintben VAN")
    cse_ohjtszam = models.SmallIntegerField(verbose_name="CSJE (>130 cm) összes hajtás")
    cse_rhjtszam = models.SmallIntegerField(verbose_name="CSJE ... ebből rágott hajtás")
    cse_adatsor = models.CharField(max_length=250, verbose_name="CSJE kiegészítés")
    cse_van = models.BooleanField(default=True, verbose_name="CSJE szintben VAN")
    adat_sta = models.ForeignKey('XAdatSta', models.DO_NOTHING, default=1)
    ucs_adatokszama = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.ucs_adat_id} - {get_taxonnev(self.ucs_txn)} / {self.uju_ohjtszam} / {self.uju_rhjtszam}'

    class Meta:
        managed = False
        db_table = 'e_ucs_adat'
        verbose_name = "UJCS adatrekord"
        verbose_name_plural = 'UJCS adatrekordok'

class FNovAdat(models.Model):
    jkv_adat = models.ForeignKey(Jegyzokonyv, models.DO_NOTHING)
    nov_adat_id = models.AutoField(primary_key=True)
    nov_txn = models.ForeignKey(Taxon, models.DO_NOTHING, verbose_name="Taxon név")
    nov_txn_status = models.ForeignKey(Status, models.DO_NOTHING, default=3, verbose_name="Taxon státusz")
    nov_gyakorisag = models.SmallIntegerField(blank=True, null=True, verbose_name="Alminta gyakoriság")
    nov_elofordul = models.BooleanField(default=False, verbose_name="Gyak=0, DE előfordul")
    nov_boritas = models.DecimalField(max_digits=8, decimal_places=1, blank=True, null=True, verbose_name="Taxon borítás (%)")
    nov_ohjtszam = models.SmallIntegerField(blank=True, null=True, verbose_name="Taxon hajtásszám")
    nov_van = models.BooleanField(default=True, verbose_name="Taxon van")
    nov_adatsor = models.CharField(max_length=250, default="Kiegészítő adat...", verbose_name="Kiegészítő adatsor")
    adat_sta = models.ForeignKey('XAdatSta', models.DO_NOTHING, default=1)
    nov_adatokszama = models.IntegerField(default=1)
    # fl01 = models.BooleanField()
    # fl02 = models.BooleanField()
    # fl03 = models.BooleanField()
    # fl04 = models.BooleanField()
    # fl05 = models.BooleanField()
    # fl06 = models.BooleanField()
    # fl07 = models.BooleanField()
    # fl08 = models.BooleanField()
    # fl09 = models.BooleanField()
    # fl10 = models.BooleanField()
    # fl11 = models.BooleanField()
    # fl12 = models.BooleanField()
    # fl13 = models.BooleanField()
    # fl14 = models.BooleanField()
    # fl15 = models.BooleanField()
    # fl16 = models.BooleanField()
    # fl17 = models.BooleanField()
    # fl18 = models.BooleanField()
    # fl19 = models.BooleanField()
    # fl20 = models.BooleanField()
    # fl21 = models.BooleanField()
    # fl22 = models.BooleanField()
    # fl23 = models.BooleanField()
    # fl24 = models.BooleanField()
    # fl25 = models.BooleanField()
    # fl26 = models.BooleanField()
    # fl27 = models.BooleanField()
    # fl28 = models.BooleanField()
    # fl29 = models.BooleanField()
    # fl30 = models.BooleanField()

    def __str__(self):
        return f'{self.nov_adat_id} - {get_taxonnev(self.nov_txn)} / {self.nov_ohjtszam}'

    class Meta:
        managed = False
        db_table = 'f_nov_adat'
        verbose_name = "ANOV adatrekord"
        verbose_name_plural = 'ANOV adatrekordok'
