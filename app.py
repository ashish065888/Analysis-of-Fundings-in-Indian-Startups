import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from streamlit import container

st.set_page_config(layout='wide')

# Reading CSV file
df=pd.read_csv('cleaned_startup_funding.csv')

df['date']=pd.to_datetime(df['date'],dayfirst=True,errors='coerce')
# Adding a new year column
df['year']=df['date'].dt.year
# Adding a new month year column
df['month_year']=df['date'].dt.strftime('%b %Y')


def load_overall_analysis():
    st.title(':blue[Overall Analysis]')

    # Function for metrics
    def load_metrics():
        col1,col2,col3,col4 = st.columns(4)
        # metrics
        # total amount
        total_amount = '$'+ str(round((df['amount'].sum())/10**9))+" Billion"
        # maximum
        maximum = '$' + str(round((df.groupby('startup')['amount'].sum().max()) / 10**9, 2)) + " Billion"

        # Average
        avg = '$' + str(round(df['amount'].mean() / 10**6,1)) + " Million"

        # Total no. of startups
        num = df['startup'].nunique()

        with col1:
            with st.container(border = True):
                st.metric('Total', total_amount)

        with col2:
            with st.container(border=True):
                st.metric('Maximum', maximum)

        with col3:
            with st.container(border=True):
                st.metric('Average', avg)

        with col4:
            with st.container(border=True):
                st.metric('Funded Startups', num)

    def load_mom_trends():
        st.divider()
        st.header(':blue[Monthly Trends]')
        option = st.selectbox('Select on the basis of',['Funds invested','Funded startups',''])
        if option=='Funded startups':
            s1 = df.groupby('month_year')['startup'].count().reset_index()
            s1['date'] = pd.to_datetime(s1['month_year'])
            s1.sort_values('date', inplace=True)
            s1['abv_date']=s1['date'].dt.strftime("%b %y")

            with st.container(border=True):
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.plot(s1['month_year'], s1['startup'])
                ax.set_xlabel('Month')
                ax.set_xticklabels(s1['abv_date'], rotation=90)
                ax.set_ylabel('No. of Startups')
                st.pyplot(fig)
        elif option=='Funds invested':
            s2 = df.groupby('month_year')['amount'].sum().reset_index()
            s2['date'] = pd.to_datetime(s2['month_year'])
            s2.sort_values('date', inplace=True)
            s2['abv_date'] = s2['date'].dt.strftime("%b %y")

            with st.container(border=True):
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.plot(s2['month_year'], s2['amount'])
                ax.set_xlabel('Month')
                ax.set_xticklabels(s2['abv_date'], rotation=90)
                ax.set_ylabel('Amount in Million USD')
                st.pyplot(fig)

    def sector_analysis():
        st.divider()
        st.header(':blue[Top 10 Sectors by Investment]')
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                sec = df.groupby('industry')['amount'].sum().sort_values(ascending=False).head(10)
                fig, ax = plt.subplots()
                ax.pie(sec, labels=sec.index, autopct='%0.1f%%',
                           explode=[0.1] + [0 for i in range(9)], shadow=True)
                st.pyplot(fig)



    def city_analysis():
        st.divider()
        st.header(':blue[Top 10 Cities by Investment]')
        col1,col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                city = df.groupby('city')['amount'].sum().sort_values(ascending=False).head(10)
                fig, ax = plt.subplots()
                ax.pie(city, labels=city.index, autopct='%0.1f%%', shadow=True)
                st.pyplot(fig)



    def startup_and_investor_analysis():

        def startup_analysis():
            with st.container(border=True):
                year = st.slider('Select year', 2015, 2020, 2015)
                top_startup = df[df['year']==year].groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)
                fig, ax = plt.subplots()
                ax.pie(top_startup, labels=top_startup.index, autopct='%0.1f%%', shadow=True)
                st.pyplot(fig)


        def investor_analysis():
            with st.container(border=True):
                year2 = st.select_slider('Select year',[2015,2016,2017,2018,2019,2020])
                top_inv = df[df['year'] == year2].groupby('investors')['amount'].sum().sort_values(ascending=False).head(10)
                fig, ax = plt.subplots(figsize=(10,10))
                ax.pie(top_inv, labels=top_inv.index, autopct='%0.1f%%', shadow=True)
                st.pyplot(fig)

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.header(':blue[Top 10 Funded Startups]')
            startup_analysis()

        st.divider()
        st.header(':blue[Top 10 Investors]')
        investor_analysis()


    # function call for metrics
    load_metrics()

    # function call for metrics
    load_mom_trends()

    # function call for sector and location graph
    sector_analysis()
    city_analysis()

    # function call for top startup and investor
    startup_and_investor_analysis()

