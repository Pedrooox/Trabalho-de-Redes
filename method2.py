"""
Método 2 - Modulação "Morse Frequencial" (2-FSK) + Detecção de erros via CRC-8
Adaptação do Código Morse para alta velocidade:
 - "Ponto" (Bit 0) -> Tom de 2000 Hz
 - "Traço" (Bit 1) -> Tom de 3500 Hz
Demodulação feita através da Análise de Espetro (FFT).
"""

import numpy as np
from common import (SAMPLE_RATE, gerar_tom, tocar, gravar,
                     texto_para_bits, bits_para_texto, PREAMBLE_DUR)

# Frequências do "Morse Frequencial"
FREQ_BIT0 = 4000         # Hz para o bit 0 (Ponto)
FREQ_BIT1 = 5000         # Hz para o bit 1 (Traço)
DURACAO_SIMBOLO = 0.08   # s por bit (40 ms, muito mais rápido que o Método 1)
BITS_CRC = 8


def crc8(dados_bits):
    """Calcula o CRC-8 (polinômio 0x07) sobre uma lista de bits de dados."""
    poly = 0x07
    reg = 0
    for bit in dados_bits + [0] * 8:
        reg = ((reg << 1) | bit) & 0x1FF
        if reg & 0x100:
            reg ^= (poly << 1)
            reg &= 0x1FF
    return [int(b) for b in format(reg & 0xFF, '08b')]


# ---------------- Transmissão ----------------

def montar_quadros(texto):
    """Cada quadro = 8 bits de dados + 8 bits de CRC-8 (16 bits por quadro)."""
    bits = texto_para_bits(texto)
    quadros = []
    for i in range(0, len(bits), 8):
        dados = bits[i:i + 8]
        if len(dados) < 8:
            dados += [0] * (8 - len(dados))
        quadros.append(dados + crc8(dados))
    return quadros


def bits_para_audio(bits):
    """Mapeia os bits para os tons acústicos correspondentes."""
    return np.concatenate([gerar_tom(FREQ_BIT1 if b else FREQ_BIT0, DURACAO_SIMBOLO) for b in bits])


def transmitir(texto):
    from common import gerar_silencio
    quadros = montar_quadros(texto)
    todos_bits = [b for q in quadros for b in q]
    
    # Gera o áudio com as frequências do Morse Adaptado
    audio_dados = bits_para_audio(todos_bits)
    
    # FIX: Envelopa os dados com silêncio (0.2s início, 0.4s final)
    audio = np.concatenate([gerar_silencio(0.2), audio_dados, gerar_silencio(0.4)])
    
    print(f"[MÉTODO 2] Transmitindo {len(quadros)} quadro(s) via Morse/FSK...")
    tocar(audio)
    print("[MÉTODO 2] Transmissão concluída.")
    exibir_estatisticas_fsk(texto)


# ---------------- Recepção (Demodulação via FFT) ----------------

def obter_energias_fsk_fft(sinal):
    """Calcula a energia nas frequências FSK utilizando a FFT (numpy)."""
    if len(sinal) == 0:
        return 0.0, 0.0
    
    # Calcula a FFT para sinais reais
    espetro = np.fft.rfft(sinal)
    frequencias = np.fft.rfftfreq(len(sinal), 1/SAMPLE_RATE)
    
    # Eleva a magnitude ao quadrado para obter a energia
    energias = np.abs(espetro) ** 2
    
    # Encontra os índices (bins) mais próximos das frequências dos bits 0 e 1
    idx_e0 = np.argmin(np.abs(frequencias - FREQ_BIT0))
    idx_e1 = np.argmin(np.abs(frequencias - FREQ_BIT1))
    
    return energias[idx_e0], energias[idx_e1]


def demodular_bits(sinal):
    """Converte o sinal de áudio novamente em bits analisando janelas de tempo."""
    amostras_por_simbolo = int(SAMPLE_RATE * DURACAO_SIMBOLO)
    # Calcula quantos bits cabem no áudio gravado
    n_bits = len(sinal) // amostras_por_simbolo 
    
    bits = []
    for i in range(n_bits):
        ini = i * amostras_por_simbolo
        janela = sinal[ini:ini + amostras_por_simbolo]
        if len(janela) < amostras_por_simbolo:
            break
            
        e0, e1 = obter_energias_fsk_fft(janela)
        # Se a energia em 3500Hz for maior, é um Traço (Bit 1), senão é Ponto (Bit 0)
        bits.append(1 if e1 > e0 else 0)
    return bits


