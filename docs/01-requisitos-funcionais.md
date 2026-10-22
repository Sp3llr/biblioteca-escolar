# Lista de requisitos funcionais

Objetivo: controlar o acervo, os usuários e a circulação de livros da escola.

## RF01 - Autenticação

Permitir entrar com e-mail e senha de um usuário cadastrado. Campos vazios e dados incorretos devem gerar uma mensagem de erro.

## RF02 - Controle de acesso

Bloquear as páginas internas para quem não estiver autenticado e permitir encerrar a sessão pelo botão Sair.

## RF03 - Painel principal

Mostrar o total de títulos cadastrados, de empréstimos ativos e de usuários cadastrados.

## RF04 - Cadastro de livros

Cadastrar livro com título, autor, categoria e quantidade disponível. Todos os campos são obrigatórios.

## RF05 - Pesquisa de livros

Pesquisar livros por parte do título, do autor ou da categoria, sem diferenciar letras maiúsculas e minúsculas.

## RF06 - Alteração de livros

Alterar os dados de um livro e validar uma quantidade inteira maior ou igual a zero.

## RF07 - Exclusão de livros

Excluir livros sem empréstimos vinculados. Se houver histórico, bloquear a exclusão e explicar o motivo.

## RF08 - Cadastro de usuários

Cadastrar nome, e-mail e senha. Impedir e-mails repetidos e exigir senha com pelo menos 6 caracteres.

## RF09 - Registro de empréstimo

Registrar usuário, livro, data do empréstimo e data prevista para devolução. As referências devem existir no banco.

## RF10 - Verificação de estoque

Bloquear empréstimos sem exemplares disponíveis e diminuir a quantidade em uma unidade após uma retirada válida.

## RF11 - Validação de datas

Impedir uma previsão anterior à data do empréstimo e impedir empréstimos com data futura.

## RF12 - Registro de devolução

Salvar a data real da devolução e aumentar o estoque em uma unidade. Não permitir devolver o mesmo empréstimo duas vezes.

## RF13 - Histórico

Listar todos os empréstimos com usuário, livro, datas e situação. Permitir filtrar ativos, devolvidos e atrasados.

## RF14 - Relatório geral

Exibir a lista dos empréstimos com as datas de retirada, previsão e devolução real.

## RF15 - Livros mais emprestados

Exibir o ranking de títulos pela quantidade de empréstimos, contando os ativos e devolvidos. Incluir títulos com zero empréstimos.

## RF16 - Exportação

Permitir baixar o ranking de livros mais emprestados em um arquivo CSV.

## Regras adotadas

Quantidade significa exemplares disponíveis. Cada empréstimo representa um exemplar. Todos os usuários autenticados usam as mesmas funções; não há perfis diferentes nesta versão.
