import json
import sys

points = json.load(open(sys.argv[1]))
import matplotlib.pyplot as plt

x = [int(-val[0]) for val in points]                 
y = [float(val[1]) for val in points]               
plt.plot(x, y, 'o-')
plt.xlabel('Количество дней до отправления')
plt.ylabel('Стоимость билета')
plt.title(sys.argv[2] if len(sys.argv) > 2 else '')
plt.xticks(x, [int(-val) for val in x])
plt.show()

