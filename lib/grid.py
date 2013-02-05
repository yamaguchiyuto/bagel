# -*- coding: utf-8 -*-

class Grid:
    """
    box: Specify target region by upper, lower, right-most, left-most point (e.g. [35.0, 45.0, 135.0, 145.0])
    div: Specify the number of division
    The order of cell number in the box:
                      1 2 3
                      4 5 6
                      7 8 9 
    """

    def __init__(self, box=[30.0, 45.0, 130.0, 145.0], div=100):
        self.box = box
        self.div = div
        self.dlat = (self.box[1] - self.box[0]) / float(self.div) # dlat denotes the width of a cell
        self.dlongi = (self.box[3] - self.box[2]) / float(self.div) # dlongi denotes the height of a cell

    def get_cell(self, point):
        """
        Returns cell number corresponding to the input (latitude, longitude) tuple
        """

        lat = point[0]
        longi = point[1]
    
        _lat = self.box[0] # start from the leftmost point
        i = 0
        while self.box[1] > _lat:
            if _lat <= lat <= (_lat + self.dlat): break

            _lat += self.dlat
            i += 1
        else:
            return None # not found

        _longi = self.box[2] # start from the upmost point
        j = 0
        while self.box[3] > _longi:
            if _longi <= longi <= (_longi + self.dlongi): break

            _longi += self.dlongi
            j += 1
        else:
            return None # not found

        return (j*self.div) + i

    def get_point(self, n):
        """
        Returns (latitude, longitude) tuple correnponding to the input cell number
        """

        if n >= self.div**2:
            return None

        i = n % self.div # column number
        j = n / self.div # row number

        leftmost = self.box[0]
        upmost = self.box[2]

        width_offset = self.dlat * (i + 0.5) # 0.5 guarantees that the point to be returned is the center of the cell
        height_offset = self.dlongi * (j + 0.5)

        lat = leftmost + width_offset
        longi = upmost + height_offset

        return [lat, longi]

if __name__ == '__main__':
    grid = Grid([30.0, 45.0, 130.0, 145.0], 3)
    cell = grid.get_cell([31.5, 142.9])
    print cell
    p = grid.get_point(cell)
    print p
    print grid.get_cell(p)
