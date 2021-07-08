import time
import pandas as pd
import numpy as np
import datetime

pd.options.display.max_columns = None

CITY_DATA = { 'chicago': 'chicago.csv',
              'new york city': 'new_york_city.csv',
              'washington': 'washington.csv' }

def get_city():
    """
    Asks user to firstly select the city they are interested in.

    Returns: (str) city - name of the city to analyse
    """

    cities = ['chicago','new york city','new york','washington',
              'washington dc','washington d.c','washington d.c.',
              'washington, d.c.']
    ny = ['new york city','new york']

    print()
    print('_'*72)
    print()
    print('Welcome to the US Bike Share Reporting Package. We provide reporting')
    print('and analysis of bike share activity across three major US cities:')
    print('    - Chicago,\n    - New York City, and\n    - Washington')
    city_input = input('Please enter the name of the city you would like to review: ')
    city_input = city_input.strip().lower()

    while city_input not in cities:
        city_input = input('Sorry, that city is not available. Please try again: ')
        city_input = city_input.strip().lower()

    if city_input == 'chicago':
        city = 'chicago'
    elif city_input in ny:
        city = 'new york city'
    else:
        city = 'washington'

    return city

def load_data(city):
    """
    Loads data for the specified city and performs the following:
        - Column 'Unnamed: 0' is removed for consistency with online version
        - Column formats updated where necessary
        - Column 'Trip' created based on start and end stations
        - New columns created separating the components of 'Start Time'

    Args:
        (str) city - name of the city to review

    Returns:
        df - Pandas DataFrame containing unfiltered city data
    """
    start_time = time.time()
    df = pd.read_csv(CITY_DATA[city])

    # Drop first column ('Unnamed: 0')
    df = df.drop(['Unnamed: 0'], axis = 1)

    # Change datetime columns to datetime format
    df['Start Time'] = df['Start Time'].astype('datetime64')
    df['End Time'] = df['End Time'].astype('datetime64')

    # Create new columns for components of Start Time
    df.insert(1,'Month', df['Start Time'].dt.strftime('%b'))
    df.insert(2,'Day', df['Start Time'].dt.strftime('%a'))
    df.insert(3,'Hour', df['Start Time'].dt.strftime('%H'))

    # Create a Trip column based on start and end station
    df['Trip'] = df['Start Station'] + ' to ' + df['End Station']

    print("Processing time: %.2f seconds." % (time.time() - start_time))

    return df

def city_summary(df):
    """
    Produces a summary table of trip volumes by month and by day of the week
    for the selected city.

    Args:
        df - the DataFrame of of unfiltered data for the selected city

    Returns:
        df_summ - a summary table of trip volumes
    """
    # Define row and column order
    mth_order = ['Jan','Feb','Mar','Apr','May','Jun']
    day_order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

    # Create summary report for thes selected city
    df_summary = df.groupby(['Month','Day'], as_index=False)['Trip'].count()
    df_summary = df_summary.pivot(index = 'Day', columns = 'Month', values = 'Trip')
    df_summary = df_summary.reindex(index = day_order, columns = mth_order)

    return df_summary

def get_filters():
    """
    Asks user to specify a month and/or day of the week to review. Users can also
    select all months and/or days.

    Returns:
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    """
    months = ['Jan','Feb','Mar','Apr','May','Jun','All']
    days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun','All']

    # get user input for month (Jan, Feb, ... , Jun, All)
    print('_'*72)
    print('\nDATA FILTERING')
    print('\nYou can tailor your review by selecting one of the available months (per the table above) or one of the days of the week, or both.  Alternatively, you can include all months and days.')
    print('\nFilter by Month:')
    month_input = input('Would you like to review a particular month in detail or all months?\nPlease enter the name of the month or type \'all\' (to include all months): ')
    month_input = month_input[0:3].strip().title()

    while month_input not in months:
        month_input = input('Sorry, we do not have data for that month. Please try again: ')
        month_input = month_input[0:3].strip().title()

    month = month_input

    # get user input for day of week (Mon, Tue, ... Sun, All)

    print('\nFilter by Day:')
    day_input = input('Would you like to review a particular day of the week or include all days?\nPlease enter the day of the week or type \'all\' (to include all days): ')
    day_input = day_input.strip().title()

    while day_input not in days:
        day_input = input('Sorry, I don\'t recognise that day. Please enter the day in full: ')
        day_input = day_input.strip().title()

    day = day_input

    return month, day

def load_filters(df,month,day):
    """
    Applies the month and day filters to the city data already selected.

    Args:
        df - the DataFrame populated with the selected city data
        month - the month filter selected
        day - the day filter selected

    Returns:
        df - filtered DataFrame with additional data modifications
    """
    if month != 'All':
        df = df.loc[df['Month'] == month]

    if day != 'All':
        df = df.loc[df['Day'] == day]

    return df

