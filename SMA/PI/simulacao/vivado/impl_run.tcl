# Uso: vivado -mode batch -source impl_run.tcl -tclargs <nome_run> <place_dir> <route_dir> <physopt_dir|none>
set name   [lindex $argv 0]
set pdir   [lindex $argv 1]
set rdir   [lindex $argv 2]
set phdir  [lindex $argv 3]
set vhdl   "C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao/vhdl"
set out    "C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao/vivado/runs/$name"
file mkdir $out
read_vhdl -vhdl2008 $vhdl/aes_sbox_pkg.vhd
read_vhdl -vhdl2008 $vhdl/aes_pkg.vhd
read_vhdl -vhdl2008 $vhdl/aes_iter.vhd
synth_design -top aes_iter -part xc7z020clg400-1 -mode out_of_context
create_clock -period 10.0 -name clk [get_ports clk]
opt_design
place_design -directive $pdir
if {$phdir ne "none"} { phys_opt_design -directive $phdir }
route_design -directive $rdir
report_utilization -file $out/utilization.rpt
report_timing_summary -file $out/timing.rpt
report_power -file $out/power_vectorless.rpt
write_checkpoint -force $out/routed.dcp
puts "RUN_DONE $name"
