# Relatório: teste de DFX (reconfiguração parcial dinâmica) no Vivado 2025.2

Teste de **ferramenta**, não de segurança: confirma se o Vivado ML Standard (edição gratuita) consegue executar o fluxo completo de *Dynamic Function eXchange* (DFX) — duas implementações físicas diferentes do mesmo bloco, trocadas por reconfiguração parcial — e mede os números de engenharia (tempo, tamanho de bitstream, área). **Não tenta recuperar nenhuma chave.**

Local: `PI/simulacao/vivado_dfx/`. Dispositivo: XC7Z020 (Zynq-7000), pacote `clg400-1`.

---

## 1. O que foi montado

Um projeto mínimo de bancada, só para exercitar o mecanismo:

- **`dfx_top`** (estático): portas estreitas (`clk`, `rst`, `din[7:0]`, `dvalid`, `dout[7:0]`, `done`), para caber no pacote sem exigir uma placa real.
- **`rm_inst`**: a região reconfigurável, com interface fixa (entidade `rm_block`, só a declaração de porta).
- **Duas variantes físicas** da região, mesma interface, implementações diferentes:
  - **Variante A**: consulta a tabela da S-box do AES (já usada no projeto) + 3 estágios de pipeline.
  - **Variante B**: XOR e rotações de bits encadeadas, sem tabela, 4 estágios de pipeline.
  - Nenhuma das duas é uma cifra real — servem só para a ferramenta ter duas implementações fisicamente distintas para trocar.

## 2. Fluxo executado (`dfx_flow.tcl`, modo *non-project*, só Tcl)

1. Síntese **fora de contexto (OOC)** de cada variante separadamente.
2. Síntese do estático com `rm_inst` como **black box de verdade** (entidade sem corpo).
3. `rm_inst` marcado com `HD.RECONFIGURABLE`; criação de um Pblock (`SLICE_X0Y0:SLICE_X15Y49`) para a região.
4. **Config. 1** = estático + variante A: a netlist OOC de A é "encaixada" no black box (`read_checkpoint -cell`), depois `opt_design` → `place_design` → `route_design` → `write_bitstream`.
5. **Config. 2** = estático + variante B: a partir do checkpoint roteado da Config. 1, a região é esvaziada de novo (`update_design -cell rm_inst -black_box`) e a parte estática é **travada** (`lock_design -level routing`) — só então a variante B é encaixada e implementada.
6. `pr_verify -full_check` compara as duas implementações.

### Um erro encontrado e corrigido no caminho

Na primeira tentativa, o Vivado renomeou a porta de saída da variante A de `dout` para `Q` ao sintetizá-la **junto** com o estático (otimização entre hierarquias). Quando tentei encaixar a variante B (sintetizada à parte, com nomes preservados), os nomes das portas não bateram e o processo travou. A correção: sintetizar **as duas variantes sempre fora de contexto**, e fazer o estático nascer com uma **black box real** desde o início. Isso resolveu, e deixa documentado que, no fluxo de DFX, **a síntese do bloco reconfigurável nunca deve ser feita junto com o estático**.

## 3. Resultados

### 3.1 O mecanismo funciona

```
INFO: [Constraints 18-13351] HDPRVerify-38: Following dcps passed to pr_verify have unlocked static: config1_routed.dcp
INFO: [Vivado 12-3253] PR_VERIFY: check points config1_routed.dcp and config2_routed.dcp are compatible
```

O `pr_verify` confirma que as duas configurações compartilham a **mesma lógica estática roteada** (1.224 blocos (*tiles*) e 170 conexões (*pips*) de roteamento estático idênticos nas duas) e têm os **20 pinos de partição compatíveis**. Isso é a prova de que a reconfiguração parcial, como mecanismo de ferramenta, está funcionando: só a região marcada troca, o resto permanece.

### 3.2 Tempos

| Etapa | Variante A | Variante B |
|---|---|---|
| Síntese fora de contexto | 18 s | 15 s |
| Implementação (opt+place+route) da configuração completa | 28,7 s | 28,8 s |
| **Total por configuração** | **≈ 47 s** | **≈ 44 s** |

A implementação da Config. 2 **reaproveitou** a parte estática já roteada da Config. 1 (via `lock_design`); mesmo assim, o tempo de `place_design`+`route_design` ficou parecido, porque o projeto é pequeno (a economia de tempo do reaproveitamento é mais visível em projetos maiores).

### 3.3 Tamanho dos bitstreams

| Arquivo | Tamanho | Observação |
|---|---|---|
| `config1.bit` (completo) | 4.045.683 bytes (≈ 4,05 MB) | Bitstream cheio do XC7Z020 |
| `config1_pblock_rm_partial.bit` | **383.476 bytes** (≈ 374 KB) | **Parcial** — só a região reconfigurável |
| `config2.bit` (completo) | 4.045.683 bytes | Idêntico em tamanho ao de config1 (mesmo dispositivo) |
| `config2_pblock_rm_partial.bit` | **383.476 bytes** | Parcial de B — mesmo tamanho do de A (mesma área de Pblock) |

