import pygame
import os
from settings import *

class NPC(pygame.sprite.Sprite):
    """
    OOP KRİTERİ: Kalıtım (Inheritance).
    Tüm NPC'ler Pygame'in Sprite sınıfından miras alarak sprite grupları ile 
    yönetilebilir ve otomatik çizim/çarpışma özelliklerini kullanır[cite: 76, 77].
    """
    def __init__(self, x, y, animasyonlar, varsayilan_durum='idle', boyut=(120, 120), ters_cevir= False):
        super().__init__()
        
        # --- ÖZELLİKLER (Attributes) ---
        self.ters_cevir = ters_cevir # Karakterin aynalanmış (ters) durup durmayacağı
        self.boyut = boyut           # NPC'nin ekrandaki piksel boyutu
        self.status = varsayilan_durum
        self.frame_index = 0
        self.facing_right = True

        # --- VERİ YAPILARI: Animasyon Yükleme ---
        # Hocanın Kriteri: Dinamik animasyon yönetimi için sözlük (dictionary) kullanımı[cite: 87].
        # 'durum' anahtar (key), 'klasor_yolu' ise değer (value) olarak işlenir.
        self.animations = {}
        for durum, klasor_yolu in animasyonlar.items():
            self.animations[durum] = self.yukle_klasor(klasor_yolu)

        # GÜVENLİK VE HATA TOLERANSI: 
        # Eğer belirtilen klasörde resim bulunamazsa oyunun çökmemesi için pembe bir kutu oluşturulur.
        if self.animations.get(self.status):
            self.image = self.animations[self.status][self.frame_index]
        else:
            self.image = pygame.Surface(self.boyut)
            self.image.fill((255, 0, 255)) # Hata belirteci olarak parlak pembe renk
        
        # NPC'nin ayak tabanını (midbottom) belirtilen koordinatlara yerleştirme
        self.rect = self.image.get_rect(midbottom=(x, y))

    def yukle_klasor(self, path):
        """
        ALGORİTMA: Klasördeki resimleri sıralı yükleme.
        Belirtilen yoldaki .png dosyalarını alfabetik sırayla okuyup ölçeklendirir.
        """
        surface_list = []
        # Klasör varlık kontrolü (Hata yönetimi)
        if not os.path.exists(path): return surface_list
        
        # Dosyaları listele ve alfabetik sırala (Animasyon akışı için kritiktir)
        files = sorted([f for f in os.listdir(path) if f.endswith('.png')])
        for img_name in files:
            # Görseli yükle ve şeffaflık kanalını (alpha) optimize et
            img = pygame.image.load(os.path.join(path, img_name)).convert_alpha()
            # NPC boyutuna göre ölçeklendirme işlemi
            img = pygame.transform.scale(img, self.boyut)
            surface_list.append(img)
            
        return surface_list

    def update(self):
        """
        NPC animasyonunu ve görsel durumunu her karede güncelleyen algoritma.
        """
        # Seçili durumda animasyon karesi mevcut mu kontrol et
        if self.animations.get(self.status):
            # Kare indeksini yavaşça artır (0.1 hızıyla akıcı geçiş)
            self.frame_index += 0.1
            
            # Animasyon döngüsü (Başa dönme kontrolü)
            if self.frame_index >= len(self.animations[self.status]):
                self.frame_index = 0
            
            # Mevcut kareyi seç
            self.image = self.animations[self.status][int(self.frame_index)]
            
            # Yön Kontrolü: Eğer sağa bakmıyorsa görseli yatayda çevir (flip)
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

            # Başlangıçta ters çevrilmiş olması gerekiyorsa (NPC tasarımı gereği) tekrar çevir
            if self.ters_cevir:
                self.image = pygame.transform.flip(self.image, True, False)
