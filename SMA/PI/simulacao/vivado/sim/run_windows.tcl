# Janelas de 10 ns alinhadas as bordas de clock; 12 janelas por cifragem (reset, carga, 10 rodadas).
set objs [get_objects -r /tb_timing/dut/*]
run 205 ns
for {set i 0} {$i < 19} {incr i} {
  for {set k 0} {$k < 12} {incr k} {
    open_saif saif/e${i}_w${k}.saif
    log_saif $objs
    run 10 ns
    close_saif
  }
}
puts "WINDOWS_DONE"
quit
