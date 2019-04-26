import pandas as pd
from scipy.stats import chisquare
import GreeneLib as gl
import numpy as np 

## -- Load, process -- ##
wd = r"M:/Programming_Projects/Python_Projects/Analytics/18- 16 Visited Campus Stats/" 

df = pd.read_excel(wd+"Data/Export 20190426-100419-Chi.xlsx", header=0, parse_dates=["Dep_Date", "Vis_Date"]) 

print(df.info())

ddict = {
	"category":["Visited_YN"],
	"int8":["Deposited_01", "Admitted_01"],
	}

df = gl.GreeneDytpe(df, ddict)

## - Clean - ##
"""
This step will remove any records in which the visit date is 
after the deposit date	
"""
rec_dep_old = df["Deposited_01"].sum()

def compareDate(selff, dep, vis):
	"""
	This function takes a date from col1 (dep) and compares it to col2 (vis),
	and returns a value based on them
	"""
	ret = "Who knows"
	blank =  pd.Timestamp("1950-01-25")
	dep_blank = df[dep].iloc[selff] == blank
	vis_blank = df[vis].iloc[selff] == blank
	neither_blank = ~dep_blank & ~vis_blank
	if (df[dep].iloc[selff] > df[vis].iloc[selff]) & neither_blank:
		ret = "Visited Then Deposited"
	elif (df[dep].iloc[selff] < df[vis].iloc[selff]) & neither_blank:
		ret = "Deposited Then Visited"
	elif (df[dep].iloc[selff] == df[vis].iloc[selff]) & neither_blank:
		ret = "Visited and deposited at same time" 
	return ret 

cat_list = []
for i in df.index:
	cat_list.append(compareDate(i, "Dep_Date", "Vis_Date"))
ret = "Did Not Visit or Deposit"
df["VisitedTimeDesc"] = cat_list

## -- Inspect -- ##

print(df.groupby("VisitedTimeDesc").size())

print("Total deposits before dropping: {}".format(df["Deposited_01"].sum()))
print("Total visited before dropping: {}".format(len(df[df["Visited_YN"]=='Yes'])))

df = df[df["VisitedTimeDesc"] != "Deposited Then Visited"]

print("Total deposits after dropping: {}".format(df["Deposited_01"].sum()))
print("Total visited after dropping: {}".format(len(df[df["Visited_YN"]=='Yes'])))

## - Begin chi-squared testing -- ##

# - Generate OVERALL contignency table - #

vis = df.groupby("Visited_YN").size().index

dep_0 = []
dep_1 = []

for v in vis:
	temp_df = df[df["Visited_YN"] == v]
	dep_0.append(len(temp_df)-sum(temp_df["Deposited_01"]))
	dep_1.append(sum(temp_df["Deposited_01"]))
	del temp_df

c_tab_dict = {
	"Visited":vis,
	"Deposited_0":dep_0,
	"Deposited_1":dep_1,
}
c_tab = pd.DataFrame(c_tab_dict)
c_tab["Visited_Total"] = c_tab["Deposited_0"]+c_tab["Deposited_1"]


c_tab = c_tab[c_tab>5]
c_tab = c_tab.dropna(how="any", axis=0).reset_index(drop=True)
print(c_tab.to_string())


# - Begin chi-squared analysis - #

dep_obs = list(zip(c_tab["Deposited_0"], c_tab["Deposited_1"]))
## [(40204, 1531), (12790, 4681)]

"""
In 2016, there were 1888 first year freshman deposits from 7506 admits of 19972 apps 
In 2017, 1955 deposits from 8110 admits of 19740 apps, 
and finally in 2018, 2194 deposits from 8210 admits of 20156 apps. 
(1888+1955+2194)/(19972+19740+20156)   =6037/59868  = 0.10083841 
"""
e_y = 0.10083841
dep_exp = list(zip(c_tab["Visited_Total"]*(1-e_y), c_tab["Visited_Total"]*e_y))
## [(37526.508958649996, 4208.49104135), (15552.79802223, 1744.20197777)]
print(dep_exp)
from scipy.stats import chi2_contingency
from scipy.stats import chisquare
chi2, p = chisquare(dep_obs, dep_exp, axis=None)

print("OVERALL POOL")
print("Chi-squared = {}".format(chi2))
print("p = {}".format(p))

## - Begin chi-squared testing -- ##

# - Generate ADMIT contignency table - #

df_adm = df[df["Admitted_01"] == 1]
vis = df_adm.groupby("Visited_YN").size().index

dep_0 = []
dep_1 = []

for v in vis:
	temp_df = df_adm[df_adm["Visited_YN"] == v]
	dep_0.append(len(temp_df)-sum(temp_df["Deposited_01"]))
	dep_1.append(sum(temp_df["Deposited_01"]))
	del temp_df

c_tab_dict = {
	"Visited":vis,
	"Deposited_0":dep_0,
	"Deposited_1":dep_1,
}
c_tab = pd.DataFrame(c_tab_dict)
c_tab["Visited_Total"] = c_tab["Deposited_0"]+c_tab["Deposited_1"]


c_tab = c_tab[c_tab>5]
c_tab = c_tab.dropna(how="any", axis=0).reset_index(drop=True)
print(c_tab.to_string())


# - Begin chi-squared analysis - #

dep_obs = list(zip(c_tab["Deposited_0"], c_tab["Deposited_1"]))
"""
In 2016, there were 1888 first year freshman deposits from 7506 admits of 19972 apps 
In 2017, 1955 deposits from 8110 admits of 19740 apps, 
and finally in 2018, 2194 deposits from 8210 admits of 20156 apps. 
expected yield: 1888+1955+2194 / 7506+8110+8210 = 6037/23826 = 0.25337866

"""
e_y = 0.25337866
dep_exp = list(zip(c_tab["Visited_Total"]*(1-e_y), c_tab["Visited_Total"]*e_y))
## [(8842.98315096, 3001.0168490399997), (8690.6723976, 2949.3276023999997)]
print(dep_exp)
from scipy.stats import chi2_contingency
from scipy.stats import chisquare
chi2, p = chisquare(dep_obs, dep_exp, axis=None)

print("ADMIT POOL")
print("Chi-squared = {}".format(chi2))
print("p = {}".format(p))