def usage_stats(df,month,day):
    """
    Displays statistics on travel times including the most frequent times
    of travel.  Statistics displayed are tailored based on the filters selected.
    Summaries of trips by hour of travel are also available for review via a report menu.

    Args:
        df - the dataframe of selected data
        month - the month filter selected
        day - the day filter selected
    """
    start_time = time.time()

    df['Hour'] = df['Hour'].astype(int)

    conditions = [(df['Hour'] >= 1) & (df['Hour'] < 5),
                  (df['Hour'] >= 5) & (df['Hour'] < 9),
                  (df['Hour'] >= 9) & (df['Hour'] < 13),
                  (df['Hour'] >= 13) & (df['Hour'] < 17),
                  (df['Hour'] >= 17) & (df['Hour'] < 21),
                  (df['Hour'] >= 21) | (df['Hour'] == 0)]
    time_order = ['1am-5am','5am-9am','9am-1pm','1pm-5pm','5pm-9pm','9pm-1am']

    df['Hr Group'] = np.select(conditions, time_order)

    # Define row and column orders
    mth_order = ['Jan','Feb','Mar','Apr','May','Jun']
    day_order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

    # calculate the most common month
    top_mth = df['Month'].value_counts().idxmax()
    top_mth_val = df['Month'].value_counts().max()
    top_mth_txt = 'Most popular month was {} with {} trips'.format(top_mth,top_mth_val)

    # calculate the most common day of week
    top_day = df['Day'].value_counts().idxmax()
    top_day_val = df['Day'].value_counts().max()
    top_day_txt = 'Most popular day was {} with {} trips'.format(top_day,top_day_val)

    # calculate the most common start hour
    top_hr = df['Hour'].value_counts().idxmax()
    top_hr_val = df['Hour'].value_counts().max()
    top_hr_txt = 'Most popular hour was {}:00 with {} trips'.format(top_hr,top_hr_val)

    # create summary tables using a groupby() method
    mth_summary = df.groupby(['Month','Hr Group'], as_index=False)['Trip'].count()
    mth_summary = mth_summary.pivot(index = 'Month', columns = 'Hr Group', values = 'Trip')
    mth_summary = mth_summary.reindex(index = mth_order, columns = time_order)
    mth_summary = mth_summary.fillna(0).astype(int)

    day_summary = df.groupby(['Day','Hr Group'], as_index=False)['Trip'].count()
    day_summary = day_summary.pivot(index = 'Day', columns = 'Hr Group', values = 'Trip')
    day_summary = day_summary.reindex(index = day_order, columns = time_order)
    day_summary = day_summary.fillna(0).astype(int)

    hr_summary = df.groupby(['Hr Group'], as_index=False)['Trip'].count()
    hr_summary = hr_summary.set_index('Hr Group').transpose()
    hr_summary = hr_summary.reindex(columns = time_order)
    hr_summary = hr_summary.fillna(0).astype(int)

    # Create detailed reports accessed via the Usage Reports Menu
    hr_mth_detail = df.groupby(['Hour','Month'], as_index=False)['Trip'].count()
    hr_mth_detail = hr_mth_detail.pivot(index = 'Hour', columns = 'Month', values = 'Trip')
    hr_mth_detail = hr_mth_detail.reindex(columns = mth_order)
    hr_mth_detail = hr_mth_detail.fillna(0).astype(int)

    hr_day_detail = df.groupby(['Hour','Day'], as_index=False)['Trip'].count()
    hr_day_detail = hr_day_detail.pivot(index = 'Hour', columns = 'Day', values = 'Trip')
    hr_day_detail = hr_day_detail.reindex(columns = day_order)
    hr_day_detail = hr_day_detail.fillna(0).astype(int)

    index_ord = [mth_order,day_order]
    row_ord = pd.MultiIndex.from_product(index_ord,names=['Month','Day'])
    mth_day_summ = df.groupby(['Month','Day','Hr Group'], as_index = False)['Trip'].count()
    mth_day_summ = mth_day_summ.pivot(index = ['Month','Day'], columns = 'Hr Group', values = 'Trip')
    mth_day_summ = mth_day_summ.reindex(index = row_ord, columns = time_order)
    mth_day_summ = mth_day_summ.fillna(0).astype(int)

    # display the calculated values
    print('_'*74)
    print('\nBIKE SHARE USAGE TIMES ANALYSIS\n')
    if month != 'All' and day != 'All':
        print(top_hr_txt)
        print('\nTrip volumes by hour band for {}s in {}\n'.format(day,month))
        print(hr_summary)
    elif month != 'All' and day == 'All':
        print(top_day_txt)
        print(top_hr_txt)
        print('\nTrip volumes by hour band by day in {}\n'.format(month))
        print(day_summary)
    elif month == 'All' and day != 'All':
        print(top_mth_txt)
        print(top_hr_txt)
        print('\nTrip volumes by hour band by month on {}s\n'.format(day))
        print(mth_summary)
    else:
        print(top_mth_txt)
        print(top_day_txt)
        print(top_hr_txt)
        print('\nTrip volumes by hour band by month\n')
        print(mth_summary)
        print('\nTrip volumes by hour band by day\n')
        print(day_summary)

    input('Press Enter to continue to the Bike Share Usage Reports menu...')

    # Bike Share Usage Reporting Menu

    while True:
        print('_'*72)
        print('\nBIKE SHARE USAGE REPORTS\n')
        print('The following reports are available:\n')
        print('    1. Bike Share Trips by Hour by Month')
        print('    2. Bike Share Trips by Hour by Day')
        print('    3. Bike Share Trips by hour band by month by day ')
        select = input('Please enter the number of the report you would like to view, or enter \'Q\' to quit: ')
        select = select.lower()

        while select not in ('1','2','3','q'):
                select = input('That is not a valid option. Please try again: ')
                select = select.lower()

        if select == '1':
            print('\nTrip volumes by hour by month')
            print(hr_mth_detail)
            input('Press Enter to return to the Bike Share Usage Reports menu...')
        elif select == '2':
            print('\nTrip volumes by hour by day')
            print(hr_day_detail)
            input('Press Enter to return to the Bike Share Usage Reports menu...')
        elif select == '3':
            print('\nTrip volumes by hour band by month and day')
            print(mth_day_summ)
            input('Press Enter to return to the Bike Share Usage Reports menu...')
        else:
            break

    # Remove any columns created specifically for usage stats
    df = df.drop(['Hr Group'], axis = 1, inplace = True)

    time_spent = time.time() - start_time
    time_spent = datetime.timedelta(seconds = int(time_spent))
    print("\nThe Usage Reporting review took {}.".format(time_spent))

