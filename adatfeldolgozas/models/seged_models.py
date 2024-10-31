# Az adatbazisbol generalt egyeb modellek, amiket a models hasznal, de az admin feluletre nem kerulnek.
from django.db import models


class XLek(models.Model):
    lek_id = models.AutoField(primary_key=True)
    lek_rnev = models.CharField(max_length=5)
    lek_nev = models.CharField(max_length=25)
    lek_leiras = models.CharField(max_length=250)

    def __str__(self):
        return self.lek_nev

    class Meta:
        managed = False
        db_table = 'x_lek'

class XSzh(models.Model):
    szh_id = models.AutoField(primary_key=True)
    szh_rnev = models.CharField(max_length=5)
    szh_nev = models.CharField(max_length=25)
    szh_leiras = models.CharField(max_length=250)

    def __str__(self):
        return self.szh_nev

    class Meta:
        managed = False
        db_table = 'x_szh'

class XEga(models.Model):
    ega_id = models.AutoField(primary_key=True)
    ega_rnev = models.CharField(max_length=5)
    ega_nev = models.CharField(max_length=25)
    ega_leiras = models.CharField(max_length=250)

    def __str__(self):
        return f'{self.ega_nev} ({self.ega_rnev})'

    class Meta:
        managed = False
        db_table = 'x_ega'

class XKrh(models.Model):
    krh_id = models.AutoField(primary_key=True)
    krh_rnev = models.CharField(max_length=5)
    krh_nev = models.CharField(max_length=25)
    krh_leiras = models.CharField(max_length=250)

    def __str__(self):
        return self.krh_nev

    class Meta:
        managed = False
        db_table = 'x_krh'

class XVzh(models.Model):
    vzh_id = models.AutoField(primary_key=True)
    vzh_rnev = models.CharField(max_length=5)
    vzh_nev = models.CharField(max_length=25)
    vzh_leiras = models.CharField(max_length=250)

    def __str__(self):
        return self.vzh_nev

    class Meta:
        managed = False
        db_table = 'x_vzh'

class XAdatSta(models.Model):
    adat_sta_id = models.SmallIntegerField(primary_key=True)
    adat_sta_rnev = models.CharField(max_length=10)
    adat_sta_leiras = models.CharField(max_length=250)

    def __str__(self):
        return self.adat_sta_rnev

    class Meta:
        managed = False
        db_table = 'x_adat_sta'







