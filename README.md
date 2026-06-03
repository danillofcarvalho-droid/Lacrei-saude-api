# Lacrei Saúde - API de Gerenciamento de Consultas Médicas

Esta é uma API RESTful de alta performance desenvolvida para o gerenciamento de profissionais da saúde e agendamentos de consultas. O projeto foi arquitetado com foco em segurança, escalabilidade, auditoria de logs e automação total de infraestrutura.

---

##  1. Decisões Técnicas e Justificativas

A arquitetura deste projeto foi desenhada visando as melhores práticas de desenvolvimento de software empresarial:

* **Python 3.11 & Django REST Framework (DRF):** Escolha fundamentada na robustez do ecossistema, maturidade de segurança nativa (proteção contra SQL Injection, XSS e CSRF) e velocidade de desenvolvimento utilizando `ModelViewSets` e `Routers` para padronização de endpoints RESTful.
* **Poetry:** Adotado para o gerenciamento de dependências determinístico. O isolamento estrito via `poetry.lock` mitiga completamente conflitos de pacotes em diferentes máquinas e garante builds idênticos entre os ambientes.
* **PostgreSQL:** Banco de dados relacional escolhido em detrimento do SQLite devido à sua consistência ACID estrita, alta capacidade de concorrência de leitura/escrita e excelente suporte à integridade referencial por chaves estrangeiras (`ForeignKey`), crucial para dados sensíveis de saúde.
* **Docker & Docker Compose:** Utilizados para a containerização completa da aplicação, eliminando o clássico problema de variação ambiental de sistemas operacionais. Toda a infraestrutura (Código + Banco) sobe com um único comando.
* **Autenticação Híbrida (Simple JWT + Sessions):** Implementação de segurança stateless baseada em tokens criptografados **JWT** para consumo de clientes externos (Frontend/Mobile/Postman), associada ao **SessionAuthentication** para permitir a navegação e testes internos através da interface nativa do DRF.
* **OpenAPI 3 / Swagger (`drf-spectacular`):** Integração automática de documentação dinâmica para facilitar o trabalho de desenvolvedores frontend integradores, eliminando a necessidade de atualização manual de contratos de API.
* **Integração com Gateway de Pagamentos (Asaas):** Implementação de arquitetura baseada em serviços (`services.py`) desacoplados e orientação a eventos utilizando webhooks (`/api/webhooks/asaas/`). Ao realizar um agendamento, o sistema gera dinamicamente uma cobrança integrada, permitindo conciliação bancária assíncrona automatizada com o evento `PAYMENT_RECEIVED` liberado sem travas de autenticação global JWT (via política `AllowAny`).

---

## 2. Setup do Ambiente Local e com Docker

### Pré-requisitos
* Docker instalado e rodando.
* Docker Compose instalado.

### Clonando o Repositório
```bash
git clone <url-do-seu-repositorio>
cd lacrei-saude-api
```

---

## 3. Instruções para Rodar o Projeto

Como o ambiente é totalmente containerizado, você não precisa instalar o Python, Poetry ou PostgreSQL diretamente na sua máquina hospedeira.

### Passo 1: Construir e Iniciar os Containers
Execute o comando abaixo na raiz do projeto. Ele fará o download do banco de dados, compilará a imagem do Django, aplicará as migrações estruturais do banco de dados e iniciará o servidor:
```bash
docker compose up --build
```

### Passo 2: Criar o Usuário Administrador (Superuser)
Com os containers rodando, abra um **novo terminal** e execute o comando abaixo para criar as suas credenciais de acesso:
```bash
docker compose exec web python manage.py createsuperuser
```
*Insira o nome de usuário, e-mail (opcional) e defina sua senha.*

### Passo 3: Endpoints Disponíveis
A API estará exposta e rodando em `http://localhost:8000/`.

* **Página Inicial da API (Navegável):** `http://localhost:8000/api/`
* **Gerenciamento de Profissionais:** `http://localhost:8000/api/profissionais/`
* **Gerenciamento de Consultas:** `http://localhost:8000/api/consultas/`
* **Geração de Token JWT (Login Externo):** `http://localhost:8000/api/token/`
* **Renovação de Token JWT (Refresh):** `http://localhost:8000/api/token/refresh/`
* **Documentação Interativa (Swagger):** `http://localhost:8000/api/docs/`

> **Nota:** Para interagir com as rotas de profissionais e consultas pelo navegador, lembre-se de clicar no botão **"Log in"** localizado no canto superior direito da tela e inserir as credenciais criadas no Passo 2.

---

## 4. Instruções para Rodar os Testes (`APITestCase`)

A aplicação conta com uma suíte de testes automatizados unitários e de integração utilizando a classe `APITestCase` do DRF. Os testes simulam requisições HTTP reais e cobrem fluxos de sucesso, validações de segurança e restrições de regras de negócio.

Para rodar a bateria de testes isolada dentro do container Docker, execute:
```bash
docker compose exec web python manage.py test
```