def station_stats(df):
    """
    Creates a new dataframe (df_stations) listing each station used in the
    selected city during the period selected, and summarising the number of trips
    that start and end at each station.

    Adds new columns to df_stations which include the difference between trip
    starts and ends for each station as both the number of trips and % of starts.

    Summarises bike share activity by trip (start staion to end station)

    Provides statistics and reports on trip volumes by station and by trip
    for the selected city and period.

    Args:
        df - the DataFrame of of unfiltered data for the selected city
    """
    start_time = time.time()

    # Create two summary tables based on start and end stations
    df_start = df.groupby(['Start Station'], as_index=False)['Trip'].count()
    df_start = df_start.rename(columns = {'Start Station':'Station','Trip':'Starts'})

    df_end = df.groupby(['End Station'], as_index=False)['Trip'].count()
    df_end = df_end.rename(columns = {'End Station':'Station','Trip':'Ends'})

    # Merge the two summary tables to create table of total starts and ends by station
    df_stations = df_start.merge(df_end, on='Station', how='outer')

    # Resolve any missing data (stations with no trip starts or ends)
    df_stations['Starts'] = df_stations['Starts'].fillna(0.0)
    df_stations['Starts'] = df_stations['Starts'].astype(int)
    df_stations['Ends'] = df_stations['Ends'].fillna(0.0)
    df_stations['Ends'] = df_stations['Ends'].astype(int)

    # Add comparative columns (variance and %)
    df_stations['Var'] = df_stations['Starts'] - df_stations['Ends']
    df_stations['%'] = df_stations['Var'] / df_stations['Starts'].replace({0:np.nan})
    df_stations['%'] = df_stations['%'].fillna(-1.0).round(3)*100

    # Calculate key stats like mean, mode and median for the Starts, Ends and Var
    tot_trips = df_stations['Starts'].sum()
    num_stations = df_stations['Station'].count()
    max_starts = df_stations['Starts'].max()
    max_starts_loc = df_stations.iloc[df_stations['Starts'].idxmax()][0]

    max_ends = df_stations['Ends'].max()
    max_ends_loc = df_stations.iloc[df_stations['Ends'].idxmax()][0]
    top_trip = df['Trip'].value_counts().max()
    top_trip_loc = df['Trip'].value_counts().idxmax()

    avg_starts = round(df_stations['Starts'].mean())

    med_starts = df_stations['Starts'].median()
    med_ends = df_stations['Ends'].median()

    max_var = df_stations['Var'].max()
    max_var_loc = df_stations.iloc[df_stations['Var'].idxmax()][0]

    # Create report content

    # Detailed list of all stations sorted alphabetically
    station_det = df_stations.sort_values(by = 'Station')
    station_det = station_det.set_index('Station')

    # Stations with trip starts but no ends and vice versa
    null_list = df_stations[(df_stations['Starts'] == 0) | (df_stations['Ends'] == 0)]
    null_list = null_list.set_index('Station')

    # Stations where the diff between trip starts and ends > 50%
    high_per = df_stations[(df_stations['%'].abs() > 50) & (df_stations['%'].abs() < 100)]
    high_per = high_per.set_index('Station')

    # The 20 most and least utilised stations
    df_stations['total'] = df_stations['Starts'] + df_stations['Ends']
    stat_sort = df_stations.sort_values(by = 'total', ascending = False)
    stat_sort = stat_sort.set_index('Station')
    top_stat = stat_sort[0:20].drop(['total'],axis=1)
    bottom_stat = stat_sort[-20:-1].drop(['total'], axis=1)

    # The 20 most and least common trips
    df_trip = df.groupby(['Trip'], as_index = False)['Trip Duration'].count()
    df_trip = df_trip.sort_values(by = 'Trip Duration', ascending = False).rename(columns = {'Trip Duration':'Trip Count'})
    df_trip = df_trip.set_index('Trip')
    top_20_trip = df_trip[0:20]
    bottom_20_trip = df_trip[-20:-1]

    # 20 stations with largest variation between trip starts and ends
    df_stations['absvar'] = df_stations['Var'].abs()
    top_var = df_stations.sort_values(by = 'absvar', ascending = False)[0:20].drop(['absvar','total'],axis=1)
    top_var = top_var.set_index('Station')

    # Print summary statistics
    print('_'*72)
    print('\nSUMMARY STATION STATISTICS\n')
    print('There was a total of {} trips across {} stations.'.format(tot_trips,num_stations))
    print('\nThe most popular station for trip starts was {} with {} trips.'.format(max_starts_loc, max_starts))
    print('The most popular station for trip ends was {} with {} trips.'.format(max_ends_loc, max_ends))
    print('The most popular trip was {} with {} trips.'.format(top_trip_loc, top_trip))
    print('\nThe average trip starts per station was {}.'.format(avg_starts))
    print('\nThe median trip starts per station was {}.'.format(med_starts))
    print('The median trip ends per station was {}.'.format(med_ends))
    print('\nThe largest difference between trip starts and ends was {} \nat {} station.\n'.format(max_var, max_var_loc))
    input('Press Enter to continue to the Station Utilisation Reports menu...')

    # Station Utilisation Report Menu
    while True:
        print('_'*72)
        print('\nSTATION AND TRIP ACTIVITY REPORTS\n')
        print('This section includes reports on Stations and Trips for the city and period selected.')
        print('\nStation Reports:')
        print('    1. Stations with trip starts but no ends (or vice versa)')
        print('    2. The 20 most utilised stations')
        print('    3. The 20 least utilised stations')
        print('    4. The 20 stations with the largest variation between starts and ends')
        print('    5. The stations where the difference between starts and ends is > 50%')
        print('    6. Detailed Station Report - listing all stations utilised in the period')
        print('\nTrip Reports:')
        print('    7. The 20 most common trips')
        print('    8. The 20 least common trips')
        select = input('Please enter the number of the report you would like to view, or enter \'Q\' to quit: ')
        select = select.lower()

        while select not in ('1','2','3','4','5','6','7','8','q'):
                select = input('That is not a valid option. Please try again: ')
                select = select.lower()

        if select == '1':
            print('_'*72)
            print('\nStations with trip starts but no ends (and vice versa)')
            print(null_list)
            input('Press Enter to return to the Station and Trip Activity Reports menu...')

        elif select == '2':
            print('_'*72)
            print('\nThe 20 most utilised stations')
            print(top_stat)
            input('Press Enter to return to the Station and Trip Activity Reports menu...')

        elif select == '3':
            print('_'*72)
            print('\nThe 20 least utilised stations')
            print(bottom_stat)
            input('Press Enter to return to the Station and Trip Activity Reports menu...')

        elif select == '4':
            print('_'*72)
            print('\nThe 20 stations with the largest variation between starts and ends')
            print(top_var)
            input('Press Enter to return to the Station and Trip Activity Reports menu...')

        elif select == '5':
            print('_'*72)
            print('\nThe stations where the difference between starts and ends is greater than 50%')
            print(high_per)
            input('Press Enter to return to the Station and Trip Activity Reports menu...')

        elif select == '6':
            print('_'*72)
            print('\nDETAILED STATION REPORT\n')
            print('The detailed station report lists all stations with activity during the period and includes trip volumes. Please note, this report contains {} rows.'.format(len(df_stations)))
            view_det = input('Would you like to continue? (Y/N): ')
            view_det = view_det.lower()

            while view_det not in ['y','n']:
                view_det = input('That is not a valid option.  Please type \'Y\' or \'N\' and press Enter: ')
                view_det = view_det.lower()

            if view_det == 'y':
                a = 0
                b = 24
                while True:
                    print('\nSTATION REPORT - Lists all stations with trips recorded during the period\n')
                    print(station_det[a:b])
                    if b >= (len(station_det) - 1):
                        input('Report End: Press Enter to to return to the Station and Trip Activity Reports menu...')
                        break
                    input('Press Enter to continue...')
                    a += 24
                    b += 24

        elif select == '7':
            print('_'*72)
            print('\nThe 20 most common trips during the period selected')
            print(top_20_trip)
            input('Press Enter to return to the Station and Trip Activity Reports menu...')

        elif select == '8':
            print('_'*72)
            print('\nThe 20 least common trips during the period selected')
            print(bottom_20_trip)
            input('Press Enter to return to the Station and Trip Activity Reports menu...')

        else:
            break

    time_spent = time.time() - start_time
    time_spent = datetime.timedelta(seconds = int(time_spent))
    print("\nThe Station Reporting review took {}.".format(time_spent))

