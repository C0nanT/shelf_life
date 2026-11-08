# Controle de validades de alimentos

Status: ready-for-agent

## Problem Statement

Estou formando um estoque de comida em casa, dividido entre o que fica no armário e é consumido no dia a dia e uma reserva de longa duração para emergências. Preciso saber quanto tenho de cada alimento (em unidades, peso ou volume) e quando cada compra vence, e ser avisado antes de algo vencer.

Testei o Grocy e ele faz muito mais do que preciso: o cadastro é pesado e ele não me avisa no Telegram. Uma lista em arquivo de texto seria simples demais, porque não controla quantidade nem baixa parcial.

## Solution

Uma página local, usada no navegador do PC, onde registro cada compra com poucos campos: nome, quantidade, medida, validade e grupo (Armário ou Reserva). A tela principal mostra tudo por validade mais próxima. Quando uso ou jogo algo fora, informo quanto saiu e o sistema desconta da compra que vence antes.

Uma rotina diária olha as validades e manda no máximo uma mensagem por dia no Telegram, só quando algum item chega a um marco de aviso. A mesma rotina faz uma cópia de segurança do banco.

## User Stories

### Registrar compras

1. Como dono do estoque, quero registrar uma compra informando só nome, quantidade, medida, validade e grupo, para não perder tempo com cadastro detalhado.
2. Como dono do estoque, quero que um alimento novo seja criado sozinho na primeira compra daquele nome, para não precisar passar por uma tela de cadastro antes.
3. Como dono do estoque, quero que o nome autocomplete e a medida venha preenchida nas compras seguintes, para digitar menos.
4. Como dono do estoque, quero que "Arroz" e "arroz" sejam o mesmo alimento, para não criar duplicados por causa de maiúsculas.
5. Como dono do estoque, quero um botão "salvar e adicionar outro", para digitar rapidamente todo o estoque atual.
6. Como dono do estoque, quero registrar a mesma comida em compras separadas, cada uma com quantidade e validade próprias, para a validade continuar certa quando compras se misturam.
7. Como dono do estoque, quero escolher entre unidade, g, kg, ml e L, para controlar qualquer tipo de alimento.
8. Como dono do estoque, quero informar quantidades com decimais, como 0,5 kg, para registrar o valor real.
9. Como dono do estoque, quero informar validade com dia, mês e ano, para registrar o que está na embalagem.
10. Como dono do estoque, quero informar validade só com mês e ano, valendo até o último dia do mês, porque muitos alimentos de longa duração trazem só isso.
11. Como dono do estoque, quero deixar a validade em branco, para registrar itens como sal, que nunca geram aviso.
12. Como dono do estoque, quero definir em cada compra se ela é do Armário ou da Reserva, para o mesmo alimento poder estar nos dois grupos.

### Ver o estoque

13. Como dono do estoque, quero uma lista única ordenada pela validade mais próxima, para ver primeiro o que exige atenção.
14. Como dono do estoque, quero os itens vencidos no topo e em destaque, para não deixá-los passar.
15. Como dono do estoque, quero filtrar a lista por Armário ou Reserva, para olhar cada grupo separadamente.
16. Como dono do estoque, quero buscar por nome, para achar um alimento rapidamente.
17. Como dono do estoque, quero uma aba com o total de cada alimento e a separação por grupo, para saber quanto tenho no total.

### Dar baixa

18. Como dono do estoque, quero informar quanto saiu de um alimento, para registrar consumo parcial.
19. Como dono do estoque, quero que a baixa desconte primeiro da compra que vence antes, para consumir na ordem certa sem pensar nisso.
20. Como dono do estoque, quero poder escolher outra compra para descontar, para quando eu pegar de fato um pacote diferente.
21. Como dono do estoque, quero informar a baixa em g ou kg (ou ml ou L) independentemente da medida do alimento, desde que seja da mesma família, para usar a medida mais prática.
22. Como dono do estoque, quero marcar o motivo como "usado" ou "jogado fora", para distinguir consumo de desperdício.
23. Como dono do estoque, quero que uma baixa maior que o disponível seja bloqueada, para o estoque nunca ficar negativo.
24. Como dono do estoque, quero que uma compra zerada saia da lista principal e continue no histórico, para a lista mostrar só o que existe.
25. Como dono do estoque, quero um histórico simples com data, alimento, quantidade e motivo, para consultar o que saiu.

