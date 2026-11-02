puts "VERSION: [version -short]"
puts "PARTS_XC7Z020: [llength [get_parts xc7z020*]]"
puts "PART_SAMPLE: [lindex [get_parts xc7z020*] 0]"
foreach c {write_sdf log_saif open_saif close_saif read_saif report_power write_verilog open_vcd log_vcd close_vcd place_design route_design phys_opt_design} {
  puts "=== help $c ==="
  if {[catch {puts [help $c]} err]} { puts "ERRO: $err" }
}
