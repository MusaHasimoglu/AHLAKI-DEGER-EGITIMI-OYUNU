import pygame
import sys
from settings import *

class Menu:
    """
    Oyunun başlangıç arayüzünü yöneten sınıf. 
    Kullanıcı etkileşimlerini (fare tıklaması) ve buton animasyonlarını kontrol eder.
    """
    def __init__(self, pencere):
        self.pencere = pencere
        
        # --- ANİMASYON VE DURUM KONTROLLERİ ---
        self.frame_index = 0
        self.animasyon_aktif = False # Animasyon sadece tıklandığında tetiklenir
        self.tiklanan_buton = None   # Hangi butonun animasyonunun oynayacağını tutan değişken
        self.last_update = pygame.time.get_ticks() # Animasyon hızı için zaman takibi
        
        # --- GÖRSEL YÜKLEME VE HATA YÖNETİMİ ---
        # Hocanın Kriteri: Yazılımın çökmesini önlemek için 'try-except' blokları kullanımı.
        try:
            # Arka planı yükle ve ekran boyutuna ölçekle
            self.arkaplan = pygame.image.load("assets/Images/UI/menu.png").convert()
            self.arkaplan = pygame.transform.scale(self.arkaplan, (GENISLIK, YUKSEKLIK))
            
            # Kareleri (frames) listelere yükleyerek animasyon hazırlığı yapılır (Veri Yapısı: List)
            # convert_alpha() kullanımı görsellerdeki şeffaflık (transparency) kanallarını korur.
            self.basla_frames = [pygame.transform.scale(pygame.image.load(f"assets/Images/UI/basla_{i}.png").convert_alpha(), (220, 80)) for i in range(1, 4)]
            self.cikis_frames = [pygame.transform.scale(pygame.image.load(f"assets/Images/UI/cikis_{i}.png").convert_alpha(), (220, 80)) for i in range(1, 4)]
            
        except Exception as e:
            # Dosya bulunamazsa varsayılan bir renk atayarak sistemin çalışmaya devam etmesi sağlanır (Hata Toleransı).
            print(f"Görsel yükleme hatası: {e}")
            self.arkaplan = pygame.Surface((GENISLIK, YUKSEKLIK))
            self.arkaplan.fill((10, 10, 30))

        # --- BUTON ALANLARI (Collision Detection) ---
        # get_rect() ile görsellerin etrafında görünmez birer kutu oluşturulur; 
        # bu kutular fare tıklamalarını algılamak (collision) için kullanılır.
        self.basla_rect = self.basla_frames[0].get_rect(center=(GENISLIK//2, 400))
        self.cikis_rect = self.cikis_frames[0].get_rect(center=(GENISLIK//2, 520))

    def animasyon_yurut(self):
        """
        ALGORİTMA: Durumsal Animasyon Yönetimi.
        Butona tıklandığında kareleri belirli bir hızda döndürür ve işlem bitince ana programa haber verir.
        """
        if self.animasyon_aktif:
            # get_ticks() ile geçen süreyi hesaplayarak FPS'ten bağımsız sabit bir animasyon hızı elde edilir.
            if pygame.time.get_ticks() - self.last_update > 120: 
                self.frame_index += 1
                self.last_update = pygame.time.get_ticks()
                
                # Eğer animasyonun tüm kareleri oynadıysa (1, 2, 3), hedeflenen eylemi gerçekleştir.
                if self.frame_index >= len(self.basla_frames):
                    if self.tiklanan_buton == "BAŞLA":
                        return "OYUN" # main.py'deki 'durum' değişkenini günceller
                    elif self.tiklanan_buton == "ÇIKIŞ":
                        pygame.quit()
                        sys.exit()
        return "MENU"

    def draw(self):
        """Menü elemanlarını ekrana çizen metod."""
        self.pencere.blit(self.arkaplan, (0, 0))

        # --- DİNAMİK BUTON ÇİZİMİ ---
        # Eğer bir butona tıklandıysa frame_index'e göre animasyon karesini çiz, 
        # tıklanmadıysa varsayılan (0. indeks) kareyi çiz.
        idx_basla = self.frame_index if self.tiklanan_buton == "BAŞLA" else 0
        self.pencere.blit(self.basla_frames[idx_basla], self.basla_rect)
        
        idx_cikis = self.frame_index if self.tiklanan_buton == "ÇIKIŞ" else 0
        self.pencere.blit(self.cikis_frames[idx_cikis], self.cikis_rect)

    def run(self):
        """Menü olay döngüsünü ve etkileşimleri yönetir."""
        self.draw()
        sonuc = self.animasyon_yurut()
        
        # Eğer animasyon bittiyse (sonuç OYUN veya EXIT ise) bu değeri döndürür.
        if sonuc != "MENU":
            return sonuc

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            # Fare Tıklama Kontrolü: Animasyon sırasında mükerrer tıklamaları engellemek için kontrol eklenmiştir.
            if event.type == pygame.MOUSEBUTTONDOWN and not self.animasyon_aktif:
                if event.button == 1: # Sol tık kontrolü
                    # collidepoint() algoritması farenin koordinatlarının buton alanı içinde olup olmadığını denetler.
                    if self.basla_rect.collidepoint(event.pos):
                        self.animasyon_aktif = True
                        self.tiklanan_buton = "BAŞLA"
                        self.frame_index = 0
                    elif self.cikis_rect.collidepoint(event.pos):
                        self.animasyon_aktif = True
                        self.tiklanan_buton = "ÇIKIŞ"
                        self.frame_index = 0
        
        return "MENU"
