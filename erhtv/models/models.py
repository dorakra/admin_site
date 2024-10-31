from datetime import datetime

from django.db import models
from erhtv.models.seged_models import XModFaa, XModFae, XModFhf, XModUjcs, XModAnov, XModTerm, XModTszel, XModFoto, XModMegj, XModTipi, XModMvpk, XModTgdk


class Log(models.Model):
    naplo_id = models.AutoField(primary_key=True)
    naplo_datum = models.DateTimeField(verbose_name='Naplóbejegyzés időpontja')
    naplo_szerepkor_id = models.IntegerField(verbose_name='Személy')
    naplo_akc = models.ForeignKey('Action', models.DO_NOTHING, verbose_name='Tevékenység')
    naplo_alkalmazas_azo = models.CharField(max_length=5, default='AdFel')
    naplo_prgresz_azo = models.CharField(max_length=5, default='n. a.')
    naplo_mvp_id = models.IntegerField(default=1, verbose_name='MVP azonosító')

    def __str__(self):
        return f'Napló {self.naplo_id} - {self.naplo_datum:%Y-%m-%d %H:%M}'

    class Meta:
        managed = False
        db_table = 'a_naplo'
        verbose_name = 'Tevékenységnapló'
        verbose_name_plural = 'Tevékenységnaplók'

class Permission(models.Model):
    prj = models.ForeignKey('Project', models.DO_NOTHING, verbose_name='Projekt')
    szm = models.ForeignKey('Person', models.DO_NOTHING, verbose_name='Személy')
    szerepkor_id = models.AutoField(primary_key=True)
    szerepkor = models.CharField(max_length=100, verbose_name='Szerepkör')
    felhasznalo = models.CharField(max_length=15, verbose_name='Felhasználó')
    jelszo = models.CharField(max_length=15, verbose_name='Jelszó')
    mikortol = models.DateField(verbose_name='Mikortól')
    meddig = models.DateField(verbose_name='Meddig')
    YES_NO_CHOICES = [(1, 'Igen'), (0, 'Nem')]
    faasz_szerk = models.SmallIntegerField(verbose_name='FAÁSZ szerkesztő', choices=YES_NO_CHOICES, default=0)
    ujcs_szerk = models.SmallIntegerField(verbose_name='ÚJCS szerkesztő', choices=YES_NO_CHOICES, default=0)
    anov_szerk = models.SmallIntegerField(verbose_name='ANÖV szerkesztő', choices=YES_NO_CHOICES, default=0)
    dfoto_szerk = models.SmallIntegerField(verbose_name='DFOTÓ szerkesztő', choices=YES_NO_CHOICES, default=0)
    megj_szerk = models.SmallIntegerField(verbose_name='MEGJ szerkesztő', choices=YES_NO_CHOICES, default=0)
    tterm_szerk = models.SmallIntegerField(verbose_name='', choices=YES_NO_CHOICES, default=0)
    tip_szerk = models.SmallIntegerField(verbose_name='ERDŐTIPUS szerkesztő', choices=YES_NO_CHOICES, default=0)
    mvp_szerk = models.SmallIntegerField(verbose_name='MVP szerkesztő', choices=YES_NO_CHOICES, default=0)
    tgdrk_szerk = models.SmallIntegerField(verbose_name='', choices=YES_NO_CHOICES, default=0)
    prjerh_szerk = models.SmallIntegerField(verbose_name='ERDŐháló szerkesztő', choices=YES_NO_CHOICES, default=0)
    txnk_szerk = models.SmallIntegerField(verbose_name='TAXONLISTA szerkesztő', choices=YES_NO_CHOICES, default=0)
    kesz_szerk = models.SmallIntegerField(verbose_name='KÉSZ szerkesztő', choices=YES_NO_CHOICES, default=0)

    def __str__(self):
        return self.szerepkor

    class Meta:
        managed = False
        db_table = 'a_szrpkor'
        verbose_name = 'Szerepkör'
        verbose_name_plural = 'Szerepkörök'