# Function for loading Investor Analysis
def load_investor_analysis(name):
    # Recent Investment of investor
    def recent_investment(name):
        st.header(':blue[Recent Investments]')
        recent = df[df['investors'].str.contains(name)][['date','amount','startup','industry','subvertical','city','investment_type']].head(5)
        recent.set_index('date', inplace=True)
        st.dataframe(recent)
        st.write('amount = 0 means undisclosed')

    # Biggest Investment and Investment by verticals
    def biggest_investment(name):
        st.divider()

        biggest = df[df['investors'].str.contains(name)].groupby('startup')['amount'].sum().sort_values(
            ascending=False).head(5)
        ver = df[df['investors'].str.contains(name)].groupby('industry')['amount'].sum().sort_values(ascending=False)
        # two columns created
        col1, col2 = st.columns(2)

        # checking if the dataframe is empty or not, if empty show not available
        if biggest.shape[0]==0 or (biggest.shape[0]==1 and biggest.iloc[0]==0):
            with col1:
                st.header(':blue[Biggest Investments]')
                st.info('Not available')
        else:
            with col1:
                st.header(':blue[Biggest Investments]')
                with st.container(border=True):
                    fig, ax = plt.subplots(figsize=(10,8))
                    ax.bar(biggest.index,biggest.values)
                    ax.set_xlabel('Startup')
                    ax.set_ylabel('Amount in Million USD')
                    st.pyplot(fig)

        # if ver can be plotted in second column
        if ver.shape[0] <= 5:
            with col2:
                st.header(':blue[Most Invested Verticals]')
                # checking if the dataframe is empty or not, if empty show not available
                if ver.shape[0] == 0 or (ver.shape[0] == 1 and ver.iloc[0] == 0):
                    st.info('Not available')
                else:
                    with st.container(border=True):
                        fig, ax = plt.subplots()
                        ax.pie(ver, labels=ver.index, autopct='%0.1f%%',
                               explode=[0.1] + [0 for i in range(ver.shape[0] - 1)], shadow=True)
                        st.pyplot(fig)

        else:
            st.header(':blue[Most Invested Verticals]')
            with st.container(border=True):
                fig, ax = plt.subplots()
                ax.pie(ver, labels=ver.index, autopct='%0.1f%%',
                       explode=[0.1] + [0 for i in range(ver.shape[0] - 1)], shadow=True)
                st.pyplot(fig)

    # Generally invests in
    def vertical(name):
        st.divider()
        st.header(':blue[Most Invested Verticals]')
        ver = df[df['investors'].str.contains(name)].groupby('industry')['amount'].sum().sort_values(ascending=False)
        if ver.shape[0]==0 or (ver.shape[0]==1 and ver.iloc[0]==0):
            st.info('Not available')
        else:
            with st.container(border=True):
                fig, ax=plt.subplots()
                ax.pie(ver,labels=ver.index,autopct='%0.1f%%',explode=[0.1]+[0 for i in range(ver.shape[0]-1)],shadow=True)
                st.pyplot(fig)

    # round and city wise investments
    def round_city(name):
        st.divider()
        rnd = df[df['investors'].str.contains(name)].groupby('investment_type')['amount'].sum().sort_values(ascending=False)
        city = df[df['investors'].str.contains(name)].groupby('city')['amount'].sum().sort_values(ascending=False)

        col1, col2 = st.columns(2)
        with col1:
            st.header(':blue[Funding Rounds]')
            if rnd.shape[0] == 0 or (rnd.shape[0] == 1 and rnd.iloc[0] == 0):
                st.info('Not available')
            else:
                with st.container(border=True):
                    fig, ax = plt.subplots(figsize=(10,8))
                    ax.pie(rnd, labels=rnd.index, autopct='%0.1f%%', explode=[0.1] + [0 for i in range(rnd.shape[0] - 1)],
                           shadow=True)
                    st.pyplot(fig)

        with col2:
            st.header(':blue[Investment by Cities]')
            if city.shape[0] == 0 or (city.shape[0] == 1 and city.iloc[0] == 0):
                st.info('Not available')
            else:
                with st.container(border=True):
                    fig, ax = plt.subplots(figsize=(10,8))
                    ax.pie(city, labels=city.index, autopct='%0.1f%%', explode=[0.1] + [0 for i in range(city.shape[0] - 1)],
                           shadow=True)
                    st.pyplot(fig)

    # to plot Year on year analysis
    def YOY_analysis(name):
        ydf = df[df['investors'].str.contains(name)].groupby('year')['amount'].sum()
        st.header('Year on Year Analysis')
        if ydf.shape[0]==0 or (ydf.shape[0]==1 and ydf.iloc[0]==0):
            st.info('Not available')
        elif ydf.shape[0]==1 and ydf.iloc[0]>0:
            with st.container(border=True):
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.bar(ydf.index, ydf.values)
                ax.set_xlabel('Year')
                ax.set_ylabel('Amount in Million USD')
                ax.set_xticks(ydf.index)
                st.pyplot(fig)
        else:
            with st.container(border=True):
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.plot(ydf.index, ydf.values,linewidth = 2,marker='o',markersize = 10)
                ax.set_xlabel('Year')
                ax.set_ylabel('Amount in Million USD')
                ax.set_xticks(ydf.index)
                st.pyplot(fig)
    #function call for recent investment
    recent_investment(name)

    # function call for biggest investment
    biggest_investment(name)

    #nvertical(name)

    # function call for round and city
    round_city(name)

    # function call for YOY analysis
    YOY_analysis(name)

