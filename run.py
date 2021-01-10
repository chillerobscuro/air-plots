from pull_data import multiprocess_retrieve
from make_plots import output_plots
from make_gif import make_gif
from utils import bay_area_sensors
from datetime import datetime


# if starting fresh
sensor_list = list(bay_area_sensors)[:1000]
hours_to_pull = 48
end_time = datetime.now()
# end_time = datetime(2020, 9, 12, 0, 0)
data_resample_frequency = 1200
# data_write_location = "data/raw/testeroni.pkl"
data_write_location = "data/raw/bignew.pkl"

# plotting
plot_var = "pm_2.5"
color_range = (0, 180)

# making gif
source_dir = "./data/images/pm_2.5/"
gif_save_location = "data/gifs/sensor_movie_new.gif"
gif_fps = 8


def run_all_steps(need_to_pull: bool = True):
    if need_to_pull:
        multiprocess_retrieve(sensor_list, hours_to_pull, save_path=data_write_location, end_time=end_time,
                              resample_rate=data_resample_frequency)

    output_plots(data_write_location, var_to_viz=plot_var, color_range=color_range)

    make_gif(source_dir, gif_save_location)


if __name__ == "__main__":
    run_all_steps()
