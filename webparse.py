import requests
from bs4 import BeautifulSoup
import csv
import ast




def price_conversion(x): # string datas to integer + replacing shortcuts
    x = x.replace("~", "")
    try:
        return int(x)
    except ValueError:
        return int(1000000 * float(x.replace("млн", "")))


def description_conversion(x): # combining resulting data for columns 'description', 'payment_range' using Tuple()
    x = x.lower()
    if "посуточно" in x:
        return (x[0:x.find("посуточно")].strip().capitalize(), "Посуточно")
    elif "помесячно" in x:
        return (x[0:x.find("помесячно")].strip().capitalize(), "Помесячно")
    elif "по часам" in x:
        return (x[0:x.find("по часам")].strip().capitalize(), "По часам")
    else:
        return (x[0:x.find("\n")].capitalize(), "Не указано")


def parser(section): # parsing whole datas
    url = 'https://krisha.kz/'
    response = requests.get(url)
    p_data = []
    if response.status_code == 200: # check for connection with website
        soup = BeautifulSoup(response.text, 'html.parser')
        offer = soup.select(section)
        offer_title = []
        parse_list_offer = []
        
        for i in offer: # slicing all unusefull data for each column
            city = []   
            p_data.append(i)
            if offer_title == []:
                offer_title.append(*[j.text for j in i.select(".title-block")])
                service_type = offer_title[0].capitalize()
            city = [j.text.strip()[0:j.text.strip().find("\n")] for j in i.select(".hot__image-header")]
            address = [j.text.strip() for j in i.select(".hot__title-address")]
            price = [j.text.strip().replace("\xa0", "")[0:j.text.strip().replace("\xa0", "").find("〒")] for j in i.select(".hot__price")]
            price = list(map(lambda x: price_conversion(x), price))
            descr = [j.text.strip() for j in i.select(".hot__title")]
            description = list(map(lambda x: description_conversion(x)[0], descr))
            payment_range = list(map(lambda x: description_conversion(x)[1], descr))

        for row in range(len(city)): # filling resulting list of data-dicts
            offer_dict = {
                "service_type": service_type, 
                "city": city[row], 
                "address": address[row], 
                "price": price[row], 
                "description": description[row], 
                "payment_range": payment_range[row]
                }
            parse_list_offer.append(offer_dict)
        return parse_list_offer
    else: 
        print("connection failed connection failed connection failed connection failed connection failed")


section_rent = ".hot-section-rent"
section_sell = ".hot-section-sell"


def values_to_csv(lst, path, mode): # use mode 'a' to not overwrite existing rows and 'w' for resetting data
    with open(path, mode=mode, encoding="utf-8") as csvfile:
        fieldnames = ["service_type", "city", "address", "price", "description", "payment_range"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(lst)
    print(f"All rows are inserted to {path} file")


def values_from_csv(path): # values from CSV (remove duplicates) or use pandas.drop_dublicates() func.
    with open(path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        data_duplicates = [str(row) for row in reader]
        data_duplicates = list(set(data_duplicates))
        return list(map(lambda x: ast.literal_eval(x), data_duplicates))


def reset_if_unique_datas_under_1000(path_unique, path_duplicates):
    with open(path_unique, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        data_unique = [row for row in reader]
        if len(data_unique) < 1000:
    
            with open(path_duplicates, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                data_duplicates = [row for row in reader]
                if len(data_duplicates) >= 1000:
                    values_to_csv(data_unique, "no_duplicates_krisha_copy.csv", "w")
                    print(f"File {path_duplicates} resetting from {len(data_duplicates)} rows with duplicates to unique data ({len(data_unique)})")
        else:
            print(f"File {path_unique} reached more than 1000 rows ({len(data_unique)}). You can change the 'if' statement to keep resetting duplicating file up to more than 1000 rows")


values_to_csv(parser(section_rent), "no_duplicates_krisha_copy.csv", "a") # values from section 'rent'
values_to_csv(parser(section_sell), "no_duplicates_krisha_copy.csv", "a") # values from section 'sell'
values_to_csv(values_from_csv("no_duplicates_krisha_copy.csv"), "no_duplicates_krisha_database.csv", "w") # removing duplicates
reset_if_unique_datas_under_1000("no_duplicates_krisha_database.csv", "no_duplicates_krisha_copy.csv") # resetting initial values for file with duplicates







                    