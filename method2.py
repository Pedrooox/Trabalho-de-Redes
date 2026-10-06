"""
Método 2 - Modulação DTMF (Dual-Tone Multi-Frequency) com FEC Hamming(7,4) estendido (8,4).
Cada quadro de 4 bits de dados é codificado em 7 bits de Hamming + 1 bit de paridade geral (8 bits no total).
Esses 8 bits são enviados como 2 símbolos DTMF (4 bits por símbolo).
"""

import numpy as np
from common import (SAMPLE_RATE, gerar_tom, gerar_silencio, tocar, gravar,
                     texto_para_bits, bits_para_texto)

# Frequências DTMF padrão (linhas e colunas)
ROWS = [697, 770, 852, 941]
COLS = [1209, 1336, 1477, 1633]

PREAMBLE_FREQ = 3000
PREAMBLE_DUR = 0.3
SILENCE_POST_PREAMBLE = 0.1
TONE_DUR = 0.08
GUARD_DUR = 0.03

# ---------------- Funções Auxiliares ----------------

def goertzel_energia(sinal, freq):
    """Estima a energia do sinal na frequência 'freq'."""
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


# ---------------- Transmissão ----------------

def codificar_hamming84(d1, d2, d3, d4):
    """Codifica 4 bits de dados em 8 bits (Hamming 7,4 + paridade par)."""
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p3 = d2 ^ d3 ^ d4
    # Bit 0 é paridade geral de tudo
    p0 = p1 ^ p2 ^ d1 ^ p3 ^ d2 ^ d3 ^ d4
    return [p0, p1, p2, d1, p3, d2, d3, d4]


def montar_quadros(texto):
    bits = texto_para_bits(texto)
    # Zero-padding se necessário
    if len(bits) % 4 != 0:
        bits.extend([0] * (4 - (len(bits) % 4)))
        
    quadros = []
    for i in range(0, len(bits), 4):
        quadros.append(codificar_hamming84(*bits[i:i+4]))
    return quadros


def gerar_dtmf(nibble_bits):
    val = (nibble_bits[0]<<3) | (nibble_bits[1]<<2) | (nibble_bits[2]<<1) | nibble_bits[3]
    row = val // 4
    col = val % 4
    t = np.linspace(0, TONE_DUR, int(SAMPLE_RATE * TONE_DUR), endpoint=False)
    # Média de duas senoides (linha + coluna)
    sinal = (np.sin(2 * np.pi * ROWS[row] * t) + np.sin(2 * np.pi * COLS[col] * t)) / 2
    return sinal


def transmitir(texto):
    quadros = montar_quadros(texto)
    partes = []
    
    # Sincronização inicial
    partes.append(gerar_tom(PREAMBLE_FREQ, PREAMBLE_DUR))
    partes.append(gerar_silencio(SILENCE_POST_PREAMBLE))
    
    for q in quadros:
        n1 = q[0:4]
        n2 = q[4:8]
        partes.append(gerar_dtmf(n1))
        partes.append(gerar_silencio(GUARD_DUR))
        partes.append(gerar_dtmf(n2))
        partes.append(gerar_silencio(GUARD_DUR))
        
    audio = np.concatenate(partes)
    print(f"[MÉTODO 2] Transmitindo via DTMF + Hamming(7,4)...")
    tocar(audio)
    print("[MÉTODO 2] Transmissão concluída.")


# ---------------- Recepção ----------------

def encontrar_inicio_payload(sinal):
    janela_busca = int(SAMPLE_RATE * 0.02)  
    passo = int(SAMPLE_RATE * 0.005)        

    if len(sinal) < janela_busca:
        return -1
        
    # 1. Encontrar o Preâmbulo
    energias_pre = [goertzel_energia(sinal[i:i+janela_busca], PREAMBLE_FREQ) 
                    for i in range(0, len(sinal) - janela_busca, passo)]
    
    if not energias_pre: return -1
    max_e_pre = max(energias_pre)
    if max_e_pre < 0.0001: return -1
        
    limiar_pre = max_e_pre * 0.3
    inicio_preambulo = -1
    for idx, e in enumerate(energias_pre):
        if e >= limiar_pre:
            inicio_preambulo = idx * passo
            break
            
    if inicio_preambulo == -1: return -1
    
    # 2. Procurar o início dos tons DTMF após o silêncio de guarda
    inicio_busca_dtmf = inicio_preambulo + int(SAMPLE_RATE * (PREAMBLE_DUR + SILENCE_POST_PREAMBLE - 0.05))
    restante = sinal[inicio_busca_dtmf:]
    
    energias_dtmf = []
    for i in range(0, len(restante) - janela_busca, passo):
        e = sum(goertzel_energia(restante[i:i+janela_busca], f) for f in ROWS + COLS)
        energias_dtmf.append(e)
        
    if not energias_dtmf: return -1
    max_e_dtmf = max(energias_dtmf)
    if max_e_dtmf < 0.0001: return -1
    
    limiar_dtmf = max_e_dtmf * 0.3
    for idx, e in enumerate(energias_dtmf):
        if e >= limiar_dtmf:
            return inicio_busca_dtmf + (idx * passo)
            
    return -1