### Escopo de Cobertura dos Testes:
* Criação de profissional com sucesso.
* Agendamento de consulta vinculada com sucesso.
* Busca customizada de consultas filtradas por ID do profissional (`/api/profissionais/{id}/consultas/`).
* Bloqueio de requisições anônimas (Garantia de segurança 401 Unauthorized).
* Rejeição de dados obrigatórios ausentes.
* Validação de Regra de Negócio: Impedimento de agendamento de consultas com datas retroativas (no passado).

---

## 5. Arquitetura de Deploy e Pipeline de CI/CD

O repositório está integrado a uma esteira automatizada de entrega contínua configurada via **GitHub Actions** (`.github/workflows/ci-cd.yml`). 

### Fluxo da Esteira (Workflow):
1. **Job 1: Lint & Test (Integração Contínua - CI):** A cada `push` ou `pull request` na branch principal (`main` ou `master`), o GitHub levanta uma máquina virtual Ubuntu, configura o Python 3.11, instala as dependências via Poetry, executa o linter `flake8` para auditar a formatação de código (PEP 8) e roda a suíte de testes do Django. Caso ocorra qualquer falha, o pipeline trava imediatamente.
2. **Job 2: Build (Empacotamento):** Se o estágio de qualidade passar, a esteira efetua o build da imagem Docker da aplicação, garantindo que o pacote está pronto para distribuição.
3. **Job 3: Deploy (Entrega Contínua - CD):** Realiza a publicação automatizada nos ambientes isolados hospedados na nuvem da **AWS**.

### 🌐 Ambientes e Estratégia de Atualização
* **Staging:** Ambiente espelho de homologação voltado para validação interna e testes de fumaça (*Smoke Tests*).
* **Production:** Ambiente real voltado ao usuário final.
* **Estratégia de Rollback (Blue/Green Deployment):** Para mitigar o risco de *downtime* (indisponibilidade), o deploy é feito utilizando a estratégia Blue/Green. O tráfego permanece direcionado ao ambiente estável antigo (Blue) enquanto o novo código é implantado na infraestrutura paralela (Green). Os roteadores de tráfego (AWS Route 53 / ALB) só alteram os ponteiros para a versão Green se todas as checagens automatizadas de saúde da aplicação derem sucesso. Se houver falha, o tráfego continua no ambiente Blue, e o rollback é instantâneo e imperceptível.

---

## 6. Histórico de Desafios, Decisões de Contorno e Melhorias Propostas

Como parte da transparência de engenharia e evolução de software, este repositório documenta os principais marcos técnicos ocorridos durante o ciclo de desenvolvimento:

### Erros Encontrados e Decisões de Contorno

1. **Erro Encontrado:** `TemplateDoesNotExist` ao carregar a raiz da API.
   * *Causa:* A interface gráfica navegável do Django REST Framework depende de templates HTML internos da biblioteca. No início da estruturação das configurações, a aplicação `rest_framework` não havia sido declarada explicitamente no escopo global.
   * *Decisão de Contorno:* Inclusão imediata de `'rest_framework'` no array de `INSTALLED_APPS` dentro do arquivo `core/settings.py`, restabelecendo os caminhos dos loaders de template.
2. **Erro Encontrado:** Loop de persistência do erro `401 Unauthorized` na interface do navegador após login do superusuário.
   * *Causa:* A API foi configurada estritamente com `JWTAuthentication` na política padrão. Como navegadores web tradicionais submetem requisições de formulários baseadas em Cookies/Sessões (e não injetando o cabeçalho `Authorization: Bearer <token>`), o middleware de segurança barrava o acesso visual mesmo após autenticação bem-sucedida.
   * *Decisão de Contorno:* Alteração da arquitetura de segurança no `settings.py` para operar em regime de **Autenticação Híbrida**, injetando o `SessionAuthentication` de forma paralela ao `JWTAuthentication`. Isso manteve os endpoints blindados para o consumo externo via tokens e destravou a usabilidade interna da interface para o desenvolvedor.

### Melhorias Propostas para Próximas Versões

Com o objetivo de elevar o nível de maturidade operacional da API em ambiente de escala, são propostas as seguintes implementações futuras:

* **Validação Avançada de Concorrência de Horários:** Implementação de uma validação customizada no nível do banco ou do serializer para impedir o agendamento de consultas conflitantes (evitar que um mesmo profissional da saúde receba dois agendamentos na mesma janela exata de hora/minuto).
* **Paginador Global (Pagination):** Implementação de paginação padrão (`PageNumberPagination` ou `LimitOffsetPagination`) nos endpoints de listagem para evitar sobrecarga de memória no servidor e lentidão no carregamento quando o volume de profissionais e consultas crescer significativamente.
* **Soft Delete (Exclusão Lógica):** Alteração do método de deleção de profissionais e consultas para usar um campo booleano (ex: `ativo=False`) em vez do método `delete()` real do banco de dados. Isso preserva o histórico de prontuários e auditorias de dados exigidos pelas leis de conformidade médica e LGPD.
* **Throttling (Limitador de Taxa):** Configuração de `ScopedRateThrottle` nas rotas críticas da API (principalmente em `/api/token/`) para blindar o servidor contra ataques de força bruta (*Brute Force*) ou requisições abusivas (*DDoS*).