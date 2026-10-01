import numpy as np
import method2
from common import SAMPLE_RATE

def testar_metodo2(texto):
    print(f"\n--- Teste Método 2 (sucesso): {texto!r} ---")
    quadros = method2.montar_quadros(texto)
    todos_bits = [b for q in quadros for b in q]
    sinal = method2.bits_para_audio(todos_bits)
    
    # Aplica a sincronização FSK exatamente como na recepção real
    inicio = method2.encontrar_inicio_fsk(sinal)
    offset_centro = int(SAMPLE_RATE * (method2.DURACAO_SIMBOLO / 2))
    sinal_alinhado = sinal[inicio + offset_centro:]
    
    bits = method2.demodular_bits(sinal_alinhado)
    method2.validar_e_decodificar(bits)


def testar_metodo2_com_erro(texto):
    print(f"\n--- Teste Método 2 (com corrupção simulada): {texto!r} ---")
    quadros = method2.montar_quadros(texto)
    todos_bits = [b for q in quadros for b in q]
    
    # Corrompe 1 bit de dados do 1º quadro -> deve falhar no CRC-8
    todos_bits[3] ^= 1  
    sinal = method2.bits_para_audio(todos_bits)
    
    inicio = method2.encontrar_inicio_fsk(sinal)
    offset_centro = int(SAMPLE_RATE * (method2.DURACAO_SIMBOLO / 2))
    sinal_alinhado = sinal[inicio + offset_centro:]
    
    bits = method2.demodular_bits(sinal_alinhado)
    method2.validar_e_decodificar(bits)


def testar_metodo2_incompleto(texto):
    print(f"\n--- Teste Método 2 (quadro incompleto simulado): {texto!r} ---")
    quadros = method2.montar_quadros(texto)
    todos_bits = [b for q in quadros for b in q]
    
    # Gera áudio apenas com os primeiros 20 bits (1 quadro completo de 16 + 4 bits do segundo)
    bits_cortados = todos_bits[:20]
    sinal = method2.bits_para_audio(bits_cortados)
    
    inicio = method2.encontrar_inicio_fsk(sinal)
    offset_centro = int(SAMPLE_RATE * (method2.DURACAO_SIMBOLO / 2))
    sinal_alinhado = sinal[inicio + offset_centro:]
    
    bits = method2.demodular_bits(sinal_alinhado)
    method2.validar_e_decodificar(bits)