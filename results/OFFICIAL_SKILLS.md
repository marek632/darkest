# Najlepszy skład + zestawy umiejętności (wspólna optymalizacja)

Przestrzeń: C(10,4)=210 składów × 35⁴ zestawów ≈ 315 mln drużyn.
Metoda: generalista RL (jedna głowa, trening na losowych klasach i
losowych zestawach 3/7 — żadna drużyna nie ma „lepszego AI") →
przesiew 210 składów (30 wspólnych seedów, losowe zestawy) →
wspinaczka po współrzędnych po wszystkich 35 zestawach na postać
(30 wspólnych seedów) → walidacja 300 seedów → dogrywka finalistów
na 800 świeżych seedach. Benchmark przeszukiwania: **6 komnat**
(3-komnatowy nasyca się — czołowe drużyny wygrywają ~100% niezależnie
od kart; przy 6 komnatach kumulująca się erozja HP/stresu/światła
różnicuje zestawy). Dane: `official_skills.json`,
`official_showdown.json`.

## Werdykt — najlepsza znana drużyna

**Arlekin + Awanturniczka + Hiena Cmentarna + Kapłanka** —
**91,4%** (CI 89,2–93,1%) na 800 świeżych 6-komnatowych wyprawach,
najmniej zgonów w finale (0,70/wyprawę); na standardowej 3-komnatowej
wyprawie ≈ 99–100%.

| Postać | Zestaw umiejętności |
|---|---|
| Arlekin | Pchnięcie sztyletem, Ukłon, Żniwa |
| Awanturniczka | Żelazny łabędź, Szerokie cięcie, Okrutne cięcie |
| Hiena Cmentarna | Wypad, Rzut sztyletem, Zatrute strzałki |
| Kapłanka | Boskie pocieszenie, Osąd, Boża łaska |

Dogrywka (800 seedów, wspólne dla wszystkich):

| Drużyna | Zwycięstwa | CI | Zgony | p vs mistrz |
|---|---|---|---|---|
| **Arlekin+Awant.+Hiena+Kapłanka** | **91,4%** | 89,2–93,1% | 0,70 | — |
| Arlekin+Awant.+Hiena+Oprych | 89,6% | 87,3–91,6% | 0,88 | 0,23 |
| Arlekin+Awant.+Badaczka+Oprych (opt.) | 89,0% | 86,6–91,0% | 1,07 | 0,11 |
| Arlekin+Awant.+Okultysta+Oprych | 85,2% | 82,6–87,5% | 1,04 | 0,0001 |

Ściśle: dwie pierwsze pozycje pozostają w remisie statystycznym
(p=0,23); mistrz ma najlepszy punktowy wynik ORAZ wyraźnie najmniej
zgonów. Czwórka z Okultystą odpada istotnie.

## Co znaczą umiejętności — twarde fakty z przeszukiwania

* **Zestaw potrafi być wart +32 punkty procentowe.** Dla składu
  Arlekin+Kapłanka+Kuszniczka+Oprych zestawy domyślne dawały 50,3%,
  po wspinaczce 82,0% (walidacja 300 świeżych seedów). Dobór kart
  bywa ważniejszy niż dobór czwartej klasy.
* **Karty-rdzenie** (wybierane przez optymalizator prawie zawsze,
  niezależnie od reszty drużyny): Oprych — Doskok + Wystrzał (6/6);
  Arlekin — Ukłon (6/6) i Żniwa (5/6); Awanturniczka — Żelazny łabędź
  (5/6); Kapłanka — Boskie pocieszenie (3/3).
* **Trzon Arlekin+Awanturniczka jest niepodważalny** — powtarza się w
  całej czołówce obu turniejów (klasowego i łącznego).
* Przy dobrych zestawach bazowych wspinaczka na 30 seedach nie
  odróżnia już wariantów (29–30/30) — kilka „ulepszeń" okazało się w
  walidacji szumem. Dlatego finał rozstrzygnęła dogrywka na 800
  świeżych seedach, a nie wynik wspinaczki.

## Zastrzeżenia

Wspinaczka po współrzędnych znajduje optimum lokalne (start z zestawów
kuratorskich); ocenia jeden wspólny model, więc ranking jest względem
jego stylu gry — słabiej ogranemu stylowi (np. maksymalna kontrola)
mogłaby pomóc dłuższa nauka. Wartości kart oznaczone `(?)` w
`docs/CARDS_PL.md` po ewentualnej korekcie odczytu mogą przesunąć
szczegóły zestawów.
