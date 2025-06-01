# BLOCKRACE
Este é um jogo de plataforma vertical simples, inspirado no estilo do jogo "Pou", desenvolvido usando Pygame Zero. O objetivo do jogador é pular entre plataformas e subir o mais alto possível, enquanto um "bot" (inimigo ou obstáculo) se move pela tela, adicionando um desafio.

### Como Jogar

Inicie o Jogo: Execute o script main.py (ou o nome do seu arquivo principal).

Tela Inicial/Carregamento: Pressione a barra de espaço para iniciar o jogo ou para sair das telas de "carregamento" ou "game over".

Movimento do Jogador:
  - Seta Esquerda: Move o jogador para a esquerda.
  - Seta Direita: Move o jogador para a direita.
  - O jogador pula automaticamente ao cair em uma plataforma.

Bot: O bot se move horizontalmente pela tela. Evite colidir com ele. Se ele cair da tela, um novo bot aparecera em uma posicao aleatoria.
Suba! O jogo rola verticalmente, e novas plataformas sao geradas a medida que voce sobe.

Fim de Jogo: Se o jogador cair da tela, o jogo termina. Pressione a barra de espaco para voltar a tela inicial.

### Recursos

   - Movimento Responsivo: Controles simples para mover o jogador.
   - Pulos Automaticos: O jogador pula ao tocar em plataformas.
   - Efeitos de Particulas: Pequenas explosoes de particulas ao pular.
   - Animacoes de Salto: O jogador e o bot se "espremem" e "esticam" ao pular, dando um efeito visual interessante.
   - Camera Dinamica: A camera segue o jogador, mantendo a acao centralizada.
   - Gerecao de Plataformas: Plataformas novas sao geradas continuamente para que o jogo nunca termine verticalmente.
   - Musica e Efeitos Sonoros: Sons para pulos do jogador e do bot, e musica de fundo.
   - Ciclo de Jogo: Telas de inicio, jogo e fim de jogo.

### Requisitos

Para rodar este jogo, voce precisara ter o Pygame Zero instalado.

Voce pode instala-lo usando pip:

    pip install pgzero

### Créditos

    imagens:  https://kenney.nl
    songs effect: https://pixabay.com
