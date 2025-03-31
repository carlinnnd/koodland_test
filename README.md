# koodland_test

Teste para tutoria Koodland.

## Descrição

Este é um jogo roguelike em 2D baseado em clássicos como vampire survivors onde você controla um personagem que precisa sobreviver a ondas de olhos voadores inimigos. O objetivo é abater o máximo de inimigos possível enquanto evita ser atingido. A dificuldade do jogo aumenta com o tempo, tornando a experiência cada vez mais desafiadora.

## Como Executar

1.  **Certifique-se de ter Python instalado em seu sistema.**
2.  **Instale a biblioteca Pygame Zero.** Você pode fazer isso usando o pip:
    ```bash
    pip install pygame-zero
    ```
3.  **Salve o código do jogo em um arquivo chamado `jogo.py`.
4.  **Certifique-se de ter as pastas de assets (`diego` e `flying_eye`) e os arquivos de imagem e música na mesma pasta do script Python.** Os seguintes arquivos são necessários:
    * Pasta `diego/`: Contém as animações do jogador (idle, running, shooting, hurt) e o arquivo `bullet.png`.
    * Pasta `flying_eye/`: Contém as animações do inimigo (fly, attack, death).
    * `background.jpg`: Imagem de fundo do jogo.
    * `2021-08-17_-_8_bit_nostalgia_-_www.fesliyanstudios.com`: Música do menu (formato compatível com Pygame Zero).
    * `2019-12-11_-_retro_platforming_-_david_fesliyan`: Música do jogo (formato compatível com Pygame Zero).
5.  **Abra um terminal ou prompt de comando, navegue até a pasta onde você salvou o arquivo e execute o jogo com o comando:**
    ```bash
    pgzrun jogo.py
    ```

## Controles

### Menu

* **Clique com o mouse** nos botões para:
    * **Começar o jogo:** Inicia uma nova partida.
    * **Música e sons:** Liga ou desliga a música e os efeitos sonoros do jogo.
    * **Saída:** Fecha o jogo.

### Durante o Jogo

* **Teclas W, A, S, D:** Movem o personagem para cima, esquerda, baixo e direita, respectivamente.
* **Tecla ESPAÇO:** Faz o personagem atirar. O tiro é direcionado para o inimigo mais próximo ou na última direção em que o jogador se moveu.

## Mecânicas do Jogo

* **Vidas:** O jogador começa com um número limitado de vidas (inicialmente 10).
* **Inimigos:** Olhos voadores aparecem periodicamente e tentam atacar o jogador.
* **Tiro:** O jogador pode atirar projéteis para derrotar os inimigos.
* **Dificuldade:** A dificuldade do jogo aumenta com o tempo, com inimigos surgindo com mais frequência e possivelmente se movendo mais rápido.
* **Invencibilidade:** Após ser atingido por um inimigo, o jogador tem um breve período de invencibilidade.
* **Game Over:** O jogo termina quando o jogador perde todas as suas vidas.
* **Música:** O jogo possui música de fundo que pode ser ligada ou desligada no menu.

## Assets

O jogo utiliza os seguintes assets:

* **Imagens do Jogador:** Localizadas na pasta `diego/`.
* **Imagem do Projétil:** `diego/bullet.png`.
* **Imagens dos Inimigos:** Localizadas na pasta `flying_eye/`.
* **Imagem de Fundo:** `background.jpg`.
* **Música do Menu:** `2021-08-17_-_8_bit_nostalgia_-_www.fesliyanstudios.com`.
* **Música do Jogo:** `2019-12-11_-_retro_platforming_-_david_fesliyan`.

Certifique-se de que esses arquivos e pastas estejam presentes no mesmo diretório do script do jogo para que ele funcione corretamente.

## Bibliotecas Utilizadas

* **Pygame Zero (`pgzrun`)**: Framework utilizado para criar o jogo.
* **`random`**: Utilizado para geração de números aleatórios, como a posição de surgimento dos inimigos.
* **`math`**: Utilizado para cálculos matemáticos, como distância e ângulos.
* **`pygame.Rect`**: Utilizado para manipulação de retângulos para detecção de colisão.