def demodular_dtmf(sinal):
    amostras_tom = int(SAMPLE_RATE * TONE_DUR)
    amostras_guarda = int(SAMPLE_RATE * GUARD_DUR)
    passo_simbolo = amostras_tom + amostras_guarda
    
    bits = []
    
    for i in range(0, len(sinal), passo_simbolo):
        janela = sinal[i : i + amostras_tom]
        if len(janela) < amostras_tom // 2:
            break
            
        e_rows = [goertzel_energia(janela, f) for f in ROWS]
        e_cols = [goertzel_energia(janela, f) for f in COLS]
        
        row = np.argmax(e_rows)
        col = np.argmax(e_cols)
        nibble = row * 4 + col
        
        bits.extend([(nibble >> 3) & 1, (nibble >> 2) & 1, (nibble >> 1) & 1, nibble & 1])
        
    return bits


def validar_e_decodificar(bits):
    dados_extraidos = []
    quadros_ok = 0
    quadros_corrigidos = 0
    quadros_falha = 0
    i = 0

    bits_recebidos_str = " ".join(str(b) for b in bits)

    while i + 8 <= len(bits):
        b = bits[i:i+8]
        s1 = b[1] ^ b[3] ^ b[5] ^ b[7]
        s2 = b[2] ^ b[3] ^ b[6] ^ b[7]
        s3 = b[4] ^ b[5] ^ b[6] ^ b[7]
        syndrome = s1 + (s2 << 1) + (s3 << 2)
        
        overall_parity = b[0] ^ b[1] ^ b[2] ^ b[3] ^ b[4] ^ b[5] ^ b[6] ^ b[7]
        
        if syndrome == 0 and overall_parity == 0:
            print("[SUCESSO] Quadro íntegro")
            quadros_ok += 1
            dados_extraidos.extend([b[3], b[5], b[6], b[7]])
            
        elif syndrome != 0 and overall_parity == 1:
            print(f"[SUCESSO] Quadro corrigido (erro no bit {syndrome} corrigido pelo Hamming)")
            quadros_corrigidos += 1
            b_corrigido = list(b)
            b_corrigido[syndrome] ^= 1
            dados_extraidos.extend([b_corrigido[3], b_corrigido[5], b_corrigido[6], b_corrigido[7]])
            
        elif syndrome == 0 and overall_parity == 1:
            print("[SUCESSO] Quadro corrigido (erro no bit de paridade geral ignorado)")
            quadros_corrigidos += 1
            dados_extraidos.extend([b[3], b[5], b[6], b[7]])
            
        else:
            print("[FALHA DE TRANSMISSÃO] Dados corrompidos (erro múltiplo)")
            quadros_falha += 1
            # Inserir zeros para manter o alinhamento dos bytes seguintes
            dados_extraidos.extend([0, 0, 0, 0])
            
        i += 8

    texto = bits_para_texto(dados_extraidos) if dados_extraidos else ""
    
    total_sucesso = quadros_ok + quadros_corrigidos
    print(f"\n[RESULTADO FINAL]")
    print(f"Quadros Íntegros: {quadros_ok}")
    print(f"Quadros Corrigidos: {quadros_corrigidos}")
    print(f"Quadros com Falha: {quadros_falha}")
    print(f"Mensagem: {texto!r} | Bits capturados: {bits_recebidos_str}")

    return texto, total_sucesso, quadros_falha


def receber():
    def live_decode(sinal):
        inicio = encontrar_inicio_payload(sinal)
        if inicio == -1 or inicio >= len(sinal):
            return []
        return demodular_dtmf(sinal[inicio:])

    sinal = gravar(live_decode)

    inicio = encontrar_inicio_payload(sinal)
    if inicio == -1 or inicio >= len(sinal):
        print("[MÉTODO 2] Nenhum preâmbulo detectado.")
        return "", 0, 0

    bits = demodular_dtmf(sinal[inicio:])
    return validar_e_decodificar(bits)
