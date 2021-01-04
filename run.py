from pull_data import multiprocess_retrieve
from make_plots import output_plots
from make_gif import make_gif
from utils import bay_area_sensors
from datetime import datetime


# if starting fresh
sensor_list = list(bay_area_sensors)[:2000]
hours_to_pull = 24
end_time = datetime.now()
data_resample_frequency = 1200
data_write_location = "data/raw/testeroni.pkl"

# plotting
plot_var = "pm_2.5"
color_range = (0, 180)

# making gif
source_dir = "./data/images/pm_2.5/"
gif_save_location = "data/gifs/sensor_movie.gif"
gif_fps = 8


if __name__ == "__main__":
    need_to_pull = True
    if need_to_pull:
        multiprocess_retrieve(sensor_list, hours_to_pull, save_path=data_write_location, end_time=end_time,
                              resample_rate=data_resample_frequency)

    output_plots(data_write_location, var_to_viz=plot_var, color_range=color_range)

    make_gif(source_dir, gif_save_location)


"""
TODO
 - fix dir structure
 - func to find nearby sensors (outdoor only)
"""
