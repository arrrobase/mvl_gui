"""
Main frame
"""

import wx, wx.grid
import pandas as pd
import numpy as np
from wx import calendar
from money import Money
from collection import Collection

dryer_names = ['{}'.format(i) for i in range(1, 17)]
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

print col2.df_washer


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
        self.calendar_control = calendar.CalendarCtrl(parent=self)

        panel_sizer.Add(self.calendar_control,
                        flag=wx.EXPAND)

        self.SetSizer(panel_sizer)
        panel_sizer.Fit(self)


class ListPanel(wx.Panel):
    """
    Panel containing list of collection dates.
    """
    def __init__(self, parent):
        super(ListPanel, self).__init__(parent)

        self.frame = parent.GetTopLevelParent()
        self.col = None
        self.col_dict= None
        self.washer_period_dfs = None
        self.dryer_period_dfs = None

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
        self.col_dict= {}
        for ind, col in enumerate(cols):
            self.list_control.InsertStringItem(ind, col.week_end.strftime('%m/%d/%y'))
            self.list_control.SetStringItem(ind, 1, str(col.num_periods))
            self.list_control.SetItemData(ind, col.id)
            self.col_dict[col.id] = col

        # set current to last item in list control
        # self.load_collection(self.col_dict[self.list_control.GetItemData(
        #     self.list_control.GetItemCount()-1)])

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

    def load_collection(self, col):
        # "save" currently selected
        if self.col is not None:
            self.col.df_washer, self.col.df_dryer = self.unsplit_col()
            print '\nsave:'
            print self.col
            print self.col.df_washer
            self.col_dict[self.col.id] = self.col

        self.col = col
        self.frame.col = col

        self.washer_period_dfs, self.dryer_period_dfs = self.split_col()
        self.frame.load_collection()

        # self.frame.machine_panel.period_panels[0].washer_grid.update_data(
        #     self.washer_period_dfs[0])

    def on_double_click(self, event):
        """
        Loads collection.

        :param event:
        """
        selected = event.m_itemIndex
        col = self.col_dict[self.list_control.GetItemData(selected)]

        self.load_collection(col)
        print '\nload:'
        print col
        print col.df_washer


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
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(6, 1)

        self.grid.SetColLabelSize(0)

        meters = ['gas',
                  'n-gas',
                  'S262',
                  'S263',
                  'water',
                  'lights']

        for ind, label in enumerate(meters):
            self.grid.SetRowLabelValue(ind, label)

        panel_sizer.Add(title,
                        border=5,
                        flag=wx.TOP | wx.BOTTOM | wx.LEFT)
        panel_sizer.Add(self.grid)

        self.SetSizer(panel_sizer)
        panel_sizer.Fit(self)


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
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(6, 2)

        self.grid.SetColLabelSize(0)

        changers = ['1',
                    '5',
                    '10',
                    '20',
                    'a',
                    'b',
                    'error']

        for ind, label in enumerate(changers):
            self.grid.SetRowLabelValue(ind, label)

        panel_sizer.Add(title,
                        border=5,
                        flag=wx.TOP | wx.BOTTOM | wx.LEFT)
        panel_sizer.Add(self.grid)

        self.SetSizer(panel_sizer)
        panel_sizer.Fit(self)


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
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(4, 1)

        self.grid.SetColLabelSize(0)

        labels = ['Total Weekly',
                  'Soap',
                  'Barrel',
                  'Purse']

        for ind, label in enumerate(labels):
            self.grid.SetRowLabelValue(ind, label)

        panel_sizer.Add(title,
                        border=5,
                        flag=wx.TOP | wx.BOTTOM | wx.LEFT)
        panel_sizer.Add(self.grid)

        self.SetSizer(panel_sizer)
        panel_sizer.Fit(self)


class MyDataSource(wx.grid.PyGridTableBase):
    def __init__(self, data):
        super(MyDataSource, self).__init__()

        self.data = data

    def GetNumberCols(self):
        return 2

    def GetNumberRows(self):
        return len(self.data)

    def GetValue(self, row, col):
        keys = {0: 'weights',
                1: 'amounts'}

        return self.data[keys[col]][row]

    def SetValue(self, row, col, value):
        keys = {0: 'weights',
                1: 'amounts'}

        if col == 0:
            Collection.update_row(self.data, row, value)

    def GetColLabelValue(self, col):
        cols = ['Weights (lb oz)', 'Amounts']

        return cols[col]

    def GetRowLabelValue(self, row):
        return self.data['names'][row]


class MyGrid(wx.grid.Grid):
    """
    Class for custom grid.
    """
    def __init__(self, parent, data):
        super(MyGrid, self).__init__(parent)

        self.SetTable(MyDataSource(data))
        self.AutoSizeColumns()

    def update_data(self, data):
        self.SetTable(MyDataSource(data))


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
                                  self.frame.list_panel.washer_period_dfs[
                                      period_num])
        self.dryer_grid = MyGrid(self,
                                 self.frame.list_panel.dryer_period_dfs[
                                      period_num])

        # panel sizer
        panel_sizer = wx.BoxSizer(wx.HORIZONTAL)

        panel_sizer.Add(self.washer_grid)
        panel_sizer.Add(self.dryer_grid)

        self.SetSizer(panel_sizer)
        panel_sizer.Fit(self)


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
        while (self.machine_nb.GetPageCount()):
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

        panel_sizer.Add(self.changer_panel,
                        flag=wx.EXPAND | wx.LEFT,
                        border=3)

        panel_sizer.Add(self.other_panel,
                        flag=wx.EXPAND | wx.LEFT,
                        border=3)

        self.SetSizer(panel_sizer)
        panel_sizer.Fit(self)


class MyFrame(wx.Frame):
    """
    Class for generating main frame.
    """
    def __init__(self):
        super(MyFrame, self).__init__(None, title='MVL collections')

        self.col = None

        # make calendar and list
        self.calendar_panel = CalendarPanel(self)
        self.list_panel = ListPanel(self)

        # calendar and list sizer
        calendar_list_sizer = wx.BoxSizer(wx.VERTICAL)

        calendar_list_sizer.Add(self.calendar_panel,
                        # proportion=1,
                        flag=wx.EXPAND)

        calendar_list_sizer.Add(self.list_panel,
                        proportion=1,
                        flag=wx.EXPAND)

        # make meter and notebook panel
        self.top_panel = TopPanel(self)
        self.machine_panel = MachinePanel(self)
        self.list_panel.load_collection(col1)

        # top and machine sizer
        top_machine_sizer = wx.BoxSizer(wx.VERTICAL)

        top_machine_sizer.Add(self.top_panel)
        top_machine_sizer.Add(self.machine_panel)

        # frame sizer
        frame_sizer = wx.BoxSizer(wx.HORIZONTAL)

        frame_sizer.Add(calendar_list_sizer,
                        flag=wx.EXPAND)

        frame_sizer.Add(top_machine_sizer,
                        flag=wx.EXPAND)

        self.SetSizer(frame_sizer)
        frame_sizer.Fit(self)
        self.Show()

    def load_collection(self):
        self.machine_panel.load_collection()


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

if __name__ == "__main__":
    main()