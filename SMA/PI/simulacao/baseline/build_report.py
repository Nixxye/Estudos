"""
Gera PI/RELATORIO_FINAL.md reunindo: ambiente, testes, baseline sintético, alvo VHDL, alvo Vivado
(simulação temporizada + potência estimada) e a rodada noturna. Tolera arquivos ausentes.

Uso:  python build_report.py [N_rodada_noturna]
"""
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PI = os.path.normpath(os.path.join(HERE, "..", ".."))
VIV = os.path.normpath(os.path.join(HERE, "..", "vivado"))
RES = os.path.join(HERE, "results")
VIVADO = r"C:\AMDDesignTools\2025.2\Vivado\bin\vivado.bat"


def sh(cmd, timeout=300):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, errors="replace")
        return (r.stdout + r.stderr).strip()
    except Exception as e:  # noqa: BLE001
        return f"(falhou: {e})"


def T(x):
    return "acima da grade" if x is None else str(x)


def jload(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return None


def ghdl_path():
    for c in [os.environ.get("GHDL"), shutil.which("ghdl")] + glob.glob(
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\ghdl*\bin\ghdl.exe")):
        if c and os.path.exists(c):
            return c
    return None


def parse_rpt(run):
    d = os.path.join(VIV, "runs", run)
    out = {}

    def rd(name):
        p = os.path.join(d, name)
        return open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else ""
    u, t, p = rd("utilization.rpt"), rd("timing.rpt"), rd("power_vectorless.rpt")
    m = re.search(r"\| Slice LUTs\s*\|\s*(\d+)", u)
    out["LUTs"] = int(m.group(1)) if m else None
    m = re.search(r"\| Slice Registers\s*\|\s*(\d+)", u)
    out["FFs"] = int(m.group(1)) if m else None
    m = re.search(r"\| Block RAM Tile\s*\|\s*([\d.]+)", u)
    out["BRAM"] = float(m.group(1)) if m else None
    m = re.search(r"WNS\(ns\).*?\n\s*-+.*?\n\s*(-?[\d.]+)", t, re.S)
    out["WNS_ns"] = float(m.group(1)) if m else None
    m = re.search(r"Total On-Chip Power \(W\)\s*\|\s*([\d.]+)", p)
    out["P_total_W"] = float(m.group(1)) if m else None
    m = re.search(r"\| Dynamic \(W\)\s*\|\s*([\d.]+)", p)
    out["P_dyn_W"] = float(m.group(1)) if m else None
    return out


def vivado_499_table():
    """Ataque sobre os traços do lote de 499 cifragens (todas as 12 janelas), se existirem."""
    d = os.path.join(VIV, "sim500")
    if not (os.path.exists(os.path.join(d, "power_windows.csv")) and os.path.exists(os.path.join(d, "pts.hex"))):
        return None
    sys.path.insert(0, HERE)
    import csv
    from aes_target import encrypt_states, hex_to_bytes
    import analyze_overnight as ao
    pts = np.array([hex_to_bytes(l.strip()) for l in open(os.path.join(d, "pts.hex")) if l.strip()])
    n = 499
    pts = pts[:n]
    ct = encrypt_states(pts, ao.KEY)[:, 10]
    hyp = ao.hypotheses(pts, ct)
    P = {}
    with open(os.path.join(d, "power_windows.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            P.setdefault(int(r["win"]), np.full(n, np.nan))[int(r["enc"])] = float(r["vccint_dyn_A"])
    rows = []
    for hname, (win, true, fn) in hyp.items():
        y = P[win]
        ok = ~np.isnan(y)
        idx = np.where(ok)[0]
        Hs = [fn(p) for p in range(16)]
        rho = np.array([ao.corr_cols(Hs[p][idx], y[idx])[true[p]] for p in range(16)])
        by_n = []
        for g in (100, 200, 300, len(idx)):
            sub = idx[:g]
            guess = ao.attack(Hs, y, sub)
            by_n.append(int((guess == true).sum()))
        rows.append((hname, win, float(rho.mean()), by_n))
    return rows


def main():
    n_over = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    L = []
    A = L.append
    A("# Relatório final: simulação de ataque por energia e contramedidas em FPGA (projeto SMA)")
    A("")
    A(f"Gerado automaticamente em {now}. Todos os números vêm de simulação; **nenhuma medição física foi feita**.")
    A("")

    # ---------- ambiente ----------
    A("## 1. Ambiente")
    A("")
    A("| Item | Versão |")
    A("|---|---|")
    A(f"| Python | {sys.version.split()[0]} (NumPy {np.__version__}) |")
    g = ghdl_path()
    A(f"| GHDL | {sh(f'\"{g}\" --version').splitlines()[0] if g else 'não encontrado'} |")
    try:
        vv = subprocess.run(["cmd", "/c", VIVADO, "-version"], capture_output=True, text=True, timeout=120,
                            errors="replace").stdout.splitlines()
    except Exception:  # noqa: BLE001
        vv = []
    A(f"| Vivado | {next((x for x in vv if 'vivado' in x.lower()), 'não encontrado').strip()} |")
    A("| Dispositivo alvo | XC7Z020 (Zynq-7000), clock de teste de 10 ns |")
    A("")

    # ---------- testes ----------
    A("## 2. Testes automáticos")
    A("")
    out = sh(f'cd /d "{HERE}" && python -m unittest discover -s tests', timeout=900)
    tail = [x for x in out.splitlines() if x.strip()][-3:]
    A("```")
    A("\n".join(tail))
    A("```")
    A("")
    A("Cobertura: AES contra o FIPS-197 e inversão do escalonamento de chave; controles negativos (traços "
      "embaralhados, ruído enorme, outra chave, ciclo errado, TVLA nulo); funções de análise sobre vazamento "
      "sintético; leitura do CSV do Vivado; e **estados do VHDL no GHDL iguais aos do modelo Python** "
      "(200 cifragens, todos os ciclos).")
    A("")

    # ---------- baseline ----------
    A("## 3. Baseline sintético (alvo A em Python e alvo B em VHDL)")
    A("")
    r = jload(os.path.join(RES, "experiments_python_full.json"))
    v = jload(os.path.join(RES, "experiments_vhdl.json"))
    if r:
        A(f"Alvo: AES-128 iterativo, uma rodada por ciclo, sem proteção. Modelo: distância de Hamming do registrador de "
          f"estado de 128 bits + ruído gaussiano (σ base = {r['sigma_base']}). TTD90 = menor N da grade com ≥ 90% de "
          f"sucesso da chave inteira ({r['reps']} repetições; grade {r['ns']}).")
        A("")
        A("| Experimento | TTD90 |")
        A("|---|---|")
        A(f"| E1 base (última rodada, σ={r['sigma_base']}) | {T(r['E1_base']['ttd90'])} |")
        for k, d in r["E2_sigma"].items():
            A(f"| E2 σ={k} | {T(d['ttd90'])} |")
        A(f"| E3 modelo errado (HW no lugar de HD) | {T(r['E3_wrong_model']['ttd90'])} |")
        A(f"| E4 carga inicial (K0) | {T(r['E4_first_round']['ttd90'])} |")
        for k, d in r["E5_quant"].items():
            A(f"| E5 quantização {k} bits | {T(d['ttd90'])} |")
        A(f"| E6 TVLA, máx \\|t\\| (limite 4,5) | {r['E6_tvla']['max_abs_t']:.1f} |")
        if v:
            A(f"| Alvo B (VHDL/GHDL), σ={v['sigma']} | {T(v['ttd90'])} |")
        A("")
        A("Ressalva: com poucas repetições a taxa em N intermediário varia ±0,1 (uma checagem com 300 repetições deu ≈ 0,66 "
          "em N=1.600, contra 0,85 com 40). O σ é escolhido por nós.")
    else:
        A("(resultados do baseline não encontrados)")
    A("")

    # ---------- Vivado ----------
    A("## 4. Alvo no Vivado: implementação, simulação temporizada e potência estimada")
    A("")
    A("Fluxo: VHDL → síntese e implementação (XC7Z020) → netlist Verilog com atrasos (SDF) → simulação temporizada no xsim "
      "→ um SAIF por janela de 10 ns alinhada às bordas de clock → `read_saif` + `report_power` (XML, corrente Vccint com "
      "resolução de µA). Janelas por cifragem: 0 = limpeza, 1 = carga (ciclo 0), 2 a 11 = rodadas 1 a 10.")
    A("")
    A("**Custo por compilação (relatórios do Vivado):**")
    A("")
    A("| compilação | LUTs | FFs | BRAM (tiles) | WNS (ns) @10 ns | potência total (W) | dinâmica (W) |")
    A("|---|---|---|---|---|---|---|")
    for rd in sorted(glob.glob(os.path.join(VIV, "runs", "*", "utilization.rpt"))):
        name = os.path.basename(os.path.dirname(rd))
        c = parse_rpt(name)
        A(f"| {name} | {c['LUTs']} | {c['FFs']} | {c['BRAM']} | {c['WNS_ns']} | {c['P_total_W']} | {c['P_dyn_W']} |")
    A("")
    A("A potência dessa tabela é a estimativa sem atividade de simulação (vetorless), só serve como custo relativo.")
    A("")
    tab = vivado_499_table()
    if tab:
        A("**Primeiro lote (499 cifragens, compilação base): ataque CPA sobre a corrente dinâmica Vccint.**")
        A("")
        A("| hipótese | janela | ρ médio do palpite certo | bytes certos com N = 100 / 200 / 300 / 499 |")
        A("|---|---|---|---|")
        for hname, win, rho, by in tab:
            A(f"| {hname} | {win} | {rho:+.3f} | {' / '.join(str(x) for x in by)} |")
        A("")
        A("Hipóteses: `reg_*` = distância de Hamming do registrador; `sbox_*` = transição da saída combinacional da S-box "
          "(`sbox_load`: SB(0)=0x63 → SB(pt⊕k); `sbox_last`: SB(s9) → SB(ct)). **Achados:** (1) o vazamento do registrador "
          "na última rodada não aparece nesse modelo de potência; (2) a lógica combinacional da S-box vaza; (3) a corrente "
          "do trilho da BRAM (Vccbram) é constante, isto é, o modelo do Vivado não faz a BRAM depender dos dados.")
        A("")

    # ---------- rodada noturna ----------
    A(f"## 5. Rodada noturna (N = {n_over} cifragens por variante)")
    A("")
    resumo = os.path.join(VIV, "overnight", "RESUMO.md")
    logs = sorted(glob.glob(os.path.join(VIV, "overnight", "logs_*")))
    if logs:
        st = os.path.join(logs[-1], "status.txt")
        if os.path.exists(st):
            A("Estado das variantes: " + "; ".join(x.strip() for x in open(st, encoding="utf-8")))
            A("")
        chk = sorted(glob.glob(os.path.join(logs[-1], "*_states_check.txt")))
        for c in chk:
            A(f"- Conferência funcional ({os.path.basename(c).replace('_states_check.txt','')}): "
              f"{open(c, encoding='utf-8').read().strip().splitlines()[-1]}")
        A("")
    if os.path.exists(resumo):
        body = open(resumo, encoding="utf-8").read().split("\n", 1)[1]
        A(body.replace("\n## ", "\n### "))
        A("")
        A("![gráfico da rodada noturna](simulacao/vivado/overnight/overnight.png)")
    else:
        A("(a rodada noturna ainda não gerou `RESUMO.md`)")
    A("")

    # ---------- conclusões ----------
    A("## 6. O que se pode afirmar e o que não")
    A("")
    A("- **Funcional (verificado):** alvo AES em Python, em VHDL (GHDL) e no netlist temporizado do Vivado produzem os mesmos "
      "estados em todos os ciclos; ataque CPA recupera a chave nos três contextos quando há hipótese compatível com a fonte de "
      "vazamento.")
    A("- **O modelo simples do baseline (só o registrador) não representa a estimativa do Vivado.** No modelo da AMD, o "
      "vazamento relevante está na lógica combinacional da S-box. Contramedidas e variantes devem ser avaliadas com "
      "hipóteses sobre essa lógica.")
    A("- **Limites:** potência é estimativa do Vivado (SAIF da simulação temporizada), não medição; ruído de medição e rede de "
      "alimentação não são modelados; uma única família de FPGA e um único alvo; as hipóteses `sbox_*` foram formuladas "
      "depois de ver o primeiro lote; resultados de N pequeno variam entre repetições.")
    A("- **Não validado:** efeito da reconfiguração parcial real (modelada como troca de conjuntos de traços), desempenho em placa, "
      "ataques com alinhamento (DTW, janela deslizante) contra clock aleatório.")
    A("")
    A("Análise detalhada dos resultados da rodada noturna: [ANALISE_RESULTADOS.md](ANALISE_RESULTADOS.md).")
    A("")
    A("## 7. Como reproduzir")
    A("")
    A("```bash")
    A("cd PI/simulacao/baseline")
    A("python -m unittest discover -s tests -v          # testes")
    A("python run_experiments.py                         # baseline sintético")
    A("python vhdl_flow.py --n 20000 --sigma 10          # alvo VHDL no GHDL")
    A("cd ../vivado")
    A("bash overnight/run_overnight.sh 5000 1,11         # compilações, simulação temporizada, potência e análise")
    A("python ../baseline/build_report.py 5000           # este relatório")
    A("```")
    A("")
    A("Arquivos principais: `PI/simulacao/baseline/` (modelo, ataque, métricas, testes), `PI/simulacao/vhdl/` (alvo B), "
      "`PI/simulacao/vivado/` (scripts Tcl, testbench Verilog, rodada noturna), e os planos em `PI/*.md`.")
    path = os.path.join(PI, "RELATORIO_FINAL.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("escrito", path)


if __name__ == "__main__":
    main()
