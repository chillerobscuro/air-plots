import os
import time
from datetime import datetime, timedelta
from multiprocessing import Manager, Process
from multiprocessing.managers import DictProxy
from typing import Dict, List, Optional

import pandas as pd
from purpleair.sensor import Sensor

from utils import bay_area_sensors, data_cols, save_to_pkl


def retrieve_data(
    hours_to_get: int, channel: str, key: str, end_time: Optional[datetime] = None
) -> pd.DataFrame:
    """Retrieve data from thingspeak.com
    hours_to_get: How many hours of data to pull
    channel: From the sensor parent tp_primary_channel
    key: From the sensor parent par.tp_primary_key
    end_time: End of data window. Defaults to datetime.now()
    return: Dataframe
    """
    if end_time is None:
        end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours_to_get)
    url = f'https://thingspeak.com/channels/{channel}/feed.csv?api_key={key}&offset=0&average=&round=2&start={start_time.strftime("%Y-%m-%d %H:%M:%S").replace(" ", "%20")}&end={end_time.strftime("%Y-%m-%d %H:%M:%S").replace(" ", "%20")}'
    weekly_data = pd.read_csv(url)

    # Format the DataFrame
    weekly_data.rename(columns=data_cols, inplace=True)
    weekly_data["created_at"] = pd.to_datetime(
        weekly_data["created_at"], format="%Y-%m-%d %H:%M:%S %Z"
    )
    weekly_data.index = weekly_data.pop("entry_id")
    return weekly_data


def parallel_pull(
    sensor_data_dict: DictProxy,
    sensor_list: List[int],
    hours_to_get: int,
    end_time: Optional[datetime] = None,
    resample_rate: int = 3600
) -> Dict[int, pd.DataFrame]:
    """This function is called by the multiprocessing manager
    sens_dic: DictProxy object written in parallel
    sensor_list: Which sensors this core should pull for
    hrs: How many hours of data to get
    resample_rate: Downsample to this frequency to normalize all indices
    return: Dict of format {sensor_num: dataframe_of_data}
    """
    for s in sensor_list:
        try:
            sen = Sensor(s)
            dic = sen.as_dict()
            lat = dic["parent"]["meta"]["lat"]
            lon = dic["parent"]["meta"]["lon"]
            parent = sen.parent
            df = retrieve_data(
                hours_to_get,
                parent.tp_primary_channel,
                parent.tp_primary_key,
                end_time=end_time,
            )
            fields = ["created_at", "PM2.5_CF_ATM_ug/m3", "Temperature_F", "Humidity_%"]
            # Keep only interesting columns and reformat, resample
            trimmed_df = df[fields]
            trimmed_df = trimmed_df.rename(columns={"PM2.5_CF_ATM_ug/m3": "pm_2.5"})
            trimmed_df = trimmed_df.assign(lat=lat, lon=lon)
            trimmed_df.set_index("created_at", inplace=True)
            trimmed_df = trimmed_df.resample(f"{resample_rate}s").mean()
            sensor_data_dict[s] = trimmed_df
        except TypeError:
            pass
        except BaseException as e:
            print(f"Exception: {e}")
            pass
    return sensor_data_dict


def combine_dfs(
    dic: DictProxy, ind: pd.DatetimeIndex, save_path: str = "data/raw/tst.pkl"
) -> None:
    """
    dic: Dict created by parallel_pull()
    ind: DatetimeIndex with each time corresponding to one plot
    save_path: Where to pickle and save data
    """
    tm_dfs = {}
    for i in ind:
        newd = pd.DataFrame()
        tm = i.strftime("%Y-%m-%d %H:%M:%S")
        for s in dic:
            try:
                row = dic[s].loc[i]
                newd = pd.concat([newd, row], axis=1, sort=False)
            except:
                pass
        tm_dfs[tm] = newd.T.reset_index(drop=True)

    print(f"Writing data to {save_path}")
    save_to_pkl(save_path, tm_dfs)


def multiprocess_retrieve(
    sensor_list: List[int],
    hours: int,
    save_path: str = "data/raw/tst.pkl",
    end_time: Optional[datetime] = None,
    resample_rate: int = 3600,
    cores: int = -1,
) -> None:
    s = Sensor(73859)
    """Use multiple cores to pull data from thingspeak api, and save plotting data to pickle
    sensor_list: Which purpleair sensor ids to populate
    hours: How many hours of data for each sensor
    save_path: Where to save the pickled data
    end_time: End of data period. By default datetime.now()
    resample_rate: Downsample data to this rate, default 10 minutes
    cores: How many cores to use. Default how many you have
    """
    with Manager() as manager:
        print("Running multiprocess retrieve")

        if cores == -1:
            cores = os.cpu_count()
            print(f"Using {cores} cores")

        global_dict = manager.dict()
        pool = [
            Process(
                target=parallel_pull,
                args=(
                    global_dict,
                    sensor_list[i::cores],
                    hours,
                    end_time,
                    resample_rate,
                ),
            )
            for i in range(cores)
        ]

        # start all processes
        for p in pool:
            p.start()

        # make sure all processes have finished before proceeding
        for p in pool:
            p.join()

        # Create array of times to plot
        if end_time is None:
            end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        indx = pd.date_range(start=start_time, end=end_time, freq=f"{resample_rate}s")
        combine_dfs(global_dict, indx, save_path=save_path)


if __name__ == "__main__":

    strt = time.time()

    sensor_list = list(bay_area_sensors)[:20]

    hrs = 24
    end_t = datetime.now()

    pth = "data/raw/testeroni.pkl"

    multiprocess_retrieve(sensor_list, hrs, save_path=pth, end_time=end_t, resample_rate=600)

    end = time.time()
    print(f"Pulling data took {round(end - strt, 2)} seconds: ")
