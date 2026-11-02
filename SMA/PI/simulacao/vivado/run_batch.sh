#!/bin/bash
# Uso: run_batch.sh <run> <nenc>   (executa a partir de PI/simulacao/vivado)
set -e
RUN=$1; N=$2
ROOT="C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao/vivado"
B="C:/AMDDesignTools/2025.2/Vivado/bin"
D="$ROOT/sim$N"
cd "$D"
sed "s/parameter NENC = 20/parameter NENC = $N/" ../tb_timing.v > tb_timing.v
cmd //c "$(cygpath -w $B/xvlog.bat) --incr --relax $(cygpath -w $ROOT/runs/$RUN/aes_timesim.v) tb_timing.v C:\AMDDesignTools\2025.2\Vivado\data\verilog\src\glbl.v" > xvlog.log 2>&1
cmd //c "$(cygpath -w $B/xelab.bat) -debug typical -L simprims_ver -L unisims_ver tb_timing glbl -s tbsim" > xelab.log 2>&1
cat > run_windows.tcl <<TCL
set objs [get_objects -r /tb_timing/dut/*]
run 205 ns
for {set i 0} {\$i < [expr {$N-1}]} {incr i} {
  for {set k 0} {\$k < 12} {incr k} {
    open_saif saif/e\${i}_w\${k}.saif
    log_saif \$objs
    run 10 ns
    close_saif
  }
}
puts "WINDOWS_DONE"
quit
TCL
cmd //c "$(cygpath -w $B/xsim.bat) tbsim -tclbatch run_windows.tcl" > xsim.log 2>&1
cd "$ROOT"
cmd //c "$(cygpath -w $B/vivado.bat) -mode batch -nojournal -nolog -source power_windows.tcl -tclargs $RUN $((N-1)) 12 $D/saif $D/power_windows.csv" > "$D/power_windows.log" 2>&1
echo BATCH_DONE
