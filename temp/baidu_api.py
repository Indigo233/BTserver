from aip import AipNlp
import json
APP_ID = '10629064'
API_KEY = 'wtHkAYvPEHVWlfyUDfp4Nzco'
SECRET_KEY = 'CN0FRSM2CjksFeBFOoBoV4GC4VSB5wRE'

client = AipNlp(APP_ID, API_KEY, SECRET_KEY)

f = open('TCM.csv')
lines = f.readlines()
values = {}
for line in lines:
    raw = line.split(',')
    for r in raw:
        r = r.strip()
        values[r] = 1
values = list(values.keys())
values = sorted(values)
values = [v for v in values if len(v) >= 1]
#values = values[:20]
total = len(values) * (len(values) - 1) / 2

result = {}
f = open("baidu_api", 'r')
for line in f.readlines():
    r = json.loads(line)
    #print(r.keys()[0])
    result.update(r)
print("load old result:", len(result))
f.close()

print(result)
f = open("baidu_api", 'a')
num_values = len(values)
for i in range(num_values):
    text1 = values[i]
    
    
    for j in range(i + 1, num_values):
        text2 = values[j]
        
	        
        key = text1 + "#" + text2
        print(key)
        key = key.decode("utf-8")
        if key in result:
            print("skip")
            continue
            
	try:            
        	resp = client.simnet(text1, text2)       
        	score = resp['score']
        	f.write(json.dumps({key:score} ) + '\n')
        	result[key] = score
        	print(len(result), total)
        except:
		pass
print(result)
f.close()
