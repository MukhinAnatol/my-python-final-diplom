import yaml


with open("shop1.yaml", 'r', encoding='utf-8') as stream:
    data = yaml.safe_load(stream)
    #print(data)
    try:
        shop_name = data['shop']
        print(shop_name)
        for cat in data['categories']:
            print(cat['id'])
            print(cat['name'])
        for item in data['goods']:
            print(item['id'])
            print(item['name'])
            print(item['price'])
            print(item['quantity'])
        for name, value in item['parameters'].items():
            print(name, value)

    except yaml.YAMLError as exc:
        print(exc)