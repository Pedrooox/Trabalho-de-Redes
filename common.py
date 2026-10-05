"""
Camada Física - Utilitários comuns de áudio
Comunicação acústica entre dispositivos usando a placa de som (meio: ondas sonoras).
"""

import numpy as np

# ---------------- Configurações globais ----------------
SAMPLE_RATE = 44100           # Hz
CANAIS = 1                    # mono

# Tom de sincronismo (marca o início de uma transmissão para os dois métodos)
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


import os
import queue
import sys
import time

try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False

def gerar_click(duracao=0.15, amplitude=1.0):
    """Gera uma 'batida' tipo bumbo (kick drum) bem alta para o Método 1."""
    t = np.linspace(0, duracao, int(SAMPLE_RATE * duracao), endpoint=False)
    # Pitch drop do bumbo: começa em 150Hz cai rápido para 40Hz
    freq_start = 150.0
    freq_end = 40.0
    decay_rate = 30.0
    freqs = freq_end + (freq_start - freq_end) * np.exp(-decay_rate * t)
    phase = 2 * np.pi * np.cumsum(freqs) / SAMPLE_RATE
    
    # Onda principal (senoide)
    onda = np.sin(phase)
    
    # Adiciona um estalo inicial (ruído)
    ruido = np.random.uniform(-1, 1, len(t))
    onda[:int(SAMPLE_RATE*0.01)] += ruido[:int(SAMPLE_RATE*0.01)] * 0.5
    
    # Envelope de amplitude para decaimento percussivo
    envelope = np.exp(-15.0 * t)
    
    som = onda * envelope
    # Normaliza para o volume máximo possível sem distorcer muito
    max_val = np.max(np.abs(som))
    if max_val > 0:
        som = som / max_val
    return (som * amplitude).astype(np.float32)


def tocar(sinal):
    """Reproduz o sinal na saída de áudio padrão (requer sounddevice + placa de som)."""
    import sounddevice as sd
    sd.play(sinal, SAMPLE_RATE)
    sd.wait()


def gravar():
    """Grava do microfone padrão com controle manual.
    Pressione ENTER para começar e ENTER para parar.
    Mostra um histograma do som no terminal."""
    import sounddevice as sd
    os.system("") # Habilita sequências ANSI no cmd/PowerShell do Windows
    q = queue.Queue()
    dados_recentes = np.zeros(2048, dtype=np.float32)
    
    def callback(indata, frames, time_info, status):
        nonlocal dados_recentes
        if status:
            pass # Ignora warnings de underflow/overflow para não poluir a interface
        q.put(indata.copy())
        if len(indata) >= 2048:
            dados_recentes = indata[-2048:, 0]
        else:
            dados_recentes = np.roll(dados_recentes, -len(indata))
            dados_recentes[-len(indata):] = indata[:, 0]
        
    input("[AGUARDANDO] Pressione ENTER para INICIAR a gravação...")
    print("[GRAVANDO] Ouvindo... (Pressione ENTER para PARAR a gravação)")
    
    if HAS_MSVCRT:
        sys.stdout.write("\n" * 10)
        sys.stdout.flush()

    # Abre o fluxo contínuo de áudio
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CANAIS, dtype='float32', callback=callback):
        if HAS_MSVCRT:
            while True:
                if msvcrt.kbhit():
                    if msvcrt.getch() in (b'\r', b'\n'):
                        break
                
                fft_val = np.abs(np.fft.rfft(dados_recentes))
                vol = np.max(np.abs(dados_recentes))
                vol_bars = min(40, int(vol * 40))
                
                bandas = [
                    (0, 500, "0-500Hz  "),
                    (500, 1000, "500-1kHz "),
                    (1000, 2000, "1k-2kHz  "),
                    (2000, 3000, "2k-3kHz  "),
                    (3000, 4500, "3k-4.5kHz"),
                    (4500, 10000, "4.5k-10k ")
                ]
                
                linhas = [f"\033[KVolume: [{'#' * vol_bars}{' ' * (40 - vol_bars)}] {vol:.2f}"]
                linhas.append("\033[K--- Histograma de Frequências ---")
                for ini, fim, nome in bandas:
                    idx_ini = int(ini * len(fft_val) / (SAMPLE_RATE / 2))
                    idx_fim = int(fim * len(fft_val) / (SAMPLE_RATE / 2))
                    val = np.mean(fft_val[idx_ini:idx_fim]) if idx_fim > idx_ini else 0
                    val_norm = val / 15.0 # Sensibilidade
                    bars = min(30, int(val_norm * 30))
                    linhas.append(f"\033[K{nome}: {'█' * bars}")
                
                sys.stdout.write(f"\033[{len(linhas)}A") # Sobe X linhas
                sys.stdout.write("\n".join(linhas) + "\n")
                sys.stdout.flush()
                time.sleep(0.05)
        else:
            input()
            
    # Agrupa os blocos de áudio gravados na fila
    dados = []
    while not q.empty():
        dados.append(q.get())
        
    print("\nGravação finalizada.")
    return np.concatenate(dados).flatten() if dados else np.array([])


# ---------------- Conversão texto <-> bits ----------------

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
