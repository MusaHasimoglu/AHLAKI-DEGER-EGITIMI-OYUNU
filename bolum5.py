import pygame
from settings import *
from npc import NPC
from level_manager import BaseLevel

class Level5(BaseLevel):
    """
    Bölüm 5: Market - Dürüstlük Testi.
    OOP KRİTERİ: Kalıtım (Inheritance). BaseLevel sınıfından miras alınarak 
    merkezi sistemler (diyalog, analiz, metin sarma) bu bölüme entegre edilir.
    Bu sahne, kasiyerin hata yapması sonucu oluşan bir dürüstlük ikilemini işler.
    """
    def __init__(self, pencere, player, player_group):
        # 'bolum5' anahtarı ile JSON dosyasındaki ilgili senaryo yüklenir.
        super().__init__(pencere, player, player_group, "bolum5")
        
        # --- DURUM KONTROLLERİ (State Machine) ---
        self.intro_mesaji_aktif = True
        self.fark_ettim_mesaji_aktif = False # Etik ikilemin fark edilme anı uyarısı
        self.kasaya_geldi = False
        
        # --- ARKAPLAN VE GÖRSELLER ---
        try:
            # Market iç mekanı arka planı yüklenir.
            self.arkaplan = pygame.image.load("assets/Images/Backgrounds/5-market.png").convert()
            self.arkaplan = pygame.transform.scale(self.arkaplan, (GENISLIK, YUKSEKLIK))
            
            # Etkileşim göstergesi (E tuşu)
            self.press_e_img = pygame.image.load("assets/Images/UI/press_e.png").convert_alpha()
            self.press_e_img = pygame.transform.scale(self.press_e_img, (40, 40))
        except Exception as e:
            # HATA TOLERANSI: Dosya yüklenemezse sistemin çökmemesi için alternatif yüzey oluşturulur.
            print(f"Hata: {e}")
            self.arkaplan = pygame.Surface((GENISLIK, YUKSEKLIK)); self.arkaplan.fill((50, 50, 70))
            self.press_e_img = pygame.Surface((30, 30)); self.press_e_img.fill(ALTIN)

        self.static_npcs = pygame.sprite.Group()
        self.setup_sprites()

    def setup_sprites(self):
        """Kasiyer NPC'sini kasanın arkasına sabit olarak yerleştirir."""
        base_path = "assets/Images/Characters/NPC/bolum5_npc/"
        
        # Kasiyerin koordinatları sahnede kasanın arkasında kalacak şekilde ayarlanmıştır.
        self.kasiyer = NPC(405, 513, {'idle': base_path + "npc1_idle/"}, boyut=(200, 200))
        self.static_npcs.add(self.kasiyer)

    def run(self):
        """Bölümün ana mantıksal döngüsü ve grafiksel katman yönetimi."""
        keys = pygame.key.get_pressed()
        
        # --- MESAJ VE MANTIK KONTROL ALGORİTMASI ---
        if self.intro_mesaji_aktif:
            # Başlangıç bilgilendirmesi sırasında oyuncu hareketi engellenir.
            self.player.input_enabled = False
            if keys[pygame.K_SPACE]:
                self.intro_mesaji_aktif = False
                pygame.time.delay(200)
                
        elif self.fark_ettim_mesaji_aktif:
            # Etik ikilemin tetiklendiği uyarı mesajı süreci.
            self.player.input_enabled = False
            if keys[pygame.K_SPACE]:
                self.fark_ettim_mesaji_aktif = False
                pygame.time.delay(200)
        else:
            # Karakter kasaya (x=320) ulaştığında otomatik durdurulur ve diyalog evresine geçilir.
            if self.player.rect.x >= 320 and not self.kasaya_geldi:
                self.player.rect.x = 320
                self.kasaya_geldi = True
                self.player.direction.x = 0
                
                # Kasaya ulaşma anında ahlaki ikilemi oyuncuya bildiren uyarı tetiklenir.
                self.fark_ettim_mesaji_aktif = True 
                if hasattr(self.player, 'facing_right'):
                    self.player.facing_right = True

            # Hareket kilidi: Oyuncu kasaya vardığında veya diyalog ekranındayken serbest yürüyüş kapatılır.
            if self.kasaya_geldi or self.diyalog_aktif or self.diyalog_bitti or self.fark_ettim_mesaji_aktif:
                self.player.input_enabled = False
            else:
                self.player.input_enabled = True

        # BaseLevel'dan miras alınan tuş yönetim metodunu (seçenekler 1-2) çalıştırır.
        self.input_yonetimi(keys)

        # --- ÇİZİMLER VE KATMAN YÖNETİMİ ---
        self.pencere.blit(self.arkaplan, (0, 0))
        
        # Kasiyerin animasyonunun güncellenmesi ve oyuncuya doğru bakması (flipping) sağlanır.
        self.static_npcs.update()
        self.kasiyer.image = pygame.transform.flip(self.kasiyer.image, True, False)
        
        self.static_npcs.draw(self.pencere)
        self.player_group.update()
        self.player_group.draw(self.pencere)

        # --- ETKİLEŞİM TETİKLEME ---
        # Oyuncu kasaya vardığında ve tüm bilgilendirmeler kapandığında 'E' tuşu ipucu görünür.
        if self.kasaya_geldi and not self.fark_ettim_mesaji_aktif and not self.diyalog_aktif and not self.diyalog_bitti:
            self.pencere.blit(self.press_e_img, (self.kasiyer.rect.centerx - 20, self.kasiyer.rect.top - 50))
            if keys[pygame.K_e]:
                self.diyalog_aktif = True

        # --- KULLANICI ARAYÜZÜ (UI) KATMANLARI ---
        if self.intro_mesaji_aktif:
            self.bilgi_kutusu_ciz("Marketten bir şeyler aldın. Şimdi parasını ödeme vakti geldi kasaya git!")
        elif self.fark_ettim_mesaji_aktif:
            # Senaryonun merkezindeki ahlaki farkındalık uyarısı.
            self.bilgi_kutusu_ciz("Kasiyerin sana fazla para üstü verdiğini fark ettin.")
        elif self.diyalog_aktif:
            # JSON dosyasındaki diyalog ağacı "Kasiyer" ismiyle yansıtılır.
            self.diyalog_kutusu_ciz(npc_ismi="Kasiyer")
        
        # Diyalog sonlandığında etik analiz ekranı çizilir ve ESC ile Bölüm 6'ya geçiş yapılır.
        if self.diyalog_bitti:
            self.feedback_ekrani_ciz()
            if keys[pygame.K_ESCAPE]: return 6 

        return 5

    def bilgi_kutusu_ciz(self, mesaj):
        """Dinamik satır kaydırmalı standart uyarı kutusu tasarımı."""
        kutu_g, kutu_y = 600, 160
        kutu_rect = pygame.Rect(GENISLIK//2 - kutu_g//2, YUKSEKLIK//2 - 200, kutu_g, kutu_y)
        
        # Saydam arka plan katmanı (HUD tasarımı)
        s_surf = pygame.Surface((kutu_rect.width, kutu_rect.height))
        s_surf.set_alpha(225); s_surf.fill((20, 20, 40))
        self.pencere.blit(s_surf, (kutu_rect.x, kutu_rect.y))
        
        # Altın sarısı çerçeve
        pygame.draw.rect(self.pencere, ALTIN, kutu_rect, 3)
        
        # Metni sarma algoritması ile içeriğin kutu sınırları içinde kalması sağlanır.
        satirlar = self.metni_sar(mesaj, self.font_ana, kutu_rect.width - 60)
        y_fark = kutu_rect.y + 40
        for satir in satirlar:
            txt = self.font_ana.render(satir, True, BEYAZ)
            self.pencere.blit(txt, (kutu_rect.x + 30, y_fark))
            y_fark += 35
        
        # Alt bilgi yönlendirme notu
        alt_not = self.font_secenek.render("[ DEVAM ETMEK İÇİN SPACE TUŞUNA BASIN ]", True, ALTIN)
        self.pencere.blit(alt_not, (kutu_rect.centerx - alt_not.get_width() // 2, kutu_rect.bottom - 40))
