import sys
import math

HARMONIC_COUNT = 64
MAX_LEVEL = 127

def compute(n, waveform_params):
    (a, b, c, xp, d, e, yp) = waveform_params

    x = n * math.pi * xp
    y = n * math.pi * yp

    module1 = 1.0 / math.pow(n, a)
    module2 = math.pow(math.sin(x), b) * math.pow(math.cos(x), c)
    module3 = math.pow(math.sin(y), d) * math.pow(math.cos(y), e)

    # Should we take absolute values of the sinusoids or not?
    result = module1 * module2 * module3
    #print('    compute = {}'.format(result))
    return result

def get_level(harmonic_number, waveform_params, max_level=127):
    #a_max = compute(1, waveform)
    a_max = 1.0
    a = compute(harmonic_number, waveform_params)
    v = math.log(math.fabs(a / a_max), 2.0)
    #print('a_max = {}, v = {}'.format(a_max, v))
    level = max_level + 8 * v
    if level < 0:
        return 0
    else:
        return level

def get_sine_levels():
    """Get list of levels with the first harmonic set to full and the rest to zero."""
    levels = [0] * HARMONIC_COUNT
    levels[0] = MAX_LEVEL
    return levels

def get_saw_levels():
    """Get level for 1/n for each harmonic."""
    levels = []
    for i in range(HARMONIC_COUNT):
        n = i + 1  # harmonic numbers start at 1
        a = 1.0 / float(n)
        print(n, a)
        level = get_level(a)
        levels.append(level)
    return levels

def get_sqr_levels():
    """Get the sawtooth levels and take out the even harmonics to get square levels."""
    saw_levels = get_saw_levels()
    levels = []
    for i in range(len(saw_levels)):
        n = i + 1
        level = saw_levels[n] if n % 2 != 0 else 0
        levels.append(level)
    return levels

def get_tri_levels():
    """Get levels for amplitude 1/n^2 for each harmonic n."""
    levels = []
    negative = False  # is current harmonic negative?
    for h in range(HARMONIC_COUNT):
        n = h + 1  # harmonic numbers start at 1
        level = 0
        if n % 2 != 0: # using only odd harmonics
            a = 1.0 / float(n * n)
            if negative:
                a = -a
                negative = not negative
            level = get_level(a)
        levels.append(level)
    return levels

levels_function_table = {
    'sin': get_sine_levels,
    'saw': get_saw_levels,
    'sqr': get_sqr_levels,
    'tri': get_tri_levels
}

def get_harmonic_levels(waveform):
    func = levels_function_table[waveform]
    return func()