class ForestReserve(models.Model):
    HUNGARY = 'HU'
    AUSTRIA = 'AU'
    CZECHIA = 'CZ'
    CROATIA = 'HR'
    ROMANIA = 'RO'
    SLOVAKIA = 'SK'
    SLOVENIA = 'SI'
    SERBIA = 'RS'
    UKRAINE = 'UA'
    COUNTRY_CHOICES = [(HUNGARY, 'Magyarország'), (AUSTRIA, 'Ausztria'), (CZECHIA, 'Csehország'),
                       (CROATIA, 'Horvátország'), (ROMANIA, 'Románia'), (SLOVAKIA, 'Szlovákia'),
                       (SLOVENIA, 'Szlovénia'), (SERBIA, 'Szerbia'), (UKRAINE, 'Ukrajna')]
    EGTAJ_CHOICES = [(0, 'Nincs megadva'),
                     (1, 'Nyugat-Dunántúl'),
                     (2, 'Dél-Dunántúl'),
                     (3, 'Kisalföld'),
                     (4, 'Dunántúli középhegység'),
                     (5, 'Északi középhegység'),
                     (6, 'Nagyalföld löszvidék'),
                     (7, 'Nagyalföld homokvidék'),
                     (8, 'Nagyalföld szikes vidék'),
                     (9, 'Nagyalföld ár- és lápter.'),
                     (51, 'Száva-sík, Szerémség SRB')]

    ert_id = models.AutoField(primary_key=True)
    ert_azo = models.CharField(unique=True, max_length=25, verbose_name='ER azonosító', help_text='az erdőrezervátum azonosítója, pl. ER-56')
    ert_ssz = models.IntegerField(verbose_name='ER sorszám', default=999, help_text='az erdőrezervátum sorszáma, pl. 56')
    ert_nev = models.CharField(max_length=100, verbose_name='ER név', help_text='az erdőrezervátum neve, pl. Kékes Erdőrezervátum')
    ert_orszag = models.CharField(max_length=2, verbose_name='Ország', choices=COUNTRY_CHOICES, default=HUNGARY)
    ert_url = models.CharField(max_length=100, verbose_name='Honlap', default='https://www.erdorezervatum.hu')
    ert_lat_n_fok = models.SmallIntegerField(db_column='ert_lat_n_fok', blank=True, null=True, verbose_name='Szélesség (fok)', default=47, help_text='a földrajzi szélesség és hosszúság fok, perc, másodpercben - <a href="https://www.futas.net/gps/gps-koordinatak-atvaltasa-konvertalasa.php" target="_blank">átváltás decimálisból</a>')  # Field name made lowercase.
    ert_lat_n_perc = models.SmallIntegerField(db_column='ert_lat_n_perc', blank=True, null=True,
                                              verbose_name='Szélesség (perc)',
                                              default='0')  # Field name made lowercase.
    ert_lat_n_mperc = models.SmallIntegerField(db_column='ert_lat_n_mperc', blank=True, null=True,
                                               verbose_name='Szélesség (mperc)',
                                               default='0')  # Field name made lowercase.
    ert_lon_e_fok = models.SmallIntegerField(db_column='ert_lon_e_fok', blank=True, null=True,
                                             verbose_name='Hosszúság (fok)', default='18')  # Field name made lowercase.
    ert_lon_e_perc = models.SmallIntegerField(db_column='ert_lon_e_perc', blank=True, null=True,
                                              verbose_name='Hosszúság (perc)',
                                              default='0')  # Field name made lowercase.
    ert_lon_e_mperc = models.SmallIntegerField(db_column='ert_lon_e_mperc', blank=True, null=True,
                                               verbose_name='Hosszúság (mperc)',
                                               default='0')  # Field name made lowercase.
    novfoldrajz = models.CharField(max_length=25, blank=True, null=True)
    egnagytaj = models.IntegerField(blank=True, null=True, choices=EGTAJ_CHOICES, default=0,
                                    verbose_name='Erdőgazdasági nagytáj')

    def __str__(self):
        return self.ert_nev

    class Meta:
        managed = False
        db_table = 'b_ert'
        verbose_name = 'Erdőrezervátum'
        verbose_name_plural = 'Erdőrezervátumok'

