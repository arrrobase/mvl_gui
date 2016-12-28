"""
Main frame
"""

import wx, wx.grid
import pandas as pd
import numpy as np
import datetime
from wx import calendar
from money import Money
from collection import Collection
from copy import deepcopy

dryer_names  = ['{}'.format(i) for i in range(1, 17)]
dryer_names += ['{}'.format(i) for i in range(67, 71)]
dryer_names += ['{}'.format(i) for i in range(72, 76)]
dryer_names += ['20']
dryer_names += ['{}'.format(i) for i in range(23, 28)]

washer_names = ['A51',
                'B51',
                'S52',
                'A40',
                'W50',
                'E26',
                'F26',
                'D25',
                'C25',
                'B25',
                'A25',
                '*12',
                '*12',
                '*12',
                '*12',
                '*12',
                '*12',
                '*12',
                '*12',
                '*12',
                '*12',
                '*12',
                '*12',
                'E20',
                'D20',
                'C20',
                'B20',
                'A20'
                ]

col1 = Collection('11/25/16', ['11/21/16', '11/25/16'],
                  washer_names, dryer_names)

col2 = Collection('11/18/16', ['11/14/16', '11/16/16', '11/18/16'],
                  washer_names, dryer_names)

today = datetime.datetime.now()

empty_col = Collection(today.strftime('%m/%d/%y'),
                       [(today - datetime.timedelta(days=4)).strftime('%m/%d/%y'),
                        today.strftime('%m/%d/%y')],
                       washer_names, dryer_names)


class ListPanel(wx.Panel):
    """
    Panel containing list of collection dates.
    """
    def __init__(self, parent):
        super(ListPanel, self).__init__(parent)

        self.frame = parent.GetTopLevelParent()

        self.col = None
        self.col_dict = None

        self.washer_period_dfs = None
        self.dryer_period_dfs = None

        self.df_meters = None
        self.df_changers = None
        self.df_others = None

        # panel sizer
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # list control
        self.list_control = wx.ListCtrl(self, style=wx.LC_REPORT)

        # add columns to list
        self.list_control.InsertColumn(0, 'Week End')
        self.list_control.InsertColumn(1, 'Periods')

        # temp add for shape
        cols = [col1, col2]

        # add cols to list control, and make lookup dict
        self.col_dict = {}
        for ind, col in enumerate(sorted(cols)):
            we_string = col.week_end.strftime('%m/%d/%y')
            self.list_control.InsertStringItem(ind, we_string)
            self.list_control.SetStringItem(ind, 1, str(col.num_periods))
            self.list_control.SetItemData(ind, col.id)
            self.col_dict[col.id] = col

        panel_sizer.Add(self.list_control,
                        flag=wx.EXPAND,
                        proportion=1)

        self.SetSizer(panel_sizer)
        panel_sizer.Fit(self)

        # binder for double click on list item
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_double_click,
                  self.list_control)

    def split_col(self):
        """
        Splits collection dataframes up by periods.
        """
        washers = [pd.concat([self.col.df_washer[i],
                              self.col.df_washer['names']], axis=1)
                   for i in range(self.col.num_periods)]

        dryers = [pd.concat([self.col.df_dryer[i],
                             self.col.df_dryer['names']], axis=1)
                  for i in range(self.col.num_periods)]

        return washers, dryers

    def unsplit_col(self):
        """
        Unsplits collection dataframes back into single dfs.
        """
        per_period = ['weights', 'amounts']
        dfs = [self.washer_period_dfs, self.dryer_period_dfs]
        names = [self.col.washer_names, self.col.dryer_names]

        ret = []

        for i, df in enumerate(dfs):
            re_df = pd.DataFrame()

            for ind, period_df in enumerate(df):
                period_df = period_df[['weights', 'amounts']]
                cols = pd.MultiIndex.from_product([[ind], per_period],
                                                  names=['Period', None])
                period_df = pd.DataFrame(np.array(period_df), columns=cols)
                re_df = pd.concat([re_df, period_df], axis=1)

            re_df['names'] = names[i]

            ret.append(re_df)

        return ret

    def on_double_click(self, event):
        """
        Updates attributes, calls load.

        :param event:
        """
        selected = event.m_itemIndex
        col = self.col_dict[self.list_control.GetItemData(selected)]

        if col is not self.col:
            self.frame.save_collection()
            self.frame.load_collection(col)

    def save_collection(self, saves):
        # "save" currently selected
        if self.col is not None:
            self.col.df_washer, self.col.df_dryer = self.unsplit_col()
            self.col.df_meters, self.col.df_changers, self.col.df_others = saves

            self.col_dict[self.col.id] = self.col

    def load_collection(self, col):
        """
        Loads in new collection.
        :param col:
        """
        if col is not self.col:
            self.update(col)

    def update(self, col):
        """
        Updates proper attributes.

        :param col:
        """
        self.col = col
        self.frame.col = col

        self.washer_period_dfs, self.dryer_period_dfs = self.split_col()

        self.df_meters = col.df_meters
        self.df_changers = col.df_changers
        self.df_others = col.df_others


