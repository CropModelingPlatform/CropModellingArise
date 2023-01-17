#!/usr/bin/env python

import os
import xarray as xr
import numpy as np


class Tools:

    def load_mask(file_path):
        ds_mask = xr.open_dataset(file_path)
        df_mask = ds_mask.to_dataframe().dropna(axis=0, how="any")
        df_mask = df_mask.reset_index()
        df_mask = df_mask.astype(np.float64).round(4)
        df_mask = df_mask.set_index(['lat', 'lon'])
        return df_mask
