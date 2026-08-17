# Ranking składów (silnik oficjalny, jeden wspólny model RL)

Model: `DDNet2(unified=True)` — jedna głowa polityki dla wszystkich 10
klas (bez Wynaturzenia); tożsamość postaci przez embedding typu +
wektor własnych umiejętności; dopasowanie do składu przez uwagę nad
tokenami sojuszników. Trening: 8000 epizodów, każdy na losowej
NIEUPORZĄDKOWANEJ kombinacji 4 z 10 klas (permutacje nierozróżniane —
szyk można przestawiać w grze). 117k parametrów.

Turniej: przesiew wszystkich C(10,4)=210 kombinacji × 30 wspólnych
seedów → walidacja top-20 × 200 świeżych seedów (kontrola przekleństwa
zwycięzcy). Dane: `results/official_rank.json`.

## Czołówka (walidacja, 200 świeżych wypraw)

| Skład | Zwycięstwa | 95% CI | Zgony |
|---|---|---|---|
| Arlekin + Awanturniczka + Hiena Cmentarna + Oprych | **100%** | 98,1–100% | 0,22 |
| Arlekin + Awanturniczka + Hiena Cmentarna + Krzyżowiec | **100%** | 98,1–100% | 0,23 |
| Arlekin + Awanturniczka + Badaczka Zarazy + Hiena Cmentarna | **100%** | 98,1–100% | 0,26 |
| Arlekin + Awanturniczka + Okultysta + Oprych | **100%** | 98,1–100% | 0,20 |
| Arlekin + Awanturniczka + Kapłanka + Oprych | 99,5% | 97,2–99,9% | 0,24 |
| Arlekin + Awanturniczka + Hiena Cmentarna + Kuszniczka | 99,5% | 97,2–99,9% | 0,24 |
| Arlekin + Awanturniczka + Badaczka Zarazy + Oprych | 99,5% | 97,2–99,9% | 0,23 |

Czołówka jest statystycznie zbita (nakładające się CI); wspólny motyw
jest jednak jednoznaczny.

## Wnioski strukturalne

* **Awanturniczka (17/20) i Arlekin (14/20) dominują czołówkę.**
  Arlekin — klasa, którą pierwotny zachłanny algorytm bez planszy
  oceniał jako najsłabszą — po dodaniu ruchu, szyku i ekonomii 2 akcji
  wchodzi do niemal wszystkich najlepszych składów. To potwierdza
  pierwotną hipotezę właściciela gry.
* **Łowca Nagród wypada najsłabiej** (18/20 najgorszych składów):
  kontrola (Naznaczenie/Ogłuszenie) nie nadąża za presją limitu 4 rund
  przy przeciętnych obrażeniach.
* Składy bez realnych obrażeń (np. Badaczka+Kapłanka+Kuszniczka+
  Okultysta) wygrywają ~0% — timeout ich zjada.
* **Skład pudełkowy** (Krzyżowiec+Kapłanka+Oprych+Awanturniczka):
  30/30 w przesiewie, 96,5% (93,0–98,3%) w walidacji — bardzo dobry,
  ale o włos za ścisłą czołówką.
* Mediana przesiewu: 27/30 — większość składów jest grywalna, ogon
  jest głęboki (minimum 0/30).

## Uczciwość porównania i zastrzeżenia

* Wszystkie składy ocenia TEN SAM model — żadnemu nie sprzyja lepiej
  wytrenowane AI. Ekspozycja treningowa na każdą kombinację jest
  z grubsza równa (~38 epizodów/kombinację) — to mało; ranking środka
  stawki jest szacunkowy, czołówka i ogon są wyraźne.
* Koszt unifikacji: model wspólny gra składem pudełkowym na 83,0%
  (78,3–86,8%) vs 98,2% modelu specjalistycznego z per-klasowymi
  głowami trenowanego tylko na tym składzie. W tej różnicy mieszają
  się dwie zmiany naraz (wspólna głowa + trening na 210 składach);
  dłuższy trening powinien ją zawęzić.
* Na losowych składach generalista: 73,3% vs heurystyka 69,7%
  (p=0,32, n.s.) — średnią obu zaniżają składy strukturalnie
  przegrane; różnice robią się duże dopiero na dobrych składach
  (pudełkowy: 83,0% vs 19,7%).