class Project(models.Model):
    MINDKESZ_CHOICES = [(1, 'Minden adatbevitel kész'), (2, 'Még nem kész minden')]
    GENERAL_CHOICES = [(0, 'Tervezett'), (1, 'Kész'), (2, 'Nincs tervezve'), (3, 'Nincs adat'), (4, 'Kimaradt')]
    OTHER_CHOICES = [(0, 'Tervezett'), (1, 'Kész'), (2, 'Nincs tervezve')]

    prj_id = models.AutoField(primary_key=True, verbose_name='PRJ azonosító')
    prj_rnev = models.CharField('Rövid név', unique=True, max_length=25, default='', help_text='rövid megnevezése, pl.: "KEKES_2005-2013"')
    prj_nev = models.CharField("Név", max_length=250, default='', help_text='az ER HTV projekt teljes megnevezése')
    prj_ert = models.ForeignKey('ForestReserve', verbose_name='ER terület',
                                on_delete=models.DO_NOTHING)
    prj_vez = models.ForeignKey('Person', verbose_name='Vezető', on_delete=models.DO_NOTHING)
    prj_ev = models.SmallIntegerField("Vonatkoztatási év", help_text='az ER HTV projekt kezdő éve')
    prj_hanyadikfelmeres = models.CharField("Hányadik felmérés", max_length=10, default='első', help_text='pl. első, második, harmadik ...')
    prj_kovetkezo_ev = models.SmallIntegerField("Következő felmérés éve", default=0)
    prj_sta = models.ForeignKey('Status', verbose_name="Státusz", default=5,
                                on_delete=models.DO_NOTHING)
    prj_leiras = models.CharField("Leírás", max_length=4000, default='', help_text='az ER HTV projekt részletesebb leírása (max. 4000 karakter)')
    prj_url = models.CharField("Honlap", max_length=100, default='https://erdorezervatum.hu')
    prj_elozo_prj_id = models.IntegerField(default=0)
    prj_elozo_faaprj_id = models.IntegerField(default=0)
    prj_elozo_faeprj_id = models.IntegerField(default=0)
    prj_elozo_fhfprj_id = models.IntegerField(default=0)
    prj_elozo_ucsprj_id = models.IntegerField(default=0)
    prj_elozo_cseprj_id = models.IntegerField(default=0)
    prj_elozo_ujuprj_id = models.IntegerField(default=0)
    prj_elozo_novprj_id = models.IntegerField(default=0)
    prj_elozo_tszprj_id = models.IntegerField(default=0)
    prj_elozo_trmprj_id = models.IntegerField(default=0)
    prj_elozo_fotprj_id = models.IntegerField(default=0)
    prj_elozo_mgjprj_id = models.IntegerField(default=0)
    prj_elozo_tipprj_id = models.IntegerField(default=0)
    prj_elozo_mvpprj_id = models.IntegerField(default=0)
    prj_elozo_tgdprj_id = models.IntegerField(default=0)
    prj_erh_terv_kesz = models.SmallIntegerField(default=2)
    prj_flm_terv_kesz = models.SmallIntegerField(default=2)
    prj_mindkesz = models.SmallIntegerField(default=2, verbose_name='Minden kész', choices=MINDKESZ_CHOICES)
    prj_faa_kesz = models.SmallIntegerField(default=2, verbose_name='Faállomány kész', choices=GENERAL_CHOICES)
    prj_fae_kesz = models.SmallIntegerField(default=2, verbose_name='Egyes fák kész', choices=GENERAL_CHOICES)
    prj_fhf_kesz = models.SmallIntegerField(default=2, verbose_name='Fekvő holtfa kész', choices=GENERAL_CHOICES)
    prj_ucs_kesz = models.SmallIntegerField(default=2, verbose_name='Újulat/cserje kész', choices=GENERAL_CHOICES)
    prj_nov_kesz = models.SmallIntegerField(default=2, verbose_name='Aljnövényzet kész', choices=GENERAL_CHOICES)
    prj_tsz_kesz = models.SmallIntegerField(default=2)
    prj_trm_kesz = models.SmallIntegerField(default=2)
    prj_fot_kesz = models.SmallIntegerField(default=2, verbose_name='Fotófeltöltés kész', choices=GENERAL_CHOICES)
    prj_fot_fokonyvtar = models.CharField(max_length=150, default='c:\\c_erdo_fotok\\')
    prj_mgj_fsz_kesz = models.SmallIntegerField(default=2)
    prj_mgj_ucs_kesz = models.SmallIntegerField(default=2)
    prj_mgj_nov_kesz = models.SmallIntegerField(default=2)
    prj_mgj_trm_kesz = models.SmallIntegerField(default=2)
    prj_mgj_kesz = models.SmallIntegerField(default=2, verbose_name='Megjegyzések kész', choices=OTHER_CHOICES)
    prj_tip_kesz = models.SmallIntegerField(default=2, verbose_name='Erdőtipizálás kész', choices=OTHER_CHOICES)
    prj_mvp_kesz = models.SmallIntegerField(default=2)
    prj_tgd_kesz = models.SmallIntegerField(default=2)
    prj_ert_dszog = models.DecimalField("Mágneses elhajlás szöge", max_digits=5, decimal_places=1, default=3.6, help_text='lásd: <a href="https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml" target="_blank">NOAA Magnetic Field Calculator </a>')
    prj_ert_ddatum = models.DateField("Mágneses elhajlás dátuma", default=datetime.strptime('2005/01/28', '%Y/%m/%d'))
    prj_tmd_faasz_id = models.SmallIntegerField("FAÁSZ tervezett módszertan azonosítója", default=1)
    prj_tmd_faa = models.ForeignKey('XModFaa', verbose_name="FAA tervezett módszertan", on_delete=models.DO_NOTHING,
                                    default=2, help_text='faállomány záródás, borítások felmérése ...')
    prj_tmd_fae = models.ForeignKey('XModFae', verbose_name="FAE tervezett módszertan",
                                    on_delete=models.DO_NOTHING, default=2, help_text='egyes fák felmérése ...')
    prj_tmd_fhf = models.ForeignKey('XModFhf', verbose_name="FHF tervezett módszertan",
                                    on_delete=models.DO_NOTHING, default=4, help_text='fekvő holtfa felmérése ...')
    prj_tmd_ujcs = models.ForeignKey('XModUjcs', verbose_name="ÚJCS tervezett módszertan",
                                     on_delete=models.DO_NOTHING, default=3, help_text='újulat és cserjeszint felmérése ...')
    prj_tmd_anov = models.ForeignKey('XModAnov', verbose_name="ANÖV tervezett módszertan",
                                     on_delete=models.DO_NOTHING, default=1, help_text='aljnövényzet felmérése ...')
    prj_tmd_term = models.ForeignKey('XModTerm', verbose_name="term tervezett módszertan",
                                     on_delete=models.DO_NOTHING, default=1)
    prj_tmd_tszel = models.ForeignKey('XModTszel', verbose_name="tszel tervezett módszertan",
                                      on_delete=models.DO_NOTHING, default=1)
    prj_tmd_foto = models.ForeignKey('XModFoto', verbose_name="DFOTÓ tervezett módszertan",
                                     on_delete=models.DO_NOTHING, default=1, help_text='dokumentumfotók készítése ...')
    prj_tmd_megj = models.ForeignKey('XModMegj', verbose_name="MEGJ tervezett módszertan",
                                     on_delete=models.DO_NOTHING, default=1, help_text='megjegyzések módszertan ...')
    prj_tmd_tipi = models.ForeignKey('XModTipi', verbose_name="TIPI tervezett módszertan",
                                     on_delete=models.DO_NOTHING, default=1, help_text='az élőhely (erdőtípus) besorolás ...')
    prj_tmd_mvpk = models.ForeignKey('XModMvpk', verbose_name="mvpk tervezett módszertan",
                                     on_delete=models.DO_NOTHING, default=2)
    prj_tmd_tgdk = models.ForeignKey('XModTgdk', verbose_name="tgdk tervezett módszertan",
                                     on_delete=models.DO_NOTHING, default=1)

    def __str__(self):
        return self.prj_nev

    class Meta:
        managed = False
        db_table = 'a_prj'
        verbose_name = 'Projekt'
        verbose_name_plural = 'Projektek'

