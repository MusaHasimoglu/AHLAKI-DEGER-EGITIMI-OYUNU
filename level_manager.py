import pygame
import json
import os
from settings import *

class BaseLevel:
    """
    ATA SINIF (PARENT CLASS): 
    10 farklı bölümün iskeletini oluşturur. Hem NPC metinlerini hem de oyuncu 
    seçeneklerini kutu genişliğine göre otomatik olarak alt satıra böler.
    """
    def __init__(self, pencere, player, player_group, bolum_anahtari):
        self.pencere = pencere
        self.player = player
        self.player_group = player_group
        self.bolum_anahtari = bolum_anahtari
        
        # --- Diyalog ve Veri Yönetimi ---
        self.diyalog_verisi = self.load_dialogues(bolum_anahtari)
        self.diyalog_aktif = False
        self.diyalog_bitti = False
        self.current_node = "START"
        self.secilen_feedbackler = []
        
        # --- Görsel ve Font Ayarları ---
        self._fontlari_yukle()

    def _fontlari_yukle(self):
        """Font dosyalarını güvenli bir şekilde yükler, hata payı bırakmaz."""
        self.font_yolu = "assets/Fonts/VT323-Regular.ttf"
        try:
            if os.path.exists(self.font_yolu):
                self.font_ana = pygame.font.Font(self.font_yolu, 24)
                self.font_secenek = pygame.font.Font(self.font_yolu, 22)
                self.font_baslik = pygame.font.Font(self.font_yolu, 38)
                self.font_diyalog_npc = pygame.font.Font(self.font_yolu, 28)     
                self.font_diyalog_secenek = pygame.font.Font(self.font_yolu, 24)
            else:
                raise FileNotFoundError
        except:
            # Font bulunamazsa sistemin çökmemesi için varsayılanlar atanır
            self.font_ana = pygame.font.Font(None, 24)
            self.font_baslik = pygame.font.Font(None, 38)
            self.font_diyalog_npc = pygame.font.Font(None, 28)
            self.font_diyalog_secenek = pygame.font.Font(None, 24)

    def load_dialogues(self, anahtar):
        """JSON dosyasından ilgili bölümün senaryosunu yükler."""
        try:
            if os.path.exists("dialogs.json"):
                with open("dialogs.json", "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                    return data.get(anahtar, {})
            return {}
        except Exception as e:
            print(f"JSON Yükleme Hatası: {e}")
            return {}

    def metni_sar(self, metin, font, max_genislik):
        """
        Dinamik Metin Kaydırma Algoritması.
        Verilen metni, font boyutuna göre satırlara böler.
        """
        kelimeler = metin.split(' ')
        satirlar = []
        su_anki_satir = ""

        for kelime in kelimeler:
            test_satiri = su_anki_satir + kelime + " "
            if font.size(test_satiri)[0] < max_genislik:
                su_anki_satir = test_satiri
            else:
                satirlar.append(su_anki_satir.strip())
                su_anki_satir = kelime + " "
        
        satirlar.append(su_anki_satir.strip())
        return satirlar

    def input_yonetimi(self, keys):
        """Klavye girişlerini diyalog akışına göre yönetir."""
        if not self.diyalog_aktif: return
        
        node = self.diyalog_verisi.get(self.current_node, {})
        options = node.get("options", [])
        
        if options:
            if keys[pygame.K_1]: 
                self.secim_yap(options[0])
            elif keys[pygame.K_2] and len(options) > 1: 
                self.secim_yap(options[1])
        elif keys[pygame.K_SPACE]:
            self.diyalog_aktif = False
            self.diyalog_bitti = True
            pygame.time.delay(200)

    def secim_yap(self, secenek):
        """Seçimi kaydeder ve sonraki diyalog düğümüne geçer."""
        self.secilen_feedbackler.append({
            "secim": secenek.get("text", "Seçim"),
            "analiz": secenek.get("feedback", "Analiz yok.")
        })
        self.current_node = secenek.get("next", "START")
        pygame.time.delay(250)

    def diyalog_kutusu_ciz(self, npc_ismi=None):
        """Hem NPC konuşmasını hem de oyuncu seçeneklerini SARARAK çizer."""
        if not self.diyalog_aktif: return
        node = self.diyalog_verisi.get(self.current_node, {})
        if not node: return

        # --- ARAYÜZ TASARIMI ---
        # Metin yoğunluğu fazla olduğu için yüksekliği 220'ye sabitledik.
        kutu_rect = pygame.Rect(60, 20, GENISLIK - 120, 220) 
        
        # Saydam Arka Plan
        s_surface = pygame.Surface((kutu_rect.width, kutu_rect.height))
        s_surface.set_alpha(200)
        s_surface.fill((20, 20, 35)) 
        self.pencere.blit(s_surface, (kutu_rect.x, kutu_rect.y))
        
        # Beyaz Çerçeve
        pygame.draw.rect(self.pencere, (230, 230, 230), kutu_rect, 2)
        
        max_metin_genisligi = kutu_rect.width - 60
        y_offset = kutu_rect.y + 20

        # --- NPC METNİNİ ÇİZ ---
        npc_metni = node.get('npc_text', '...')
        tam_metin = f"{npc_ismi}: {npc_metni}" if npc_ismi else npc_metni
        npc_satirlar = self.metni_sar(tam_metin, self.font_diyalog_npc, max_metin_genisligi)
        
        for satir in npc_satirlar:
            n_surf = self.font_diyalog_npc.render(satir, True, ALTIN)
            self.pencere.blit(n_surf, (kutu_rect.x + 30, y_offset))
            y_offset += 30 

        # --- SEÇENEKLERİ ÇİZ ---
        options = node.get("options", [])
        if options:
            y_offset += 10 # Konuşma ile seçenekler arası boşluk
            for i, opt in enumerate(options):
                opt_metni = f"[{i+1}] - {opt.get('text', '')}"
                
                # Seçenek metni de uzun olabileceği için sarmalıyoruz
                opt_satirlar = self.metni_sar(opt_metni, self.font_diyalog_secenek, max_metin_genisligi - 20)
                
                for satir in opt_satirlar:
                    o_surf = self.font_diyalog_secenek.render(satir, True, BEYAZ)
                    self.pencere.blit(o_surf, (kutu_rect.x + 40, y_offset))
                    y_offset += 26
                y_offset += 8 # Seçenekler arası ekstra boşluk
        else:
            # Seçenek yoksa Space uyarısını göster
            bitis_mesaji = self.font_diyalog_secenek.render("[ DEVAM ETMEK İÇİN SPACE ]", True, ALTIN)
            mesaj_rect = bitis_mesaji.get_rect(centerx=GENISLIK // 2, bottom=kutu_rect.bottom - 20)
            self.pencere.blit(bitis_mesaji, mesaj_rect)

    def feedback_ekrani_ciz(self, alt_not="[ SONRAKİ BÖLÜM İÇİN ESC ]"):
        """Bölüm sonu analiz ekranı."""
        overlay = pygame.Surface((GENISLIK, YUKSEKLIK))
        overlay.set_alpha(240)
        overlay.fill(SIYAH)
        self.pencere.blit(overlay, (0, 0))
        
        baslik = self.font_baslik.render("BÖLÜM ANALİZİ", True, ALTIN)
        self.pencere.blit(baslik, (GENISLIK // 2 - baslik.get_width() // 2, 50))
        
        y_pos = 130
        for item in self.secilen_feedbackler:
            # Seçim
            s_surf = self.font_ana.render(f"> Seçim: {item['secim']}", True, (100, 200, 255))
            self.pencere.blit(s_surf, (100, y_pos))
            y_pos += 35
            
            # Analiz
            analiz_satirlar = self.metni_sar(f"Etik Analiz: {item['analiz']}", self.font_secenek, GENISLIK - 200)
            for satir in analiz_satirlar:
                a_surf = self.font_secenek.render(satir, True, BEYAZ)
                self.pencere.blit(a_surf, (130, y_pos))
                y_pos += 28
            y_pos += 25
            
        alt_surf = self.font_secenek.render(alt_not, True, ALTIN)
        self.pencere.blit(alt_surf, (GENISLIK // 2 - alt_surf.get_width() // 2, YUKSEKLIK - 70))
