import pygame
from settings import *
from npc import NPC
from level_manager import BaseLevel

class Level4(BaseLevel):
    """
    Bölüm 4: Kütüphane Sahnesi.
    OOP KRİTERİ: Kalıtım (Inheritance). BaseLevel ata sınıfından miras alınarak 
    merkezi diyalog motoru ve metin sarma sistemleri projeye dahil edilmiştir.
    Bu bölümde toplumsal alanlarda gürültü yapmama ve başkalarının haklarına saygı teması işlenir.
    """
    def __init__(self, pencere, player, player_group):
        # 'bolum4' anahtarı ile JSON dosyasındaki kütüphane senaryosu yüklenir.
        super().__init__(pencere, player, player_group, "bolum4")
        
        # --- DURUM YÖNETİMİ (State Management) ---
        self.intro_mesaji_aktif = True      # Başlangıç görev tanımı kutusu
        self.gurultucuye_yaklasti = False   # Oyuncunun gürültü yapan NPC'lere varıp varmadığı
        
        # --- ARKAPLAN VE GÖRSEL VARLIKLAR ---
        try:
            # Kütüphane arka planı ve etkileşim ikonları yüklenir.
            self.arkaplan = pygame.image.load("assets/Images/Backgrounds/4-kutuphane.png").convert()
            self.arkaplan = pygame.transform.scale(self.arkaplan, (GENISLIK, YUKSEKLIK))
            self.press_e_img = pygame.image.load("assets/Images/UI/press_e.png").convert_alpha()
            self.press_e_img = pygame.transform.scale(self.press_e_img, (40, 40))
        except:
            # HATA TOLERANSI: Görsel bulunamazsa sistemin çökmemesi için alternatif yüzeyler oluşturulur.
            self.arkaplan = pygame.Surface((GENISLIK, YUKSEKLIK)); self.arkaplan.fill((40, 40, 50))
            self.press_e_img = pygame.Surface((30, 30)); self.press_e_img.fill(ALTIN)

        self.static_npcs = pygame.sprite.Group()
        self.setup_sprites()

    def setup_sprites(self):
        """Kütüphanedeki öğrenci NPC'lerini sahneye yerleştirir."""
        base_path = "assets/Images/Characters/NPC/bolum4_npc/"
        
        # Gürültü yapan öğrencileri temsil eden iki ayrı NPC nesnesi oluşturulur.
        # NPC1 (Sağdaki öğrenci)
        self.NPC1 = NPC(730, 560, {'idle': base_path + "npc1_idle/"}, boyut=(200, 200))
        self.static_npcs.add(self.NPC1)
        
        # NPC2 (Soldaki öğrenci)
        self.NPC2 = NPC(660, 560, {'idle': base_path + "npc2_idle/"}, boyut=(200, 200))
        self.static_npcs.add(self.NPC2)
        
        # Görsel derinlik için oyuncunun zemin hizası NPC'lere göre ayarlanır.
        self.player.rect.bottom = self.NPC1.rect.bottom

    def run(self):
        """Bölümün ana mantıksal döngüsü ve çizim yönetimi."""
        keys = pygame.key.get_pressed()
        
        # --- MANTIK VE HAREKET KONTROL ALGORİTMASI ---
        if self.intro_mesaji_aktif:
            # Başlangıç uyarısı okunurken oyuncu hareketi engellenir.
            self.player.input_enabled = False
            if keys[pygame.K_SPACE]:
                self.intro_mesaji_aktif = False
                pygame.time.delay(200)
        else:
            # Oyuncunun etkileşim noktasına (x=500) ulaşıp ulaşmadığı kontrol edilir.
            if self.player.rect.x >= 500 and not self.gurultucuye_yaklasti:
                self.player.rect.x = 500
                self.gurultucuye_yaklasti = True
                self.player.direction.x = 0
                if hasattr(self.player, 'facing_right'):
                    self.player.facing_right = True

            # Hareket Kilidi: Etkileşim anında veya diyalog aktifken kontrol kilitlenir.
            if self.gurultucuye_yaklasti or self.diyalog_aktif or self.diyalog_bitti:
                self.player.input_enabled = False
            else:
                self.player.input_enabled = True

        # BaseLevel'dan miras alınan tuş yönetim sistemini (1, 2 tuşları) çalıştırır.
        self.input_yonetimi(keys)

        # --- ÇİZİMLER VE GÖRSEL MANTIK ---
        self.pencere.blit(self.arkaplan, (0, 0))
        
        # Sprite'ların animasyon karelerini güncelle
        self.static_npcs.update()

        # --- DİNAMİK YÖNELİM ALGORİTMASI (Flipping Logic) ---
        # 1. NPC1 her zaman sola baksın (Oyuncuya doğru yönelme).
        self.NPC1.image = pygame.transform.flip(self.NPC1.image, True, False)
        
        # 2. NPC2 diyalog başladığında sola dönerek oyuncuya odaklanır (Sosyal etkileşim simülasyonu).
        if self.diyalog_aktif:
            self.NPC2.image = pygame.transform.flip(self.NPC2.image, True, False)

        # Çizimi gerçekleştir
        self.static_npcs.draw(self.pencere)
        self.player_group.update()
        self.player_group.draw(self.pencere)

        # --- ETKİLEŞİM VE UI KATMANLARI ---
        # Oyuncu uygun mesafeye geldiğinde 'E' tuşu ipucunu yansıt.
        if self.gurultucuye_yaklasti and not self.diyalog_aktif and not self.diyalog_bitti:
            self.pencere.blit(self.press_e_img, (self.NPC1.rect.centerx - 50, self.NPC1.rect.top - 50))
            if keys[pygame.K_e]:
                self.diyalog_aktif = True

        # Bilgilendirme ve diyalog kutularını çiz
        if self.intro_mesaji_aktif:
            self.bilgi_kutusu_ciz("Ders çalışmaya geldin fakat yan taraftaki iki kişi çok gürültü yapıyor. Onları uyarmak için yanlarına git!")
        elif self.diyalog_aktif:
            # JSON'dan gelen metinler "Öğrenci" ismiyle ekrana yansıtılır.
            self.diyalog_kutusu_ciz(npc_ismi="Öğrenci")
        
        # Bölüm bittiyse etik analiz ekranını göster ve Level 5'e geçişi yönet.
        if self.diyalog_bitti:
            self.feedback_ekrani_ciz()
            if keys[pygame.K_ESCAPE]: return 5 

        return 4

    def bilgi_kutusu_ciz(self, mesaj):
        """Dinamik ve profesyonel bilgilendirme kutusu tasarımı."""
        kutu_g, kutu_y = 600, 160
        kutu_rect = pygame.Rect(GENISLIK//2 - kutu_g//2, YUKSEKLIK//2 - 200, kutu_g, kutu_y)
        
        # Saydam arka plan katmanı
        s_surf = pygame.Surface((kutu_rect.width, kutu_rect.height))
        s_surf.set_alpha(225); s_surf.fill((20, 20, 40))
        self.pencere.blit(s_surf, (kutu_rect.x, kutu_rect.y))
        
        # Altın sarısı çerçeve çizimi
        pygame.draw.rect(self.pencere, ALTIN, kutu_rect, 3)
        
        # Metni sarma algoritması ile içeriği kutuya hapseder.
        satirlar = self.metni_sar(mesaj, self.font_ana, kutu_rect.width - 60)
        y_fark = kutu_rect.y + 40
        for satir in satirlar:
            txt = self.font_ana.render(satir, True, BEYAZ)
            self.pencere.blit(txt, (kutu_rect.x + 30, y_fark))
            y_fark += 35
        
        # Alt bilgi yönlendirmesi
        alt_not = self.font_secenek.render("[ DEVAM ETMEK İÇİN SPACE TUŞUNA BASIN ]", True, ALTIN)
        self.pencere.blit(alt_not, (kutu_rect.centerx - alt_not.get_width() // 2, kutu_rect.bottom - 40))
