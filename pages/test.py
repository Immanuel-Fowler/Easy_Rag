import os
Datbases = []
for entry in os.listdir('../'):
    full_path = os.path.join('../', entry)
    if os.path.isdir(full_path) and 'data_' in entry:
        Datbases.append(entry)

print(Datbases)