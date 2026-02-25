# Fluxo Técnico do Bot

## Estrutura Geral

main()
 ├── calibrar_sistema()
 └── trabalhar(coords)

---

## trabalhar(coords)

### Etapa 1: Abrir NFC-e

- click BTN_ABRIR_NFCE
- click BTN_OK_POPUP1
- click BTN_OK_POPUP2
- click BTN_OK_CONFIRMACAO

---

### Etapa 2: Selecionar última nota

- click LISTA_DE_NOTAS
- press END
- doubleClick última nota

---

### Etapa 3: Loop de itens

while valor_atual < meta:

    click BTN_INCLUIR_ITENS
    click CAMPO_BUSCA_PRODUTO
    write letra aleatória
    click PRIMEIRO_ITEM_LISTA
    press DOWN aleatório
    press ENTER

    ajustar valor × 1.5
    ajustar quantidade

    press ENTER

---

### Etapa 4: Impostos

click CAMPO_CSOSN
write 102

click CAMPO_CFOP
write 5102

click CHECKBOX_TRIBUTO_TODOS
click BTN_SALVAR_IMPOSTOS
click BTN_OK_IMPOSTOS

---

### Etapa 5: Pagamento

doubleClick nota

click CAMPO_PAGAMENTO
click OPCAO_CARTAO_CREDITO

click CAMPO_DINHEIRO
CTRL+A
DELETE

click BTN_TRANSMITIR
click BTN_FECHAR_PREVIEW