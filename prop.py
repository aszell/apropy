import re
from collections import OrderedDict
from namedlist import namedlist

TransItem = namedlist('TransItem', 'key, comment, trans', default='')

def unidecode(stre):
    stnew = stre.group(0).decode('unicode-escape')
    #print "re: ", stre.group(0), stnew, hexlify(stre.group(0))
    return stnew

def to_unicode(st):
    # first convert normal accented latin-1 string to unicode
    st = st.decode('latin-1')
    # then convert unicode escapes to unicode in the unicode string
    # (done so to avoid various python 2.7 error messages regarding encoding)
    rest = re.sub(r'\\u[0-9a-fA-F]{4}', unidecode, st)
    return rest

def from_unicode(ust):
    st = ''
    for uch in ust:
        res =  uch.encode('iso-8859-1', "xmlcharrefreplace")
        #print res, len(res)
        if len(res) > 1:
            assert(res[0:2] == '&#')
            st += '\\u%04x' % int(res[2:-1])
        else:
            st += res
    return st

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
        l = to_unicode(l)
        if state == MULTILINE:
            if not ismultiline(l):
                state = COMMENTS
                item.trans += l.rstrip('\n')
                tdict[item.key] = item
                item = TransItem()
            else:
                item.trans += l
        elif state == COMMENTS:
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
        outstr = item.key + '=' + item.trans
        fhnd.write(from_unicode(outstr) + '\n')

if __name__ == "__main__":
    #with open('msg_bundle_hu.properties.orig', 'rU') as fin:
    with open('msg_bundle_hu.properties', 'rU') as fin:
        items = propread(fin)

    print items['Standings']
    #print items['AICasual'].trans.decode('unicode-escape')
    #print items['AICasual'].trans.decode('unicode-escape').encode('unicode-escape')

    with open('res', 'wb') as fout:
        propsave(fout, items)