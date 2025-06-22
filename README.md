# Desafio Técnico - Desenvolvedor Fullstack (Instituto Senai de Inovação)

Este projeto é uma aplicação web fullstack desenvolvida como parte do processo seletivo do ISI. A aplicação simula um sistema de gerenciamento de produtos e descontos, permitindo o cadastro, listagem, edição, exclusão e aplicação de descontos em produtos.

## ✨ Funcionalidades Implementadas

* **Backend (API RESTful em FastAPI):**
    * CRUD completo de Produtos com soft-delete e restauração.
    * Listagem de produtos com filtros avançados, paginação e ordenação.
    * CRUD completo de Cupons de desconto com validações de negócio.
    * Sistema para aplicar/remover descontos (percentuais e via cupom) em produtos.
    * Testes de integração para o ciclo de vida do produto.
* **Frontend (React + Vite):**
    * Interface reativa baseada no design do Figma.
    * Tabela de produtos interativa com busca e paginação.
    * Formulário em modal para criação e edição de produtos.
    * Modais de confirmação e de aplicação de descontos.
    * Atualização automática da UI após operações de CRUD (Create, Read, Update, Delete).
* **Infraestrutura (Docker):**
    * Ambiente 100% containerizado com Docker Compose.
    * Serviços independentes para backend, frontend e banco de dados (PostgreSQL).

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3, FastAPI, SQLModel (SQLAlchemy + Pydantic)
* **Frontend:** React, Vite, JavaScript, TailwindCSS
* **Banco de Dados:** PostgreSQL
* **Infraestrutura:** Docker, Docker Compose
* **UI Components:** Shadcn/UI, Lucide React (ícones)
* **Testes:** Pytest
* **Comunicação API:** Axios
* **Gerenciamento de Estado (Frontend):** TanStack Query (React Query)

---

## 🚀 Como Rodar o Projeto

Para executar o projeto localmente, você precisará ter o **Docker** e o **Docker Compose** instalados.

1.  **Clone o Repositório**
    ```bash
    git clone [https://github.com/Mauro-Jorge/desafio-isi-dev.git](https://github.com/Mauro-Jorge/desafio-isi-dev.git)
    cd desafio-isi-dev
    ```

2.  **Inicie os Contêineres**
    Use o Docker Compose para construir as imagens e iniciar todos os serviços.
    ```bash
    docker compose up --build
    ```
    *(Você pode adicionar a flag `-d` no final para rodar em segundo plano)*.

3.  **Acesse as Aplicações:**
    * **Frontend (Aplicação Principal):** [http://localhost:5173](http://localhost:5173)
    * **Backend (Documentação da API):** [http://localhost:8001/docs](http://localhost:8001/docs)

4.  **Rodando os Testes Automatizados**
    Com os contêineres no ar (usando `docker compose up -d`), execute o seguinte comando no terminal:
    ```bash
    docker compose exec isi-products-service pytest
    ```

---

## 📂 Estrutura do Projeto

O projeto está organizado da seguinte forma:

-   **/backend/services/products_service**: Contém toda a aplicação backend em FastAPI.
    -   **/app/api/routes**: Define os endpoints da API (produtos, cupons).
    -   **/app/core**: Configurações centrais, como a conexão com o banco e funções auxiliares.
    -   **/app/models**: Define as tabelas do banco de dados (`Product`, `Coupon`).
    -   **/app/schemas**: Define os "contratos" de dados da API para validação.
    -   **/app/tests**: Contém os testes automatizados.
-   **/frontend**: Contém toda a aplicação frontend em React.
    -   **/src/components**: Componentes reutilizáveis da UI (Tabela, Formulários, Modais).
    -   **/src/lib**: Configuração de bibliotecas, como o cliente `axios`.
    -   **/src/hooks**: Hooks customizados, como o `useDebounce`.
-   **docker-compose.yml**: Orquestra todos os serviços (backend, frontend, db).
-   **README.md**: Este arquivo.