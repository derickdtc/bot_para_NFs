# Bot Automação NFC-e

Automação em Python para emissão de Notas Fiscais de Consumidor Eletrônica (NFC-e) via interface desktop.

O sistema automatiza um processo repetitivo de:
- Abertura de nova NFC-e
- Inclusão de itens aleatórios
- Aplicação de impostos fixos
- Seleção de forma de pagamento (Cartão de Crédito)
- Transmissão da nota
- Fechamento da pré-visualização

---

## 🎯 Objetivo

Automatizar a geração de múltiplas notas fiscais com:

- Itens escolhidos de forma aleatória
- Quantidade variável (1 a 5)
- Preço ajustado para 150% do valor original
- Valor final da nota entre R$ 50 e R$ 300
- Impostos fixos:
  - CSOSN = 102
  - CFOP = 5102
- Pagamento sempre:
  - 03 = Cartão de Crédito

---

## ⚙️ Tecnologias

- Python 3.10+
- pyautogui
- keyboard
- pyperclip

---

## 🧠 Como funciona

O bot utiliza:
- Calibração manual de coordenadas
- Automação de mouse e teclado
- Loop de inclusão de itens até atingir meta
- Aplicação automática de impostos
- Finalização e transmissão

---

## 🚀 Execução

```bash
python bot_notas.py