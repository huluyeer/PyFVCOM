import numpy.testing as test
import numpy as np

from unittest import TestCase

from PyFVCOM.read_results import nodes2elems
from PyFVCOM.grid_tools import *


class GridToolsTest(TestCase):

    def setUp(self):
        """ Make a really simple unstructured grid of 8 elements as two rows of 4 elements. """
        self.x = np.array([0, 1, 0, 1, 0, 1, 2, 2, 2])
        self.y = np.array([0, 0, 1, 1, 2, 2, 0, 1, 2])
        self.tri = np.array([[0, 2, 1], [1, 2, 3], [2, 5, 3], [2, 4, 5], [1, 3, 7], [1, 7, 6], [3, 5, 7], [7, 5, 8]])
        self.xc = nodes2elems(self.x, self.tri)
        self.yc = nodes2elems(self.y, self.tri)
        self.z = np.array([0, 1, 1, 0, 2, 1, 2, 3, 3])

    def test_get_node_control_area(self):
        test_node_area = 2 / 3
        node = 1
        node_area = node_control_area(node, self.x, self.y, self.xc, self.yc, self.tri)
        test.assert_almost_equal(node_area, test_node_area)

    def test_get_element_control_area(self):
        test_element_area = 2
        node = 2
        art = get_area(np.asarray((self.x[self.tri[:, 0]], self.y[self.tri[:, 0]])).T,
                       np.asarray((self.x[self.tri[:, 1]], self.y[self.tri[:, 1]])).T,
                       np.asarray((self.x[self.tri[:, 2]], self.y[self.tri[:, 2]])).T)
        element_area = element_control_area(node, self.tri, art)
        test.assert_almost_equal(element_area, test_element_area)

    def test_get_control_volumes(self):
        test_node_areas = [1 / 6, 2 / 3, 2 / 3,
                           2 / 3, 1 / 6, 2 / 3,
                           1 / 6, 2 / 3, 1 / 6]
        test_element_areas = [0.5, 2, 2, 2, 0.5, 2, 0.5, 2, 0.5]
        node_areas, element_areas = control_volumes(self.x, self.y, self.tri)
        test.assert_almost_equal(node_areas, test_node_areas)
        test.assert_almost_equal(element_areas, test_element_areas)

    def test_find_nearest_point(self):
        target_x, target_y = 0.5, 0.75
        test_x, test_y, test_dist, test_index = 0, 1, np.min(np.hypot(self.x - target_x, self.y - target_y)), 2
        x, y, dist, index = find_nearest_point(self.x, self.y, target_x, target_y)
        test.assert_equal(index, test_index)
        test.assert_equal(x, test_x)
        test.assert_equal(y, test_y)
        test.assert_equal(dist, test_dist)

    def test_elem_side_lengths(self):
        diagonal = np.hypot(1, 1)
        test_lengths = [[1, diagonal, 1], [diagonal, 1, 1], [diagonal, 1, 1], [1, 1, diagonal],
                        [1, 1, diagonal], [diagonal, 1, 1], [1, diagonal, 1], [diagonal, 1, 1]]
        lengths = element_side_lengths(self.tri, self.x, self.y)
        test.assert_equal(lengths, test_lengths)

    def test_clip_triangulation(self):
        model = {key: getattr(self, key) for key in ('xc', 'yc')}
        test_clipped = [[2, 6, 7], [0, 1, 2], [7, 6, 4], [4, 1, 0], [6, 2, 4], [4, 2, 1]]
        # test_clipped = [[0, 1, 2]]
        clipped = clip_triangulation(model, 1)
        test.assert_equal(clipped, test_clipped)

    def test_mesh2grid_1(self):
        test_x, test_y, test_z = [0, 1, 2], [0, 1, 2], [[0, 1, 2], [1, 0, 1], [2, 3, 3]]
        nx, ny = 3, 3
        x, y, z = mesh2grid(self.x, self.y, self.z, nx, ny)
        test.assert_equal(x, test_x)
        test.assert_equal(y, test_y)
        test.assert_equal(z, test_z)

    def test_mesh2grid_2(self):
        test_x, test_y, test_z = [[0, 0.5, 1] for i in range(3)], [[0] * 3, [0.5] * 3, [1] * 3], [[0, 0, 1], [0, 0, 1], [1, 1, 0]]
        nnx, nny = np.array([0, 0.5, 1]), np.array([0, 0.5, 1])
        nx, ny = np.meshgrid(nnx, nny)
        x, y, z = mesh2grid(self.x, self.y, self.z, nx, ny)
        test.assert_equal(x, test_x)
        test.assert_equal(y, test_y)
        test.assert_equal(z, test_z)

    def test_line_sample(self):
        start, end = np.array((0, 0.1)), np.array((0.7, 2.1))
        test_idx = (0, 2, 3)
        test_line = np.array([[-0.0311804, 0.01091314], [0.28062361, 0.90178174], [0.38975501, 1.21358575]])
        test_dist = [0, 0.44095746, 0.59529257]
        idx, line, dist = line_sample(self.x, self.y, (start, end), return_distance=True)
        test.assert_equal(test_idx, idx)
        test.assert_almost_equal(test_line, line)
        test.assert_almost_equal(test_dist, dist)

    def test_OSGB35_to_WGS84(self):
        # Make up some fairly realistic coordinates.
        x, y = [10000, 20000], [50000, 60000]
        test_lon, test_lat = [-7.46963128, -7.34010597], [50.22103197, 50.31708046]
        lon, lat = OSGB36_to_WGS84(x, y)
        test.assert_almost_equal(lon, test_lon)
        test.assert_almost_equal(lat, test_lat)

    def test_connectivity(self):
        test_e = [[0, 1], [0, 2], [1, 2], [1, 3],
                  [1, 6], [1, 7], [2, 3], [2, 4],
                  [2, 5], [3, 5], [3, 7], [4, 5],
                  [5, 7], [5, 8], [6, 7], [7, 8]]
        test_te = [[1, 2, 0], [2, 6, 3], [8, 9, 6], [7,11, 8],
                   [3, 10, 5], [5, 14, 4], [9,12,10], [12, 13, 15]]
        test_e2t = [[0, -1], [0, -1], [0, 1], [1, 4],
                    [5, -1], [4, 5], [1, 2], [3, -1],
                    [2, 3], [2, 6], [4, 6], [3, -1],
                    [6, 7], [7, -1], [5, -1], [7, -1]]
        test_bnd = [True] * len(self.x)
        test_bnd[3] = False  # only a single non-boundary node
        e, te, e2t, bnd = connectivity(np.array((self.x, self.y)).T, self.tri)
        test.assert_equal(e, test_e)
        test.assert_equal(te, test_te)
        test.assert_equal(e2t, test_e2t)
        test.assert_equal(bnd, test_bnd)

    def test_clip_domain(self):
        extents = (0, 1.5, 0, 2)
        test_mask = np.arange(6)  # omit the easternmost nodes
        mask = clip_domain(self.x, self.y, extents)
        test.assert_equal(mask, test_mask)

    def test_find_connected_nodes(self):
        node = 2
        test_nodes = [0, 1, 3, 4, 5]
        nodes = find_connected_nodes(node, self.tri)
        test.assert_equal(nodes, test_nodes)

    def test_find_connected_elements(self):
        node = 5
        test_elements = [2, 3, 6, 7]
        elements = find_connected_elements(node, self.tri)
        test.assert_equal(elements, test_elements)

    def test_get_area(self):
        test_area = [0.5] * len(self.xc)
        area = get_area(np.asarray((self.x[self.tri[:, 0]], self.y[self.tri[:, 0]])).T,
                        np.asarray((self.x[self.tri[:, 1]], self.y[self.tri[:, 1]])).T,
                        np.asarray((self.x[self.tri[:, 2]], self.y[self.tri[:, 2]])).T)
        test.assert_equal(area, test_area)

    def test_find_bad_node(self):
        test_bad_ids = [False] * len(self.x)
        for i in [0, 4, 6, 8]:
            test_bad_ids[i] = True
        bad_ids = []
        for i in range(len(self.x)):
            bad_ids.append(find_bad_node(self.tri, i))
        test.assert_equal(bad_ids, test_bad_ids)

    def test_trigradient(self):
        test_dx = [0.9795292144557374, 0.973516444967788, -2.4679172020659035,
                   0.9868774304319136, -1.8685950121249413, 0.4735164449677718,
                   0.9138276343530278, 4.495348104056548, 2.7619518609336566]
        test_dy = [0.9743381412946664, -1.930942271353314, 1.0794506650966564,
                   0.039367708704254094, 1.3455913122791008, 1.8486495653813806,
                   1.2570462168215415, 0.5794506650966351, 0.06288323675218344]
        dx, dy = trigradient(self.x, self.y, self.z)
        test.assert_equal(dx, test_dx)
        test.assert_equal(dy, test_dy)

    def test_ind2sub(self):
        ind = 25
        shape = (10, 20)
        test_row, test_col = 1, 5
        rows, cols = ind2sub(shape, ind)
        test.assert_equal(rows, test_row)
        test.assert_equal(cols, test_col)

    def test_rotate_points(self):
        angle = 45
        test_xr = [-0.41421356, 0.29289322, 0.29289322, 1, 1, 1.70710678, 1, 1.70710678, 2.41421356]
        test_yr = [1, 0.29289322, 1.70710678, 1, 2.41421356, 1.70710678, -0.41421356, 0.29289322, 1]
        xr, yr = rotate_points(self.x, self.y, (1, 1), angle)
        test.assert_almost_equal(xr, test_xr)
        test.assert_almost_equal(yr, test_yr)

    def test_get_boundary_polygons(self):
        test_boundary_polygon_list = [[0, 2, 4, 5, 8, 7, 6, 1]]
        boundary_polygon_list = get_boundary_polygons(self.tri)
        test.assert_equal(boundary_polygon_list, test_boundary_polygon_list)

    def test_get_attached_unique_nodes(self):
        node = 2
        test_boundary_nodes = [0, 4]
        boundary_nodes = get_attached_unique_nodes(node, self.tri)
        test.assert_equal(boundary_nodes, test_boundary_nodes)

    def test_grid_metrics(self):
        test_ntve = []
        test_nbve = []
        test_nbe = []
        test_isbce = []
        test_isonb = []
        ntve, nbve, nbe, isbce, isonb = grid_metrics(self.tri)
        test.assert_equal(ntve, test_ntve)
        test.assert_equal(nbve, test_nbve)
        test.assert_equal(nbe, test_nbe)
        test.assert_equal(isbce, test_isbce)
        test.assert_equal(isonb, test_isonb)
