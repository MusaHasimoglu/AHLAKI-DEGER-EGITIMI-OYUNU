import pygame
from settings import *
from npc import NPC
from level_manager import BaseLevel

class Level9(BaseLevel):
    """
    Bölüm 9: Sahil - Çevre Bilinci.
    OOP KRİTERİ: Kalıtım (Inheritance). BaseLevel sınıfından miras alınarak 
    merkezi sistemler (diyalog, analiz, metin sarma) bu bölüme entegre edilir.
    Bu sahne, yere çöp atan bir yabancıya karşı gösterilecek ahlaki tutumu işler.
    """
    def __init__(self, pencere, player, player_group):
        # 'bolum9' anahtarı ile JSON dosyasındaki ilgili senaryo yüklenir.
        super().__init__(pencere, player, player_group, "bolum9")
        
        # --- DURUM KONTROLLERİ (State Machine) ---
        self.intro_mesaji_aktif = True
        self.olay_yerinde = False
        
        # --- ARKAPLAN VE GÖRSEL VARLIKLAR ---
        try:
            # Sahil/Park arka planı yüklenir.
            self.arkaplan = pygame.image.load("assets/Images/Backgrounds/9-yere_cöp.png").convert()
            self.arkaplan = pygame.transform.scale(self.arkaplan, (GENISLIK, YUKSEKLIK))
            
            # Yerdeki Şişe Görseli (Etkileşimi destekleyen görsel öğe)
            self.sise_img = pygame.image.load("assets/Images/UI/sise.png").convert_alpha()
            self.sise_img = pygame.transform.scale(self.sise_img, (160, 90))
            # Şişe, senaryo gereği NPC'nin önüne yerleştirilir.
            self.sise_rect = self.sise_img.get_rect(midbottom=(850, 600))
            
            # Etkileşim Simgesi (E tuşu)
            self.press_e_img = pygame.image.load("assets/Images/UI/press_e.png").convert_alpha()
            self.press_e_img = pygame.transform.scale(self.press_e_img, (40, 40))
        except Exception as e:
            # HATA TOLERANSI: Dosya yüklenemezse sistemin çökmemesi için alternatif yüzeyler oluşturulur.
            print(f"Hata: {e}")
            self.arkaplan = pygame.Surface((GENISLIK, YUKSEKLIK)); self.arkaplan.fill((50, 100, 50))
            self.sise_img = pygame.Surface((20, 40)); self.sise_img.fill((0, 200, 255))
            self.sise_rect = self.sise_img.get_rect(midbottom=(700, 650))
            self.press_e_img = pygame.Surface((30, 30)); self.press_e_img.fill(ALTIN)

        self.static_npcs = pygame.sprite.Group()
        self.setup_sprites()

    def setup_sprites(self):
        """Çöp atan NPC'yi sahnede konumlandırır."""
        base_path = "assets/Images/Characters/NPC/bolum9_npc/"
        
        # NPC, oyuncunun etkileşime geçeceği noktada bekler.
        self.cop_atan = NPC(780, 600, {'idle': base_path + "npc1_idle/"}, boyut=(200, 200), ters_cevir=False)
        self.static_npcs.add(self.cop_atan)
        
        # Oyuncu ve NPC'nin ayak hizası görsel bütünlük için eşitlenir.
        self.player.rect.bottom = self.cop_atan.rect.bottom

    def run(self):
        """Bölümün ana mantıksal döngüsü ve grafiksel katman yönetimi."""
        keys = pygame.key.get_pressed()
        
        # --- MANTIK AKIŞI ALGORİTMASI ---
        if self.intro_mesaji_aktif:
            # Görev yönergesi okunurken oyuncu hareketi engellenir.
            self.player.input_enabled = False
            if keys[pygame.K_SPACE]:
                self.intro_mesaji_aktif = False
                pygame.time.delay(200)
        else:
            # Karakter NPC'ye yeterince yaklaştığında (x=570) otomatik olarak durdurulur.
            if self.player.rect.x >= 570 and not self.olay_yerinde:
                self.player.rect.x = 570
                self.olay_yerinde = True
                self.player.direction.x = 0
                if hasattr(self.player, 'facing_right'):
                    self.player.facing_right = True

            # Hareket kilidi: Olay anında veya diyalog ekranındayken serbest yürüyüş kapatılır.
            if self.olay_yerinde or self.diyalog_aktif or self.diyalog_bitti:
                self.player.input_enabled = False
            else:
                self.player.input_enabled = True

        # BaseLevel'dan miras alınan tuş yönetim metodunu (seçenekler 1-2) çalıştırır.
        self.input_yonetimi(keys)

        # --- ÇİZİMLER VE KATMAN YÖNETİMİ ---
        self.pencere.blit(self.arkaplan, (0, 0))
        
        # Yerdeki şişeyi, derinlik algısı için NPC ve oyuncunun arkasında kalacak şekilde çiz.
        self.pencere.blit(self.sise_img, self.sise_rect)
        
        self.static_npcs.update()
        self.static_npcs.draw(self.pencere)
        self.player_group.update()
        self.player_group.draw(self.pencere)

        # --- ETKİLEŞİM TETİKLEME ---
        # Oyuncu uygun mesafeye ulaştığında 'E' tuşu ipucu NPC'nin üstünde belirir.
        if self.olay_yerinde and not self.diyalog_aktif and not self.diyalog_bitti:
            self.pencere.blit(self.press_e_img, (self.cop_atan.rect.centerx - 20, self.cop_atan.rect.top - 50))
            if keys[pygame.K_e]:
                self.diyalog_aktif = True # Diyalog motorunu başlatır.

        # --- KULLANICI ARAYÜZÜ (UI) KATMANLARI ---
        if self.intro_mesaji_aktif:
            self.bilgi_kutusu_ciz("Birisinin yere çöp attığını gördün. Onu uyarmalısın!")
        elif self.diyalog_aktif:
            # JSON'dan çekilen diyalog metinleri "Yabancı" ismiyle ekrana yansıtılır.
            self.diyalog_kutusu_ciz(npc_ismi="Yabancı")
        
        # Diyalog bittiğinde etik analiz ekranını göster ve ESC ile Bölüm 10'a geç.
        if self.diyalog_bitti:
            self.feedback_ekrani_ciz()
            if keys[pygame.K_ESCAPE]: return 10 

        return 9

    def bilgi_kutusu_ciz(self, mesaj):
        """Dinamik satır kaydırmalı bilgilendirme kutusu tasarımı."""
        kutu_g, kutu_y = 600, 160
        kutu_rect = pygame.Rect(GENISLIK//2 - kutu_g//2, YUKSEKLIK//2 - 200, kutu_g, kutu_y)
        
        # Saydam arka plan katmanı.
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
