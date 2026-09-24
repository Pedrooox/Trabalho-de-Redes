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
    print("=== Comunicação Acústica - Camada Física ===")
    print("1) Transmitir mensagem")
    print("2) Receber mensagem")
    modo = input("Escolha o modo [1/2]: ").strip()

    print("\nMétodo:")
    print("1) Método 1 - Obrigatório (batidas sonoras, quadro de 9 bits, paridade)")
    print("2) Método 2 - Livre escolha (FSK + CRC-8)")
    metodo = input("Escolha o método [1/2]: ").strip()

    if modo == '1':
        texto = input("Digite a mensagem a transmitir: ")
        (method1 if metodo == '1' else method2).transmitir(texto)

    elif modo == '2':
        n_chars = int(input("Quantidade de caracteres esperados na mensagem: ").strip())
        if metodo == '1':
            method1.receber(15.0)
        else:
            method2.receber(n_chars * 16)  # 16 bits (8 dados + 8 CRC) por caractere
    else:
        print("Opção inválida.")
        sys.exit(1)


if __name__ == "__main__":
    menu()