### Mover e corrigir

26. Como dono do estoque, quero mover uma compra inteira ou parte dela entre Armário e Reserva, para fazer o rodízio da reserva antes de vencer.
27. Como dono do estoque, quero editar qualquer campo de uma compra, para corrigir erros de digitação ou de contagem.
28. Como dono do estoque, quero editar a validade de uma compra manualmente, para ajustar quando abro algo que estraga mais rápido.
29. Como dono do estoque, quero apagar uma compra registrada por engano, para corrigir o estoque.
30. Como dono do estoque, quero que correções e exclusões não contem como "usado" nem "jogado fora", para não sujar os números de consumo e desperdício.

### Gerenciar alimentos

31. Como dono do estoque, quero uma página "Alimentos" simples, para renomear um alimento e definir exceções.
32. Como dono do estoque, quero renomear um alimento para um nome já existente e juntar os dois depois de confirmar, para resolver casos como "Arrroz" e "Arroz" sem perder registros.
33. Como dono do estoque, quero que a junção seja bloqueada se as medidas forem de famílias diferentes, para não somar peso com volume ou unidades.
34. Como dono do estoque, quero que a troca de família de medida fique bloqueada enquanto houver compras registradas, para não invalidar quantidades existentes.
35. Como dono do estoque, quero definir prazos de aviso próprios para um alimento, para tratar casos que fogem da regra do grupo.

### Receber avisos

36. Como dono do estoque, quero ser avisado 7 dias antes e no dia do vencimento para itens do Armário, porque são consumidos rapidamente.
37. Como dono do estoque, quero ser avisado 90, 30 e 7 dias antes e no dia do vencimento para itens da Reserva, para ter tempo de consumi-los no dia a dia antes de vencer.
38. Como dono do estoque, quero receber no máximo uma mensagem por dia no Telegram, juntando todos os itens, para não ser incomodado.
39. Como dono do estoque, quero não receber mensagem nos dias sem marco novo, para o aviso continuar relevante.
40. Como dono do estoque, quero que as mensagens venham no bot que já uso e comecem com "Estoque", para distingui-las dos alertas dos sites.
41. Como dono do estoque, quero que a verificação rode ao ligar o PC e todo dia às 9h sem duplicar avisos, para não perder nada mesmo ligando o PC em horários variados.
42. Como dono do estoque, quero que um item cadastrado já dentro de um prazo entre uma vez no próximo resumo com os dias reais restantes, para não ser avisado só no dia de vencer.
43. Como dono do estoque, quero ver só o marco mais recente de cada item depois de muito tempo com o PC desligado, para não receber avisos atrasados repetidos.
44. Como dono do estoque, quero que mover uma compra ou mudar sua validade recalcule os avisos, para os prazos corresponderem à situação nova.
45. Como dono do estoque, quero parar de receber avisos de um item depois de vencido, mantendo-o em destaque na lista até eu dar baixa, para não ser cobrado todo dia.

### Rodar e proteger os dados

46. Como dono do estoque, quero que o sistema suba sozinho ao ligar o PC, para não precisar lembrar de iniciá-lo.
47. Como dono do estoque, quero que o sistema só seja acessível neste PC e abra sem login, para usar sem atrito e sem expor os dados.
48. Como dono do estoque, quero uma cópia diária do banco em `/home/conan/Desktop/backups/estoque/`, para recuperar o estoque em caso de erro ou banco corrompido.
49. Como dono do estoque, quero manter só as 7 cópias mais recentes, para a pasta não crescer sem controle.

## Implementation Decisions

### Tecnologia e implantação

