## O que é o projeto?
Este pacote ROS2 contém um sistema de simulação de um drone desenvolvido com Pygame.

## Pré-requisitos

- ROS2
- Biblioteca Pygame (`pip install pygame`)

## Como rodar?
Este pacote foi projetado para ser executado a partir da raiz de um workspace ROS2.

    ```bash
    # Na raiz do workspace
    colcon build --packages-select drone_control
    ```

    ```bash
    # Na raiz do workspace
    source install/setup.bash
    ```

    ```bash
    ros2 launch drone_control sim_launch.py
    ```
## Para ver as mensagens publicadas nos tópicos:

    ```bash
    # Na raiz do workspace
    source install/setup.bash
    ```
    ```bash
    #mostra os topicos existentes
    ros2 topic list
    ```

    ```bash
    #esse mostra as msg no tópico posicao
     ros2 topic echo /posicao
    ```


## Controles

- **W / S**: Mover para frente / trás (Pitch)
- **A / D**: Mover para os lados (Roll)
- **Seta Esquerda / Seta Direita**: Girar no próprio eixo (Yaw)
- **Seta Cima / Seta Baixo**: Aumentar / diminuir a potência (Throttle)

## Nós do Pacote

- **`no_drone.py` (`drone_node`)**: simula o drone. Contém a física do drone, recebe comandos de controle e dados do sensor Lidar, e publica a posição atual do drone.
- **`no_lidar.py` (`lidar_node`)**: Simula o sensor Lidar. Recebe a posição do drone e publica a distância vertical até o chão ou o obstáculo mais próximo.
- **`no_comando.py` (`comando_node`)**: A interface com o usuário. Utiliza Pygame para criar a janela de visualização, capturar os comandos do teclado e publicá-los para o nó do drone.
