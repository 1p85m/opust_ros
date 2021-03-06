#! /usr/bin/env python3

import rospy

from std_msgs.msg import Float64
from std_msgs.msg import Float32
from std_msgs.msg import String
from std_msgs.msg import Bool
from std_msgs.msg import Float64MultiArray

import time
from datetime import datetime as dt
import threading
import sys
sys.path.append("/home/exito/ros/src/opust_ros/lib/")
import calc_offset

node_name = "worldcoordinate_onepoint"

class worldcoord(object):

    x = 0
    y = 0
    coord = 0
    planet = 0
    off_x = 0
    off_y = 0
    off_coord = ""
    hosei = ""
    lamda = 0
    dcos = 0
    limit = False
    hosei = 0
    timestamp=0
    from_node=""

    def __init__(self):

        rospy.Subscriber("ps_x",Float64, self._receive_x, queue_size=1)
        rospy.Subscriber("ps_y",Float64, self._receive_y, queue_size=1)
        rospy.Subscriber("ps_coord", String, self._receive_coord, queue_size=1)
        rospy.Subscriber("ps_planet", String, self._receive_planet, queue_size=1)
        rospy.Subscriber("ps_off_x", Float64, self._receive_off_x, queue_size=1)
        rospy.Subscriber("ps_off_y", Float64, self._receive_off_y, queue_size=1)
        rospy.Subscriber("ps_offcoord" ,String, self._receive_offcoord, queue_size=1)
        rospy.Subscriber("ps_hosei", String, self._receive_hosei, queue_size=1)
        rospy.Subscriber("ps_lamda", Float64, self._receive_lamda, queue_size=1)
        rospy.Subscriber("ps_dcos", Float64, self._receive_dcos, queue_size=1)
        rospy.Subscriber("ps_limit", Bool, self._receive_limit, queue_size=1)

        rospy.Subscriber("ps_from_node", String, self._receive_from_node, queue_size=1)
        rospy.Subscriber("ps_timestamp", Float64, self._receive_timestamp, queue_size=1)

        self.pub_x_list = rospy.Publisher("wc_x_list", Float64MultiArray, queue_size=1)
        self.pub_y_list = rospy.Publisher("wc_y_list", Float64MultiArray, queue_size=1)
        self.pub_time_list = rospy.Publisher("wc_time_list", Float64MultiArray, queue_size=1)
        self.pub_coord = rospy.Publisher("wc_coord", String, queue_size=1)
        self.pub_off_az = rospy.Publisher("wc_off_az", Float32, queue_size=1)
        self.pub_off_el = rospy.Publisher("wc_off_el", Float32, queue_size=1)
        self.pub_hosei = rospy.Publisher("wc_hosei", String, queue_size=1)
        self.pub_lamda = rospy.Publisher("wc_lamda", Float64, queue_size=1)
        self.pub_limit = rospy.Publisher("wc_limit", Bool, queue_size=1)

        self.pub_timestamp = rospy.Publisher("wc_timestamp", Float64, queue_size=1)

        self.thread_start = threading.Thread(target=self.create_list)
        pass

    def _receive_x(self, q):
        if abs(q.data) > 360.: #limit check
            pass
        else:
            self.x = q.data
        return

    def _receive_y(self, q):
        if abs(q.data)>90: #limit check
            pass
        else:
            self.y = q.data
        return

    def _receive_coord(self, q):
        self.coord = q.data

    def _receive_offcoord(self, q):
        self.off_coord = q.data

    def _receive_planet(self, q):
        self.planet = q.data

    def _receive_off_x(self, q):
        self.off_x = q.data

    def _receive_off_y(self, q):
        self.off_y = q.data

    def _receive_hosei(self, q):
        self.hosei = q.data

    def _receive_lamda(self, q):
        self.lamda = q.data

    def _receive_dcos(self, q):
        self.dcos = q.data

    def _receive_limit(self, q):
        self.limit = q.data

    def _receive_from_node(self, q):
        self.hosei = q.data

    def _receive_timestamp(self, q):
        self.timestamp= q.data


    def create_list(self):
        self.from_node = node_name
        while not rospy.is_shutdown():
            x = self.x
            y = self.y
            coord = self.coord
            planet = self.planet
            off_x = self.off_x
            off_y = self.off_y
            off_coord = self.off_coord
            hosei = self.hosei
            lamda = self.lamda
            dcos = self.dcos
            limit = self.limit
            timestamp = self.timestamp

            self.x = 0
            self.y = 0
            self.coord = ""
            self.planet = ""
            self.off_x = 0
            self.off_y = 0
            self.off_coord = ""
            self.hosei = ""
            self.lamda = 0
            self.dcos = 0
            self.limit = False
            self.timestamp = 0

            if timestamp:
                print("start_create_list")

                ret = calc_offset.calc_offset([x], [y],
                                              coord,
                                              [off_x], [off_y],
                                              off_coord,
                                              dcos,
                                              [dt.fromtimestamp(timestamp)])
                if not ret:
                    continue
                current_time = time.time()

                array = Float64MultiArray()
                array.data = [ret[0], ret[0]]
                self.pub_x_list.publish(array)

                array.data = [ret[1], ret[1]]
                self.pub_y_list.publish(array)

                array.data = [timestamp, timestamp+3600.]
                self.pub_time_list.publish(array)

                msg = String()
                msg.data = coord
                self.pub_coord.publish(msg)

                msg.data = hosei
                self.pub_hosei.publish(msg)

                msg = Float32()
                msg.data = ret[2]
                self.pub_off_az.publish(msg)

                msg.data = ret[3]
                self.pub_off_el.publish(msg)

                msg = Bool()
                msg.data = limit
                self.pub_limit.publish(msg)

                msg = Float64()
                msg.data = lamda
                self.pub_lamda.publish(msg)

                msg.data = current_time
                self.pub_timestamp.publish(msg)

                print("publish status!!\n")
                print("end_create_list\n")
            else:
                pass
            time.sleep(0.1)
        return

if __name__ == "__main__":
    rospy.init_node(node_name)
    wc = worldcoord()
    list_thread = threading.Thread(target=wc.create_list)
    list_thread.start()
    print("start calculation")
