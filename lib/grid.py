# -*- coding: utf-8 -*-

class Grid:
    # box: 対象とする範囲を軽度の上限下限、緯度の左限右限で指定する (e.g. [35.0, 45.0, 135.0, 145.0])
    # div: 対象範囲を何分割するかを指定する (e.g. 10)
    # セル番号の順番:
    #                   1 2 3
    #                   4 5 6
    #                   7 8 9 
    def __init__(self, box=[30.0, 45.0, 130.0, 145.0], div=100):
        self.box = box
        self.div = div
        self.dlat = (self.box[1] - self.box[0]) / float(self.div)
        self.dlong = (self.box[3] - self.box[2]) / float(self.div)

    # 与えられた緯度経度からセル番号を返す
    def get_cell(self, point):
        lat = point[0]
        long = point[1]
    
        _lat = self.box[0]
        i = 0
        while self.box[1] > _lat: # 緯度がboxの端に到達するまで
            if _lat <= lat <= (_lat + self.dlat):
                break
            else:
                _lat += self.dlat
                i += 1

        _long = self.box[2]
        j = 0
        while self.box[3] > _long:
            if _long <= long <= (_long + self.dlong):
                break
            else:
                _long += self.dlong
                j += 1

        if i >= self.div or j >= self.div:
            return None

        return (j*self.div) + i

    # 与えられたセル番号から代表点の緯度経度を返す
    def get_point(self, n):
        if n >= self.div**2:
            return None

        i = n%self.div
        j = n/self.div
        lat = self.box[0] + (self.dlat * (i+0.5))
        long = self.box[2] + (self.dlong * (j+0.5))

        return [lat, long]

if __name__ == '__main__':
    grid = Grid([30.0, 45.0, 130.0, 145.0], 3)
    cell = grid.get_cell([31.5, 142.9])
    print cell
    p = grid.get_point(cell)
    print p
    print grid.get_cell(p)
