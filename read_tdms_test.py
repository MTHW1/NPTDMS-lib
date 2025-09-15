import os
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from nptdms import TdmsFile


def get_param(list, keyname):
    val=([value for key, value in list if key == keyname])[0]
    return val
        

file="16-05-2025_14-09-24.tdms"
if not os.path.exists(file):
    print("Файл не найден")
    exit(1)

# read
tdms_file = TdmsFile.read(file)

print("Параметры эксперимета:")
exp_params=tdms_file.properties.items()
print(f"Имя файла: {get_param(exp_params,'name')}")
print(f"Время: {get_param(exp_params,'Start Time')}")
freq=float(get_param(exp_params,'ADC Frequency, MHz'))
print(f"Частота АЦП: {freq}")
adc_len=int(get_param(exp_params,'ADC Len, points'))
print(f"Количество отсчетов АЦП: {adc_len}")
# количество усреднений (прогонов)
nn=int(get_param(exp_params,'ADC runs conut'))
print(f"Количество усреднений в одном измерении : {nn}")
use_calibration= False if get_param(exp_params,'Gain correction used')=='False' else True
if not use_calibration:
    print(f"Амплитуда в относительных единицах")
else:
    print(f"Амплитуда в вольтах")

# количество измерений в эксперименте
exp_n= int( 1 if get_param(exp_params,'Is series')=='False' else get_param(exp_params,'Series count'))
print(f"Количество измерений: {exp_n}")
if exp_n > 1 :
    n_delta = get_param(exp_params,'Series delta t, s')
    print(f"Заданное время между измерениями: {n_delta}, сек.")
    

# массив данных акустика
raw_arr=np.zeros((exp_n, nn, 2, adc_len))
# масив данных с установки
mb_arr=np.zeros((exp_n, nn, 2, 259))

print(f"Измерения:")
# для каждого измерения
for i in range(exp_n):
# for i in range(1):
    meas_name=tdms_file.groups()[i].name
    meas_params=list(tdms_file.groups()[i].channels()[3].properties.items())

    # параметры измерения
    print(f"|- Измерение {i} ({meas_name})")    
    unix_t=get_param(meas_params,"MB0")
    meas_tm_start = datetime.fromtimestamp(unix_t).strftime('%Y-%m-%d %H:%M:%S')
    print(f"  |- Время начала измерения: {meas_tm_start}")

    # прогоны
    for j in range(nn):
    # for j in range(1):        
        
        # p
        pwawe_props=tdms_file.groups()[i].channels()[3+j].properties.items()
        mb_arr[i,j,0,:]=[value for key, value in pwawe_props ]
        pwawe_data=tdms_file.groups()[i].channels()[3+j].data[:]
        raw_arr[i,j,0,:]=pwawe_data[:]
        # s
        swawe_props=tdms_file.groups()[i].channels()[3+j+nn].properties.items()
        mb_arr[i,j,1,:]=[value for key, value in pwawe_props ]
        swawe_data=tdms_file.groups()[i].channels()[3+j+nn].data[:] 
        raw_arr[i,j,1,:]=swawe_data[:]

        print(f"  |- Усреднение {j} (Raw {j})")
        print(f"    |- P волна")
        unix_t=get_param(pwawe_props,"MB0")
        usredn_tm_start = datetime.fromtimestamp(unix_t).strftime('%Y-%m-%d %H:%M:%S')
        print(f"      |- Время записи: {usredn_tm_start}")
        print(f"      |- Датчик LVDT {get_param(pwawe_props,"MB11")}")
        print(f"      |- Осевое давление P7.1 {get_param(pwawe_props,"MB22")}")
        print(f"      |- ...")
        print(f"      |- data: {pwawe_data[:5]} ...")       
        print(f"    |- S волна")
        unix_t=get_param(swawe_props,"MB0")
        usredn_tm_start = datetime.fromtimestamp(unix_t).strftime('%Y-%m-%d %H:%M:%S')
        print(f"      |- Время записи: {usredn_tm_start}")
        print(f"      |- Датчик LVDT {get_param(swawe_props,"MB11")}")
        print(f"      |- Осевое давление P7.1 {get_param(pwawe_props,"MB22")}")
        print(f"      |- ...")
        print(f"      |- data: {swawe_data[:5]} ...")
        
    print(f"  |- ...")
print(f"|- ...")


# усредним прогоны
data=np.sum(raw_arr, axis=1)
data=data/nn
x = np.linspace(0, (1/freq)*adc_len-1, adc_len) 
# усредним данные с установки
mb1=np.sum(mb_arr, axis=1)
mb1=mb1/nn
mb=np.sum(mb1, axis=1)
mb=mb/2
mb_x=np.linspace(0, exp_n-1,exp_n) 

# show
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(10, 8))
for i in range(exp_n):
    k=0.1
    axes[0].plot(x, data[i,0,:]-i*k, color='blue',linewidth=1, label='P')
    axes[0].set_ylabel('P', color='blue')
    axes[1].plot(x, data[i,1,:]-i*k, color='red',linewidth=1, label='S')
    axes[1].set_ylabel('S', color='red')

axes[2].plot(mb_x, mb[:,11], color='blue')
axes[2].set_ylabel('P7.1', color='blue')

axes2 = axes[2].twinx()
axes2.plot(mb_x, -(mb[:,22]-mb[0,22]), color='red')
axes2.set_ylabel('LVDS', color='red')
plt.show()