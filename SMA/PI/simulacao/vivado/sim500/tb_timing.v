`timescale 1ns/1ps
// Testbench Verilog para a simulacao temporizada (netlist do Vivado + SDF).
// Le plaintexts de pts.hex, usa chave fixa, e grava o registrador de estado nos ciclos 0..10.
module tb_timing;
  parameter NENC = 500;
  reg clk = 0, rst = 0, start = 0;
  reg [127:0] pt = 0, key = 128'h000102030405060708090a0b0c0d0e0f;
  wire [127:0] state_o;
  wire done;
  aes_iter dut (.clk(clk), .rst(rst), .start(start), .pt(pt), .key(key),
                .state_o(state_o), .done(done));
  always #5 clk = ~clk;
  reg [127:0] mem [0:NENC-1];
  integer i, r, fd;
  initial begin
    $readmemh("pts.hex", mem);
    fd = $fopen("states_timing.txt", "w");
    #200;                                   // aguarda o GSR do netlist
    for (i = 0; i < NENC; i = i + 1) begin
      rst = 1; @(posedge clk); #1; rst = 0;
      pt = mem[i]; start = 1; @(posedge clk); #1; start = 0;
      @(negedge clk);
      $fwrite(fd, "%032x", state_o);
      for (r = 1; r <= 10; r = r + 1) begin
        @(negedge clk);
        $fwrite(fd, " %032x", state_o);
      end
      $fwrite(fd, "\n");
    end
    $fclose(fd);
    $finish;
  end
endmodule
