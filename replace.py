import os

for i in os.walk("/home/bingtao/workspace/hubs/funmedia/funmedia"):
    for file in i[2]:
        path=os.path.join(i[0], file)
        if not path.endswith(".py"):
            continue
        print(path)
        text=open(path,'r').read()
        open(path,'w').write(text.replace("from f2",'from funmedia'))
    