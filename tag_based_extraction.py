import pandas as pd

import re
# sys.path.append('tagging_logic')
from tagging import bioes_tagging, company_names_extended  

def invert_dictionary(dictionary):
    inverted_dict = {}
    for key, values in dictionary.items():
        for value in values:
            inverted_dict[value] = key
    return inverted_dict

def extract_info_from_tags(question):
    inverted_company_names = invert_dictionary(company_names_extended)
    tags = bioes_tagging(question)
    words = question.split()
    info_dict = {}
    #완
    # Extract age
    age_tags = [i for i, tag in enumerate(tags) if tag == 'S-Age']
    if age_tags:
        age_word = words[age_tags[0]]
        age = re.findall(r'\d+', age_word)[0]
        info_dict['Age'] = int(age)

    #완
    # Extract gender
    gender_map = {
        'male': 'man',
        'man': 'man',
        "men's": 'man',
        'his': 'man',
        "men": 'man',
        'female': 'female',
        'woman': 'female',
        'women': 'female',
        'her': 'female'
    }
    gender_tags = [words[i] for i, tag in enumerate(tags) if tag == "E-Gender"]
    if gender_tags:
        info_dict['Gender'] = gender_map[gender_tags[0]]

    #완
    insurance_price_tags = [i for i, tag in enumerate(tags) if tag == "E-insurancePrice"]
    if insurance_price_tags:
        price_word = words[insurance_price_tags[0]]
        price = re.findall(r'\d+', price_word.replace(',', ''))[0]
        info_dict['Insurance Price'] = int(price)


    range_map = {
            "more cheap": 'less',
            "or less": 'less',
            "or over": 'over',
            "over": 'over',
            "less": 'less',
            "around": 'around',
            "below": 'less',
            "under": 'less',
            "up": 'over',
            "less than": 'less',
    }
    
    #이상 이하 범위 리턴 완
    insurance_price_range_tags = [(i, words[i]) for i, tag in enumerate(tags) if tag == "E-insurancePriceRange"]
    insurance_price_range_list = []    
    for insurance_price_range, range_word in insurance_price_range_tags:
        range_list = [range_map[range_word]]
        window_size = 4
        start_idx = max(0, insurance_price_range - window_size)
        end_idx = min(len(tags), insurance_price_range + window_size + 1)

        # Extract values from context
        for idx in range(start_idx, end_idx):
            if tags[idx] == 'S-Age':
                range_list.append('age')
                break
            elif tags[idx] == 'E-insurancePrice':
                range_list.append('price')
                break
            elif tags[idx] == 'E-priceIndex':
                range_list.append('priceIndex')
                break
        
        insurance_price_range_list.append(range_list)
        
    if insurance_price_range_list:
        info_dict['Insurance Price Range Index'] = insurance_price_range_list

    minmax_map = {
       "most expensive": "max",
            "very expensive": "min",
            "most affordable": "max",
            "cheapest": "min",
            "mid-range": "mid",
            "luxurious":"max",
            "economical":"mid",
    }
     
    # 최대 최소 필터링 로직
    insurance_price_minmax_range_tags = [(i, words[i]) for i, tag in enumerate(tags) if tag == "E-minmaxInsurancePriceRange"]
    insurance_price_minmax_range_list = []    
    for insurance_price_minmax, range_word in insurance_price_minmax_range_tags:
        range_list = [minmax_map[range_word.replace(",", "")]]
        window_size = 4
        start_idx = max(0, insurance_price_minmax - window_size)
        end_idx = min(len(tags), insurance_price_minmax + window_size + 1)

        # Extract values from context
        for idx in range(start_idx, end_idx):
            if tags[idx] == 'S-Age':
                range_list.append('age')
                break
            elif tags[idx] == 'E-insurancePrice':
                range_list.append('price')
                break
            elif tags[idx] == 'E-priceIndex':
                range_list.append('priceIndex')
                break
        
        insurance_price_minmax_range_list.append(range_list)
        
    if insurance_price_minmax_range_list:
        info_dict['Insurance Price MinMax Index'] = insurance_price_minmax_range_list


    # 보험 타입 (유병력자, 무병력자) 완
    insurance_type_map = {
        "medical-free":"ActualCost",
        "no medical history":"ActualCost",
        "disease-free":"ActualCost",
        "healthcare-free":"ActualCost",
        "sick person":"PreExistingConditionActualCost",
        "higher risk of getting sick" : "PreExistingConditionActualCost",        
        "health problems": "PreExistingConditionActualCost",
        "past illnesses": "PreExistingConditionActualCost",
        "previous medical conditions.": "PreExistingConditionActualCost",
        "history of diseases": "PreExistingConditionActualCost",
        "history of health issues": "PreExistingConditionActualCost",
        "previous illnesses": "PreExistingConditionActualCost",
        "history of health problems": "PreExistingConditionActualCost",
        "history of past diseases": "PreExistingConditionActualCost",
        "health issues in the past": "PreExistingConditionActualCost",
        "suffered from diseases": "PreExistingConditionActualCost",
    }
    insurance_type_tags = [words[i] for i, tag in enumerate(tags) if tag in ["E-insuranceType", "B-insuranceType"]]
    if insurance_type_tags:
        info_dict['Insurance Type'] = insurance_type_map[' '.join(insurance_type_tags)]
        
    # # Extract company name 완
    company_name_tags = []
    i = 0  # 인덱스 변수 초기화
    while i < len(tags):
        tag = tags[i]
        
        if tag == "I-companyName":
            start_idx = i
            company_name = " ".join(words[start_idx:start_idx+2]).replace(",", "")
            company_name_tags.append(company_name)
            for _ in range(2):
                tags.pop(start_idx)
                words.pop(start_idx)
        elif tag == "B-companyName":
            start_idx = i
            company_name_tags.append(words[start_idx].replace(",", ""))
            tags.pop(start_idx)
            words.pop(start_idx)
        elif tag == "E-companyName":
            company_name_tags.append(words[i].replace(",", ""))
            tags.pop(i)
            words.pop(i)
        else:
            i += 1  # 다음 인덱스로 이동

    
    if company_name_tags:
        companys = []
        for i in company_name_tags:
            companys.append(inverted_company_names.get(i, []))
    companys = [item for item in companys if item]
    info_dict['Company Name'] = companys


    # Extract price index 완
    price_index_tags = [i for i, tag in enumerate(tags) if tag in ["B-priceIndex", "E-priceIndex"]]
    if price_index_tags:
        index_word = " ".join([words[i] for i in price_index_tags])
        info_dict['Price Index'] = index_word

    # Extract cancellation refund 
    cancellation_refund_tags = [words[i] for i, tag in enumerate(tags) if tag == "E-cancellationRefund"]
    if cancellation_refund_tags:
        info_dict['Cancellation Refund'] = cancellation_refund_tags[0]


    registration_type_map = {
            "consultation-free":"online",
            "consultation free":"online",
            "online-registration":"online",
            "in-person visit":"visit",
            "mail-in application":"mail",
            "Agent-assisted":"agent",
            "Agent assisted":"agent",
            "agent assisted":"agent",
            "Phone Enrollment":"agent",
            "phone enrollment":"agent",
            "agent":"agent",
    }
    # Extract registration type 
    registration_type_tags = [words[i] for i, tag in enumerate(tags) if tag == "E-registrationType"]
    if registration_type_tags:
        info_dict['Registration Type'] = registration_type_map[' '.join(registration_type_tags)]

    
    return info_dict
