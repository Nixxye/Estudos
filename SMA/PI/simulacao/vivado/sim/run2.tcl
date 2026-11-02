run 200 ns
open_saif w1.saif
log_saif [get_objects -r /tb_timing/dut/*]
run 50 ns
close_saif
open_saif w2.saif
log_saif [get_objects -r /tb_timing/dut/*]
run 50 ns
close_saif
puts "SAIF_TEST_DONE"
quit
