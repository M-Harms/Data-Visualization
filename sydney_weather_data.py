import pandas as pd
import numpy as np


def load_data():
    """Load and process data from weather stations in Sydney, Australia.
    Data obtained from:
    https://www.kaggle.com/datasets/jsphyg/weather-dataset-rattle-package?resource=download&select=weatherAUS.csv
    """
    # Read in CSV
    df_all = pd.read_csv('rain_aus/weatherAUS.csv')
    # Take only the rows from Sydney
    df = df_all[df_all['Location'] == 'Sydney'].copy()

    # Convert date column to a datetime object
    df['Date'] = pd.to_datetime(df['Date'])

    # Add a month and season column
    df['month'] = df.Date.dt.month

    conditions = [
        (df['month'] == 12),
        ((1 <= df['month']) & (df['month'] < 3)),
        ((3 <= df['month']) & (df['month'] < 6)),
        ((6 <= df['month']) & (df['month'] < 9)),
        ((9 <= df['month']) & (df['month'] < 12))
    ]
    outputs = ['Summer', 'Summer', 'Fall', 'Winter', 'Spring']

    df['season'] = pd.Categorical(pd.Series(np.select(conditions, outputs, None)).values
                                  , ['Spring', 'Summer', 'Fall', 'Winter'])
    # Convert the boolean, yes/no columns into 1s and 0s
    df.loc[df['RainToday'] == 'Yes', 'RainToday'] = 1
    df.loc[df['RainToday'] == 'No', 'RainToday'] = 0
    df.loc[df['RainTomorrow'] == 'Yes', 'RainTomorrow'] = 1
    df.loc[df['RainTomorrow'] == 'No', 'RainTomorrow'] = 0

    df['RainToday'] = (df['RainToday'] == 'Yes').astype(int)
    df['RainTomorrow'] = (df['RainTomorrow'] == 'Yes').astype(int)

    # Make the columns numeric

    # Drop rows with NA Values
    # Drop RainTomorrow, since it is supposed to be truth
    #df.dropna(subset='WindDir9am', inplace=True)
    #df.dropna(subset='WindDir3pm', inplace=True)
    df.dropna(subset='WindSpeed9am', inplace=True)
    df.dropna(subset='WindSpeed3pm', inplace=True)
    df.dropna(subset='Cloud9am', inplace=True)
    df.dropna(subset='Cloud3pm', inplace=True)

    # The minimum for gusts is 17. The NWS in the US only records gusts above 16 knots.
        # Because of that, I am assuming null values, had no wind gusts above that threshold, so I am replacing them with 0.
    df['WindGustSpeed'].fillna(0, inplace=True)

    # Select columns to take the median of for NA values. I took the median of the values, grouped by month, since the
    # median and means would change drastically through the year
    columns_to_median = ['MinTemp', 'MaxTemp', 'Rainfall', 'Evaporation', 'Sunshine', 'Humidity9am', 'Humidity3pm',
                         'Pressure9am', 'Pressure3pm', 'Temp9am', 'Temp3pm', 'RainToday']
    for col in columns_to_median:
        df[col].fillna(df.groupby(['month'])[col].transform('median'), inplace=True)

    return df
