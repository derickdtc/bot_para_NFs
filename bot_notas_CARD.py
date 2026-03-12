import ctypes
import json
import random
import string
import time
from datetime import datetime, timedelta
from pathlib import Path

import pyautogui
import pyperclip

# --- CONFIGURACOES ---
TEMPO_DE_TRABALHO_MINUTOS = 10
PAUSA_MINIMA = 5
PAUSA_MAXIMA = 10
META_VALOR_NOTA = (50, 200)
MARGEM_SUPERIOR_META = 100
ARQUIVO_COORDENADAS = Path(__file__).with_name("coordenadas.json")
PONTOS_CALIBRAGEM = [
    "BTN_ABRIR_NFCE",
    "BTN_NOMES_EM_BRANCO",
    "BTN_NOMES_EM_BRANCO2",
    "BTN_OK_JANELAS",
    "LISTA_DE_NOTAS",
    "BTN_INCLUIR_ITENS",
    "BTN_REMOVER_ITENS",
    "CAMPO_BUSCA_PRODUTO",
    "PRIMEIRO_ITEM_LISTA",
    "CAMPO_QUANTIDADE",
    "CAMPO_VALOR_UNIT",
    "BTN_ITEM_PARA_IMPOSTOS",
    "CAMPO_CSOSN",
    "CAMPO_CFOP",
    "CHECKBOX_TRIBUTO_TODOS",
    "BTN_SALVAR_IMPOSTOS",
    "BTN_CONFIRMAR_IMPOSTOS",
    "BTN_TRANSMITIR",
    "CAMPO_DINHEIRO",
    "CAMPO_PAGAMENTO",
    "OPCAO_CARTAO_CREDITO",
    "BTN_FECHAR_PREVIEW",
]

# Deixe True para acompanhar a automacao mais devagar.
MODO_LENTO_DEBUG = True
FATOR_LENTO = 1.5 if MODO_LENTO_DEBUG else 1.0
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


def parse_valor_numerico(valor_texto):
    valor = valor_texto.strip().replace(" ", "")
    if not valor:
        raise ValueError("Valor vazio")

    # Sistema usa apenas '.' como separador decimal.
    valor = "".join(ch for ch in valor if ch.isdigit() or ch == ".")
    if not valor:
        raise ValueError("Valor sem digitos")

    # Alguns campos podem copiar sem separador decimal (ex: "29900" para 29.900).
    if valor.isdigit():
        if len(valor) >= 4:
            return float(valor) / 1000.0, ".", 3
        return float(valor), ".", 0

    # Se vier com mais de um ponto, considera o ultimo como separador decimal.
    if valor.count(".") > 1:
        partes = valor.split(".")
        parte_inteira = "".join(partes[:-1]) or "0"
        parte_decimal = partes[-1] or "000"
    else:
        parte_inteira, parte_decimal = valor.rsplit(".", 1)
        if not parte_inteira:
            parte_inteira = "0"
        if not parte_decimal:
            parte_decimal = "000"
    casas_decimais = len(parte_decimal)
    preco = float(f"{parte_inteira}.{parte_decimal}")
    return preco, ".", casas_decimais


def formatar_valor(preco, separador_decimal, casas_decimais):
    _ = separador_decimal
    return f"{preco:.{casas_decimais}f}"


def copiar_campo(coords, campo):
    pyautogui.click(coords[campo])
    pausa(0.25)
    pyautogui.hotkey("ctrl", "a")
    pausa(0.08)
    pyautogui.hotkey("ctrl", "c")
    pausa(0.12)
    return pyperclip.paste().strip()


def escrever_campo(coords, campo, valor):
    pyautogui.click(coords[campo])
    pausa(0.25)
    pyautogui.hotkey("ctrl", "a")
    pausa(0.08)
    pyautogui.press("backspace")
    pausa(0.08)
    pyperclip.copy(str(valor))
    pyautogui.hotkey("ctrl", "v")
    pausa(0.25)


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

    # Sobrescreve por cima no padrao: inteiro + espaco + decimal.
    pyautogui.write(parte_inteira, interval=0.08)
    pyautogui.press("space")
    pyautogui.write(parte_decimal, interval=0.08)
    pausa(0.25)


