import xlrd
from xlrd import xldate as xd
from collection import Collection
import numpy as np


def load_mvl_main(workbook, dryer_names, washer_names):

    wb = xlrd.open_workbook(workbook)

    sheets = [i for i in wb.sheet_names() if i.startswith('WE')]

    washer_rows  = list(range(32, 37)) + list(range(38, 44)) + list(range(45, 57)) + list(range(58, 63))
    dryer_rows   = list(range(69, 79)) + list(range(80, 86)) + list(range(87, 101))
    changer_rows = list(range(113, 117))

    cols = []

    for sh in sheets:
        name = sh

        try:
            sh = wb.sheet_by_name(sh)

            # dates
            start = xd.xldate_as_datetime(sh.cell_value(0, 1), 0)
            end = xd.xldate_as_datetime(sh.cell_value(1, 1), 0)
            period_1 = xd.xldate_as_datetime(sh.cell_value(2, 1), 0)

            # meters
            meters = [sh.cell_value(i, 1) for i in [7, 8, 9, 10, 12]]
            meters.insert(1, np.NAN)

            # changers
            changer_right = [sh.col(21)[i].value for i in changer_rows]
            changer_right = [int(i) if i else np.NAN for i in changer_right]
            changer_right += [np.NAN] * 3

            if sh.cell_value(112, 20) == 'Changer L':
                changer_left = [sh.col(20)[i].value for i in changer_rows]
                changer_left = [int(i) if i else np.NAN for i in changer_left]
                changer_left += [np.NAN] * 3

            else:
                changer_left = None


            # period 1 washers
            period_1_lb = [sh.col(7)[i].value for i in range(32, 37)]
            period_1_oz = [sh.col(8)[i].value for i in range(32, 37)]

            period_1_lb = [str(int(i)) if i != '' else '' for i in period_1_lb]
            period_1_oz = [str(i) if i != '' else '' for i in period_1_oz]

            period_1_washer = [' '.join([i, j]) for i, j in list(zip(period_1_lb,
                                                                     period_1_oz))]
            period_1_washer += [''] * 23

            # period 2 washers
            period_2_washer_lb = [sh.col(12)[i].value for i in washer_rows]
            period_2_washer_oz = [sh.col(13)[i].value for i in washer_rows]

            period_2_washer_lb = [str(int(i)) if i != '' else '' for i in period_2_washer_lb]
            period_2_washer_oz = [str(i) if i != '' else '' for i in period_2_washer_oz]

            period_2_washer = [' '.join([i, j]) for i, j in list(zip(period_2_washer_lb,
                                                                     period_2_washer_oz))]

            # period 2 dryers
            period_2_dryer_lb = [sh.col(12)[i].value for i in dryer_rows]
            period_2_dryer_oz = [sh.col(13)[i].value for i in dryer_rows]

            period_2_dryer_lb = [str(int(i)) if i != '' else '' for i in period_2_dryer_lb]
            period_2_dryer_oz = [str(i) if i != '' else '' for i in period_2_dryer_oz]

            period_2_dryer = [' '.join([i, j]) for i, j in list(zip(period_2_dryer_lb,
                                                                    period_2_dryer_oz))]

            # make collection
            col = Collection(end.strftime('%m/%d/%y'),
                             [period_1.strftime('%m/%d/%y'), end.strftime('%m/%d/%y')],
                             washer_names, dryer_names)

            # set meter values
            col.df_meters['readings'] = meters

            col.df_washer[(0, 'weights')] = period_1_washer
            Collection.update(col.df_washer, 0)

            col.df_washer[(1, 'weights')] = period_2_washer
            Collection.update(col.df_washer, 1)

            col.df_dryer[(1, 'weights')] = period_2_dryer
            Collection.update(col.df_dryer, 1)

            col.df_changers['right'] = changer_right
            if changer_left is not None:
                col.df_changers['left'] = changer_left

            cols.append(col)
            print name, col, '   .... Done'

        except:
            print 'error with sheet:', name
            raise

    print '\nDone'
    return cols



