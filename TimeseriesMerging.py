import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import joblib
from utils import string2json
# from config import TIMESTEP
import argparse
import sys

plt.interactive(True)
pd.options.display.max_columns = 15
pic_prefix = 'pic/'

data_dict_resampled = joblib.load('data/data_dict_resampled')
gamedata_dict = joblib.load('data/gamedata_dict')

parser = argparse.ArgumentParser()
parser.add_argument('--TIMESTEP', default=10, type=float)
if __debug__:
    print('SUPER WARNING!!! YOU ARE INTO DEBUG MODE', file=sys.stderr)
    args = parser.parse_args(['--TIMESTEP=10'])
else:
    args = parser.parse_args()

TIMESTEP = args.TIMESTEP


data_dict_resampled_merged = {}

def timestamp2step(times, df_start_time):
    return np.round((np.array(times) - df_start_time) / TIMESTEP).astype(int)


# player_id = list(gamedata_dict.keys())[0]  # DEBUG

for player_id in gamedata_dict:
    df_resampled4player = data_dict_resampled[player_id]
    df_resampled4player = df_resampled4player.reset_index()
    gamedata_dict4player = gamedata_dict[player_id]

    time_game_start = pd.to_datetime(gamedata_dict4player['time_game_start'], unit='s')
    time_game_end = pd.to_datetime(gamedata_dict4player['time_game_end'], unit='s')

    mask_gametime = (time_game_start < df_resampled4player['time']) & (df_resampled4player['time'] < time_game_end)

    df_resampled4player = df_resampled4player.loc[mask_gametime]  # Only data during the game is now used

    df_resampled4player['time'] = df_resampled4player['time'].apply(lambda x: x.timestamp())

    df_start_time = df_resampled4player['time'].min()

    times_kills = timestamp2step(gamedata_dict4player['times_kills'], df_start_time)  # TODO: check. I found a bug
    times_deaths = timestamp2step(gamedata_dict4player['times_is_killed'], df_start_time)  # TODO: check. I found a bug
    if 'shootout_times_start_end' in gamedata_dict4player:
        times_shootouts = timestamp2step(gamedata_dict4player['shootout_times_start_end'], df_start_time)
    else:
        times_shootouts = []

    # times_kills = np.round((np.array(gamedata_dict4player['times_kills']) - df_start_time) / TIMESTEP)
    # times_deaths = np.round((np.array(gamedata_dict4player['times_is_killed'])  - df_start_time) / TIMESTEP)
    # times_shootouts = np.round((np.array(gamedata_dict4player['shootout_times_start_end'])  - df_start_time) / TIMESTEP)
    #
    # # times_kills = [np.round(TIMESTEP * np.round(moment / TIMESTEP), 2) for moment in times_kills]  # 2 here just in case.
    # # times_deaths = [np.round(TIMESTEP * np.round(moment / TIMESTEP), 2) for moment in times_deaths]  # 2 here just in case.
    # # times_shootouts = [np.round(TIMESTEP * np.round(moment / TIMESTEP), 2) for moment in times_shootouts]  # 2 here just in case.

    df_resampled4player['step'] = timestamp2step(df_resampled4player['time'], df_start_time)
    df_resampled4player.set_index('step', inplace=True)

    df_resampled4player['kill'] = 0
    df_resampled4player['death'] = 0
    df_resampled4player['shootout'] = 0

    n_steps = len(df_resampled4player)

    for time_kill in times_kills:
        if (0 <= time_kill < n_steps):
            # df_resampled4player.loc[time_kill, 'kill'] = 1
            df_resampled4player.loc[time_kill, 'kill'] += 1  # I fixed a bug

    for time_death in times_deaths:
        if (0 <= time_death < n_steps):
            # df_resampled4player.loc[time_death, 'death'] = 1
            df_resampled4player.loc[time_death, 'death'] += 1  # I fixed a bug

    for time_shootout_start, time_shootout_end in times_shootouts:
        assert time_shootout_start <= time_shootout_end
        if (0 <= time_shootout_start < n_steps):
            # df_resampled4player.loc[time_shootout_start:time_shootout_end, 'shootout'] = 1
            df_resampled4player.loc[time_shootout_start:time_shootout_end+1, 'shootout'] += 1  # I fixed a bug

    df_resampled4player['timedelta'] = pd.to_timedelta(df_resampled4player.index.values * TIMESTEP, unit='s')

    df_resampled4player.reset_index(inplace=True)
    df_resampled4player.drop(columns=['step', 'time'], inplace=True)
    df_resampled4player.set_index('timedelta', inplace=True)

    data_dict_resampled_merged[player_id] = df_resampled4player


joblib.dump(data_dict_resampled_merged, 'data/data_dict_resampled_merged')