def trip_dur_report(month, day, tot_report, mth_report, day_report, mth_day_report):
    """
    Prints the relevant trip duration summary reports, subject to the selected reporting criteria.

    Args:
        month - the month filter selected
        day - the day filter selected
        tot_report - summary of all trips by trip duration category
        mth_report - summary of trips by month by trip duration category
        day_report - summary of trips by day by trip duration category
        mth_day_report - summary of trips by month by day and by trip duration category
    """

    print('_'*72)
    print('\nTRIP DURATION REPORTS\n')

    if (month == 'All') & (day == 'All'):
        print('Summary of all trips by Trip duration category')
        print(tot_report)
        print('\nSummary of trips by Month by Trip duration category')
        print(mth_report)
        print('\nSummary of trips by Day by Trip duration category')
        print(day_report)
        extra = input('\nWould you like to see a summary of trips by Trip duration category by both Month and Day? (Y/N): ')
        extra = extra.lower()

        while extra not in ['y','n']:
            extra = input('That is not a valid option.  Please enter either \'Y\' or \'N\':')
            extra = extra.lower()

        if extra == 'y':
            print('\nSummary of trips by Month by Day by Trip duration category')
            print(mth_day_report)
            input('Press Enter to return to the Trip Duration Reporting Menu...')

    elif (month == 'All') & (day != 'All'):
        print('Summary of all trips on {}s by Trip duration category'.format(day))
        print(tot_report)
        print('\nSummary of trips on {}s by Month by Trip duration category'.format(day))
        print(mth_report)
        input('Press Enter to return to the Trip Duration Reporting Menu...')

    elif (month != 'All') & (day == 'All'):
        print('Summary of all trips in {} by Trip duration category'.format(month))
        print(tot_report)
        print('\nSummary of trips in {} by Day by Trip duration category'.format(month))
        print(day_report)
        input('Press Enter to return to the Trip Duration Reporting Menu...')

    else:
        print('Summary of all trips by trip duration category for {}s in {}'.format(day, month))
        print(tot_report)
        input('Press Enter to return to the Trip Duration Reports menu...')

def except_report(duration_except, ex_count):
    """
    Prints an exception summary report if any trip duration exceptions were identified.
    An exception is where the difference between start time and end time is different
    to the Trip Duration data provided.
    If there are no exceptions in the selected data, a message to that effect is displayed.

    Args:
        duration_except - the trip duration exception report
        ex_count - the number of exceptions counted
    """
    print('_'*72)
    print('\nTRIP DURATION EXCEPTIONS')

    if ex_count > 0:
        print('\nTrip duration reporting is based on the Trip Duration data provided. However, we have identified a number of discrepancies between Trip start and end times and the Trip Duration data.')
        print('\nThe following exception report has been produced by comparing the difference between the Trip Start and End Times, and the Trip Duration data.')
        print('\nVariances in the summary table below are based on the absolute value of the variance and have been categorised into bands to simplify analysis.')
        print('\nSummary of Trip Duration Exceptions')
        print(duration_except)
        print('\nSome exceptions may warrant investigation.')
    else:
        print('\nThere are no trip duration exceptions to report')

    input('Press Enter to return to the Trip Duration Reports menu...')

