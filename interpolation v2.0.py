
"""
SABR parameters interpolation
"""
import numpy as np
import pandas as pd

def pandas_strtofloat(df):
    df.iloc[0,:] = df.iloc[0,1:].map(lambda x: str(x)[:-1]).astype(float)
    df.iloc[:,0] = df.iloc[1:,0].map(lambda x: str(x)[:-1]).astype(float)
    return df

def linear_interpolation(xsnum, xlnum, ysnum, ylnum, xobs):
    yobs = (xobs - xsnum) / (xlnum - xsnum) * (ylnum - ysnum) + ysnum
    return yobs

def linear_extrapolation(k, xobs, xnum, ynum):
    yobs = k * (xobs - xnum) + ynum
    return yobs

def quadinterpolation(df,interval):
    df = pandas_strtofloat(df)
    row_num = int((df.iloc[-1,0]-df.iloc[1,0]) /interval +1)
    col_num = int((df.iloc[0,-1]-df.iloc[0,1]) /interval +1)
    df_row = np.linspace(df.iloc[1,0],df.iloc[-1,0],row_num)
    df_col = np.linspace(df.iloc[0,1],df.iloc[0,-1],col_num)
    new_df = pd.DataFrame(index = df_row, columns = df_col)
    #interpolation
    for n in range(1, len(df.index)):
        for i in range(row_num):
            for j in range(0,len(df.columns)):
                if new_df.columns[i] == df.iloc[0,j]:
                    new_df.iloc[int(1/interval*(df.iloc[n,0]-1)),i] = df.iloc[n,j]
                elif new_df.columns[i] > df.iloc[0,j] and new_df.columns[i] < df.iloc[0,j+1]:
                    new_df.iloc[int(1/interval*(df.iloc[n,0]-1)),i] = linear_interpolation(df.iloc[0,j], df.iloc[0,j+1], df.iloc[n,j], df.iloc[n,j+1], new_df.columns[i])
    for n in range(1, len(df.columns)):
        for i in range(col_num):
            for j in range(0,len(df.index)):
                if new_df.index[i] == df.iloc[j,0]:
                    new_df.iloc[i,int(1/interval*(df.iloc[0,n]-1))] = df.iloc[j,n]
                elif new_df.index[i] > df.iloc[j,0] and new_df.index[i] < df.iloc[j+1,0]:
                    new_df.iloc[i,int(1/interval*(df.iloc[0,n]-1))] = linear_interpolation(df.iloc[j,0], df.iloc[j+1,0], df.iloc[j,n], df.iloc[j+1,n], new_df.index[i])
    for n in range(0,row_num):
        for i in range(0,col_num):
            for j in range(0,len(df.columns)-1):
                if new_df.columns[i] > df.iloc[0,j] and new_df.columns[i] < df.iloc[0,j+1]:
                    new_df.iloc[n,i] = linear_interpolation(df.iloc[0,j], df.iloc[0,j+1], new_df.iloc[n,int(1/interval*(df.iloc[0,j]-1))],new_df.iloc[n,int(1/interval*(df.iloc[0,j+1]-1))],new_df.columns[i])
    #extrapolation
    new_df_extra1 = pd.DataFrame(index = df_row, columns = np.linspace(0.25,0.75,int((0.75-0.25)/0.25+1)))
    for i in range(0, row_num):
        for j in range(0,len(new_df_extra1.columns)):
            k = (new_df.iloc[i,0] - new_df.iloc[i,1]) / (new_df.columns[0] - new_df.columns[1])
            new_df_extra1.iloc[i,j] = linear_extrapolation(k, new_df_extra1.columns[j], new_df.columns[0], new_df.iloc[i,0])
    new_df_extra2 = pd.DataFrame(index = df_row, columns = np.linspace(10.25,20,int((20-10.25)/0.25+1)))
    for i in range(0, row_num):
        for j in range(0,len(new_df_extra2.columns)):
            k = (new_df.iloc[i,-1] - new_df.iloc[i,-2]) / (new_df.columns[-1] - new_df.columns[-2])
            new_df_extra2.iloc[i,j] = linear_extrapolation(k, new_df_extra2.columns[j], new_df.columns[-1], new_df.iloc[i,-1])
    new_df = new_df_extra1.join(new_df)
    new_df = new_df.join(new_df_extra2)  

    new_df_extra3 = pd.DataFrame(index = np.linspace(0.25,0.75,int((0.75-0.25)/0.25+1)), columns = new_df.columns)
    for i in range(0, len(new_df.columns)):
        for j in range(0, len(new_df_extra3.index)):
            k = (new_df.iloc[0,i] - new_df.iloc[1,i]) / (new_df.index[0] - new_df.index[1])
            new_df_extra3.iloc[j,i] = linear_extrapolation(k, new_df_extra3.index[j], new_df.index[0], new_df.iloc[0,i])
    new_df_extra4 = pd.DataFrame(index = np.linspace(10.25,20,int((20-10.25)/0.25+1)), columns = new_df.columns)
    for i in range(0, len(new_df.columns)):
        for j in range(0, len(new_df_extra4.index)):
            k = (new_df.iloc[-1,i] - new_df.iloc[-2,i]) / (new_df.index[-1] - new_df.index[-2])
            new_df_extra4.iloc[j,i] = linear_extrapolation(k, new_df_extra4.index[j], new_df.index[-1], new_df.iloc[-1,i])
    new_df = pd.concat([new_df_extra3, new_df, new_df_extra4])
    return  new_df
    
dataset = pd.read_excel('sabrparameters.xlsx',header = None, index_col = None)
interval = 0.25
alpha = pd.DataFrame(dataset.iloc[1:5,:])
nu = pd.DataFrame(dataset.iloc[7:11,:])
rho = pd.DataFrame(dataset.iloc[13:17,:])

inter_alpha = quadinterpolation(alpha, interval)
#inter_nu = quadinterpolation(nu, interval)
#inter_rho = quadinterpolation(rho, interval)

