import glob

import numpy as np
import pandas as pd


def load_data():
    """Load and Clean Data from the Chicago Libraries Dataset"""
    final_column_names = ['branch', 'january', 'february', 'march',
                          'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
                          'december', 'year']

    path = r'./chicago/library_data'  # use your path
    all_files = glob.glob(path + '/*.csv')
    dfs = list()

    # Import all the library data
    for file in all_files:
        year = file[-8:-4]
        df_tmp = pd.read_csv(file)
        df_tmp = df_tmp.rename(columns={df_tmp.columns[0]: 'branch'})
        drop_columns = ['ADDRESS', 'CITY', 'ZIP', 'ZIP CODE', 'Location', 'LOCATION', 'YTD']
        for name in drop_columns:
            if name in df_tmp.columns:
                df_tmp = df_tmp.drop(name, axis=1)
        df_tmp['year'] = int(year)
        df_tmp.columns.values[0:] = final_column_names
        dfs.append(df_tmp)

    # Take the datasets and concat them together
    df = pd.concat(dfs)

    # Convert All  Libraries to the same nomenclature
    df2 = df.replace(['Daley, Richard J.-Bridgeport', 'Daley, Richard J.', 'Daley, Richard J.- Bridgeport',
                      'Daley, Richard J.- Bridgeport'], value='Richard J. Daley')
    df2 = df2.replace(
        ['Daley, Richard M.-W Humboldt', 'Daley, Richard M.', 'Richard M.-W Humboldt', 'Daley, Richard M.- W Humboldt'],
        value='Richard M. Daley')
    df2 = df2.replace('HAROLD WASHINGTON LIBRARY CENTER', 'Harold Washington Library Center')
    df2 = df2.replace(
        ['eBooks/Downloadable Media', 'Downloadable Media', 'Talking Books', 'Talking Book and Braille downloadable'],
        'Downloadable Media')
    df2 = df2.replace(['Online Renewals', 'Itivia Renewal', 'Itivia Renewals', 'Auto-Renewals',
                       'Patron Initiated renewals (automated phone)', 'Patron Initiated renewals (online)'],
                      'Renewals', )
    df2 = df2.replace(['Legler', 'Legler Regional'], 'Legler')
    df2 = df2.replace(['Woodson Regional', 'Woodson Regional Library'], 'Woodson')
    df2 = df2.replace(['Sulzer Regional', 'Sulzer Regional Library'], 'Sulzer')
    df2.reindex()

    # Extract the address data from a single dataset, and merge it to all the datasets, since there was no address data
    # in several of the datasets.
    import_names = ['branch', 'address', 'city', 'zip', 'january', 'february', 'march', 'april', 'may', 'june', 'july',
                    'august', 'september', 'october', 'november', 'december', 'ytd', 'location']
    df_locations = pd.read_csv('./chicago/library_data/library_2023.csv', names=import_names, header=0)
    df_locations = df_locations.drop(
        ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
         'december', 'ytd'], axis=1)
    # Convert All Daley Libraries to the same nomenclature
    df_locations = df_locations.replace(
        ['Daley, Richard J.-Bridgeport', 'Daley, Richard J.', 'Daley, Richard J.- Bridgeport',
         'Daley, Richard J.- Bridgeport'], value='Richard J. Daley')
    df_locations = df_locations.replace(
        ['Daley, Richard M.-W Humboldt', 'Daley, Richard M.', 'Richard M.-W Humboldt', 'Daley, Richard M.- W Humboldt'],
        value='Richard M. Daley')
    df_locations = df_locations.replace('HAROLD WASHINGTON LIBRARY CENTER', 'Harold Washington Library Center')
    df_locations = df_locations.replace(
        ['eBooks/Downloadable Media', 'Downloadable Media', 'Talking Books', 'Talking Book and Braille downloadable'],
        'Downloadable Media')
    df_locations = df_locations.replace(['Online Renewals', 'Itivia Renewal', 'Itivia Renewals', 'Auto-Renewals',
                                         'Patron Initiated renewals (automated phone)',
                                         'Patron Initiated renewals (online)'], 'Renewals', )
    # df_locations = df_locations.replace(['Talking Books','Talking Book and Braille downloadable'], 'Talking Books')
    df_locations = df_locations.replace(['Legler', 'Legler Regional'], 'Legler')
    df_locations = df_locations.replace(['Woodson Regional', 'Woodson Regional Library'], 'Woodson')
    df_locations = df_locations.replace(['Sulzer Regional', 'Sulzer Regional Library'], 'Sulzer')

    conditions = [
        (df_locations['address'].str.contains(" W.", case=True, flags=0, na=None, regex=True) == True),
        (df_locations['address'].str.contains(" E.", case=True, flags=0, na=None, regex=True) == True),
        (df_locations['address'].str.contains(" N.", case=True, flags=0, na=None, regex=True) == True),
        (df_locations['address'].str.contains(" S.", case=True, flags=0, na=None, regex=True) == True),
    ]
    outputs = ['West', 'East', 'North', 'South']

    df_locations['region'] = pd.Series(np.select(conditions, outputs, 'City Wide'))

    extra_locations = pd.DataFrame([['Roosevelt', '1101 W. Taylor Street', 'CHICAGO', 60607.0, 'NA', 'West']],
                                   columns=df_locations.columns)

    df_locations = pd.concat([df_locations, extra_locations])
    df_locations = df_locations.drop_duplicates()

    # Merge the locations and original dataset
    df3 = pd.merge(df2, df_locations, how='left', on=['branch'])
    df3 = df3.drop(['address', 'city', 'zip', 'location'], axis=1)

    # Change the columns to a more usful format, and create a 'date' column
    month_d = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7,
               'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}
    df_final = df3.melt(['branch', 'year', 'region'], var_name='month', value_name='transactions')
    df_final['month'] = df_final['month'].map(month_d)
    df_final['day'] = 1
    df_final['date'] = pd.to_datetime(df_final[['year', 'month', 'day']], )  # + MonthEnd(0)
    df_final.drop(['day'], axis=1, inplace=True)

    # pd.to_datetime(tmp)

    # Drop the renewals, so we just have initial checkouts
    df_final2 = df_final[df_final['branch'] != 'Renewals'].copy()

    return df_final2
