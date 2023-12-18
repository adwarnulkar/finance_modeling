import streamlit as st

script_path = __file__
st.text(f"This script was run from {script_path}")

"""
# This is markdown
"""

import pandas as pd
import numpy as np
import os
import glob
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


# Functions
def model_mortgage_payment(LOAN_AMOUNT,RATE_OF_INTEREST,MONTHLY_PAYMENT,TAX_AND_INSURANCE,YEARLY_INJECTION=20000):
  
  P_list = [0]
  I_list = [0]
  B_list = [0]

  i = RATE_OF_INTEREST / (12*100)

  count = 0

  while sum(P_list) < LOAN_AMOUNT:
    
    x = MONTHLY_PAYMENT - TAX_AND_INSURANCE

    REMAINING_BALANCE = LOAN_AMOUNT - sum(P_list)

    I = i*(REMAINING_BALANCE)
    P = x - I
    I_list.append(I)

    if(count%12 == 0 and count!= 0):
      P_list.append(P+YEARLY_INJECTION)
      B_list.append(REMAINING_BALANCE - x - YEARLY_INJECTION)
    else:
      P_list.append(P)
      B_list.append(REMAINING_BALANCE - x)

    count = count + 1

  df_model = pd.DataFrame({
    "Principal_payment" : P_list,
    "Interest_payment" : I_list,
    "Remaining_balance" : B_list,
  })
  
  df_model = df_model.iloc[1:]
  return df_model


payment_history_database = os.path.join(os.path.dirname(script_path),"../database/payment_history/")

payment_history_xlsx = st.selectbox(
    'Select payment history ?',
    os.listdir(payment_history_database))

payment_history_xlsx = os.path.join(payment_history_database,payment_history_xlsx)
st.write('You selected:', payment_history_xlsx)
st.write(f"Payment xlsx exists ? {os.path.exists(payment_history_xlsx)}")

RATE_OF_INTEREST = st.number_input("Mortage Interest Rate : ", value=2.75)
TAX_AND_INSURANCE = st.number_input("Tax and insurance (per month) : " , value=708)
SKIP_ROWS = 11
MONTHLY_PAYMENT = st.number_input("Monthly payment towards mortgage (in $) : ",value = 5500)
YEARLY_INJECTION = st.number_input("Yearly injection from Bonus/RSU rewards (in $) : ",value=20000)

# Read payment history
df_history = pd.read_excel(payment_history_xlsx,skiprows=SKIP_ROWS)

# Compute remaining loan balance
remaining_balance = df_history["REMAINING BALANCE"][0]
st.write(f"Remaining Loan Balance : **${remaining_balance}**")

cols = ["PRINCIPAL","INTEREST","ESCROW"]
st.table(df_history[cols].sum())

fig = px.pie(values=df_history[cols].sum(), names=cols)
fig.update_layout(
  title_text = "Distribution of payment",
  height = 600
)
st.plotly_chart(fig)

# Show history of remaining balance
date_list = []
balance_list = []
for date , row in df_history.groupby("DATE"):
  date_list.append(date)
  balance_list.append(row["REMAINING BALANCE"].min())

df_balance = pd.DataFrame({"DATE":date_list,"REMAINING BALANCE":balance_list})
df_balance["DATE"] = pd.to_datetime(df_balance["DATE"])
df_balance = df_balance.sort_values(by="DATE")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_balance["DATE"], y=df_balance["REMAINING BALANCE"]))
fig.update_layout(
  title_text = "History of remaining balance",
  xaxis_title = "<b>Date<b>",
  yaxis_title = "<b>Balance remaining ($)<b>",
  height = 600
)
st.plotly_chart(fig)

# Obtain Amortization Schedule
df_model = model_mortgage_payment(LOAN_AMOUNT=remaining_balance,
                                  RATE_OF_INTEREST=RATE_OF_INTEREST,
                                  MONTHLY_PAYMENT=MONTHLY_PAYMENT,
                                  TAX_AND_INSURANCE=TAX_AND_INSURANCE,
                                  YEARLY_INJECTION=YEARLY_INJECTION
                                  )

#t = np.arange(datetime(1985,7,1), datetime(2015,7,1), timedelta(days=30)).astype(datetime)
#st.write(df_model)
years_remaining = df_model.shape[0]/12
st.write(f"Years remaining from now to pay off the mortgage : {years_remaining:0.2f} years !!")

last_date = df_balance.DATE.iloc[-1]
st.write(last_date)

old_date = last_date + relativedelta(months=1)
new_date_list = []
for i in range(0,df_model.shape[0]):
  new_date = old_date + relativedelta(months=1)
  new_date_list.append(new_date)
  old_date = new_date

st.write(new_date)
df_estimate = pd.DataFrame({
                          "REMAINING BALANCE" : df_model.Remaining_balance,
                          "DATE" : new_date_list
                          })
st.write(df_estimate)

df_payoff = pd.concat([df_balance,df_estimate]).reset_index(drop=True)
st.write(df_payoff)


fig = go.Figure()
fig.add_trace(go.Scatter(x=df_balance["DATE"], y=df_balance["REMAINING BALANCE"],name="History"))
fig.add_trace(go.Scatter(x=df_estimate["DATE"], y=df_estimate["REMAINING BALANCE"],name="Model"))
fig.update_layout(
  title_text = "Pay off model",
  xaxis_title = "<b>Date<b>",
  yaxis_title = "<b>Balance remaining ($)<b>",
  height = 600,
  width = 1000
)
st.plotly_chart(fig)
