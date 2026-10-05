"""
Comunicação Acústica entre Dispositivos - Camada Física (Modelo ISO/OSI)
Ponto de entrada: escolha do método (1 ou 2) e do modo (transmissor/receptor).

Requisitos: pip install numpy sounddevice
"""

import sys
import method1
import method2


def duracao_estimada_metodo1(n_caracteres):
    n_bits = n_caracteres * 9  # 9 bits por caractere (8 dados + 1 paridade)
    tempo_simbolo_pior_caso = (method1.SILENCIO_ENTRE * 2 + 0.03 * 2 + method1.GAP_ENTRE_BATIDAS)
    return n_bits * tempo_simbolo_pior_caso + 1.0


def menu():
    print("\n=== Comunicação Acústica - Camada Física ===")
    print("1) Transmitir mensagem")
    print("2) Receber mensagem")
    print("0) Sair")
    modo = input("Escolha o modo [1/2/0]: ").strip()

    if modo == '0':
        print("Saindo...")
        return

    if modo not in ['1', '2']:
        print("Opção inválida.")
        return

    print("\nMétodo:")
    print("1) Método 1 - Obrigatório (batidas sonoras, quadro de 9 bits, paridade)")
    print("2) Método 2 - Livre escolha (FSK + CRC-8)")
    metodo = input("Escolha o método [1/2]: ").strip()

    if metodo not in ['1', '2']:
        print("Método inválido.")
        return

    if modo == '1':
        texto = input("Digite a mensagem a transmitir: ")
        
        from common import texto_para_bits
        bits = texto_para_bits(texto)
        bits_str = "".join(str(b) for b in bits)
        print(f"\n[INFO] Binário da mensagem a ser transmitida:\n{bits_str}\n")
        
        (method1 if metodo == '1' else method2).transmitir(texto)

    elif modo == '2':
        if metodo == '1':
            method1.receber()
        else:
            method2.receber()


if __name__ == "__main__":
    menu()
