import ctypes
import time

import pyautogui
import pyperclip

# Deixe True para acompanhar a automacao mais devagar.
MODO_LENTO_DEBUG = True
FATOR_LENTO = 2.2 if MODO_LENTO_DEBUG else 1.0
pyautogui.PAUSE = 0.12 * FATOR_LENTO


def pausa(segundos):
    time.sleep(segundos * FATOR_LENTO)


def aguardar_clique_direito():
    vk_rbutton = 0x02
    while True:
        if ctypes.windll.user32.GetAsyncKeyState(vk_rbutton) & 0x8000:
            while ctypes.windll.user32.GetAsyncKeyState(vk_rbutton) & 0x8000:
                time.sleep(0.02)
            time.sleep(0.1)
            return
        time.sleep(0.02)


def copiar_campo(coords, campo):
    pyautogui.click(coords[campo])
    pausa(0.25)
    pyautogui.hotkey("ctrl", "a")
    pausa(0.08)
    pyautogui.hotkey("ctrl", "c")
    pausa(0.12)
    return pyperclip.paste().strip()


def parse_valor_numerico(valor_texto):
    valor = valor_texto.strip().replace(" ", "")
    if not valor:
        raise ValueError("Valor vazio")

    valor = "".join(ch for ch in valor if ch.isdigit() or ch == ".")
    if not valor:
        raise ValueError("Valor sem digitos")

    # Ex: "40000" deve ser interpretado como 40.000.
    if valor.isdigit():
        if len(valor) >= 4:
            return float(valor) / 1000.0
        return float(valor)

    # Se vier com mais de um ponto, considera o ultimo como separador decimal.
    if valor.count(".") > 1:
        partes = valor.split(".")
        parte_inteira = "".join(partes[:-1]) or "0"
        parte_decimal = partes[-1] or "000"
    else:
        parte_inteira, parte_decimal = valor.rsplit(".", 1)
        parte_inteira = parte_inteira or "0"
        parte_decimal = parte_decimal or "000"

    return float(f"{parte_inteira}.{parte_decimal}")


def escrever_valor_unitario_mascarado(coords, valor_formatado, valor_visivel_atual):
    pyautogui.click(coords["CAMPO_VALOR_UNIT"])
    pausa(0.25)
    pyautogui.press("end")
    pausa(0.08)

    # Vai para o inicio do valor visivel atual.
    passos_esquerda = len(valor_visivel_atual.strip())
    for _ in range(passos_esquerda):
        pyautogui.press("left")
    pausa(0.08)

    if "." in valor_formatado:
        parte_inteira, parte_decimal = valor_formatado.split(".", 1)
    else:
        parte_inteira, parte_decimal = valor_formatado, "000"

    parte_inteira = parte_inteira if parte_inteira else "0"
    parte_decimal = (parte_decimal + "000")[:3]

    # Se o novo inteiro tiver mais digitos que o atual, recua casas extras
    # para preencher a area antes do ponto (ex.: 9.900 -> 14.850).
    atual_limpo = "".join(ch for ch in valor_visivel_atual if ch.isdigit() or ch == ".")
    if "." in atual_limpo:
        parte_inteira_atual = atual_limpo.split(".", 1)[0]
    else:
        parte_inteira_atual = atual_limpo
    if not parte_inteira_atual:
        parte_inteira_atual = "0"

    casas_extras = max(0, len(parte_inteira) - len(parte_inteira_atual))
    for _ in range(casas_extras):
        pyautogui.press("left")
    pausa(0.05)

    # Regra pedida: nao apagar; sobrescrever como "inteiro + espaco + decimal".
    pyautogui.write(parte_inteira, interval=0.08)
    pyautogui.press("space")
    pyautogui.write(parte_decimal, interval=0.08)
    pausa(0.25)


def atualizar_valor_unitario(coords):
    valor_inicial = copiar_campo(coords, "CAMPO_VALOR_UNIT")
    preco_original = parse_valor_numerico(valor_inicial)
    if preco_original <= 0:
        raise ValueError(f"Valor original invalido ({preco_original})")

    preco_venda_alvo = preco_original * 1.5
    valor_formatado = f"{preco_venda_alvo:.3f}"
    print(f"Valor inicial '{valor_inicial}' -> alvo '{valor_formatado}'")

    for tentativa in range(1, 4):
        try:
            valor_visivel = copiar_campo(coords, "CAMPO_VALOR_UNIT")
            escrever_valor_unitario_mascarado(coords, valor_formatado, valor_visivel)

            valor_confirmado = copiar_campo(coords, "CAMPO_VALOR_UNIT")
            preco_confirmado = parse_valor_numerico(valor_confirmado)

            tolerancia = max(0.001, abs(preco_venda_alvo) * 0.02)
            if abs(preco_confirmado - preco_venda_alvo) <= tolerancia:
                print(
                    f"OK (tentativa {tentativa}): {preco_original:.3f} -> "
                    f"{preco_confirmado:.3f} (confirmado: '{valor_confirmado}')"
                )
                return preco_confirmado

            raise ValueError(
                f"Confirmacao divergente: esperado {valor_formatado}, "
                f"recebido '{valor_confirmado}'"
            )
        except Exception as e:
            print(f"[warn] Falha na tentativa {tentativa}: {e}")
            pausa(0.7)

    raise RuntimeError("Nao foi possivel atualizar o valor unitario apos 3 tentativas.")


def calibrar_sistema():
    print("\n" + "=" * 50)
    print("   MODO DE CALIBRAGEM - CAMPO UNITARIO")
    print("=" * 50)
    print("Aponte o mouse para [ CAMPO_VALOR_UNIT ] e clique com o botao direito.\n")

    aguardar_clique_direito()
    coords = {"CAMPO_VALOR_UNIT": pyautogui.position()}
    print(f"Coordenada salva: {coords['CAMPO_VALOR_UNIT']}")

    print("\nIniciando teste em 2 segundos...")
    pausa(2.0)
    return coords


def trabalhar(coords):
    preco_final = atualizar_valor_unitario(coords)
    print(f"Teste concluido. Valor final: {preco_final:.3f}")


if __name__ == "__main__":
    coordenadas = calibrar_sistema()
    trabalhar(coordenadas)
