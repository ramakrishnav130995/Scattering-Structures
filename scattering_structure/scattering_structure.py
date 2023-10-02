import numpy as np

class ScatteringStructure:
    def __innit__(self, position, geometry, arrangement, dist, scatterer_size):
        self.center_pos = position
        self.geometry = geometry
        self.arrangement = arrangement
        self.dist = dist
        self.scatterer_size = scatterer_size

        # supported arrangement types
        def arr_types(type):
            if type not in ['rectangular', 'tetrahedral', 'random', 'poisson_disc']:
                raise TypeError(f'The given geometry type {type} is not supported')
        arr_types(geometry['type'])

    def create_rectangular_pattern(self):
        max_x = self.geometry['lx']
        max_y = self.geometry['ly']
        positions = np.array([(x, y)
                              for x in np.arange(0, max_x, step=self.dist)
                              for y in np.arange(0, max_y, step=self.dist)])

        return positions

    def create_tetrahedral_pattern(self):
        max_x = self.geometry['lx']
        max_y = self.geometry['ly']

        sqrt3 = np.sqrt(3)

        positions = []
        for x in np.arange(0, max_x, step=self.dist * sqrt3):
            for y in np.arange(0, max_y, step=self.dist):
                positions.append((x, y))
            # Offset the x-coordinate by half of the step on every other row
            x += self.dist * sqrt3 / 2
            for y in np.arange(0, max_y, step=self.dist):
                positions.append((x, y))

        positions = np.array(positions)
        return positions

    def create_random_pattern(self, num_points, x_range, y_range):
        points = []
        while len(points) < num_points:
            x = np.random.uniform(x_range[0] + self.scatterer_size, x_range[1] - self.scatterer_size)
            y = np.random.uniform(y_range[0] + self.scatterer_size, y_range[1] - self.scatterer_size)
            valid = True
            for px, py in points:
                distance = np.sqrt((x - px) ** 2 + (y - py) ** 2)
                if distance < 2 * self.scatterer_size:
                    valid = False
                    break
            if valid:
                points.append((x, y))
        return np.array(points)

    def poisson_disc_sampling_pattern(self):
        pass

