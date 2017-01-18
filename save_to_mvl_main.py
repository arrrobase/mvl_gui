from win32com.client import DispatchEx
import os
import numpy as np
import datetime


def save_to_mvl_main(workbook, previous_we, col):
    """
    Saves collection as a new sheet in workbook.

    :param workbook:
    :param previous_we:
    :param col:
    :return:
    """
    wb_path = os.path.abspath(workbook)
    assert os.path.exists(wb_path)

    sheet_to_copy = 'blank'
    insert_before = 'WE ' + previous_we.strftime('%m-%d-%y')

    new_name = 'WE ' + col.week_end.strftime('%m-%d-%y')

    # use DipsatchEx to create new instance of Excel to avoid interfering with
    # other open instances
    # workbook must still be closed, but other workbooks can be opened
    excel = DispatchEx('Excel.Application')

    try:
        wb = excel.Workbooks.Open(wb_path)

        # make copy and move to correct position
        wb.Worksheets(sheet_to_copy).Copy(wb.Worksheets(insert_before))

        # rename worksheet
        sh_name2 = sheet_to_copy + ' (2)'
        wb.Worksheets(sh_name2).Name = new_name

        sh = wb.Worksheets(new_name)

        # write dates
        start = (col.week_end - datetime.timedelta(days=6)).strftime('%m-%d-%y')
        end = col.week_end.strftime('%m/%d/%y')
        period_1 = col.period_dates[0].strftime('%m/%d/%y')

        sh.Cells(1, 2).Value = start
        sh.Cells(2, 2).Value = end
        sh.Cells(3, 2).Value = period_1

        # write meters
        meters = list(col.df_meters['readings'])
        meters.pop(1)
        for ind, i in enumerate([8, 9, 10, 11, 13]):
            to_write = meters[ind]
            if np.isnan(to_write):
                sh.Cells(i, 2).Value = ''
            else:
                sh.Cells(i, 2).Value = to_write

        # write changers
        changer_rows = list(range(114, 118))
        changer_right = list(col.df_changers['right'])
        for ind, i in enumerate(changer_rows):
            sh.Cells(i, 22).Value = changer_right[ind]

        changer_left = list(col.df_changers['left'])
        if not np.isnan(changer_left[0]):
            for ind, i in enumerate(changer_rows):
                sh.Cells(i, 21).Value = changer_left[ind]

        # TODO fix and write remaining

        washer_rows = list(range(33, 38)) +\
                      list(range(39, 45)) +\
                      list(range(46, 58)) +\
                      list(range(59, 64))

        dryer_rows  = list(range(70, 80)) +\
                      list(range(81, 87)) +\
                      list(range(88, 102))

        def unpack(weights):
            lbs = []
            ozes = []

            for i in weights:
                try:
                    lb, oz = i.split(' ')
                    lbs.append(lb)
                    ozes.append(oz)

                except ValueError:
                    if not i:
                        lbs.append('')
                        ozes.append('')

                    else:
                        lbs.append('')
                        ozes.append(i)

            return lbs, ozes

        # write period 1 and 2 washers
        period_1_washer = list(col.df_washer[(0, 'weights')])
        period_1_lb, period_1_oz = unpack(period_1_washer)

        period_2_washer = list(col.df_washer[(1, 'weights')])
        period_2_lb, period_2_oz = unpack(period_2_washer)

        for ind, i in enumerate(washer_rows):
            # period 1
            sh.Cells(i, 8).Value = period_1_lb[ind]
            sh.Cells(i, 9).Value = period_1_oz[ind]
            # period 2
            sh.Cells(i, 13).Value = period_2_lb[ind]
            sh.Cells(i, 14).Value = period_2_oz[ind]

        # write period 1 and 2 dryers
        period_1_dryer = list(col.df_dryer[(0, 'weights')])
        period_1_lb, period_1_oz = unpack(period_1_dryer)

        period_2_dryer = list(col.df_dryer[(1, 'weights')])
        period_2_lb, period_2_oz = unpack(period_2_dryer)

        for ind, i in enumerate(dryer_rows):
            # period 1
            sh.Cells(i, 8).Value = period_1_lb[ind]
            sh.Cells(i, 9).Value = period_1_oz[ind]
            # period 2
            sh.Cells(i, 13).Value = period_2_lb[ind]
            sh.Cells(i, 14).Value = period_2_oz[ind]

        wb.Save()

    except:
        excel.Quit()
        del excel
        raise

    # quit and make sure process ends
    excel.Quit()
    del excel

    print 'saved sheet "{}" in {}.'.format(new_name, wb_path)
