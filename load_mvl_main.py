import xlrd
from xlrd import xldate as xd
from collection import Collection, washer_names, dryer_names
from money import Money
import numpy as np
# from line_profiler import profile


def get_sheet_names(wb):
    sheet_names = wb.sheet_names()
    sheet_names = [i for i in sheet_names if i.startswith('WE')]
    return sheet_names


# @profile
def get_sheet_data(sheet, sh, changer_rows, washer_rows, dryer_rows):
        # dates
        start = xd.xldate_as_datetime(sh.cell_value(0, 1), 0)
        end = xd.xldate_as_datetime(sh.cell_value(1, 1), 0)
        period_1 = xd.xldate_as_datetime(sh.cell_value(2, 1), 0)

        # meters
        meters = [sh.cell_value(i, 1) for i in [7, 8, 9, 10, 12]]
        meters = [i if i else np.NAN for i in meters]
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

        # other coin amounts
        weekly_lb = str(sh.cell_value(116, 23))
        weekly_oz = str(sh.cell_value(116, 24))
        weekly = ' '.join([weekly_lb, weekly_oz]).strip()
        weekly = Money.from_weight(weekly)

        # period 1 washers
        period_1_lb = sh.col_values(7, 32, 37)
        period_1_oz = sh.col_values(8, 32, 37)

        period_1_lb = [str(int(i)) if i != '' else '' for i in period_1_lb]
        period_1_oz = [str(i) if i != '' else '' for i in period_1_oz]

        period_1_washer = [' '.join([i, j]).strip() for i, j in list(zip(
            period_1_lb, period_1_oz))]
        period_1_washer += [''] * 23

        # period 2 washers
        period_2_washer_lb = sh.col_values(12, 32, 37) \
                             + sh.col_values(12, 38, 44) \
                             + sh.col_values(12, 45, 57) \
                             + sh.col_values(12, 58, 63)
        period_2_washer_oz = sh.col_values(13, 32, 37) \
                             + sh.col_values(13, 38, 44) \
                             + sh.col_values(13, 45, 57) \
                             + sh.col_values(13, 58, 63)

        period_2_washer_lb = [str(int(i)) if i != '' else '' for i in period_2_washer_lb]
        period_2_washer_oz = [str(i) if i != '' else '' for i in period_2_washer_oz]

        period_2_washer = [' '.join([i, j]).strip() for i, j in list(zip(period_2_washer_lb,
                                                                 period_2_washer_oz))]

        # period 2 dryers
        period_2_dryer_lb = sh.col_values(12, 69, 79) \
                             + sh.col_values(12, 80, 86) \
                             + sh.col_values(12, 87, 101)
        period_2_dryer_oz = sh.col_values(13, 69, 79) \
                             + sh.col_values(13, 80, 86) \
                             + sh.col_values(13, 87, 101)

        period_2_dryer_lb = [str(int(i)) if i != '' else '' for i in period_2_dryer_lb]
        period_2_dryer_oz = [str(i) if i != '' else '' for i in period_2_dryer_oz]

        period_2_dryer = [' '.join([i, j]).strip() for i, j in list(zip(period_2_dryer_lb,
                                                                period_2_dryer_oz))]

        # make collection
        col = Collection(end.strftime('%m/%d/%y'),
                         [period_1.strftime('%m/%d/%y'), end.strftime('%m/%d/%y')],
                         washer_names, dryer_names, sheet_name=sheet)

        # set values
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

        col.df_others.loc[0] = weekly

        return col

# @profile
def load_mvl_main(workbook='MVL main FILE.xlsx'):

    wb = xlrd.open_workbook(workbook)

    sheets = get_sheet_names(wb)

    washer_rows  = list(range(32, 37)) + list(range(38, 44)) + list(range(45, 57)) + list(range(58, 63))
    dryer_rows   = list(range(69, 79)) + list(range(80, 86)) + list(range(87, 101))
    changer_rows = list(range(113, 117))

    cols = []

    for ind, sheet in enumerate(sheets):
        try:
            print '{}.'.format(ind+1), sheet,
            sh = wb.sheet_by_name(sheet)
            col = get_sheet_data(sheet, sh, changer_rows, washer_rows,
                                 dryer_rows)
            print col, '.... Done'
            cols.append(col)
        except:
            print 'error with sheet:', sheet
            raise

    print '\nDone'
    return cols


if __name__ == '__main__':
    load_mvl_main()