O bitstream parcial é **9,5% do tamanho do completo**. Os dois bitstreams parciais, gerados **automaticamente** pelo Vivado assim que a célula está marcada `HD.RECONFIGURABLE` — não foi preciso nenhum comando ou opção extra de licença.

### 3.4 Estimativa de tempo de reconfiguração (projeção, não medida)

Usando o tamanho do parcial (383.476 bytes) com as taxas de transferência da interface ICAP citadas na literatura revisada no projeto (não medidas aqui):

| Taxa | Tempo estimado |
|---|---|
| 400 MB/s (teórico, 32 bits a 100 MHz) | ≈ 0,96 ms |
| 10 MB/s (controlador típico, caso favorável) | ≈ 38 ms |
| 4,6 MB/s (controlador típico, caso menos favorável) | ≈ 83 ms |

Isto é só a **razão tamanho ÷ taxa**. O tempo real de reconfiguração em hardware depende do controlador (PCAP/ICAP, software ou IP dedicado) e **não foi medido** — não há placa neste projeto.

### 3.5 Diferença de área e custo entre as variantes

| | Variante A (config1) | Variante B (config2) |
|---|---|---|
| Slice LUTs | 0 | 16 |
| Slice Registers | 11 | 29 |
| WNS (folga de temporização) | +7,69 ns | +8,41 ns |
| Potência total estimada | 0,111 W | 0,107 W |
| Potência dinâmica estimada | 0,007 W | 0,003 W |

(Variante A usa 0 LUTs porque a tabela da S-box cabe inteira nos próprios flip-flops/MUX de rota nesta implementação mínima; isso é uma particularidade deste bloco de bancada, não uma regra geral.)

### 3.6 Avisos (nenhum erro bloqueante)

- `DRC NSTD-1` e `DRC UCIO-1` (pinos sem local físico nem padrão elétrico atribuído): **esperado**, porque este design de bancada não tem placa alvo. Rebaixados para aviso de propósito, só para permitir gerar o bitstream de teste; **nunca fazer isso em um projeto que vai para hardware real**.
- `DRC HDPR-45` (1 aviso crítico): o retângulo do Pblock não cobre todos os tipos de sítio recomendados pela ferramenta para a região. Não impediu a implementação, mas em um projeto real vale ajustar a forma do Pblock.
- **Nenhum erro** nas duas implementações (`DRC finished with 0 Errors` nas duas).

## 4. O que isso confirma sobre a edição gratuita do Vivado

| Recurso usado | Funcionou na ML Standard, sem licença extra? |
|---|---|
| `HD.RECONFIGURABLE`, Pblock, DFX não-projeto | **Sim** |
| `write_bitstream` completo | Sim |
| `write_bitstream` **parcial** (gerado automaticamente) | **Sim** |
| `pr_verify` | Sim |
| `lock_design -level routing` (reaproveitar estático) | Sim |

Isso resolve a dúvida de licenciamento que tínhamos: pelo menos para este projeto pequeno no XC7Z020, **a edição gratuita cobriu o fluxo de DFX ponta a ponta**, sem nenhuma mensagem pedindo licença adicional.

## 5. Limites deste teste

- **Bloco de bancada, não o AES do projeto.** As variantes A e B não são cifras; servem só para validar a ferramenta. Portar o `aes_iter` (barramentos de 128 bits) para esse fluxo exigiria uma interface estreita (serial, por exemplo) para caber nos pinos do pacote, ou manter a reconfiguração em contexto *out-of-context*/sem bitstream real (como já fazemos no fluxo de simulação temporizada).
- **Sem placa.** Os bitstreams não foram carregados em hardware; os tempos de reconfiguração são projeção, não medição.
- **Pblock pequeno e único.** Não foi testado com múltiplas regiões reconfiguráveis nem com regiões do tamanho do `aes_iter` real (que usa BRAM, por exemplo — BRAM dentro de uma região reconfigurável tem regras adicionais não exercitadas aqui).
- **Nenhuma relação com análise de potência por canal lateral.** Este teste é sobre a ferramenta de reconfiguração, não sobre o que foi medido nos relatórios da rodada noturna.

## 6. Próximo passo de engenharia, se o grupo quiser continuar por aqui

Para ligar este mecanismo ao restante do projeto (o `aes_iter` já implementado e medido), seria necessário:
1. Definir uma interface estreita para o `aes_iter` caber como região reconfigurável de um estático maior (ex.: FIFO ou registrador serial para entrada/saída de 128 bits).
2. Repetir este mesmo fluxo com duas ou mais variantes **reais** do `aes_iter` (por exemplo, as compilações `base` e `nobram` que já existem).
3. Medir o tempo e o tamanho do bitstream parcial dessa região maior (deve ser proporcional ao tamanho do `aes_iter`: 748 a 1.251 LUTs, contra os poucos LUTs/FFs deste teste de bancada).

Isso é só o próximo passo de **engenharia de hardware** (construir e medir a reconfiguração). Qualquer uso desses artefatos para avaliar impacto sobre a recuperação de chave é uma etapa separada, e deve ser conduzida com orientação da professora ou de alguém da área de segurança, como já conversamos.