def trip_duration_stats(df, month, day):
    """
    Produces trip duration reports and statistics for the selected city.

    Args:
        df - the DataFrame of of unfiltered data for the selected city
        month - the month filter selected
        day - the day filter selectd
    """
    start_time = time.time()

    # Create new column for trip duration bands
    conditions = [(df['Trip Duration'] <= 300),
                  (df['Trip Duration'] > 300) & (df['Trip Duration'] <= 600),
                  (df['Trip Duration'] > 600) & (df['Trip Duration'] <= 900),
                  (df['Trip Duration'] > 900) & (df['Trip Duration'] <= 1200),
                  (df['Trip Duration'] > 1200) & (df['Trip Duration'] <= 3600),
                  (df['Trip Duration'] > 3600) & (df['Trip Duration'] <= 10800),
                  (df['Trip Duration'] > 10800) & (df['Trip Duration'] <= 21600),
                  (df['Trip Duration'] > 21600)]
    values = ['5 min','10 min','15 min','20 min','1 hr','3 hr','6 hr','>6 hr']

    df['Trip Times'] = np.select(conditions, values)

    # Calculate the difference in seconds between Start Time and End Time and compare to Trip Duration
    df.insert(7,'Date Diff', df['End Time'] - df['Start Time'])
    df.insert(8,'Seconds', df['Date Diff'].dt.total_seconds().astype(int))
    df.insert(9,'Var', abs((df['Trip Duration'] - df['Seconds'])).astype(int))

    # Define variance category
    definition = [(df['Var'] <= 1),
                  (df['Var'] > 1) & (df['Var'] <= 5),
                  (df['Var'] > 5) & (df['Var'] <= 60),
                  (df['Var'] > 60) & (df['Var'] <= 600),
                  (df['Var'] > 600) & (df['Var'] <= 3600),
                  (df['Var'] > 3600) & (df['Var'] <= 21600),
                  (df['Var'] > 21600) & (df['Var'] <= 86400),
                  (df['Var'] > 86400)]
    categories = ['1 sec','5 sec','1 min','10 min','1 hr','6 hr','24 hr','>24 hr']
    df['Var Cat'] = np.select(definition, categories)

    # Define column and row values and order
    mth_order = ['Jan','Feb','Mar','Apr','May','Jun']
    day_order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    mth_day_ord = [mth_order,day_order]
    rows = pd.MultiIndex.from_product(mth_day_ord,names=['Month','Day'])

    # Are there execptions
    ex_count = df[df['Var'] != 0]['Trip'].count()

    # Summary of trip duartion exceptions by Variance Category and Month
    duration_except = df[df['Var'] != 0].groupby(['Month','Var Cat'], as_index = False)['Trip'].count()
    duration_except = duration_except.pivot(index = 'Month', columns = 'Var Cat', values = 'Trip')
    duration_except = duration_except.reindex(index = mth_order, columns = categories)
    duration_except = duration_except.fillna(0).astype(int)

    # Calculate key trip duration stats
    tot_time = df['Trip Duration'].sum()
    tot_time = datetime.timedelta(seconds = int(tot_time))
    avg_time = df['Trip Duration'].mean()
    avg_time = datetime.timedelta(seconds = int(avg_time))
    med_time = df['Trip Duration'].median()
    med_time = datetime.timedelta(seconds = int(med_time))
    longest = df['Trip Duration'].max()
    longest = datetime.timedelta(seconds = int(longest))
    shortest = df['Trip Duration'].min()
    shortest = datetime.timedelta(seconds = int(shortest))

    # Create trip duration reports

    # Total view
    tot_report = df.groupby(['Trip Times'], as_index = False)['Trip'].count()
    tot_report = tot_report.set_index('Trip Times').transpose().reindex(columns = values)
    tot_report = tot_report.fillna(0).astype(int)

    # Month view
    mth_report = df.groupby(['Month','Trip Times'], as_index = False)['Trip'].count()
    mth_report = mth_report.pivot(index = ['Month'], columns = ['Trip Times'], values = 'Trip')
    mth_report = mth_report.reindex(index = mth_order, columns = values)
    mth_report = mth_report.fillna(0).astype(int)

    # Day view
    day_report = df.groupby(['Day','Trip Times'], as_index = False)['Trip'].count()
    day_report = day_report.pivot(index = ['Day'], columns = ['Trip Times'], values = 'Trip')
    day_report = day_report.reindex(index = day_order, columns = values)
    day_report = day_report.fillna(0).astype(int)

    # Combined month and day view
    mth_day_report = df.groupby(['Month','Day','Trip Times'], as_index=False)['Trip'].count()
    mth_day_report = mth_day_report.pivot(index = ['Month','Day'], columns = 'Trip Times', values = 'Trip')
    mth_day_report = mth_day_report.reindex(index = rows, columns = values).fillna(0)
    mth_day_report = mth_day_report.astype(int)

    # Print trip duration stats
    print('_'*72)
    print('\nTRIP DURATION SUMMARY STATISTICS\n')
    print('Total combined time of all trips during the period (days and h:m:s): {}'.format(tot_time))
    print('\nThe longest trip was (h:m:s:): {}'.format(longest))
    print('The shortest trip was (h:m:s:): {}'.format(shortest))
    print('\nAverage trip duration (h:m:s): {}'.format(avg_time))
    print('Median trip duration (h:m:s): {}'.format(med_time))
    input('Press Enter to continue to the Trip Duration Reports menu...')

    # Trip Duration Reporting Menu

    while True:
        print('_'*72)
        print('\nTRIP DURATION REPORTS\n')
        print('The following reports are available:\n')
        print('    1. Bike Share Trips by Trip Duration')
        print('    2. Trip Duration Exceptions')
        select = input('Please enter the number of the report you would like to view, or enter \'Q\' to quit: ')
        select = select.lower()

        while select not in ('1','2','q'):
                select = input('That is not a valid option. Please try again: ')
                select = select.lower()

        if select == '1':
            trip_dur_report(month, day, tot_report, mth_report, day_report, mth_day_report)

        elif select == '2':
            except_report(duration_except, ex_count)

        else:
            break

    # Remove any columns created specifically for trip duration stats
    df = df.drop(['Trip Times','Date Diff','Seconds','Var','Var Cat'], axis = 1, inplace = True)

    time_spent = time.time() - start_time
    time_spent = datetime.timedelta(seconds = int(time_spent))
    print("\nThe Trip Duration Reporting review took {}.".format(time_spent))

