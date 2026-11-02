# Uso: vivado -mode batch -source power_windows.tcl -tclargs <run> <n_enc> <n_win> <saifdir> <saida.csv>
lassign $argv run nenc nwin saifdir outcsv
set root C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao/vivado
open_checkpoint $root/runs/$run/routed.dcp
create_clock -period 10.0 -name clk [get_ports clk]
set fo [open $outcsv w]
puts $fo "enc,win,vccint_dyn_A,vccint_total_A,vccbram_dyn_A"
set tmp $root/sim/_tmp_power.xml
set t0 [clock milliseconds]
for {set i 0} {$i < $nenc} {incr i} {
  for {set k 0} {$k < $nwin} {incr k} {
    reset_switching_activity -all
    read_saif -quiet -strip_path tb_timing/dut $saifdir/e${i}_w${k}.saif
    report_power -quiet -format xml -file $tmp
    set fh [open $tmp r]; set x [read $fh]; close $fh
    set ok [regexp {contents="Vccint".*?contents="[0-9.]+".*?contents="([0-9.]+)".*?contents="([0-9.]+)"} $x -> tot dyn]
    regexp {contents="Vccbram".*?contents="[0-9.]+".*?contents="[0-9.]+".*?contents="([0-9.]+)"} $x -> bdyn
    puts $fo "$i,$k,$dyn,$tot,$bdyn"
  }
}
close $fo
puts "WINDOWS_POWER_DONE [expr {([clock milliseconds]-$t0)/1000.0}] s"