class CalendarPanel(wx.Panel):
    """
    Panel containing simple calendar.
    """
    def __init__(self, parent):
        super(CalendarPanel, self).__init__(parent)

        self.frame = parent.GetTopLevelParent()

        # panel sizer
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # calendar control
        self.calendar_control = calendar.GenericCalendarCtrl(parent=self,
            style=calendar.CAL_SEQUENTIAL_MONTH_SELECTION)

        panel_sizer.Add(self.calendar_control,
                        flag=wx.EXPAND)

        self.SetSizer(panel_sizer)
        panel_sizer.Fit(self)

        self.col_days = {}
        for col in self.frame.list_panel.col_dict.itervalues():
            date = col.week_end
            if date.year not in self.col_days:
                self.col_days[date.year] = {}

            if date.month not in self.col_days[date.year]:
                self.col_days[date.year][date.month] = []

            self.col_days[date.year][date.month].append(date.day)

        self.reset_cal()

        self.Bind(calendar.EVT_CALENDAR_MONTH,
                  self.reset_cal,
                  self.calendar_control)

        self.Bind(calendar.EVT_CALENDAR_YEAR,
                  self.reset_cal,
                  self.calendar_control)

    def reset_cal(self, event=None):
        # turn wx.datetime into datetime.date
        date = self.calendar_control.GetDate()
        ymd = map(int, date.FormatISODate().split('-'))
        date = datetime.date(*ymd)

        for day in range(1, 32):
            self.calendar_control.ResetAttr(day)

        if date.year in self.col_days:
            if date.month in self.col_days[date.year]:
                for day in self.col_days[date.year][date.month]:
                    self.calendar_control.SetAttr(day,
                        calendar.CalendarDateAttr(colBack=(255, 69, 0, 100)))


