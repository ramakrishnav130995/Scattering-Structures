import numpy as np
import poisson_disc


class ScatteringStructure:
    def __innit__(self, position, geometry: dict, arrangement: str, dist: float, scatterer_radius: float):
        self.center_pos = position
        self.geometry = geometry
        self.arrangement = arrangement
        self.dist = dist
        self.scatterer_radius = scatterer_radius

        # supported arrangement types
        def arr_types(type):
            if type not in ['rectangular', 'tetrahedral', 'random', 'poisson_disc']:
                raise TypeError(f'The given geometry type {type} is not supported')
        arr_types(geometry['type'])

    # ---------------------------------------
    # DIFFERENT SCATTERER DISTRIBUTIONS
    # ---------------------------------------

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

    def create_random_pattern(self, num_points):
        max_x = self.geometry['lx']
        max_y = self.geometry['ly']

        points = []
        while len(points) < num_points:
            # create random point in given range
            x = np.random.uniform(0 + self.scatterer_radius, max_x - self.scatterer_radius)
            y = np.random.uniform(0 + self.scatterer_radius, max_y - self.scatterer_radius)
            # only as point to list if it doesn't hit rest of the
            valid = True
            for px, py in points:
                distance = np.sqrt((x - px) ** 2 + (y - py) ** 2)
                if distance < 2 * self.scatterer_radius:
                    valid = False
                    break
            if valid:
                points.append((x, y))
        return np.array(points)

    def poisson_disc_sampling_pattern(self):
        max_x = self.geometry['lx']
        max_y = self.geometry['ly']

        # generate point pattern via Bridson's poisson sampling algorithm
        # https://www.cs.ubc.ca/~rbridson/docs/bridson-siggraph07-poissondisk.pdf
        points = poisson_disc.Bridson_sampling(radius=self.scatterer_radius, dims=np.array([max_x, max_y]))

        return points

    # ---------------------------------------
    # REDUCE TO SPECIFIC GEOMETRIES
    # ---------------------------------------

    def reduce_to_circle(self):
        pass

    def reduce_to_pizza_slice(self):
        pass

    # ---------------------------------------
    # VISUALIZATION AND SAVE FUNCTIONS
    # ---------------------------------------

    def plot_distribution(self):
        pass

    def plot_scatterer(self):
        pass

    def save_distribution(self):
        pass
