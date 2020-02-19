import json

nums = [5, 9, 45, 4, 5]
filename = 'name.json'

with open(filename, 'w') as f:
    json.dump(nums, f)
    