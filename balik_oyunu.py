import pygame
import random

pygame.init()

GENISLIK = 800
YUKSEKLIK = 600
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
pygame.display.set_caption("Muharrem Dede'nin Oltası")
saat = pygame.time.Clock()
yazi = pygame.font.SysFont("arial", 26)
kucuk_yazi = pygame.font.SysFont("arial", 20)
buyuk_yazi = pygame.font.SysFont("arial", 80, bold=True)
baslik_yazi = pygame.font.SysFont("georgia", 32, bold=True)

# Renkler
GOKYUZU = (135, 206, 235)
SU = (30, 100, 180)
KUM = (230, 210, 150)
BEYAZ = (255, 255, 255)
KIRMIZI = (220, 30, 30)
KAHVE = (120, 70, 30)
SIYAH = (0, 0, 0)
YESIL = (80, 200, 100)
KAGIT = (240, 228, 196)
MUREKKEP = (60, 40, 20)
GOLGE = (150, 140, 120)

SU_SEVIYESI = 300
BALIKCI_X = 120
BALIKCI_Y = SU_SEVIYESI - 10

BALIKLAR = [
    {"ad": "Hamsi",    "puan": 5,  "sans": 35, "hiz": 2.0, "renk": (190, 200, 210)},
    {"ad": "İstavrit", "puan": 8,  "sans": 25, "hiz": 2.6, "renk": (120, 150, 170)},
    {"ad": "Levrek",   "puan": 15, "sans": 18, "hiz": 3.3, "renk": (170, 180, 190)},
    {"ad": "Palamut",  "puan": 20, "sans": 10, "hiz": 3.9, "renk": (90, 110, 150)},
    {"ad": "Lüfer",    "puan": 30, "sans": 8,  "hiz": 4.6, "renk": (70, 130, 160)},
    {"ad": "Kalkan",   "puan": 50, "sans": 4,  "hiz": 5.3, "renk": (150, 120, 80)},
]

def balik_sec():
    agirliklar = [b["sans"] for b in BALIKLAR]
    return random.choices(BALIKLAR, weights=agirliklar)[0]

# Mini oyun ayarları
BAR_X = 640
BAR_UST = 110
BAR_YUKSEKLIK = 400
KUTU_BOY = 100

# Oyun durumları: giris, bosta, bekliyor, vurdu, mini
durum = "giris"
baslangic_zamani = 0
bekleme_suresi = 0
vurma_zamani = 0
VURMA_PENCERESI = 1000
mesaj = ""
puan = 0
defter = {}
defter_acik = False

# Mini oyun değişkenleri
secilen = None
kutu_y = 0
kutu_hiz = 0
balik_y = 0
hedef_y = 0
ilerleme = 0

def balik_ciz(x, y, renk, boyut=1.0):
    govde = pygame.Rect(0, 0, int(50 * boyut), int(22 * boyut))
    govde.center = (x, y)
    pygame.draw.ellipse(ekran, renk, govde)
    kuyruk = [(govde.left + 2, y), (govde.left - int(14 * boyut), y - int(10 * boyut)),
              (govde.left - int(14 * boyut), y + int(10 * boyut))]
    pygame.draw.polygon(ekran, renk, kuyruk)
    pygame.draw.circle(ekran, SIYAH, (govde.right - int(10 * boyut), y - 3), 3)

