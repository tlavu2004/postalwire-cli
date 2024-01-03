import yaml

# Load YAML data from file
with open('./Clone/Socket/src/config.yml', encoding='utf-8') as f:
    config = yaml.safe_load(f)

email_user = config['General']['Username']
mailbox = config['General']['Mailbox']

with open(f'./Clone/Socket/src/{mailbox}/{email_user}/MailClassification.yml', 'r') as file:
    data = yaml.safe_load(file)

# Create a dictionary to store keys based on their values
keys_by_value = {}

# Iterate through the data
for key, value in data.items():
    # Check if the value is already in the dictionary
    if value in keys_by_value:
        keys_by_value[value].append(key)
    else:
        keys_by_value[value] = [key]

# Print keys with the same value
for value, keys in keys_by_value.items():
    if len(keys) >= 1:
        print(f"Keys with value '{value}': {keys}")