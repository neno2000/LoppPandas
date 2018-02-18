import pandas as pd
import pandas as pd2
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# from weasyprint import HTML

pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
options = Options()
options.add_argument("--headless")
browser = webdriver.Firefox(firefox_options=options)
# browser = webdriver.Chrome() #replace with .Firefox(), or with the browser of your choice
# browser = webdriver.PhantomJS() #replace with .Firefox(), or with the browser of your choice
url = "http://results.neptron.se/#/kristinaloppethalvan2018/?sortOrder=Place&raceId=101&categoryId=101&page=0&pageSize=25"
url2 = "http://results.neptron.se/#/kristinaloppet2017/?sortOrder=Place&raceId=102&categoryId=105&gender=F&page=0&pageSize=25"
dfAll18 = pd.DataFrame()
dfAll17 = pd2.DataFrame()
# check the first url
for x in range(0, 17):
    rString = "&page=" + str(x)
    urlz = url.replace("&page=0", rString)
    print(urlz)
    browser.get(urlz)  # navigate to the page
    browser.refresh()
    innerHTML = browser.execute_script("return document.body.innerHTML")  # returns the inner HTML as a string
    browser.refresh()
    page = BeautifulSoup(innerHTML.encode('utf-8'), 'lxml')
    table = page.find_all('table')[0]
    df = pd.read_html(str(table))

    dfAll18 = dfAll18.append(df, ignore_index=True)  # with 0s rather than NaNs

# print(dfAll18.to_json(orient='records'))

## check the second url

for x in range(0, 17):
    rString = "&page=" + str(x)
    urlz = url2.replace("&page=0", rString)
    print(urlz)
    browser.get(urlz)  # navigate to the page
    browser.refresh()
    innerHTML = browser.execute_script("return document.body.innerHTML")  # returns the inner HTML as a string
    browser.refresh()
    page = BeautifulSoup(innerHTML.encode('utf-8'), 'lxml')
    table = page.find_all('table')[0]
    df2 = pd2.read_html(str(table))

    dfAll17 = dfAll17.append(df2, ignore_index=True)  # with 0s rather than NaNs

browser.close()
# print(dfAll17.to_json(orient='records'))

dfAll17.drop_duplicates('Name')
dfAll18.drop_duplicates('Name')

columns = ['Name', 'Time']
df_filt2017 = dfAll17[(dfAll17.Status == 'Finished')]
df_filt2018 = dfAll18[(dfAll18.Status == 'Finished')]

df_new1 = pd.DataFrame(df_filt2017, columns=columns)
df_new2 = pd.DataFrame(df_filt2018, columns=columns)

df_new1.drop_duplicates(keep='first').shape
df_new2.drop_duplicates(keep='first').shape

result = pd.concat([df_new1, df_new2], axis=1, join_axes=[df_new1.Name])
df_new1['Time'] = pd.to_datetime(df_new1['Time'])
df_new1['Year'] = '2017'
df_new2['Time'] = pd.to_datetime(df_new2['Time'])
df_new2['Year'] = '2018'

df = pd.merge(df_new1, df_new2, on='Name', how='outer')
df['Result'] = df['Time_y'] - df['Time_x']
df = df.query('Result != "NaT"')
df = df.drop_duplicates(keep=False)

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template("myreport.html")
df_tab = pd.DataFrame(df, columns=['Name', 'Result'])
template_vars = {"title": "Kristina Loppet",
                 "national_pivot_table": df_tab.to_html()}

html_out = template.render(template_vars)

print()
print(df['Result'].describe())
print(html_out.encode('utf-8'))
