import rclpy
from rclpy.node import Node
import math
from std_msgs.msg import String 


PONTO_DE_ESTABILIDADE = 50.0
DISTANCIA_MINIMA_LIDAR = 20.0

class Motor:
    def __init__(self):
        self.velocidade = 0
    def setVelocidade(self, v):
        self.velocidade = max(0, min(100, v))

class Drone:
    def __init__(self):
        self.x, self.y, self.z = 400.0, 150.0, 0.0
        self.pitch, self.roll, self.yaw = 0.0, 0.0, 0.0
        self.yaw_command = 0.0
        self.throttle = 50.0
        self.lidar_distance = 300.0
        self.chao_y_detectado = 300.0
        self.parada_emergencia = False
        self.motor0, self.motor1, self.motor2, self.motor3 = Motor(), Motor(), Motor(), Motor()

    def motorMixing(self):
        m0 = self.throttle - self.pitch - self.roll - self.yaw_command
        m1 = self.throttle - self.pitch + self.roll + self.yaw_command
        m2 = self.throttle + self.pitch + self.roll - self.yaw_command
        m3 = self.throttle + self.pitch - self.roll + self.yaw_command
        self.motor0.setVelocidade(m0)
        self.motor1.setVelocidade(m1)
        self.motor2.setVelocidade(m2)
        self.motor3.setVelocidade(m3)

    def atualizar(self):
        self.motorMixing()
        if self.yaw > 180: self.yaw -= 360
        if self.yaw < -180: self.yaw += 360
        media = (self.motor0.velocidade + self.motor1.velocidade + self.motor2.velocidade + self.motor3.velocidade) / 4
        self.y -= (media - PONTO_DE_ESTABILIDADE) * 0.1
        pitch_magnitude, roll_magnitude = self.pitch * 0.2, self.roll * 0.2
        angulo_rad = math.radians(self.yaw)
        dx_pitch, dz_pitch = math.cos(angulo_rad) * pitch_magnitude, math.sin(angulo_rad) * pitch_magnitude
        dx_roll, dz_roll = -math.sin(angulo_rad) * roll_magnitude, math.cos(angulo_rad) * roll_magnitude
        self.z += dz_pitch + dz_roll
        self.x += dx_pitch + dx_roll
        self.x, self.z, self.y = max(0, min(800, self.x)), max(-150, min(150, self.z)), max(0, min(300, self.y))
        if self.lidar_distance < DISTANCIA_MINIMA_LIDAR:
            if not self.parada_emergencia:
                self.parada_emergencia = True
                self.throttle = PONTO_DE_ESTABILIDADE
                self.y = self.chao_y_detectado - DISTANCIA_MINIMA_LIDAR
        else:
            self.parada_emergencia = False

class DroneNode(Node):
    def __init__(self):
        super().__init__('droneNode')
        self.drone = Drone()
        self.posicao_publisher = self.create_publisher(String, 'posicao', 10)
        self.velocidade_subscriber = self.create_subscription(String, 'velocidade', self.velocidadeCallback, 10)
        self.throttle_subscriber = self.create_subscription(String, 'throttle', self.throttleCallback, 10)
        self.lidar_subscriber = self.create_subscription(String, 'distancia', self.lidarCallback, 10)
        self.timer = self.create_timer(1.0/60.0, self.update_loop)

    def velocidadeCallback(self, msg):
        try:
            #transforma os dados recebidos em um dicionario, primeiro separando os dados q estao 
            dados = dict(item.split(':') for item in msg.data.split(','))

            #pega os valores do dicionario criado que estao em pitch e roll
            pitch = float(dados.get('pitch', 0.0))
            roll = float(dados.get('roll', 0.0))
            yaw_cmd = float(dados.get('yaw_cmd', 0.0))
            if not self.drone.parada_emergencia:
                self.drone.pitch = pitch
                self.drone.roll = roll
            else:
                self.drone.pitch = 0.0
                self.drone.roll = 0.0
            self.drone.yaw_command = yaw_cmd
            self.drone.yaw -= self.drone.yaw_command * 0.1
        except (ValueError, IndexError) as e:
            self.get_logger().error(f'Erro ao interpretar pitch, roll e yaw: {msg.data}. Erro: {e}')

    def throttleCallback(self, msg):
        try:
            self.drone.throttle = float(msg.data)
            self.drone.throttle = max(0, min(100, self.drone.throttle))
        except ValueError:
            self.get_logger().error(f'Formato de throttle inválido: {msg.data}')

    def lidarCallback(self, msg):
        try:
            dados = dict(item.split(':') for item in msg.data.split(','))
            self.drone.lidar_distance = float(dados.get('dist', 300.0))
            self.drone.chao_y_detectado = float(dados.get('chao_y', 300.0))
        except (ValueError, IndexError) as e:
            self.get_logger().error(f'Erro ao interpretar lidar: {msg.data}. Erro: {e}')

    def update_loop(self):
        self.drone.atualizar()
        
        #formata pra string os valores das posiçoes do drone
        statusPosicao = (
            f"x:{self.drone.x:.1f},"
            f"y:{self.drone.y:.1f},"
            f"z:{self.drone.z:.1f},"
            f"yaw:{self.drone.yaw:.1f}"
        )

        #envia as posições do drone
        msg = String()
        msg.data = statusPosicao
        self.posicao_publisher.publish(msg)

def main(args=None):
    rclpy.init()
    node = DroneNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()