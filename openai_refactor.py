from openai import OpenAI
import os
import pandas as pd
import re

print("Hello, OpenAI!")

csv_path = "results/designCodeSmells.csv"
directory = ["books-core/", "books-web/"]

client = OpenAI(
  api_key="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",
)

def get_refactored_code(client, design_smell, source_code):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a refactoring system. Do not change class name."},
            {"role": "user", "content": f'Refactor the following code to remove the {design_smell} smell: ``` java\n{source_code}\n```\n'}
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
            continue
        refactored_code_java = refactored_code_java.group(1)
        with open(file_path, 'w') as file:
            file.write(refactored_code_java)
            print(f"Refactored {file_path} with {design_smell} smell")