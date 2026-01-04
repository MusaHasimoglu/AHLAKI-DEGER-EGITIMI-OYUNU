import pygame
from settings import *
from npc import NPC
from level_manager import BaseLevel

class Level1(BaseLevel):
    """
    OOP KRİTERİ: Kalıtım (Inheritance). 
    BaseLevel sınıfından miras alarak diyalog sistemi, metin sarma ve analiz ekranı 
    gibi karmaşık özellikleri hazır olarak kullanır.
    """
    def __init__(self, pencere, player, player_group):
        # 'bolum1' anahtarı gönderilerek JSON dosyasındaki ilgili senaryo yüklenir.
        super().__init__(pencere, player, player_group, "bolum1")
        
        # --- DURUM YÖNETİMİ (State Machine) ---
        # Oyunun akışını kontrol eden bayraklar (flags) ve evreler tanımlanır.
        self.baslangic_uyarisi_aktif = True  # İlk açılış mesajı
        self.npc_uyarisi_aktif = False       # Kaynakçı gelince çıkan mesaj
        self.evre = "yolcular_bekliyor"      # Mevcut sahne durumu
        
        # --- GÖRSEL VARLIKLAR VE HATA YÖNETİMİ ---
        try:
            # Arka plan görseli yüklenir ve ekran çözünürlüğüne adapte edilir.
            self.arkaplan = pygame.image.load("assets/Images/Backgrounds/1-otobus_duragi.png").convert()
            self.arkaplan = pygame.transform.scale(self.arkaplan, (GENISLIK, YUKSEKLIK))
            
            # Etkileşim ipucu (E tuşu görseli) yüklenir.
            self.press_e_img = pygame.image.load("assets/Images/UI/press_e.png").convert_alpha()
            self.press_e_img = pygame.transform.scale(self.press_e_img, (40, 40))
        except:
            # Dosya eksikse oyunun devam etmesi için varsayılan yüzeyler oluşturulur.
            self.arkaplan = pygame.Surface((GENISLIK, YUKSEKLIK)); self.arkaplan.fill((100, 100, 250))
            self.press_e_img = pygame.Surface((30, 30)); self.press_e_img.fill(ALTIN)

        # Sprite Grupları: NPC'lerin toplu yönetimi için kullanılır.
        self.static_npcs = pygame.sprite.Group() 
        self.kaynakci_group = pygame.sprite.GroupSingle() 
        self.setup_sprites()

    def setup_sprites(self):
        """NPC'leri sahnede belirli koordinatlara modüler olarak yerleştirir."""
        base_path = "assets/Images/Characters/NPC/bolum1_npc/"
        
        # Sabit duran yolcu NPC'leri oluşturulur.
        n1 = NPC(710, 595, {'idle': base_path + "npc1_idle/"}, boyut=(200, 200))
        n2 = NPC(630, 595, {'idle': base_path + "npc2_idle/"}, boyut=(200, 200))
        n3 = NPC(550, 595, {'idle': base_path + "npc3_idle/"}, boyut=(200, 200))
        self.static_npcs.add(n1, n2, n3)

        # 'Kaynakçı' (sırayı bozan kişi) başlangıçta ekranın dışında (-100) bekler.
        self.kaynakci = NPC(-100, 595, {
            'idle': base_path + "npc4_idle/",
            'run': base_path + "npc4_run/"
        }, varsayilan_durum='run', boyut=(200, 200))
        self.kaynakci_group.add(self.kaynakci)

    def run(self):
        """Bölümün ana çalışma döngüsü; mantıksal kontrolleri ve çizimleri yönetir."""
        keys = pygame.key.get_pressed()
        
        # --- HAREKET VE KONTROL KİLİDİ ALGORİTMASI ---
        # Uyarı ekranları veya diyaloglar aktifken oyuncunun hareketi kısıtlanır.
        if self.baslangic_uyarisi_aktif:
            self.player.input_enabled = False 
            if keys[pygame.K_SPACE]:
                self.baslangic_uyarisi_aktif = False
                self.player.input_enabled = True 
                pygame.time.delay(200)
        
        elif self.npc_uyarisi_aktif:
            self.player.input_enabled = False 
            if keys[pygame.K_SPACE]:
                self.npc_uyarisi_aktif = False
                self.player.input_enabled = True 
                pygame.time.delay(200)
        
        else:
            # Görünmez Sınır (X=470): Oyuncunun sıranın en önüne geçmesi engellenir.
            if self.evre != "etkilesim" and self.player.rect.centerx >= 470:
                self.player.rect.centerx = 470
                self.player.input_enabled = False
                self.player.status = 'idle'
            else:
                # Diyalog kutusu açıksa karakter durdurulur.
                self.player.input_enabled = not self.diyalog_aktif

            self.input_yonetimi(keys) # BaseLevel'dan gelen tuş yönetimini çalıştırır.
            self.update_logic()      # NPC hareketlerini günceller.

        # --- GÖRSEL KATMANLARIN ÇİZİMİ (Layering) ---
        self.pencere.blit(self.arkaplan, (0, 0))
        self.static_npcs.update()
        self.static_npcs.draw(self.pencere)
        self.kaynakci_group.update()
        self.kaynakci_group.draw(self.pencere)
        self.player_group.update()
        self.player_group.draw(self.pencere)

        # --- ETKİLEŞİM TETİKLEME (Interaction Logic) ---
        # Oyuncu kaynakçıya yaklaştığında 'E' tuşu ipucunu gösterir.
        if self.evre == "etkilesim" and not self.diyalog_aktif and not self.diyalog_bitti:
            mesafe = abs(self.player.rect.centerx - self.kaynakci.rect.centerx)
            if mesafe < 150: 
                self.pencere.blit(self.press_e_img, (self.kaynakci.rect.centerx - 20, self.kaynakci.rect.top - 50))
                if keys[pygame.K_e]:
                    self.diyalog_aktif = True # Diyalog penceresini açar.

        # --- KULLANICI ARAYÜZÜ (HUD) YÖNETİMİ ---
        if self.baslangic_uyarisi_aktif:
            self.uyari_kutusu_ciz("Hey! Otobüs geliyor sıraya geç!")
        elif self.npc_uyarisi_aktif:
            self.uyari_kutusu_ciz("Birisi sıranın önüne geçti, onunla konuş!")
        elif self.diyalog_aktif:
            self.diyalog_kutusu_ciz(npc_ismi="Kaynakçı") 
        
        # Bölüm bittiyse analiz ekranını göster ve ESC ile sonraki bölüme geç.
        if self.diyalog_bitti:
            self.feedback_ekrani_ciz() 
            if keys[pygame.K_ESCAPE]: return 2 # Game sınıfına Level 2'ye geçme sinyali gönderir.

        return 1

    def uyari_kutusu_ciz(self, mesaj):
        """Bilgilendirme mesajlarını şık bir kutu içerisinde ekrana yansıtır."""
        kutu_gen, kutu_yuk = 650, 140
        x, y = (GENISLIK - kutu_gen) // 2, 100
        kutu_rect = pygame.Rect(x, y, kutu_gen, kutu_yuk)
        
        # Kutu ve çerçeve çizimi
        pygame.draw.rect(self.pencere, (40, 40, 60), kutu_rect)
        pygame.draw.rect(self.pencere, ALTIN, kutu_rect, 3)
        
        # Metinlerin hizalanarak çizilmesi
        txt = self.font_ana.render(mesaj, True, BEYAZ)
        sub_txt = self.font_secenek.render("[ DEVAM ETMEK İÇİN SPACE TUŞUNA BASIN ]", True, ALTIN)
        self.pencere.blit(txt, (x + (kutu_gen - txt.get_width()) // 2, y + 35))
        self.pencere.blit(sub_txt, (x + (kutu_gen - sub_txt.get_width()) // 2, y + 85))

    def update_logic(self):
        """
        ALGORİTMA: Olay Tetikleme Sistemi.
        Oyuncu belirli bir noktayı geçtiğinde 'sıraya kaynak yapma' olayını başlatır.
        """
        # Oyuncu X=350 koordinatını geçtiğinde kaynakçı koşmaya başlar.
        if self.player.rect.centerx > 350 and self.evre == "yolcular_bekliyor":
            self.evre = "kaynakci_kosuyor"

        if self.evre == "kaynakci_kosuyor":
            if self.kaynakci.rect.centerx < 790: 
                self.kaynakci.rect.x += 7 # NPC hızı
            else:
                # Kaynakçı sıranın başına ulaştığında durur ve etkileşim evresi başlar.
                self.kaynakci.status = 'idle'
                if not self.diyalog_bitti and self.evre != "etkilesim":
                    self.npc_uyarisi_aktif = True
                    self.evre = "etkilesim"
