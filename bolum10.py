import pygame
import sys  # Oyunun tamamen kapatılması (Final) için gerekli kütüphane
from settings import *
from npc import NPC
from level_manager import BaseLevel

class Level10(BaseLevel):
    """
    Bölüm 10 (FİNAL): Zorbalıkla Mücadele.
    OOP KRİTERİ: Kalıtım (Inheritance) ve Metod Ezme (Method Overriding). 
    BaseLevel sınıfından miras alınır ve final sahnesi için özelleştirmeler yapılır.
    Bu sahne, okul ortamında yaşanan akran zorbalığına karşı ahlaki müdahaleyi işler.
    """
    def __init__(self, pencere, player, player_group):
        # 'bolum10' anahtarı ile JSON dosyasındaki final senaryosu yüklenir.
        super().__init__(pencere, player, player_group, "bolum10")
        
        # --- DURUM KONTROLLERİ (State Management) ---
        self.intro_mesaji_aktif = True # Başlangıç görevi yönergesi
        self.olay_yerinde = False      # Oyuncunun zorbalık anına ulaşıp ulaşmadığı
        
        # --- ARKAPLAN VE GÖRSELLER ---
        try:
            # Okul bahçesi final arka planı yüklenir.
            self.arkaplan = pygame.image.load("assets/Images/Backgrounds/10-zorbalik.png").convert()
            self.arkaplan = pygame.transform.scale(self.arkaplan, (GENISLIK, YUKSEKLIK))
            
            # Etkileşim ipucu (E tuşu)
            self.press_e_img = pygame.image.load("assets/Images/UI/press_e.png").convert_alpha()
            self.press_e_img = pygame.transform.scale(self.press_e_img, (40, 40))
        except Exception as e:
            # HATA TOLERANSI: Görsel bulunamazsa sistemin çökmemesi sağlanır.
            print(f"Hata: {e}")
            self.arkaplan = pygame.Surface((GENISLIK, YUKSEKLIK)); self.arkaplan.fill((30, 30, 30))
            self.press_e_img = pygame.Surface((30, 30)); self.press_e_img.fill(ALTIN)

        self.static_npcs = pygame.sprite.Group()
        self.setup_sprites()

    def setup_sprites(self):
        """İki farklı NPC'yi (Zorba ve Mağdur) sahneye yerleştirerek ahlaki ikilemi görselleştirir."""
        base_path = "assets/Images/Characters/NPC/bolum10_npc/"
        
        # 1. ZORBA: Oyuncunun doğrudan etkileşime geçip uyaracağı karakter.
        self.zorba = NPC(750, 700, {'idle': base_path + "npc1_idle/"}, boyut=(200, 200), ters_cevir=False)
        
        # 2. MAĞDUR: Zorbalığa uğrayan ve oyuncunun yardımına ihtiyaç duyan karakter.
        # 'ters_cevir=True' ile zorba karakterine doğru bakması sağlanır.
        self.magdur = NPC(850, 700, {'idle': base_path + "npc2_idle/"}, boyut=(200, 200), ters_cevir=True)
        
        self.static_npcs.add(self.zorba, self.magdur)
        
        # Oyuncunun zemindeki duruşu NPC'lerle eşitlenir.
        self.player.rect.bottom = self.zorba.rect.bottom

    def run(self):
        """Bölümün ana mantıksal akışını ve final çıkış işlemlerini yönetir."""
        keys = pygame.key.get_pressed()
        
        # --- MANTIK VE HAREKET AKIŞI ALGORİTMASI ---
        if self.intro_mesaji_aktif:
            # Başlangıç bilgilendirmesi sırasında oyuncu hareketi yazılımsal olarak kilitlenir.
            self.player.input_enabled = False
            if keys[pygame.K_SPACE]:
                self.intro_mesaji_aktif = False
                pygame.time.delay(200)
        else:
            # Karakter olay yerine (x=550) yaklaştığında otomatik olarak durdurulur.
            if self.player.rect.x >= 550 and not self.olay_yerinde:
                self.player.rect.x = 550
                self.olay_yerinde = True
                self.player.direction.x = 0
                if hasattr(self.player, 'facing_right'): self.player.facing_right = True

            # Hareket Kilidi: Diyalog aktifken veya olay yerinde hareket kısıtlanır.
            if self.olay_yerinde or self.diyalog_aktif or self.diyalog_bitti:
                self.player.input_enabled = False
            else:
                self.player.input_enabled = True

        # BaseLevel'dan miras alınan tuş yönetim sistemini çalıştırır (1 ve 2 tuşları).
        self.input_yonetimi(keys)

        # --- ÇİZİMLER ---
        self.pencere.blit(self.arkaplan, (0, 0))
        
        # NPC grubunun (Zorba ve Mağdur) animasyonlarını ve görsellerini güncelle.
        self.static_npcs.update()
        self.static_npcs.draw(self.pencere)
        
        self.player_group.update()
        self.player_group.draw(self.pencere)

        # --- ETKİLEŞİM TETİKLEME (Interaction Logic) ---
        # Oyuncu uygun mesafeye ulaştığında 'E' tuşu ipucu zorba karakterin üzerinde belirir.
        if self.olay_yerinde and not self.diyalog_aktif and not self.diyalog_bitti:
            self.pencere.blit(self.press_e_img, (self.zorba.rect.centerx - 20, self.zorba.rect.top - 50))
            if keys[pygame.K_e]:
                self.diyalog_aktif = True # Diyalog penceresini açar.

        # --- KULLANICI ARAYÜZÜ (UI) KATMANLARI ---
        if self.intro_mesaji_aktif:
            self.bilgi_kutusu_ciz("Okul önünde bir zorbalığa şahit oldun. Mağdur arkadaşını korumak için hemen müdahale et!")
        elif self.diyalog_aktif:
            # JSON'dan gelen senaryo metinleri "Zorba" ismiyle ekrana yansıtılır.
            self.diyalog_kutusu_ciz(npc_ismi="Zorba")
        
        # --- FİNAL ÇIKIŞ MANTIĞI ---
        if self.diyalog_bitti:
            # Bu metod BaseLevel'dakini ezerek final mesajını yansıtır.
            self.feedback_ekrani_ciz()
            
            # Final: ESC'ye basıldığında oyun güvenli bir şekilde kapatılır.
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

        return 10

    def bilgi_kutusu_ciz(self, mesaj):
        """Dinamik satır kaydırmalı bilgilendirme kutusu tasarımı."""
        kutu_g, kutu_y = 600, 160
        kutu_rect = pygame.Rect(GENISLIK//2 - kutu_g//2, YUKSEKLIK//2 - 200, kutu_g, kutu_y)
        
        # Saydam arka plan katmanı (HUD tasarımı).
        s_surf = pygame.Surface((kutu_rect.width, kutu_rect.height))
        s_surf.set_alpha(225); s_surf.fill((20, 20, 40))
        self.pencere.blit(s_surf, (kutu_rect.x, kutu_rect.y))
        
        # Altın sarısı çerçeve çizimi.
        pygame.draw.rect(self.pencere, ALTIN, kutu_rect, 3)
        
        # Metni sarma algoritması içeriği kutu sınırları içinde tutar.
        satirlar = self.metni_sar(mesaj, self.font_ana, kutu_rect.width - 60)
        y_fark = kutu_rect.y + 40
        for satir in satirlar:
            txt = self.font_ana.render(satir, True, BEYAZ)
            self.pencere.blit(txt, (kutu_rect.x + 30, y_fark))
            y_fark += 35
            
        alt_not = self.font_secenek.render("[ DEVAM ETMEK İÇİN SPACE TUŞUNA BASIN ]", True, ALTIN)
        self.pencere.blit(alt_not, (kutu_rect.centerx - alt_not.get_width() // 2, kutu_rect.bottom - 40))

    def feedback_ekrani_ciz(self):
        """
        TEKNİK KRİTER: Metod Ezme (Overriding).
        Ata sınıftaki (BaseLevel) feedback_ekrani_ciz metodunu ezer.
        Böylece final sahnesi için özel bir çıkış yönergesi yansıtılmış olur.
        """
        super().feedback_ekrani_ciz(alt_not_metni="[ OYUNU BİTİRMEK İÇİN ESC TUŞUNA BASIN ]")