def atualizar_valor_unitario(coords):
    valor_inicial = copiar_campo(coords, "CAMPO_VALOR_UNIT")
    preco_original, _, _ = parse_valor_numerico(valor_inicial)
    if preco_original <= 0:
        raise ValueError(f"Valor original invalido ({preco_original})")

    preco_venda_alvo = preco_original * 1.5
    valor_formatado = formatar_valor(preco_venda_alvo, ".", 3)
    print(
        f"   Valor unit inicial: '{valor_inicial}' -> "
        f"alvo {preco_venda_alvo:.3f}"
    )

    for tentativa in range(1, 4):
        try:
            valor_visivel = copiar_campo(coords, "CAMPO_VALOR_UNIT")
            escrever_valor_unitario_mascarado(coords, valor_formatado, valor_visivel)

            valor_confirmado = copiar_campo(coords, "CAMPO_VALOR_UNIT")
            preco_confirmado, _, _ = parse_valor_numerico(valor_confirmado)

            tolerancia = max(0.001, abs(preco_venda_alvo) * 0.02)
            if abs(preco_confirmado - preco_venda_alvo) <= tolerancia:
                print(
                    f"   Valor unit OK (tentativa {tentativa}): "
                    f"{preco_original:.3f} -> {preco_confirmado:.3f}"
                )
                return preco_confirmado

            raise ValueError(
                "Escala incorreta apos escrita "
                f"('{valor_formatado}' -> '{valor_confirmado}')"
            )
        except Exception as e:
            print(f"   [warn] Falha ao atualizar valor unit (tentativa {tentativa}): {e}")
            pausa(0.7)

    # Fallback para nao deixar o item zerado.
    valor_fallback = formatar_valor(15.0, ".", 3)
    valor_visivel = copiar_campo(coords, "CAMPO_VALOR_UNIT")
    escrever_valor_unitario_mascarado(coords, valor_fallback, valor_visivel)
    print("   [warn] Usando valor fallback 15.000 para evitar item com valor zero.")
    return 15.0


def atualizar_quantidade(coords, qtd):
    for tentativa in range(1, 5):
        escrever_campo(coords, "CAMPO_QUANTIDADE", str(qtd))
        valor_lido = copiar_campo(coords, "CAMPO_QUANTIDADE")
        if valor_lido.startswith(str(qtd)):
            print(f"   Quantidade OK (tentativa {tentativa}): {valor_lido}")
            return True
        print(f"   [warn] Quantidade nao confirmada (tentativa {tentativa}): '{valor_lido}'")
        pausa(0.5)
    return False


def limpar_e_preencher_campo(coords, campo, valor):
    escrever_campo(coords, campo, valor)


def selecionar_item_para_impostos(coords):
    pyautogui.keyUp("ctrl")
    pyautogui.keyUp("shift")
    pyautogui.keyUp("alt")
    pyautogui.click(coords["BTN_ITEM_PARA_IMPOSTOS"])
    print("   Item selecionado para aplicacao de impostos.")
    pausa(0.4)


def abrir_item_para_impostos(coords):
    selecionar_item_para_impostos(coords)
    # Apos remocao o primeiro clique pode ser absorvido pelo fechamento do popup.
    pyautogui.click(coords["BTN_ITEM_PARA_IMPOSTOS"])
    pausa(0.2)
    pyautogui.press("enter")
    pausa(0.6)


def abrir_nota_para_transmissao(coords):
    selecionar_ultima_nota(coords)
    # Abre a nota selecionada na lista sem usar o botao de impostos.
    pyautogui.press("enter")
    pausa(2.4)


def selecionar_ultima_nota(coords):
    pyautogui.keyUp("ctrl")
    pyautogui.keyUp("shift")
    pyautogui.keyUp("alt")
    pyautogui.click(coords["LISTA_DE_NOTAS"])
    pausa(0.35)
   # pyautogui.click(coords["LISTA_DE_NOTAS"])
    #pausa(0.2)

    # Forca navegacao para o fim por teclado.
    pyautogui.hotkey("ctrl", "end")
    pausa(0.12)
    pyautogui.press("end")
    pausa(0.12)
    pyautogui.hotkey("ctrl", "end")
    pausa(0.12)
    pyautogui.press("end")
    print("   Ultima nota selecionada.")
    pausa(0.12)
    

 


def normalizar_posicao(posicao):
    if hasattr(posicao, "x") and hasattr(posicao, "y"):
        return int(posicao.x), int(posicao.y)
    if isinstance(posicao, (tuple, list)) and len(posicao) >= 2:
        return int(posicao[0]), int(posicao[1])
    raise ValueError(f"Posicao invalida: {posicao}")


def salvar_coordenadas(coords):
    payload = {}
    for nome, posicao in coords.items():
        x, y = normalizar_posicao(posicao)
        payload[nome] = {"x": x, "y": y}

    with ARQUIVO_COORDENADAS.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"Coordenadas salvas em: {ARQUIVO_COORDENADAS}")


def carregar_coordenadas():
    if not ARQUIVO_COORDENADAS.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {ARQUIVO_COORDENADAS}")

    with ARQUIVO_COORDENADAS.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    coords = {}
    for nome, posicao in payload.items():
        if isinstance(posicao, dict):
            x = int(posicao["x"])
            y = int(posicao["y"])
        elif isinstance(posicao, (list, tuple)) and len(posicao) >= 2:
            x = int(posicao[0])
            y = int(posicao[1])
        else:
            raise ValueError(f"Formato invalido para '{nome}': {posicao}")
        coords[nome] = (x, y)
    return coords


