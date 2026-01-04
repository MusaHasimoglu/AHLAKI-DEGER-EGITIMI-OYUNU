import pygame
from settings import *
from npc import NPC
from level_manager import BaseLevel

class Level7(BaseLevel):
    """
    Bölüm 7: Oda - Kişisel Verilerin Gizliliği.
    OOP KRİTERİ: Kalıtım (Inheritance). BaseLevel ata sınıfından miras alınarak 
    JSON tabanlı diyalog ve analiz sistemleri projeye dahil edilmiştir.
    Bu bölümde, üçüncü bir şahsa ait özel bilginin (telefon numarası) izinsiz 
    paylaşılıp paylaşılmaması ikilemi işlenir.
    """
    def __init__(self, pencere, player, player_group):
        # 'bolum7' anahtarı ile JSON dosyasındaki oda senaryosu yüklenir.
        super().__init__(pencere, player, player_group, "bolum7")
        
        # --- DURUM YÖNETİMİ (State Management) ---
        self.intro_mesaji_aktif = True      # Başlangıç görev yönergesi kutusu
        self.bulusma_gerceklesti = False    # Oyuncunun Beren'e ulaşıp ulaşmadığı
        
        # --- ARKAPLAN VE GÖRSEL VARLIKLAR ---
        try:
            # Genç odası arka planı yüklenir.
            self.arkaplan = pygame.image.load("assets/Images/Backgrounds/7-oda.png").convert()
            self.arkaplan = pygame.transform.scale(self.arkaplan, (GENISLIK, YUKSEKLIK))
            
            # Etkileşim ipucu (E tuşu) yüklenir.
            self.press_e_img = pygame.image.load("assets/Images/UI/press_e.png").convert_alpha()
            self.press_e_img = pygame.transform.scale(self.press_e_img, (40, 40))
        except Exception as e:
            # HATA TOLERANSI: Dosya yükleme hatasında sistemin çalışmaya devam etmesi sağlanır.
            print(f"Görsel yükleme hatası: {e}")
            self.arkaplan = pygame.Surface((GENISLIK, YUKSEKLIK)); self.arkaplan.fill((45, 30, 60))
            self.press_e_img = pygame.Surface((30, 30)); self.press_e_img.fill(ALTIN)

        self.static_npcs = pygame.sprite.Group()
        self.setup_sprites()

    def setup_sprites(self):
        """Beren karakterini (NPC) odaya yerleştirir ve yönünü otomatik ayarlar."""
        base_path = "assets/Images/Characters/NPC/bolum7_npc/"
        
        # TEKNİK DETAY: 'ters_cevir=True' parametresi NPC sınıfı tarafından algılanarak
        # karakterin görselini yatayda aynalar, böylece karakter sola (oyuncuya) bakar.
        self.beren = NPC(800, 600, {'idle': base_path + "npc1_idle/"}, boyut=(200, 200), ters_cevir= True)
        
        self.static_npcs.add(self.beren)
        
        # Oyuncu ve NPC'nin ayak hizası tutarlılık için eşitlenir.
        self.player.rect.bottom = self.beren.rect.bottom

    def run(self):
        """Bölümün ana mantıksal akışını ve çizim süreçlerini yönetir."""
        keys = pygame.key.get_pressed()
        
        # --- MANTIK VE HAREKET AKIŞI ALGORİTMASI ---
        if self.intro_mesaji_aktif:
            # Görev mesajı okunurken oyuncu hareketi yazılımsal olarak kısıtlanır.
            self.player.input_enabled = False
            if keys[pygame.K_SPACE]:
                self.intro_mesaji_aktif = False
                pygame.time.delay(200)
        else:
            # Karakter Beren'e yeterince yaklaştığında (x=620) otomatik durdurulur.
            if self.player.rect.x >= 620 and not self.bulusma_gerceklesti:
                self.player.rect.x = 620
                self.bulusma_gerceklesti = True
                self.player.direction.x = 0
                
                # Karakterin durduğunda sağa (muhatabına) bakması sağlanır.
                if hasattr(self.player, 'facing_right'):
                    self.player.facing_right = True

            # Hareket Kilidi: Diyalog aktifken veya buluşma anında kontrol kilitlenir.
            if self.bulusma_gerceklesti or self.diyalog_aktif or self.diyalog_bitti:
                self.player.input_enabled = False
            else:
                self.player.input_enabled = True

        # BaseLevel'dan miras alınan tuş yönetim sistemini (seçenekler) çalıştırır.
        self.input_yonetimi(keys)

        # --- ÇİZİMLER VE KATMAN YÖNETİMİ ---
        self.pencere.blit(self.arkaplan, (0, 0))
        
        # NPC grubunun güncellenmesi (ters_cevir mantığı update içinde işlenir).
        self.static_npcs.update() 
        self.static_npcs.draw(self.pencere)
        
        # Oyuncu sprite'ının güncellenmesi ve ekrana yansıtılması.
        self.player_group.update()
        self.player_group.draw(self.pencere)

        # --- ETKİLEŞİM TETİKLEME ---
        # Oyuncu Beren'in yanına ulaştığında etkileşim ikonu aktifleşir.
        if self.bulusma_gerceklesti and not self.diyalog_aktif and not self.diyalog_bitti:
            # İpucu görseli Beren'in başı hizasında dinamik olarak konumlandırılır.
            self.pencere.blit(self.press_e_img, (self.beren.rect.centerx - 20, self.beren.rect.top - 50))
            if keys[pygame.K_e]:
                self.diyalog_aktif = True # Diyalog motorunu başlatır.

        # --- KULLANICI ARAYÜZÜ (UI) KATMANLARI ---
        if self.intro_mesaji_aktif:
            self.bilgi_kutusu_ciz("Beren senden başka bir arkadaşının telefon numarasını istiyor. Onunla diyaloğa geç!")
        elif self.diyalog_aktif:
            # JSON'dan çekilen senaryo metinleri "Beren" ismiyle ekrana yansıtılır.
            self.diyalog_kutusu_ciz(npc_ismi="Beren")
        
        # Bölüm analizi tamamlandığında Level 8'e geçiş için ESC tuşunu bekler.
        if self.diyalog_bitti:
            self.feedback_ekrani_ciz() # Seçimlerin etik analizini gösterir.
            if keys[pygame.K_ESCAPE]: return 8 

        return 7

    def bilgi_kutusu_ciz(self, mesaj):
        """
        Dinamik satır kaydırmalı bilgilendirme kutusu.
        'metni_sar' algoritması ile metnin kutu dışına taşması engellenir.
        """
        kutu_g, kutu_y = 600, 160
        kutu_rect = pygame.Rect(GENISLIK//2 - kutu_g//2, YUKSEKLIK//2 - 200, kutu_g, kutu_y)
        
        # Saydam arka plan katmanı tasarımı.
        s_surf = pygame.Surface((kutu_rect.width, kutu_rect.height))
        s_surf.set_alpha(225); s_surf.fill((20, 20, 40))
        self.pencere.blit(s_surf, (kutu_rect.x, kutu_rect.y))
        
        # Altın sarısı çerçeve çizimi.
        pygame.draw.rect(self.pencere, ALTIN, kutu_rect, 3)
        
        # Metni sarma algoritması ile içeriği kutu sınırları içinde tutar.
        satirlar = self.metni_sar(mesaj, self.font_ana, kutu_rect.width - 60)
        y_fark = kutu_rect.y + 40
        for satir in satirlar:
            txt = self.font_ana.render(satir, True, BEYAZ)
            self.pencere.blit(txt, (kutu_rect.x + 30, y_fark))
            y_fark += 35
        
        # Alt bilgi yönlendirme notu.
        alt_not = self.font_secenek.render("[ DEVAM ETMEK İÇİN SPACE TUŞUNA BASIN ]", True, ALTIN)
        self.pencere.blit(alt_not, (kutu_rect.centerx - alt_not.get_width() // 2, kutu_rect.bottom - 40))
