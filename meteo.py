#functions ###########################################################

def url_open(url, ua='', charset=''):
  '''
  Manage file requests
  '''
  retval=''
  try:
    headers={}
    headers['User-Agent']=ua
    req=urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
      if charset=='':
        charset=response.headers.get_content_charset()
      retval=response.read().decode(charset)
  except urllib.error.HTTPError as e:
    print('HTTP error:', e.code)
  except urllib.error.URLError as e:
    print('Server connection failed', e.reason)
  else:
    print('File accessed successfully')
  finally:
    return retval
  
def month_skip(year, month):
  '''
  Calculate next month
  '''
  if month<12:
    month+=1
  else:
    year+=1;
    month=1;
  return year, month

def month_days(year, month):
  '''
  Calculate the days of a month
  '''
  if month in (1,3,5,7,8,10,12):
    return 31
  elif month in (4,6,9,11):
    return 30
  elif month==2:
    if year%4==0 and (year%100!=0 or year%400==0):
      return 29
    else:
      return 28
  return False

def month_name(month):
  '''
  Return the name of a month 
  '''
  return ('Ιαν','Φεβ','Μαρ','Απρ','Μαι','Ιουν','Ιουλ','Αυγ','Σεπ','Οκτ','Νοε','Δεκ')[month-1]

def time24(passval):
  '''
  Format 24-hour time 
  '''
  hour=re.findall(r'\d*:', passval)[0][:-1]
  min=re.findall(r':\d*', passval)[0][1:]
  if len(re.findall(r'p', passval))>0:
    hour=str(int(hour)+12)
  return hour.zfill(2)+':'+min.zfill(2)


#program #############################################################


#basic configuration

import os.path
import re
import urllib.request
import urllib.error
import socket 
timeout=10 #χρόνος αναμονής σε δευτερόλεπτα
socket.setdefaulttimeout(timeout)


#url configuration

conf={}
conf['url_user_agent']="Mozilla/5.0 (Windows NT 6.1; rv:62.0) Gecko/20100101 Firefox/62.0"
with open('meteo.txt','r',encoding='utf-8') as fi:
  for li in fi:
    print(li.strip())
    _=li.strip().split(' ')
    conf[_[0][:-1]]=_[1]


#request and save files

month=int(conf['url_month_from'])
year=int(conf['url_year_from'])
while True:
  dir_name='./'+conf['url_place']
  file_name=str(year)+'_'+str(month).zfill(2)+'.txt'
  print('Search', dir_name+'/'+file_name)
  if os.path.isfile(dir_name+'/'+file_name):
    print('File found locally')
  else:
    url=conf['url_base']+'/'+conf['url_place']+'/'+str(year)+'-'+str(month).zfill(2)+'.txt'
    print('Request '+url)
    data=url_open(url, conf['url_user_agent'], conf['url_charset'])
    if data!='':
      if not os.path.isdir(dir_name):
        os.mkdir(dir_name);
      with open(dir_name+'/'+file_name, "w", encoding='utf-8') as fi:
        fi.write(data)
    
  if month==int(int(conf['url_month_till'])) and year==int(int(conf['url_year_till'])):
    break
  year, month=month_skip(year, month)


#read files
  
data=[]
month=int(conf['url_month_from'])
year=int(conf['url_year_from'])
while True:
  dir_name='./'+conf['url_place']
  file_name=str(year)+'_'+str(month).zfill(2)+'.txt'
  if os.path.isfile(dir_name+'/'+file_name):
    print('Read '+dir_name+'/'+file_name)
    with open(dir_name+'/'+file_name,'r',encoding='utf-8') as fi:

      #initialize data array for each year
      if len(data)<year-int(conf['url_year_from'])+1:
        data.append([])
        for m in range(12):
          data[len(data)-1].append([])
          for d in range(month_days(year, m+1)):
            data[len(data)-1][m].append([])
            
      #pick out data
      is_data=False
      for li in fi:
        if li[0:3]=='---':
          is_data=not is_data
        elif is_data:
          _=re.findall(r'-?\d+.?:?\S*', li.strip())
          if len(_)>=6:
            data[len(data)-1][month-1][int(_[0])-1].append(float(_[1]))
            data[len(data)-1][month-1][int(_[0])-1].append(float(_[2]))
            data[len(data)-1][month-1][int(_[0])-1].append(time24(_[3]))
            data[len(data)-1][month-1][int(_[0])-1].append(float(_[4]))
            data[len(data)-1][month-1][int(_[0])-1].append(time24(_[5]))

  if month==int(int(conf['url_month_till'])) and year==int(int(conf['url_year_till'])):
    break
  year, month=month_skip(year, month)


