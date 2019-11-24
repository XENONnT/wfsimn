
import pkg_resources
import numpy as np
from scipy import fftpack
import matplotlib.pyplot as plt
import seaborn as sns


class visualizer():

    def __init__(self, wf):
        self.wf = wf
        sns.set(style='whitegrid')
        self.reset_to_write_cbar = False


    def show_pulse(self, pmtid, save=False, filename='pulse.png'):

        time = np.arange(0, 1000, 2)
        pulse = self.wf[:, pmtid]
        sns.lineplot(time, pulse)
        plt.xlabel('time (ns)')
        plt.ylabel('ADC/2ns')
        #plt.ylim(-30, 120)
        if save is True: plt.savefig(filename)

        return

    def show_sum_pulse(self, save=False, filename='pulse_sum.png'):

        time = np.arange(0, 1000, 2)
        pulse = np.sum(self.wf, axis=1)
        sns.lineplot(time, pulse)
        plt.xlabel('time (ns)')
        plt.ylabel('ADC/2ns')
        #plt.ylim(-30, 120)
        if save is True: plt.savefig(filename)

        return

    def show_tops(self, num_shown = 5, save=False, filename='pulse_top.png'):

        time = np.arange(0, 1000, 2)

        max_list = self.wf.max(axis=0)
        max_order = np.sort(max_list)[::-1]
        index_pmts = np.where(max_list > max_order[num_shown])[0]

        for index_pmt in index_pmts:
            pulse = self.wf[:, index_pmt]
            sns.lineplot(time, pulse, label='PMT#'+str(index_pmt))

        plt.xlabel('time (ns)')
        plt.ylabel('ADC/2ns')

        if save is True: plt.savefig(filename)
        return

    def show_power_spectrum(self, pmtid):

        pulse = self.wf[:, pmtid]
        fft_wave = fftpack.fft(pulse)
        fft_fre = fftpack.fftfreq(n=pulse.size, d=2.e-9)

        plt.plot(fft_fre, fft_wave.real, label="real part")
        plt.plot(fft_fre, fft_wave.imag, label="imaginary part")
        plt.xscale('log')
        # plt.ylim(-400, 400)
        plt.xlabel("frequency (Hz)")
        plt.legend()

        return

    def show_map(self, timebin, save=False, filename='map.png'):

        pulse = self.reshape_to_2d(self.wf)

        print('shape', pulse.shape)
        #plt.imshow(pulse[timebin].T, vmax=120, vmin=-30)
        plt.imshow(pulse[timebin], vmax=120, vmin=-30)


        plt.title('Time ' + str(int(timebin)) + 'bins')
        plt.xlabel(r'PMT $\theta$ a.u.')
        plt.ylabel(r'PMT $Z$ a.u.')
        if self.reset_to_write_cbar == False:
            cbar = plt.colorbar(orientation='horizontal', pad=0.28)
            cbar.set_label('ADC Value')
        plt.xticks([0, 4, 8, 12, 16])
        plt.yticks([0, 2, 4])

        if save == True:
            plt.savefig(filename)

        self.reset_to_write_cbar = True

        return

    def reshape_to_2d(self, wfs):
        # wfs (500, 120)

        # PMT map
        pmt_list = np.array([
             4,  8,  76,  72,  1,  5,  9,  77,  73,  2,  6, 10,  78,  74,  3,  7, 11,  79,  75,  0,
            16, 20,  84,  80, 13, 17, 21,  85,  81, 14, 18, 22,  86,  82, 15, 19, 23,  87,  83, 12,
            28, 32,  92,  88, 25, 29, 33,  93,  89, 26, 30, 34,  94,  90, 27, 31, 35,  95,  91, 24,
            40, 44, 100,  96, 37, 41, 45, 101,  97, 38, 42, 46, 102,  98, 39, 43, 47, 103,  99, 36,
            52, 56, 108, 104, 49, 53, 57, 109, 105, 50, 54, 58, 110, 106, 51, 55, 59, 111, 107, 48,
            64, 68, 116, 112, 61, 65, 69, 117, 113, 62, 66, 70, 118, 114, 63, 67, 71, 119, 115, 60 ])

        wfs = wfs[:, pmt_list]
        wfs = np.reshape(wfs, (500, 6, 20))
        return wfs

