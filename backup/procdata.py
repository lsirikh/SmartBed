import json

def build_data(byte_data, data_dict):
    tmp_data = byte_data.decode('utf-8').split(',')[1:]
    data = {
    "collect_time": data_dict['collect_time'],
    "duid": data_dict['duid'],
    "name": data_dict['name'],
    "sex": data_dict['sex'],
    "age": data_dict['age'],
    "height": data_dict['height'],
    "weight": data_dict['weight'],
    "accelerationx": float(tmp_data[-6]),
    "accelerationy": float(tmp_data[-5]),
    "accelerationz": float(tmp_data[-4]),
    "temperature": float(tmp_data[-3]),
    "humidity": float(tmp_data[-2]),
    "lightsensor": float(tmp_data[-1]),
    "pad_value": [int(i) for i in tmp_data[:-6]]
    }
    #return json.dumps(data)
    return data