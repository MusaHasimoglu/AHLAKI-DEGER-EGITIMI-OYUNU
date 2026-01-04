import pygame
from settings import *
from npc import NPC
from level_manager import BaseLevel

class Level2(BaseLevel):
    """
    Bölüm 2: Sınav Sahnesi.
    OOP KRİTERİ: Kalıtım (Inheritance). BaseLevel ata sınıfından miras alınarak
    diyalog ve analiz sistemleri projeye dahil edilmiştir.
    """
    def __init__(self, pencere, player, player_group):
        # 'bolum2' anahtarı ile JSON dosyasındaki senaryo verileri yüklenir.
        super().__init__(pencere, player, player_group, "bolum2")
        
        # --- DURUM YÖNETİMİ (State Machine) ---
        self.evre = "sinav_basladi"
        self.intro_mesaji_aktif = True  # İlk bilgilendirme kutusu kontrolü
        self.siraya_oturdu = False      # Karakterin hedef noktaya ulaşıp ulaşmadığı
        self.ikinci_mesaj_aktif = False # Arkadaştan gelen seslenme uyarısı
        self.ikinci_mesaj_goruldu = False 
        
        # --- GÖRSEL VARLIKLAR VE HATA YÖNETİMİ ---
        try:
            # Sınıf ortamı arka planı yüklenir
            self.arkaplan = pygame.image.load("assets/Images/Backgrounds/2-sinif.png").convert()
            self.arkaplan = pygame.transform.scale(self.arkaplan, (GENISLIK, YUKSEKLIK))
            self.press_e_img = pygame.image.load("assets/Images/UI/press_e.png").convert_alpha()
            self.press_e_img = pygame.transform.scale(self.press_e_img, (40, 40))
        except Exception as e:
            # Dosya yükleme hatalarında sistemin çökmemesi için varsayılan yüzeyler oluşturulur.
            print(f"Hata: {e}")
            self.arkaplan = pygame.Surface((GENISLIK, YUKSEKLIK)); self.arkaplan.fill((50, 50, 50))
            self.press_e_img = pygame.Surface((30, 30)); self.press_e_img.fill(ALTIN)

        self.static_npcs = pygame.sprite.Group() 
        self.setup_sprites()

    def setup_sprites(self):
        """Sınıftaki diğer karakterleri (NPC) sahnede konumlandırır."""
        base_path = "assets/Images/Characters/NPC/bolum2_npc/"
        # Sınavda kopya teklif edecek olan arkadaş (Kerem) karakteri oluşturulur.
        self.arkadas = NPC(720, 595, {'idle': base_path + "npc1_idle/"}, boyut=(200, 200))
        self.static_npcs.add(self.arkadas)

    def run(self):
        """Bölümün ana mantıksal döngüsü."""
        keys = pygame.key.get_pressed()
        
        # --- HAREKET VE MESAJ KONTROL ALGORİTMASI ---
        # 1. Aşama: Başlangıç uyarısı aktifken hareket engellenir.
        if self.intro_mesaji_aktif:
            self.player.input_enabled = False 
            if keys[pygame.K_SPACE]:
                self.intro_mesaji_aktif = False
                pygame.time.delay(200)
        
        # 2. Aşama: İkinci bilgilendirme mesajı yönetimi.
        elif self.ikinci_mesaj_aktif:
            self.player.input_enabled = False
            if keys[pygame.K_SPACE]:
                self.ikinci_mesaj_aktif = False
                self.ikinci_mesaj_goruldu = True
                pygame.time.delay(200)
                
        else:
            # Karakterin hedef sıraya (x=470) ulaşıp ulaşmadığının kontrolü.
            if self.player.rect.x >= 470 and not self.siraya_oturdu:
                self.player.rect.x = 470 
                self.siraya_oturdu = True
                
                # Karakterin sıraya oturduğunda arkadaki arkadaşına bakması sağlanır.
                self.player.direction.x = 0 
                if hasattr(self.player, 'facing_right'):
                    self.player.facing_right = False 
                
                # Karakter durduğu an ikinci bilgilendirme mesajı tetiklenir.
                if not self.ikinci_mesaj_goruldu:
                    self.ikinci_mesaj_aktif = True

            # Karakter sıraya oturduğunda veya diyalog penceresi açıkken kontrol kilidi uygulanır.
            if self.siraya_oturdu or self.diyalog_aktif or self.diyalog_bitti or self.ikinci_mesaj_aktif:
                self.player.input_enabled = False
            else:
                self.player.input_enabled = True

        # Klavye girişlerini işle (BaseLevel'dan miras alınan metod)
        self.input_yonetimi(keys)
        self.update_logic()

        # --- GÖRSEL KATMANLARIN ÇİZİMİ ---
        self.pencere.blit(self.arkaplan, (0, 0))
        self.static_npcs.update()
        self.static_npcs.draw(self.pencere)
        self.player_group.update()
        self.player_group.draw(self.pencere)

        # --- ETKİLEŞİM TETİKLEME ---
        # Oyuncu sıraya oturduktan sonra 'E' tuşu ipucu aktif hale getirilir.
        if self.siraya_oturdu and not self.ikinci_mesaj_aktif and not self.diyalog_aktif and not self.diyalog_bitti:
            self.pencere.blit(self.press_e_img, (self.arkadas.rect.centerx - 20, self.arkadas.rect.top - 60))
            if keys[pygame.K_e]:
                self.diyalog_aktif = True 

        # --- ARAYÜZ YÖNETİMİ ---
        if self.intro_mesaji_aktif:
            self.bilgi_kutusu_ciz("Sınav başlıyor. Arkadaşının önündeki sıraya geç hemen!")
        
        elif self.ikinci_mesaj_aktif:
            self.bilgi_kutusu_ciz("Arka sıradan Kerem sana sesleniyor. Diyaloğa geç!")
            
        elif self.diyalog_aktif:
            # JSON dosyasındaki 'bolum2' verileri Kerem ismiyle ekrana yansıtılır.
            self.diyalog_kutusu_ciz(npc_ismi="Kerem")
        
        # Bölüm bittiyse geri bildirim ekranını göster ve sonraki bölüme geçiş sinyali ver.
        if self.diyalog_bitti:
            self.feedback_ekrani_ciz()
            if keys[pygame.K_ESCAPE]: return 3 # Bölüm 3'e geçiş

        return 2

    def bilgi_kutusu_ciz(self, mesaj):
        """
        Dinamik satır kaydırmalı bilgilendirme kutusu.
        'metni_sar' algoritmasını kullanarak metni kutu genişliğine uyarlar.
        """
        kutu_g, kutu_y = 600, 160
        kutu_rect = pygame.Rect(GENISLIK//2 - kutu_g//2, YUKSEKLIK//2 - 200, kutu_g, kutu_y)
        
        # Yarı saydam arka plan tasarımı
        s_surf = pygame.Surface((kutu_rect.width, kutu_rect.height))
        s_surf.set_alpha(225); s_surf.fill((20, 20, 40))
        self.pencere.blit(s_surf, (kutu_rect.x, kutu_rect.y))
        
        # Altın sarısı çerçeve çizimi
        pygame.draw.rect(self.pencere, ALTIN, kutu_rect, 3)
        
        # Metin sarma algoritması ile içeriğin kutuya sığdırılması
        satirlar = self.metni_sar(mesaj, self.font_ana, kutu_rect.width - 60)
        y_fark = kutu_rect.y + 40
        for satir in satirlar:
            txt = self.font_ana.render(satir, True, BEYAZ)
            self.pencere.blit(txt, (kutu_rect.x + 30, y_fark))
            y_fark += 35
            
        alt_not = self.font_secenek.render("[ DEVAM ETMEK İÇİN SPACE TUŞUNA BASIN ]", True, ALTIN)
        self.pencere.blit(alt_not, (kutu_rect.centerx - alt_not.get_width() // 2, kutu_rect.bottom - 40))

    def update_logic(self):
        """NPC veya çevre dinamiklerini güncellemek için kullanılan boş metod yapısı."""
        pass
