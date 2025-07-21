import rclpy
from rclpy.node import Node
import pygame
from std_msgs.msg import String

class Obstaculo:
    def __init__(self, x, z, largura, profundidade, altura):
        self.rect_chao = pygame.Rect(x, z, largura, profundidade)
        self.altura = altura

class LidarNode(Node):
    def __init__(self):
        super().__init__('lidar_node_str')
        self.drone_x = 0.0
        self.drone_y = 0.0
        self.drone_z = 0.0
        self.obstaculos = [
            Obstaculo(x=100, z=50, largura=80, profundidade=50, altura=100),
            Obstaculo(x=300, z=-100, largura=50, profundidade=50, altura=50)
        ]

        # Publisher de String
        self.lidar_publisher = self.create_publisher(String, 'distancia', 10)
        # Subscriber de String
        self.state_subscriber = self.create_subscription(String, '/drone/state_str', self.state_callback, 10)

    def state_callback(self, msg):
        try:
            # Precisa interpretar a string de estado apenas para pegar x, y, z
            dados = dict(item.split(':') for item in msg.data.split(','))
            self.drone_x = float(dados.get('x', 0.0))
            self.drone_y = float(dados.get('y', 0.0))
            self.drone_z = float(dados.get('z', 0.0))
        except (ValueError, IndexError) as e:
            self.get_logger().error(f'Erro ao interpretar state_str no Lidar: {msg.data}. Erro: {e}')
            return
        
        # A lógica de cálculo do Lidar é chamada aqui
        self.update_lidar()

    def update_lidar(self):
        chao_y = 300.0
        for obs in self.obstaculos:
            if obs.rect_chao.collidepoint(self.drone_x, self.drone_z):
                topo_obs_y = 300.0 - obs.altura
                if topo_obs_y < chao_y:
                    chao_y = topo_obs_y
        
        distancia = chao_y - self.drone_y

        # Formata a medição como uma string
        lidar_str = f"dist:{distancia:.1f},chao_y:{chao_y:.1f}"
        msg = String()
        msg.data = lidar_str
        self.lidar_publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = LidarNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()