import pygame
from settings import *
from level_manager import BaseLevel

class Level8(BaseLevel):
    """
    Bölüm 8: Sokak - Para Bulma.
    OOP KRİTERİ: Kalıtım (Inheritance). BaseLevel ata sınıfından miras alınarak 
    JSON tabanlı senaryo motoru ve merkezi UI sistemleri kullanılır.
    TEMATİK ODAK: Sahipsiz bir eşya bulunduğunda dürüstlük ve empati ilkelerine 
    uygun karar verme becerisi.
    """
    def __init__(self, pencere, player, player_group):
        # 'bolum8' anahtarı ile JSON dosyasındaki sokak senaryosu yüklenir.
        super().__init__(pencere, player, player_group, "bolum8")
        
        # --- DURUM KONTROLLERİ (State Management) ---
        self.intro_mesaji_aktif = True # Başlangıç görevi uyarısı
        self.olay_yerinde = False      # Oyuncunun cüzdanın yanına varıp varmadığı
        
        # --- ARKAPLAN VE GÖRSEL VARLIKLAR ---
        try:
            # Sokak arka planı ve cüzdan görseli yüklenir.
            self.arkaplan = pygame.image.load("assets/Images/Backgrounds/8-para_bulma.png").convert()
            self.arkaplan = pygame.transform.scale(self.arkaplan, (GENISLIK, YUKSEKLIK))
            
            # Cüzdan objesi (Interacting Object) yüklenir ve ölçeklenir.
            self.cuzdan_img = pygame.image.load("assets/Images/UI/wallet.png").convert_alpha()
            self.cuzdan_img = pygame.transform.scale(self.cuzdan_img, (50, 50))
            
            # Cüzdanın zemindeki konumu belirlenir.
            self.cuzdan_rect = self.cuzdan_img.get_rect(midbottom=(650, 600))
            
            # Etkileşim ipucu (E tuşu) yüklenir.
            self.press_e_img = pygame.image.load("assets/Images/UI/press_e.png").convert_alpha()
            self.press_e_img = pygame.transform.scale(self.press_e_img, (40, 40))
        except Exception as e:
            # HATA TOLERANSI: Dosya eksikliğinde sistemin çalışmaya devam etmesi sağlanır.
            print(f"Görsel yükleme hatası: {e}")
            self.arkaplan = pygame.Surface((GENISLIK, YUKSEKLIK)); self.arkaplan.fill((60, 60, 80))
            self.cuzdan_img = pygame.Surface((40, 40)); self.cuzdan_img.fill((139, 69, 19))
            self.cuzdan_rect = self.cuzdan_img.get_rect(midbottom=(650, 600))
            self.press_e_img = pygame.Surface((30, 30)); self.press_e_img.fill(ALTIN)

        # Bu bölümde fiziksel bir NPC bulunmadığından grup boş bırakılır.
        self.static_npcs = pygame.sprite.Group()

    def run(self):
        """Bölümün ana mantıksal akışını ve grafik katmanlarını yönetir."""
        keys = pygame.key.get_pressed()
        
        # --- MESAJ VE MANTIK AKIŞI ALGORİTMASI ---
        if self.intro_mesaji_aktif:
            # Görev yönergesi okunurken oyuncu hareketi yazılımsal olarak kilitlenir.
            self.player.input_enabled = False
            if keys[pygame.K_SPACE]:
                self.intro_mesaji_aktif = False
                pygame.time.delay(200)
        else:
            # Karakter cüzdanın yanına (x=450) ulaştığında otomatik olarak durdurulur.
            if self.player.rect.x >= 450 and not self.olay_yerinde:
                self.player.rect.x = 450
                self.olay_yerinde = True
                self.player.direction.x = 0
                if hasattr(self.player, 'facing_right'):
                    self.player.facing_right = True

            # Hareket Kilidi: Cüzdanın yanındayken veya diyalog aktifken kontrol kısıtlanır.
            if self.olay_yerinde or self.diyalog_aktif or self.diyalog_bitti:
                self.player.input_enabled = False
            else:
                self.player.input_enabled = True

        # BaseLevel'dan miras alınan tuş yönetim sistemini çalıştırır.
        self.input_yonetimi(keys)

        # --- GÖRSEL KATMANLARIN ÇİZİMİ ---
        self.pencere.blit(self.arkaplan, (0, 0))
        self.pencere.blit(self.cuzdan_img, self.cuzdan_rect)
        
        # Oyuncu sprite'ının güncellenmesi ve yansıtılması.
        self.player_group.update()
        self.player_group.draw(self.pencere)

        # --- ETKİLEŞİM TETİKLEME (Object Interaction) ---
        # Oyuncu cüzdana ulaştığında 'E' tuşu ipucu cüzdanın üstünde belirir.
        if self.olay_yerinde and not self.diyalog_aktif and not self.diyalog_bitti:
            self.pencere.blit(self.press_e_img, (self.cuzdan_rect.centerx - 20, self.cuzdan_rect.top - 50))
            if keys[pygame.K_e]:
                self.diyalog_aktif = True # Karar verme sürecini (İç Ses) başlatır.

        # --- KULLANICI ARAYÜZÜ (UI) KATMANLARI ---
        if self.intro_mesaji_aktif:
            self.bilgi_kutusu_ciz("Yolun ilerisinde yerde bir şey duruyor ne olduğuna bak!")
        elif self.diyalog_aktif:
            # Bu bölümde "İç Ses" mekanizması kullanılarak oyuncunun kendiyle 
            # yüzleşmesi sağlanır (Önemli pedagojik unsur).
            self.diyalog_kutusu_ciz(npc_ismi="İç Ses")
        
        # Diyalog sonlandığında etik analiz ekranını göster ve ESC ile Bölüm 9'a geç.
        if self.diyalog_bitti:
            self.feedback_ekrani_ciz()
            if keys[pygame.K_ESCAPE]: return 9 

        return 8

    def bilgi_kutusu_ciz(self, mesaj):
        """
        Dinamik satır kaydırmalı bilgilendirme kutusu tasarımı.
        'metni_sar' algoritması ile metnin kutu dışına taşması engellenir.
        """
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
        
        # Alt bilgi yönlendirme notu.
        alt_not = self.font_secenek.render("[ DEVAM ETMEK İÇİN SPACE TUŞUNA BASIN ]", True, ALTIN)
        self.pencere.blit(alt_not, (kutu_rect.centerx - alt_not.get_width() // 2, kutu_rect.bottom - 40))
