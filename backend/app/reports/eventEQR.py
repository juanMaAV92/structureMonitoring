from fpdf import FPDF

class EventEQR(FPDF):
    def __init__(self, title, subtitle, author, date):
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.date = date

    def header(self):
        # Rendering logo:
        self.image("/home/juanmaav92/Documents/structureMonitoring/backend/app/utils/seismic/Untitled.png", 160, 8, 30)

        # Printing title, subtitle, author and date:
        self.set_font("helvetica", "B", 20)
        self.cell(0, 10, self.title, border=0, new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("helvetica", "B", 15)
        self.cell(0, 5, self.subtitle, border=0, new_x="LMARGIN", new_y="NEXT", align="C")
        self.cell(0, 7, self.author, border=0, new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("helvetica", "B", 10)
        self.cell(0, 5, self.date, border=0, new_x="LMARGIN", new_y="NEXT", align="C")
        
        # Performing a line break:
        self.ln(10)

    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", "I", 8)
        # Printing page number:
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def create_table(self, data):
        # Column widths
        col_width = self.w / 4.5
        row_height = self.font_size * 1.5

        # Calculate x position of the table
        table_x = (self.w - col_width * 2) / 2
        # Move current x position to center of page
        self.set_x(table_x)

        # Table header
        self.set_fill_color(180, 180, 180)
        self.cell(col_width, row_height, 'Key', border=1, fill=True, align="C")
        self.cell(col_width, row_height, 'Value', border=1, fill=True, align="C")
        self.ln(row_height)
        self.set_fill_color(255, 255, 255)
        # Table rows
        for key, value in data.items():
            self.set_x(table_x)
            self.cell(col_width, row_height, str(key), border=1)
            self.cell(col_width, row_height, str(value), border=1)
            self.ln(row_height)

    def add_image_with_header(self, title, image_path, width):
        # Add title
        self.cell(0, 8, title, align="C", border=1)
        self.ln(5)

        # Add image
        image_x = (self.w - width) / 2
        self.set_x(image_x)
        self.image(image_path, w=width)
        self.ln(20)


    def generate_report(self, data, path, image_signal_path, image_spectrum_path):
        # Adding a new page to the PDF
        self.add_page()

        # Adding the table to the PDF
        for key, values in data.items():
            self.cell(0, 10, f"Tabla eje {key}", align="C")
            self.ln(8)
            self.create_table(values)
            self.ln(10)

        # Adding images to the PDF
        
        self.add_image_with_header("Gráfica tiempo eje x", image_signal_path, 100)
        self.add_image_with_header("Gráfica frecuencia eje x", image_spectrum_path, 100)

        # Saving the PDF
        self.output(f'{path}report.pdf')




if __name__ == '__main__':
    pdf_report = EventEQR(
        title="Reporte evento sismico",
        subtitle="presa bajo anchicaya",
        author="Presas e Infraestructura",
        date="2023/04/01"
    )

    data = {'x': 
            {'max_ampl': 0.16536958191468626, 
             'max_freq': 2.2758757173956066, 
             'duration': 0.2881492449019265}, 
            'y': 
            {'max_ampl': 0.19092409060723525, 
             'max_freq': 1.682169008509796, 
             'duration': 0.2941862893723288}, 
            'z': 
            {'max_ampl': 0.16728404575795575, 
             'max_freq': 2.1967148228774986, 
             'duration': 0.26498219106410636}}
    
    path = '/home/juanmaav92/Documents/structureMonitoring/backend/temp/'
    path_event = f'{path}/axis_x.jpg'
    path_fft =  f'{path}/fft_x.jpg'

    pdf_report.generate_report(data, path, path_event, path_fft)
