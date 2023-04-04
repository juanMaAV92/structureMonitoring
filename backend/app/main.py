


from app.reports.eventEQR import EventEQR
from app.utils.seismic.eqr import processing_signal, read_csv


if __name__ == '__main__':
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

    pdf_report.generate_report(params, path_event, path_fft)
    