def run_report(df, group, idx, col, idx_ord, col_ord):
    """
    Generates and displays the report based on the parameters provided

    Args:
        df - dataframe
        group - columns used in the groupby() function
        idx - dataframe column(s) specified as the index in the pivot
        col - dataframe column specified as the index in the pivot
        idx_ord - index order required for re-indexing the pivot
        col_ord - column order required for re-indexing the pivot
    """
    # Generate report
    report_detail = df.groupby(group, as_index = False)['Trip'].count()
    report_detail = report_detail.pivot(index = idx, columns = col, values = 'Trip')
    report_detail = report_detail.reindex(index = idx_ord, columns = col_ord)
    report_detail = report_detail.fillna(0).astype(int)

    print()
    print('_'*72)
    print('\nBIKE SHARE USER REPORTS\n')
    print('User Activity Report')
    print(report_detail)
    input('Press Enter to return to the Bike Share User Reports menu...')


def user_report_menu(df, city, month, day):
    """
    Allows the user to select from a range of reporting options subject to their data
    selection criteria.

    Args:
        df - DataFrame
        city - selected city
        month - selected month
        day - selected day

    Calls:
        run_report() - to generate the relevant report
    """
    # Define different group by options
    a = ['User Type','Month']
    b = ['User Type','Day']
    c = ['User Type','Month','Day']

    d = ['User Type','Age Group']
    e = ['User Type','Gender','Age Group']
    f = ['User Type','Month','Age Group']
    g = ['User Type','Day','Age Group']
    h = ['Gender','Age Group']
    i = ['Gender','User Type','Age Group']
    j = ['Gender','Month','Age Group']
    k = ['Gender','Day','Age Group']

    # Define standard index and column orders
    mth_order = ['Jan','Feb','Mar','Apr','May','Jun']
    day_order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    gender = ['Female','Male','Unknown']
    age_groups = ['N/A','<18','18-29','30\'s','40\'s','50\'s','60\'s','70+']

    index_a = ['User Type']
    index_b = ['User Type']
    index_c = ['User Type','Month']
    index_d = ['User Type']
    index_e = ['User Type','Gender']
    index_f = ['User Type','Month']
    index_g = ['User Type','Day']
    index_h = ['Gender']
    index_i = ['Gender','User Type']
    index_j = ['Gender','Month']
    index_k = ['Gender','Day']

    # Define columns used in the pivot tables
    col_w1 = ['Month']
    col_w23 = ['Day']
    col_other = ['Age Group']

    # Define User Types by city
    if city == 'chicago':
        ut_order = ['Customer','Dependent','Subscriber']
    elif city == 'new york city':
        ut_order = ['Customer','Subscriber','Unknown']
    else:
        ut_order = ['Customer','Subscriber']

    # Define indices for MultiIndex DataFrames
    idx_a = ut_order
    idx_b = ut_order
    idx_c = [ut_order,mth_order]
    idx_d = ut_order
    idx_e = [ut_order,gender]
    idx_f = [ut_order,mth_order]
    idx_g = [ut_order,day_order]
    idx_h = gender
    idx_i = [gender,ut_order]
    idx_j = [gender,mth_order]
    idx_k = [gender,day_order]

    # Define row indices
    rows_c = pd.MultiIndex.from_product(idx_c, names = index_c)
    rows_e = pd.MultiIndex.from_product(idx_e, names = index_e)
    rows_f = pd.MultiIndex.from_product(idx_f, names = index_f)
    rows_g = pd.MultiIndex.from_product(idx_g, names = index_g)
    rows_i = pd.MultiIndex.from_product(idx_i, names = index_i)
    rows_j = pd.MultiIndex.from_product(idx_j, names = index_j)
    rows_k = pd.MultiIndex.from_product(idx_k, names = index_k)

    if city == 'washington':
        while True:
            print('_'*72)
            print('\nBIKE SHARE USER REPORTS\n')
            print('The following User Type activity reports are available:')
            print('   1. User Type by Month')
            print('   2. User Type by Day')
            print('   3. User Type by Month and Day')
            select = input('Please enter the number of the report you would like to view, or enter \'Q\' to quit: ')
            select = select.lower()

            while select not in ('1','2','3','q'):
                select = input('That is not a valid option. Please try again: ')
                select = select.lower()

            if select == '1':
                group = a
                idx = index_a
                col = col_w1
                idx_ord = idx_a
                col_ord = mth_order
                run_report(df, group, idx, col, idx_ord, col_ord)
            elif select == '2':
                group = b
                idx = index_b
                col = col_w23
                idx_ord = idx_b
                col_ord = day_order
                run_report(df, group, idx, col, idx_ord, col_ord)
            elif select == '3':
                group = c
                idx = index_c
                col = col_w23
                idx_ord = rows_c
                col_ord = day_order
                run_report(df, group, idx, col, idx_ord, col_ord)
            else:
                break

    else:
        while True:
            print('_'*72)
            print('\nBIKE SHARE USER REPORTS\n')
            print('There are a range of reporting options available. You have a choice of the following reports:')
            print('\nReports by User Type:')
            print('    1. User Type by Age Group')
            print('    2. User Type by Gender by Age Group')
            print('    3. User Type by Month by Age Group')
            print('    4. User Type by Day by Age Group')
            print('\nReports by Gender:')
            print('    5. Gender by Age Group')
            print('    6. Gender by User Type by Age Group')
            print('    7. Gender by Month by Age Group')
            print('    8. Gender by Day by Age Group')

            select = input('Please enter the number of the report you would like to view, or enter \'Q\' to quit: ')
            select = select.lower()

            while select not in ('1','2','3','4','5','6','7','8','q'):
                select = input('That is not a valid option. Please try again: ')
                select = select.lower()

            if select == '1':
                group = d
                idx = index_d
                col = col_other
                idx_ord = idx_d
                col_ord = age_groups
                run_report(df, group, idx, col, idx_ord, col_ord)
            elif select == '2':
                group = e
                idx = index_e
                col = col_other
                idx_ord = rows_e
                col_ord = age_groups
                run_report(df, group, idx, col, idx_ord, col_ord)
            elif select == '3':
                group = f
                idx = index_f
                col = col_other
                idx_ord = rows_f
                col_ord = age_groups
                run_report(df, group, idx, col, idx_ord, col_ord)
            elif select == '4':
                group = g
                idx = index_g
                col = col_other
                idx_ord = rows_g
                col_ord = age_groups
                run_report(df, group, idx, col, idx_ord, col_ord)
            elif select == '5':
                group = h
                idx = index_h
                col = col_other
                idx_ord = idx_h
                col_ord = age_groups
                run_report(df, group, idx, col, idx_ord, col_ord)
            elif select == '6':
                group = i
                idx = index_i
                col = col_other
                idx_ord = rows_i
                col_ord = age_groups
                run_report(df, group, idx, col, idx_ord, col_ord)
            elif select == '7':
                group = j
                idx = index_j
                col = col_other
                idx_ord = rows_j
                col_ord = age_groups
                run_report(df, group, idx, col, idx_ord, col_ord)
            elif select == '8':
                group = k
                idx = index_k
                col = col_other
                idx_ord = rows_k
                col_ord = age_groups
                run_report(df, group, idx, col, idx_ord, col_ord)
            else:
                break