class SamplingPoint(models.Model):
    ert = models.ForeignKey(ForestReserve, models.DO_NOTHING, verbose_name='Erdőterület', default=15)
    mvp_id = models.AutoField(primary_key=True, verbose_name='MVP ID')
    mvp_azo = models.CharField(max_length=25, verbose_name='Mintavételi pont azonosító')
    mvp_eov_x = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='EOV_X', default=0)
    mvp_eov_y = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='EOV_Y', default=0)
    mvp_tszfm = models.DecimalField(max_digits=4, decimal_places=0, verbose_name='Tszf magasság', default=9999)
    mvp_pontossag = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='Pontosság', default=25)
    mvp_lejtesirany = models.SmallIntegerField(verbose_name='Lejtésirány (fok)', default=999)
    mvp_lejtoszog = models.SmallIntegerField(verbose_name='Lejtőszög (fok)', default=0)
    mvp_wgs84_fi = models.FloatField(blank=True, null=True, verbose_name='WGS84 (fi)')
    mvp_wgs84_lambda = models.FloatField(blank=True, null=True, verbose_name='WGS84 (lambda )')
    mvp_utm_x = models.FloatField(blank=True, null=True)
    mvp_utm_y = models.FloatField(blank=True, null=True)
    mvp_maxfa = models.IntegerField(verbose_name='Eddig felmért fák száma', default=0)
    mvp_mtvz = models.CharField(max_length=25, blank=True, null=True, verbose_name='MT vagy VZ')
    temporal_x = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    temporal_y = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    megjegyzes = models.CharField(max_length=25, blank=True, null=True, verbose_name='Megjegyzés')

    def __str__(self):
        return self.mvp_azo

    class Meta:
        managed = False
        db_table = 'c_mvp'
        unique_together = (('ert', 'mvp_azo'),)
        verbose_name = 'Mintavételi pont'
        verbose_name_plural = 'Mintavételi pontok'