class MeterPanel(wx.Panel):
    """
    Panel containing view of meter readings.
    """
    def __init__(self, parent):
        super(MeterPanel, self).__init__(parent)

        self.frame = parent.GetTopLevelParent()

        # panel sizer
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # label
        title = wx.StaticText(self, label='Meter Readings')

        # create control
        self.grid = MyGrid(self, empty_col.df_meters, MyMetersDataSource)
        self.grid.SetColLabelSize(0)

        panel_sizer.Add(title,
                        border=5,
                        flag=wx.TOP | wx.BOTTOM | wx.LEFT)

        panel_sizer.Add(wx.StaticLine(self),
                        flag=wx.EXPAND)

        panel_sizer.Add(self.grid)

        self.SetSizer(panel_sizer)
        panel_sizer.Fit(self)

    def update_grid(self, values):
        for i, value in enumerate(values):
            self.grid.Table.SetValue(i, 0, value)

        msg = wx.grid.GridTableMessage(self.grid.Table,
                                       wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.grid.ProcessTableMessage(msg)


class ChangerPanel(wx.Panel):
    """
    Panel containing view of meter readings.
    """
    def __init__(self, parent):
        super(ChangerPanel, self).__init__(parent)

        self.frame = parent.GetTopLevelParent()

        # panel sizer
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # label
        title = wx.StaticText(self, label='Changer Readings')

        # create control
        self.grid = MyGrid(self, empty_col.df_changers, MyChangersDataSource)
        self.grid.SetColLabelSize(0)

        panel_sizer.Add(title,
                        border=5,
                        flag=wx.TOP | wx.BOTTOM | wx.LEFT)

        panel_sizer.Add(wx.StaticLine(self),
                        flag=wx.EXPAND)

        panel_sizer.Add(self.grid)

        self.SetSizer(panel_sizer)
        panel_sizer.Fit(self)

    def update_grid(self, values):
        left = values['left']
        right = values['right']

        for i, column in enumerate([left, right]):
            for j, value in enumerate(column):
                # print i, j, value
                self.grid.Table.SetValue(j, i, value)

        msg = wx.grid.GridTableMessage(self.grid.Table,
                                       wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.grid.ProcessTableMessage(msg)


class OtherPanel(wx.Panel):
    """
    Panel containing view of meter readings.
    """
    def __init__(self, parent):
        super(OtherPanel, self).__init__(parent)

        self.frame = parent.GetTopLevelParent()

        # panel sizer
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # label
        title = wx.StaticText(self, label='Other Coin Amounts')

        # create control
        self.grid = MyGrid(self, empty_col.df_others, MyOthersDataSource)
        self.grid.SetColLabelSize(0)

        panel_sizer.Add(title,
                        border=5,
                        flag=wx.TOP | wx.BOTTOM | wx.LEFT)

        panel_sizer.Add(wx.StaticLine(self),
                        flag=wx.EXPAND)

        panel_sizer.Add(self.grid)

        self.SetSizer(panel_sizer)
        panel_sizer.Fit(self)

    def update_grid(self, values):
        for i, value in enumerate(values):
            self.grid.Table.SetValue(i, 0, value)

        msg = wx.grid.GridTableMessage(self.grid.Table,
                                       wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.grid.ProcessTableMessage(msg)


class MyMachineDataSource(wx.grid.PyGridTableBase):
    def __init__(self, data):
        super(MyMachineDataSource, self).__init__()

        self.data = data

    def GetNumberCols(self):
        return 2

    def GetNumberRows(self):
        return len(self.data)

    def GetValue(self, row, col):
        keys = {0: 'weights',
                1: 'amounts'}

        val = self.data[keys[col]][row]

        try:
            if col == 1 and np.isnan(val.amount):
                val = ''
        except:
            pass
        finally:
            return val

    def SetValue(self, row, col, value):
        if col == 0:
            Collection.update(self.data, row, value)

        msg = wx.grid.GridTableMessage(self.GetView().Table,
                                       wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.GetView().ProcessTableMessage(msg)

    def GetColLabelValue(self, col):
        cols = ['Weights (lb oz)', 'Amounts']

        return cols[col]

    def GetRowLabelValue(self, row):
        return self.data['names'][row]


class MyMetersDataSource(wx.grid.PyGridTableBase):
    def __init__(self, data):
        super(MyMetersDataSource, self).__init__()

        self.data = data

    def GetNumberCols(self):
        return 1

    def GetNumberRows(self):
        return len(self.data)

    def GetValue(self, row, col):
        val = self.data['readings'][row]

        try:
            if np.isnan(val):
                val = ''
        except:
            pass
        finally:
            return val

    def SetValue(self, row, col, value):
        self.data.set_value(row, 'readings', float(value))

    def GetColLabelValue(self, col):
        return 'Readings'

    def GetRowLabelValue(self, row):
        return self.data['meters'][row]


class MyChangersDataSource(wx.grid.PyGridTableBase):
    def __init__(self, data):
        super(MyChangersDataSource, self).__init__()

        self.data = data

    def GetNumberCols(self):
        return 2

    def GetNumberRows(self):
        return len(self.data)

    def GetValue(self, row, col):
        keys = {0: 'left',
                1: 'right'}

        val = self.data[keys[col]][row]

        try:
            if np.isnan(val):
                val = ''
            else:
                val = int(val)
        except:
            pass
        finally:
            return val

    def SetValue(self, row, col, value):
        keys = {0: 'left',
                1: 'right'}

        self.data.set_value(row, keys[col], float(value))

    def GetColLabelValue(self, col):
        # spaces to make columns larger
        labels = ['left    ', 'right   ']

        return labels[col]

    def GetRowLabelValue(self, row):
        return self.data['bills'][row]


class MyOthersDataSource(wx.grid.PyGridTableBase):
    def __init__(self, data):
        super(MyOthersDataSource, self).__init__()

        self.data = data

    def GetNumberCols(self):
        return 1

    def GetNumberRows(self):
        return len(self.data)

    def GetValue(self, row, col):
        val = self.data['amounts'][row]

        try:
            if np.isnan(val.amount):
                val = ''
        except:
            pass
        finally:
            return val

    def SetValue(self, row, col, value):
        self.data.set_value(row, 'amounts', Money(float(value)))

    def GetColLabelValue(self, col):
        return 'Amounts'

    def GetRowLabelValue(self, row):
        return self.data['labels'][row]


class MyGrid(wx.grid.Grid):
    """
    Class for custom grid.
    """
    def __init__(self, parent, data, source):
        super(MyGrid, self).__init__(parent)

        self.SetTable(source(data))
        self.AutoSizeColumns()


class PeriodPanel(wx.Panel):
    """
    Class for grid for a single period.
    """
    def __init__(self, parent, period_num):
        super(PeriodPanel, self).__init__(parent)

        self.frame = parent.GetTopLevelParent()

        self.period_num = period_num
        self.period_end = self.frame.col.period_dates[self.period_num]

        self.washer_grid = MyGrid(self,
            self.frame.list_panel.washer_period_dfs[period_num],
            MyMachineDataSource)

        self.dryer_grid = MyGrid(self,
            self.frame.list_panel.dryer_period_dfs[period_num],
            MyMachineDataSource)

        # panel sizer
        panel_sizer = wx.BoxSizer(wx.HORIZONTAL)

        panel_sizer.Add(self.washer_grid,
                        border=5,
                        flag=wx.RIGHT)
        panel_sizer.Add(self.dryer_grid)

        self.SetSizer(panel_sizer)


class MachinePanel(wx.Panel):
    """
    Panel with sheets of washers and dryers.
    """
    def __init__(self, parent):
        super(MachinePanel, self).__init__(parent)

        self.frame = parent.GetTopLevelParent()

        # notebook to hold panels
        self.machine_nb = wx.Notebook(self)

    def load_collection(self):

        periods = self.frame.col.num_periods

        self.period_panels = [PeriodPanel(self.machine_nb, i) for i in
                              range(periods)]

        while self.machine_nb.GetPageCount():
            self.machine_nb.DeletePage(0)

        for panel in self.period_panels:
            self.machine_nb.AddPage(panel, 'Period {} - {}'.format(
                panel.period_num + 1, panel.period_end.strftime('%m/%d/%y')))

        panel_sizer = wx.BoxSizer(wx.HORIZONTAL)

        panel_sizer.Add(self.machine_nb)

        self.SetSizer(panel_sizer)
        panel_sizer.Fit(self)


class TopPanel(wx.Panel):
    """
    Panel holding the top row of panels.
    """
    def __init__(self, parent):
        super(TopPanel, self).__init__(parent)

        self.frame = parent.GetTopLevelParent()

        # panel sizer
        panel_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # panels
        self.meter_panel = MeterPanel(self)
        self.changer_panel = ChangerPanel(self)
        self.other_panel = OtherPanel(self)

        panel_sizer.Add(self.meter_panel,
                        flag=wx.EXPAND | wx.LEFT,
                        border=3)

        panel_sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL),
                        flag=wx.LEFT | wx.RIGHT | wx.EXPAND,
                        border=5)

        panel_sizer.Add(self.changer_panel,
                        flag=wx.EXPAND)

        panel_sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL),
                        flag=wx.LEFT | wx.RIGHT | wx.EXPAND,
                        border=5)

        panel_sizer.Add(self.other_panel,
                        flag=wx.EXPAND | wx.RIGHT,
                        border=3)

        self.SetSizer(panel_sizer)
        panel_sizer.Fit(self)

    def load_collection(self):
        self.meter_panel.update_grid(self.frame.col.df_meters['readings'])
        self.changer_panel.update_grid(self.frame.col.df_changers[['left',
                                                                   'right']])
        self.other_panel.update_grid(self.frame.col.df_others['amounts'])


