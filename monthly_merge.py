import os
import glob
import pandas as pd

# change it to current directory if necessary
curdir = os.getcwd()


os.chdir(curdir)

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

pd.concat(monthly_csv).sort_values(['Category','DateTime']).to_csv(f"{curdir}/0_Merged/{current_year}_{current_month}.csv",index=False)

# Move all the directories to monthly directory
import shutil

destination_directory = f'{curdir}/News/{current_year}_{current_month}'
os.mkdir(destination_directory)

for category in categories:
    source_directory = f'{curdir}/News/{category}'
    
    # Move the directory
    shutil.move(source_directory, destination_directory)
    os.mkdir(f'{curdir}/News/{category}')
