"""
Método 2 (Livre Escolha) - Modulação FSK + Detecção de erros via CRC-8
Cada bit vira um tom senoidal de frequência distinta (FSK), permitindo maior
taxa de transmissão que o Método 1 (baseado em batidas), mantendo confiabilidade via CRC-8.
"""

import numpy as np
from common import (SAMPLE_RATE, gerar_tom, gerar_silencio, tocar, gravar,
                     texto_para_bits, bits_para_texto, PREAMBLE_FREQ, PREAMBLE_DUR)

FREQ_BIT0 = 1200         # Hz
FREQ_BIT1 = 2200         # Hz
DURACAO_SIMBOLO = 0.05   # s por bit (bem mais rápido que o Método 1)
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
    return np.concatenate([gerar_tom(FREQ_BIT1 if b else FREQ_BIT0, DURACAO_SIMBOLO) for b in bits])


def transmitir(texto):
    quadros = montar_quadros(texto)
    todos_bits = [b for q in quadros for b in q]
    
    # Gera diretamente o áudio com as frequências FSK (1200/2200 Hz)
    audio = bits_para_audio(todos_bits)
    
    print(f"[MÉTODO 2] Transmitindo {len(quadros)} quadro(s) via FSK...")
    tocar(audio)
    print("[MÉTODO 2] Transmissão concluída.")
    exibir_estatisticas_fsk(texto)


# ---------------- Recepção (demodulação via algoritmo de Goertzel) ----------------

def goertzel_energia(sinal, freq):
    """Estima a energia do sinal na frequência 'freq' (mais leve que uma FFT completa)."""
    n = len(sinal)
    if n == 0:
        return 0.0
    k = int(0.5 + n * freq / SAMPLE_RATE)
    w = (2 * np.pi / n) * k
    coef = 2 * np.cos(w)
    s_prev = s_prev2 = 0.0
    for amostra in sinal:
        s = amostra + coef * s_prev - s_prev2
        s_prev2, s_prev = s_prev, s
    return s_prev2 ** 2 + s_prev ** 2 - coef * s_prev * s_prev2


def demodular_bits(sinal):
    amostras_por_simbolo = int(SAMPLE_RATE * DURACAO_SIMBOLO)
    # Calcula quantos bits cabem no áudio gravado
    n_bits = len(sinal) // amostras_por_simbolo 
    
    bits = []
    for i in range(n_bits):
        ini = i * amostras_por_simbolo
        janela = sinal[ini:ini + amostras_por_simbolo]
        if len(janela) < amostras_por_simbolo:
            break
        e0 = goertzel_energia(janela, FREQ_BIT0)
        e1 = goertzel_energia(janela, FREQ_BIT1)
        bits.append(1 if e1 > e0 else 0)
    return bits


def encontrar_inicio_fsk(sinal):
    janela = int(SAMPLE_RATE * 0.01)  # Janela de 10ms
    passo = int(SAMPLE_RATE * 0.002)  # Avança de 2 em 2ms
    
    # Descobre o nível de ruído da sala no início da gravação
    energias = []
    for i in range(0, min(len(sinal) - janela, int(SAMPLE_RATE * 0.5)), passo):
        trecho = sinal[i:i + janela]
        e0 = goertzel_energia(trecho, FREQ_BIT0)
        e1 = goertzel_energia(trecho, FREQ_BIT1)
        energias.append(max(e0, e1))
    
    ruido_fundo = np.mean(energias) if energias else 0.0001
    limiar_deteccao = max(ruido_fundo * 5, 0.001)

    # Varre o áudio procurando o primeiro som de 1200Hz ou 2200Hz
    for i in range(0, len(sinal) - janela, passo):
        trecho = sinal[i:i + janela]
        e0 = goertzel_energia(trecho, FREQ_BIT0)
        e1 = goertzel_energia(trecho, FREQ_BIT1)
        
        if max(e0, e1) > limiar_deteccao:
            return i

    return 0


def receber():
    sinal = gravar() # Chama sem parâmetros
    
    inicio = encontrar_inicio_fsk(sinal)
    offset_centro = int(SAMPLE_RATE * (DURACAO_SIMBOLO / 2))
    sinal_alinhado = sinal[inicio + offset_centro:]
    
    # Chama a demodulação com o sinal já alinhado
    bits = demodular_bits(sinal_alinhado)
    return validar_e_decodificar(bits)


def validar_e_decodificar(bits):
    dados_validos = []
    quadros_ok = quadros_falha = 0
    i = idx = 0
    
    # 1. Transforma a lista de bits [0, 1, 0...] numa string legível "010..."
    bits_recebidos_str = "".join(str(b) for b in bits)

    while i + 16 <= len(bits):
        dados, crc_recebido = bits[i:i + 8], bits[i + 8:i + 16]
        if crc_recebido == crc8(dados):
            quadros_ok += 1
            dados_validos.extend(dados)
        else:
            quadros_falha += 1
            print(f"[FALHA DE TRANSMISSÃO] Quadro {idx} corrompido (CRC-8 não confere).")
        i += 16
        idx += 1

    texto = bits_para_texto(dados_validos) if dados_validos else ""
    
    # 2. Adiciona os bits na mensagem final
    if quadros_falha == 0 and quadros_ok > 0:
        print(f"[SUCESSO] {quadros_ok} quadro(s) íntegro(s). Mensagem: {texto!r} | Bits: {bits_recebidos_str}")
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
    
    # Tempo total = Preâmbulo + Silêncio de pausa (0.15s) + Bits de dados/CRC
    tempo_overhead = PREAMBLE_DUR + 0.15
    tempo_dados_crc = num_caracteres * bits_por_quadro * DURACAO_SIMBOLO
    tempo_total = tempo_overhead + tempo_dados_crc
    
    
    bps_util = num_bits_dados / tempo_total if tempo_total > 0 else 0

    print("\n--- RESUMO DE DESEMPENHO (MÉTODO 2 - FSK) ---")
    print(f"Tempo Total de Transmissão: {tempo_total:.2f} s")
    print(f"Velocidade Efetiva:  {bps_util:.2f} bps")
    print("--------------------------------------------\n")