class MyFrame(wx.Frame):
    """
    Class for generating main frame.
    """
    def __init__(self):
        super(MyFrame, self).__init__(None, title='MVL collections')

        self.col = None

        # make calendar and list
        self.list_panel = ListPanel(self)
        self.calendar_panel = CalendarPanel(self)

        # calendar and list sizer
        calendar_list_sizer = wx.BoxSizer(wx.VERTICAL)

        calendar_list_sizer.Add(self.calendar_panel,
                                flag=wx.EXPAND)

        calendar_list_sizer.Add(self.list_panel,
                                proportion=1,
                                flag=wx.EXPAND)

        # make meter and notebook panel
        self.machine_panel = MachinePanel(self)
        self.top_panel = TopPanel(self)

        self.load_collection(empty_col)

        # top and machine sizer
        top_machine_sizer = wx.BoxSizer(wx.VERTICAL)

        top_machine_sizer.Add(self.top_panel)
        top_machine_sizer.Add(wx.StaticLine(self),
                              border=5,
                              flag=wx.TOP | wx.BOTTOM | wx.EXPAND)
        top_machine_sizer.Add(self.machine_panel)

        # frame sizer
        frame_sizer = wx.BoxSizer(wx.HORIZONTAL)

        frame_sizer.Add(calendar_list_sizer,
                        flag=wx.EXPAND)

        frame_sizer.Add(top_machine_sizer,
                        flag=wx.EXPAND)

        self.SetSizer(frame_sizer)
        frame_sizer.Fit(self)

        # change background color to match panels on win32
        self.SetBackgroundColour(wx.NullColour)

        self.Show()

    def load_collection(self, col):
        self.list_panel.load_collection(col)
        self.machine_panel.load_collection()
        self.top_panel.load_collection()

    def save_collection(self):
        saves = [deepcopy(panel.grid.Table.data) for panel in
                 self.top_panel.GetChildren()]

        self.list_panel.save_collection(saves)


def main():
    """
    Main function to start GUI.
    """
    # instantiate app
    global app
    app = wx.App(False)
    # instantiate window
    frame = MyFrame()
    # run app
    app.MainLoop()

if __name__ == '__main__':
    main()