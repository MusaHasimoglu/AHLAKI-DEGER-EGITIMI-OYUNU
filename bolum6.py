import pygame
from settings import *
from level_manager import BaseLevel

class Level6(BaseLevel):
    """
    Bölüm 6: Trafik Sahnesi.
    OOP KRİTERİ: Kalıtım (Inheritance). BaseLevel ata sınıfından miras alınarak 
    JSON tabanlı senaryo yönetimi ve merkezi UI sistemleri kullanılır[cite: 77, 153].
    TEMATİK ODAK: Trafik kuralları ve başkalarının haklarına saygı duyma[cite: 12, 51].
    """
    def __init__(self, pencere, player, player_group):
        # 'bolum6' anahtarı ile JSON senaryosu yüklenir.
        # Bu yaklaşım veriyi koddan ayırarak modülerliği sağlar[cite: 82, 153].
        super().__init__(pencere, player, player_group, "bolum6")
        
        # --- DURUM YÖNETİMİ (State Management) ---
        self.intro_mesaji_aktif = True # Başlangıç görevi uyarısı
        self.gecit_mesaji_aktif = False # İhlali fark etme anı uyarısı
        self.olay_yerinde = False      # Oyuncunun yaya geçidine varıp varmadığı
        
        # --- ARKAPLAN VE GÖRSEL VARLIKLAR ---
        try:
            # Şehir trafiği arka planı yüklenir[cite: 118].
            self.arkaplan = pygame.image.load("assets/Images/Backgrounds/6-trafik.png").convert()
            self.arkaplan = pygame.transform.scale(self.arkaplan, (GENISLIK, YUKSEKLIK))
            self.press_e_img = pygame.image.load("assets/Images/UI/press_e.png").convert_alpha()
            self.press_e_img = pygame.transform.scale(self.press_e_img, (40, 40))
        except Exception as e:
            # HATA TOLERANSI: Görsel bulunamazsa sistemin çökmemesi için alternatif yüzeyler oluşturulur[cite: 161].
            print(f"Hata: {e}")
            self.arkaplan = pygame.Surface((GENISLIK, YUKSEKLIK)); self.arkaplan.fill((80, 80, 80))
            self.press_e_img = pygame.Surface((30, 30)); self.press_e_img.fill(ALTIN)

        # Bu bölümde fiziksel bir NPC sprite'ı bulunmadığından grup boş bırakılır.
        self.static_npcs = pygame.sprite.Group()

    def run(self):
        """Bölümün ana mantıksal akışını ve grafiksel katmanlarını yönetir."""
        keys = pygame.key.get_pressed()
        
        # --- MANTIK VE HAREKET KONTROL ALGORİTMASI ---
        if self.intro_mesaji_aktif:
            # Başlangıç mesajı okunurken oyuncu hareketi yazılımsal olarak kilitlenir.
            self.player.input_enabled = False
            if keys[pygame.K_SPACE]:
                self.intro_mesaji_aktif = False
                pygame.time.delay(200)
                
        elif self.gecit_mesaji_aktif:
            # İhlal fark edildiğinde çıkan uyarı süreci.
            self.player.input_enabled = False
            if keys[pygame.K_SPACE]:
                self.gecit_mesaji_aktif = False
                pygame.time.delay(200)
        else:
            # Karakter yaya geçidinin başlangıcına (x=370) ulaştığında durdurulur.
            if self.player.rect.x >= 370 and not self.olay_yerinde:
                self.player.rect.x = 370
                self.olay_yerinde = True
                self.player.direction.x = 0
                
                # Oyuncuya ahlaki ikilemi (araba ihlali) bildiren mesaj tetiklenir.
                self.gecit_mesaji_aktif = True 
                if hasattr(self.player, 'facing_right'):
                    self.player.facing_right = True

            # Hareket Kilidi: Etkileşim anında veya diyalog penceresi açıkken kontrol kısıtlanır.
            if self.olay_yerinde or self.diyalog_aktif or self.diyalog_bitti or self.gecit_mesaji_aktif:
                self.player.input_enabled = False
            else:
                self.player.input_enabled = True

        # BaseLevel'dan miras alınan tuş yönetim sistemini çalıştırır (1 ve 2 tuşları)[cite: 64].
        self.input_yonetimi(keys)

        # --- ÇİZİMLER ---
        self.pencere.blit(self.arkaplan, (0, 0))
        
        # Oyuncu sprite'ının güncellenmesi ve ekrana yansıtılması.
        self.player_group.update()
        self.player_group.draw(self.pencere)

        # --- ETKİLEŞİM (Background Interaction) ---
        # Bu bölümde NPC sprite'ı yerine, arkaplandaki arabanın koordinatları üzerinden etkileşim kurulur.
        if self.olay_yerinde and not self.gecit_mesaji_aktif and not self.diyalog_aktif and not self.diyalog_bitti:
            # 'E' ipucu simgesi arkaplandaki arabanın camı hizasında dinamik olarak çizilir.
            self.pencere.blit(self.press_e_img, (550, 450))
            if keys[pygame.K_e]:
                self.diyalog_aktif = True

        # --- KULLANICI ARAYÜZÜ (UI) KATMANLARI ---
        if self.intro_mesaji_aktif:
            self.bilgi_kutusu_ciz("Otomobillere kırmızı ışık yandı karşıya geçme zamanı!")
        elif self.gecit_mesaji_aktif:
            # Oyuncunun empati kurmasını ve duruma müdahale etmesini sağlayan yönerge.
            self.bilgi_kutusu_ciz("Yaya geçidinin üstünde duran araba yüzünden karşıya geçemiyorsun bir şeyler yap ve sürücüyle diyaloğa geç!")
        elif self.diyalog_aktif:
            # JSON'dan çekilen diyalog metinleri "Sürücü" ismiyle ekrana yansıtılır[cite: 63].
            self.diyalog_kutusu_ciz(npc_ismi="Sürücü")
        
        # Bölüm bittiyse etik analiz ekranını göster ve ESC ile Bölüm 7'ye geçiş yap.
        if self.diyalog_bitti:
            self.feedback_ekrani_ciz() # Seçimlerin ahlaki sonuçlarını gösterir[cite: 65].
            if keys[pygame.K_ESCAPE]: return 7 

        return 6

    def bilgi_kutusu_ciz(self, mesaj):
        """
        Dinamik satır kaydırmalı bilgilendirme kutusu.
        Metni kutu genişliğine uyarlamak için 'metni_sar' algoritması kullanılır[cite: 91, 157].
        """
        kutu_g, kutu_y = 600, 160
        kutu_rect = pygame.Rect(GENISLIK//2 - kutu_g//2, YUKSEKLIK//2 - 200, kutu_g, kutu_y)
        
        # Saydam arka plan katmanı (HUD tasarımı).
        s_surf = pygame.Surface((kutu_rect.width, kutu_rect.height))
        s_surf.set_alpha(225); s_surf.fill((20, 20, 40))
        self.pencere.blit(s_surf, (kutu_rect.x, kutu_rect.y))
        
        # Altın sarısı çerçeve çizimi.
        pygame.draw.rect(self.pencere, ALTIN, kutu_rect, 3)
        
        # Metni sarma algoritması ile içeriğin kutu sınırları içinde kalması sağlanır.
        satirlar = self.metni_sar(mesaj, self.font_ana, kutu_rect.width - 60)
        y_fark = kutu_rect.y + 40
        for satir in satirlar:
            txt = self.font_ana.render(satir, True, BEYAZ)
            self.pencere.blit(txt, (kutu_rect.x + 30, y_fark))
            y_fark += 35
        
        # Kullanıcıyı yönlendiren alt bilgi notu.
        alt_not = self.font_secenek.render("[ DEVAM ETMEK İÇİN SPACE TUŞUNA BASIN ]", True, ALTIN)
        self.pencere.blit(alt_not, (kutu_rect.centerx - alt_not.get_width() // 2, kutu_rect.bottom - 40))