class Action(models.Model):
    akc_id = models.AutoField(primary_key=True)
    akc_azo = models.CharField(max_length=15)
    akc_megj = models.CharField(max_length=50)

    def __str__(self):
        return self.akc_azo

    class Meta:
        managed = False
        db_table = 'x_akc'
        verbose_name = 'Akció/Tevékenység'
        verbose_name_plural = 'Akciók/Tevékenységek'

class Status(models.Model):
    sta_id = models.AutoField(primary_key=True)
    sta_tipus = models.CharField(max_length=25)
    sta_rnev = models.CharField(max_length=25)
    sta_leiras = models.CharField(max_length=250)

    def __str__(self):
        return self.sta_leiras

    class Meta:
        managed = False
        db_table = 'x_sta'
        verbose_name = 'Státusz'
        verbose_name_plural = 'Státuszok'

class Person(models.Model):
    szm_id = models.AutoField(primary_key=True, verbose_name='Személy(ek) azonosítója. FK_a_')
    szm_rnev = models.CharField(max_length=25, verbose_name='Személy(ek) rövidített neve')
    szm_nev = models.CharField(max_length=250, verbose_name='Személy(ek) neve részletesen')
    djangouser = models.CharField(unique=True, max_length=15, blank=True, null=True)

    def __str__(self):
        return self.szm_nev

    class Meta:
        managed = False
        db_table = 'x_szm'
        verbose_name = 'Személy'
        verbose_name_plural = 'Személyek'

class Taxon(models.Model):
    NN_CHOICES = [('D', 'D'), ('M', 'M'), ('P', 'P'), ('G', 'G'), ('X', 'X')]
    TXNRANG_CHOICES = [('A', 'A'), ('AF', 'AF'), ('AGG', 'AGG'), ('F', 'F'), ('F?', 'F?'), ('FA', 'FA'), ('GEN', 'GEN'), ('H', 'H'), ('NCK', 'NCK'), ('T', 'T'), ('V', 'V')]
    FACSJE_CHOICES = [('FA', 'FA'), ('CSJE', 'CSJE')]
    HONOS_CHOICES = [('IDH', 'IDH'), ('ŐSH', 'ŐSH')]

    txn_id = models.AutoField(primary_key=True)
    txn_azo = models.CharField(max_length=10, blank=True, null=True)
    erd_kod = models.SmallIntegerField(blank=True, null=True)
    soossz = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    kod532 = models.CharField(max_length=12, blank=True, null=True)
    nn = models.CharField(max_length=5, blank=True, null=True, choices=NN_CHOICES)
    csalad = models.CharField(max_length=25, blank=True, null=True)
    taxonrang = models.CharField(max_length=5, blank=True, null=True, choices=TXNRANG_CHOICES)
    genus = models.CharField(max_length=25, blank=True, null=True)
    species = models.CharField(max_length=25, blank=True, null=True)
    auctor = models.CharField(max_length=50, blank=True, null=True)
    istax = models.CharField(max_length=25, blank=True, null=True)
    istax_auctor = models.CharField(max_length=50, blank=True, null=True)
    magyarnev = models.CharField(max_length=50, blank=True, null=True)
    latinnev = models.CharField(max_length=100, blank=True, null=True)
    megjegyzes = models.CharField(max_length=250, blank=True, null=True)
    facsje = models.CharField(max_length=5, blank=True, null=True, choices=FACSJE_CHOICES)
    eletforma = models.CharField(max_length=10, blank=True, null=True)
    honos = models.CharField(max_length=5, blank=True, null=True, choices=HONOS_CHOICES)
    jel_rkod = models.SmallIntegerField(blank=True, null=True)
    jel_gkod = models.SmallIntegerField(blank=True, null=True)
    jel_bkod = models.SmallIntegerField(blank=True, null=True)
    jel_tkod = models.SmallIntegerField(blank=True, null=True)
    knt_rkod = models.SmallIntegerField(blank=True, null=True)
    knt_gkod = models.SmallIntegerField(blank=True, null=True)
    knt_bkod = models.SmallIntegerField(blank=True, null=True)
    knt_vkod = models.SmallIntegerField(blank=True, null=True)
    genusvalaszto = models.CharField(max_length=50, blank=True, null=True)
    latinnevvalaszto = models.CharField(max_length=150, blank=True, null=True)
    osztaly_fafajlatinnev_focsoport = models.CharField(max_length=50, blank=True, null=True)
    osztaly_fafajlatinnev_csoport = models.CharField(max_length=50, blank=True, null=True)
    osztaly_csjelatinnev_focsoport = models.CharField(max_length=50, blank=True, null=True)
    osztaly_csjelatinnev_csoport = models.CharField(max_length=50, blank=True, null=True)
    osztaly_gyszintlatinnev_focsoport = models.CharField(max_length=50, blank=True, null=True)
    osztaly_gyszintlatinnev_csoport = models.CharField(max_length=50, blank=True, null=True)
    vedettseg_2012 = models.CharField(max_length=3, blank=True, null=True)
    tvertek_2012 = models.SmallIntegerField(blank=True, null=True)
    gyom = models.CharField(max_length=5, blank=True, null=True)
    nitrofil = models.CharField(max_length=5, blank=True, null=True)
    klzsvprd2012 = models.CharField(max_length=5, blank=True, null=True)
    krlyvprd2008 = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return self.latinnev
    
    class Meta:
        managed = False
        db_table = 'x_txn'
        verbose_name = 'Taxon'
        verbose_name_plural = 'Teljes taxonlista'