def load_startup_analysis(name):
    startup_df = df[df['startup'].str.contains(name)]
    raised_amount = startup_df['amount'].sum()
    def details():
        col1, col2, col3, col4 = st.columns(4)
        # metrics
        # total amount raised
        total_amount = '$' + str(round((startup_df['amount'].sum()/10**6),2)) + " Million"
        # vertical
        vertical = startup_df['industry'].iloc[0]

        # No. of Rounds of Funding
        rnd_num = startup_df.groupby(['date','investment_type'])['startup'].count().sum()

        # location
        location = startup_df['city'].head(1).iloc[0]

        with col1:
            with st.container(border=True):
                st.metric('Industry', vertical)

        with col2:
            with st.container(border=True):
                st.metric('Location', location)

        with col3:
            with st.container(border=True):
                if raised_amount ==0:
                    st.metric('Total amount raised', 'Undisclosed')
                else:
                    st.metric('Total amount raised', total_amount)

        with col4:
            with st.container(border=True):
                st.metric('No. of Funding Rounds', rnd_num)

    def Funding_raised_per_year():
        st.divider()
        fund = startup_df.groupby('year')['amount'].sum()
        rnd = startup_df.groupby(['investment_type'])['amount'].sum()
        col1,col2 = st.columns(2)
        with col1:
            st.header(":blue[Funding raised per year]")
            with st.container(border=True):
                if raised_amount ==0:
                    st.info('Not Available')
                else:
                    fig, ax = plt.subplots(figsize=(10, 8))
                    ax.bar(fund.index, fund.values,color='#825B32')
                    ax.set_xlabel('Year')
                    ax.set_ylabel('Amount in Million USD')
                    ax.set_xticks(fund.index)
                    st.pyplot(fig)
        with col2:
            st.header(":blue[Funding raised per round]")
            with st.container(border=True):
                if raised_amount ==0:
                    st.info('Not Available')
                else:
                    fig, ax = plt.subplots(figsize=(10, 8))
                    ax.bar(rnd.index, rnd.values,color="#6CBEC7")
                    ax.set_xlabel('Round')
                    ax.set_ylabel('Amount in Million USD')
                    st.pyplot(fig)

    def Investor():
        st.title(':blue[Investors]')
        in_df = startup_df.groupby('investors')['amount'].sum()
        in_df = in_df.astype(str)
        in_df = '$'+in_df+' M'
        with container(border=True):
            st.dataframe(in_df)



    #def Funding_raised_per_round():
       ## st.header(":green[Funding raised per round]")
        #rnd = startup_df.groupby(['round'])['amount'].sum()
    details()
    Funding_raised_per_year()
    Investor()


# Creating the sidebar
st.sidebar.title('Startup Funding Analysis')
option = st.sidebar.selectbox('Select one',['Overall','Startup','Investor'],index=None)

if option == 'Overall':
    # btn0=st.sidebar.button('Show Overall Analysis')
    #if btn0:
    load_overall_analysis()
elif option == 'Startup':
    selected_startup = st.sidebar.selectbox('Choose Startup',sorted(df['startup'].unique()),index=None)
    st.title(':blue[{}]'.format(selected_startup))
    btn1 = st.sidebar.button('Find details')
    if btn1:
        load_startup_analysis(selected_startup)


else:
    selected_investor = st.sidebar.selectbox('Choose Investor', sorted(df['investors'].unique()),index=None)
    st.title(':blue[{}]'.format(selected_investor))
    btn2 = st.sidebar.button('Find details')
    if btn2:
        load_investor_analysis(selected_investor)