def user_stats(df, city, month, day):
    """
    Produces trip duration reports and statistics for the selected city.

    Args:
        df - the DataFrame of of unfiltered data for the selected city
        city - selected city
        month - selected month
        day - selected day
    """
    start_time = time.time()

    # Create Year column based on Start Time
    df.insert(1,'Year', df['Start Time'].dt.year)

    # Clean Data
    if city == 'new york city':
        df[['User Type']] = df[['User Type']].fillna('Unknown')
        df[['Gender']] = df[['Gender']].fillna('Unknown')
        df[['Birth Year']] = df[['Birth Year']].fillna(0.0)
        df['Birth Year'] = df['Birth Year'].astype(int)
    elif city == 'chicago':
        df[['Gender']] = df[['Gender']].fillna('Unknown')
        df[['Birth Year']] = df[['Birth Year']].fillna(0.0)
        df['Birth Year'] = df['Birth Year'].astype(int)

    # Create an Age column that is zero if Birth Year missing
    if city != 'washington':
        df.loc[df['Birth Year'] == 0, 'Age'] = 0
        df.loc[df['Birth Year'] != 0, 'Age'] = df['Year'] - df['Birth Year']
        df['Age'] = df['Age'].astype(int)

        # Create new column for Age Group of the users
        ages = [(df['Age'] == 0),
                (df['Age'] > 0) & (df['Age'] < 18),
                (df['Age'] >= 18) & (df['Age'] < 30),
                (df['Age'] >= 30) & (df['Age'] < 40),
                (df['Age'] >= 40) & (df['Age'] < 50),
                (df['Age'] >= 50) & (df['Age'] < 60),
                (df['Age'] >= 60) & (df['Age'] < 70),
                (df['Age'] >= 70)]
        age_groups = ['N/A','<18','18-29','30\'s','40\'s','50\'s','60\'s','70+']

        df['Age Group'] = np.select(ages, age_groups)

    # Calculate user stats and reports based on city
    if city == 'washington':
        user_type_count = df.groupby(['User Type'], as_index = False)['Trip'].count()
        user_type_count = user_type_count.set_index('User Type').rename(columns = {'Trip':'Trips'})

    else:
        male = df[df['Gender'] == 'Male']['Trip'].count()
        female = df[df['Gender'] == 'Female']['Trip'].count()
        unknown = df[df['Gender'] == 'Unknown']['Trip'].count()
        user_type_summ = df.groupby(['User Type','Gender'], as_index = False)['Trip'].count()
        user_type_summ = user_type_summ.pivot(index = ['User Type'], columns = ['Gender'], values = 'Trip')
        user_type_summ = user_type_summ.fillna(0).astype(int)
        user_type_summ['Total'] = user_type_summ['Female']+user_type_summ['Male']+user_type_summ['Unknown']
        birth_yr_max = df['Birth Year'].max()
        birth_yr_min = df[df['Birth Year'] != 0]['Birth Year'].min()
        age_max = df['Age'].max()

        if age_max > 90:
            over_90 = df[df['Age'] > 90]
            over_90_count = len(over_90)
            over_90 = over_90.groupby(['Birth Year','Age'], as_index = False)['Trip'].count()
            over_90 = over_90.set_index('Birth Year').rename(columns = {'Trip':'Trips'})

    # Print summary user statistics
    print('_'*72)
    print('\nBIKE SHARE USER SUMMARY STATISTICS\n')

    if city == 'washington':
        print('Summary of trips by User Type')
        print(user_type_count)
        if (month != 'All') & (day != 'All'):
            input('There are no more user reports available for the data selected. Press Enter to continue...')
        else:
            input('Press Enter to continue to the Bike Share User Reports menu...')
            user_report_menu(df, city, month, day)
    else:
        print('Summary of trips by User Type and Gender')
        print(user_type_summ)
        print('\nThe number of male users was {}'.format(male))
        print('The number of female users was {}'.format(female))
        print('The number of users where the gender is unknown was {}'.format(unknown))
        print('\nThe earliest Birth Year was {}.'.format(birth_yr_min))
        print('The latest Birth Year was {}.'.format(birth_yr_max))

        if age_max > 90:
            print('\nThere were {} trips by users > 90 years old'.format(over_90_count))
            older = input('Would you like to see a breakdown by Age of trips by users > 90 years old? (Y/N): ')
            older = older.lower()

            while older not in ['y','n']:
                older = input('That is not a valid option.  Please enter either \'Y\' or \'N\':')
                older = older.lower()

            if older == 'y':
                print('\nSummary of trips by users > 90 years old')
                print(over_90)
                input('Press Enter to continue to the Bike Share User Reports menu...')

        user_report_menu(df, city, month, day)

    # Remove any columns created specifically for user stats
    if city != 'washington':
        df = df.drop(['Year','Age','Age Group'], axis = 1, inplace = True)
    else:
        df = df.drop(['Year'], axis = 1, inplace = True)

    time_spent = time.time() - start_time
    time_spent = datetime.timedelta(seconds = int(time_spent))
    print("\nThe User Reporting review took {}.".format(time_spent))

