import re

SPECIMAN_REGEX='AMNH [A-Z]-[0-9]*'

def find_specimans(file_name):
    text = open(file_name)
    article = text.read()
    p = re.compile(SPECIMAN_REGEX)
    sp_list = list(set(p.findall(article)))
    sp_list.sort()
    return sp_list
    
speciman_list = find_specimans('N3849.txt')
print speciman_list

  