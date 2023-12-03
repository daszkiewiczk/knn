import tkinter as tk
from tkinter import filedialog
import csv
import math

dane_uczace = []
liczba_kategorii = 0
WIDTH=600
HEIGHT=400

# Funkcja do wczytania danych z pliku tekstowego
def wczytaj_dane():
    nazwa_pliku = filedialog.askopenfilename(filetypes=[("Pliki tekstowe", "*.txt")])
    if nazwa_pliku:
        global dane_uczace, liczba_kategorii
        
        with open(nazwa_pliku, 'r') as plik:
            czytnik = csv.reader(plik)
            min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
            for wiersz in czytnik:
                # Wczytaj dane z pliku
                x, y = float(wiersz[0]), float(wiersz[1])
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
                dane_uczace.append([x, y, int(wiersz[2])])
                if int(wiersz[2]) > liczba_kategorii:
                    liczba_kategorii = int(wiersz[2])

        # Normalizacja danych metodą Min-Max
        for punkt in dane_uczace:
            punkt[0] = (punkt[0] - min_x) / (max_x - min_x)
            punkt[1] = (punkt[1] - min_y) / (max_y - min_y)
    print(dane_uczace)
    print(liczba_kategorii)
    canvas.delete("all")  # Wyczyść obszar przed narysowaniem nowych punktów
    for punkt in dane_uczace:
        x, y = punkt[0]*WIDTH, punkt[1]*HEIGHT
        kategoria = punkt[2]
        rozmiar_punktu = 5
        kolor_kategorii = ['blue', 'orange', 'yellow', 'purple', 'cyan', 'pink']
        canvas.create_oval(x - rozmiar_punktu, y - rozmiar_punktu, 
                            x + rozmiar_punktu, y + rozmiar_punktu, 
                            fill=kolor_kategorii[kategoria])

# Obliczanie odległości między punktami
def odleglosc(punkt1, punkt2, metryka='euklidesowa'):
    if metryka == 'euklidesowa':
        return math.sqrt((punkt1[0] - punkt2[0])**2 + (punkt1[1] - punkt2[1])**2)
    elif metryka == 'miejska':
        return abs(punkt1[0] - punkt2[0]) + abs(punkt1[1] - punkt2[1])
    else:
        return None

# Funkcja do klasyfikacji punktu
def klasyfikuj_punkt(event, rodzaj_glosowania='proste', k=3):
    global odleglosc
    x, y = event.x, event.y
    punkt = (x, y)
    # Znajdź k najbliższych sąsiadów i dokonaj klasyfikacji
    odleglosci = []
    for i, obserwacja in enumerate(dane_uczace):
        odleglosci.append((i, odleglosc(punkt, obserwacja[:2])))
    odleglosci.sort(key=lambda x: x[1])
    k_najblizsze = odleglosci[:k]
    
    # Dokonaj głosowania na podstawie wybranej metody
    licznik = [0] * (liczba_kategorii + 1)
    if rodzaj_glosowania == 'proste':
        for indeks, _ in k_najblizsze:
            kategoria = dane_uczace[indeks][2]
            licznik[kategoria] += 1
    elif rodzaj_glosowania == 'wazone':
        for indeks, odleglosc in k_najblizsze:
            kategoria = dane_uczace[indeks][2]
            licznik[kategoria] += 1 / (odleglosc ** 2)
    
    # Znajdź kategorię z największą liczbą głosów
    kategoria_wybrana = licznik.index(max(licznik))
    
    # Wizualizacja klasyfikacji i wyróżnienie sąsiadów
    canvas.delete("neighbors")  # Usuń poprzednie wyróżnienia sąsiadów
    for indeks, _ in k_najblizsze:
        punkt_uczacy = dane_uczace[indeks]
        x_uczacy, y_uczacy = punkt_uczacy[0], punkt_uczacy[1]
        if indeks == k_najblizsze[-1][0]:
            if kategoria_wybrana == punkt_uczacy[2]:
                kolor = 'green'  # Kolor zielony dla poprawnie sklasyfikowanego punktu
            else:
                kolor = 'red'  # Kolor czerwony dla niepoprawnie sklasyfikowanego punktu
            
            # Rysowanie kwadratu wokół klikniętego punktu
            rozmiar_kwadratu = 10
            canvas.create_rectangle(x - rozmiar_kwadratu, y - rozmiar_kwadratu, 
                                    x + rozmiar_kwadratu, y + rozmiar_kwadratu, 
                                    outline=kolor)
        
        # Wyróżnienie sąsiadów
        rozmiar_okregu = 5
        canvas.create_oval(x_uczacy - rozmiar_okregu, y_uczacy - rozmiar_okregu, 
                           x_uczacy + rozmiar_okregu, y_uczacy + rozmiar_okregu, 
                           outline='black', width=2, tags="neighbors")
    
    # Wizualizacja klasyfikacji klikniętego punktu
    rozmiar_okregu = 7
    canvas.create_oval(x - rozmiar_okregu, y - rozmiar_okregu, 
                       x + rozmiar_okregu, y + rozmiar_okregu, 
                       outline='black', width=2)
    canvas.create_text(x, y, text=str(kategoria_wybrana), fill='black', tags="neighbors")

# Tworzenie GUI
root = tk.Tk()
root.title("K-Najbliżsi Sąsiedzi")

# Przycisk do wczytania danych
btn_wczytaj = tk.Button(root, text="Wczytaj dane", command=wczytaj_dane)
btn_wczytaj.pack()

# Obszar wyświetlający punkty
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='white')
canvas.pack()


canvas.bind("<Button-1>", klasyfikuj_punkt)

root.mainloop()