import numpy as np
import poisson_disc
import matplotlib.pyplot as plt
import math


class ScatteringStructure:
    def __init__(self, geometry: dict, arrangement: dict, scatterer_radius: float, position=(0, 0)):
        self.center_pos = position
        self.geometry = geometry
        self.arrangement = arrangement
        self.scatterer_radius = scatterer_radius

        self.points = None
        # create arrangement based on class definition
        if arrangement['type'] == 'rectangular':
            self.points = self.create_rectangular_pattern()
        elif arrangement['type'] == 'tetrahedral':
            self.points = self.create_tetrahedral_pattern()
        elif arrangement['type'] == 'random':
            self.points = self.create_random_pattern()
        elif arrangement['type'] == 'poisson_disc':
            self.points = self.create_poisson_disc_sampling_pattern()
        else:
            raise TypeError(f'The given arrangement type {self.arrangement} is not supported')

        # reduce arrangement from box to fill a pizza slice or circle
        # TODO

    # ---------------------------------------
    # DIFFERENT SCATTERER DISTRIBUTIONS
    # ---------------------------------------

    def create_rectangular_pattern(self):
        max_x = self.geometry['lx']
        max_y = self.geometry['ly']
        dist = self.arrangement['dist']
        positions = np.array([(x, y)
                              for x in np.arange(0 + self.scatterer_radius, max_x - self.scatterer_radius,
                                                 step=dist)
                              for y in np.arange(0 + self.scatterer_radius, max_y - self.scatterer_radius,
                                                 step=dist)])

        return positions

    def create_tetrahedral_pattern(self):
        # TODO does not work
        max_x = self.geometry['lx']
        max_y = self.geometry['ly']
        dist = self.arrangement['dist']
        sqrt3 = np.sqrt(3)

        positions = []
        off_center = True  # first iteration will be off_center = False
        for x in np.arange(0 + self.scatterer_radius, max_x, step=dist):
            off_center = not off_center
            for y in np.arange(0, max_y, step=dist * sqrt3):
                if off_center:
                    positions.append((x, y))
                else:
                    positions.append((x + 0.5 * dist, y))
            # Offset the x-coordinate by half of the step on every other row
            x += dist * sqrt3 / 2
            for y in np.arange(0, max_y, step=dist):
                positions.append((x, y))

        positions = np.array(positions)
        return positions

    def create_random_pattern(self):
        # TODO can be done faster
        max_x = self.geometry['lx']
        max_y = self.geometry['ly']

        # if the structure should just be plainly instanced
        if not self.arrangement['optimization']:
            points = []
            num_points = self.arrangement['num_points']
            while len(points) < num_points:
                # create random point in given range
                x = np.random.uniform(0 + self.scatterer_radius, max_x - self.scatterer_radius)
                y = np.random.uniform(0 + self.scatterer_radius, max_y - self.scatterer_radius)
                # only as point to list if it doesn't hit rest of the
                valid = True
                for px, py in points:
                    distance = np.sqrt((x - px) ** 2 + (y - py) ** 2)
                    if distance < 4 * self.scatterer_radius:
                        valid = False
                        break
                if valid:
                    points.append((x, y))
            return np.array(points)
        # otherwise a point is added until the target RMS is hit
        else:
            points = []
            # the loop is done until it fails
            # only later the solution with the closest to target_rms is picked
            target_rms = self.arrangement['target_rms']
            best_points = []
            best_rms = 0
            i = 0
            while i < 20:
                # create random point in given range
                x = np.random.uniform(0 + self.scatterer_radius, max_x - self.scatterer_radius)
                y = np.random.uniform(0 + self.scatterer_radius, max_y - self.scatterer_radius)
                # only as point to list if it doesn't hit rest of the
                point_valid = True
                for px, py in points:
                    distance = np.sqrt((x - px) ** 2 + (y - py) ** 2)
                    if distance < 4 * self.scatterer_radius:
                        point_valid = False
                        # set false-try counter
                        i += 1
                        break
                if point_valid:
                    # reset false-try counter
                    i = 0
                    points.append((x, y))
                    # test if this is the best solution until now
                    current_rms = self.rms(points)
                    print('RMS', current_rms)
                    if abs(current_rms-target_rms) < abs(best_rms-target_rms):
                        print('RMS IMPROVED')
                        best_rms = current_rms
                        best_points = points
            return np.array(best_points)

    def create_poisson_disc_sampling_pattern(self):
        # TODO implement optimization
        max_x = self.geometry['lx']
        max_y = self.geometry['ly']

        # generate point pattern via Bridson's poisson sampling algorithm
        # https://www.cs.ubc.ca/~rbridson/docs/bridson-siggraph07-poissondisk.pdf
        points = poisson_disc.Bridson_sampling(radius=3 * self.scatterer_radius, dims=np.array([max_x, max_y]))

        return points

    # ---------------------------------------
    # REDUCE TO SPECIFIC GEOMETRIES
    # ---------------------------------------

    def reduce_to_circle(self):
        pass

    def reduce_to_pizza_slice(self):
        pass

    # ---------------------------------------
    # OTHER FUNCTIONS
    # ---------------------------------------

    def rms(self, points=None):
        # use class-set distribution of points
        if points is None:
            p = self.points
        # otherwise use given
        else:
            p = points
        # compute rms
        n = len(p)
        if n == 0:
            return 0
        else:
            outer_sum = 0
            for (px, py) in p:
                inner_sum = 0
                for (x, y) in p:
                    inner_sum += math.dist([px, py], [x, y]) ** 2
                outer_sum += (inner_sum / n) ** 0.5
            outer_sum *= 1 / n

            return outer_sum

    def plot_distribution(self):
        # Unzip data into x and y
        x, y = zip(*self.points)

        # Create a scatter plot with marker size
        plt.scatter(x, y, s=np.pi * self.scatterer_radius ** 2)

        # Set aspect ratio to equal
        plt.gca().set_aspect('equal')
        plt.xlabel('μm')
        plt.ylabel('μm')

        # Display the plot
        plt.show()

    def plot_scatterer(self):
        pass

    def save_distribution(self):
        pass
