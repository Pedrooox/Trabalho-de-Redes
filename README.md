**Fundamentação Teórica:**  

**Engenharia e Arquitetura das Soluções:**  
Explicação Geral:
    
O trabalho tem como objetivo a compressão da Camada Física do modelo ISO/OSI utilizando ondas sonoras para
transmitir informações binárias entre dispositivos, como pré requisitos, o código exige, não só a instalação do Python na máquina, como também a instalação de duas bibliotecas, NumPy (para manipulação de arrays e processamento digital de sinais) e SoundDevice (para reprodução e gravação de áudio via placa de som).

Explicação do Método 1:  
   
O 'Método 1', como solicitado, traz uma abordagem mais simples e padronizada, baseada em impactos sonoros (batida de palmas, batida com a mão em alguma superfície, sons com a boca, etc.) onde o caractere é transmitido em quadros de 9 bits. Para o algoritmo, uma batida representa 0, e duas batidas consecutivas 1, ele recebe as batidas dentro do intervalo de tempo e valida a paridade de cada quadro de 9 bits para garantir que a mensagem não foi corrompida pelo ruído do ambiente. 

Utilização - Transmissão: O usuário precisa estar com o terminal aberto, dentro das pastas corretas, e então executar o comando 'python main.py' o terminal exibirá uma opção de escolha, 1 para 'Transmitir mensagem' ou 2 para 'Receber mensagem', selecionando 1 e pressionando a tecla Enter, haverá novamente a opção de escolha, mas agora entre 'Método 1' e 'Método 2', nesse caso, selecionando 1 para o 'Método 1'.
'Digite a mensagem a transmitir' será exibido no terminal, basta digitar a mensagem e pressionar Enter, e então a transmissão será iniciada.

Utilização - Recepção: O usuário precisa estar com o terminal aberto, dentro das pastas corretas, e então executar o comando 'python main.py' o terminal exibirá uma opção de escolha, 1 para 'Transmitir mensagem' ou 2 para 'Receber mensagem', selecionando 2 e pressionando a tecla Enter, haverá novamente a opção de escolha, mas agora entre 'Método 1' e 'Método 2', nesse caso, selecionando 1 para o 'Método 1'. O sistema irá pedir a quantidade de caracteres esperados na mensagem, após informar, basta pressionar Enter, e então ele gravará a mensagem durante 35 segundos, exibindo o resultado após esse tempo.

Explicação do Método 2:  

No 'Método 2', o texto é dividido em quadros de 16 bits, com 8 bits de dados e 8 de verificação redundante CRC-8. A transmissão inicia em 3000 Hz para sincronização, seguido por tons de 1200 Hz para o bit 0 e 2200 Hz para o bit 1, tendo 0,05 segundos de duração por símbolo. 
Para a recepção, a energia das frequências alvo é calculada para localizar o ponto exato de início da mensagem, finalizando com o recalculo do CRC-8.
O CRC-8 (Cyclic Redundancy Check de 8 bits) serve para detectar erros de transmissão em sistemas de comunição e armazenamento de dados.

Utilização - Transmissão: O usuário precisa estar com o terminal aberto, dentro das pastas corretas, e então executar o comando 'python main.py' o terminal exibirá uma opção de escolha, 1 para 'Transmitir mensagem' ou 2 para 'Receber mensagem', selecionando 1 e pressionando a tecla Enter, haverá novamente a opção de escolha, mas agora entre 'Método 1' e 'Método 2', nesse caso, selecionando 2 para o 'Método 2'.
'Digite a mensagem a transmitir' será exibido no terminal, basta digitar a mensagem e pressionar Enter, e então a transmissão será iniciada, utilizando 9 quadros via FSK, 1200 Hz para bit 0 e 2200 Hz para bit 1.

Utilização - Recepção: O usuário precisa estar com o terminal aberto, dentro das pastas corretas, e então executar o comando 'python main.py' o terminal exibirá uma opção de escolha, 1 para 'Transmitir mensagem' ou 2 para 'Receber mensagem', selecionando 2 e pressionando a tecla Enter, haverá novamente a opção de escolha, mas agora entre 'Método 1' e 'Método 2', nesse caso, selecionando 2 para o 'Método 2'. O sistema irá pedir a quantidade de caracteres esperados na mensagem, após informar, basta pressionar Enter, e então ele gravará a mensagem durante 10 segundos, exibindo o resultado após esse tempo.

**Divisão de Tarefas para cada membro da equipe:**  
Eduardo Giroto:  
Pedro Frederico:  
Nicolas Nakaie:  
Kauã Lopes:  
Walter Aurélio:  

**Desafios, Problemas e Soluções:**  

**Declaração do Uso de Inteligência Artificial:**  

**Conclusão:**  