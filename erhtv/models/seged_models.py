# Az adatbazisbol generalt egyeb modellek, amiket a models hasznal, de az admin feluletre nem kerulnek.
from django.db import models


class XModAnov(models.Model):
    mod_anov_id = models.AutoField(primary_key=True)
    mod_anov_rnev = models.CharField(max_length=5)
    mod_anov_nev = models.CharField(max_length=25)
    mod_anov_leiras = models.CharField(max_length=4000)
    anov_mintaterulet = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    anov_almintakor_te = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    anov_almintakor_sz = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.mod_anov_rnev

    class Meta:
        managed = False
        db_table = 'x_mod_anov'


class XModFaa(models.Model):
    mod_faa_id = models.AutoField(primary_key=True)
    mod_faa_rnev = models.CharField(max_length=5)
    mod_faa_nev = models.CharField(max_length=25)
    mod_faa_leiras = models.CharField(max_length=4000)
    faa_hatokor_szorzo = models.DecimalField(max_digits=3, decimal_places=1)

    def __str__(self):
        return self.mod_faa_nev

    class Meta:
        managed = False
        db_table = 'x_mod_faa'


class XModFae(models.Model):
    mod_fae_id = models.AutoField(primary_key=True)
    mod_fae_rnev = models.CharField(max_length=5)
    mod_fae_nev = models.CharField(max_length=25)
    mod_fae_leiras = models.CharField(max_length=4000)
    faasz_mintakor_r = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    faasz_szszproba_k = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)

    def __str__(self):
        return self.mod_fae_nev

    class Meta:
        managed = False
        db_table = 'x_mod_fae'


class XModFhf(models.Model):
    mod_fhf_id = models.AutoField(primary_key=True)
    mod_fhf_rnev = models.CharField(max_length=5)
    mod_fhf_nev = models.CharField(max_length=25)
    mod_fhf_leiras = models.CharField(max_length=4000)
    faasz_fhflinea_h = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)

    def __str__(self):
        return self.mod_fhf_nev

    class Meta:
        managed = False
        db_table = 'x_mod_fhf'


class XModFoto(models.Model):
    mod_foto_id = models.AutoField(primary_key=True)
    mod_foto_rnev = models.CharField(max_length=5)
    mod_foto_nev = models.CharField(max_length=25)
    mod_foto_leiras = models.CharField(max_length=4000)

    def __str__(self):
        return self.mod_foto_nev

    class Meta:
        managed = False
        db_table = 'x_mod_foto'


class XModMegj(models.Model):
    mod_megj_id = models.AutoField(primary_key=True)
    mod_megj_rnev = models.CharField(max_length=5)
    mod_megj_nev = models.CharField(max_length=25)
    mod_megj_leiras = models.CharField(max_length=4000)
    megj_param1 = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)

    def __str__(self):
        return self.mod_megj_nev

    class Meta:
        managed = False
        db_table = 'x_mod_megj'


class XModMvpk(models.Model):
    mod_mvpk_id = models.AutoField(primary_key=True)
    mod_mvpk_rnev = models.CharField(max_length=5)
    mod_mvpk_nev = models.CharField(max_length=25)
    mod_mvpk_leiras = models.CharField(max_length=4000)
    mod_mvpk_param1 = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)

    def __str__(self):
        return self.mod_mvpk_nev

    class Meta:
        managed = False
        db_table = 'x_mod_mvpk'


class XModTerm(models.Model):
    mod_term_id = models.AutoField(primary_key=True)
    mod_term_rnev = models.CharField(max_length=5)
    mod_term_nev = models.CharField(max_length=25)
    mod_term_leiras = models.CharField(max_length=4000)
    term_param1 = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)

    def __str__(self):
        return self.mod_term_nev

    class Meta:
        managed = False
        db_table = 'x_mod_term'


class XModTgdk(models.Model):
    mod_tgdk_id = models.AutoField(primary_key=True)
    mod_tgdk_rnev = models.CharField(max_length=5)
    mod_tgdk_nev = models.CharField(max_length=25)
    mod_tgdk_leiras = models.CharField(max_length=4000)
    mod_tgdk_param1 = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)

    def __str__(self):
        return self.mod_tgdk_nev

    class Meta:
        managed = False
        db_table = 'x_mod_tgdk'


class XModTipi(models.Model):
    mod_tip_id = models.AutoField(primary_key=True)
    mod_tip_rnev = models.CharField(max_length=5)
    mod_tip_nev = models.CharField(max_length=25)
    mod_tip_leiras = models.CharField(max_length=4000)
    tip_param1 = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)

    def __str__(self):
        return self.mod_tip_nev

    class Meta:
        managed = False
        db_table = 'x_mod_tipi'


class XModTszel(models.Model):
    mod_tszel_id = models.AutoField(primary_key=True)
    mod_tszel_rnev = models.CharField(max_length=5)
    mod_tszel_nev = models.CharField(max_length=25)
    mod_tszel_leiras = models.CharField(max_length=4000)
    tszel_param1 = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)

    def __str__(self):
        return self.mod_tszel_nev

    class Meta:
        managed = False
        db_table = 'x_mod_tszel'


class XModUjcs(models.Model):
    mod_ujcs_id = models.AutoField(primary_key=True)
    mod_ujcs_rnev = models.CharField(max_length=5)
    mod_ujcs_nev = models.CharField(max_length=25)
    mod_ujcs_leiras = models.CharField(max_length=4000)
    uju_mintaterulet = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    uju_almintakor_te = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    uju_almintakor_sz = models.SmallIntegerField(blank=True, null=True)
    csj_mintaterulet = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    csj_almintakor_te = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    csj_almintakor_sz = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.mod_ujcs_nev

    class Meta:
        managed = False
        db_table = 'x_mod_ujcs'

