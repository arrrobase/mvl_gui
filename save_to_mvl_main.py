from win32com.client import DispatchEx
import os


def save_to_mvl_main(workbook, previous_we, collection):
    """
    Saves collection as a new sheet in workbook.

    :param workbook:
    :param previous_we:
    :param collection:
    :return:
    """
    wb_path = os.path.abspath(workbook)
    assert os.path.exists(wb_path)

    try:
        sheet_to_copy = 'WE ' + previous_we.strftime('%m-%d-%y')
    except AttributeError:
        sheet_to_copy = previous_we

    new_name = 'WE ' + collection.week_end.strftime('%m-%d-%y')

    # use DipsatchEx to create new instance of Excel to avoid interfering with
    # other open instances
    # workbook must still be closed, but other workbooks can be opened
    excel = DispatchEx('Excel.Application')
    wb = excel.Workbooks.Open(wb_path)

    # make copy and move to before original
    wb.Worksheets(sheet_to_copy).Copy(wb.Worksheets(sheet_to_copy))

    # rename worksheet
    sh_name2 = sheet_to_copy + ' (2)'
    wb.Worksheets(sh_name2).Name = new_name

    wb.Save()
    # quit and make sure process ends
    excel.Quit()
    del excel

    print 'Done'
