

"""**Listagem:** Use `requests.get("/users")` para listar todos os usuários em uma tabela editável (`st.data_editor`).
    * **Formulário de Edição:** Ao clicar em um usuário, popule um formulário para que o admin possa editar:
        * Nome de usuário.
        * Perfil (`admin` ou `usuario`) em um `st.selectbox`.
        * Lista de UGs (usando `st.text_area` para inserir UGs separadas por vírgula ou um widget de seleção múltipla).
        * Campo opcional para redefinir senha.
    * **Criação:** Um formulário para criar novos usuários, que chamaria o `POST /users` (exemplo que adicionei ao `credenciamento.py`)."""