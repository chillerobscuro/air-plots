import datetime
import os
import pickle
import warnings
from os import walk
from typing import Tuple

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.cbook
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils import aqi_from_pm, bay_area_sensors, load_from_pkl, title_dict

warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)


def output_plots(
    df_list_path: str,
    var_to_viz: str = "temp_f",
    save_path: str = "./data/images/",
    figsize: Tuple[float, float] = (5., 7.5),
    color_range: Tuple[int, int] = (0, 100),
    cmap: str = "RdYlGn_r",
) -> None:
    """Makes plots for each timestep in input data
    df_list_path: Path to saved data from pull_data.py
    var_to_viz: Which variable to visualize
    save_path: Directory to save plots
    figsize: Size of output plots
    color_range: Min and Max value for making the colorbar
    cmap: Color mapping for plots and colorbar. "RdYlGn_r" and "plasma" work best
    """
    save_path += f"{var_to_viz}/"
    df_list = load_from_pkl(df_list_path)
    # print(df_list)
    print(f"Saving images for {len(df_list)} dfs")
    for now in df_list:
        df = df_list[now]
        if df.empty:
            print(f'No data for {now}')
            continue
        fl_name = f"{now}_map.png"

        # check if file already has image
        cont = 1
        for (_, _, fls) in walk(save_path):
            if fl_name in fls:
                cont = 0
        if not cont:
            continue

        # Create the figure and the axes
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        # lat and lon coords to plot
        # extent = [-128, -65, 23, 50.5]  # whole USA
        extent = [-123, -121.75, 37, 38.75]  # Bay Area
        # extent = [-122.65, -122.15, 37.6, 38.]  # SF city Area

        df = df[df["lon"].between(extent[0], extent[1])]
        df = df[df["lat"].between(extent[2], extent[3])]
        lat = df["lat"].values
        lon = df["lon"].values

        # Variable from which to generate the color gradient
        if var_to_viz in ["pm_2.5_old", "PM2.5_CF_ATM_ug/m3"]:
            colors = df[var_to_viz].fillna(-1).apply(aqi_from_pm).values

        elif var_to_viz == "temp_f":
            colors = df[var_to_viz].values - 8

        else:
            colors = df[var_to_viz]

        # Display some map info
        ax.set_extent(extent)
        land10m = cfeature.NaturalEarthFeature(
            "physical",
            "land",
            "10m",
            edgecolor="black",
            facecolor="lightgray",
            linewidth=0.5,
        )
        ax.add_feature(land10m)

        # Add scatter points for each coordinate pair
        c_min, c_max = color_range[0], color_range[1]
        scatter = ax.scatter(
            lon,
            lat,
            marker="o",
            c=colors,
            cmap=cmap,
            zorder=5,
            s=5,
            vmin=c_min,
            vmax=c_max,
        )

        # Add scale
        plt.cm.ScalarMappable(cmap=cmap)
        plt.colorbar(scatter, fraction=0.06542, pad=0).set_label(
            f"{title_dict[var_to_viz]}", rotation=90
        )
        ax.set_facecolor("lightblue")
        plt.title(f"{title_dict[var_to_viz]} at {now}")

        if not os.path.exists(save_path):
            os.makedirs(save_path)
        plt.savefig(save_path + fl_name, dpi=300, bbox_inches="tight")
        plt.close()


if __name__ == "__main__":
    fl = "data/raw/testeroni.pkl"
    var = "pm_2.5_old"
    # var = 'Temperature_F'
    # var = 'Humidity_%'
    output_plots(fl, var_to_viz=var)
