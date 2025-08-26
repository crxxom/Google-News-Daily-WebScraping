import os
import glob
import pandas as pd

os.chdir("/Users/jadonng/Desktop/Computer_Science/Data_Scraping/Google_News")

categories = ['Business', 'Entertainment', 'Headlines', 'Health', 'Science', 'Sports', 'Technology', 'Worldwide']

monthly_csv = []

for category in categories:

    csv_files = glob.glob(os.path.join(os.getcwd()+'/News/'+category, '*.csv'))

    for file in csv_files:
        try:
            f = pd.read_csv(file)
            f['Category'] = category
            monthly_csv.append(f)
        except:
            continue


from datetime import datetime
current_year = datetime.now().year
current_month = datetime.now().month

pd.concat(monthly_csv).sort_values(['Category','DateTime']).to_csv(f"0_Merged/{current_year}_{current_month}.csv",index=False)

# Move all the directories to monthly directory
import shutil

destination_directory = f'/Users/jadonng/Desktop/Computer_Science/Data_Scraping/Google_News/News/{current_year}_{current_month}'
os.mkdir(destination_directory)

for category in categories:
    source_directory = f'/Users/jadonng/Desktop/Computer_Science/Data_Scraping/Google_News/News/{category}'
    
    # Move the directory
    shutil.move(source_directory, destination_directory)
    os.mkdir(f'/Users/jadonng/Desktop/Computer_Science/Data_Scraping/Google_News/News/{category}')
