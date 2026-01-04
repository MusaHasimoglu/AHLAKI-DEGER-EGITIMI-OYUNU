import pygame
import os
from settings import *

class Player(pygame.sprite.Sprite):
    """
    OOP KRİTERİ: Kalıtım 
    Player sınıfı, Pygame'in Sprite sınıfından miras alarak hazır grafik ve çarpışma 
    yönetimi özelliklerini bünyesine katar.
    """
    def __init__(self, pos):
        super().__init__()
        
        # --- VERİ YAPILARI ---
        # Animasyon durumlarını ve bunlara karşılık gelen resim listelerini
        # organize etmek için bir sözlük (dictionary) veri yapısı kullanılır.
        self.character_path = 'assets/Images/Characters/player/' 
        self.animations = {'idle': [], 'run': [], 'walk': []}
        
        # Karakter varlıklarını (assets) otomatik yükleyen metodun çağrılması
        self.import_assets()
        
        # Animasyon Kontrol Değişkenleri
        self.status = 'idle'      # Karakterin mevcut durumu
        self.frame_index = 0      # Animasyonun hangi karesinde olduğumuz
        self.animation_speed = 0.15 # Kareler arası geçiş hızı
        
        # İlk kareyi belirleme ve ekran koordinatlarını ayarlama
        # Görsel bulunamazsa yedek bir yüzey (Surface) oluşturulur.
        self.image = self.animations['idle'][0] if self.animations['idle'] else pygame.Surface((32, 64))
        self.rect = self.image.get_rect(midbottom=pos)

        # --- HAREKET VE DURUM YÖNETİMİ ---
        # Vektör tabanlı hareket; yön ve hızı ayrı bileşenlerde tutmamızı sağlar.
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 5
        self.facing_right = True # Karakterin baktığı yön (Sağ/Sol)
        
        # Kontrol Kilidi: Diyaloglar esnasında karakterin hareketini durdurmak için kullanılır.
        self.input_enabled = True 

    def import_assets(self):
        """Animasyon klasörlerini modüler ve dinamik bir şekilde yükler."""
        for animation in self.animations.keys():
            full_path = os.path.join(self.character_path, animation)
            self.animations[animation] = self.yukle_klasor(full_path)

    def yukle_klasor(self, path):
        """
        ALGORİTMA: Dizin tarama ve resim ölçeklendirme algoritması.
        Belirtilen yoldaki görselleri alfabetik sırayla listeye aktarır.
        """
        surface_list = []
        if not os.path.exists(path): return surface_list

        # Dosyaları alfabetik sıralamak (sorted), animasyonun doğru sırayla akmasını sağlar.
        files = sorted([f for f in os.listdir(path) if f.endswith('.png')])
        
        for img_name in files:
            img_path = os.path.join(path, img_name)
            # Resim yükleme ve performans için piksel formatı dönüştürme (convert_alpha)
            img_surf = pygame.image.load(img_path).convert_alpha()
            
            # settings.py'den gelen katsayı ile karakter boyutunu dinamik ölçeklendirme
            yeni_size = (int(img_surf.get_width() * KARAKTER_BOYUT_CARPANI), 
                         int(img_surf.get_height() * KARAKTER_BOYUT_CARPANI))
            img_surf = pygame.transform.scale(img_surf, yeni_size)
            surface_list.append(img_surf)
            
        return surface_list

    def get_input(self):
        """Klavye girişlerini (Input Handling) yöneten ve durumu güncelleyen metod."""
        keys = pygame.key.get_pressed()
        
        # Sağa hareket kontrolü
        if keys[pygame.K_d]:
            self.direction.x = 1
            self.facing_right = True
            self.status = 'run'
        # Sola hareket kontrolü
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.facing_right = False
            self.status = 'run'
        # Durma hali
        else:
            self.direction.x = 0
            self.status = 'idle'

    def animate(self):
        """
        ALGORİTMA: Kare indeksi hesaplama ve görsel yansıtma.
        Frame index değerini artırarak döngüsel bir animasyon akışı sağlar.
        """
        animation = self.animations.get(self.status, [])
        if not animation: return

        # Frame index hıza göre artırılır, listenin sonuna gelince başa döner.
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation): self.frame_index = 0
        
        # İlgili kare seçilir; karakter sola bakıyorsa görsel yatayda ters çevrilir (flip).
        image = animation[int(self.frame_index)]
        self.image = image if self.facing_right else pygame.transform.flip(image, True, False)

    def update(self):
        """Her oyun karesinde (frame) karakterin tüm fiziksel ve görsel özelliklerini yeniler."""
        # Eğer diyalog aktif değilse kullanıcı girişlerini işle
        if self.input_enabled:
            self.get_input()
        else:
            # Diyalog esnasında karakterin durması ve idle animasyonuna geçmesi sağlanır.
            self.direction.x = 0
            self.status = 'idle'

        # Animasyonu işlet ve pozisyonu güncelle
        self.animate()
        self.rect.x += self.direction.x * self.speed
        
        # EKRAN SINIRLARI KONTROLÜ (Kapsülleme örneği)
        # Karakterin oyun alanı dışına taşması yazılımsal olarak engellenir.
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > GENISLIK: self.rect.right = GENISLIK
