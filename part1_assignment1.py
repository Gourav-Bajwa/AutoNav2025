#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

class TurtleBoxArtist(Node):

    def _init_(self):
        super()._init_('turtle_box_artist')

        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.on_pose, 10)

        self.origin_x = None
        self.origin_y = None
        self.heading = None

        self.edge_len = 3.0
        self.move_speed = 1.2
        self.rotate_speed = 1.6

        self.next_angle = None
        self.step = 'forward'  # either 'forward' or 'turn'
        self.edge_count = 0

        self.get_logger().info("TurtleBoxArtist launched. Let's paint a square!")

    def on_pose(self, pose):
        twist = Twist()

        if self.origin_x is None:
            # capture starting state once
            self.origin_x = pose.x
            self.origin_y = pose.y
            self.heading = pose.theta
            self.next_angle = self.adjust_angle(self.heading + math.pi / 2)
            self.get_logger().info("Init pose recorded.")

        if self.step == 'forward':
            dist_moved = self.get_distance(pose.x, pose.y, self.origin_x, self.origin_y)
            if dist_moved < self.edge_len - 0.05:
                twist.linear.x = self.move_speed
            else:
                twist.linear.x = 0.0
                self.step = 'turn'
                self.get_logger().info(f"Edge {self.edge_count + 1} done. Rotating...")

        elif self.step == 'turn':
            angle_gap = self.adjust_angle(self.next_angle - pose.theta)
            if abs(angle_gap) > 0.04:
                twist.angular.z = self.rotate_speed if angle_gap > 0 else -self.rotate_speed
            else:
                twist.angular.z = 0.0
                self.origin_x = pose.x
                self.origin_y = pose.y
                self.next_angle = self.adjust_angle(self.next_angle + math.pi / 2)
                self.edge_count += 1
                if self.edge_count >= 4:
                    self.get_logger().info("Square complete. Job done!")
                    self.cmd_pub.publish(Twist())  # stop everything
                    rclpy.shutdown()
                    return
                self.step = 'forward'

        self.cmd_pub.publish(twist)

    def get_distance(self, x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return math.sqrt(dx*dx + dy*dy)

    def adjust_angle(self, angle):
        """Wrap angle to [-pi, pi]"""
        while angle > math.pi:
            angle -= 2*math.pi
        while angle < -math.pi:
            angle += 2*math.pi
        return angle

def main(args=None):
    rclpy.init(args=args)
    node = TurtleBoxArtist()
    rclpy.spin(node)
    rclpy.shutdown()

if _name_ == '_main_':
    main()
