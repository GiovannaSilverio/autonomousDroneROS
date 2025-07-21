import rclpy
from rclpy.node import Node
import pygame
import math
from geometry_msgs.msg import Twist, Pose
from std_msgs.msg import Float64

class InterfaceNode(Node):
    def __init__(self):
        super().__init__('interface_node')
        self.drone_pose = Pose()
        self.drone_pose.position.x = 400.0
        self.drone_pose.position.y = 150.0

        self.cmd_vel_publisher = self.create_publisher(Twist, '/drone/cmd_vel', 10)
        self.throttle_publisher = self.create_publisher(Float64, '/drone/throttle', 10)
        self.pose_subscriber = self.create_subscription(Pose, '/drone/pose', self.pose_callback, 10)

        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Drone 3D Simulação)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        self.obstaculos = [pygame.Rect(100, 50, 80, 50), pygame.Rect(300, -100, 50, 50)]
        self.obstaculos_alturas = [100, 50]
        self.current_throttle = 50.0

    def pose_callback(self, msg: Pose):
        self.drone_pose = msg

    def run(self):
        running = True
        while running and rclpy.ok():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.handle_keys()
            self.draw()
            rclpy.spin_once(self, timeout_sec=0)
            self.clock.tick(60)
        pygame.quit()
        self.destroy_node()
        rclpy.shutdown()

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        cmd_vel_msg = Twist()

        if keys[pygame.K_UP]: self.current_throttle += 1.0
        if keys[pygame.K_DOWN]: self.current_throttle -= 1.0
        self.current_throttle = max(0, min(100, self.current_throttle))
        throttle_msg = Float64()
        throttle_msg.data = self.current_throttle
        self.throttle_publisher.publish(throttle_msg)

        if keys[pygame.K_w]: cmd_vel_msg.linear.x = 10.0
        elif keys[pygame.K_s]: cmd_vel_msg.linear.x = -10.0
        else: cmd_vel_msg.linear.x = 0.0
        if keys[pygame.K_d]: cmd_vel_msg.linear.y = 10.0
        elif keys[pygame.K_a]: cmd_vel_msg.linear.y = -10.0
        else: cmd_vel_msg.linear.y = 0.0
        if keys[pygame.K_LEFT]: cmd_vel_msg.angular.z = 15.0
        elif keys[pygame.K_RIGHT]: cmd_vel_msg.angular.z = -15.0
        else: cmd_vel_msg.angular.z = 0.0
        self.cmd_vel_publisher.publish(cmd_vel_msg)

    def draw(self):
        self.screen.fill((255, 255, 255))
        tela_cima = pygame.Rect(0, 0, 800, 300)
        tela_lado = pygame.Rect(0, 300, 800, 300)
        pygame.draw.rect(self.screen, (220, 240, 255), tela_cima)
        self.desenhar_obstaculos_superior(tela_cima)
        self.desenhar_vista_superior(tela_cima)
        pygame.draw.rect(self.screen, (200, 255, 200), tela_lado)
        self.desenhar_obstaculos_lateral(tela_lado)
        self.desenhar_vista_lateral(tela_lado)
        pygame.display.flip()

    def desenhar_vista_superior(self, area):
        q = self.drone_pose.orientation
        yaw_rad = math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        centro_x = int(self.drone_pose.position.x)
        centro_z = area.top + area.height // 2 + int(self.drone_pose.position.z)
        dx, dz = math.cos(yaw_rad) * 20, math.sin(yaw_rad) * 20
        pygame.draw.circle(self.screen, (100, 100, 255), (centro_x, centro_z), 10)
        pygame.draw.line(self.screen, (255, 0, 0), (centro_x, centro_z), (centro_x + dx, centro_z + dz), 3)

    def desenhar_vista_lateral(self, area):
        centro_z_tela = area.left + area.width // 2 + int(self.drone_pose.position.z)
        centro_y_tela = area.top + int(self.drone_pose.position.y)
        corpo_rect = pygame.Rect(0, 0, 30, 10)
        corpo_rect.center = (centro_z_tela, centro_y_tela)
        pygame.draw.rect(self.screen, (100, 100, 255), corpo_rect)

    def desenhar_obstaculos_superior(self, area):
        for obs_rect in self.obstaculos:
            pos_x_tela = obs_rect.left
            pos_y_tela = area.top + (area.height // 2) + obs_rect.top
            rect_desenho = pygame.Rect(pos_x_tela, pos_y_tela, obs_rect.width, obs_rect.height)
            pygame.draw.rect(self.screen, (100, 100, 100), rect_desenho)

    def desenhar_obstaculos_lateral(self, area):
        for i, obs_rect in enumerate(self.obstaculos):
            pos_x_tela = area.left + (area.width // 2) + obs_rect.top
            altura_na_tela = self.obstaculos_alturas[i]
            pos_y_tela = area.top + (300 - altura_na_tela)
            largura_na_tela = obs_rect.height
            rect_desenho = pygame.Rect(pos_x_tela, pos_y_tela, largura_na_tela, altura_na_tela)
            pygame.draw.rect(self.screen, (0, 100, 0), rect_desenho)

def main(args=None):
    rclpy.init(args=args)
    node = InterfaceNode()
    node.run()

if __name__ == '__main__':
    main()