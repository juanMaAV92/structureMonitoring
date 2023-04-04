
import obspy
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict




def read_csv( path: str ) -> pd.DataFrame:    
    headers = [ 'time', 'date', 'nn', 'nn1', 'nn2', 'nn3', 'x', 'y', 'z' ]
    sep_headers = ','
    sep_decimal = '.'
    df = pd.read_csv(   path, header= None, names= headers, sep= sep_headers,decimal= sep_decimal )
    df['date'] = df['date'] + ' ' + df['time']
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y %H:%M:%S.%f')
    df.drop(['time'], axis=1, inplace=True)
    return df

def processing_spectrum( tr: obspy.Trace, samply_frequency: float, axis_name: str, path: str ):
    
     # Calculate the amplitude of the signal.
    max_ampl = np.amax(np.abs(tr))

    fft_vals = np.fft.fft(tr)
    fft_freq = np.fft.fftfreq(len(tr), 1/samply_frequency)
    max_freq_idx = np.argmax(np.abs(fft_vals[:len(fft_vals)//2]))
    max_freq = np.abs(fft_freq[max_freq_idx])
  
    # Calculate the duration of the signal.
    duration = np.ptp(tr)

    # Calculate the spectral amplitude and FFT.
    fft_vals_abs = np.abs(fft_vals)
    ampl_spectral = fft_vals_abs[:len(fft_vals)//2]
    fft_vals_abs_norm = fft_vals_abs / len(fft_vals_abs)

    graph_fft( fft_freq, fft_vals_abs_norm, ampl_spectral, axis_name, path )
        
    return  {
        'max_ampl'  : max_ampl,
        'max_freq'  : max_freq,
        'duration'  : duration
    }


def processing_signal( df: pd.DataFrame, path: str ) -> Dict:
    t0 = obspy.UTCDateTime(df['date'].iloc[0])
    dt = df['date'].diff().median().total_seconds()
    Fs = 1/dt

    param = {}
    for axis in ['x', 'y', 'z']:
        tr = obspy.Trace(df[axis].values)
        tr.stats.starttime = t0
        tr.stats.delta = dt
        tr.detrend( type= 'constant')               # removing offset
        tr.filter("bandpass", freqmin=1.0, freqmax=10.0, corners=2, zerophase=True)
        param[ axis ] = processing_spectrum( tr, Fs, axis, path )
        graph_signal( tr, axis, path )

    return param


def graph_signal( tr: obspy.Trace, axis_name: str, path: str )-> None:
    fig, axs = plt.subplots()  
    axs.plot(tr.times(), tr.data)
    axs.set_ylabel(f'eje {axis_name.upper()} [mg]')  
    axs.set_xlabel('Tiempo [s]')  
    plt.savefig( f'{path}axis_{axis_name}.jpg')
    plt.close(fig)


def graph_fft( fft_freq: np.ndarray, fft_vals: np.ndarray, amp_spectral:  np.ndarray, axis_name: str, path: str ):
    fig, axs = plt.subplots()       
    axs.bar(fft_freq[:len(fft_vals)//2], amp_spectral, width=1)
    axs.set_ylabel(f'eje {axis_name} [mg]')  
    axs.set_xlabel('Frecuencia [Hz]')     
    plt.savefig( f'{path}fft_{axis_name}.jpg')
    plt.close(fig)




if __name__ == '__main__':
    from app.reports.eventEQR import EventEQR
    path = '/home/juanmaav92/Documents/structureMonitoring/backend/temp/'
    file = 'EQR120-2022-12-12_18-41-34.csv'
    df = read_csv( path+file )
    params = processing_signal( df, path )

    pdf_report = EventEQR(
        title="Reporte evento sismico",
        subtitle="presa bajo anchicaya",
        author="Presas e Infraestructura",
        date="2023/04/01"
    )

    path_event = f'{path}/axis_x.jpg'
    path_fft =  f'{path}/fft_x.jpg'

    pdf_report.generate_report(params, path, path_event, path_fft)

    

    
