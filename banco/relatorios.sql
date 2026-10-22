-- Ranking: inclui livros sem empréstimos e conta ativos e devolvidos.
SELECT l.titulo, l.autor, COUNT(e.id_emprestimo) AS total_emprestimos
FROM livro l
LEFT JOIN emprestimo e ON e.id_livro = l.id_livro
GROUP BY l.id_livro
ORDER BY total_emprestimos DESC, l.titulo;

-- Histórico completo.
SELECT u.nome, l.titulo, e.data_emprestimo, e.data_prevista, e.data_devolucao
FROM emprestimo e
JOIN usuario u ON u.id_usuario = e.id_usuario
JOIN livro l ON l.id_livro = e.id_livro
ORDER BY e.id_emprestimo DESC;
