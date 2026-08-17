# Karty z pudełka (zdjęcia od właściciela): bohaterowie, umiejętności, bossowie

Źródło pierwotne: fotografie kart z polskiej edycji Darkest Dungeon: Gra
planszowa. Ten plik jest jedynym źródłem danych dla silnika w
`ddsim/official/`. Wartości niepewne (drobne ikony) oznaczone `(?)`.

## Legenda ikon (moja interpretacja odczytu)

* Wiersz 4 ramek u góry karty umiejętności = **Wymagane Postawy**;
  podświetlone = dozwolone. Odczyt ikon: sztandar/filar = **Wspierająca
  (W)**, wachlarz noży = **Zasięgowa (Z)**, tarcza = **Defensywna (D)**,
  miecz = **Agresywna (A)**. Kolejność na karcie: W · Z · D · A —
  wnioskowana z kart jednoznacznych (Gwiazda poranna = walka wręcz →
  tarcza+miecz; Święta lanca = skok z tyłu → filar+noże). **(?)** do
  potwierdzenia legendą z instrukcji.
* `⤵N` = Zasięg (obszary płytki; 0 = własny obszar; `1-2` = zakres;
  `2` = dokładnie 2).
* Czaszki czerwone = liczba celów-wrogów; hełmy złote = cele-sojusznicy.
* `Krytyk X [c] Dok. Y [d]` = rzut K10: ≤X−mod = kryt (obrażenia c),
  ≤Y−Unik = trafienie (obrażenia d). Zielone liczby = leczenie.
* Ikony efektów: 🔴 kropla = Krwotok, 🟢 kropla = Zaraza, ♦♦♦ żółte =
  Ogłuszenie, ⇈ niebieskie = Wzmocnienie, ⇊ czerwone = Osłabienie,
  ◎ = Naznaczenie, pancerz = Ochrona, ↯ = Riposta, « = Odepchnięcie/
  Przyciągnięcie, 🔥 = Światło, szara głowa = stres, zielony plus = leczenie.
* `Na siebie` = efekt osobisty (działa zawsze przy użyciu); efekty celu
  wymagają trafienia.

## Panele bohaterów (11 postaci, poziom I)

Format: Unik (złota ikona) / Wytrzymałość (serce) / Szybkość (buty) /
Odporność. Wszyscy: kość Progu Śmierci; Zdolność Osady = warstwa
kampanii (poza symulacją bitwy).

| Bohater | Unik | Wytrz. | Szyb. | Odporność | Zdolność Osady |
|---|---|---|---|---|---|
| Krzyżowiec | 0 | 17 | 1 | Ogłuszenie | Żarliwa przemowa (koniec dnia: inni bez akcji, −5 stresu każdy) |
| Kapłanka | 0 | 12 | 1 | Krwotok | Modlitwa (−9 stresu, wzmocnienie(?) 6t) albo Psalm (4 pomocników: −1 stres, ⇈3t) |
| Oprych | 1 | 12 | 2 | Ogłuszenie | Czyszczenie spluw (⇈6t) |
| Awanturniczka | 1 | 14 | 2 | Krwotok | Ostrzenie broni (⇈5t) albo Zastraszenie (usuń Stróża do końca dnia) |
| Okultysta | 1 | 10 | 2 | Osłabienie | Diaboliczny rytuał (+1 stres; cel: +2 lecz., −2 stres, ⇈3t) |
| Wynaturzenie | 1 | 13 | 2 | Zaraza | Bestialski trening / Opanowanie |
| Arlekin | 2 | 10 | 3 | Osłabienie | Nie ma róży bez kolców (−2 stresu za każdą kartę/…) |
| Kuszniczka | 0 | 14 | 1 | Przesuwanie | Gotowość bojowa (K10: leczenie/stres) |
| Badaczka Zarazy | 0 | 11 | 3 | Zaraza | Eksperymentalne remedium (+4 lecz., usuń chorobę, +3 stres(?)) |
| Hiena Cmentarna | 1 | 11 | 3 | Zaraza | Szaber (dobierz kartę) |
| Łowca Nagród | 1 | 14 | 2 | Ogłuszenie | Daleki zwiad (+1 stres; odkryj komnatę na starcie zadania) |

