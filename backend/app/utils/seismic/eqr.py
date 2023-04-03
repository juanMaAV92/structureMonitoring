
import obspy
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

path = '/home/juanmaav92/Documents/structureMonitoring/backend/app/utils/seismic/EQR120-2022-12-12_18-41-34.csv'

def axis_iterator():
    yield 'x'
    yield 'y'
    yield 'z'

def read_csv( path ):    
    headers = [ 'time', 'date', 'nn', 'nn1', 'nn2', 'nn3', 'x', 'y', 'z' ]
    sep_headers = ','
    sep_decimal = '.'
    df = pd.read_csv(   path, header= None, 
                        names= headers, 
                        sep= sep_headers,
                        decimal= sep_decimal )
    df['date'] = df['date'] + ' ' + df['time']
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y %H:%M:%S.%f')
    df.drop(['time'], axis=1, inplace=True)
    return df

def fft( trace, samply_frequency ):
    max_value_mg = np.max(np.abs(trace.data))    
    fft_vals = np.fft.fft(trace.data)
    fft_freq = np.fft.fftfreq(len(trace.data), 1/samply_frequency)
    max_freq_idx = np.argmax(np.abs(fft_vals[:len(fft_vals)//2]))
    max_freq = np.abs(fft_freq[max_freq_idx])

    # Calculate the amplitude of the signal.
    max_ampl = np.amax(np.abs(trace.data))

    # Calculate the duration of the signal.
    duration = np.ptp(trace.times())

    # Calculate the spectral amplitude and FFT.
    fft_vals_abs = np.abs(fft_vals)
    ampl_spectral = fft_vals_abs[:len(fft_vals)//2]
    fft_vals_abs_norm = fft_vals_abs / len(fft_vals_abs)

    return  {
        'max_value_mg' : max_value_mg,
        'max_freq'  : max_freq,
        'max_ampl'  : max_ampl,
        'duration'  : duration,
        'fft_freq'  : fft_freq,
        'amp_spectral' : ampl_spectral,
        'fft_vals'  : fft_vals_abs_norm
    }


def processing_acel( dt ):
    t0 = obspy.UTCDateTime(df['date'].iloc[0])
    dt = df['date'].diff().median().total_seconds()
    Fs = 1/dt

    param = {}
    st = []
    for i, axis in enumerate(['x', 'y', 'z']):
        tr = obspy.Trace(df[axis].values)
        tr.stats.starttime = t0
        tr.stats.delta = dt
        tr.detrend( type= 'constant')               # removing offset
        tr.filter("bandpass", freqmin=1.0, freqmax=10.0, corners=2, zerophase=True)
        st.append( tr )
        param[ axis ] = fft( tr, Fs )

    return st, param


def grap_acel( st ):
    fig, axs = plt.subplots(nrows=3, sharex=True, figsize=(8, 10))
    cnt = 0
    axis = axis_iterator()
    for tr in st:        
        axs[cnt].plot(tr.times(), tr.data)
        axs[cnt].set_ylabel(f'{next(axis)} (mg)')  
        axs[cnt].set_xlabel('Tiempo (s)')  
        cnt+=1 
    fig.suptitle('Aceleración en los ejes x, y, z', fontsize=16)
    plt.savefig( 'event.jpg')


def grap_fft( fft ):
    fig, axs = plt.subplots(nrows=3, sharex=True, figsize=(8, 10))
    cnt = 0
    axis = axis_iterator()
    for channel, data in fft.items():        
        axs[cnt].bar(data['fft_freq'][:len(data['fft_vals'])//2], data['amp_spectral'], width=1)
        axs[cnt].set_ylabel(f'{next(axis)} (mg)')  
        
        cnt+=1 
    fig.suptitle('Espectro frecuencia en los ejes x, y, z', fontsize=16)
    plt.xlabel('Tiempo (s)')
    plt.savefig( 'fft.jpg')






if __name__ == '__main__':
    df = read_csv( path )
    st, fft = processing_acel( df )
    grap_acel( st )
    grap_fft( fft )