- Projeto novo e pequeno, separado do `price_trail` e do `homelab-monitoring`. Mesmas tecnologias do `price_trail`: Python, Flask e SQLite.
- O motivo da separação: os dados do estoque são digitados à mão e não têm outra origem, enquanto os do `price_trail` podem ser reimportados dos PDFs.
- O serviço escuta somente no endereço local do PC, sem login. O acesso pelo celular é futuro e exigirá decidir acesso e autenticação.
- Interface em português do Brasil.
- O serviço sobe sozinho ao ligar o PC.
- Usa o mesmo bot e a mesma conversa do Telegram dos alertas dos sites. Token e identificador da conversa são configuração do novo projeto, fora do controle de versão.

### Módulos

- **Estoque**: regras de alimentos, compras, baixas, movimentações, correções e junções. Toda regra de negócio fica aqui, sem depender da camada web.
- **Medidas**: famílias de medida, conversão e normalização de quantidades.
- **Avisos**: dado o estado do estoque e a data atual, decide quais compras entram no resumo e monta o texto. Sem acesso a rede.
- **Envio ao Telegram**: envia o resumo. Substituível nos testes.
- **Backup**: copia o banco com segurança, mesmo com o serviço em uso, e aplica a retenção.
- **Rotina diária**: comando único que executa verificação, envio e backup, recebendo data, envio e pasta de destino de fora.
- **Web**: páginas e API. Só traduz requisições para o módulo Estoque.

### Modelo de dados

- **Alimento**: nome de exibição, nome normalizado único (sem espaços nas pontas e sem diferenciar maiúsculas), medida, e marcos de aviso de exceção opcionais.
- **Compra**: alimento, quantidade restante, validade opcional, precisão da validade (dia ou mês), grupo (Armário ou Reserva), data de registro e último marco já avisado.
- **Baixa**: data, alimento, compra de origem, quantidade e motivo (usado ou jogado fora). Baixas continuam no histórico mesmo que a compra zere ou seja apagada.
- Quantidades são guardadas de forma exata, sem erro de arredondamento de ponto flutuante.

### Medidas

- Medidas permitidas: unidade, g, kg, ml e L.
- Famílias: peso (g, kg), volume (ml, L) e unidade. Só há conversão dentro da família (1000 g = 1 kg, 1000 ml = 1 L).
- Não existe conversão como "1 pacote = 500 g".
- Cada alimento pertence a uma família, definida na primeira compra. Trocar de família é bloqueado enquanto houver compras registradas.

### Validade

- A validade com mês e ano vale até o último dia do mês, e continua sendo exibida como mês e ano.
- Compras sem validade nunca geram aviso e aparecem depois das que têm validade na lista.

### Regras de baixa

- Sem compra escolhida, a baixa desconta da compra com validade mais próxima e continua nas seguintes se precisar. Compras sem validade são as últimas.
- Uma baixa que atravessa várias compras gera uma linha de histórico por compra.
- Baixa maior que o disponível é rejeitada por inteiro, sem desconto parcial.
- Compra zerada sai da lista principal.

### Movimentação e correção

- Mover parte de uma compra cria outra compra com mesma validade no grupo de destino.
- Editar e apagar compras não gera baixa.
- Abrir uma embalagem não tem tratamento próprio. Se ela estragar mais rápido, a validade é editada à mão.

### Junção de alimentos

- Renomear para um nome existente pede confirmação e move compras e histórico para o alimento de destino.
- Junção entre famílias de medida diferentes é bloqueada.

### Avisos

