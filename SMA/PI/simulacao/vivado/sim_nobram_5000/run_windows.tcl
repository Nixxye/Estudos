set objs [get_objects -r /tb_timing/dut/*]
set wins [split "1,11" ,]
run 205 ns
for {set i 0} {$i < [expr {5000-1}]} {incr i} {
  for {set k 0} {$k < 12} {incr k} {
    if {[lsearch -exact $wins $k] >= 0} {
      open_saif saif/e${i}_w${k}.saif
      log_saif $objs
      run 10 ns
      close_saif
    } else {
      run 10 ns
    }
  }
}
puts "WINDOWS_DONE"
quit
