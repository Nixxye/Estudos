#!/bin/bash
# Rodada noturna: para cada variante/compilação -> implementar -> simular com atrasos -> potência por janela.
# Uso:  bash overnight/run_overnight.sh [N_cifragens] [janelas] [arquivo_variantes]
# Padrão: N=5000, janelas "1,11", variantes em overnight/variants.conf
# Retomável: etapas já concluídas são puladas se os arquivos de saída existirem.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"                       # .../simulacao/vivado
BASEL="$(cd "$ROOT/../baseline" && pwd)"
N="${1:-5000}"
WINS="${2:-1,11}"
CONF="${3:-$HERE/variants.conf}"; CONF="$(cd "$(dirname "$CONF")" && pwd)/$(basename "$CONF")"
VB="C:/AMDDesignTools/2025.2/Vivado/bin"
TS="$(date +%Y%m%d_%H%M%S)"
LOGDIR="$ROOT/overnight/logs_$TS"; mkdir -p "$LOGDIR"
STATUS="$LOGDIR/status.txt"
log(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOGDIR/run.log"; }
W(){ cygpath -m "$1"; }                               # caminho estilo Windows com /
vivado_batch(){ local tcl="$1"; shift; cmd //c "$(cygpath -w $VB/vivado.bat) -mode batch -nojournal -nolog -source $(cygpath -w "$tcl") -tclargs $*"; }

log "INICIO  N=$N janelas=$WINS conf=$CONF"
# plaintexts comuns a todas as variantes (mesma semente), primeiro = vetor FIPS-197
python - "$N" "$ROOT/overnight/pts_$N.hex" <<'PY'
import sys, numpy as np
n=int(sys.argv[1]); rng=np.random.default_rng(2026)
pts=[bytes.fromhex('00112233445566778899aabbccddeeff')]+[bytes(rng.integers(0,256,16,dtype=np.uint8)) for _ in range(n-1)]
open(sys.argv[2],'w').write('\n'.join(p.hex() for p in pts)+'\n')
PY

while IFS='|' read -r name synth pdir rdir phdir; do
  name="$(echo $name)"; [[ -z "$name" || "$name" == \#* ]] && continue
  synth="$(echo $synth)"; pdir="$(echo $pdir)"; rdir="$(echo $rdir)"; phdir="$(echo $phdir)"
  RUN="$ROOT/runs/$name"; SIM="$ROOT/sim_${name}_$N"
  VLOG="$LOGDIR/$name.log"
  log "=== $name  (synth=$synth place=$pdir route=$rdir physopt=$phdir)"

  # 1) implementação + netlist temporizado + SDF
  if [[ -s "$RUN/aes_timesim.v" && -s "$RUN/aes_timesim.sdf" ]]; then log "  impl: já existe, pulando"
  else
    log "  impl..."; vivado_batch "$ROOT/impl_variant.tcl" $name $synth $pdir $rdir $phdir > "$LOGDIR/${name}_impl.log" 2>&1
    if [[ ! -s "$RUN/aes_timesim.v" ]]; then log "  FALHA impl ($name)"; echo "$name FALHA_IMPL" >> "$STATUS"; continue; fi
  fi
  # 2) simulação temporizada + SAIF nas janelas escolhidas
  mkdir -p "$SIM/saif"; cd "$SIM"
  cp "$ROOT/overnight/pts_$N.hex" pts.hex
  sed "s/parameter NENC = 20/parameter NENC = $N/" "$ROOT/tb_timing.v" > tb_timing.v
  if [[ -s power.csv && $(wc -l < power.csv) -gt $((N-1)) ]]; then log "  power.csv completo, pulando sim/potência"
  else
    log "  xsim..."
    cmd //c "$(cygpath -w $VB/xvlog.bat) --incr --relax $(cygpath -w "$RUN/aes_timesim.v") tb_timing.v C:\AMDDesignTools\2025.2\Vivado\data\verilog\src\glbl.v" > xvlog.log 2>&1
    cmd //c "$(cygpath -w $VB/xelab.bat) -debug typical -L simprims_ver -L unisims_ver tb_timing glbl -s tbsim" > xelab.log 2>&1
    cat > run_windows.tcl <<TCL
set objs [get_objects -r /tb_timing/dut/*]
set wins [split "$WINS" ,]
run 205 ns
for {set i 0} {\$i < [expr {$N-1}]} {incr i} {
  for {set k 0} {\$k < 12} {incr k} {
    if {[lsearch -exact \$wins \$k] >= 0} {
      open_saif saif/e\${i}_w\${k}.saif
      log_saif \$objs
      run 10 ns
      close_saif
    } else {
      run 10 ns
    }
  }
}
puts "WINDOWS_DONE"
quit
TCL
    cmd //c "$(cygpath -w $VB/xsim.bat) tbsim -tclbatch run_windows.tcl" > xsim.log 2>&1
    if ! grep -q WINDOWS_DONE xsim.log; then log "  FALHA xsim ($name)"; echo "$name FALHA_XSIM" >> "$STATUS"; cd "$ROOT"; continue; fi
    # estados registrados no testbench: conferência funcional
    python "$BASEL/check_states.py" "$SIM/states_timing.txt" "$SIM/pts.hex" > "$LOGDIR/${name}_states_check.txt" 2>&1
    log "  estados: $(tail -1 "$LOGDIR/${name}_states_check.txt")"
    # 3) potência por janela
    log "  potência por janela..."
    cd "$ROOT"
    vivado_batch "$ROOT/power_windows_sel.tcl" $name $((N-1)) "${WINS//,/_}" "$(W "$SIM/saif")" "$(W "$SIM/power.csv")" > "$LOGDIR/${name}_power.log" 2>&1
    if ! grep -q POWER_DONE "$LOGDIR/${name}_power.log"; then log "  FALHA potência ($name)"; echo "$name FALHA_POTENCIA" >> "$STATUS"; continue; fi
    rm -rf "$SIM/saif"
  fi
  echo "$name OK" >> "$STATUS"; log "  $name concluída"
  cd "$ROOT"
done < "$CONF"

log "análise..."
cd "$BASEL" && python analyze_overnight.py "$N" "$WINS" "$CONF" > "$LOGDIR/analise.log" 2>&1
log "relatório final..."
cd "$BASEL" && python build_report.py "$N" > "$LOGDIR/relatorio.log" 2>&1
log "FIM. Resumo em $ROOT/overnight/RESUMO.md ; logs em $LOGDIR"
