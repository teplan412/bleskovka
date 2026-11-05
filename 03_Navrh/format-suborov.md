# Formáty súborov

Bleskovka pracuje s dvoma typmi súborov:

| Súbor | Smer | Požiadavka / use case | Formáty |
|---|---|---|---|
| **Súbor s kvízom** (otázky) | import do editora kvízu | FR-009, UC-007 | CSV, Excel (`.xlsx`) |
| **Súbor s výsledkami** | export po skončení hry | FR-046, UC-026 | CSV, Excel (`.xlsx`) |

Vzorové súbory sú v adresári [`vzory/`](vzory/).

---

## 1. Súbor s kvízom (import otázok)

Súbor obsahuje **iba otázky**. Názov kvízu sa zadáva v editore a import pridá
otázky na koniec práve otvoreného kvízu (UC-007, výstupná podmienka).

### 1.1 Všeobecné pravidlá

| Vlastnosť | CSV | Excel (`.xlsx`) |
|---|---|---|
| Kódovanie | UTF-8 (s BOM aj bez neho) | – |
| Oddeľovač stĺpcov | bodkočiarka `;` (predvolený v slovenskom Exceli) | – |
| Hárok | – | číta sa iba **prvý hárok**, jeho názov je ľubovoľný |
| Prvý riadok | hlavička s názvami stĺpcov (povinná) | hlavička s názvami stĺpcov (povinná) |
| Úvodzovky | text so `;`, `"` alebo zalomením riadka sa uzavrie do `"…"`, vnútorná `"` sa zdvojí (RFC 4180) | – |
| Prázdne riadky | ignorujú sa | ignorujú sa |
| Medzery na začiatku a konci bunky | orežú sa | orežú sa |
| Max. počet otázok v jednom súbore | 100 | 100 |
| Max. veľkosť súboru | 1 MB | 1 MB |

Poradie stĺpcov je pevné. Názvy v hlavičke sa porovnávajú bez ohľadu na veľkosť písmen.

### 1.2 Stĺpce

| # | Stĺpec | Povinný | Obsah | Pravidlá |
|---|---|---|---|---|
| 1 | `otazka` | áno | text otázky | 1 – 200 znakov |
| 2 | `odpoved_a` | áno | 1. možnosť odpovede | 1 – 80 znakov |
| 3 | `odpoved_b` | áno | 2. možnosť odpovede | 1 – 80 znakov |
| 4 | `odpoved_c` | nie | 3. možnosť odpovede | 0 – 80 znakov |
| 5 | `odpoved_d` | nie | 4. možnosť odpovede | 0 – 80 znakov; ak je vyplnená, musí byť vyplnená aj `odpoved_c` |
| 6 | `spravna` | áno | písmeno správnej odpovede | `A`, `B`, `C` alebo `D` (aj malé); musí ukazovať na vyplnenú odpoveď |
| 7 | `cas` | áno | časový limit na odpoveď v sekundách | celé číslo z povolených hodnôt: `5`, `10`, `20`, `30`, `60`, `90`, `120` |

Ďalšie pravidlá pre riadok (vychádzajú z FR-002 a FR-010):

- otázka má **2 až 4** možnosti odpovede a **práve jednu** správnu odpoveď,
- dve možnosti v tej istej otázke nesmú mať rovnaký text (bez ohľadu na veľkosť písmen),
- otvorené (textové) otázky a viac správnych odpovedí sa nepodporujú (FR-010),
- obrázok k otázke (FR-008, UC-006) sa cez import nepridáva – pridáva sa v editore.

Povolené časové limity a maximálne dĺžky textov sú uložené v konfigurácii pravidiel
hry (NFR-B-02), hodnoty vyššie sú predvolené.

### 1.3 Príklad (CSV)

```csv
otazka;odpoved_a;odpoved_b;odpoved_c;odpoved_d;spravna;cas
Koľko bitov má jeden bajt?;4;8;16;32;B;20
Hlavné mesto Slovenska je…;Košice;Bratislava;Žilina;;B;10
Python je interpretovaný jazyk.;Pravda;Nepravda;;;A;10
Ktorý protokol zabezpečuje šifrované webové spojenie?;HTTP;FTP;HTTPS;SMTP;C;30
Čo vypíše print(2 ** 3)?;6;8;9;23;B;20
```

Rovnaký obsah v Exceli: [`vzory/kviz-vzor.xlsx`](vzory/kviz-vzor.xlsx)
(CSV: [`vzory/kviz-vzor.csv`](vzory/kviz-vzor.csv)).

### 1.4 Kontrola pri importe (UC-007)

**Chyba celého súboru** – import sa zastaví a kvíz sa nezmení (UC-007, alternatíva 3a):

- nepodporovaná prípona (iná než `.csv` / `.xlsx`) alebo poškodený súbor,
- súbor je väčší ako 1 MB alebo nemá žiadny riadok s otázkou,
- chýba hlavička alebo nezodpovedá stĺpcom z kapitoly 1.2,
- súbor obsahuje viac ako 100 otázok.

Hláška obsahuje popis očakávanej štruktúry (zoznam stĺpcov) a odkaz na vzorový súbor.

