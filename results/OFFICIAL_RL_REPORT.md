# RL na silniku oficjalnych zasad — wyniki

Silnik: `ddsim/official/` (dane z kart: `docs/CARDS_PL.md`).
Trening: `python -m ddsim.official.train --episodes 4000
--save models/rl_official.pt --eval-runs 400` (~20 min CPU, 447k
parametrów, seedy treningowe 710M+, ewaluacyjne 720M+ — rozłączne).

Drużyna: czwórka z pudełka (Krzyżowiec, Kapłanka, Oprych,
Awanturniczka), domyślne zestawy 3 umiejętności; wyprawa = 3 komnaty
z losowym doborem potworów z talii, odpoczynek 4 punkty między
komnatami, spadek światła, limit 4 rund na komnatę.

## Ewaluacja (400 identycznych wypraw, greedy)

| Polityka | Zwycięstwa | 95% CI | Zgony/wyprawę |
|---|---|---|---|
| **RL (transformer v2)** | **98,2%** | 96,4–99,1% | 0,32 |
| Heurystyka zachłanna | 19,5% | 15,9–23,7% | 0,32 |

Test dwóch proporcji: p < 0,0001. Krzywa treningu gładka: 0% → 96%
(sampling) w 4000 epizodów, bez zapaści entropii.

## Skąd ta różnica

Heurystyka przegrywa niemal wyłącznie przez **timeout z limitu 4 rund**
(78% wypraw) — na oficjalnych zasadach marnowanie akcji jest zabójcze.
RL kończy komnaty w limicie (2 timeouty na 150 wypraw).

Analiza behawioralna (150 wypraw, 7643 decyzje):

* **17% decyzji to zmiany szyku** (1303×) — model aktywnie tańczy
  postawami: Kapłanka przełącza się między postawami wspierającymi
  (Osąd/leczenie) a pozycją bezpieczną, Awanturniczka wraca do postaw
  przednich po odepchnięciach i ustawia legalność Szerokiego cięcia.
* Ruch po płytce jest rzadki (53×) — kafle są małe, zasięgi pokrywają
  większość odległości, a potwory same podchodzą; przestrzeń planszy
  gra głównie przez zasięgi i odpychanie, nie przez bieganie.
* Podział ról: Awanturniczka i Oprych = obrażenia (Szerokie cięcie przy
  zatłoczeniu, Żelazny łabędź na dystans 2, Puszczenie krwi/Doskok),
  Kapłanka = Osąd (obrażenia + samoleczenie), Krzyżowiec = tank-medyk
  (Pierwsza pomoc ~50% akcji, Kara boska na Plugawych).

## Zastrzeżenia

Wartości oznaczone `(?)` w `docs/CARDS_PL.md` (część postaw na kartach,
Bastion wiary, szybkość potworów, liczba akcji bossów) mogą po korekcie
właściciela zmienić szczegóły — architektura i pipeline treningu
pozostają te same. Warstwa wyprawy (3 komnaty, odpoczynek) jest
adaptacją — oficjalne karty zadań nie były fotografowane.
