import numpy as np
import cv2


class StarMap:

    @classmethod
    def from_database(cls, angular_positions, **kwargs):
        return StarMap(
            len(angular_positions),
            angular_positions=np.array(angular_positions),
            **kwargs,
        )

    def __init__(
            self,
            num_stars,
            angular_positions=None,
            background_colour=[0, 0, 0],
            star_colour=[255, 255, 255],
            constellation_colour=[243, 242, 165],
            stellar_radii=1):
        self._num_stars = num_stars
        self._background_colour = background_colour
        self._star_colour = star_colour
        self._constellation_colour = constellation_colour
        self._stellar_radii = stellar_radii
        self._edges = []

        if angular_positions is None:
            self._angular_positions = np.random.rand(self._num_stars, 2)
            self._angular_positions[:, 0] *= 2 * np.pi
            self._angular_positions[:, 1] = np.arccos(
                2 * self._angular_positions[:, 1] - 1
            )
        else:
            self._angular_positions = angular_positions

    def write_texture(self, resolution, path):
        texture = np.empty((resolution[0], resolution[1], 3))
        texture[..., :] = self._background_colour

        image_positions = self._angular_positions / np.pi
        image_positions[:, 0] *= resolution[1] / 2 # x
        image_positions[:, 1] *= resolution[0] # y
        image_positions = image_positions.astype(int)

        for position in image_positions:
            cv2.ellipse(
                texture,
                tuple(position),
                (
                    int(
                        self._stellar_radii
                        * (2 * np.abs(position[1] / resolution[0] - 0.5) + 1)**2.25 # hacks for the hackathon
                    ),
                    self._stellar_radii,
                ),
                0,
                0,
                360,
                self._star_colour,
                -1,
            )

        for edge in self._edges:
            point_0 = image_positions[edge[0]]
            point_1 = image_positions[edge[1]]
            cv2.line(
                texture,
                tuple(point_0),
                tuple(point_1),
                self._constellation_colour,
                self._stellar_radii,
            )
        cv2.imwrite(path, texture)
        # map = Basemap(projection='cyl', lat_0=0, lon_0=0)

        # map.drawmapboundary(fill_color='black')

        # for lon in range(0, 360, 20):
        #     for lat in range(-60, 90, 30):
        #         map.tissot(lon, lat, 4, 50)

        # plt.show()

    @property
    def num_stars(self):
        return self._num_stars

    @property
    def angular_positions(self):
        """"""
        return self._angular_positions

    @property
    def edges(self):
        return self._edges

    def add_edges(self, new_edges):
        self._edges.extend(new_edges)

    def get_stars_within_angle(self, star_index, min_angle=0.005, max_angle=1.5):
        """
        """
        indices = []
        star_position = self._angular_positions[star_index]
        for index, position in enumerate(self._angular_positions):
            if index == star_index:
                continue
            angular_distance = self._distance_between_angular_positions(
                position,
                star_position,
            )
            if angular_distance > min_angle and angular_distance < max_angle:
                indices.append(index)

        return indices

    def get_angle_between_stars(self, index_0, index_1):
        difference = self._angular_positions[index_1] - self._angular_positions[index_0]
        return np.arctan2(difference[1], difference[0])

    @staticmethod
    def _distance_between_angular_positions(position_0, position_1):
        """
        """
        delta_theta = position_1[0] - position_0[0]
        delta_phi = position_1[1] - position_0[1]

        return np.sqrt(delta_theta**2 + delta_phi**2)

    def get_distance_between_stars(self, star_index_0, star_index_1):
        """
        """
        position_0 = self._angular_positions[star_index_0]
        position_1 = self._angular_positions[star_index_1]

        return self._distance_between_angular_positions(position_0, position_1)

    def get_distance_to_nearest_star(self, angular_position):
        """
        """
        distances = [
            self._distance_between_angular_positions(position, angular_position)
            for position in self._angular_positions
        ]
        return np.argmin(distances), np.min(distances)
