import csv
import re
import numbers

def remove_non_ascii(text):
    try:
        return re.sub(r'[^\x00-\x7F]+', '', text)
    except TypeError:
        return text
    

def is_number_value(my_dict, key):
    breakpoint()
    if key in my_dict:
        return isinstance(my_dict[key], numbers.Number)
    return False

def parse_effects(file_path):
    effects = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            effect = {
                'ID': remove_non_ascii(row['ID']),
                'Effect': remove_non_ascii(row['Effect']),
                'Description': remove_non_ascii(row['Description']),
                'Colors': remove_non_ascii(row['Colors']),
                'Parms': remove_non_ascii(row['Parms'])
            }
            if(not str.isdigit(effect['ID'])):  
                continue
            effects.append(effect)
    return effects

file_path = 'c:\\Projects\\dune-weaver-wled-server\\effects.txt'
effects = parse_effects(file_path)
print("effects_list = [")
for effect in effects:
    print("    {")
    print(f"        'ID': '{effect['ID']}',")
    print(f"        'Effect': '{effect['Effect']}',")
    print(f"        'Description': '{effect['Description']}',")
    print(f"        'Colors': '{effect['Colors']}',")
    print(f"        'Parms': '{effect['Parms']}'")
    print("    },")
print("]")