def encontrar_inicio_fsk(sinal):
    """Procura no áudio o ponto exato onde a transmissão começa para sincronizar os quadros."""
    janela = int(SAMPLE_RATE * 0.01)  # Janela de 10ms
    passo = int(SAMPLE_RATE * 0.002)  # Avança de 2 em 2ms
    
    # Descobre o nível de ruído da sala no início da gravação
    energias = []
    for i in range(0, min(len(sinal) - janela, int(SAMPLE_RATE * 0.5)), passo):
        trecho = sinal[i:i + janela]
        e0, e1 = obter_energias_fsk_fft(trecho)
        energias.append(max(e0, e1))
    
    ruido_fundo = np.mean(energias) if energias else 0.0001
    limiar_deteccao = max(ruido_fundo * 5, 0.001)

    # Varre o áudio procurando o primeiro som do transmissor
    for i in range(0, len(sinal) - janela, passo):
        trecho = sinal[i:i + janela]
        e0, e1 = obter_energias_fsk_fft(trecho)
        
        if max(e0, e1) > limiar_deteccao:
            return i

    return 0


def receber():
    from common import gerar_silencio
    sinal = gravar() # Aguarda o utilizador gravar o áudio
    
    inicio = encontrar_inicio_fsk(sinal)
    sinal_alinhado = sinal[inicio:]
    
    # FIX: Adiciona 0.5s de silêncio (zeros) no final do array.
    # Garante que a janela do último bit nunca seja cortada por falta de amostras.
    sinal_alinhado = np.concatenate([sinal_alinhado, gerar_silencio(0.5)])
    
    # Chama a demodulação via FFT com o sinal já alinhado e estendido
    bits = demodular_bits(sinal_alinhado)
    return validar_e_decodificar(bits)


def validar_e_decodificar(bits):
    """Aplica a regra de deteção de erros (CRC-8) e converte de volta para texto."""
    dados_validos = []
    quadros_ok = quadros_falha = 0
    i = idx = 0
    
    bits_recebidos_str = "".join(str(b) for b in bits)

    while i + 16 <= len(bits):
        dados, crc_recebido = bits[i:i + 8], bits[i + 8:i + 16]
        # Validação da integridade usando a lógica CRC-8
        if crc_recebido == crc8(dados):
            quadros_ok += 1
            dados_validos.extend(dados)
        else:
            quadros_falha += 1
            print(f"[FALHA DE TRANSMISSÃO] Quadro {idx} corrompido (CRC-8 não confere).")
        i += 16
        idx += 1

    bits_sobrando = len(bits) - i
    if bits_sobrando > 0:
        bits_faltantes = 16 - bits_sobrando
        print(f"[AVISO] O quadro {idx + 1} não está completo (faltam {bits_faltantes} bits).")

    texto = bits_para_texto(dados_validos) if dados_validos else ""
    
    if quadros_falha == 0 and quadros_ok > 0:
        print(f"[SUCESSO] {quadros_ok} quadro(s) íntegro(s). Mensagem: {texto!r} | Bits: {bits_recebidos_str}")
    elif quadros_ok > 0:
        print(f"[RESULTADO PARCIAL] {quadros_ok} quadro(s) OK. Mensagem interceptada: {texto!r} | Bits: {bits_recebidos_str}") 
    else:
        if len(bits) > 0:
            print(f"[RESULTADO] {quadros_ok} quadro(s) OK, {quadros_falha} quadro(s) com FALHA. | Bits: {bits_recebidos_str}")
        else:
            print(f"[RESULTADO] Nenhum bit detectado.")

    return texto, quadros_ok, quadros_falha


# ---------------- Exibição de Desempenho (bps) ----------------

def exibir_estatisticas_fsk(texto_enviado):
    num_caracteres = len(texto_enviado)
    num_bits_dados = num_caracteres * 8
    
    bits_por_quadro = 16  # 8 bits dados + 8 bits CRC-8
    
    tempo_overhead = PREAMBLE_DUR + 0.15
    tempo_dados_crc = num_caracteres * bits_por_quadro * DURACAO_SIMBOLO
    tempo_total = tempo_overhead + tempo_dados_crc
    
    bps_util = num_bits_dados / tempo_total if tempo_total > 0 else 0

    print("\n--- RESUMO DE DESEMPENHO (MÉTODO 2 - MORSE/FSK) ---")
    print(f"Tempo Total de Transmissão: {tempo_total:.2f} s")
    print(f"Velocidade Efetiva (Payload):  {bps_util:.2f} bps")
    print("--------------------------------------------------\n")
