import numpy as np

SAMPLE_RATE = 44100           # Hz
CANAIS = 1                    # mono

PREAMBLE_FREQ = 3000           # Hz
PREAMBLE_DUR = 0.25             # s


def gerar_tom(freq, duracao, amplitude=0.8, fade=0.003):
    """Gera um tom senoidal puro com fade in/out para evitar estalos (cliques) indesejados."""
    t = np.linspace(0, duracao, int(SAMPLE_RATE * duracao), endpoint=False)
    onda = amplitude * np.sin(2 * np.pi * freq * t)
    n_fade = int(SAMPLE_RATE * fade)
    if n_fade > 0 and n_fade * 2 < len(onda):
        janela = np.linspace(0, 1, n_fade)
        onda[:n_fade] *= janela
        onda[-n_fade:] *= janela[::-1]
    return onda.astype(np.float32)


def gerar_silencio(duracao):
    return np.zeros(int(SAMPLE_RATE * duracao), dtype=np.float32)


def gerar_click(duracao=0.03, amplitude=0.9):
    """Gera uma 'batida' curta (ruído de impacto, ex: batida na mesa/palma) para o Método 1."""
    n = int(SAMPLE_RATE * duracao)
    ruido = amplitude * np.random.uniform(-1, 1, n)
    envelope = np.exp(-np.linspace(0, 12, n))   # decaimento percussivo
    return (ruido * envelope).astype(np.float32)


def tocar(sinal):
    """Reproduz o sinal na saída de áudio padrão (requer sounddevice + placa de som)."""
    import sounddevice as sd
    sd.play(sinal, SAMPLE_RATE)
    sd.wait()


def gravar(duracao):
    """Grava 'duracao' segundos do microfone padrão."""
    import sounddevice as sd
    print(f"[GRAVANDO] Ouvindo por {duracao:.1f}s...")
    sinal = sd.rec(int(duracao * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                    channels=CANAIS, dtype='float32')
    sd.wait()
    return sinal.flatten()



def texto_para_bits(texto):
    """Converte uma string (UTF-8) em lista de bits (0/1)."""
    bits = []
    for byte in texto.encode('utf-8'):
        bits.extend(int(b) for b in format(byte, '08b'))
    return bits


def bits_para_texto(bits):
    """Converte uma lista de bits (múltiplo de 8) de volta em string UTF-8."""
    n_bytes = len(bits) // 8
    valores = []
    for i in range(n_bytes):
        byte_bits = bits[i * 8:(i + 1) * 8]
        valores.append(int(''.join(map(str, byte_bits)), 2))
    return bytes(valores).decode('utf-8', errors='replace')


def bit_de_paridade_par(bits8):
    """Retorna o 9º bit (paridade PAR) para 8 bits de dados."""
    return sum(bits8) % 2