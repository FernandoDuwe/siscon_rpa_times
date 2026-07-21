# Robô RPA para Lançamento de Horas no Benner Siscon (Dockerizado)

Este projeto contém um robô RPA (Robotic Process Automation) desenvolvido em Python com a biblioteca Playwright, empacotado com Docker e Docker Compose. Ele automatiza o processo de login e lançamento de horas no sistema Benner Siscon, permitindo que os parâmetros sejam passados via linha de comando.

## Pré-requisitos

Para executar este projeto, você precisará ter instalado em sua máquina:

*   **Docker:** [Instruções de instalação](https://docs.docker.com/get-docker/)
*   **Docker Compose:** Geralmente vem junto com a instalação do Docker Desktop. Caso contrário, [instale-o separadamente](https://docs.docker.com/compose/install/)

## Estrutura do Projeto

O projeto é composto pelos seguintes arquivos:

*   `benner_rpa.py`: O script Python principal que contém a lógica de automação usando Playwright.
*   `Dockerfile`: Define como a imagem Docker do robô será construída, incluindo as dependências do Python e do Playwright.
*   `docker-compose.yml`: Orquestra a construção e execução do contêiner Docker, passando as variáveis de ambiente e os argumentos para o script Python.
*   `.env.example`: Um arquivo de exemplo para as variáveis de ambiente que você precisará configurar.
*   `requirements.txt`: Lista as dependências Python do projeto.

## Configuração

1.  **Crie o arquivo `.env`:**
    Copie o arquivo `.env.example` para `.env` na raiz do projeto:
    ```bash
    cp .env.example .env
    ```

2.  **Edite o arquivo `.env`:**
    Abra o arquivo `.env` e preencha as variáveis com suas credenciais e os dados padrão para o lançamento de horas:
    ```ini
    BENNER_USERNAME=seu_usuario_aqui
    BENNER_PASSWORD=sua_senha_aqui
    BENNER_KEY=2584207 # Chave da solicitação (ex: 2584207)
    BENNER_DATA=DD/MM/AAAA # Data para lançamento das horas (ex: 13/07/2026)
    BENNER_INICIO=HH:MM # Hora de início (ex: 09:00)
    BENNER_FIM=HH:MM # Hora de fim (ex: 18:00)
    BENNER_OBSERVACOES="Suas observações aqui" # Observações para o lançamento de horas
    BENNER_TIPO="Análise de sistemas" # Tipo de atividade (ex: Análise de sistemas)
    DISPLAY=:0 # **IMPORTANTE:** Configure conforme seu sistema operacional (veja a seção "Visualização do Navegador")
    ```

    **Atenção:** Em ambientes de produção, credenciais e dados sensíveis devem ser gerenciados de forma mais segura (ex: Docker secrets, HashiCorp Vault, etc.) e não diretamente em arquivos `.env`.

## Execução

1.  **Construa a imagem Docker:**
    No diretório raiz do projeto (onde estão o `docker-compose.yml` e o `Dockerfile`), execute:
    ```bash
    docker-compose build
    ```
    Isso construirá a imagem Docker do robô, instalando todas as dependências.

2.  **Execute o robô:**
    Para rodar o robô, use o seguinte comando:
    ```bash
    docker-compose run --rm benner-rpa
    ```
    O parâmetro `--rm` garante que o contêiner seja removido após a execução.

    **Passando parâmetros via linha de comando (sobrescrevendo o `.env`):**
    Você pode sobrescrever qualquer variável definida no `.env` diretamente no comando `docker-compose run`:
    ```bash
    docker-compose run --rm -e BENNER_DATA="14/07/2026" -e BENNER_INICIO="08:00" -e BENNER_FIM="17:00" benner-rpa
    ```
    Ou, para passar todos os parâmetros:
    ```bash
    docker-compose run --rm \
      -e BENNER_USERNAME="novo_usuario" \
      -e BENNER_PASSWORD="nova_senha" \
      -e BENNER_KEY="1234567" \
      -e BENNER_DATA="14/07/2026" \
      -e BENNER_INICIO="08:00" \
      -e BENNER_FIM="17:00" \
      -e BENNER_OBSERVACOES="Nova atividade" \
      -e BENNER_TIPO="Desenvolvimento" \
      benner-rpa
    ```

## Visualização do Navegador (Opcional)

O script Python está configurado com `headless=False`, o que significa que o navegador será aberto e você poderá ver a automação em tempo real. Para que isso funcione dentro do Docker, é necessário configurar o `DISPLAY` corretamente.

*   **Linux:**
    Certifique-se de que seu servidor X está rodando e que você tem permissão para acessar o display. A configuração `DISPLAY=:0` e o mapeamento de volume `- /tmp/.X11-unix:/tmp/.X11-unix` no `docker-compose.yml` geralmente funcionam.

*   **macOS (com XQuartz):**
    1.  Instale o XQuartz.
    2.  Abra o XQuartz e vá em `XQuartz > Preferences > Security` e marque "Allow connections from network clients".
    3.  Reinicie o XQuartz.
    4.  No seu terminal, execute `ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')` (ou `en1` se `en0` não funcionar) e depois `xhost + $ip`.
    5.  No arquivo `.env`, defina `DISPLAY=host.docker.internal:0`.

*   **Windows (com VcXsrv ou similar):**
    1.  Instale e configure um servidor X como o VcXsrv.
    2.  No arquivo `.env`, defina `DISPLAY=host.docker.internal:0`.

**Modo Headless:**
Se você não precisa ver o navegador (para execução em segundo plano ou em servidores sem interface gráfica), você pode alterar `headless=False` para `headless=True` no arquivo `benner_rpa.py` e remover as configurações de `volumes` e `DISPLAY` do `docker-compose.yml`.

## Observações Importantes

*   **Seletores:** Os seletores (`input[name="UserName"]`, `button:has-text("Acessar")`, etc.) foram inferidos a partir das imagens fornecidas. Se o layout do sistema Benner Siscon mudar, pode ser necessário ajustar esses seletores no arquivo `benner_rpa.py`.
*   **URLs:** As URLs utilizadas (`https://siscon.benner.com.br/Login?ReturnUrl=%2f%3f` e `https://siscon.benner.com.br/siscon/e/solicitacoes/Solicitacao.aspx?key={key}&p=1`) são baseadas nas informações fornecidas. Verifique se elas permanecem válidas.
*   **Tipo de Atividade:** O preenchimento do campo "Tipo" (`Etapa - Atividade`) assume que é um campo de texto ou que a seleção pode ser feita digitando e pressionando Enter. Se for um dropdown mais complexo, o seletor e a lógica de interação precisarão ser ajustados.
*   **Erros de Acesso:** Como observado anteriormente, o sistema Benner Siscon pode ter restrições de acesso (IP, rede corporativa). Certifique-se de que o ambiente onde o Docker está sendo executado tem permissão para acessar o sistema.

---

**Autor:** Manus AI
