# -*- coding:utf-8 -*-  
import numpy as np
import math
import json
class Triangulation:
    def __init__(self, filepath):
        self.delay = 8
        self.A     = 50

        self.IN = 0
        self.OUT = 1
        self.INTERSECTION = 2
        self.coordination = {}
        self.coordination = {}
        lines = open(filepath).readlines()
        for line in lines:
            raw = line.split()
            id = raw[0].lower()
            x, y = float(raw[1]), float(raw[2])
            self.coordination[id] = (x, y)

	print(self.coordination)

        # deal with rssi2distance
        self.min_rssi = 1000
        self.max_rssi = -1000
        self.rssi2distance_cache = {}
        self.distance2rssi_cache = {}
        for i in range(10,61):
            d = 1.0 * i / 10
            self.distance2rssi_cache[d] = self.distance2rssi(d)
        tmp = {}


        for d, r in self.distance2rssi_cache.items():
            r_round = round(r)
            if r_round > self.max_rssi:
                self.max_rssi = r_round
            if r_round < self.min_rssi:
                self.min_rssi = r_round

            if (r_round not in tmp) or ( abs(r - r_round) < tmp[r_round][1] ):
                tmp[r_round] = (d, abs(r - r_round))
        self.rssi2distance_cache = {r:t[0] for r, t in tmp.items()}




    def distance2rssi(self, distance):
        x = distance
        a = 0.05826
        b = -0.72404
        c = 3.45703
        d = -10.64741
        e = -55.85714

        rssi = a * (x**4) + b * (x**3) + c * (x**2) + d * (x) + e
        return rssi

    def rssi2distance(self, rssi): # 蓝牙信号强度转化成距离
        #d = (abs(rssi) - self.A) / (10 * self.delay)
        #d = pow(10, d)
        #return d
        rssi = int(rssi)
        if rssi in self.rssi2distance_cache:
            return self.rssi2distance_cache[rssi]
        elif rssi > self.min_rssi:
            return 0.5
        else:
            return 6


    def getMatrix(self, points): # 构造线性方程
        if len(points) <= 1:
            return None

        x_n, y_n, d_n = points[-1]
        A = []
        b = []
        for i in range(len(points) - 1):
            x_i, y_i, d_i = points[i]
            A_i = [2*(x_i - x_n), 2*(y_i - y_n) ]
            b_i = [x_i**2 - x_n**2 + y_i**2 - y_n**2 + d_n**2 - d_i**2]
            A.append(A_i)
            b.append(b_i)
        A = np.array(A)
        b = np.array(b)
        return A, b

    def getCoord_GradDescent(self, points):  #使用 梯度下降 的方式获取 位置坐标（很不稳定）
        X = np.array([[0], [0]])
        A, b = self.getMatrix(points)
        # loss = (AX -b).T.dot(AX -b)

        for i in range(10):
            grad = 2 * A.T.dot(A.dot(X) - b)
            X = X - 0.1 * grad

        return  X

        pass

    def getCoord_MLE(self, points):  #使用 最小二乘法 获取位置坐标
        A, b = self.getMatrix(points)
        temp1 = A.T.dot(b)
        temp2 = np.linalg.inv(A.T.dot(A))
        coord = temp2.dot(temp1)
        coord = coord.flatten()
        x = float(coord[0])
        y = float(coord[1])
        return (x, y)

    def getLoss(self, A, b, x, y):  #计算误差（欧氏距离）
        X = np.array([[x], [y]])
        pred_delta = A.dot(X) - b
        loss = pred_delta.T.dot(pred_delta)
        return loss

    def getCoord_GEO(self, points):  #使用 三角定位 获取位置坐标
        points = sorted(points, key = lambda x:x[2])
        print(points)
        find = False
        x_1, y_1, x_2, y_2 = 0,0,0,0
        for i in range(len(points) - 1):
            if(self.getStatus(points[i], points[i + 1]) == self.INTERSECTION):
                x_1, y_1, x_2, y_2 = self.getIntersection(points[i], points[i + 1])
                find = True
                break
        if(find):
            A, b = self.getMatrix(points)
            loss1 = self.getLoss(A, b, x_1, y_1)
            loss2 = self.getLoss(A, b, x_2, y_2)

            if(loss1 < loss2): # 选择误差最小的
                return x_1, y_1
            else:
                return x_2, y_2
        else:
            return None, None


    def getStatus(self, point_a, point_b):   #判断两圆的位置关系
        point_a = [float(i) for i in point_a]
        point_b = [float(i) for i in point_b]
        x_a, y_a, r_a = point_a
        x_b, y_b, r_b = point_b

        AB = pow((x_a - x_b)**2 + (y_a - y_b)**2, 0.5)

        if abs(r_a + r_b) < AB:
            return self.OUT
        elif AB >= abs(r_a - r_b):
            return self.INTERSECTION
        else:
            return self.IN



    def getIntersection(self, point_a, point_b, return_e = False): #计算两圆的交点
        point_a = [float(i) for i in point_a]
        point_b = [float(i) for i in point_b]
        x_a, y_a, r_a = point_a
        x_b, y_b, r_b = point_b

        AB = pow((x_a - x_b)**2 + (y_a - y_b)**2, 0.5)
        AE = (r_b**2 - r_a**2 - AB**2) / (-2 * AB)

        x_e = x_a + (x_b - x_a)*(AE / AB)
        y_e = y_a + (y_b - y_a)*(AE / AB)

        if return_e:
            return x_e, y_e

        CE = pow(r_a**2 - AE**2, 0.5)

        cos = sin = 0

        if y_a == y_b:
            cos = 0
            sin = 1
        elif x_a == x_b:
            cos = 1
            sin = 0
        else:
            k_ab = (y_b - y_a) / (x_b - x_a)
            k_cd = -1 / k_ab
            angle = math.atan(k_cd)

            cos = math.cos(angle)
            sin = math.sin(angle)
        x_c = x_e + cos * CE
        y_c = y_e + sin * CE
        x_d = x_e - cos * CE
        y_d = y_e - sin * CE
        return x_c,y_c,x_d,y_d




    def removeInsideCircle(self, points): # 去除大圆包含小圆的情况
        points = sorted(points, key=lambda x: x[2], reverse=True)
        # 去除包含小圆的大圆
        clean_points = []
        for i in range(len(points)):
            x_i, y_i, r_i = points[i]
            good = True
            for j in range(i + 1, len(points)):
                #if(self.getStatus(points[i], points[j]) == self.IN):
                x_j, y_j, r_j = points[j]
                dis = pow((x_i - x_j) ** 2 + (y_i - y_j) ** 2, 0.5)
                if r_i - dis > 2 * r_j:    #但大圆与小圆的边距大于 小圆的半径 时候 才舍弃该大圆
                    good = False
                    break
            if good:
                clean_points.append(points[i])
        return clean_points


    def removeInlinePoint(self,points): #去除三点共线的点
        clean_points = []
        points = sorted(points, key=lambda x: x[2])
        k_set = set()

        for j in range(len(points)):
            x_j, y_j ,_ = points[j]
            good = True

            k_set_j = set()
            for i in range(len(clean_points)):
                x_i, y_i, _ = clean_points[i]
                k = None
                if(x_i == x_j):
                    k = 'inf'
                else:
                    k = (y_j - y_i) / (x_j - x_i)

                if (k in k_set) or (k in k_set_j):
                    good = False
                    break
                else:
                    k_set_j.add(k)
            if good:
                k_set.union(k_set_j)
                clean_points.append(points[j])
        return clean_points

    def removeAbnormalPoint(self,points): # 去除异常点：圆心距离远大于半径和
        thelta = 5
        clean_points = []
        points = sorted(points, key=lambda x: x[2])

        for j in range(len(points)):
            x_j, y_j, r_j = points[j]
            good = True

            for i in range(len(clean_points)):
                x_i, y_i, r_i = clean_points[i]
                dis1 = pow((x_i - x_j)**2 + (y_i - y_j)**2, 0.5)
                dis2 = r_i + r_j
                if dis1 > thelta * dis2: #如果圆心距大于 半径的和 thelta倍 就舍弃
                    good = False
                    break
            if good:
                clean_points.append(points[j])
        return clean_points

    def getCleanPoints(self, points): # 清理数据点
        points = self.removeInsideCircle(points)
        #print(len(points), points)
        points = self.removeInlinePoint(points)
        #print(len(points), points)
        points = self.removeAbnormalPoint(points)
        #print(len(points), points)
        return points

    def getCoord(self, request, need_meta=False):
        points = []
        for r in request:
	    rssi = request[r]
            r = r[-2:].lower()
            #print(r)
            if r in self.coordination:# or r[-2:] in self.coordination:

                point = [self.coordination[r][0], self.coordination[r][1], self.rssi2distance(rssi)]
                points.append(point)
	print("process points:", points)
        x, y = self._getCoord(points)
        #response = json.dumps(response)
        resp = {"x":x, "y":y}
	
	
        if need_meta:
            meta_str = json.dumps(points)
            resp["meta1"] = meta_str
            #response = response + "\n\t" + meta_str
	
	resp["meta2"] = "\nreceive " + str(len(points)) + " points\n"
        return json.dumps(resp)


    def _getCoord(self, points):
        points = self.getCleanPoints(points)
        print("points len ", len(points))
        if len(points) == 0:
            return None, None
        elif len(points) == 1:
            return points[0][0], points[0][1]
        elif len(points) == 2:
            return self.getIntersection(points[0], points[1], return_e=True)
        else:
            return self.getCoord_MLE(points)





if __name__ == '__main__':
    t = Triangulation('./coordination')
    req = {'ssid1':0.5, 'ssid2':0.2}
    #print(t.rssi2distance_cache)
    print(t.coordination)
    #print(t.getCoord(req))
    #for i in range(-80, -40):
    #    print(i, t.rssi2distance(i) )
    req = {u'19:5A:5D:68:12:7F': u'-74'}
    z = t.getCoord(req, need_meta=True)
    print(z)







