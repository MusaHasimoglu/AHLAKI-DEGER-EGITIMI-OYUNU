import pygame
from settings import *
from npc import NPC
from level_manager import BaseLevel

class Level3(BaseLevel):
    """
    Bölüm 3: Okul Çıkışı / Şehir Parkı.
    OOP KRİTERİ: Kalıtım (Inheritance). BaseLevel ata sınıfından miras alarak
    dinamik diyalog motoru ve metin sarma algoritmalarını kullanır.
    """
    def __init__(self, pencere, player, player_group):
        # 'bolum3' anahtarı ile JSON dosyasındaki senaryo verileri yüklenir.
        super().__init__(pencere, player, player_group, "bolum3")
        
        # --- DURUM YÖNETİMİ (State Management) ---
        # Oyunun mantıksal akışını kontrol eden bayraklar.
        self.intro_mesaji_aktif = True      # Başlangıç bilgilendirme kutusu
        self.bulusma_gerceklesti = False    # Karakterin Selim'in yanına varıp varmadığı
        
        # --- ARKAPLAN VE GÖRSEL VARLIKLAR ---
        try:
            # Şehir parkı arka planı yüklenir.
            self.arkaplan = pygame.image.load("assets/Images/Backgrounds/3-park.png").convert()
            self.arkaplan = pygame.transform.scale(self.arkaplan, (GENISLIK, YUKSEKLIK))
            
            # Etkileşim göstergesi (E tuşu) yüklenir.
            self.press_e_img = pygame.image.load("assets/Images/UI/press_e.png").convert_alpha()
            self.press_e_img = pygame.transform.scale(self.press_e_img, (40, 40))
        except Exception as e:
            # HATA TOLERANSI: Görsel bulunamazsa oyunun çökmemesi için alternatif yüzey oluşturulur.
            print(f"Görsel yükleme hatası: {e}")
            self.arkaplan = pygame.Surface((GENISLIK, YUKSEKLIK)); self.arkaplan.fill((80, 100, 80))
            self.press_e_img = pygame.Surface((30, 30)); self.press_e_img.fill(ALTIN)

        self.static_npcs = pygame.sprite.Group()
        self.setup_sprites()

    def setup_sprites(self):
        """NPC'leri sahneye yerleştirir ve zemin hizalamasını (Y-ekseni) yapar."""
        base_path = "assets/Images/Characters/NPC/bolum3_npc/"
        
        # Sorumluluk ikilemini tetikleyecek Selim karakteri oluşturulur.
        self.selim = NPC(950, 620, {'idle': base_path + "npc1_idle/"}, boyut=(200, 200))
        self.static_npcs.add(self.selim)
        
        # Görsel derinlik ve tutarlılık için oyuncunun ayak hizası Selim'e eşitlenir.
        self.player.rect.bottom = self.selim.rect.bottom

    def run(self):
        """Bölümün ana mantığını ve çizim işlemlerini yöneten merkezi metod."""
        keys = pygame.key.get_pressed()
        
        # --- HAREKET VE DURMA MANTIĞI ALGORİTMASI ---
        if self.intro_mesaji_aktif:
            # Bilgilendirme mesajı okunurken oyuncu hareketi engellenir.
            self.player.input_enabled = False
            if keys[pygame.K_SPACE]:
                self.intro_mesaji_aktif = False
                pygame.time.delay(200)
        else:
            # Karakter Selim'e yeterince yaklaştığında (x=750) otomatik olarak durdurulur.
            if self.player.rect.x >= 750 and not self.bulusma_gerceklesti:
                self.player.rect.x = 750
                self.bulusma_gerceklesti = True
                self.player.direction.x = 0
                
                # Karakterin durduğunda muhatabına (sağa) bakması sağlanır.
                if hasattr(self.player, 'facing_right'):
                    self.player.facing_right = True

            # Hareket Kilidi: Buluşma anında veya diyalog aktifken kontrol devre dışı bırakılır.
            if self.bulusma_gerceklesti or self.diyalog_aktif or self.diyalog_bitti:
                self.player.input_enabled = False
            else:
                self.player.input_enabled = True

        # BaseLevel'dan miras alınan tuş yönetim sistemini çalıştırır.
        self.input_yonetimi(keys)

        # --- GÖRSEL KATMANLARIN ÇİZİMİ ---
        self.pencere.blit(self.arkaplan, (0, 0))
        self.static_npcs.update()
        self.static_npcs.draw(self.pencere)
        self.player_group.update()
        self.player_group.draw(self.pencere)

        # --- ETKİLEŞİM TETİKLEME ---
        # Oyuncu ve Selim yan yana geldiğinde 'E' tuşu ipucu aktif hale getirilir.
        if self.bulusma_gerceklesti and not self.diyalog_aktif and not self.diyalog_bitti:
            # İpucu görseli NPC'nin başının üstünde dinamik olarak konumlandırılır.
            self.pencere.blit(self.press_e_img, (self.selim.rect.centerx - 20, self.selim.rect.top - 50))
            if keys[pygame.K_e]:
                self.diyalog_aktif = True

        # --- KULLANICI ARAYÜZÜ (UI) KATMANLARI ---
        if self.intro_mesaji_aktif:
            self.bilgi_kutusu_ciz("Selim ileride üzgün bir halde bekliyor. Nesi olduğunu öğrenmek için yanına git.")
        elif self.diyalog_aktif:
            # JSON dosyasındaki diyalog ağacı Selim ismiyle ekrana yansıtılır.
            self.diyalog_kutusu_ciz(npc_ismi="Selim")
        
        # Bölüm analizi tamamlandığında Level 4'e geçiş sinyali gönderilir.
        if self.diyalog_bitti:
            self.feedback_ekrani_ciz()
            if keys[pygame.K_ESCAPE]: return 4 

        return 3

    def bilgi_kutusu_ciz(self, mesaj):
        """Bölüm 1 standartlarına uygun, dinamik satır kaydırmalı bilgilendirme kutusu."""
        kutu_g, kutu_y = 600, 160
        kutu_rect = pygame.Rect(GENISLIK//2 - kutu_g//2, YUKSEKLIK//2 - 200, kutu_g, kutu_y)
        
        # Saydam arka plan katmanı (Alpha Blending)
        s_surf = pygame.Surface((kutu_rect.width, kutu_rect.height))
        s_surf.set_alpha(225); s_surf.fill((20, 20, 40))
        self.pencere.blit(s_surf, (kutu_rect.x, kutu_rect.y))
        
        # Tasarıma uygun altın sarısı çerçeve
        pygame.draw.rect(self.pencere, ALTIN, kutu_rect, 3)
        
        # Metni sarma algoritması ile içeriği kutu sınırlarına hapseder.
        satirlar = self.metni_sar(mesaj, self.font_ana, kutu_rect.width - 60)
        y_fark = kutu_rect.y + 40
        for satir in satirlar:
            txt = self.font_ana.render(satir, True, BEYAZ)
            self.pencere.blit(txt, (kutu_rect.x + 30, y_fark))
            y_fark += 35
        
        # Kullanıcıyı yönlendiren alt bilgi notu
        alt_not = self.font_secenek.render("[ DEVAM ETMEK İÇİN SPACE TUŞUNA BASIN ]", True, ALTIN)
        self.pencere.blit(alt_not, (kutu_rect.centerx - alt_not.get_width() // 2, kutu_rect.bottom - 40))
