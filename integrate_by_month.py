from datetime import datetime, timedelta
import pandas as pd

FROM_DATE = "YYYY-MM-DD"    
TO_DATE = "YYYY-MM-DD"


def main():
    combined_by_month = pd.DataFrame()
    prev_month = 'first'

    for date in date_range(FROM_DATE, TO_DATE):
        path = 'data/' + date[2:4] + '-' + date[4:6] + '/' + date + '.csv'
        data = pd.read_csv(path, index_col=0)
        
        if ((prev_month == date[4:6]) | (prev_month == 'first')):
            combined_by_month = pd.concat([combined_by_month, data], axis='index')
        else:
            csv_name = 'data/20' + prev_year + '_' + prev_month + '.csv'
            combined_by_month.to_csv(csv_name, encoding='utf-8-sig') 
            combined_by_month = data.copy()

        prev_year = date[2:4]
        prev_month = date[4:6]

    csv_name = 'data/' + TO_DATE.split('-')[0] + '_' + TO_DATE.split('-')[1] + '.csv'
    combined_by_month.to_csv(csv_name, encoding='utf-8-sig', index=False) 


def date_range(start, end):
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    dates = [(start + timedelta(days=i)).strftime("%Y%m%d") for i in range((end-start).days+1)]
    return dates


if __name__ == '__main__':
    main()