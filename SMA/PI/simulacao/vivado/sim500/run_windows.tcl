set objs [get_objects -r /tb_timing/dut/*]
run 205 ns
for {set i 0} {$i < [expr {500-1}]} {incr i} {
  for {set k 0} {$k < 12} {incr k} {
    open_saif saif/e${i}_w${k}.saif
    log_saif $objs
    run 10 ns
    close_saif
  }
}
puts "WINDOWS_DONE"
quit
