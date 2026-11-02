# Uso: vivado -mode batch -source export_timesim.tcl -tclargs <nome_run>
set name [lindex $argv 0]
set out  "C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao/vivado/runs/$name"
open_checkpoint $out/routed.dcp
write_sdf -mode timesim -force $out/aes_timesim.sdf
write_verilog -mode timesim -sdf_anno true -sdf_file $out/aes_timesim.sdf -force $out/aes_timesim.v
report_power -file $out/power_vectorless2.rpt
puts "EXPORT_DONE $name"
