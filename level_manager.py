import pygame
import json
import os
from settings import *

class BaseLevel:
    """
    ATA SINIF (PARENT CLASS): 
    Bu sınıf, 10 farklı bölümün ortak fonksiyonlarını barındırır. 
    Kod tekrarını önleyerek projenin modülerliğini ve sürdürülebilirliğini sağlar.
    """
    def __init__(self, pencere, player, player_group, bolum_anahtari):
        self.pencere = pencere
        self.player = player
        self.player_group = player_group
        
        # --- VERİ YÖNETİMİ ---
        # Her bölüm kendi JSON anahtarını göndererek ilgili senaryoyu yükler.
        self.diyalog_verisi = self.load_dialogues(bolum_anahtari)
        
        # Diyalog kontrol değişkenleri
        self.diyalog_aktif = False
        self.diyalog_bitti = False
        self.current_node = "START" # Diyalog ağacının başlangıç noktası
        self.secilen_feedbackler = [] # Oyuncunun seçimlerinin toplandığı liste
        
        # --- FONT VE TİPOGRAFİ AYARLARI ---
        self.font_yolu = "assets/Fonts/VT323-Regular.ttf"
        
        if os.path.exists(self.font_yolu):
            # Retro atmosfer için özel piksel font boyutları tanımlanır.
            self.font_ana = pygame.font.Font(self.font_yolu, 24)
            self.font_secenek = pygame.font.Font(self.font_yolu, 22)
            self.font_baslik = pygame.font.Font(self.font_yolu, 38)
            self.font_diyalog_npc = pygame.font.Font(self.font_yolu, 28)     
            self.font_diyalog_secenek = pygame.font.Font(self.font_yolu, 24)
        else:
            # Font dosyası bulunamazsa sistemin çökmemesi için varsayılan fontlar atanır.
            self.font_ana = pygame.font.Font(None, 24)
            self.font_baslik = pygame.font.Font(None, 38)
            self.font_diyalog_npc = pygame.font.Font(None, 28)
            self.font_diyalog_secenek = pygame.font.Font(None, 24)

    def load_dialogues(self, anahtar):
        """
        ALGORİTMA: JSON Tabanlı Dinamik Senaryo Yükleme.
        Encoding='utf-8-sig' parametresi ile Türkçe karakter uyumluluğu sağlanmıştır.
        """
        try:
            if os.path.exists("dialogs.json"):
                with open("dialogs.json", "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                    # Sadece ilgili bölüme ait senaryo bloğunu geri döndürür.
                    return data.get(anahtar, {})
            return {}
        except Exception as e:
            print(f"JSON Yükleme Hatası: {e}")
            return {}

    def metni_sar(self, metin, font, max_genislik):
        """
        ALGORİTMA: Dinamik Metin Kaydırma (Text Wrapping).
        Diyalogların kutu dışına taşmasını engelleyen, genişlik kontrolü yapan algoritma.
        """
        kelimeler = metin.split(' ')
        satirlar = []
        su_anki_satir = ""

        for kelime in kelimeler:
            # Yeni kelime eklendiğinde oluşacak genişliği piksel cinsinden test eder.
            test_satiri = su_anki_satir + kelime + " "
            if font.size(test_satiri)[0] < max_genislik:
                su_anki_satir = test_satiri
            else:
                # Sınır aşıldıysa mevcut satırı listeye ekler ve yeni satıra geçer.
                satirlar.append(su_anki_satir.strip())
                su_anki_satir = kelime + " "
        
        # Son kalan kelimeleri ekler.
        satirlar.append(su_anki_satir.strip())
        return satirlar

    def input_yonetimi(self, keys):
        """Diyalog esnasında kullanıcıdan gelen sayısal seçimleri işleyen kontrol mekanizması."""
        if not self.diyalog_aktif: return
        
        node = self.diyalog_verisi.get(self.current_node, {})
        options = node.get("options", [])
        
        # Klavye girişlerine göre diyalog dallanması (Branching logic) yönetilir.
        if options:
            if keys[pygame.K_1]: self.secim_yap(options[0])
            elif keys[pygame.K_2] and len(options) > 1: self.secim_yap(options[1])
        elif keys[pygame.K_SPACE]:
            # Eğer seçenek yoksa SPACE ile diyalog sonlandırılır.
            self.diyalog_aktif = False
            self.diyalog_bitti = True
            pygame.time.delay(200)

    def secim_yap(self, secenek):
        """
        Oyuncunun yaptığı seçimi kaydeder ve diyalog ağacında bir sonraki düğüme geçer.
        Bu süreç ahlaki geri bildirimlerin (feedback) toplanmasını sağlar.
        """
        self.secilen_feedbackler.append({
            "secim": secenek.get("text", "Seçim"),
            "analiz": secenek.get("feedback", "Analiz yok.")
        })
        # JSON'daki 'next' anahtarına göre bir sonraki konuşmaya geçer.
        self.current_node = secenek.get("next", "START")
        pygame.time.delay(250) # Hatalı çift tıklamayı önlemek için kısa bir bekleme.

    def diyalog_kutusu_ciz(self, npc_ismi=None):
        """Kompakt ve estetik bir diyalog kutusu çizen grafik arayüz (UI) fonksiyonu."""
        if not self.diyalog_aktif: return
        node = self.diyalog_verisi.get(self.current_node, {})
        if not node: return

        # --- ARAYÜZ TASARIMI (Saydamlık ve Çerçeve) ---
        kutu_rect = pygame.Rect(60, 20, GENISLIK - 120, 180) 
        
        # Saydam arka plan katmanı (Alpha blending)
        s_surface = pygame.Surface((kutu_rect.width, kutu_rect.height))
        s_surface.set_alpha(180) # %70 saydamlık oranı
        s_surface.fill((20, 20, 35)) # Koyu gece mavisi tonu
        self.pencere.blit(s_surface, (kutu_rect.x, kutu_rect.y))
        
        # Beyaz kenar çerçevesi çizimi
        pygame.draw.rect(self.pencere, (230, 230, 230), kutu_rect, 2)
        
        # --- METİN YERLEŞTİRME ---
        npc_metni = node.get('npc_text', '...')
        tam_metin = f"{npc_ismi}: {npc_metni}" if npc_ismi else npc_metni
        
        # Metni otomatik olarak satırlara böler (Wrap).
        max_metin_genisligi = kutu_rect.width - 60
        npc_satirlar = self.metni_sar(tam_metin, self.font_diyalog_npc, max_metin_genisligi)
        
        y_offset = kutu_rect.y + 20
        for satir in npc_satirlar:
            n_surf = self.font_diyalog_npc.render(satir, True, ALTIN)
            self.pencere.blit(n_surf, (kutu_rect.x + 30, y_offset))
            y_offset += 30 

        # --- SEÇENEKLERİN LİSTELENMESİ ---
        options = node.get("options", [])
        if options:
            y_offset += 10
            for i, opt in enumerate(options):
                opt_metni = f"[{i+1}] - {opt.get('text', '')}"
                o_surf = self.font_diyalog_secenek.render(opt_metni, True, BEYAZ)
                self.pencere.blit(o_surf, (kutu_rect.x + 40, y_offset))
                y_offset += 28
        else:
            # Diyalog sonu uyarısını kutunun altına sabitleme
            bitis_mesaji = self.font_diyalog_secenek.render("[ DEVAM ETMEK İÇİN SPACE TUŞUNA BASIN ]", True, ALTIN)
            mesaj_rect = bitis_mesaji.get_rect(centerx=GENISLIK // 2, bottom=kutu_rect.bottom - 15)
            self.pencere.blit(bitis_mesaji, mesaj_rect)

    def feedback_ekrani_ciz(self, alt_not_metni="[ SONRAKİ BÖLÜME GEÇMEK İÇİN ESC TUŞUNA BASIN ]"):
        """
        Bölüm sonunda oyuncunun seçimlerini analiz eden üstbilişsel geri bildirim ekranı.
        """
        # Ekranı tamamen kaplayan koyu bir katman oluşturur.
        overlay = pygame.Surface((GENISLIK, YUKSEKLIK))
        overlay.set_alpha(240)
        overlay.fill(SIYAH)
        self.pencere.blit(overlay, (0, 0))
        
        baslik = self.font_baslik.render("BÖLÜM ANALİZİ", True, ALTIN)
        self.pencere.blit(baslik, (GENISLIK // 2 - baslik.get_width() // 2, 50))
        
        y_pos = 130
        max_feedback_genisligi = GENISLIK - 200 

        # Oyuncunun yaptığı her bir ahlaki seçimin analizi listelenir.
        for item in self.secilen_feedbackler:
            secim_metni = f"> Seçim: {item['secim']}"
            s_surf = self.font_ana.render(secim_metni, True, (100, 200, 255))
            self.pencere.blit(s_surf, (100, y_pos))
            y_pos += 35
            
            # Etik analiz metni uzun olabileceği için yine sarma algoritması kullanılır.
            analiz_metni = f"Etik Analiz: {item['analiz']}"
            analiz_satirlar = self.metni_sar(analiz_metni, self.font_secenek, max_feedback_genisligi)
            for satir in analiz_satirlar:
                a_surf = self.font_secenek.render(satir, True, BEYAZ)
                self.pencere.blit(a_surf, (130, y_pos))
                y_pos += 28
            y_pos += 30 
            
        alt_not = self.font_secenek.render(alt_not_metni, True, ALTIN)
        self.pencere.blit(alt_not, (GENISLIK // 2 - alt_not.get_width() // 2, YUKSEKLIK - 70))
