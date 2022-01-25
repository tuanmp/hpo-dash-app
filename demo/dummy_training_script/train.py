import json
import sys
import math

def accuracy(x, y):
    return math.sqrt(x**2+y**2)

def main():
    input_file=sys.argv[1]

    with open(input_file, 'r') as f:
        search_point = json.loads(f.read())
    
    x = search_point.get('x', 0)
    y = search_point.get('y', 0)
    
    output = {'accuracy': accuracy(x,y)}

    with open('output.json', 'w') as f:
        json.dump(output, f, indent=4)
    
    return 0

if __name__ == '__main__':
    main()