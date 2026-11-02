
# Teste de DFX (Dynamic Function eXchange / reconfiguracao parcial) no Vivado 2025.2,
# fluxo "non-project" (so Tcl, sem projeto .xpr). So testa a FERRAMENTA: compila duas
# implementacoes fisicas diferentes do MESMO bloco (rm_variant_a e rm_variant_b, interface
# identica) e troca uma pela outra via DFX. NAO simula nenhum ataque.
#
# Padrao: as DUAS variantes sao sintetizadas fora de contexto (OOC) e depois "encaixadas"
# (stitch) no estatico via read_checkpoint -cell. Isso evita divergencia de nomes de porta
# entre uma sintese inline e uma OOC (ja visto num teste anterior: Vivado renomeou uma saida
# registrada de "dout" para "Q" na sintese inline).
set ROOT   C:/Users/cjean/Desktop/Estudos/SMA/PI/simulacao
set DFX    $ROOT/vivado_dfx
set OUT    $DFX/out
set PART   xc7z020clg400-1
file mkdir $OUT
file delete -force {*}[glob -nocomplain $OUT/*]

proc log {msg} { puts "DFX_LOG: $msg" }

# ---------- 0) sintese OOC das duas variantes ----------
log "sintetizando variante A (OOC)..."
read_vhdl -vhdl2008 $ROOT/vhdl/aes_sbox_pkg.vhd
read_vhdl -vhdl2008 $DFX/rm_variant_a.vhd
synth_design -mode out_of_context -top rm_variant_a -part $PART
write_checkpoint -force $OUT/rm_variant_a_synth.dcp
set t_synth_a [expr {[clock milliseconds]}]
close_design -quiet

log "sintetizando variante B (OOC)..."
read_vhdl -vhdl2008 $ROOT/vhdl/aes_sbox_pkg.vhd
read_vhdl -vhdl2008 $DFX/rm_variant_b.vhd
synth_design -mode out_of_context -top rm_variant_b -part $PART
write_checkpoint -force $OUT/rm_variant_b_synth.dcp
close_design -quiet

# ---------- 1) estatico (dfx_top) com rm_inst = variante A inicialmente, so para existir
#               um ponto de partida a marcar como reconfiguravel ----------
set fh [open $DFX/dfx_top_cfg1.vhd w]
puts $fh {
library ieee;
use ieee.std_logic_1164.all;

entity dfx_top is
  port (
    clk    : in  std_logic;
    rst    : in  std_logic;
    din    : in  std_logic_vector(7 downto 0);
    dvalid : in  std_logic;
    dout   : out std_logic_vector(7 downto 0);
    done   : out std_logic
  );
end entity dfx_top;

architecture rtl of dfx_top is
begin
  -- rm_block (so a entidade, sem arquitetura): nasce como BLACK BOX de verdade,
  -- para que config1 e config2 sejam stitched do MESMO jeito (sem assimetria de nomes).
  rm_inst : entity work.rm_block
    port map (clk => clk, rst => rst, din => din, dvalid => dvalid, dout => dout, done => done);
end architecture rtl;
}
close $fh
read_vhdl -vhdl2008 $DFX/rm_block.vhd
read_vhdl -vhdl2008 $DFX/dfx_top_cfg1.vhd

log "sintetizando o estatico (dfx_top)..."
synth_design -top dfx_top -part $PART
create_clock -period 10.0 -name clk [get_ports clk]

log "marcando rm_inst como regiao reconfiguravel..."
set_property HD.RECONFIGURABLE 1 [get_cells rm_inst]
create_pblock pblock_rm
add_cells_to_pblock [get_pblocks pblock_rm] [get_cells rm_inst]
resize_pblock [get_pblocks pblock_rm] -add {SLICE_X0Y0:SLICE_X15Y49}
set_property SNAPPING_MODE ON [get_pblocks pblock_rm]

log "encaixando a netlist OOC da variante A no black box rm_inst..."
read_checkpoint -cell rm_inst $OUT/rm_variant_a_synth.dcp

set t0 [clock milliseconds]
opt_design
place_design
route_design
set t_impl_a [expr {([clock milliseconds]-$t0)/1000.0}]
write_checkpoint -force $OUT/config1_routed.dcp
# Pinos nao tem LOC/IOSTANDARD atribuidos (projeto de bancada, sem placa real alvo).
# Rebaixa essas 2 checagens de DRC para o bitstream poder ser gravado mesmo assim.
set_property SEVERITY {Warning} [get_drc_checks NSTD-1]
set_property SEVERITY {Warning} [get_drc_checks UCIO-1]
log "gravando bitstream config1 (estatico + variante A)... tempo impl=${t_impl_a}s"
if {[catch {write_bitstream -force -file $OUT/config1.bit} err]} {
  log "write_bitstream config1 FALHOU: $err"
} else {
  log "write_bitstream config1 OK (inclui o .bit completo; e o _partial.bit se a ferramenta gerar um para esta config)"
}
report_utilization -file $OUT/config1_util.rpt
report_timing_summary -file $OUT/config1_timing.rpt
report_power -file $OUT/config1_power.rpt

# ---------- 2) config2 (estatico TRAVADO + variante B via DFX) ----------
log "preparando config2: travando o estatico e trocando rm_inst por variante B..."
update_design -cell rm_inst -black_box
lock_design -level routing
read_checkpoint -cell rm_inst $OUT/rm_variant_b_synth.dcp

set t0 [clock milliseconds]
opt_design
place_design
route_design
set t_impl_b [expr {([clock milliseconds]-$t0)/1000.0}]
write_checkpoint -force $OUT/config2_routed.dcp
log "gravando bitstream config2 (estatico + variante B)... tempo impl=${t_impl_b}s"
if {[catch {write_bitstream -force -file $OUT/config2.bit} err]} {
  log "write_bitstream config2 FALHOU: $err"
} else {
  log "write_bitstream config2 OK"
}
# (o write_bitstream acima, com HD.RECONFIGURABLE setado, deve gerar sozinho um .bit parcial;
# conferido na listagem de arquivos no final do log)
report_utilization -file $OUT/config2_util.rpt
report_timing_summary -file $OUT/config2_timing.rpt
report_power -file $OUT/config2_power.rpt

log "verificando compatibilidade DFX (pr_verify) entre config1 e config2..."
if {[catch {set vr [pr_verify -full_check -file $OUT/pr_verify.rpt $OUT/config1_routed.dcp $OUT/config2_routed.dcp]} verr]} {
  log "pr_verify FALHOU ou nao aplicavel: $verr"
} else {
  log "pr_verify terminou: $vr"
}

log "arquivos gerados em $OUT:"
foreach f [lsort [glob -nocomplain $OUT/*]] {
  set sz [file size $f]
  log "  [file tail $f]  ${sz} bytes"
}
log "DFX_FLOW_DONE"
