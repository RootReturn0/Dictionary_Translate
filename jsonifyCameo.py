# Save the explanation of Cameo code from txt to json
import json
import os

ORIGIN_FILE_PATH = './doc/CameoCode.txt'
TARGET_FILE_PATH = './doc/CameoCode.json'

jsonData = []

def extract():
    global jsonData
    with open(ORIGIN_FILE_PATH, 'r') as f:
        # print(f.readlines())
        while(True):
            line=''
            cameo = ''
            name = ''
            description = []
            usage_notes = []
            example = []
            c=0
            while(True):
                c+=1
                line = f.readline()
                if line.startswith(' CAMEO'):
                    cameo=line.split()[-1]
                elif line.startswith(' Name'):
                    # print(' '.join(line.split()[1:]))
                    name = ' '.join(line.split()[1:])
                elif line.startswith(' Description'):
                    description.append(' '.join(line.split()[1:]))
                    while(True):
                        line = f.readline()
                        if line.startswith(' Usage Notes') or line.startswith(' Example') or line=='\n':
                            break
                        description.append(' '.join(line.split()))
                if line.startswith(' Usage Notes'):
                    usage_notes.append(' '.join(line.split()[1:]))
                    while(True):
                        line = f.readline()
                        if line.startswith(' Example') or line=='\n':
                            break
                        usage_notes.append(' '.join(line.split()))
                if line.startswith(' Example'):
                    example.append(' '.join(line.split()[1:]))
                    while(True):
                        line = f.readline()
                        if line=='\n' or ('VERB CODEBOOK' in line):
                            break
                        example.append(' '.join(line.split()))
                if line == '\n' or line =='':
                    break
            if cameo:
                jsonData.append({
                    'cameo': cameo,
                    'name': name,
                    'description': description,
                    'usage_notes': usage_notes,
                    'example': example,
                })
            if line == '':
                f.close()
                print('File Extracted!')
                break

def writeFile():
    global jsonData
    with open(TARGET_FILE_PATH,'w') as json_file:
        json.dump(jsonData,json_file,ensure_ascii=False)
        json_file.close()
        print('JSON File saved!')


if __name__ == "__main__":
    extract()
    writeFile()
