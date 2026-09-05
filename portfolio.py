import numpy as np
import pandas as pd
from pathlib import Path
from yahoo_scraper import Data
import matplotlib.pyplot as plt
import yfinance as yf
from matplotlib.ticker import MaxNLocator

class Portfolio:
    def __init__(self):
        self.portfolio={}

    def construct_portfolio(self):
        self.csv=pd.read_csv('Portfolio/portfolio.csv')
        self.csv=self.csv[~self.csv.iloc[:, 0].isna().cummax()] #drops all rows starting from the first row, whos first element is a NaN

        self.companies=self.csv.columns.tolist()[1:]

        for company in self.companies:
            df=self.csv[company]
            df = df[~df.isna().cummax()]
            info=[]
            for i in range(0,df.shape[0],4):
                date=df[i]
                d, m, y = date.split('/')
                date = f"{y}-{m}-{d}"

                shares=df[i+1]
                amount=df[i+2]
                currency=df[i+3]
                info.append((date, shares, amount, currency))


            self.portfolio[company]=info

    def load_data(self):
        self.info=Data(companies=self.companies, start="2026-08-11", end=None)
        self.info.companies=self.companies
        self.info.load_companies()
        self.info.construct_data()

        for i in self.companies:
            company_info=self.portfolio[i]

            for j in company_info:
                date=j[0]
                closing_price=float(j[2])/float(j[1])

                self.info.results[i].at[date, 'Close']=closing_price

            self.info.results[i]['Daily Return']=self.info.results[i]['Close'].pct_change()


        self.days=self.info.results['NVDA'].shape[0]
    #
    # def construct_tracker(self):
    #     self.tracker={}
    #
    #     for company in self.companies:
    #         self.tracker[company]=pd.DataFrame()
    #
    #         dates_addedfunds=[]
    #         amount_addedfunds=[]
    #
    #         if len(self.portfolio[company])>0:
    #             for i in range(1, len(self.portfolio[company])):
    #                 dates_addedfunds.append(self.portfolio[company][i][0])
    #                 amount_addedfunds.append(self.portfolio[company][i][2])
    #
    #
    #         start_date=self.portfolio[company][0][0]
    #         start_amount=float(self.portfolio[company][0][2])
    #
    #         current_value=start_amount
    #         current_day=0
    #
    #         while current_day<self.days:
    #             current_day=current_day+1
    #             start_date_location=self.info.results[company].index.get_loc(start_date)
    #             current_date_location=start_date_location+current_day
    #             current_date=self.info.results[company].index[current_date_location]
    #
    #             if current_date==self.info.results[company].index[-1]:
    #                 break
    #
    #             growth_from_previous_day=self.info.results[company]['Daily Return'].iloc[current_date_location]
    #             current_value=current_value*(1+growth_from_previous_day)
    #
    #             for index, date_addedfunds in enumerate(dates_addedfunds):
    #                 if current_date==date_addedfunds:
    #
    #                     current_value=current_value+amount_addedfunds[index]
    #
    #             self.tracker[company][current_date]=current_value

    def construct_tracker(self):
        self.tracker = {}

        for company in self.companies:
            # 1. Start with a clean copy of the market data
            df = self.info.results[company].copy()

            # 2. Create columns to track your transactions
            df['Shares Bought'] = 0.0
            df['Cash Invested'] = 0.0

            # 3. Map your purchases directly onto the dates
            company_info = self.portfolio[company]
            for j in company_info:
                date = j[0]
                shares = float(j[1])
                amount = float(j[2])

                # Make sure the date exists in the index to avoid KeyError
                if date in df.index:
                    df.at[date, 'Shares Bought'] += shares
                    df.at[date, 'Cash Invested'] += amount

            # 4. Calculate cumulative shares owned and total cash invested over time
            df['Total Shares Owned'] = df['Shares Bought'].cumsum()
            df['Total Principal'] = df['Cash Invested'].cumsum()

            # 5. The true portfolio value is simply your total shares * the actual close price
            df['Portfolio Value'] = df['Total Shares Owned'] * df['Close']


            start_date = company_info[0][0]
            df = df.loc[start_date:]


            self.tracker[company] = df[['Total Shares Owned', 'Total Principal', 'Portfolio Value']]

    def finalise_tracker(self):

        forex_data = yf.download('USDEUR=X', start=self.info.start, end=self.info.end, interval='1d')


        usdeur_rates = forex_data['Close'].squeeze()

        all_values = {}
        all_principals = {}

        for company in self.companies:
            if company in self.tracker:
                currency = self.portfolio[company][0][3].strip().upper()

                daily_values = self.tracker[company]['Portfolio Value']
                daily_principals = self.tracker[company]['Total Principal']


                if currency == 'USD':
                    aligned_rates = usdeur_rates.reindex(daily_values.index).ffill().bfill()

                    daily_values = daily_values * aligned_rates
                    daily_principals = daily_principals * aligned_rates

                all_values[company] = daily_values
                all_principals[company] = daily_principals

        df_values = pd.DataFrame(all_values).ffill().fillna(0)
        df_principals = pd.DataFrame(all_principals).ffill().fillna(0)


        self.total_portfolio = pd.DataFrame(index=df_values.index)
        self.total_portfolio['Total Portfolio Value'] = df_values.sum(axis=1)
        self.total_portfolio['Total Principal Invested'] = df_principals.sum(axis=1)

    def plotting_tracker(self):
        portfolio_values = self.total_portfolio['Total Portfolio Value'].values
        principal_values = self.total_portfolio['Total Principal Invested'].values
        days = range(len(portfolio_values))


        plt.figure(figsize=(10, 6))
        plt.plot(days, portfolio_values, label='Portfolio Value', color='#1f77b4', linewidth=2)

        change=(-principal_values[-1]/portfolio_values[-1] +1)*100
        plt.title(f"Current Portfolio Value {portfolio_values[-1]:.2f} EUR ({change:.2f}%)")
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.xlabel('Days Since First Investment')
        plt.ylabel('Value')
        plt.grid(True, linestyle='--', alpha=0.7)



        plt.plot(days, principal_values, label='Total Invested', color='gray', linestyle='--')
        plt.legend()

        path=r'C:\Users\panis\PycharmProjects\Growth_calculator\Portfolio'
        path=Path(path)
        filename='fig.png'
        path=path/filename
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.show()

