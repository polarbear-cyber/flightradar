import matplotlib.cm as cm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import rasterio
from rasterio.plot import show
from scipy.ndimage.filters import gaussian_filter

class DataVisualizer:
    def __init__(self, db_path, table_name, geotiff_file):
        self.db_path = db_path
        self.table_name = table_name
        self.geotiff_file = geotiff_file

    def extract_data_from_db(self):
        conn = sqlite3.connect(self.db_path)
        df_from_db = pd.read_sql(f"SELECT * FROM {self.table_name}", conn)
        conn.close()
        return df_from_db

    def filter_data(self, df):
        with rasterio.open(self.geotiff_file) as src:
            left, bottom, right, top = src.bounds

            mask = (
                (df['longitude'] >= left) &
                (df['longitude'] <= right) &
                (df['latitude'] >= bottom) &
                (df['latitude'] <= top)
            )

        return df[mask]

    @staticmethod
    def plot_heatmap(x, y, s, bins=1000):
        heatmap, xedges, yedges = np.histogram2d(x, y, bins=bins)
        heatmap = gaussian_filter(heatmap, sigma=s)
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        return heatmap.T, extent
    
    def visualize_data(self, df_filtered):
        sigmas = [5]
        icao_classes = df_filtered["icao_class"].unique()
        num_classes = len(icao_classes)
        rows = int(np.ceil(num_classes / 2))
        fig, axs = plt.subplots(rows, 2, figsize=(10, 6 * rows), dpi=300)

        for i, icao_class in enumerate(icao_classes):
            ax = axs[i // 2, i % 2]
            x, y = df_filtered[df_filtered["icao_class"] == icao_class][["longitude", "latitude"]].values.T

            with rasterio.open(self.geotiff_file) as src:
                show(src, ax=ax, cmap='gray', alpha=0.7)

            img, extent = self.plot_heatmap(x, y, sigmas[0])
            img = np.where(img <= 0.02, np.nan, img)
            img = np.where(img == 0, np.nan, img)
            im = ax.imshow(img, extent=extent, origin='lower', cmap=cm.jet)
            ax.set_title(f"ICAO Class {icao_class}")

            cax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
            cbar = fig.colorbar(im, cax=cax)
            cbar.set_label('Density')

        # Apply tight layout
        plt.tight_layout()

        # Save the figure with high DPI and tight layout
        plt.savefig('output_plot.png', dpi=300, bbox_inches='tight')
        plt.show()

    def run(self):
        df = self.extract_data_from_db()
        df_filtered = self.filter_data(df)
        self.visualize_data(df_filtered)


if __name__ == "__main__":
    db_path = "flights.db"
    table_name = "flight_data"
    geotiff_file = "map.tif"

    data_visualizer = DataVisualizer(db_path, table_name, geotiff_file)
    data_visualizer.run()
