# Requisitos de infraestrutura

## Hardware

Processador Dual Core ou superior; 4 GB de RAM; pelo menos 20 GB livres para sistema, dependências e dados. Para usar Docker com mais conforto, são recomendados 8 GB de RAM.

## Cliente

Computador com navegador atualizado, como Chrome, Edge ou Firefox. Interface acessível pelo endereço do servidor; não exige instalar Python em cada computador cliente.

## Servidor sem Docker

Windows, Linux ou macOS; Python 3.12; PostgreSQL 16 ou superior; bibliotecas do requirements.txt. O Flask atende a demonstração local na porta 5000.

## Servidor com Docker

Docker Engine com Compose ou Docker Desktop. O Compose inicia a aplicação Python e o PostgreSQL 17, cria as tabelas e popula o banco na primeira inicialização.

## Rede

Rede local da escola para acesso entre máquinas. Internet para instalar dependências, baixar imagens Docker e publicar no GitHub; o uso local não depende de serviços externos.

## Portas e acesso

Demonstração: http://localhost:5000. O Compose libera a porta somente no próprio computador. Para uso na rede escolar, configurar o endereço de escuta, firewall e um servidor HTTP apropriado.

## Persistência e backup

Banco salvo no PostgreSQL. No Compose, os dados ficam em volume persistente. Fazer backup com pg_dump e guardar uma cópia em local diferente do servidor.

## Configuração

Definir DATABASE_URL e SECRET_KEY. Usar credenciais próprias fora da demonstração, limitar o acesso ao banco e usar HTTPS para acesso público.
