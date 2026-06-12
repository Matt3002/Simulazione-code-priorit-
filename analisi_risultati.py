"""
Analisi statistica dei risultati della simulazione OMNeT++
Progetto 10 - Simulazione di Sistemi
Matteo Pio Trotta - matteopio.trotta@studio.unibo.it

Legge i file .sca dalla cartella results/ e calcola:
- Media campionaria per ogni metrica
- Intervallo di confidenza al 95% (t di Student, 19 gradi di liberta')
"""

import os
import re
import math

RESULTS_DIR = "results"
T_095_19 = 2.093  # t di Student, alpha=0.05, nu=19

METRICS = {
    "coda1Delay:mean": "delay1",
    "coda2Delay:mean": "delay2",
    "coda1Len:mean":   "len1",
    "coda2Len:mean":   "len2",
    "coda1Thru:mean":  "thru1",
    "coda2Thru:mean":  "thru2",
}

def parse_results(results_dir):
    configs = {}
    for fname in os.listdir(results_dir):
        if not fname.endswith(".sca"):
            continue
        m = re.match(
            r"General-p_val=([\d.]+),q_val=([\d.]+),sigma_val=([\d.]+)-#(\d+)\.sca",
            fname
        )
        if not m:
            continue
        p, q, sigma = m.group(1), m.group(2), m.group(3)
        key = (float(p), float(q), float(sigma))
        if key not in configs:
            configs[key] = {v: [] for v in METRICS.values()}

        with open(os.path.join(results_dir, fname)) as f:
            for line in f:
                for pattern, varname in METRICS.items():
                    if pattern in line:
                        parts = line.strip().split()
                        try:
                            configs[key][varname].append(float(parts[-1]))
                        except (ValueError, IndexError):
                            pass
    return configs

def confidence_interval(values):
    n = len(values)
    if n == 0:
        return None, None
    mean = sum(values) / n
    if n == 1:
        return mean, 0.0
    std = math.sqrt(sum((x - mean) ** 2 for x in values) / (n - 1))
    ic = T_095_19 * std / math.sqrt(n)
    return round(mean, 4), round(ic, 4)

def print_table_delay(configs):
    print("\n=== TEMPO MEDIO DI PERMANENZA [slot] (IC 95%) ===\n")
    print(f"{'p':>5} {'q':>4} {'sigma':>6} | {'E[W1] +/- IC':>20} | {'E[W2] +/- IC':>25} | Stato")
    print("-" * 80)
    for key in sorted(configs.keys()):
        p, q, sigma = key
        lam1 = (1 - p) / p
        lamT = lam1 + q
        stable = "Stabile" if lamT < sigma else "INSTABILE (Coda 2)"
        d = configs[key]
        w1, ic1 = confidence_interval(d["delay1"])
        w2, ic2 = confidence_interval(d["delay2"])
        w2_str = f"{w2:.4f} +/- {ic2:.4f}" if w2 and w2 < 1000 else "inf (instabile)"
        print(f"{p:>5} {q:>4} {sigma:>6} | {w1:>8.4f} +/- {ic1:<8.4f} | {w2_str:>25} | {stable}")

def print_table_length(configs):
    print("\n=== LUNGHEZZA MEDIA DELLE CODE (IC 95%) ===\n")
    print(f"{'p':>5} {'q':>4} {'sigma':>6} | {'L1 +/- IC':>18} | {'L2 +/- IC':>22} | Stato")
    print("-" * 75)
    for key in sorted(configs.keys()):
        p, q, sigma = key
        lam1 = (1 - p) / p
        lamT = lam1 + q
        stable = "Stabile" if lamT < sigma else "INSTABILE"
        d = configs[key]
        l1, ic1 = confidence_interval(d["len1"])
        l2, ic2 = confidence_interval(d["len2"])
        l2_str = f"{l2:.4f} +/- {ic2:.4f}" if l2 and l2 < 1000 else "inf (instabile)"
        print(f"{p:>5} {q:>4} {sigma:>6} | {l1:>7.4f} +/- {ic1:<7.4f} | {l2_str:>22} | {stable}")

def print_table_throughput(configs):
    print("\n=== THROUGHPUT (IC 95%) ===\n")
    print(f"{'p':>5} {'q':>4} {'sigma':>6} | {'lam1':>6} {'lam2':>6} {'lamT':>6} {'sigma':>6} | {'Th1':>6} {'Th2':>6} | Stato")
    print("-" * 80)
    for key in sorted(configs.keys()):
        p, q, sigma = key
        lam1 = round((1 - p) / p, 4)
        lam2 = q
        lamT = round(lam1 + lam2, 4)
        stable = "Stabile" if lamT < sigma else "INSTABILE"
        d = configs[key]
        th1, _ = confidence_interval(d["thru1"])
        th2, _ = confidence_interval(d["thru2"])
        print(f"{p:>5} {q:>4} {sigma:>6} | {lam1:>6.4f} {lam2:>6.4f} {lamT:>6.4f} {sigma:>6} | {th1:>6.4f} {th2:>6.4f} | {stable}")

def print_validation(configs):
    print("\n=== VALIDAZIONE TEORICA E[W1] = 1 / (sigma - lambda1) ===\n")
    print(f"{'p':>5} {'q':>4} {'sigma':>6} | {'E[W1]_teo':>10} {'E[W1]_sim':>10} {'Errore%':>8}")
    print("-" * 55)
    for key in sorted(configs.keys()):
        p, q, sigma = key
        lam1 = (1 - p) / p
        lamT = lam1 + q
        if sigma <= lam1:
            continue
        W1_teo = 1 / (sigma - lam1)
        w1_sim, _ = confidence_interval(configs[key]["delay1"])
        err = abs(w1_sim - W1_teo) / W1_teo * 100
        print(f"{p:>5} {q:>4} {sigma:>6} | {W1_teo:>10.4f} {w1_sim:>10.4f} {err:>7.2f}%")

if __name__ == "__main__":
    print("Lettura risultati da:", RESULTS_DIR)
    configs = parse_results(RESULTS_DIR)
    print(f"Configurazioni trovate: {len(configs)}")

    print_validation(configs)
    print_table_throughput(configs)
    print_table_delay(configs)
    print_table_length(configs)
