import numpy as np
import pandas as pd
import itertools
from bokeh.io import output_notebook , show
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.models import HoverTool
from bokeh.palettes import Spectral6

def get_finance_df (start_year=2019,years_of_service=20,joining_salary=105000,tax_rate=30,
                   monthly_expense=3000,expense_rate=2,growth_rate=8,cash_retain_perc=60):
    year = np.arange(start_year,start_year + years_of_service)
    
    hike_perc = 2*np.ones(len(year))
    hike_perc[2::3] = 4
    hike_perc[0] = 0
    
    yearly_income_pre_taxed = np.zeros(len(year))
    yearly_income_pre_taxed[0] = joining_salary
    
    for x in np.arange(1,len(year)):
        yearly_income_pre_taxed[x] = yearly_income_pre_taxed[x-1]*(1 + hike_perc[x]/100)
    
    df = pd.DataFrame({'year': year , 'yearly_income_pre_taxed' : yearly_income_pre_taxed , 'hike_perc' : hike_perc})
    
    df['yearly_income_post_taxed'] = df['yearly_income_pre_taxed'] * (1 - tax_rate/100)
    
    yearly_expenditure = np.zeros(len(year))
    yearly_expenditure[0] = monthly_expense * 12
    
    for x in np.arange(1,len(year)):
        yearly_expenditure[x] = yearly_expenditure[x-1]*(1 + expense_rate/100)
        
    df['yearly_expenditure'] = yearly_expenditure
    
    df['yearly_savings'] = df['yearly_income_post_taxed'] - df['yearly_expenditure']
    
    df['cash_retained'] = df['yearly_savings'] * cash_retain_perc / 100
    
    df['cash_invested'] = df['yearly_savings'] - df['cash_retained']
    
    df['ROI'] = df['cash_invested'] * ((1 + growth_rate / 100)**years_of_service)
    
    return df.astype(int)

def plot_expense(df_expense):
    category = list(df_expense.index)
    expenses = ['budget','amount']
    data = {'category' : category,'budget' : df_expense.budget , 'amount' : df_expense.Amount}
    
    x = [ (cat, expense) for cat in category for expense in expenses ]
    counts = list(itertools.chain(*zip(data['budget'], data['amount'])))
   
    source = ColumnDataSource(data=dict(x=x, counts=counts))
    
    p = figure(x_range=FactorRange(*x), plot_height=400, plot_width=950,title="Expense Report")
    p.vbar(x='x', top='counts', width=0.9, source=source, color='red' ,line_color="white",
          fill_color=factor_cmap('x', palette=Spectral6, factors=expenses, start=1, end=2))
    p.add_tools(HoverTool(tooltips=[("CATEGORY", "@x"), ("VALUE", "@counts")]))
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None
    p.yaxis.axis_label = 'Expense ($)'
    return(p)
