open_checkpoint C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao/vivado/runs/base/routed.dcp
create_clock -period 10.0 -name clk [get_ports clk]
read_saif -strip_path tb_timing/dut C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao/vivado/sim/w1.saif
report_power -format xml -file C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao/vivado/sim/p_w1.xml
report_power -file C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao/vivado/sim/p_w1.txt -hier all -l 20