class ErtTxn(models.Model):
    SKALA_CHOICES = [(-1, 'nem fordul elő (-1)'), (0, 'előfordul (0)'), (1, 'gyakori taxon (1)'), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)]

    # ert_values = ForestReserve.objects.exclude(ert_nev__contains='TESZT').order_by('ert_nev').values('ert_id', 'ert_nev')
    # ERT_CHOICES = [(ert['ert_id'], ert['ert_nev']) for ert in ert_values]
    # txn_values = Taxon.objects.order_by('latinnev').values('txn_id', 'latinnev')
    # TXN_CHOICES = [(txn['txn_id'], txn['latinnev']) for txn in txn_values]

    # ert_id = models.IntegerField(choices=ERT_CHOICES, verbose_name = 'ER terület')
    # txn_id = models.IntegerField(choices=TXN_CHOICES, verbose_name = 'Taxon')
    ert = models.ForeignKey('ForestReserve', verbose_name='ER terület', on_delete=models.DO_NOTHING)
    txn = models.ForeignKey('Taxon', verbose_name='Taxon', on_delete=models.DO_NOTHING)
    gyakori_faasz = models.IntegerField(choices=SKALA_CHOICES, verbose_name = 'FAÁSZ szintben')
    gyakori_ujcs = models.IntegerField(choices=SKALA_CHOICES, verbose_name = 'ÚJCS szintben')
    gyakori_anov = models.IntegerField(choices=SKALA_CHOICES, verbose_name = 'ANÖV szintben')
    gyakori_ossz = models.IntegerField(blank=True, null=True)
    erttxn_id = models.AutoField(primary_key=True)
    
    def __str__(self):
        return f'{self.ert_id} {self.txn_id}'
        
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # Hack to not save the gyakori_ossz as this is computed column
        self._meta.local_fields = [f for f in self._meta.local_fields if f.name not in ('gyakori_ossz')]
        super(ErtTxn, self).save(force_insert, force_update, using, update_fields)
    
    class Meta:
        managed = False
        db_table = 'b_ert_txn'
        unique_together = (('ert_id', 'txn_id'),)
        verbose_name = 'Taxon ER-onként'
        verbose_name_plural = 'Taxonok ER-onként'


class PrMvpCsop(models.Model):
    csopprj = models.ForeignKey('PrMvpCsopKat', models.DO_NOTHING, verbose_name = 'Csoport kategória')
    csoport_id = models.AutoField(primary_key=True)
    csoport_rnev = models.CharField(max_length=25, verbose_name = 'Rövid név')
    csoport_nev = models.CharField(max_length=250, verbose_name="Név")
    csoport_leiras = models.CharField(max_length=4000, verbose_name="Leírás")

    def __str__(self):
        return self.csoport_rnev

    class Meta:
        managed = False
        db_table = 'j_csop'
        verbose_name = 'PRJ-MVP csoport'
        verbose_name_plural = 'PRJ-MVP csoportok'


class PrMvpCsopElem(models.Model):
    prj = models.ForeignKey(Project, models.DO_NOTHING, verbose_name = 'Projekt')
    mvp = models.ForeignKey(SamplingPoint, models.DO_NOTHING, verbose_name = 'Mintavételi pont')
    csoport = models.ForeignKey(PrMvpCsop, models.DO_NOTHING, verbose_name = 'Csoport')
    csoport_adatix_id = models.AutoField(primary_key=True, verbose_name = 'ID')

    class Meta:
        managed = False
        db_table = 'j_csop_adatix'
        unique_together = (('prj', 'mvp', 'csoport'),)
        verbose_name = 'PRJ-MVP csoportelem'
        verbose_name_plural = 'PRJ-MVP csoportelemek'


