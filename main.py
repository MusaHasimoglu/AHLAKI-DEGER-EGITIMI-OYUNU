import pygame
import sys
import os
from settings import *
from player import Player
# Her bir bölüm modüler bir yapıda ayrı dosyalardan içe aktarılır
from bolum1 import Level1
from bolum2 import Level2
from bolum3 import Level3
from bolum4 import Level4
from bolum5 import Level5
from bolum6 import Level6
from bolum7 import Level7
from bolum8 import Level8
from bolum9 import Level9
from bolum10 import Level10
from menu import Menu 

class Game:
    def __init__(self):
        """Oyunun temel bileşenlerini ve sistemlerini başlatan yapıcı metod."""
        pygame.init()
        
        # --- SES SİSTEMİ BAŞLATMA ---
        # Oyunun işitsel geri bildirimleri için mikser modülü başlatılır
        pygame.mixer.init()
        
        # Ekran ayarları settings.py dosyasındaki sabitlerden çekilir
        self.pencere = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
        pygame.display.set_caption("Ahlaki Karar Oyunu")
        
        # Oyunun her bilgisayarda aynı hızda çalışması için saat objesi oluşturulur
        self.clock = pygame.time.Clock()

        # Menü sistemi başlatılır ve varsayılan durum "MENU" olarak atanır
        self.menu = Menu(self.pencere)
        self.durum = "MENU" 

        # Oyuncu (Player) nesnesi tekil bir grup içinde yönetilir (Sprite yönetimi)
        self.player = Player((100, 595)) 
        self.player_group = pygame.sprite.GroupSingle(self.player)

        # Bölüm kontrol değişkenleri; oyun ilk bölümden başlatılır
        self.current_level_id = 1 
        self.level = None

        # --- MÜZİĞİ BAŞLAT ---
        self.arka_plan_muzigi_cal()

    def arka_plan_muzigi_cal(self):
        """Atmosferi desteklemek için arka plan müziğini sonsuz döngüde başlatır."""
        muzik_yolu = "assets/Sounds/Menu Theme.wav"
        
        # Dosya yolu kontrolü yapılarak olası çökmelerin önüne geçilir
        if os.path.exists(muzik_yolu):
            try:
                pygame.mixer.music.load(muzik_yolu)
                # Ses seviyesi, diyalogların okunmasını engellememek için düşük tutulur
                pygame.mixer.music.set_volume(0.15)
                # loops=-1 parametresi müziğin kesintisiz çalmasını sağlar
                pygame.mixer.music.play(loops=-1)
            except Exception as e:
                print(f"Müzik çalma hatası: {e}")
        else:
            print(f"Uyarı: {muzik_yolu} dosyası bulunamadı.")

    def setup_level(self):
        """Seçili bölüm ID'sine göre ilgili sınıfı örnekler ve oyuncu konumunu ayarlar."""
        # Her bölüm için oyuncunun başlangıç koordinatları o sahnenin tasarımına göre güncellenir
        if self.current_level_id == 1:
            self.level = Level1(self.pencere, self.player, self.player_group)
        elif self.current_level_id == 2:
            self.player.rect.centerx = 150 
            self.level = Level2(self.pencere, self.player, self.player_group)
        elif self.current_level_id == 3:
            self.player.rect.x = 100
            self.player.rect.y = 620
            self.level = Level3(self.pencere, self.player, self.player_group)
        elif self.current_level_id == 4:
            self.player.rect.x = 50 
            self.player.rect.y = 640 
            self.level = Level4(self.pencere, self.player, self.player_group)
        elif self.current_level_id == 5: 
            self.player.rect.x = 50    
            self.player.rect.y = 550  
            self.level = Level5(self.pencere, self.player, self.player_group)
        elif self.current_level_id == 6: 
            self.player.rect.x = 50    
            self.player.rect.y = 450  
            self.level = Level6(self.pencere, self.player, self.player_group)
        elif self.current_level_id == 7: 
            self.player.rect.x = 50    
            self.player.rect.y = 450  
            self.level = Level7(self.pencere, self.player, self.player_group)
        elif self.current_level_id == 8: 
            self.player.rect.x = 50    
            self.player.rect.y = 450  
            self.level = Level8(self.pencere, self.player, self.player_group)
        elif self.current_level_id == 9: 
            self.player.rect.x = 50    
            self.player.rect.y = 450  
            self.level = Level9(self.pencere, self.player, self.player_group)
        elif self.current_level_id == 10: 
            self.player.rect.x = 50    
            self.player.rect.y = 450  
            self.level = Level10(self.pencere, self.player, self.player_group)

    def run(self):
        """Oyunun ana döngüsü; olayları yönetir, ekranı günceller ve durumu kontrol eder."""
        while True:
            # Durum Yönetimi: Menü mü yoksa Oyun mu aktif?
            if self.durum == "MENU":
                self.durum = self.menu.run()
                if self.durum == "OYUN":
                    self.setup_level() # Menüden çıkınca ilk bölüm yüklenir
            
            elif self.durum == "OYUN":
                # Pygame olaylarını (kapatma tuşu vb.) kontrol eder
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                # Her karede ekran temizlenir
                self.pencere.fill(SIYAH) 

                if self.level:
                    # Aktif bölümün mantığı çalıştırılır ve varsa yeni bölüm ID'si alınır
                    new_level_id = self.level.run()

                    # Bölüm geçiş kontrolü: Eğer fonksiyon farklı bir ID döndürürse yeni bölüm yüklenir
                    if new_level_id != self.current_level_id:
                        self.current_level_id = new_level_id
                        self.setup_level()

            # Grafiklerin ekrana yansıtılması
            pygame.display.update()
            
            # FPS (Saniyedeki Kare Sayısı) 60'a sabitlenerek işlemci kullanımı optimize edilir
            self.clock.tick(60)

# Programın doğrudan çalıştırılıp çalıştırılmadığını kontrol eder
if __name__ == "__main__":
    game = Game()
    game.run()
