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

Mesmo que a verificação da integridade dos bits seja uma função da Camada de Enlace, ela foi implementada nesse projeto para ajudar a entender e identificar os possiveis erros de transmissão. Para isso fo utilizado. Paridade Par no Método 1, que funciona com base nos 9 primeiros bits onde ele verifica se no total de bits 1 tem par.
Crc-8 no Método 2

## Pré-requisitos
    
O código exige o interpretador Python instalado e as bibliotecas `numpy` (para manipulação de arrays e processamento digital de sinais) e `sounddevice` (para reprodução e gravação de áudio via interface de som).

## Explicação do Método 1:  
   
O 'Método 1', como solicitado, traz uma abordagem mais simples e padronizada, baseada em impactos sonoros (batida de palmas, batida com a mão em alguma superfície, sons com a boca, etc.) onde a mensagem é transmitido em quadros de 9 bits. Para o algoritmo, uma batida representa 0, e duas batidas consecutivas 1, ele recebe as batidas dentro do intervalo de tempo e valida a paridade de cada quadro de 9 bits para garantir que a mensagem não foi corrompida pelo ruído do ambiente. 

### Utilização - Transmissão
O usuário precisa estar com o terminal aberto, dentro das pastas corretas, e então executar o comando 'python main.py' o terminal exibirá uma opção de escolha, 1 para 'Transmitir mensagem' ou 2 para 'Receber mensagem', selecionando 1 e pressionando a tecla Enter, haverá novamente a opção de escolha, mas agora entre 'Método 1' e 'Método 2', nesse caso, selecionando 1 para o 'Método 1'.
'Digite a mensagem a transmitir' será exibido no terminal, basta digitar a mensagem e pressionar Enter, e então a transmissão será iniciada.

### Utilização - Recepção
O usuário precisa estar com o terminal aberto, dentro das pastas corretas, e então executar o comando 'python main.py' o terminal exibirá uma opção de escolha, 1 para 'Transmitir mensagem' ou 2 para 'Receber mensagem', selecionando 2 e pressionando a tecla Enter, haverá novamente a opção de escolha, mas agora entre 'Método 1' e 'Método 2', nesse caso, selecionando 1 para o 'Método 1'. Ao pressionar Enter, o sistema iniciará a gravação, parando após pressionar novamente o Enter exibindo o resultado obtido.

## Explicação do Método 2:  

No 'Método 2', é utilizada uma abordagem mais avançada para a transmissão de dados. Aplica-se a técnica de modulação FSK (Frequency-Shift Keying), utilizando tons de 2000 Hz para representar o bit 0 e 3500 Hz para o bit 1, com 0,04 segundos de duração por símbolo. O texto é dividido em quadros de 16 bits, sendo 8 bits de dados e 8 bits de verificação de redundância cíclica (CRC-8).
Na recepção, a energia das frequências-alvo é calculada para localizar o ponto exato de início da mensagem, finalizando com o recálculo do CRC-8.
O algoritmo CRC-8 (Cyclic Redundancy Check de 8 bits) recebe o quadro de 16 bits, separa os 8 bits de dados e refaz a divisão polinomial. Se o resto da divisão for zero, significa que os dados não sofreram interferência. Caso contrário, a validação matemática falha e o sistema descarta o quadro corrompido. 

### Utilização - Transmissão
O usuário precisa estar com o terminal aberto, dentro das pastas corretas, e então executar o comando 'python main.py' o terminal exibirá uma opção de escolha, 1 para 'Transmitir mensagem' ou 2 para 'Receber mensagem', selecionando 1 e pressionando a tecla Enter, haverá novamente a opção de escolha, mas agora entre 'Método 1' e 'Método 2', nesse caso, selecionando 2 para o 'Método 2'.
'Digite a mensagem a transmitir' será exibido no terminal, basta digitar a mensagem e pressionar Enter, e então a transmissão será iniciada, utilizando 8 bits via FSK, 2000 Hz para bit 0 e 3200 Hz para bit 1.

### Utilização - Recepção
O usuário precisa estar com o terminal aberto, dentro das pastas corretas, e então executar o comando 'python main.py' o terminal exibirá uma opção de escolha, 1 para 'Transmitir mensagem' ou 2 para 'Receber mensagem', selecionando 2 e pressionando a tecla Enter, haverá novamente a opção de escolha, mas agora entre 'Método 1' e 'Método 2', nesse caso, selecionando 2 para o 'Método 2'. Ao pressionar Enter, o sistema iniciará a gravação, parando após pressionar novamente o Enter exibindo o resultado obtido.

**Divisão de Tarefas para cada membro da equipe:**  
Eduardo Giroto:  
Pedro Frederico:  
Nicolas Nakaie:  
Kauã Lopes:  
Walter Aurélio:  

## Desafios, Problemas e Soluções:  
### Validação e Deteção de Corrupção de Dados (Paridade)
Problema: Ruidos acusticos indesejados, como cliques de teclado e ecos no recinto podiam inverter bits ou dificultar a interpretação pelo receptor.
Solução: A funcionalidade "Pariedade" funciona com 9 bits, sendo o nono bit reservado para a pariedade. O algoritmo calcula se a quantidade de bits '1' é par. Caso algum bit seje perdido ou invertido, o calculo de pariedade identifica o erro e retorna que o quadro está corrompido. Isso impede que seje exibida uma mensagem errada. 

### Tratamento de quadors incompletos
Problema: Caso a gravacao fosse interrompida ou desse erro por causa de ruido, ocorria um desalinhamento na contagem dos bits, o que causava problemas ao tentar converter os bytes incompletos.
Solução: Foi implementada uma lógica de validação parcial nos dois metodos. O código agora contabiliza os quadros íntegros e transcreve a mesnsagem (caracter e bits) obtida até o limite válido. Ao chegar nos quadros corrompidos o sistema um aviso detalhando o erro e indincando a quantidade de bits que faltaram para fechar o quadro. 

**Declaração do Uso de Inteligência Artificial:**  

**Conclusão:**  
