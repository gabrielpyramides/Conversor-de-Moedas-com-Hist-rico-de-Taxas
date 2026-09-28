# FinancePro - Conversor de Moedas

Um aplicativo simples e com interface moderna feito em Python para conversão inteligente entre Real, Dólar e Euro. O sistema busca as taxas de conversão em tempo real, entrega o cálculo do IOF,e possui um log de histórico que salva automaticamente cada operação realizada.

## 🚀 Como rodar o projeto no seu computador

### 1. Pré-requisitos
Você precisa ter o **Python** instalado no seu sistema. 
> **Aviso para usuários Windows:** Durante a instalação do Python, certifique-se de marcar a opção **"Add Python to PATH"**.

### 2. Download
Faça o clone deste repositório ou baixe o arquivo principal (`finance_pro.py`) e coloque em uma pasta de sua preferência.

### 3. Instalação das dependências
O projeto utiliza duas bibliotecas que não vêm por padrão no Python: o `customtkinter` (para a interface gráfica) e o `requests` (para consultar as taxas na internet). 

Abra o terminal (ou prompt de comando) na pasta onde o arquivo está salvo e digite:

`pip install customtkinter requests`

### 4. Executando o aplicativo
Com as dependências instaladas, basta rodar o comando abaixo no terminal para abrir o programa:

`python finance_pro.py`

## ⚙️ Principais Funcionalidades

**Cotações em Tempo Real:** O sistema busca as taxas diretamente de uma API para garantir que o valor exibido seja o oficial do mercado financeiro no exato momento da consulta.
**Calculadora de IOF Integrada:** O usuário já sabe o custo real da transação antes mesmo de fechar o negócio. O sistema calcula automaticamente as taxas para cartões (4,38%) e espécie (1,10%).
**Diário Financeiro:** Funciona como um "diário financeiro", registrando os valores e as moedas envolvidas, a taxa de câmbio usada no momento, além da data e hora exatas da conversão. É possível exportar esses dados para um arquivo `.csv`.