def data_view(df):
    """
    Allows users to view the raw data (5 rows at a time). Includes an end of file message.

    Args:
        df - the dataframe with the selected data
    """

    x = 0
    y = 5
    df = df.drop(['Month','Day','Hour','Trip'], axis = 1)
    while True:
        print('\nDETAILED DATA - Lists every trip recorded during the period\n')
        print(df[x:y])
        if y >= (len(df) - 1):
            input('Data File End: Press Enter to quit...')
            break
        cont = input('\nWould you like to continue? (Y/N): ')
        cont = cont.lower()

        while cont not in ['y','n']:
            cont = input('That is not a valid option. Please type \'Y\' or \'N\' and press Enter: ')
            cont = cont.lower()

        if cont == 'n':
            break
        x += 5
        y += 5

def report_pack(df, city, month, day):
    """
    Provides a menu system that allows users to choose the area they want to look at.
    Option 5 gives users access to the raw data (5 rows at a time).  If they do not select
    this option during their session, users will be asked if they want to view the data before they quit.
    However, if users have selected option 5 during their session, they will not be prompted again when they quit.

    Args:
        df - the dataframe with the selected data
        city - the selected city
        month - the selected month filter
        day - the selected day filter
    """
    viewed = False
    while True:
        print()
        print('_'*72)
        print('\nBIKE SHARE REPORTING\n')
        print('You can select from the following Bike Share Data reporting categories:')
        print('    1. Bike Share Usage Times')
        print('    2. Station and Trip Activity')
        print('    3. Trip Durations')
        print('    4. User Information')
        print('    5. Raw Data Review (5 rows at a time)\n')
        select = input('Please enter the category number you would like to review or hit \'Q\' to quit: ')
        select = select.lower()
        count = 0

        # Handles incorrectly keyed options
        while select not in ['1','2','3','4','5','q']:
            count += 1
            if count < 3:
                select = input('That is not a valid option.  Please try again: ')
                select = select.lower()
            elif count >= 3:
                select = input('You must enter a number between 1 and 5 or enter \'Q\' to quit: ')
                select = select.lower()

        # Calls the relevant reporting functions
        if select == '1':
            usage_stats(df, month, day)
        elif select == '2':
            station_stats(df)
        elif select == '3':
            trip_duration_stats(df, month, day)
        elif select == '4':
            user_stats(df, city, month, day)
        elif select == '5':
            viewed = True
            data_view(df)
        elif select == 'q':
            if viewed == False:
                final = input('\nBefore you finish, would you like to review the selected data in detail? (Y/N): ')
                final = final.lower()

                while final not in ['y','n']:
                    final = input('That is not a valid option. Please type \'Y\' or \'N\' and press Enter: ')
                    final = final.lower()

                if final == 'y':
                    data_view(df)
            break

def main():
    while True:
        # City selection
        city = get_city()
        print('\nRetrieving data ...\n')
        # Data loaded and summary table presented
        df = load_data(city)
        city_summ = city_summary(df)
        print('\nBelow is a summary of trip volumes by month and day for {}'.format(city.title()))
        print()
        print(city_summ)
        input('Press Enter to continue...')
        # Month and Day filters obtained and applied
        month, day = get_filters()
        df = load_filters(df,month,day)
        print('\nThankyou, the required data has been selected.')
        time.sleep(2)
        # Reporting initiated
        report_pack(df, city, month, day)
        # Review re-start option
        restart = input('\nWould you like to review another city? (Y/N): ')
        restart = restart.lower()

        while restart.lower() not in ['y','n']:
            restart = input('That is not a valid option. Please type \'Y\' or \'N\' and press Enter: ')
            restart = restart.lower()

        if restart == 'n':
            break


if __name__ == "__main__":
	main()
