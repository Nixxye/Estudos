%% GUIA P1 - Sistemas de Controle A (ELN77A) - Listas 01 e 02 no MATLAB
% Requer: Symbolic Math Toolbox (syms/solve/limit) e Control System Toolbox
% (tf/zpk/feedback/connect/lsim). Rode seção por seção (Ctrl+Enter).
%
% Metodo A (simbolico): uma equacao por somador + equacao da saida -> solve.
%   REGRA: em solve(eqs, [..]) liste TODOS os sinais que voce nomeou + C.
%   Se o numero de equacoes for diferente do numero de incognitas o
%   resultado vem "Empty sym: 0-by-1".
% Metodo B (numerico) : series/parallel/feedback com valores escolhidos.
% Metodo C (transcricao): sumblk + connect copia o diagrama bloco a bloco.

clear; clc; close all

%% Q1(a) - Lista 02:  C/R = (G + H1) / (1 + G*H2)
% ATENCAO: H2 le a saida de G (antes do somador final), nao C(s).
syms R C E G H1 H2
eqs = [ E == R - H2*G*E, ...   % somador 1
        C == G*E + H1*E ];     % somador 2
sol = solve(eqs, [E C]);
T1a = simplify(sol.C / R);
disp('Q1(a):'), pretty(T1a)

% Conferencia numerica (Metodo C)
G = tf(10,[1 2]);  H1 = tf(1,[1 3]);  H2 = tf(0.5,1);
G.u  = 'e';  G.y  = 'g';
H1.u = 'e';  H1.y = 'h1';
H2.u = 'g';  H2.y = 'h2';                 % H2 le a saida de G
S1 = sumblk('e = r - h2');
S2 = sumblk('c = g + h1');
Tc = connect(G,H1,H2,S1,S2,'r','c');
Tf = minreal((G + H1)/(1 + G*H2));
fprintf('Q1(a) diferenca connect x formula: %g\n', norm(minreal(Tc) - Tf));

%% Q1(b) - Lista 02:  C/R = G1*G2 + G2 + 1   (sem realimentacao)
syms R C X G1 G2
sol = solve([ X == G1*R + R, C == G2*X + R ], [X C]);
T1b = expand(sol.C / R);
disp('Q1(b):'), disp(T1b)

G1 = tf(2,[1 1]); G2 = tf(3,[1 4]);
Tb = minreal( (1 + G1)*G2 + 1 );

%% Q1(c) - Lista 02:  C/R = (G1+G2) / (1 + (G1+G2)*(G3-G4))
syms R C E F G1 G2 G3 G4
eqs = [ F == G3*C - G4*C, ...  % somador da realimentacao (+G3, -G4)
        E == R - F, ...
        C == (G1 + G2)*E ];
sol = solve(eqs, [E F C]);
T1c = simplify(sol.C / R);
disp('Q1(c):'), pretty(T1c)

G1 = tf(1,[1 1]); G2 = tf(2,[1 3]); G3 = tf(1,[1 5]); G4 = tf(0.2,1);
Tb = feedback(parallel(G1,G2), G3 - G4);   % feedback(Gdireto, Hrealim)

%% Q1(d) - Lista 02  ==  Q1 - Lista 01:  C/R = (1+G1)*G2 / (1 + G2*(H1-H2))
syms R C E F U G1 G2 H1 H2
eqs = [ F == H1*C - H2*C, ...
        E == R - F, ...
        U == E + G1*R, ...     % G1 entra direto de R, fora da malha
        C == G2*U ];
sol = solve(eqs, [E F U C]);
T1d = simplify(sol.C / R);
disp('Q1(d) / L01-Q1:'), pretty(T1d)

% Metodo C: transcricao literal
G1 = tf(3,1); G2 = tf(1,[1 2]); H1 = tf(1,[1 5]); H2 = tf(2,1);
G1.u='r'; G1.y='g1';   G2.u='u'; G2.y='c';
H1.u='c'; H1.y='h1';   H2.u='c'; H2.y='h2';
S1 = sumblk('f = h1 - h2');
S2 = sumblk('e = r - f');
S3 = sumblk('u = e + g1');
Tc = connect(G1,G2,H1,H2,S1,S2,S3,'r','c');
% Metodo B: G1 movido para fora da malha
Tb = minreal( (1 + G1) * feedback(G2, H1 - H2) );
fprintf('Q1(d) diferenca connect x formula: %g\n', norm(minreal(Tc) - Tb));

%% Q2 - Listas 01 e 02:  C = (Gc*Gp*R + D) / (1 + Gc*Gp)
syms R D C E Gc Gp
sol = solve([ E == R - C, C == Gc*Gp*E + D ], [E C]);
Cs  = simplify(sol.C);
disp('Q2:'), disp(collect(Cs, [R D]))
T_R = simplify(diff(Cs, R));   % Gc*Gp/(1+Gc*Gp)  -> C/R
T_D = simplify(diff(Cs, D));   % 1/(1+Gc*Gp)      -> C/D

