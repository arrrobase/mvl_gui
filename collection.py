import numpy as np
import pandas as pd
from money import Money
from datetime import datetime as dt
from random import randint
import xlsxwriter
# from collections import OrderedDict
import cPickle


class Collection:
    """
    Class containing 1 week of collections.
    """
    def __init__(self, week_end, collection_dates, washer_names, dryer_names):

        self.id = id(self)

        self.week_end = dt.strptime(week_end, '%m/%d/%y')
        self.num_periods = len(collection_dates)
        self.period_dates = list(map(lambda date: dt.strptime(date, '%m/%d/%y'), collection_dates))

        self.washer_names = washer_names
        self.dryer_names = dryer_names

        self.df_washer = self.make_df(self.washer_names)
        self.df_dryer = self.make_df(self.dryer_names)
        self.df_meters, self.df_changers, self.df_others = self.make_other_dfs()

        self.grouped = None
        self.stats = None

    def make_df(self, machine_names):
        """
        Makes machine specific pandas dataframe object.

        :return: pandas df
        """
        per_period = ['weights', 'amounts']

        weights = ['' for i in range(len(machine_names))]
        amounts = [Money.from_weight(i) for i in weights]

        periods = [i for i in range(self.num_periods)]
        cols = pd.MultiIndex.from_product([periods, per_period], names=[
            'Period', None])

        ar = np.array([weights, amounts] * self.num_periods)
        ar = np.transpose(ar)

        df = pd.DataFrame(ar, columns=cols)
        df['names'] = machine_names

        return df

    def make_other_dfs(self):
        """
        Makes dfs for meters, changer, and other coin amounts
        :return:
        """
        meters = ['gas',
                  'n-gas',
                  'S262',
                  'S263',
                  'water',
                  'lights']

        df_meters = pd.DataFrame({'meters': meters})
        df_meters['readings'] = [np.NAN for i in meters]

        changers = ['1',
                    '5',
                    '10',
                    '20',
                    'a',
                    'b',
                    'error']

        df_changers = pd.DataFrame({'bills': changers})
        df_changers['left'] = [np.NAN for i in changers]
        df_changers['right'] = [np.NAN for i in changers]

        labels = ['Total Weekly',
                  'Soap',
                  'Barrel',
                  'Purse']

        amounts = [Money() for i in labels]
        df_others = pd.DataFrame({'labels': labels, 'amounts':amounts})

        return df_meters, df_changers, df_others

    def __repr__(self):
        return 'Week end: {}, periods: {}'.format(self.week_end.strftime(
            '%m/%d/%y'), self.num_periods)

    def __lt__(self, other):
        return self.week_end < other.week_end

    def merge_machines(self):
        return pd.concat(self.df_washer, self.df_dryer)

    @staticmethod
    def set_value(df, row, value, period=None):
        if period is None:
            df.set_value(row, 'weights', value)

        else:
            df.set_value(row, (period, 'weights'), value)

        Collection.update(df, period)

    @staticmethod
    def update(df, period=None):
        if period is None:
            # propagate changes
            amounts = list(map(Money.from_weight, df['weights']))
            diff = [amounts[0]] + list(np.diff(amounts))

            for ind, i in enumerate(diff):
                if i < 0:
                    diff[ind] = Money.from_weight(df['weights'][ind])

            df['amounts'] = diff

        else:
            # propagate changes
            amounts = list(map(Money.from_weight, df[period]['weights']))
            diff = [amounts[0]] + list(np.diff(amounts))

            for ind, i in enumerate(diff):
                if i < 0:
                    diff[ind] = Money.from_weight(df[period]['weights'][ind])

            df[period]['amounts'] = diff


    @staticmethod
    def make_weights(n):
        base = 0
        i = 0
        while i < n:
            s = ''
            base += randint(0, 5)
            if base > 20:
                base -= 20
            s += str(base)
            s += ' '
            s += str(randint(0, 15))
            s += '.'
            s += str(randint(0, 9))
            yield s
            i += 1

    # def get_stats(self):
    #     stats = self.df.copy()
    #     self.stats = stats.applymap(float)
    #
    #     self.grouped = self.stats.groupby(lambda x: type(x).__name__)
    #
    #     desc = self.grouped.describe(percentiles=[])
    #     # map all but count to money
    #     desc.iloc[1:7, :] = desc.iloc[1:7, :].applymap(Money)
    #     desc.iloc[8:, :] = desc.iloc[8:, :].applymap(Money)
    #
    #     to_print = ''
    #     to_print += str(desc)
    #     to_print += '\n'
    #
    #     dryer_total = desc.loc['Dryer'].loc['sum'].sum()
    #     washer_total = desc.loc['Washer'].loc['sum'].sum()
    #
    #     to_print += '\n'
    #     to_print += 'Dryer '
    #     to_print += str(dryer_total)
    #     to_print += '\n'
    #     to_print += 'Washer '
    #     to_print += str(washer_total)
    #     to_print += '\n'
    #     to_print += '-' * 14
    #     to_print += '\n'
    #     to_print += 'Total  '
    #     to_print += str(dryer_total + washer_total)
    #
    #     return to_print

    # def get_sum(self):
    #     return Money(self.df.sum().sum())

    # def get_plots(self):
    #     # if self.grouped is None:
    #     #     self.get_stats()
    #     if self.stats is None:
    #         self.get_stats()
    #
    #     self.stats.plot.bar(stacked=True)
    #     import matplotlib.pyplot as plt
    #     plt.show()

    def to_csv(self):
        print 'saving...'
        print
        print self.df_washer

        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook('test_out.xlsx')
        worksheet = workbook.add_worksheet()

        worksheet.write(0, 0, 'Period End')

        # formats
        date_format = workbook.add_format({'num_format': 'mm/dd/yy'})
        center_format = workbook.add_format({'align': 'center'})

        date_merge = workbook.add_format({'num_format': 'mm/dd/yy',
                                          'align': 'center'})

        # write headers
        for i, date in enumerate(self.period_dates):
            worksheet.merge_range(0, i*2+1, 0, i*2+2, date, date_merge)
            worksheet.write(1, i*2+1, 'weights')
            worksheet.write(1, i*2+2, 'amounts')

        to_write = self.df_washer['names']
        worksheet.write_column(2, 0, to_write)

        # write data
        to_write = self.df_washer[0]['weights']
        worksheet.write_column(2, 1, to_write)

        workbook.close()
        print
        print 'saved'

        # print '\npickling...'
        # with open('test_pickle.pkl', 'wb') as f:
        #     cPickle.dump(self, f, -1)
        # print '\npickled'

