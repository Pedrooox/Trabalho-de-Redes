# Fundamentação Teórica 


## Modelo ISO OSI
Física: Pega os bits e os transforma em uma forma de comunicação interpretável pelo meio de transmissão
Enlace: Transforma um canal bruto em uma linha que parece livre de erros. Usando a detecção de erros, evita mandar muitas mensagens para um dispositivo mais lento e gerencia o endereço físico e o controle de acesso ao meio.
Redes: Responsável pelo endereçamento lógico e pelo roteamento
tranporte: Responsável pelo controle dos dados, podendo ser orientado à conexão ou não orientado à conexão.
Sessão: Estabelece e encerra uma sessão de comunicação entre o transmissor e o receptor.
Apresentação: Faz a tradução e criptografia dos dados.
Aplicação: Funciona como uma interface com o usuario (software) e a rede.

## Camada Física

A Camada Física é a primeira camada do modelo OSI, sendo a base de toda a comunicação de rede. Ela é responsável pela transmissão e recepção de um fluxo de bits brutos não estruturados através de um meio de comunicação físico.

Sinais Analógicos vs. Digitais: O sinal analógico varia de forma contínua ao longo do tempo e pode assumir infinitos valores de amplitude dentro de um intervalo. Propaga-se em forma de ondas contínuas. Com tudo, o sinal digital é discreto e não contínuo, assumindo apenas um conjunto finito de valores previamente definidos (geralmente dois estados, 0 e 1, representados por transições abruptas de tensão elétrica, luz ou frequência).

Largura de Banda: Em telecomunicações e na física de redes, refere-se à diferença entre as frequências mais alta e mais baixa que um canal de comunicação suporta e consegue transmitir sem degradação excessiva, sendo medida em Hertz (Hz). A largura de banda determina a capacidade máxima de transporte de dados do meio.

Modulação: É o processo de alterar uma ou mais características de uma onda periódica (chamada de onda portadora) com um sinal modulador que contém a informação real. Ao variar propriedades como amplitude, frequência ou fase, a modulação permite adequar o sinal para que ele viaje longas distâncias pelo meio físico sem perder sua integridade.

## Detecção de Erros

Mesmo que a verificação da integridade dos bits seja uma função da Camada de Enlace, ela foi implementada nesse projeto para ajudar a entender e identificar os possiveis erros de transmissão. Para isso fo utilizado. 
**Paridade Par Método 1:** a mensagem é dividida em quadros fixos de 9 bits (8 bits de dados UTF-8 + 1 bit de paridade).
**Crc-8 no Método 2:** a mensagem é transmitida em quadros de 16 bits (8 bits de dados + 8 bits de código de verificação CRC). 

## Pré-requisitos
    
O código exige o interpretador Python e o pip instalado e as bibliotecas `numpy` (para manipulação de arrays e processamento digital de sinais) e `sounddevice` (para reprodução e gravação de áudio via interface de som).

# Engenharia e Arquitetura das Soluções

## Explicação do Método 1:  
   
O 'Método 1', como solicitado, traz uma abordagem mais simples e padronizada, com uma abordagem de comunicação acústica baseada em sinais de impacto ou pulsos sonoros curtos (batida de palmas, batida com a mão em alguma superfície ou beeps de áudio, etc.)mensagem é dividida e transmitida em quadros estruturados de 9 bits (8 bits de dados úteis + 1 bit de paridade). Para o algoritmo, uma batida + intervalo representa 0, e duas batidas consecutivas + intervalo representa 1. O recptor recebe as batidas no audio, agrupa e valida a paridade de cada quadro de 9 bits para garantir que a mensagem não foi corrompida pelo ruído do ambiente. 

### Detecção de Erros via Paridade Par
A Paridade Par é um mecanismo simples e eficaz de checagem de erros na camada de enlace. O seu funcionamento ocorre em duas etapas:

**Na Transmissão:** O software analisa os 8 bits de dados (UTF-8) do caractere e conta a quantidade de bits 1 presentes, Se a contagem de bits 1 for ímpar, o 9º bit (bit de paridade) é definido como 1, garantindo que a soma total de bits 1 no quadro de 9 bits seja sempre um número par. Se a contagem já for par, o 9º bit é definido como 0

