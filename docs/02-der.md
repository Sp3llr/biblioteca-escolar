# Diagrama Entidade Relacionamento

```mermaid
erDiagram
    Usuario ||--o{ Emprestimo : realiza
    Livro ||--o{ Emprestimo : possui
    Usuario {
        int id_usuario PK
        varchar nome
        varchar email UK
        varchar senha
    }
    Livro {
        int id_livro PK
        varchar titulo
        varchar autor
        varchar categoria
        int quantidade
    }
    Emprestimo {
        int id_emprestimo PK
        date data_emprestimo
        date data_prevista
        date data_devolucao
        int id_usuario FK
        int id_livro FK
    }
```

- Um usuário pode ter zero ou vários empréstimos. Cada empréstimo tem um único usuário.
- Um livro pode aparecer em zero ou vários empréstimos. Cada empréstimo corresponde a um exemplar daquele título.
- `data_prevista` guarda o prazo; `data_devolucao` guarda a data real e fica nula enquanto o empréstimo está ativo.
- `quantidade` representa os exemplares disponíveis, não o estoque total.
- `email` é único. `senha` guarda hash PBKDF2-SHA256.
- Todos os campos são obrigatórios, exceto a devolução real. As chaves estrangeiras impedem apagar registros com histórico vinculado.
