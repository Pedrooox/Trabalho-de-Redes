"""
Método 2 - Modulação usando FSK + Detecção de erros via CRC-8
 -  (Bit 0) -> Tom de 3900 Hz
 -  (Bit 1) -> Tom de 5000 Hz
Demodulação feita através da Análise de Espetro (FFT).
"""

import numpy as np
from common import (SAMPLE_RATE, gerar_tom, tocar, gravar,
                    texto_para_bits, bits_para_texto)

# Frequências 
FREQ_BIT0 = 3900         # Hz para o bit 0 
FREQ_BIT1 = 5000         # Hz para o bit 1 
DURACAO_SIMBOLO = 0.06   # s por bit 
BITS_CRC = 8

# Sequência de preâmbulo (10101011) para acordar o AGC e sincronizar os quadros
PREAMBULO_BITS = [1, 0, 1, 0, 1, 0, 1, 1]


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
    
    # Extrai os bits dos quadros
    bits_dados = [b for q in quadros for b in q]
    
    todos_bits = PREAMBULO_BITS + bits_dados
    
    audio_dados = bits_para_audio(todos_bits)

    audio = np.concatenate([gerar_silencio(0.2), audio_dados, gerar_silencio(0.4)])
    
    print(f"[MÉTODO 2] Transmitindo preâmbulo + {len(quadros)} quadro(s) via FSK...")
    tocar(audio)
    print("[MÉTODO 2] Transmissão concluída.")
    exibir_estatisticas_fsk(texto)


# ---------------- Recepção (demodulação via algoritmo de Goertzel) ----------------

def obter_energias_fsk_fft(sinal):
    """Calcula a energia nas frequências FSK utilizando a FFT (numpy)."""
    if len(sinal) == 0:
        return 0.0, 0.0
    
    espetro = np.fft.rfft(sinal)
    frequencias = np.fft.rfftfreq(len(sinal), 1/SAMPLE_RATE)
    
    energias = np.abs(espetro) ** 2
    
    idx_e0 = np.argmin(np.abs(frequencias - FREQ_BIT0))
    idx_e1 = np.argmin(np.abs(frequencias - FREQ_BIT1))
    
    return energias[idx_e0], energias[idx_e1]


def demodular_bits(sinal):
    """Converte o sinal de áudio novamente em bits analisando janelas de tempo e remove o ruído final."""
    amostras_por_simbolo = int(SAMPLE_RATE * DURACAO_SIMBOLO)
    n_bits = len(sinal) // amostras_por_simbolo 
    
    energias_maximas = []
    bits_decodificados = []
    
    for i in range(n_bits):
        ini = i * amostras_por_simbolo
        janela = sinal[ini:ini + amostras_por_simbolo]
        if len(janela) < amostras_por_simbolo:
            break
            
        e0, e1 = obter_energias_fsk_fft(janela)
        energias_maximas.append(max(e0, e1))
        bits_decodificados.append(1 if e1 > e0 else 0)
        
    if not energias_maximas:
        return []
        
    # Define 5% do volume máximo como "limiar de silêncio"
    limiar_silencio = max(energias_maximas) * 0.05
    
    # Procura qual foi o último bit que superou o limiar de silêncio
    ultimo_idx_valido = 0
    for i in range(len(energias_maximas)):
        if energias_maximas[i] > limiar_silencio:
            ultimo_idx_valido = i
            
    # Retorna apenas até ao último bit audível real
    return bits_decodificados[:ultimo_idx_valido + 1]


def encontrar_inicio_fsk(sinal):
    """Procura no áudio o ponto exato onde a transmissão começa para sincronizar os quadros."""
    janela = int(SAMPLE_RATE * 0.01)
    passo = int(SAMPLE_RATE * 0.002)
    
    energias = []
    for i in range(0, min(len(sinal) - janela, int(SAMPLE_RATE * 0.5)), passo):
        trecho = sinal[i:i + janela]
        e0 = goertzel_energia(trecho, FREQ_BIT0)
        e1 = goertzel_energia(trecho, FREQ_BIT1)
        energias.append(max(e0, e1))
    
    ruido_fundo = np.mean(energias) if energias else 0.0001
    limiar_deteccao = max(ruido_fundo * 5, 0.001)

    for i in range(0, len(sinal) - janela, passo):
        trecho = sinal[i:i + janela]
        e0 = goertzel_energia(trecho, FREQ_BIT0)
        e1 = goertzel_energia(trecho, FREQ_BIT1)
        
        if max(e0, e1) > limiar_deteccao:
            return max(0, i - int(SAMPLE_RATE * 0.002))

    return 0


