import numpy as np
from common import (SAMPLE_RATE, gerar_click, gerar_silencio, tocar, gravar,
                     texto_para_bits, bits_para_texto, bit_de_paridade_par,
                     gerar_tom, PREAMBLE_FREQ, PREAMBLE_DUR)

SILENCIO_ENTRE = 0.20    
GAP_ENTRE_BATIDAS = 0.10



def montar_quadros(texto):
    """Quebra o texto em quadros de 9 bits (8 bits de dados + 1 bit de paridade par)."""
    bits = texto_para_bits(texto)
    quadros = []
    for i in range(0, len(bits), 8):
        dados = bits[i:i + 8]
        if len(dados) < 8:
            dados += [0] * (8 - len(dados))
        paridade = bit_de_paridade_par(dados)
        quadros.append(dados + [paridade])
    return quadros


def bit_para_audio(bit):
    if bit == 0:
        simbolo = gerar_click()
    else:
        simbolo = np.concatenate([gerar_click(), gerar_silencio(GAP_ENTRE_BATIDAS), gerar_click()])
    return np.concatenate([gerar_silencio(SILENCIO_ENTRE), simbolo, gerar_silencio(SILENCIO_ENTRE)])


def transmitir(texto):
    quadros = montar_quadros(texto)
    preambulo = gerar_tom(PREAMBLE_FREQ, PREAMBLE_DUR)
    partes = [preambulo, gerar_silencio(0.15)]
    for quadro in quadros:
        for bit in quadro:
            partes.append(bit_para_audio(bit))
    audio = np.concatenate(partes)
    print(f"[MÉTODO 1] Transmitindo {len(quadros)} quadro(s) ({len(texto)} caractere(s))...")
    tocar(audio)
    print("[MÉTODO 1] Transmissão concluída.")



def detectar_batidas(sinal, limiar_rel=0.25, dist_min=0.03):
    """Detecção de onset por energia do sinal: retorna os índices (amostras) dos picos (batidas)."""
    janela = max(1, int(SAMPLE_RATE * 0.005))
    energia = np.convolve(sinal ** 2, np.ones(janela) / janela, mode='same')
    limiar = limiar_rel * np.max(energia) if np.max(energia) > 0 else 0
    acima = energia > limiar
    picos = []
    dist_min_amostras = int(SAMPLE_RATE * dist_min)
    i = 0
    while i < len(acima):
        if acima[i]:
            inicio = i
            while i < len(acima) and acima[i]:
                i += 1
            pico_idx = inicio + int(np.argmax(energia[inicio:i]))
            if not picos or pico_idx - picos[-1] > dist_min_amostras:
                picos.append(pico_idx)
        else:
            i += 1
    return picos


def agrupar_em_bits(sinal):
    """Agrupa as batidas detectadas em slots (símbolos): 1 batida = bit 0, 2 batidas = bit 1."""
    batidas = detectar_batidas(sinal)
    if not batidas:
        return []
    tempos = np.array(batidas) / SAMPLE_RATE
    limiar_gap = GAP_ENTRE_BATIDAS * 3
    slots, atual = [], [tempos[0]]
    for t in tempos[1:]:
        if t - atual[-1] > limiar_gap:
            slots.append(atual)
            atual = [t]
        else:
            atual.append(t)
    slots.append(atual)
    return [0 if len(s) == 1 else 1 for s in slots]


def receber(duracao_estim):
    sinal = gravar(duracao_estim)
    bits = agrupar_em_bits(sinal)
    print(f"[MÉTODO 1] {len(bits)} bit(s)/símbolo(s) detectado(s).")
    return validar_e_decodificar(bits)


def validar_e_decodificar(bits):
    """Recorta os 8 primeiros bits de cada quadro de 9, valida a paridade e reconstrói o texto."""
    dados_validos = []
    quadros_ok = quadros_falha = 0
    i = idx = 0
    while i + 9 <= len(bits):
        quadro = bits[i:i + 9]
        dados, paridade_recebida = quadro[:8], quadro[8]
        if paridade_recebida == bit_de_paridade_par(dados):
            quadros_ok += 1
            dados_validos.extend(dados)
        else:
            quadros_falha += 1
            print(f"[FALHA DE TRANSMISSÃO] Quadro {idx} corrompido (paridade não confere).")
        i += 9
        idx += 1

    texto = bits_para_texto(dados_validos) if dados_validos else ""
    if quadros_falha == 0 and quadros_ok > 0:
        print(f"[SUCESSO] {quadros_ok} quadro(s) íntegro(s). Mensagem: {texto!r}")
    else:
        print(f"[RESULTADO] {quadros_ok} quadro(s) OK, {quadros_falha} quadro(s) com FALHA.")
    return texto, quadros_ok, quadros_falha