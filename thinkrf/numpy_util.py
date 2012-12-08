import numpy
import math


def compute_fft(data_pkt, reflevel_pkt):
    """
    Return an array of dBm values by computing the FFT of
    the passed data and reference level.

    :param data_pkt: packet containing samples
    :type data_pkt: thinkrf.vrt.DataPacket
    :param reflevel_pkt: packet containing 'reflevel' value
    :type reflevel_pkt: thinkrf.vrt.ContextPacket

    :returns: numpy array of dBm values as floats
    """
    reference_level = reflevel_pkt.fields['reflevel']

    iq_data = data_pkt.data.numpy_array()
    i_data = numpy.array(iq_data[:,0], dtype=float) / len(iq_data)
    q_data = numpy.array(iq_data[:,1], dtype=float) / len(iq_data)
    return _compute_fft(i_data, q_data, reference_level)

def _compute_fft(i_data, q_data, reference_level):
    calibrated_q = _calibrate_i_q(i_data, q_data)
    i_removed_dc_offset = i_data - numpy.mean(i_data)
    q_removed_dc_offset = calibrated_q - numpy.mean(calibrated_q)
    iq = i_removed_dc_offset + 1j * q_removed_dc_offset
    windowed_iq = iq * numpy.hanning(len(i_data))

    FFT_BASELINE = -28.5
    ADC_DYNAMIC_RANGE = 72.5
    noise_level_offset = reference_level - FFT_BASELINE - ADC_DYNAMIC_RANGE

    fft_result = numpy.fft.fftshift(numpy.fft.fft(windowed_iq))
    fft_result = 20 * numpy.log10(numpy.abs(fft_result)) + noise_level_offset

    median_index = len(fft_result) // 2
    fft_result[median_index] = (fft_result[median_index - 1]
        + fft_result[median_index + 1]) / 2
    return fft_result


def _calibrate_i_q(i_data, q_data):
    samples = len(i_data)

    sum_of_squares_i = sum(i_data ** 2)
    sum_of_squares_q = sum(q_data ** 2)

    amplitude = math.sqrt(sum_of_squares_i * 2 / samples)
    ratio = math.sqrt(sum_of_squares_i / sum_of_squares_q)

    p = (q_data / amplitude) * ratio * (i_data / amplitude)

    sinphi = 2 * sum(p) / samples
    phi_est = -math.asin(sinphi)

    return (math.sin(phi_est) * i_data + ratio * q_data) / math.cos(phi_est)

