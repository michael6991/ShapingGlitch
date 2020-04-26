"""
Here, the apparatus for scoring a chromosome is operated.
Normally the function called here will write the given chromosome to the AWG, initialize a glitching session
through the arduino, and then receive (and maybe calculate) score from arduino.
However, during production, a simulation score will be used.
"""
from global_constants_and_functions import *

DEBUG = True


def score_chromosome(chromosome):
    if DEBUG:
        return sim_score_chromosome(chromosome)
    else:
        return glitch_score_chromosome(chromosome)


def glitch_score_chromosome(chromosome):
    raise NotImplementedError()


def sim_score_chromosome(chromosome):
    """
    as a simulation check we assume only a V shaped
    :param chromosome:
    :return:
    """
    _, y_samples = chromosome.interpolate_coordinates()
    v_pulse_samples = v_pulse_shape(0.6, 0.6, 0.6, chromosome.num_samples)
    return 1 / (np.linalg.norm(y_samples - v_pulse_samples) * np.linalg.norm(chromosome.freq - 20e6)
                + np.finfo(float).eps)


def v_pulse_shape(width: float, depth: float, loc: float, length=SAMPLE_NUM):
    assert 0 <= depth <= 1
    assert 0 <= loc <= 1
    assert width / 2 <= loc
    assert loc + width / 2 <= 1

    points = np.array([
        [0, 0],
        [loc - width / 2, 0],
        [loc, -depth],
        [loc + width / 2, 0],
        [1, 0]
    ])
    f = interp1d(points[:, 0], points[:, 1], kind='linear')
    return f(np.arange(length) / (length - 1))


if __name__ == "__main__":
    plt.plot(np.arange(SAMPLE_NUM) / (SAMPLE_NUM - 1), v_pulse_shape(0.6, 0.6, 0.6))
