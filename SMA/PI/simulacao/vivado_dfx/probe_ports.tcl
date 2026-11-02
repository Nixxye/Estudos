open_checkpoint C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao/vivado_dfx/out/static_locked.dcp
puts "=== black box rm_inst pins ==="
foreach p [get_pins -of [get_cells rm_inst] -filter {IS_LEAF}] { puts "  $p" }
close_design
open_checkpoint C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao/vivado_dfx/out/rm_variant_b_synth.dcp
puts "=== rm_variant_b top ports ==="
foreach p [get_ports] { puts "  $p  dir=[get_property DIRECTION $p]  bits=[get_property NUM_BITS $p]" }
