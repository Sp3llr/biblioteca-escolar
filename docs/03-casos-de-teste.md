# Casos de teste de software

## Preparação

Usar um banco de avaliação carregado com banco/biblioteca.sql. Os casos que citam o banco inicial devem começar com os dados originais. Não usar dados reais.

## CT01 - Login válido (RF01)

Passos: Entrar com ana@escola.com e Biblioteca123.

Resultado esperado: Abrir o painel e mostrar o nome de Ana.

## CT02 - Login inválido (RF01)

Passos: Usar o mesmo e-mail com senha errada.

Resultado esperado: Mostrar erro e manter o acesso bloqueado.

## CT03 - Campos vazios (RF01)

Passos: Tentar entrar sem e-mail ou sem senha.

Resultado esperado: Exigir os dois campos e não criar sessão.

## CT04 - Acesso direto e saída (RF02)

Passos: Abrir /livros sem login; depois entrar, sair e abrir /painel.

Resultado esperado: Redirecionar ao login nos dois acessos sem sessão.

## CT05 - Painel inicial (RF03)

Passos: Importar o banco vazio com o SQL e entrar.

Resultado esperado: Mostrar 5 títulos, 3 empréstimos ativos e 3 usuários.

## CT06 - Cadastrar e pesquisar (RF04, RF05)

Passos: Cadastrar Livro Teste, Autor Teste, categoria Teste, quantidade 2; pesquisar pelo título.

Resultado esperado: Salvar no banco e mostrar o livro na pesquisa.

## CT07 - Quantidade e campos (RF04, RF06)

Passos: Tentar salvar com título vazio, quantidade -1, 1,5 ou texto. Depois salvar com quantidade 0.

Resultado esperado: Bloquear os dados inválidos; aceitar quantidade 0.

## CT08 - Alterar livro (RF06)

Passos: Alterar categoria e quantidade do Livro Teste. Reabrir a página.

Resultado esperado: Mostrar os novos dados também após recarregar.

## CT09 - Excluir livro (RF07)

Passos: Excluir Livro Teste sem empréstimos. Tentar excluir Dom Casmurro.

Resultado esperado: Excluir o primeiro e bloquear o segundo para preservar o histórico.

## CT10 - Empréstimo com estoque (RF09, RF10)

Passos: No banco inicial, emprestar um exemplar de Dom Casmurro.

Resultado esperado: Criar um empréstimo e reduzir o estoque de 3 para 2.

## CT11 - Empréstimo sem estoque (RF10)

Passos: Tentar emprestar Algoritmos e Lógica de Programação (estoque 0).

Resultado esperado: Opção indisponível na tela; servidor também bloqueia sem alterar o banco.

## CT12 - Datas inválidas (RF11)

Passos: Informar previsão anterior à retirada; depois tentar retirada futura.

Resultado esperado: Mostrar erro e manter empréstimos e estoque sem mudança.

## CT13 - Devolução e repetição (RF12)

Passos: Devolver o empréstimo inicial de ID 5 e tentar a mesma devolução novamente.

Resultado esperado: Salvar a data real e passar estoque de 0 para 1. Na repetição, manter 1.

## CT14 - Histórico e filtros (RF13, RF14)

Passos: Abrir os filtros Todos, Ativos, Devolvidos e Atrasados.

Resultado esperado: Mostrar apenas registros da situação selecionada. O empréstimo inicial de Carla aparece em atrasados.

## CT15 - Ranking e CSV (RF15, RF16)

Passos: Com o banco inicial, abrir Relatórios e baixar o CSV.

Resultado esperado: O Pequeno Príncipe aparece primeiro com 2 empréstimos. CSV contém os mesmos totais.

## CT16 - Cadastro de usuário (RF08)

Passos: Cadastrar nome, e-mail novo e senha com 6 ou mais caracteres. Repetir o e-mail.

Resultado esperado: Criar a primeira conta, permitir login e bloquear o e-mail repetido.

## CT17 - Último exemplar simultâneo (RF10)

Passos: Enviar duas solicitações ao mesmo tempo para A Hora da Estrela, com 1 exemplar disponível.

Resultado esperado: Apenas um pedido é aceito. Estoque termina em 0 e nunca fica negativo.

## CT18 - Proteção de formulário (RF02)

Passos: Com login feito, enviar um POST sem o token do formulário.

Resultado esperado: Responder 400 e não alterar o banco.

## Execução

O README explica como executar a suíte de integração. Os testes usam PostgreSQL de verdade e recriam as tabelas de um banco exclusivo de testes. O roteiro manual também cobre os campos e botões na interface.