**Na Recepção:** Ao captar o quadro de 9 bits pelo áudio, o software calcula novamente a paridade sobre os 8 primeiros bits de dados recebidos. Se o bit de paridade calculado for igual ao 9º bit captado no áudio, o quadro é validado e convertido em texto. Caso haja divergência (provocada por uma batida perdida ou por um eco/ruído captado erroneamente), o sistema detecta a corrupção e rejeita o quadro. 

### Utilização - Transmissão
O usuário precisa estar com o terminal aberto, dentro das pastas corretas, e então executar o comando 'python main.py' o terminal exibirá uma opção de escolha, 1 para 'Transmitir mensagem', 2 para 'Receber mensagem' e 0 para 'sair', selecionando 1 e pressionando a tecla Enter, haverá novamente a opção de escolha, mas agora entre 'Método 1' e 'Método 2', nesse caso, selecionando 1 para o 'Método 1'.
'Digite a mensagem a transmitir' será exibido no terminal, basta digitar a mensagem e pressionar Enter, e então a transmissão será iniciada.

### Utilização - Recepção
O usuário precisa estar com o terminal aberto, dentro das pastas corretas, e então executar o comando 'python main.py' o terminal exibirá uma opção de escolha, 1 para 'Transmitir mensagem', 2 para 'Receber mensagem'e 0 para 'sair', selecionando 2 e pressionando a tecla Enter, haverá novamente a opção de escolha, mas agora entre 'Método 1' e 'Método 2', nesse caso, selecionando 1 para o 'Método 1'. Ao pressionar Enter, o sistema iniciará a gravação, parando após pressionar novamente o Enter exibindo o resultado obtido.

## Explicação do Método 2:  

O Método 2 representa uma abordagem de comunicação acústica digital de maior desempenho e confiabilidade, operando através da modulação por chaveamento de frequência (2-FSK — Binary Frequency-Shift Keying) acoplada a um mecanismo avançado de detecção de erros na camada de enlace (CRC-8).
Neste método, os dados são transmitidos em quadros estruturados de 16 bits (8 bits de carga útil de dados + 8 bits de verificação de redundância).
**A modulação 2-FSK** mapeia diretamente os bits binários em frequências senoidais puras no domínio da frequência, sedo o bit 0 transmitido como um tom senoidal de 4000 Hz. O bit 1 e transmitido como um tom senoidal de 5000 Hz. Onde tem uma duração do Símbolo Fixada em 0,08 segundos por bit, permitindo uma taxa de transmissão substancialmente mais rápida que o Método 1.

### Demodulacao (FFT)

Na **demodulacao** ocorre a recuperação do sinal ocorre por meio do fatiamento contínuo do áudio em janelas temporais. A análise de frequência é realizada individualmente para cada janela usando a Transformada Rápida de **Fourier (FFT):** a FFT converte o trecho de áudio do domínio do tempo para o domínio da frequência. O algoritmo extrai a densidade de energia acumulada especificamente em 4000 Hz e 5000 Hz, com isso ele faz uma comparacao das energias e com isso e demodulada como bit 1 ou 0.

### Detecção de Erros via CRC-8 (Cyclic Redundancy Check)

O **CRC-8 (Cyclic Redundancy Check)** é um método matemático altamente robusto baseado em divisão polinomial em aritmética de módulo 2.
**Na Transmissão:** O algoritmo pega os 8 bits de dados (mensagem) e aplica o polinômio gerador padrão $x^8 + x^2 + x + 1$ (representado pelo hexadecimal 0x07). O resto dessa divisão resulta em um byte de verificação (8 bits de CRC), que é anexado ao final do quadro, totalizando 16 bits.
**Na Recepção:** Ao receber o quadro de 16 bits pelo ar, o receptor divide a sequência completa pelo mesmo polinômio gerador. Se o resto da divisão for igual a zero (ou o CRC recalculado for idêntico ao recebido), matematicamente prova-se que o quadro não sofreu interferências de fase, ecos ou ruídos durante a propagação no ar, caso contrario a validação falha e o quadro corrompido é rejeitado.

