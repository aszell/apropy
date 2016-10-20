from collections import OrderedDict
from namedlist import namedlist

TransItem = namedlist('TransItem', 'key, comment, trans', default='')

def isemptyline(st):
    return not st.strip()

def iscomment(st):
    return st.strip() and st.lstrip()[0] == '#'

def ismultiline(st):
    return st.strip() and st.rstrip('\n')[-1] == '\\'

def iskey(st):
    return '=' in st

def break_key(st):
    twoparts = st.split('=', 1)
    keyword = twoparts[0].strip()
    trans = twoparts[1].rstrip('\n')
    return keyword, trans
    
def propread(fhnd):
    ''' Return an ordered dictionary with key, comments, translation pairs.
        Properly process multiline comments and translations, and parse unicode strings '''
    COMMENTS = 0
    MULTILINE = 1
    
    state = COMMENTS
    
    item = TransItem()
    tdict = OrderedDict()

    for l in fhnd:
        if state == MULTILINE:
            if not ismultiline(l):
                state = COMMENTS
                item.trans += l.rstrip('\n')
                tdict[item.key] = item
                item = TransItem()
            else:
                item.trans += l
        if state == COMMENTS:
            if iscomment(l) or isemptyline(l):
                item.comment += l
            elif iskey(l):
                item.key, item.trans = break_key(l)
                if ismultiline(l):
                    state = MULTILINE
                    item.trans += '\n'
                else:
                    tdict[item.key] = item
                    item = TransItem()

    return tdict
    
def propsave(fhnd, propdict):
    for key, item in propdict.items():
        fhnd.write(item.comment)
        fhnd.write(item.key + '=' + item.trans + '\n')

if __name__ == "__main__":
    #with open('msg_bundle_hu.properties.orig', 'rU') as fin:
    with open('msg_bundle_hu.properties', 'rU') as fin:
        items = propread(fin)
        
    print items['wholeday']

    with open('res', 'wb') as fout:
        propsave(fout, items)