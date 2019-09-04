#/usr/bin/env python3
import re
import sys
import encodings
import pkgutil

all_encodings = set()

for _, modname, _ in pkgutil.iter_modules(
        encodings.__path__, encodings.__name__ + '.',
):
    try:
        mod = __import__(modname, fromlist=[str('__trash')])
    except (ImportError, LookupError):
        # A few encodings are platform specific: mcbs, cp65001
        # print('skip {}'.format(modname))
        continue

    try:
        enc = mod.getregentry()
        try:
            if not enc._is_text_encoding:
                continue
        except AttributeError:
            try:
                ''.encode(enc.name)
            except LookupError:
                continue
        all_encodings.add(enc.name)
    except AttributeError as e:
        # the `aliases` module doensn't actually provide a codec
        # print('skip {}'.format(modname))
        if 'regentry' not in str(e):
            raise

all_encodings -= set(['unicode-internal', 'undefined', 'mbcs', 'oem', 'raw-unicode-escape', 'unicode-escape', 'charmap'])
try:
    import ebcdic
    all_encodings |= set(ebcdic.codec_names)
except ModuleNotFoundError:
    pass
try:
    import cbmcodecs
    all_encodings |= {'petscii-c64en-lc', 'petscii-c64en-uc', 'petscii-vic20en-lc', 'petscii-vic20en-uc', 'screencode-c64-lc', 'screencode-c64-uc'}
except ModuleNotFoundError:
    pass

all_encodings = sorted(all_encodings)

found = False
if sys.argv[1] == '-f':
    strseen = sys.argv[2]
    strreal = sys.argv[3]
    for enc_s in all_encodings:
        try:
            seen_enc = strseen.encode(enc_s)
        except (LookupError, UnicodeError):
            continue
        for enc_r in all_encodings:
            try:
                real_enc = strreal.encode(enc_r)
            except (LookupError, UnicodeError):
                continue
            if seen_enc == real_enc:
                print('Found candidate: {}, {}'.format(enc_s, enc_r))
                found = True
    if not found:
        print('No candidates found')
else:
    strdata = sys.argv[1]
    sval = sys.argv[2]
    sval = re.sub(r'\s', '', sval)
    if len(sval) % 2 == 1:
        sval = u'0' + sval
    val = bytes([int(sval[i:i+2], 16) for i in range(0, len(sval), 2)])

    for enc in all_encodings:
        try:
            strenc = strdata.encode(enc)
        except (LookupError, UnicodeError):
            continue
        if strenc == val:
            print('Encoding match: ' + enc)
            found = True

    if not found:
        print('No matching encoding found')
