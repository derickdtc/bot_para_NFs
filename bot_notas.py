import pyautogui
import keyboard
import time
import random
import string
import pyperclip
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES ---
TEMPO_DE_TRABALHO_MINUTOS = 60 
PAUSA_MINIMA = 60               
PAUSA_MAXIMA = 120              
META_VALOR_NOTA = (50, 300)     

def calibrar_sistema():
    print("\n" + "="*50)
    print("   MODO DE CALIBRAGEM")
    print("="*50)
    print("Aponte o mouse para o local e aperte ESPAÇO.\n")
    
    pontos = [
        #"BTN_NOMES_EM_BRANCO",
        "BTN_ABRIR_NFCE",          
        "BTN_OK_JANELAS",          
        "LISTA_DE_NOTAS",          
        "BTN_INCLUIR_ITENS",       
        "CAMPO_BUSCA_PRODUTO",     
        "PRIMEIRO_ITEM_LISTA",     
        "CAMPO_QUANTIDADE",        
        "CAMPO_VALOR_UNIT",        
        "CAMPO_CSOSN",             
        "CAMPO_CFOP",              
        "CHECKBOX_TRIBUTO_TODOS",  
        "BTN_SALVAR_IMPOSTOS",
        #"BTN_CONFIRMAR_IMPOSTOS",
        # "BTN_SELECIONAR_NOTA",     
        "BTN_TRANSMITIR",          
        "CAMPO_DINHEIRO",          
        "CAMPO_PAGAMENTO",         
        "OPCAO_CARTAO_CREDITO",    
        "BTN_FECHAR_PREVIEW"       
    ]
    
    coords = {}
    for ponto in pontos:
        print(f"-> Aponte para: [ {ponto} ] e tecle ESPAÇO.")
        keyboard.wait('space')
        coords[ponto] = pyautogui.position()
        print(f"   Salvo: {coords[ponto]}")
        time.sleep(0.5) 
        
    print("\n✅ Calibragem concluída! Iniciando em 5 segundos...")
    time.sleep(5)
    return coords

def trabalhar(coords):
    # 1. Abrir e Selecionar Nota
    pyautogui.click(coords['BTN_ABRIR_NFCE'])
    time.sleep(2)
    pyautogui.press('enter') 
    
    pyautogui.click(coords['LISTA_DE_NOTAS'])
    pyautogui.press('end')
    time.sleep(1)
    
    # 2. Loop de Inclusão de Itens
    valor_atual_nota = 0
    meta = random.randint(META_VALOR_NOTA[0], META_VALOR_NOTA[1])
    print(f"--- Nova Nota. Meta: R$ {meta:.2f} ---")
    
    while valor_atual_nota < meta:
        pyautogui.click(coords['BTN_INCLUIR_ITENS'])
        time.sleep(1.5)
        
        # GERA UMA LETRA ALEATÓRIA
        letra_aleatoria = random.choice(string.ascii_lowercase)
        
        pyautogui.click(coords['CAMPO_BUSCA_PRODUTO'])
        pyautogui.write(letra_aleatoria)
        time.sleep(1.5) # Aguarda o sistema carregar a lista de produtos
        
        # Clica no primeiro item da lista
        pyautogui.click(coords['PRIMEIRO_ITEM_LISTA'])
        time.sleep(0.5)
        
        # Desce um número aleatório de vezes para pegar um item diferente
        descidas = random.randint(0, 10)
        for _ in range(descidas):
            pyautogui.press('down')
            time.sleep(0.1)
            
        pyautogui.press('enter') # Abre o item selecionado
        time.sleep(1.5) 
        
        # PREENCHE VALOR UNITÁRIO (Lendo o valor original)
        pyautogui.click(coords['CAMPO_VALOR_UNIT'])
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'c') # Copia o valor atual
        time.sleep(0.2)
        
        # Captura do clipboard e converte para número
        try:
            valor_copiado = pyperclip.paste().strip()
            # Trata o padrão brasileiro (ex: 1.500,50 -> 1500.50)
            valor_copiado = valor_copiado.replace('.', '').replace(',', '.')
            preco_original = float(valor_copiado)
        except ValueError:
            print("Erro ao ler preço original. Usando valor padrão de R$ 10.00")
            preco_original = 10.00
            
        preco_venda = preco_original * 1.5
        
        pyautogui.click(coords['CAMPO_VALOR_UNIT'])
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyautogui.write(f"{preco_venda:.2f}".replace('.', ','))
        time.sleep(0.5)

        # PREENCHE QUANTIDADE
        qtd = random.randint(1, 5)
        pyautogui.click(coords['CAMPO_QUANTIDADE'])
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyautogui.write(str(qtd))
        time.sleep(0.5)
        
        # Confirma o item na nota
        pyautogui.press('enter') 
        time.sleep(1)
        
        valor_total_item = qtd * preco_venda
        valor_atual_nota += valor_total_item
        print(f"   Item add (Letra '{letra_aleatoria}', x{qtd}) - Total acumulado: {valor_atual_nota:.2f}")
        time.sleep(1)

    # 3. Impostos
    print("   Aplicando impostos...")
    pyautogui.click(coords['LISTA_DE_NOTAS']) 
    pyautogui.press('end')
    pyautogui.doubleClick() 
    time.sleep(1.5)
    
    pyautogui.click(coords['CAMPO_CSOSN'])
    pyautogui.write('102')
    
    pyautogui.click(coords['CAMPO_CFOP'])
    pyautogui.write('5102')
    
    pyautogui.click(coords['CHECKBOX_TRIBUTO_TODOS'])
    time.sleep(0.5)
    
    pyautogui.click(coords['BTN_SALVAR_IMPOSTOS'])
    time.sleep(1)
    pyautogui.press('enter') 

    # 4. Transmissão e Pagamento
    print("   Finalizando nota...")
    pyautogui.click(coords['LISTA_DE_NOTAS'])
    pyautogui.press('end')
    pyautogui.doubleClick() 
    time.sleep(2)
    
    pyautogui.click(coords['CAMPO_PAGAMENTO'])
    time.sleep(0.5)
    pyautogui.click(coords['OPCAO_CARTAO_CREDITO'])
    time.sleep(0.5)
    
    pyautogui.click(coords['CAMPO_DINHEIRO'])
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace') 
    
    pyautogui.click(coords['BTN_TRANSMITIR'])
    time.sleep(5) 
    
    pyautogui.click(coords['BTN_FECHAR_PREVIEW'])
    print("✅ Nota finalizada com sucesso!")

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    coords = calibrar_sistema()
    
    inicio = datetime.now()
    fim = inicio + timedelta(minutes=TEMPO_DE_TRABALHO_MINUTOS)
    
    print(f"\nIniciando execução. Término previsto: {fim.strftime('%H:%M')}")
    
    while datetime.now() < fim:
        try:
            trabalhar(coords)
            pausa = random.randint(PAUSA_MINIMA, PAUSA_MAXIMA)
            print(f"Aguardando {pausa} segundos para a próxima nota...")
            time.sleep(pausa)
            
        except KeyboardInterrupt:
            print("\nExecução interrompida.")
            break
        except Exception as e:
            print(f"Erro: {e}. Retomando em 10 segundos...")
            time.sleep(10)