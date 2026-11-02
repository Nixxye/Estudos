open_checkpoint C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao/vivado/runs/base/routed.dcp
create_clock -period 10.0 -name clk [get_ports clk]
foreach w {w1 w2} {
  set t0 [clock milliseconds]
  read_saif -strip_path tb_timing/dut C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao/vivado/sim/$w.saif
  set t1 [clock milliseconds]
  set rpt [report_power -return_string]
  set t2 [clock milliseconds]
  regexp {Dynamic \(W\)\s*\|\s*([0-9.]+)} $rpt -> dyn
  regexp {Total On-Chip Power \(W\)\s*\|\s*([0-9.]+)} $rpt -> tot
  regexp {Design Nets Matched\s*\|\s*([0-9.]+%[^|]*)\|} $rpt -> matched
  puts "POWER $w dyn=$dyn total=$tot read_saif_ms=[expr $t1-$t0] report_power_ms=[expr $t2-$t1]"
  if {[info exists matched]} { puts "MATCHED $w $matched" }
}