**Chyba v riadku** – systém zobrazí zoznam chybných riadkov a ponúkne import
iba platných otázok (UC-007, alternatíva 3b). Pri každej chybe uvedie
číslo riadka v súbore (hlavička = riadok 1) a dôvod, napr.:

| Riadok | Chyba |
|---|---|
| 4 | Chýba text otázky. |
| 7 | Otázka má iba jednu možnosť odpovede (potrebné sú aspoň 2). |
| 9 | Správna odpoveď `D` nie je vyplnená. |
| 12 | Časový limit `15` nie je povolený (povolené: 5, 10, 20, 30, 60, 90, 120). |

### 1.5 Bezpečnosť

- Všetky texty sa ukladajú ako obyčajný text; pri zobrazení sa HTML znaky escapujú
  (NFR-S-03), takže `<script>` v otázke sa zobrazí doslova.
- Z Excelu sa čítajú iba hodnoty buniek, vzorce sa nevyhodnocujú.

---

## 2. Súbor s výsledkami (export)

Hostiteľ si po skončení hry stiahne poradie hráčov (UC-026). Export je dostupný,
kým systém neodstráni údaje o hre (najneskôr 24 hodín po skončení – NFR-S-08);
potom systém zobrazí informáciu podľa UC-026, alternatíva 1a.

### 2.1 Názov súboru

```
bleskovka-vysledky_<nazov-kvizu>_<RRRR-MM-DD>_<HHMM>.csv   (resp. .xlsx)
```

- `<nazov-kvizu>` – názov kvízu bez diakritiky, malými písmenami, medzery a
  nepovolené znaky nahradené `-`, najviac 40 znakov,
- dátum a čas = koniec hry (čas servera, Europe/Bratislava).

Príklad: `bleskovka-vysledky_informatika-opakovanie_2026-11-05_1045.csv`

### 2.2 Stĺpce (tabuľka poradia)

| # | Stĺpec | Typ | Obsah |
|---|---|---|---|
| 1 | `poradie` | celé číslo | konečné poradie (1 = víťaz) |
| 2 | `prezyvka` | text | prezývka hráča (1 – 16 znakov, FR-025) |
| 3 | `skore` | celé číslo | celkový počet bodov (FR-041) |
| 4 | `spravne_odpovede` | celé číslo | počet správnych odpovedí |
| 5 | `pocet_otazok` | celé číslo | počet otázok v hre |
| 6 | `sucet_casov_s` | desatinné číslo (1 des. miesto) | súčet časov odpovedí v sekundách; použije sa pri rovnosti bodov (FR-045) |

Pravidlá:

- riadky sú zoradené podľa `skore` zostupne, pri rovnosti podľa `sucet_casov_s`
  vzostupne (FR-045); ak je rovnaký aj čas, hráči majú **rovnaké poradie**,
- do `sucet_casov_s` sa započíta čas každej odoslanej odpovede (správnej aj nesprávnej);
  za otázku bez odpovede sa započíta celý časový limit otázky,
- súbor obsahuje všetkých hráčov hry vrátane tých, ktorí sa počas hry odpojili,
  so skóre, ktoré mali v čase skončenia hry; hráči odstránení z čakárne (UC-015) v ňom nie sú,
- súbor obsahuje iba prezývky, žiadne iné osobné údaje (NFR-S-04).

Body za otázku (FR-041): `round(1000 − 500 × čas_odpovede / časový_limit)` pri správnej
odpovedi, inak 0. Príklad: správna odpoveď za 5 s pri limite 20 s = 875 bodov.

### 2.3 CSV

- kódovanie **UTF-8 s BOM** (aby Excel správne zobrazil diakritiku),
- oddeľovač `;`, desatinná čiarka (`20,8`), prvý riadok je hlavička,
- obsahuje iba tabuľku poradia z kapitoly 2.2.

```csv
poradie;prezyvka;skore;spravne_odpovede;pocet_otazok;sucet_casov_s
1;Jana;4382;5;5;20,8
2;Marek;3725;4;5;13,1
3;kubo7;3135;4;5;33,6
4;Ema;2525;3;5;44,4
5;Tomi;560;1;5;62,1
```

Vzor: [`vzory/vysledky-vzor.csv`](vzory/vysledky-vzor.csv)

### 2.4 Excel (`.xlsx`)

Súbor má dva hárky:

1. **`Poradie`** – rovnaké stĺpce ako CSV (kapitola 2.2), hlavička tučným písmom
   a ukotvená, čísla uložené ako čísla (nie text).
2. **`Hra`** – súhrnné údaje vo dvojiciach *názov – hodnota*:

| Položka | Príklad |
|---|---|
| Kvíz | Informatika – opakovanie |
| Začiatok hry | 05.11.2026 10:31 |
| Koniec hry | 05.11.2026 10:45 |
| Počet otázok | 5 |
| Počet hráčov | 5 |

### 2.5 Bezpečnosť

- Prezývka alebo názov kvízu začínajúce znakom `=`, `+`, `-` alebo `@` sa pri
  exporte doplnia na začiatku o apostrof `'`, aby ich Excel nespustil ako vzorec
  (ochrana pred „CSV injection“, NFR-S-03).
- Export môže stiahnuť iba hostiteľ, ktorý hru vytvoril (NFR-S-01).