**Korekta wsteczna:** liczba przy złotej postrzępionej ikonie na kartach
potworów (wcześniej wpisana do tabeli jako „Szybkość") to w
rzeczywistości **Unik** — zgadza się z przykładem z instrukcji
(Kościany Kusznik: Unik 1). Szybkość potworów pozostaje nieznana
(przyjęte: 2, oznaczone jako założenie).

## Umiejętności bohaterów (poziom I, 7 kart każdy)

Format: Postawy | Zasięg | Cele | Krytyk [c] / Dok [d] | Efekty.

### Krzyżowiec
| Karta | Post. | Zas. | Cele | K/D | Efekty |
|---|---|---|---|---|---|
| Kara boska | DA | 0 | 1 wróg | 0 [13] / 9 [7] | +1 kontra Plugawy |
| Ogłuszający cios | DA | 0 | 1 wróg | 0 [8] / 9 [4] | Ogłuszenie 1t |
| Święta lanca | WZ | 1 | 1 wróg | 1 [13] / 9 [7] | Na siebie: Przyciągnięcie 1; +1 kontra Plugawy |
| Bastion wiary | DA(?) | — | na siebie | — | Na siebie: Ochrona 2t, Garda(?) 3t, Światło +2(?) |
| Inspirujący okrzyk | WZDA(?) | 0 | 1 sojusznik | — | lecz. +1, stres −1, Światło +1 |
| Pierwsza pomoc | WZDA | 0-1 | 1 sojusznik | 2 [+4] / 12 [+2] | leczenie |
| Żarliwe oskarżenie | DA(?) | 1 | 2 wrogów | 0 [9] / 9 [5] | — |

### Kapłanka
| Karta | Post. | Zas. | Cele | K/D | Efekty |
|---|---|---|---|---|---|
| Gwiazda poranna | DA | 1 | 1 wróg | 0 [9] / 9 [5] | +1 kontra Plugawy |
| Oślepiająca światłość | WZD(?) | 1 | 1 wróg | 1 [4] / 9 [2] | Ogłuszenie 1t, Światło +1 |
| Boskie pocieszenie | WZD | 1 | 3 sojuszników | 3 [+3] / 12 [+2] | Na siebie: lecz. +2 |
| Osąd | WZ | 1-2 | 1 wróg | 1 [8] / 9 [4] | Na siebie: lecz. +2 |
| Boża łaska | WZ | 0-1 | 1 sojusznik | 3 [+5] / 12 [+3] | leczenie |
| Oświecenie | WZ(?) | 1-2 | 1 wróg | 0 [4] / 9 [2] | Osłabienie 1t, Światło +1 |
| Ręka światłości | DA(?) | 1 | 1 wróg | 1 [6] / 9 [3] | Na siebie: Wzmocnienie 3t; +1 kontra Plugawy |

### Oprych
| Karta | Post. | Zas. | Cele | K/D | Efekty |
|---|---|---|---|---|---|
| Doskok | WZDA | 1 | 1 wróg | 1 [8] / 9 [4] | Na siebie: Riposta 2t, Przyciągnięcie 1 |
| Strzał z bliska | WZD(?) | 0 | 1 wróg | 1 [15] / 10 [9] | Na siebie: Odepchnięcie 1; cel: Odepchnięcie 1 |
| Strzał naprowadzający | WZ(?) | 1-2 | 1 wróg | 0 [3] / 10 [2] | Na siebie: Wzmocnienie 3t |
| Puszczenie krwi | ZDA(?) | 0 | 1 wróg | 0 [9] / 10 [5] | Krwotok 2/2t |
| Siekańce | ZD(?) | 0-1 | 3 wrogów | 0 [5] / 8 [3] | Osłabienie 1t |
| Wystrzał | WZ(?) | 1-2 | 1 wróg | 1 [9] / 9 [5] | +2 kontra Naznaczony |
| Ohydne cięcie | DA(?) | 0 | 1 wróg | 1 [11] / 9 [7] | — |

### Awanturniczka
| Karta | Post. | Zas. | Cele | K/D | Efekty |
|---|---|---|---|---|---|
| Szerokie cięcie | ZDA(?) | 1 | 3 wrogów | 0 [6] / 8 [4] | Na siebie: Przyciągnięcie 1 |
| Okrutne cięcie | DA | 0 | 1 wróg | 1 [12] / 9 [7] | — |
| Żelazny łabędź | DA(?) | 2 | 1 wróg | 1 [12] / 9 [7] | — |
| Rozlew krwi | DA | 0 | 1 wróg | 1 [14] / 9 [9] | Na siebie: 3 rany; Krwotok 3/2t |
| Każdy krwawi | ZDA(?) | 1 | 1 wróg | 0 [8] / 9 [5] | Krwotok 2/2t |
| Przypływ adrenaliny | WZDA | — | na siebie | — | Usuń Krwotok+Zarazę, Wzmocnienie 3t |
| Barbarzyński ryk | DA(?) | 0 | 2 wrogów | — / 10 | Ogłuszenie 1t |

### Okultysta
| Karta | Post. | Zas. | Cele | K/D | Efekty |
|---|---|---|---|---|---|
| Mroczna rekonstrukcja | WZ | 0-1 | 1 sojusznik | 3 [+8] / 9 [+4] | cel: Krwotok 1/2t |
| Uścisk demona | WZD(?) | 2 | 1 wróg | 1 [4] / 9 [3] | Przyciągnięcie 2 |
| Artyleria otchłani | WZ | 2 | 2 wrogów | 0 [6] / 9 [4] | +1 kontra Przedwieczny |
| Klątwa osłabienia | WZD(?) | 1-2 | 1 wróg | 1 [3] / 10 [2] | Osłabienie 2t |
| Cięcie ofiarne | ZDA(?) | 0 | 1 wróg | 1 [7] / 8 [5] | +1 kontra Przedwieczny |
| Przekleństwo | WZ(?) | 1-2 | 1 wróg | 1 [2] / 10 [1] | Naznaczenie 2t |
| Macki otchłani | DA(?) | 1 | 1 wróg | 1 [4] / 9 [3] | Ogłuszenie 2t, Światło −1 |

### Arlekin
| Karta | Post. | Zas. | Cele | K/D | Efekty |
|---|---|---|---|---|---|
| Pchnięcie sztyletem | WZDA | 1 | 1 wróg | 1 [7] / 9 [5] | Na siebie: Przyciągnięcie 1; Ignoruje Ochronę |
| Ukłon | DA | 0 | 1 wróg | 1 [10] / 14 [7] | Na siebie: Odepchnięcie 3 |
| Solówka | WZ(?) | 2 | 1 wróg | — / 12 | Na siebie: Wzmocnienie 2t, Przyciągnięcie 2; cel: Ogłuszenie(?) 1t |
| Inspirująca nuta | WZ | 0 | 2 sojuszników | 2 / 20 | Na siebie: stres −1; cel: stres −1 |
| Heroiczna ballada | WZ(?) | 1 | 2 sojuszników | — | Na siebie: Wzmocnienie 2t; cel: Wzmocnienie 2t |
| Żniwa | DA(?) | 1 | 2 wrogów | 0 [4] / 9 [3] | Krwotok 2/2t |
| Urwany wątek | ZD(?) | 1 | 1 wróg | 1 [6] / 10 [4] | Krwotok 3/1t |

### Badaczka Zarazy
| Karta | Post. | Zas. | Cele | K/D | Efekty |
|---|---|---|---|---|---|
| Panaceum | WZ | 0 | 1 sojusznik | 1 [+2] / 20 [+1] | Usuń Krwotok+Zarazę |
| Trujący podmuch | WZD(?) | 1 | 1 wróg | 1 [4] / 9 [2] | Zaraza 4/2t, Osłabienie 1t |
| Granat zarazy | WZ | 2 | 2 wrogów | 0 [2] / 9 [1] | Zaraza 3/2t |
| Nacięcie | ZDA(?) | 0 | 1 wróg | 1 [8] / 9 [5] | Krwotok 2/2t |
| Gaz oślepiający | WZ | 1-2 | 2 wrogów | — / 9 | Ogłuszenie 1t |
| Sole trzeźwiące | WZ(?) | 0 | 1 sojusznik | — | Wzmocnienie 3t |
| Podmuch zamętu | WZD(?) | 1 | 1 wróg | — / 9 | Odepchnięcie 2 LUB Przyciągnięcie 2; Ogłuszenie 1t |

### Kuszniczka
| Karta | Post. | Zas. | Cele | K/D | Efekty |
|---|---|---|---|---|---|
| Bandażowanie | WZ | 0-1 | 1 sojusznik | 0 [+6] / 8 [+4] | Na siebie: Wzmocnienie(?) 2t |
| Priorytetowy cel | WZ | 1-2 | 1 wróg | — / 10 | Naznaczenie 2t |
| Bolas | WZ | 1 | 1 wróg | 1 [6] / 10 [3] | Na siebie: Odepchnięcie 1; cel: Odepchnięcie 2 |
| Na oślep | WZDA | 0-2 | 1 wróg | 0 [8] / 8 [5] | Na siebie: Odepchnięcie 1 |
| Ogień zaporowy | WZ | 1-2 | 2 wrogów | 0 [4] / 9 [2] | Osłabienie 1t |
| Snajperska precyzja | WZ | 2 | 1 wróg | 1 [9] / 9 [6] | +3 kontra Naznaczony |
| Flara | WZ | 1-2 | 1-2 dowolne | — / 10 | Na siebie: usuń Ogłuszenie+Naznaczenie; sojusznik: usuń Ogłuszenie+Naznaczenie; wróg: Osłabienie 2t |

### Hiena Cmentarna
| Karta | Post. | Zas. | Cele | K/D | Efekty |
|---|---|---|---|---|---|
| Rzut sztyletem | WZD(?) | 1-2 | 1 wróg | 2 [7] / 9 [4] | +1 kontra Zaraza, +2 kontra Naznaczony |
| Rozłupanie czaszki | ZDA(?) | 0 | 1 wróg | 1 [7] / 9 [4] | Ignoruje Ochronę |
| Zatrute strzałki | WZ | 1-2 | 1 wróg | 1 [4] / 10 [2] | Zaraza 2/3t |
| Wypad | WZ | 2 | 1 wróg | 1 [11] / 10 [7] | Na siebie: Przyciągnięcie 2; +2 kontra Zaraza |
| Nawałnica sztyletów | ZD(?) | 1 | 2 wrogów | 0 [6] / 9 [3] | — |
| Odsunięcie w cień | DA(?) | — | na siebie | — | Na siebie: Wzmocnienie 2t, Odepchnięcie 2 |
| Środki dopingujące | WZDA | — | na siebie | — | Na siebie: Wzmocnienie 2t, usuń Krwotok+Zarazę |

### Wyrzutek → **Wynaturzenie** (8 kart: 2 transformacje + 6 bojowych)
| Karta | Forma | Post. | Zas. | Cele | K/D | Efekty |
|---|---|---|---|---|---|---|
| Potworna żółć | Człowiek | ZD(?) | 1-2 | 2 wrogów | 0 [3] / 10 [2] | Zaraza 2/2t |
| Kajdany | Człowiek | ZD(?) | 1 | 1 wróg | 0 [6] / 10 [4] | Ogłuszenie 1t |
| Rozgrzeszenie | Człowiek | WZ(?) | — | na siebie | 1 [+4] / 12 [+2] | Na siebie: stres −1 |
| Transformacja w Bestię (II) | Człowiek | WZDA | — | wszyscy sojusznicy | — | Na siebie: forma Bestii, Wzmocnienie 3t, lecz. +6; sojusznicy: stres +2 |
| Roztrzaskanie | Bestia | DA(?) | 1 | 1 wróg | 0 [10] / 8 [7] | Na siebie: Przyciągnięcie 1, stres +1; cel: Odepchnięcie 2, Osłabienie 1t |
| Szał | Bestia | DA(?) | 0 | 1 wróg | 1 [12] / 9 [9] | Na siebie: stres +1 |
| Pokiereszowanie | Bestia | DA(?) | 0 | 2 wrogów | 0 [9] / 9 [5] | Na siebie: Wzmocnienie 2t, stres +1 |
| Transformacja w człowieka | Bestia | WZDA | — | wszyscy sojusznicy | — | Na siebie: forma Człowieka, Osłabienie 3t, stres −1; sojusznicy: stres −1 |

### Łowca Nagród
| Karta | Post. | Zas. | Cele | K/D | Efekty |
|---|---|---|---|---|---|
| Do mnie | WZDA(?) | 2 | 1 wróg | 0 [4] / 9 [2] | Naznaczenie 2t, Przyciągnięcie 2 |
| Wykonanie wyroku | ZDA(?) | 0 | 1 wróg | 1 [10] / 9 [6] | +1 kontra Człowiek, +2 kontra Naznaczony |
| Wyrok śmierci | WZD(?) | 0-2 | 1 wróg | — / 10 | Na siebie: Wzmocnienie 2t; cel: Naznaczenie 3t, Osłabienie 2t |
| Egzekucja | ZDA(?) | 0-1 | 1 wróg | 1 [10] / 9 [6] | +2 kontra Ogłuszony |
| Podbródkowy | DA(?) | 0 | 1 wróg | 0 [5] / 9 [3] | Ogłuszenie 1t, Odepchnięcie 2 |
| Granat błyskowy | WZ(?) | 1-2 | 1 wróg | — / 10 | Ogłuszenie 1t, Odepchnięcie 1 LUB Przyciągnięcie 1 |
| Kolczatki | WZD(?) | 2 | 1 wróg | 1 [2] / 9 [1] | Krwotok 2/3t, Osłabienie 1t |

## Bossowie (6 kart, poziom III)

Format: rodzina · pozycja · rozmiar; Unik (złota ikona); Wytrzymałość.
Liczba akcji na rundę: przyjęta 2 (talia inicjatywy proporcjonalna do
akcji — instrukcja; dokładna liczba per boss nieznana → założenie).
Tabele u dołu kart (postawa/K10 → numer umiejętności) odczytane częściowo.

| Boss | Typ | Unik | Wytrz. | Odporn./Niewrażl. | Umiejętności |
|---|---|---|---|---|---|
| Prorok | Plugawy·Front·Duży | 3 | 151 | odp. Ogłuszenie(?); niewr. Przesuwanie | 1: Mam cię na oku — Zatłoczony ⤵1, 2 cele, K1 [5]/D11 [3], Zaraza(?) 2t, stres +1 · 2: Odrzucenie — Zatłoczony ⤵1, 4 cele, K1 [5]/D10 [3], Zaraza 3/3t(?) · 3: W gruz się obrócisz — Specjalna (Strzaskane Ławki), K0 [24]/D10 [16] |
| Fanatyk | Człowiek·Front·Duży | 2 | 72 | odp. Zaraza; niewr. Przesuwanie | 1: Słuszne potępienie — Zatłoczony ⤵2, 4 cele, K0 [4]/D12 [2], na siebie Wzmocnienie 3t, stres +2(?) · 2: Pogromienie heretyków — Najbardziej zestresowany ⤵1, K1 [11]/D11 [6], Ogłuszenie 1t, Odepchnięcie 2, stres +1 · 3: Sprawiedliwa furia — Zatłoczony ⤵1, 4 cele, K0 [14]/D11 [10], stres +1 |
| Serce Ciemności | Demiurgiczny·Duży | 3 | 250 | odp. Osłabienie; niewr. Ogłuszenie+Przesuwanie | 1: Ujrzyj prawdę — Zatłoczony ⤵0-10, 3 cele, K1 [3]/D12 [2], stres +3, Światło −1 · 2: Nakłucie — Najbliższy ⤵0-10, K2 [18]/D12 [14], Krwotok 3/3t, stres +1 · 3: Zniweczenie — Najdalszy ⤵0-10, K2 [18]/D12 [14], Ogłuszenie 1t, Zaraza 3/3t, stres +1 |
| Brzemienne Serce | Przedwieczny·Duży·Front | 3 | 100 | odp. Zaraza; niewr. Ogłuszenie(?)+Przesuwanie | 1: Przywołanie — przyzywa potwora z talii; pasywnie (instrukcja str. 38–40): bohater raniący Serce dostaje 2 Zarazy 3t, a Serce leczy 2 |
| Druga Forma Antenata | Przedwieczny·Człowiek·Duży·Front | 2 | 166 | niewr. Przesuwanie(?) | 1: Przetworzenie — Zatłoczony ⤵1, 2 cele, K2 [16]/D12 [9], Krwotok 3/3t, stres +1, Światło −1 · 2: Masowa anihilacja — Najdalszy ⤵2, K1 [8]/D12 [4], Zaraza 2/4t, stres +1 · 3: Objęcia beznadziei — Najbliższy ⤵0, K0 [4]/D12 [2], Osłabienie 2t, stres +2, Odepchnięcie 2 |
| Powłócząca Przeraza | Przedwieczny·Duży·Front | 3 | 109 | odp. Zaraza; niewr. Przesuwanie+Ogłuszenie(?) | 1: Rozprucie — Najbliższy ⤵1, K1 [11]/D11 [7], Krwotok 3/2t · 2: Negatywne wibracje — Zatłoczony ⤵1, 4 cele, K0 [2]/D11 [1], „Potasujcie znaczniki postaw bohaterów" · 3: Rezonujący rozkład — Zatłoczony ⤵1, 4 cele, K1 [4]/D12 [2], stres +2, Światło −1 |

## Główne pozostałe niepewności (do potwierdzenia przez właściciela)

1. **Mapowanie ikon postaw** na kartach (kolejność W·Z·D·A) — pewne
   funkcjonalnie, nie literalnie; pojedyncze karty mogą mieć inny zestaw
   postaw niż odczytany (oznaczone `(?)`).
2. **Bastion wiary**: odczyt „Ochrona 2t + Garda 3t + Światło +2" —
   szczególnie ikona Gardy vs Naznaczenia i Światło +2.
3. **Szybkość potworów i bossów** — nieznana (przyjęte 2).
4. **Liczba akcji bossów na rundę** — przyjęte 2.
5. **Tabele K10 postaw bossów** — odczytane fragmentarycznie, przyjęte
   rozkłady w `ddsim/official/monsters.py`.
6. Efekty drobnych ikon przy bossach oznaczone `(?)`.