#process data

print('Process data')
lowest=['']*12*3
low=[0]*12*3
low_time=[[]]*12*3
mean=[0]*12*3
high=[0]*12*3
high_time=[[]]*12*3
highest=['']*12*3
days=[0]*12*3
for m in range(12):
  for m10 in range(3):
    _low_time=[]
    _high_time=[]
    for y in range(len(data)):
      if len(data[y][m][0])>0:
        month_range=range(10*m10, 10*(m10+1))
        if m10==2:
          month_range=range(10*m10, len(data[y][m]))
        for d in month_range:
          if lowest[m*3+m10]=='' or lowest[m*3+m10]>data[y][m][d][3]:
            lowest[m*3+m10]=data[y][m][d][3]
          low[m*3+m10]+=data[y][m][d][3]
          _low_time.append(data[y][m][d][4])
          mean[m*3+m10]+=data[y][m][d][0]
          high[m*3+m10]+=data[y][m][d][1]
          _high_time.append(data[y][m][d][2])
          if highest[m*3+m10]=='' or highest[m*3+m10]<data[y][m][d][1]:
            highest[m*3+m10]=data[y][m][d][1]
          days[m*3+m10]+=1
    if len(_low_time)>0:
      _low_time.sort()
      _high_time.sort()
      low_time[m*3+m10]=[_low_time[len(_low_time)//3], _low_time[len(_low_time)//-3]]
      high_time[m*3+m10]=[_high_time[len(_high_time)//3], _high_time[len(_high_time)//-3]]


#print results

print('------- ------- ------------------ ----------------- ------------------ -------')
print('{:^80}'.format('ΔΙΑΚΥΜΑΝΣΗ ΘΕΡΜΟΚΡΑΣΙΩΝ ΕΤΟΥΣ (ΑΝΑ 10ΗΜΕΡΟ)'))
print('')
print('{:^80}'.format('Τοποθεσία: '+conf['url_place']+', Εξέταση δεδομένων (από-έως): '+conf['url_month_from']+'/'+conf['url_year_from']+'-'+conf['url_month_till']+'/'+conf['url_year_till']))
print('------- ------- ------------------ ----------------- ------------------ -------')
print('        Ελάχιστ       Χαμηλές        Μέσες θερμοκρ         Υψηλές       Μέγιστη')
print('------- ------- ------------------ ----------------- ------------------ -------')
for m in range(12):
  for m10 in range(3):
    if days[m*3+m10]>0:
      prev_item=m*3+m10-1
      if prev_item<0:
        prev_item=len(days)-1
      if days[prev_item]==0:
        prev_item=m*3+m10
      print('{0:4s}({1})  {2:4.1f}  {3:5.1f} ({4}-{5})   {6:5.1f} ({7:+4.1f})   {8:5.1f} ({9}-{10})  {11:4.1f}'.format(
        month_name(m+1),
        m10+1,
        lowest[m*3+m10],
        low[m*3+m10]/days[m*3+m10],
        low_time[m*3+m10][0],
        low_time[m*3+m10][1],
        mean[m*3+m10]/days[m*3+m10],
        mean[m*3+m10]/days[m*3+m10]-mean[prev_item]/days[prev_item],
        high[m*3+m10]/days[m*3+m10],
        high_time[m*3+m10][0],
        high_time[m*3+m10][1],
        highest[m*3+m10]))
print('------- ------- ------------------ ----------------- ------------------ -------')
