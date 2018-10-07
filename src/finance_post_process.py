import numpy as np
import pandas as pd

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
