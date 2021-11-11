import json

def xtract_one_azinvoice(srcname:str, azformJson:dict, inclBox:bool, inclFields:bool) -> dict:
    xtract_flds = dict()
    xtract_flds.update({'srcname': srcname, 'status': azform_json.get('status'), 'pages': list(), 'boxes': list(), 'fields': list()})

    if inclBox and 'readResults' in azform_json.get('analyzeResult'):
        for pg in azformJson.get('analyzeResult').get('readResults'):
            pgno = pg.get('page')
            for ln in pg.get('lines'):
                newbox = {'pgno': pgno, 'text': ln.get('text'), 'coords': ln.get('boundingBox')}
                xtract_flds.get('boxes').append(newbox)

    if inclFields and 'documentResults' in azform_json.get('analyzeResult'):
        for colln in azformJson.get('analyzeResult').get('documentResults'):
            for fld in colln.get('fields'):
                f = colln.get('fields').get(fld)
                if 'type' in f and 'text' in f and 'confidence' in f and f.get('type') not in ['array']:
                    value = ''
                    value = f.get('valueString') if 'valueString' in f else value
                    value = f.get('valueNumber') if 'valueNumber' in f else value
                    value = f.get('valueDate') if 'valueDate' in f else value

                    l = {'srcname': srcname, 'fld': fld, 'type': f.get('type'), 'text': f.get('text'), 'value': value, 'score': f.get('confidence'), 'tbllist': list()}
                    xtract_flds.get('fields').append(l)
                else:
                    l = {'fld': fld, 'type': f.get('type'), 'text': '', 'value': '', 'score': 0, 'tbllist': list()}
                    for rno, r in enumerate(f.get('valueArray')):
                        if 'type' in r and r.get('type') in ['object'] and 'valueObject' in r:
                            l.get('tbllist').append({'rno': rno+1, 'r': list()})
                            
                            itmobj = r.get('valueObject')
                            for k in itmobj:
                                i = itmobj.get(k)
                                value = ''
                                value = i.get('valueString') if 'valueString' in i else value
                                value = i.get('valueNumber') if 'valueNumber' in i else value
                                value = i.get('valueDate') if 'valueDate' in i else value

                                itm = {'srcname': srcname, 'fld': k, 'type': i.get('type'), 'text': i.get('text'), 'value': value, 'score': i.get('confidence')}
                                l.get('tbllist')[-1]['r'].append(itm)

                    xtract_flds.get('fields').append(l)

    return xtract_flds

def collate_xtractd_azinvoices(xtractdAzInvoices:dict) -> dict:
    azi = xtractdAzInvoices
    cl_fields = dict()
    for invc in azi:
        srcname = azi.get(invc).get('srcname')
        for xtract_row in azi.get(invc).get('fields'):
            if xtract_row.get('value') not in ['']:
                # regular fields.. not a table
                cl_fields.update({xtract_row.get('fld'): {'clflds': [], 'textseen': list()}}) if xtract_row.get('fld') not in cl_fields else None
                if xtract_row.get('text') not in cl_fields.get(xtract_row.get('fld')).get('textseen'):
                    # keep only unique records
                    xtract_row.pop('tbllist', None)
                    cl_fields.get(xtract_row.get('fld')).get('clflds').append(xtract_row)
                    cl_fields.get(xtract_row.get('fld')).get('textseen').append(xtract_row.get('text'))

            else:
                # tabular fields.. is a table
                tbl_prefix = xtract_row.get('fld')
                for tbl_row in xtract_row.get('tbllist'):
                    r = tbl_row.get('r')
                    for col in r:
                        cl_fields.update({col.get('fld'): {'clflds': [], 'textseen': list()}}) if col.get('fld') not in cl_fields else None
                        if col.get('text') not in cl_fields.get(col.get('fld')).get('textseen'):
                            # keep only unique records
                            col.pop('tbllist', None)
                            cl_fields.get(col.get('fld')).get('clflds').append(col)
                            cl_fields.get(col.get('fld')).get('textseen').append(col.get('text'))

    # now process the titles also
    cl_fields.update({'_InvoiceFields_': {'clflds': [], 'textseen': list()}})
    for fld in cl_fields:
        row = {'srcname': srcname, 'fld': fld, 'type': 'string', 'text': fld, 'value': fld, 'score': 100}
        cl_fields.get('_InvoiceFields_').get('clflds').append(row) if fld not in ['_InvoiceFields_'] else None

    # and also the file-names

    return cl_fields

#files = ["InvoiceResult-C0139 08-30-2021 DIR108647.pdf.json", "InvoiceResult-D0024 08-27-2021 CIN0009795.pdf.json", "InvoiceResult-D0024 08-31-2021 CIN0010044.pdf.json"]
files = ["InvoiceResult-A0095 01-12-2021 382576-4328.pdf.json"]
xtract_result = dict()
for f in files:
    with open(f, encoding="utf8") as fptr:
        azform_json = json.load(fptr)
        xtract_flds = xtract_one_azinvoice(srcname=f, azformJson=azform_json, inclBox=False, inclFields=True)
        fptr.close()

    xtract_result.update({f: xtract_flds})

# print(xtract_result)

colltd_fields = collate_xtractd_azinvoices(xtractdAzInvoices=xtract_result)
for fld in colltd_fields:
    print("======================= {}".format(fld))
    for val in colltd_fields.get(fld).get('clflds'):
        print(val)







