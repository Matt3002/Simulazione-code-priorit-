# Progetto 10 — Simulazione di Sistemi

Simulazione di un **sistema a code a tempo discreto con priorità assoluta e interruzioni casuali del server**, sviluppato in [OMNeT++](https://omnetpp.org/) 6.3.0.

Il modello è una variante dell'*Option A* (server singolo con priorità) descritta in:

> H. Bruneel, A. Devos, *"Coupled queues with server interruptions: Some solutions"*,
> Performance Evaluation, vol. 167 (2025), art. 102466.
> [https://doi.org/10.1016/j.peva.2024.102466](https://doi.org/10.1016/j.peva.2024.102466)

**Autore:** Matteo Pio Trotta — `matteopio.trotta@studio.unibo.it`

---

## Descrizione del modello

Il sistema è composto da un singolo server condiviso e da due code a capacità infinita:

- **Coda 1 (Tipo 1)** — arrivi con distribuzione **geometrica** di parametro `p`, tasso medio `λ₁ = (1−p)/p`
- **Coda 2 (Tipo 2)** — arrivi con distribuzione di **Poisson** di parametro `q`, tasso medio `λ₂ = q`

Regole principali:

- **Priorità assoluta** alla Coda 1: la Coda 2 è servita solo quando la Coda 1 è vuota
- Servizio deterministico di **1 time slot** per utente
- **Interruzioni Bernoulli**: il server è disponibile con probabilità `σ` in ogni slot
- Dinamica temporale **Late Arrival System** (servizio prima degli arrivi)

Il sistema è stabile se e solo se `λ₁ + λ₂ < σ`.

---

## Struttura del repository

```
.
├── ModuloCode.cc            # Logica di simulazione C++ (slot-per-slot)
├── SistemaPriorita.ned      # Topologia della rete e dichiarazione statistiche
├── omnetpp.ini              # Configurazione campagna (8 config × 20 run)
├── Makefile                 # Build OMNeT++
├── analisi_risultati.py     # Script di analisi statistica dei risultati
├── AnalisiRisultati.anf     # File di analisi grafica OMNeT++
└── docs/
    ├── relazione_estesa.tex      # Relazione tecnica (LaTeX)
    └── Presentazione_Progetto10.pptx  # Slide di presentazione
```

---

## Parametri della campagna

Vengono esplorate tutte le combinazioni dei seguenti parametri (8 configurazioni totali):

| Parametro | Valori |
|-----------|--------|
| `p` (geometrica) | 0.75, 0.85 |
| `q` (Poisson) | 0.2, 0.3 |
| `σ` (disponibilità server) | 0.6, 0.7 |

Ogni configurazione è eseguita per **20 repliche indipendenti** (`repeat = 20`), con:

- `sim-time-limit = 200000s` (durata totale)
- `warmup-period = 10000s` (rimozione del transiente iniziale)

---

## Metriche stimate

Per ciascuna classe `i ∈ {1, 2}`, con stima puntuale e intervallo di confidenza al 95%:

- **Tempo medio di permanenza** `E[Wᵢ]`
- **Throughput** `θᵢ`
- **Lunghezza media della coda** `E[Lᵢ]`

Gli intervalli di confidenza sono calcolati con la distribuzione *t* di Student (ν = 19 gradi di libertà).

---

## Come compilare ed eseguire

### Prerequisiti

- OMNeT++ 6.3.0 (con il terminale MinGW su Windows)
- Python 3 (per l'analisi dei risultati)

### Compilazione

```bash
make
```

### Esecuzione della campagna (modalità batch)

```bash
./Progetto10.exe -m -u Cmdenv -c General omnetpp.ini
```

Al termine vengono prodotti 160 file di risultati (`.sca`, `.vec`, `.vci`) nella cartella `results/`.

### Analisi dei risultati

```bash
python3 analisi_risultati.py
```

Lo script legge i file `.sca`, raggruppa le repliche per configurazione e stampa le tabelle con medie e intervalli di confidenza per tutte le metriche.

---

## Risultati principali

- **Validazione teorica**: il tempo medio di permanenza della Coda 1 coincide con la formula analitica `E[W₁] = 1/(σ − λ₁)`, con errore massimo < 0.25%
- **Legge di Little** verificata su entrambe le code (scarto ≤ 0.16%)
- **Isolamento della classe prioritaria**: la Coda 1 è indipendente dal traffico di Tipo 2
- **Caso instabile** (`p=0.75, q=0.3, σ=0.6`): la Coda 2 diverge mentre il suo throughput satura alla capacità residua `σ − λ₁`

Per l'analisi completa si veda la relazione in `docs/`.

---

## Note

I file generati dalla simulazione (`results/`, `out/`, eseguibili) sono esclusi dal versionamento tramite `.gitignore` e vengono prodotti localmente alla compilazione ed esecuzione.
