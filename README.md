# Stussi Launcher

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/Qt-PySide6-darkblue?logo=qt" alt="PySide6" />
  <img src="https://img.shields.io/badge/Steam-Launcher-ff4d4d" alt="Steam Launcher" />
</p>

Stussi Launcher é um aplicativo desktop para Windows, desenvolvido em Python com PySide6, pensado para oferecer uma experiência visual moderna, rápida e inspirada no universo de corrida e performance.

## ✨ Principais recursos

- Visualização da biblioteca Steam instalada
- Busca e ordenação de jogos por nome, tamanho ou último uso
- Modo tela cheia e modo janela
- Interface com cards animados e estilo polido
- Tela inicial personalizada com som e splash screen
- Compatibilidade com telas largas e resoluções altas
- Abertura rápida dos jogos diretamente pelo Steam

## 🧩 Sobre o projeto

O projeto foi criado para reunir em uma única interface os jogos instalados no Steam, mantendo o visual elegante e organizado. Ele lê os manifestos do Steam para identificar os jogos disponíveis e exibe uma experiência mais imersiva para o usuário.

## 🛠️ Requisitos

- Python 3.10 ou superior
- Steam instalado e com sessão iniciada
- Sistema operacional Windows

Instale as dependências com:

```bash
pip install -r requirements.txt
```

## ▶️ Como executar

Na pasta do projeto, rode:

```bash
python main.py
```

## 📦 Como gerar o executável

Para criar um executável standalone no Windows:

```bash
pyinstaller StussiLauncher.spec
```

O resultado será gerado na pasta `dist/`.

## 📁 Estrutura do projeto

```text
.
├── main.py               # Interface principal e lógica da aplicação
├── steam_utils.py        # Funções para descobrir e iniciar jogos do Steam
├── requirements.txt      # Dependências do projeto
├── StussiLauncher.spec   # Configuração do PyInstaller
├── icon.ico              # Ícone da aplicação
├── somstussi.wav         # Som de inicialização
└── README.md             # Documentação do projeto
```

## 🎨 Estilo da interface

A aplicação utiliza um visual escuro com identidade de performance, com:

- destaque em azul-marinho e vermelho
- cards arredondados com brilho sutil
- animações suaves para navegação e interação
- foco em apresentação em tela cheia

## 🔎 Solução de problemas

- Se nenhum jogo aparecer, verifique se o Steam está instalado corretamente e se a biblioteca possui jogos.
- Se o aplicativo não iniciar, confirme que todas as dependências foram instaladas.
- Se houver erro na geração do executável, verifique se os arquivos usados pela configuração estão presentes no projeto.

## 📸 Capturas

> Adicione imagens aqui posteriormente para mostrar a interface do launcher.

## 🚀 Próximos passos

Melhorias planejadas para versões futuras:

- filtro por gênero ou tags
- seção com jogos recentes
- temas personalizáveis
- suporte a opções extras de inicialização
- atualização automática da aplicação

---

Se quiser, também posso adicionar um arquivo `LICENSE` e melhorar ainda mais a apresentação do repositório.
