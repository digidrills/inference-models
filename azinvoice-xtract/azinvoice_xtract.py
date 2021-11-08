import json

def xtract_one_azinvoice(srcname:str, azform_json:dict, incl_box:bool, incl_fields:bool) -> dict:
    xtract_flds = dict()
    xtract_flds.update({'srcname': srcname, 'status': azform_json.get('status'), 'pages': list(), 'boxes': list(), 'fields': list()})

    if incl_box and 'readResults' in azform_json.get('analyzeResult'):
        for pg in azform_json.get('analyzeResult').get('readResults'):
            pgno = pg.get('page')
            for ln in pg.get('lines'):
                newbox = {'pgno': pgno, 'text': ln.get('text'), 'coords': ln.get('boundingBox')}
                xtract_flds.get('boxes').append(newbox)

    if incl_fields and 'documentResults' in azform_json.get('analyzeResult'):
        for colln in azform_json.get('analyzeResult').get('documentResults'):
            for fld in colln.get('fields'):
                f = colln.get('fields').get(fld)
                if 'type' in f and 'text' in f and 'confidence' in f and f.get('type') not in ['array']:
                    value = ''
                    value = f.get('valueString') if 'valueString' in f else value
                    value = f.get('valueNumber') if 'valueNumber' in f else value
                    value = f.get('valueDate') if 'valueDate' in f else value

                    l = {'fld': fld, 'type': f.get('type'), 'text': f.get('text'), 'value': value, 'score': f.get('confidence'), 'tbllist': list()}
                    xtract_flds.get('fields').append(l)
                else:
                    l = {'fld': fld, 'type': f.get('type'), 'text': '', 'value': '', 'score': 0, 'tbllist': list()}
                    for rno, r in enumerate(f.get('valueArray')):
                        if 'type' in r and r.get('type') in ['object']:
                            l.get('tbllist').append({'rno': rno+1, 'r': list()})
                            
                            itmobj = r.get('valueObject')
                            for k in itmobj:
                                i = itmobj.get(k)
                                value = ''
                                value = i.get('valueString') if 'valueString' in i else value
                                value = i.get('valueNumber') if 'valueNumber' in i else value
                                value = i.get('valueDate') if 'valueDate' in i else value

                                itm = {'fld': k, 'type': i.get('type'), 'text': i.get('text'), 'value': value, 'score': i.get('confidence')}
                                l.get('tbllist')[-1]['r'].append(itm)

                    xtract_flds.get('fields').append(l)

    return xtract_flds

files = ["InvoiceResult-C0139 08-30-2021 DIR108647.pdf.json", "InvoiceResult-D0024 08-27-2021 CIN0009795.pdf.json", "InvoiceResult-D0024 08-31-2021 CIN0010044.pdf.json"]
xtract_result = dict()
for f in files:
    with open(f) as fptr:
        azform_json = json.load(fptr)
        xtract_flds = xtract_one_azinvoice(srcname=f, azform_json=azform_json, incl_box=False, incl_fields=True)
        fptr.close()

    xtract_result.update({f: xtract_flds})

print(xtract_result)