% Metodo C com duas entradas -> sistema 1x2
Gc = tf(2,1); Gp = tf(1,[1 1]);
Gc.u='e'; Gc.y='u';  Gp.u='u'; Gp.y='y';
S1 = sumblk('e = r - c');
S2 = sumblk('c = y + d');
T  = connect(Gc,Gp,S1,S2,{'r','d'},'c');
tf(T)                          % T(1) = C/R,  T(2) = C/D
figure, step(T), grid on, title('Q2: resposta a degrau em R e em D')

%% Q3 - Listas 01 e 02:  Eo/Ei = (R2*C2*s + 1) / ((R1*C2 + R2*C2)*s + 1 + C2/C1)
syms s R1 R2 C1 C2 positive
Z1 = R1 + 1/(C1*s);            % braco serie: R1 -- C1
Z2 = R2 + 1/(C2*s);            % braco da saida: R2 -- C2
H  = simplify(Z2/(Z1 + Z2));   % divisor de tensao (saida sem carga)
[num, den] = numden(H);
num = collect(expand(num/C1), s);   % divide por C1 -> forma do gabarito
den = collect(expand(den/C1), s);
disp('Q3:'), pretty(num/den)

% Resposta em frequencia com valores de exemplo
Hn = subs(H, [R1 R2 C1 C2], [1e3 1e3 1e-6 1e-6]);
[n, d] = numden(Hn);
Htf = tf(sym2poly(n), sym2poly(d));
figure, bode(Htf), grid on, title('Q3: Bode com R=1k, C=1uF')

%% Q4 - Lista 01: e(inf) para degrau unitario  ->  1/11 = 0.0909
G = zpk([], [-1 -10], 100);    % 100/((s+1)(s+10)), tipo 0
T = feedback(G, 1);
fprintf('Q4 estavel? %d   polos: %s\n', isstable(T), mat2str(pole(T),3));

Kp    = dcgain(G);             % 10
e_inf = 1/(1 + Kp);            % 0.0909
fprintf('Q4: Kp = %g, e(inf) = 1/(1+Kp) = %.4f\n', Kp, e_inf);

Es = feedback(tf(1), G);       % E/R = 1/(1+G)
fprintf('Q4: dcgain(E/R) = %.4f\n', dcgain(Es));

[y, t] = step(T, 5);  e = 1 - y;
figure, plot(t, e), grid on, xlabel('t (s)'), ylabel('e(t)'), title('Q4: erro ao degrau')
fprintf('Q4: e(end) simulado = %.4f\n', e(end));

syms s
Gs = 100/((s+1)*(s+10));
disp('Q4 limite simbolico:'), disp(limit( s*(1/s)/(1 + Gs), s, 0 ))

%% Q5 - Lista 01: e(inf) para rampa com integrador  ->  1/Kv = 0.1
G = zpk([], [0 -1 -10], 100);  % 100/(s(s+1)(s+10)), tipo 1
T = feedback(G, 1);
fprintf('Q5 estavel? %d   polos: %s\n', isstable(T), mat2str(pole(T),3));
% polos -0.039 +- 3.03j: transitorio lento (~100 s) e muito oscilatorio

syms s
Gs = 100/(s*(s+1)*(s+10));
Kv    = limit(s*Gs, s, 0);     % 10
e_inf = 1/Kv;                  % 0.1
fprintf('Q5: Kv = %s, e(inf) = 1/Kv = %s\n', char(Kv), char(e_inf));
disp('Q5 limite simbolico:'), disp(limit( s*(1/s^2)/(1 + Gs), s, 0 ))

t = 0:0.01:150;  r = t;
y = lsim(T, r, t);  e = r - y;
figure, plot(t, e), grid on, xlabel('t (s)'), ylabel('e(t)'), title('Q5: erro a rampa')
fprintf('Q5: e(end) simulado = %.4f\n', e(end));

% Comparacao: sistema tipo 0 (Q4) com rampa -> erro cresce sem limite
G0 = zpk([], [-1 -10], 100);
y0 = lsim(feedback(G0,1), r, t);
fprintf('Tipo 0 com rampa: erro em t=150s = %.2f (diverge)\n', r(end) - y0(end));

%% Funcao generica: erro em regime pelo teorema do valor final
% Uso:  syms s;  erro_regime(100/((s+1)*(s+10)), 1/s)
function e = erro_regime(G_sym, R_sym)
    syms s
    e = limit( s * R_sym / (1 + G_sym), s, 0 );
end