def coordenadas_faltantes(coords):
    return [ponto for ponto in PONTOS_CALIBRAGEM if ponto not in coords]


def capturar_coordenadas(pontos, coords_iniciais=None):
    if not pontos:
        return dict(coords_iniciais or {})

    print("\n" + "=" * 50)
    print("   MODO DE CALIBRAGEM")
    print("=" * 50)
    print("Aponte o mouse para o local e clique com o botao direito.\n")

    coords = dict(coords_iniciais or {})
    for ponto in pontos:
        print(f"-> Aponte para: [ {ponto} ] e clique com o botao direito.")
        aguardar_clique_direito()
        pos = pyautogui.position()
        coords[ponto] = (int(pos.x), int(pos.y))
        print(f"   Salvo: {coords[ponto]}")
        pausa(0.4)
    return coords


def escolher_ponto_para_atualizar():
    print("\nPontos disponiveis para atualizar:")
    for indice, ponto in enumerate(PONTOS_CALIBRAGEM, start=1):
        print(f"{indice:2d}. {ponto}")
    print(" 0. NOVO_PONTO_CUSTOM")

    escolha = input("Escolha numero ou nome do ponto: ").strip()
    if escolha == "0":
        novo_nome = input("Nome do novo ponto: ").strip().upper().replace(" ", "_")
        if not novo_nome:
            raise ValueError("Nome do novo ponto nao pode ser vazio.")
        return novo_nome
    if escolha.isdigit():
        indice = int(escolha)
        if 1 <= indice <= len(PONTOS_CALIBRAGEM):
            return PONTOS_CALIBRAGEM[indice - 1]
        raise ValueError("Indice fora do intervalo.")

    nome = escolha.upper().replace(" ", "_")
    if not nome:
        raise ValueError("Ponto invalido.")
    return nome


def calibrar_sistema():
    coords = capturar_coordenadas(PONTOS_CALIBRAGEM)
    salvar_coordenadas(coords)
    print("\nCalibragem concluida. Iniciando em 3 segundos...")
    pausa(3)
    return coords


def preparar_coordenadas():
    while True:
        print("\n" + "=" * 50)
        print("Coordenadas")
        print("=" * 50)
        print("1) Usar coordenadas salvas")
        print("2) Recalibrar todas")
        print("3) Adicionar/atualizar uma coordenada")
        print("4) Sair")
        opcao = input("Escolha [1/2/3/4]: ").strip()

        if opcao == "1":
            try:
                coords = carregar_coordenadas()
            except Exception as e:
                print(f"[warn] Nao foi possivel carregar coordenadas: {e}")
                continue

            faltantes = coordenadas_faltantes(coords)
            if faltantes:
                print(f"[warn] Coordenadas faltando: {', '.join(faltantes)}")
                print("Capturando apenas os pontos faltantes...")
                coords = capturar_coordenadas(faltantes, coords)
                salvar_coordenadas(coords)
            return coords

        if opcao == "2":
            return calibrar_sistema()

        if opcao == "3":
            try:
                coords = carregar_coordenadas()
            except Exception:
                coords = {}

            try:
                ponto = escolher_ponto_para_atualizar()
            except Exception as e:
                print(f"[warn] {e}")
                continue

            print(f"-> Aponte para: [ {ponto} ] e clique com o botao direito.")
            aguardar_clique_direito()
            pos = pyautogui.position()
            coords[ponto] = (int(pos.x), int(pos.y))
            print(f"   Atualizado: {ponto} = {coords[ponto]}")
            salvar_coordenadas(coords)

            faltantes = coordenadas_faltantes(coords)
            if faltantes:
                print(f"[warn] Ainda faltam pontos para execucao: {', '.join(faltantes)}")
                print("Use opcao 1 ou 2 para completar.")
                continue
            return coords

        if opcao == "4":
            raise SystemExit("Execucao cancelada pelo usuario.")

        print("[warn] Opcao invalida.")

def remover_item(coords):
    selecionar_item_para_impostos(coords)
    pyautogui.press("end")
    pausa(0.12)
    pyautogui.click(coords["BTN_REMOVER_ITENS"])
    pausa(0.4)





