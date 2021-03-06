from global_constants_and_functions import *


class Chromosome():
    """An individual class that contains the glitch attributes as genes/locuses of a chromosome.
    """

    def __init__(self, length=N, freq=None, num_samples=SAMPLE_NUM,
                 min_freq=MIN_FREQ, max_freq=MAX_FREQ, mode_freq=MAX_FREQ,
                 max_dac_int=MAX_DAC_INT, min_dac_int=MIN_DAC_INT):
        """ Initializes new chromosome with random parameters.
        :param length: length of coordinate list (excluding endpoints)
        :param freq: frequency parameter to the AWG, determines length of pulse
        """
        self.num_samples = num_samples
        self.length = length
        self.coordinates = self.calculate_random_coordinates(self.length)
        if freq is None:
            self.freq = np.random.triangular(min_freq, mode_freq, max_freq)
        else:
            self.freq = freq
        self.max_dac_int = max_dac_int
        self.min_dac_int = min_dac_int
        self.raw_waveform_int_list = None
        self.id = uuid.uuid4()

    def __str__(self):
        return "id = {}\nfreq = {:.4g}\ncoordinates =\n{}\n".format(self.id,
                                                                    self.freq,
                                                                    np.array2string(self.coordinates, precision=3))

    def __repr__(self):
        return "id = {}, freq = {:.4g}, coordinates = {}".format(self.id,
                                                                 self.freq,
                                                                 np.array2string(self.coordinates, precision=3))

    @classmethod
    def calculate_random_coordinates(cls, length=N):
        """
        :return: random coordinates array
        """
        coordinates = np.random.random([length, 2])
        coordinates[:, 1] = -1 + 2 * coordinates[:, 1]  # set y values between -1 and 1
        coordinates[:, 0] = np.sort(coordinates[:, 0])  # sort x values
        return coordinates

    def sort_coordinates(self):
        """
        Sort coordinates with ascending x values.
        Remove duplicates in x coordinates if found, and add random points instead.
        :return:
        """
        self.coordinates = self.coordinates[self.coordinates[:, 0].argsort()]  # sort x values
        indices_to_remove = np.argwhere(np.diff(self.coordinates[:, 0], axis=0) == 0)
        if indices_to_remove.size > 0:
            self.remove_points(indices_to_remove)
            # add random points instead of deleted ones
            self.add_random_points(indices_to_remove.size)

    def interpolate_coordinates(self, interp_method='quadratic'):
        """
        Convert coordinates to array of integers to be sent to AWG.
        *** Currently offset not supported. ***
        :return: x_samples, y_samples
        """
        coordinates_to_interpolate = np.concatenate([[[0, 0]], self.coordinates, [[1, 0]]], axis=0)
        interp_func = interp1d(coordinates_to_interpolate[:, 0],
                               coordinates_to_interpolate[:, 1], kind=interp_method)
        x_samples = np.arange(self.num_samples) / (self.num_samples - 1)
        y_samples = interp_func(x_samples)
        return x_samples, y_samples

    def plot_waveform_uncut(self):
        """
        plot the waveform this chromosome represents "ideally".
        """
        x_samples, y_samples = self.interpolate_coordinates()
        fig, ax = plt.subplots()
        ax.plot(x_samples, y_samples, c='b')
        ax.scatter(self.coordinates[:, 0], self.coordinates[:, 1], c='r')
        ax.grid()

    def calc_raw_waveform_int(self):
        """
        Calculate raw waveform data in integer type
        """
        _, y_samples = self.interpolate_coordinates()
        y_samples *= self.max_dac_int
        y_samples[y_samples > self.max_dac_int] = self.max_dac_int
        y_samples[y_samples < self.min_dac_int] = self.min_dac_int
        self.raw_waveform_int_list = (np.int_(np.round(y_samples))).tolist()

    def plot_waveform_int(self):
        self.calc_raw_waveform_int()
        x_samples = np.arange(self.num_samples) / (self.num_samples - 1)
        fig, ax = plt.subplots()
        ax.plot(x_samples, self.raw_waveform_int_list, c='b')
        ax.scatter(self.coordinates[:, 0], self.coordinates[:, 1] * self.max_dac_int, c='r')
        ax.grid()

    def generate_binary_data_string(self):
        """
        :return: string of data to visualize what is sent to the AWG
        """
        self.calc_raw_waveform_int()
        binary_string = ''.join([convert_int_to_comp2_binary_string(x, 16) for x in self.raw_waveform_int_list])
        return binary_string

    def generate_bin_stream_to_awg(self):
        """
        :return: string to send to AWG
        """
        self.calc_raw_waveform_int()
        return b''.join([convert_int_to_comp2_ascii(x, 2) for x in self.raw_waveform_int_list])

    def add_noise(self):
        """
        add noise to coordinates.
        :return:
        """
        self.coordinates[:, 1] += np.random.randn(self.length) * 0.1
        self.freq += np.random.randn() * MIN_FREQ

    def is_point_in_chromosome(self, point) -> bool:
        """
        Checks whether a point exists in a chromosome sequence.
        :param point: numpy array of size 1x2.
        """
        return any([(self.coordinates[i] == point).all() for i in range(self.coordinates.shape[0])])

    def is_x_in_chromosome(self, point) -> bool:
        """
        Checks whether an x value of point exists in a chromosome sequence.
        :param point: numpy array of size 1x2.
        """
        return (self.coordinates[:, 0] == point[0]).any()

    def remove_points(self, indices_to_remove):
        """
        remove points from chromosome.
        :param ind:
        :return:
        """
        indices_to_remove = np.array(indices_to_remove)
        if self.length > len(indices_to_remove):
            self.coordinates = np.delete(self.coordinates, indices_to_remove, axis=0)
            self.length -= len(indices_to_remove)

    def add_random_points(self, num_of_points):
        """
        add random point to chromosome.
        :return:
        """
        random_points = np.random.random([num_of_points, 2])
        random_points[:, 1] = -1 + 2 * random_points[:, 1]
        self.coordinates = np.concatenate([self.coordinates, random_points], axis=0)
        self.length += num_of_points
        self.coordinates = self.coordinates[self.coordinates[:, 0].argsort()]  # sort x values

    def generate_new_id(self):
        self.id = uuid.uuid4()

    def make_copy(self):
        """
        return identical copy with different ID.
        :return:
        """
        copy = deepcopy(self)
        copy.generate_new_id()
        return copy


if __name__ == "__main__":
    plt.close('all')
    plt.close()
    c = Chromosome()
    c.plot_waveform_int()
    binstring = c.generate_bin_stream_to_awg()