### Utilização - Transmissão
O usuário precisa estar com o terminal aberto, dentro das pastas corretas, e então executar o comando 'python main.py' o terminal exibirá uma opção de escolha, 1 para 'Transmitir mensagem' ou 2 para 'Receber mensagem' e 0 para 'Sair', selecionando 1 e pressionando a tecla Enter, haverá novamente a opção de escolha, mas agora entre 'Método 1' e 'Método 2', nesse caso, selecionando 2 para o 'Método 2'.
'Digite a mensagem a transmitir' será exibido no terminal, basta digitar a mensagem e pressionar Enter, e então a transmissão será iniciada, utilizando 8 bits via FSK, 2000 Hz para bit 0 e 3200 Hz para bit 1.

### Utilização - Recepção
O usuário precisa estar com o terminal aberto, dentro das pastas corretas, e então executar o comando 'python main.py' o terminal exibirá uma opção de escolha, 1 para 'Transmitir mensagem' ou 2 para 'Receber mensagem' e 0 para 'Sair', selecionando 2 e pressionando a tecla Enter, haverá novamente a opção de escolha, mas agora entre 'Método 1' e 'Método 2', nesse caso, selecionando 2 para o 'Método 2'. Ao pressionar Enter, o sistema iniciará a gravação, parando após pressionar novamente o Enter exibindo o resultado obtido.


# Divisão de Tarefas para cada membro da equipe:  
**Eduardo Giroto:** Planejameto, video e software (fez a base do metodo 1 e main.py)
**Pedro Frederico:** Planejamento, video e testador  
**Nicolas Nakaie:**  Planejamento, testador, pesquisa, software ( metodo 2) 
**Kauã Lopes:** Pesquisa, documentacao, planejamento e software ( arquivos de teste e metodo 2 ). 
**Walter Aurélio:** Planejamento, documentacao e testador 

# Desafios, Problemas e Soluções:  
### Validação e Deteção de Corrupção de Dados (Paridade)
Problema: Ruidos acusticos indesejados, como cliques de teclado e ecos no recinto podiam inverter bits ou dificultar a interpretação pelo receptor.
Solução: A funcionalidade "Pariedade" funciona com 9 bits, sendo o nono bit reservado para a pariedade. O algoritmo calcula se a quantidade de bits '1' é par. Caso algum bit seje perdido ou invertido, o calculo de pariedade identifica o erro e retorna que o quadro está corrompido. Isso impede que seje exibida uma mensagem errada. 

### Tratamento de quadors incompletos
Problema: Caso a gravacao fosse interrompida ou desse erro por causa de ruido, ocorria um desalinhamento na contagem dos bits, o que causava problemas ao tentar converter os bytes incompletos.
Solução: Foi implementada uma lógica de validação parcial nos dois metodos. O código agora contabiliza os quadros íntegros e transcreve a mesnsagem (caracter e bits) obtida até o limite válido. Ao chegar nos quadros corrompidos o sistema um aviso detalhando o erro e indincando a quantidade de bits que faltaram para fechar o quadro. 

# Declaração do Uso de Inteligência Artificial: 
Utilizamos as Inteligências Artificiais para gerar os códigos iniciais e suas implementações, assim como alterações e correções feitas durante o processo e desenvolvimento do trabalho. As IAs também foram utilizadas como ferramenta para estudos e explicações para maior compreensão dos códigos e do trabalho como um todo.
Claude: Códigos iniciais;
Google Gemini: Novos códigos, pesquisas, dúvidas, alterações dos códigos;
Google Antigravity: Utilizado junto ao VS Code para alterações dos códigos e correção de erros.

# Conclusão:  
O trabalho nos permitiu, como grupo, observar as principais dificuldades e desafios presentes na camada Física. Ao utilizar frequências sonoras para transportar dados, os ruídos e frequências externas são um empecilho que atrapalham o programa de ler os sons e reconhecer a mensagem transmitida, assim como precisamos de formas dentro do código para controle de erros, como o bit de paridade par e CRC-8. Tivemos bastante trabalho com o metodo 2, onde foi necessario refazer-lo para que conseguissemoos um resultado empolgante, onde foi trocado o algoritimo de goertzel para o FFT, e melhoras o nosso entendimento com o fsk e crc-8. De forma prática aprendemos como contornar essas interferências e buscar através de tentativa e erro, pesquisa e alterações no código, as melhores maneiras de receber e transmitir esses dados com maior precisão.