def trabalhar(coords):
    ITENS_POR_NOTA = 0

    pyautogui.click(coords["BTN_ABRIR_NFCE"])
    pausa(1.5)
    pyautogui.click(coords["BTN_NOMES_EM_BRANCO"])
    pausa(0.5)
    pyautogui.click(coords["BTN_NOMES_EM_BRANCO2"])
    pausa(0.5)
    pyautogui.press("enter")
    pausa(0.8)

    selecionar_ultima_nota(coords)
    pausa(0.4)

    valor_atual_nota = 0
    meta = random.randint(META_VALOR_NOTA[0], META_VALOR_NOTA[1])
    limite_superior = meta + MARGEM_SUPERIOR_META
    print(
        f"--- Nova Nota. Meta: R$ {meta:.2f} "
        f"(faixa valida ate R$ {limite_superior:.2f}) ---"
    )

    while valor_atual_nota < meta:
        pyautogui.click(coords["BTN_INCLUIR_ITENS"])
        pausa(2.2)

        letras_permitidas = [letra for letra in string.ascii_lowercase if letra not in ("q", "x")]
        letra_aleatoria = random.choice(letras_permitidas)
        pyautogui.click(coords["CAMPO_BUSCA_PRODUTO"])
        pausa(0.25)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
        pyautogui.write(letra_aleatoria, interval=0.08)
        pyautogui.press("enter")
        pausa(2.1)

        pyautogui.click(coords["PRIMEIRO_ITEM_LISTA"])
        pausa(0.6)

        descidas = random.randint(0, 18)
        for _ in range(descidas):
            pyautogui.press("down")
            pausa(0.15)

        pyautogui.press("enter")
        pausa(2.0)

        qtd = random.randint(1, 5)
        qtd_ok = atualizar_quantidade(coords, qtd)
        if not qtd_ok:
            print("   [warn] Quantidade nao confirmou, seguindo com valor digitado.")

        preco_venda = atualizar_valor_unitario(coords)

        pyautogui.press("enter")
        pausa(2.0)

        valor_total_item = qtd * preco_venda
        valor_atual_nota += valor_total_item
        print(
            f"   Item add (Letra '{letra_aleatoria}', x{qtd}) - "
            f"Total acumulado: {valor_atual_nota:.2f}"
        )

        ITENS_POR_NOTA += 1

        if valor_atual_nota >= meta:
            if valor_atual_nota <= limite_superior:
                print(
                    f"   Meta atingida dentro da margem: "
                    f"{valor_atual_nota:.2f} em [{meta:.2f}, {limite_superior:.2f}]"
                )
            elif ITENS_POR_NOTA == 1:
                print(" O limite superior foi ultrapassado com apenas 1 item. Aceitando nota acima do limite por questões de viabilidade.")         
                     
                 
            break

        pausa(1.0)

    if valor_atual_nota > limite_superior and ITENS_POR_NOTA > 1:
         remover_item(coords)
         print("   Valor ultrapassou o limite superior, item removido.")
         #pyautogui.click(coords["BTN_ITEM_PARA_IMPOSTOS"])   

    print("   Aplicando impostos...")
    abrir_item_para_impostos(coords)
    limpar_e_preencher_campo(coords, "CAMPO_CSOSN", "102")
    limpar_e_preencher_campo(coords, "CAMPO_CFOP", "5102")

    pyautogui.click(coords["CHECKBOX_TRIBUTO_TODOS"])
    pausa(0.8)
    pyautogui.click(coords["BTN_SALVAR_IMPOSTOS"])
    pausa(1.2)
    pyautogui.click(coords["BTN_CONFIRMAR_IMPOSTOS"])
    pausa(1.0)

    print("   Finalizando nota...")
    abrir_nota_para_transmissao(coords)

    pyautogui.click(coords["CAMPO_PAGAMENTO"])
    pausa(0.6)
    pyautogui.click(coords["OPCAO_CARTAO_CREDITO"])
    pausa(0.8)

    pyautogui.click(coords["CAMPO_DINHEIRO"])
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")

    pyautogui.click(coords["BTN_TRANSMITIR"])
    pausa(1.0)
    pyautogui.click(coords["BTN_FECHAR_PREVIEW"])
    print("Nota finalizada com sucesso.")


if __name__ == "__main__":
    coords = preparar_coordenadas()

    inicio = datetime.now()
    fim = inicio + timedelta(minutes=TEMPO_DE_TRABALHO_MINUTOS)

    print(f"\nIniciando execucao. Termino previsto: {fim.strftime('%H:%M')}")

    while datetime.now() < fim:
        try:
            trabalhar(coords)
            pausa_aleatoria = random.randint(PAUSA_MINIMA, PAUSA_MAXIMA)
            print(f"Aguardando {pausa_aleatoria} segundos para a proxima nota...")
            pausa(pausa_aleatoria)
        except KeyboardInterrupt:
            print("\nExecucao interrompida.")
            break
        except Exception as e:
            print(f"Erro: {e}. Retomando em 10 segundos...")
            pausa(10)
