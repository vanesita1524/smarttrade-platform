import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import seaborn as sns
from pathlib import Path

def generate_ecopetrol_graph():
    # Configurar el estilo
    plt.style.use('bmh')  # Usamos un estilo incorporado de matplotlib
    
    # Leer el CSV
    csv_path = Path(__file__).parent / 'static' / 'data' / 'Ecopetrol_unificado_limpio.csv'
    df = pd.read_csv(csv_path, sep=';')
    
    # Convertir la columna Fecha a datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    # Crear la figura y los ejes
    plt.figure(figsize=(12, 6))
    
    # Graficar los precios de cierre
    plt.plot(df['Fecha'], df['Precio cierre'], 
            linewidth=2, 
            label='Precio de Cierre')
    
    # Configurar el título y etiquetas
    plt.title('Histórico Precio de Cierre Ecopetrol', 
            fontsize=14, 
            pad=20)
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Precio (COP)', fontsize=12)
    
    # Formatear las fechas en el eje x
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    
    # Añadir cuadrícula
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Añadir leyenda
    plt.legend()
    
    # Ajustar los márgenes
    plt.tight_layout()
    
    # Guardar el gráfico
    output_path = Path(__file__).parent / 'static' / 'img' / 'ecopetrol_history.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    generate_ecopetrol_graph()