- Marcos padrão: Armário em 7 e 0 dias; Reserva em 90, 30, 7 e 0 dias. Uma exceção por alimento substitui os marcos do grupo.
- Para cada compra com saldo e validade, com `d` dias restantes, o **marco atual** é o menor marco maior ou igual a `d`. Compra com `d` negativo usa o marco 0.
- Compra entra no resumo quando tem marco atual e ele é diferente do último marco já avisado. O resumo mostra os dias reais restantes (ou há quantos dias venceu).
- Depois do envio, o marco atual é gravado como último marco avisado de cada compra incluída. Depois do marco 0, a compra não gera novos avisos.
- Mover uma compra de grupo, mudar sua validade ou alterar os marcos do alimento limpa o último marco avisado. A compra criada por movimentação parcial começa sem marco avisado.
- Baixa parcial não altera os marcos.
- Sem nenhuma compra a avisar, nada é enviado.
- A rotina roda ao ligar o PC e todo dia às 9h, no fuso local. Rodar várias vezes no mesmo dia não duplica aviso, porque o controle é por marco já avisado.

### Backup

- A rotina diária grava uma cópia do banco por dia em `/home/conan/Desktop/backups/estoque/` e mantém as 7 mais recentes.
- Essa pasta fica no mesmo PC, então a cópia protege contra erro e banco corrompido, mas não contra falha de disco ou perda do PC. Esse risco foi aceito por enquanto.

### Telas

- **Lista principal**: compras com saldo por validade mais próxima, vencidas no topo e em destaque, filtro por grupo e busca por nome. Ações de baixa, mover, editar e apagar.
- **Totais**: total por alimento, com separação por grupo.
- **Nova compra**: formulário com autocompletar do nome e botão "salvar e adicionar outro".
- **Histórico**: lista de baixas com data, alimento, quantidade e motivo, sem gráficos.
- **Alimentos**: renomear, juntar e definir marcos de exceção. Nenhum campo obrigatório além de nome e medida.

## Testing Decisions

Um bom teste verifica comportamento visível de fora: o que a API responde, o que aparece nas listas, o que seria enviado ao Telegram e os arquivos gerados. Não testa tabelas, funções internas ou detalhes de implementação.

Pontos de teste acordados:

- **Página/API**: requisições HTTP ao aplicativo Flask, com banco temporário. Cobre compra, baixa, mover, correção, junção de alimentos, totais, histórico e validações.
- **Rotina diária**: chamada ao comando único de verificação e backup, com data simulada, Telegram falso e pasta temporária. Cobre marcos, resumo único, ausência de avisos duplicados, longos períodos com o PC desligado, recálculo após mover ou editar, e retenção de 7 cópias.

Módulos cobertos: Estoque, Medidas, Avisos e Backup são exercitados por esses dois pontos, sem testes diretos. Não há testes de navegador.

Referência: os testes do `price_trail` seguem esse padrão, com caso base de API usando o cliente de testes do Flask e testes próprios de backup.

## Out of Scope

- Código de barras.
- Preços.
- Lista de compras.
- Estoque mínimo.
- Receitas.
- Importação das notas fiscais do `price_trail`.
- Marcar embalagem como aberta com prazo próprio.
- Cálculo de autonomia da reserva (dias para um número de pessoas).
- Conversão entre famílias de medida ou entre embalagem e peso.
- Acesso pelo celular e login.
- Gráficos de consumo ou desperdício.
- Cópia de segurança fora do PC.
- Integração com o Grafana ou o Prometheus.

## Further Notes

Decisões não discutidas explicitamente, assumidas nesta spec e fáceis de mudar:

- Se o envio ao Telegram falhar, nenhum marco é gravado como avisado e a próxima execução tenta de novo. A falha fica registrada em log. O backup roda mesmo com falha no envio.
- Uma exceção de marcos por alimento vale para esse alimento em qualquer grupo.
- Compra registrada já vencida entra uma vez no próximo resumo, informando há quantos dias venceu, seguindo a mesma regra de item já dentro do prazo.
- Na junção de alimentos, os marcos de exceção do alimento de destino são mantidos.
- "Feijão" e "feijao" contam como alimentos diferentes, e a junção resolve esse caso.
- Se a validade empatar na baixa automática, desconta primeiro a compra registrada há mais tempo.

O projeto roda em Docker. O serviço do Docker foi habilitado na inicialização do PC em 2026-11-08. Ainda falta confirmar com um reinício real que tudo volta sozinho.
