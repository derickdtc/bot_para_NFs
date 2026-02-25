
---

# 📘 fluxo_funcional.md

```markdown
# Fluxo Funcional do Sistema NFC-e

## 1️⃣ Abertura

1. Clicar em "Abrir NFCe"
2. Confirmar popup 1
3. Confirmar popup 2 (bug do sistema)
4. Confirmar popup final

---

## 2️⃣ Selecionar Nota

1. Rolar lista até o final
2. Selecionar última nota
3. Clicar em "Incluir Itens"

---

## 3️⃣ Inclusão de Itens

Loop até valor da nota estar entre 50 e 300:

1. Digitar letra aleatória no campo Nome
2. Selecionar item aleatório da lista
3. Abrir item
4. Ajustar:
   - Quantidade (1 a 5)
   - Valor Unitário = valor_original × 1.5
5. Confirmar item

---

## 4️⃣ Aplicar Impostos

1. Clicar em qualquer item
2. Preencher:
   - CSOSN = 102
   - CFOP = 5102
3. Marcar:
   - Tributo para todos os itens
4. Salvar
5. Confirmar popup

---

## 5️⃣ Transmissão

1. Dar duplo clique na nota
2. Selecionar pagamento:
   - 03 = Cartão de Crédito
3. Limpar campo Dinheiro
4. Clicar em Transmitir
5. Fechar preview no X

---

## 6️⃣ Loop

Voltar ao passo 1.