def defter_ciz():
    sayfa = pygame.Rect(100, 40, 600, 520)
    pygame.draw.rect(ekran, (90, 55, 25), sayfa.inflate(16, 16), border_radius=12)
    pygame.draw.rect(ekran, KAGIT, sayfa, border_radius=8)

    baslik = baslik_yazi.render("Muharrem Dede'nin Defteri", True, MUREKKEP)
    ekran.blit(baslik, (GENISLIK // 2 - baslik.get_width() // 2, 62))
    pygame.draw.line(ekran, MUREKKEP, (140, 115), (660, 115), 2)

    ekran.blit(kucuk_yazi.render("Tür", True, MUREKKEP), (250, 125))
    ekran.blit(kucuk_yazi.render("Adet", True, MUREKKEP), (470, 125))
    ekran.blit(kucuk_yazi.render("Değeri", True, MUREKKEP), (560, 125))

    for i, b in enumerate(BALIKLAR):
        y = 185 + i * 58
        yakalandi = b["ad"] in defter
        if yakalandi:
            balik_ciz(175, y, b["renk"], 1.0)
            ad_yazisi = yazi.render(b["ad"], True, MUREKKEP)
            adet_yazisi = yazi.render(str(defter[b["ad"]]), True, MUREKKEP)
            puan_yazisi = yazi.render(f"{b['puan']} puan", True, MUREKKEP)
        else:
            balik_ciz(175, y, GOLGE, 1.0)
            ad_yazisi = yazi.render("???", True, GOLGE)
            adet_yazisi = yazi.render("-", True, GOLGE)
            puan_yazisi = yazi.render("?", True, GOLGE)
        ekran.blit(ad_yazisi, (250, y - 14))
        ekran.blit(adet_yazisi, (480, y - 14))
        ekran.blit(puan_yazisi, (560, y - 14))
        pygame.draw.line(ekran, (200, 185, 150), (140, y + 28), (660, y + 28), 1)

    toplam = sum(defter.values())
    ekran.blit(kucuk_yazi.render(f"Toplam yakalanan: {toplam} balık   |   Keşfedilen: {len(defter)}/{len(BALIKLAR)}", True, MUREKKEP), (140, 520))
    ekran.blit(kucuk_yazi.render("Kapatmak için D", True, GOLGE), (530, 520))

calisiyor = True
while calisiyor:
    simdi = pygame.time.get_ticks()
    tuslar = pygame.key.get_pressed()

    # 1) Olaylar
    for olay in pygame.event.get():
        if olay.type == pygame.QUIT:
            calisiyor = False

        if olay.type == pygame.KEYDOWN:
            if olay.key == pygame.K_d and (durum == "bosta" or defter_acik):
                defter_acik = not defter_acik

            elif olay.key == pygame.K_ESCAPE:
                defter_acik = False

            elif olay.key == pygame.K_SPACE and not defter_acik:
                if durum == "giris":
                    durum = "bosta"
                    mesaj = "BOŞLUK tuşuyla oltayı at"

                elif durum == "bosta":
                    durum = "bekliyor"
                    baslangic_zamani = simdi
                    bekleme_suresi = random.randint(2000, 5000)
                    mesaj = "Olta atıldı... Boğaz'ın sesini dinle..."

                elif durum == "bekliyor":
                    durum = "bosta"
                    mesaj = "Acele etme, balık sabırlıları sever. (BOŞLUK)"

                elif durum == "vurdu":
                    durum = "mini"
                    secilen = balik_sec()
                    kutu_y = BAR_UST + BAR_YUKSEKLIK - KUTU_BOY
                    kutu_hiz = 0
                    balik_y = BAR_UST + BAR_YUKSEKLIK // 2
                    hedef_y = balik_y
                    ilerleme = 30
                    mesaj = "BOŞLUK'a basılı tut, balığı yeşil kutuda tut!"

    # 2) Oyun mantığı
    if durum == "bekliyor" and simdi - baslangic_zamani >= bekleme_suresi:
        durum = "vurdu"
        vurma_zamani = simdi
        mesaj = "BALIK VURDU! Hemen BOŞLUK!"

    if durum == "vurdu" and simdi - vurma_zamani > VURMA_PENCERESI:
        durum = "bosta"
        mesaj = "Balık kaçtı... Muharrem Dede olsa yakalardı. (BOŞLUK)"

    if durum == "mini":
        if tuslar[pygame.K_SPACE]:
            kutu_hiz -= 0.5
        else:
            kutu_hiz += 0.4
        kutu_hiz = max(-7, min(7, kutu_hiz))
        kutu_y += kutu_hiz

        if kutu_y < BAR_UST:
            kutu_y = BAR_UST
            kutu_hiz = 0
        if kutu_y + KUTU_BOY > BAR_UST + BAR_YUKSEKLIK:
            kutu_y = BAR_UST + BAR_YUKSEKLIK - KUTU_BOY
            kutu_hiz = 0

        if abs(balik_y - hedef_y) < secilen["hiz"]:
            hedef_y = random.randint(BAR_UST + 15, BAR_UST + BAR_YUKSEKLIK - 15)
        if balik_y < hedef_y:
            balik_y += secilen["hiz"]
        else:
            balik_y -= secilen["hiz"]

        if kutu_y <= balik_y <= kutu_y + KUTU_BOY:
            ilerleme += 0.4
        else:
            ilerleme -= 0.3

        if ilerleme >= 100:
            ad = secilen["ad"]
            yeni_tur = ad not in defter
            defter[ad] = defter.get(ad, 0) + 1
            puan += secilen["puan"]
            if yeni_tur:
                mesaj = f"{ad}! Muharrem Dede'nin defterine eklendi. (D)"
            else:
                mesaj = f"{ad} yakaladın! +{secilen['puan']} puan (BOŞLUK)"
            durum = "bosta"
        elif ilerleme <= 0:
            mesaj = "Balık oltadan kurtuldu... Bir dahaki sefere. (BOŞLUK)"
            durum = "bosta"

    # 3) Çizim
    ekran.fill(GOKYUZU)
    pygame.draw.rect(ekran, SU, (0, SU_SEVIYESI, GENISLIK, YUKSEKLIK - SU_SEVIYESI))
    pygame.draw.rect(ekran, KUM, (0, YUKSEKLIK - 60, GENISLIK, 60))
    pygame.draw.rect(ekran, KAHVE, (0, SU_SEVIYESI - 5, 220, 15))

    pygame.draw.circle(ekran, (255, 200, 150), (BALIKCI_X, BALIKCI_Y - 70), 15)
    pygame.draw.rect(ekran, (200, 50, 50), (BALIKCI_X - 12, BALIKCI_Y - 55, 24, 45))

    if durum in ("giris", "bosta"):
        olta_ucu_x = BALIKCI_X + 80
        olta_ucu_y = BALIKCI_Y - 100
    else:
        olta_ucu_x = 400
        olta_ucu_y = SU_SEVIYESI + 120
    pygame.draw.line(ekran, SIYAH, (BALIKCI_X + 10, BALIKCI_Y - 45), (BALIKCI_X + 90, BALIKCI_Y - 110), 3)
    pygame.draw.line(ekran, BEYAZ, (BALIKCI_X + 90, BALIKCI_Y - 110), (olta_ucu_x, olta_ucu_y), 1)
    if durum not in ("giris", "bosta"):
        pygame.draw.circle(ekran, KIRMIZI, (olta_ucu_x, olta_ucu_y), 7)

    if durum == "vurdu":
        isaret = buyuk_yazi.render("!", True, KIRMIZI)
        ekran.blit(isaret, (olta_ucu_x - 15, SU_SEVIYESI - 120))

    if durum == "mini":
        pygame.draw.rect(ekran, (20, 40, 80), (BAR_X - 10, BAR_UST - 10, 100, BAR_YUKSEKLIK + 20), border_radius=8)
        pygame.draw.rect(ekran, (40, 80, 140), (BAR_X, BAR_UST, 50, BAR_YUKSEKLIK))
        pygame.draw.rect(ekran, YESIL, (BAR_X, int(kutu_y), 50, KUTU_BOY))
        balik_ciz(BAR_X + 28, int(balik_y), secilen["renk"], 0.6)
        pygame.draw.rect(ekran, (60, 60, 60), (BAR_X + 60, BAR_UST, 18, BAR_YUKSEKLIK))
        dolu = int(BAR_YUKSEKLIK * ilerleme / 100)
        pygame.draw.rect(ekran, (255, 200, 40), (BAR_X + 60, BAR_UST + BAR_YUKSEKLIK - dolu, 18, dolu))

    ekran.blit(yazi.render(mesaj, True, BEYAZ), (20, 20))
    ekran.blit(yazi.render(f"Puan: {puan}", True, BEYAZ), (20, 55))
    ekran.blit(kucuk_yazi.render(f"Muharrem Dede'nin Defteri: {len(defter)}/{len(BALIKLAR)} tür  (D tuşu ile aç)", True, BEYAZ), (20, 90))

    if durum == "giris":
        karartma = pygame.Surface((GENISLIK, YUKSEKLIK))
        karartma.set_alpha(190)
        karartma.fill((10, 20, 40))
        ekran.blit(karartma, (0, 0))
        satirlar = [
            "Muharrem Dede'nin eski oltası sana miras kaldı.",
            "Boğaz'daki iskele hâlâ yerinde, deniz hâlâ sakin.",
            "Muharrem Dede'nin defterindeki balıkların hepsini",
            "yakalayabilir misin?",
            "",
            "Başlamak için BOŞLUK tuşuna bas.",
        ]
        for i, s in enumerate(satirlar):
            ekran.blit(yazi.render(s, True, BEYAZ), (110, 170 + i * 40))

    if defter_acik:
        karartma = pygame.Surface((GENISLIK, YUKSEKLIK))
        karartma.set_alpha(150)
        karartma.fill((0, 0, 0))
        ekran.blit(karartma, (0, 0))
        defter_ciz()

    pygame.display.flip()
    saat.tick(60)

pygame.quit()
