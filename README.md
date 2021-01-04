## Air Quality Replays

![Pretty nice tbh](docs/sensor_movie_smaller.gif)

Use historic purpleair sensor data to make a gif of air quality, temperature, or humidity. 

Use `python run.py` to run with test settings, or edit `run.py` with custom params.

The gifs are built in 3 steps:
    
1. `pull_data.py` Pulls the data from thingspeak.com, which stores up to a year of data. Uses `multiprocessing` to run
in parallel.
2. `make_plots.py` Makes a plot for each time step.
3. `make_gif.py` Combines all the plots into a single gif.

The biggest challenge is installing cartopy and it's dependencies. [Good luck.](https://scitools.org.uk/cartopy/docs/latest/installing.html)
    