class PrMvpCsopKat(models.Model):
    csopprj_id = models.AutoField(primary_key=True)
    csopprj_rnev = models.CharField(db_column='csopprj-rnev', max_length=25, verbose_name="Rövid név")  # Field renamed to remove unsuitable characters.
    csopprj_nev = models.CharField(max_length=250, verbose_name="Név")
    csopprj_vez = models.ForeignKey('Person', models.DO_NOTHING, verbose_name="Vezető")
    csopprj_ev = models.SmallIntegerField(verbose_name="Év")
    csopprj_leiras = models.CharField(max_length=4000, verbose_name="Leírás")
    csopprj_url = models.CharField(max_length=250, blank=True, null=True, verbose_name="Link")

    def __str__(self):
        return self.csopprj_rnev

    class Meta:
        managed = False
        db_table = 'j_csopprj'
        verbose_name = 'PRJ-MVP csoportkategória'
        verbose_name_plural = 'PRJ-MVP csoportkategóriák'

class Jegyzokonyv(models.Model):
    CHOICES = [(2, 'nincs tervezve (2)'), (0, 'tervezett (0'), (1, 'kész (1)'),  (3, 'nincs adat (3)'), (4, 'felmérésből kimaradt (4)')]
    
    prj = models.ForeignKey(Project, models.DO_NOTHING, verbose_name="Projekt")
    mvp = models.ForeignKey('SamplingPoint', models.DO_NOTHING, verbose_name="MVP")
    jkv_adat_id = models.AutoField(primary_key=True, verbose_name="JKV")
    faasz_felmeresdatum = models.DateField(blank=True, null=True, verbose_name="FAÁSZ felmérésdátum")
    faasz_felmero = models.ForeignKey('Person', models.DO_NOTHING, verbose_name='FAÁSZ felmérő', default=1)
    faasz_jkonyvezo = models.ForeignKey('Person', models.DO_NOTHING, verbose_name='FAÁSZ jegyzőkönyvező', default=1)
    faasz_modszertan_id = models.SmallIntegerField()
    faa_modszertan = models.ForeignKey('XModFaa', verbose_name="FAA tervezett módszertan", on_delete=models.DO_NOTHING, default=2, help_text='faállomány záródás, borítások felmérése ...')
    fae_modszertan = models.ForeignKey('XModFae', verbose_name="FAE tervezett módszertan", on_delete=models.DO_NOTHING, default=2, help_text='egyes fák felmérése ...')
    fhf_modszertan = models.ForeignKey('XModFhf', verbose_name="FHF tervezett módszertan", on_delete=models.DO_NOTHING, default=4, help_text='fekvő holtfa felmérése ...')
    faasz_adatlap_ssz = models.CharField(max_length=5, blank=True, default='', verbose_name="FAÁSZ adatlap sorszáma")
    faa_kesz = models.SmallIntegerField(default=2, choices=CHOICES, verbose_name="FAA készültség")
    fae_kesz = models.SmallIntegerField(default=2, choices=CHOICES, verbose_name="FAE készültség")
    fae_mvhanyad = models.DecimalField(max_digits=4, decimal_places=2)
    fhf_kesz = models.SmallIntegerField(default=2, choices=CHOICES, verbose_name="FHF készültség")
    fhf_mvhanyad = models.DecimalField(max_digits=4, decimal_places=2)
    ujcs_felmeresdatum = models.DateField(blank=True, null=True)
    ujcs_felmero = models.ForeignKey('Person', models.DO_NOTHING, verbose_name='UJCS jfelmérő', default=1)
    ujcs_jkonyvezo = models.ForeignKey('Person', models.DO_NOTHING, verbose_name='UJCS jegyzőkönyvező', default=1)
    ujcs_modszertan = models.ForeignKey('XModUjcs', models.DO_NOTHING)
    ujcs_adatlap_ssz = models.CharField(max_length=5, blank=True, default='', verbose_name="UJCS adatlap sorszáma")
    ujcs_kesz = models.SmallIntegerField(default=2, choices=CHOICES, verbose_name="UJCS készültség")
    ujcs_mvhanyad = models.DecimalField(max_digits=4, decimal_places=2)
    anov_felmeresdatum = models.DateField(blank=True, null=True)
    anov_felmero = models.ForeignKey('Person', models.DO_NOTHING, verbose_name='ANÖV felmérő', default=1)
    anov_jkonyvezo = models.ForeignKey('Person', models.DO_NOTHING, verbose_name='ANÖV jegyzőkönyvező', default=1)
    anov_modszertan = models.ForeignKey('XModAnov', models.DO_NOTHING, verbose_name='Módszertan')
    anov_adatlap_ssz = models.CharField(max_length=5, blank=True, default='', verbose_name="ANÖV adatlap sorszáma")
    anov_boritas = models.SmallIntegerField(blank=True, null=True)
    anov_4x7pl2 = models.BooleanField()
    anov_kesz = models.SmallIntegerField(default=2, choices=CHOICES, verbose_name="ANÖV készültség")
    anov_mvhanyad = models.DecimalField(max_digits=4, decimal_places=2)
    term_felmeresdatum = models.DateField(blank=True, null=True)
    term_felmero_id = models.SmallIntegerField(default=1)
    term_jkonyvezo_id = models.SmallIntegerField(default=1)
    term_modszertan = models.ForeignKey('XModTerm', models.DO_NOTHING)
    term_adatlap_ssz = models.CharField(max_length=5)
    term_kesz = models.SmallIntegerField(default=2)
    foto_felmeresdatum = models.DateField(blank=True, null=True)
    foto_felmero = models.ForeignKey('Person', models.DO_NOTHING, default=1)
    foto_modszertan = models.ForeignKey('XModFoto', models.DO_NOTHING)
    foto_adatlap_ssz = models.CharField(max_length=5, blank=True, default='', verbose_name="FOTO adatlap sorszáma")
    foto_kesz = models.SmallIntegerField(default=2, choices=CHOICES, verbose_name="FOTO készültség")
    megj_felmeresdatum = models.DateField(blank=True, null=True)
    megj_felmero = models.ForeignKey('Person', models.DO_NOTHING, default=1)
    megj_modszertan = models.ForeignKey('XModMegj', models.DO_NOTHING)
    megj_adatlap_ssz = models.CharField(max_length=5, blank=True, null=True, default='', verbose_name="MEGJ adatlap sorszáma")
    megj_kesz = models.SmallIntegerField(default=2)
    megj_fsz_kesz = models.SmallIntegerField(default=2, choices=CHOICES)
    megj_ucs_kesz = models.SmallIntegerField(default=2, choices=CHOICES)
    megj_nov_kesz = models.SmallIntegerField(default=2, choices=CHOICES)
    megj_trm_kesz = models.SmallIntegerField(default=2)
    tip_felmeresdatum = models.DateField(blank=True, null=True)
    tip_felmero = models.ForeignKey('Person', models.DO_NOTHING, default=1)
    tip_modszertani = models.ForeignKey('XModTipi', models.DO_NOTHING)
    tip_adatlapssz_ssz = models.CharField(max_length=5, blank=True, null=True, default='', verbose_name="TIP adatlap sorszáma")
    tip_kesz = models.SmallIntegerField(default=2, choices=CHOICES)
    mvpk_felmeresdatum = models.DateField(blank=True, null=True)
    mvpk_felmero_id = models.SmallIntegerField(default=1)
    mvpk_modszertan = models.ForeignKey('XModMvpk', models.DO_NOTHING)
    mvpk_adatlap_ssz = models.CharField(max_length=5, blank=True, null=True, default='')
    mvpk_kesz = models.SmallIntegerField(default=2)
    uju_kesz = models.SmallIntegerField(default=2, choices=CHOICES)
    cse_kesz = models.SmallIntegerField(default=2, choices=CHOICES)
    erht_kesz = models.SmallIntegerField(default=2, choices=CHOICES)
    flmt_kesz = models.SmallIntegerField(default=2, choices=CHOICES)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # Hack to not save the gyakori_ossz as this is computed column
        self._meta.local_fields = [f for f in self._meta.local_fields if f.name not in ('faasz_modszertan_id', 'fae_mvhanyad', 'fhf_mvhanyad', 'ujcs_mvhanyad', 'anov_4x7pl2', 'anov_mvhanyad', 'term_modszertan', 'mvpk_modszertan')]#, '', '', '', '', '', '', '')]
        super(Jegyzokonyv, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'Jegyzőkönyv ID: {self.jkv_adat_id}'

    class Meta:
        managed = False
        db_table = 'c_jkv_adat'
        unique_together = (('prj', 'mvp'),)
        verbose_name = 'Jegyzőkönyv'
        verbose_name_plural = 'Jegyzőkönyvek'
