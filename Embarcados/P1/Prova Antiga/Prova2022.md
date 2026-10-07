# 1ª Prova (Teoria e Lab) – Sistemas Embarcados

**Prof. Douglas Renaux** - 2 / Maio / 2022 – Prova SEM consulta e sem calculadora

## 1. Questão 1 – Programação concorrente e RTOS – 4 pts

Você é o responsável, na empresa onde trabalha, a elaborar a solução para um novo produto. Trata-se de uma almofada com aquecimento elétrico controlada por um microcontrolador Cortex-M.

**Descrição do funcionamento:**

1. a interface com o usuário consiste em um botão de pressão e 3 leds: amarelo, laranja, vermelho.
2. a situação inicial é: aquecimento desligado, todos os leds apagados.
3. ao pressionar o botão uma vez o aquecimento vai a 30% e o led amarelo acende
4. ao pressionar o botão novamente o aquecimento vai a 60% e apenas o led laranja está iluminado
5. ao pressionar o botão novamente o aquecimento vai a 100% e apenas o led vermelho está iluminado.
6. ao pressionar o botão novamente volta-se ao passo 2.
7. após 40 minutos de aquecimento, contados desde que a última vez que o botão foi pressionado, o sistema desliga automaticamente (modo sleep). Neste caso, o led que estava aceso passa a piscar na frequência de 0.5 Hz (1 segundo aceso, 1 segundo apagado).
8. estando no modo sleep, ao pressionar o botão o controlador vai para a situação inicial (passo 2).

A solução a ser implementada deve fazer uso do ThreadX, de uma ISR, 3 threads, 2 filas de mensagens, um evento e um temporizador do ThreadX:

- cada vez que o botão é pressionado a ISR é chamada e seta o flag de evento para a tarefa "ModoDeOperação".
- a tarefa "ModoDeOperação" define o estado do sistema conforme as regras de funcionamento acima, e informa as tarefas "Leds" e "ControleDeTemperatura" o que devem fazer, enviando mensagens a elas. Há filas de mensagens separadas para "ModoDeOperação" informar "Leds" e "ControleDeTemperatura".
- a tarefa "Leds" gerencia os leds acendendo-os, apagando-os e fazendo-os piscar, conforme os comandos recebidos de "ModoDeOperação".
- a tarefa "ControleDeTemperatura" gerencia a resistência de aquecimento da almofada, conforme os comandos recebidos de "ModoDeOperação".

**1a ( 1 ponto )**
Apresente um diagrama em UML, usando a notação apresentada nesta disciplina, com o botão, a ISR, as tarefas, as filas de mensagens, o flag de evento, o temporizador, os leds e a resistência de aquecimento. Defina no diagrama os comandos enviados por meio das filas de mensagens.

**1b ( 1.5 pts )**
Escreva a função `tx_application_define( )`

**1c ( 1.5 pts )**
Escreva a função principal da tarefa "Leds". Esta função deve receber mensagens via fila com "ModoDeOperação", usar um temporizador do ThreadX, e ligar/desligar os leds adequadamente. Assuma que foi disponibilizada a função `void led(on_off, led_id);` onde `on_off` é uma enumeração com `OFF` e `ON` e `led_id` é uma enumeração com `AMARELO`, `LARANJA` e `VERMELHO`.

Esta função, chamada `LedsMain( )`, deve ter os parâmetros adequados para que possa ser referenciada pelo serviço `tx_thread_create( )`.

*(Respostas de 1a, 1b e 1c no espaço abaixo e no verso desta página.)*

## 2. Questão 2 – Interrupções – 3 pts

**2a ( 1.5 pts )**
Considerando o problema apresentado na questão 1, descreva DETALHADAMENTE, todo o processo de atendimento a uma interrupção do botão de pressão, desde o sinal elétrico gerado pelo botão pressionado até o início da execução do código da ISR. A descrição deve apresentar o funcionamento do hardware, do software, do controlador de interrupção, do core e da memória. Apresente na forma de uma sequência de passos. **Utilize o número de passos que achar necessário.**

**2b ( 1.5 pts )**
Escreva, em C, a ISR do botão de pressão. Considere que estão disponíveis as funções de acesso ao hardware do GPIO associado ao botão. O cabeçalho da ISR deve ser compatível com o de uma rotina de atendimento à interrupção.

## 3. Questão 3 – Assembly – 3 pts

Planeje e elabore duas funções em **assembly**. Estas funções devem seguir rigorosamente a AAPCS.

**função 1:**`void systickConfig(void)`
– esta função deve configurar o SysTick para gerar interrupções periódicas a cada 2ms, considerando que o clock do processador é de 100 MHz. A função também deve iniciar a operação do SysTick.

**função 2:**`void systickISR(void)`
– esta função é a rotina de atendimento do SysTick. Deve ler um inteiros sem sinal de 64 bits, que está no endereços 0x2000 0050. Este valor devem ser incrementado e o resultado, em 64 bits, deve ser armazenado no mesmo endereço. Lembre-se do correto tratamento do flag de carry (CY) quando tratar de inteiros de 64 bits.

**Apresente:3a ( 0.5 pts )** - planejamento das funções (graficamente ou textualmente)
**3b ( 0.25 pts )** - planejamento da alocação de registradores
**3c ( 2.25 pts )** - código assembly (preencher a tabela a seguir)

*(Responda abaixo os itens 3a e 3b, responda 3c na próxima página. Você será avaliado pela correção do código e pelo uso eficiente do conjunto de instruções.)*