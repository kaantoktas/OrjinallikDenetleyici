import tkinter as tk
from tkinter import scrolledtext
import requests
import json
import nltk
from nltk.tokenize import sent_tokenize



API_ANAHTARI = "AIzaSyDFK6R5OOhHi-byyo2CrkC1N7d1t_DOv3U"
ARAMA_MOTORU_ID = "kaantoktas"

class IntihalDenetleyici:
    def __init__(self, pencere):
        self.pencere = pencere
        self.pencere.title("İntihal Denetleyici")
        self.pencere.geometry("800x600")

        self.setup_ui()
    
    def setup_ui(self):
        baslik = tk.Label(self.pencere, text="Metin İntihal Denetleyicisi", font=("Arial", 20, "bold"))
        baslik.pack(pady=10)

        metin_etiketi = tk.Label(self.pencere, text="Lütfen kontrol etmek istediğiniz metni buraya yapıştırın:", font=("Arial", 12))
        metin_etiketi.pack(pady=(0, 5))
        
        self.metin_kutusu = scrolledtext.ScrolledText(self.pencere, width=80, height=15, font=("Arial", 12))
        self.metin_kutusu.pack(pady=10)

        
        kontrol_butonu = tk.Button(self.pencere, text="İntihali Denetle", command=self.intihali_denetle, font=("Arial", 14), bg="lightgreen")
        kontrol_butonu.pack(pady=10)

        sonuc_etiketi = tk.Label(self.pencere, text="Denetim Sonuçları:", font=("Arial", 12))
        sonuc_etiketi.pack(pady=(10, 5))
        
        self.sonuc_kutusu = scrolledtext.ScrolledText(self.pencere, width=80, height=10, font=("Arial", 12), state=tk.DISABLED)
        self.sonuc_kutusu.pack(pady=10)

    def intihali_denetle(self):
        self.sonuc_kutusu.config(state=tk.NORMAL)
        self.sonuc_kutusu.delete("1.0", tk.END)
        self.sonuc_kutusu.insert(tk.END, "Denetim başlatılıyor...\n")
        self.sonuc_kutusu.update()

        makale = self.metin_kutusu.get("1.0", tk.END).strip()
        if not makale:
            self.sonuc_kutusu.insert(tk.END, "Lütfen kontrol etmek için bir metin girin.")
            self.sonuc_kutusu.config(state=tk.DISABLED)
            return

        cumleler = sent_tokenize(makale, language="turkish")
        
        toplam_intihal = 0
        intihal_edilen_cumleler = []

        for cumle in cumleler:
            if len(cumle.split()) < 5:  
                continue

            arama_sorgusu = cumle
            url = f"https://www.googleapis.com/customsearch/v1?key={API_ANAHTARI}&cx={ARAMA_MOTORU_ID}&q={arama_sorgusu}"
            
            try:
                response = requests.get(url)
                response.raise_for_status()
                arama_sonuclari = response.json()
                
                if "items" in arama_sonuclari:
                    for item in arama_sonuclari["items"]:
                        if "snippet" in item and arama_sorgusu in item["snippet"]:
                            toplam_intihal += 1
                            intihal_edilen_cumleler.append(f"Cümle: '{cumle}'\nBulunan Kaynak: {item['link']}\n")
                            break
            except requests.exceptions.RequestException as e:
                self.sonuc_kutusu.insert(tk.END, f"API isteği sırasında hata oluştu: {e}\n")
                break
            
            self.sonuc_kutusu.update()

        oran = (toplam_intihal / len(cumleler)) * 100 if cumleler else 0
        self.sonuc_kutusu.insert(tk.END, f"\n--- Denetim Tamamlandı ---\n")
        self.sonuc_kutusu.insert(tk.END, f"İntihal Oranı: %{oran:.2f}\n\n")

        if intihal_edilen_cumleler:
            self.sonuc_kutusu.insert(tk.END, "İntihal Olarak İşaretlenen Cümleler:\n")
            for cumle_bilgisi in intihal_edilen_cumleler:
                self.sonuc_kutusu.insert(tk.END, cumle_bilgisi)
        else:
            self.sonuc_kutusu.insert(tk.END, "İntihal tespit edilmedi. Metin %100 özgün görünüyor.")

        self.sonuc_kutusu.config(state=tk.DISABLED)

if __name__ == "__main__":
    kok = tk.Tk()
    uygulama = IntihalDenetleyici(kok)
    kok.mainloop()