def receber():
    from common import gerar_silencio
    
    def live_decode(sinal_atual):
        if len(sinal_atual) < int(SAMPLE_RATE * 0.1):
            return []
        inicio = encontrar_inicio_fsk(sinal_atual)
        if inicio == 0 and np.max(np.abs(sinal_atual)) < 0.05:
            return []
        sinal_alinhado = sinal_atual[inicio:]
        return demodular_bits(sinal_alinhado)
        
    sinal = gravar(live_decode)
    
    inicio = encontrar_inicio_fsk(sinal)
    sinal_alinhado = sinal[inicio:]
    
    sinal_alinhado = np.concatenate([sinal_alinhado, gerar_silencio(0.5)])
    
    bits = demodular_bits(sinal_alinhado)
    return validar_e_decodificar(bits)


def validar_e_decodificar(bits):
    """Aplica a regra de deteção de erros (CRC-8) e converte de volta para texto."""
    
    # Busca o preâmbulo para alinhar perfeitamente o início dos dados
    idx_dados = 0
    encontrou_preambulo = False
    
    # Varre a lista de bits procurando o padrão 10101011
    for i in range(len(bits) - len(PREAMBULO_BITS) + 1):
        if bits[i:i + len(PREAMBULO_BITS)] == PREAMBULO_BITS:
            idx_dados = i + len(PREAMBULO_BITS)
            encontrou_preambulo = True
            break
            
    if encontrou_preambulo:
        print(f"[SYNC] Preâmbulo encontrado. Descartando {idx_dados - len(PREAMBULO_BITS)} bits de ruído inicial.")
    else:
        print("[AVISO] Preâmbulo não encontrado de forma nítida. Tentando decodificar desde o início.")
        
    # Corta os bits para começar estritamente após o preâmbulo
    bits_payload = bits[idx_dados:]

    dados_validos = []
    quadros_ok = quadros_falha = 0
    i = idx = 0
    
    bits_recebidos_str = "".join(str(b) for b in bits_payload)

    # Decodifica os quadros a partir do payload
    while i + 16 <= len(bits_payload):
        dados = bits_payload[i:i + 8]
        crc_recebido = bits_payload[i + 8:i + 16]
        
        if crc_recebido == crc8(dados):
            quadros_ok += 1
            dados_validos.extend(dados)
        else:
            quadros_falha += 1
            print(f"[FALHA DE TRANSMISSÃO] Quadro {idx} corrompido (CRC-8 não confere).")
        i += 16
        idx += 1

    bits_sobrando = len(bits_payload) - i
    if bits_sobrando > 0:
        bits_faltantes = 16 - bits_sobrando
        print(f"[AVISO] O quadro {idx + 1} não está completo (faltam {bits_faltantes} bits).")

    texto = bits_para_texto(dados_validos) if dados_validos else ""
    
    # 2. Adiciona os bits na mensagem final
    if quadros_falha == 0 and quadros_ok > 0:
        print(f"[SUCESSO] {quadros_ok} quadro(s) íntegro(s). Mensagem: {texto!r} | Bits: {bits_recebidos_str}")
    elif quadros_ok > 0:
        # Mostra o que conseguiu decodificar mesmo com falhas ou quadros incompletos
        print(f"[RESULTADO PARCIAL] {quadros_ok} quadro(s) OK. Mensagem interceptada: {texto!r} | Bits: {bits_recebidos_str}") 
    else:
        if len(bits_payload) > 0:
            print(f"[RESULTADO] {quadros_ok} quadro(s) OK, {quadros_falha} quadro(s) com FALHA. | Bits: {bits_recebidos_str}")
        else:
            print(f"[RESULTADO] Nenhum bit de dados detectado.")

    return texto, quadros_ok, quadros_falha

# ---------------- Exibição de Desempenho (bps) ----------------

def exibir_estatisticas_fsk(texto_enviado):
    num_caracteres = len(texto_enviado)
    num_bits_dados = num_caracteres * 8
    
    bits_por_quadro = 16  # 8 bits dados + 8 bits CRC-8
    
    tempo_preambulo = len(PREAMBULO_BITS) * DURACAO_SIMBOLO
    
    
    tempo_overhead = 0.60 + tempo_preambulo
    
    tempo_dados_crc = num_caracteres * bits_por_quadro * DURACAO_SIMBOLO
    tempo_total = tempo_overhead + tempo_dados_crc
    
    
    bps_util = num_bits_dados / tempo_total if tempo_total > 0 else 0

    print("\n--- RESUMO DE DESEMPENHO (MÉTODO 2 - FSK) ---")
    print(f"Tempo Total de Transmissão: {tempo_total:.2f} s")
    print(f"Velocidade Efetiva:  {bps_util:.2f} bps")
    print("--------------------------------------------\n")