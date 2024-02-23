from openai import OpenAI
import os
import pandas as pd
import re

limit_count = 2

print("Hello, OpenAI!")

csv_path = "results/designCodeSmells.csv"
directory = ["books-core/", "books-web/"]

def encode_string(string, shift):
    encoded_string = ""
    for char in string:
        if char.isalpha():
            ascii_offset = ord('a') if char.islower() else ord('A')
            encoded_char = chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
            encoded_string += encoded_char
        elif char.isdigit():
            encoded_char = str((int(char) + shift) % 10)
            encoded_string += encoded_char
        elif char.isspace():
            encoded_char = ' '
            encoded_string += encoded_char
        else:
            encoded_char = char
            encoded_string += encoded_char
    return encoded_string

def decode_string(string, shift):
    return encode_string(string, -shift)

api_key = "vn-CtUwpK4kqt059WwamietW6EoenIMt6owyH1i5Hh5IcFCjRgb"

client = OpenAI(
  api_key=decode_string(api_key, 3),
)

def get_refactored_code(client, design_smell, source_code):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a refactoring system. Do not change class name. Do not refactor unless needed."},
            {"role": "user", "content": f'If the following code contains the {design_smell} design smell, refactor it to remove this design smell. If there is no design smell, return nothing: ``` java\n{source_code}\n```\n'}
        ],
        temperature=0,
    )
    refactored_code = response.choices[0].message.content
    return refactored_code

def find_file(directory, file_name):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == file_name:
                return os.path.join(root, file)
    return None

df = pd.read_csv(csv_path)

pr_title = ""
pr_description = "| File Name | Design Smell |\n|------------|-----------|\n"

count = 0

for index, row in df.iterrows():
    design_smell = row['Code Smell']
    file_name = row['Type Name']
    file_name += ".java"
    file_path = None
    for directory1 in directory:
        file_path = find_file(directory1, file_name)
        if file_path:
            break
    if file_path:
        with open(file_path, 'r') as file:
            source_code = file.read()
        refactored_code = get_refactored_code(client, design_smell, source_code)
        refactored_code_java = re.search(r'```java\n(.*?)\n```', refactored_code, re.DOTALL)
        if refactored_code_java is None:
            print("No refactoring needed")
        refactored_code_java = refactored_code_java.group(1)
        with open(file_path, 'w') as file:
            file.write(refactored_code_java)
            print(f"Refactored {file_path} with {design_smell} smell")
            count += 1
            pr_description += f"| {file_name} | {design_smell} |\n"
    if(count >= limit_count):
        break

pr_title = f"Refactored {count} smells"
pr_description += "\n"

with open('pr_title.txt', 'w') as file:
    file.write(pr_title)

with open('pr_body.txt', 'w') as file:
    file.write(pr_description)

print(pr_description)