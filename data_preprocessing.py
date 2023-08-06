import pandas as pd
from io import BytesIO
import requests
import json

async def data_preprocessing(data):
    df = pd.read_excel(BytesIO(data))
    print(df.groupby('companyName').count())
    for index, row in df.iterrows():
        data_dict = row.to_dict()
        
        # Convert premiumMale and premiumFemale to int
        data_dict['premiumMale'] = int(data_dict['premiumMale'].replace(',', ''))
        data_dict['premiumFemale'] = int(data_dict['premiumFemale'].replace(',', ''))
        data_dict['premiumRenewable'] = bool(data_dict['premiumRenewable'])
        data_dict['guaranteeInsurance'] = bool(data_dict['guaranteeInsurance'])
        data_dict['actualLossCoverage'] = bool(data_dict['actualLossCoverage'])
        data_dict['fixedInterestRate'] = bool(data_dict['fixedInterestRate'])
    
        # Convert dictionary to JSON
        data_json = json.dumps(data_dict, ensure_ascii=False)
        
        # Send JSON data using requests library
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        
        # Replace NaN values with None
        data_dict = {k: v if pd.notna(v) else None for k, v in data_dict.items()}
        
        res = requests.post('http://localhost:3000/api/insurance-suggesters/create', json=data_dict, headers=headers)
        print(res)
        print(f'{index}번째 데이터 등록 완료')
    return 0