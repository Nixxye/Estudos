# Uso: vivado -mode batch -source impl_variant.tcl -tclargs <nome> <sintese> <place> <route> <physopt>
lassign $argv name synth pdir rdir phdir
set root C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao
set out  $root/vivado/runs/$name
file mkdir $out
read_vhdl -vhdl2008 $root/vhdl/aes_sbox_pkg.vhd
read_vhdl -vhdl2008 $root/vhdl/aes_pkg.vhd
read_vhdl -vhdl2008 $root/vhdl/aes_iter.vhd
if {$synth eq "nobram"} {
  synth_design -top aes_iter -part xc7z020clg400-1 -mode out_of_context -max_bram 0
} else {
  synth_design -top aes_iter -part xc7z020clg400-1 -mode out_of_context
}
create_clock -period 10.0 -name clk [get_ports clk]
opt_design
place_design -directive $pdir
if {$phdir ne "none"} { phys_opt_design -directive $phdir }
route_design -directive $rdir
report_utilization -file $out/utilization.rpt
report_timing_summary -file $out/timing.rpt
report_power -file $out/power_vectorless.rpt
write_checkpoint -force $out/routed.dcp
write_sdf -mode timesim -force $out/aes_timesim.sdf
write_verilog -mode timesim -sdf_anno true -sdf_file $out/aes_timesim.sdf -force $out/aes_timesim.v
puts "IMPL_DONE $name"
