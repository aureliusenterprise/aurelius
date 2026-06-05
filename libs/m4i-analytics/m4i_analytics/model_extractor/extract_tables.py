"""
Created on Thu Aug 23 21:18:33 2018

@author: andre
"""

# %%
import itertools

import sqlparse
from sqlparse.sql import Function, Identifier, IdentifierList
from sqlparse.tokens import DML, Keyword, Name, Punctuation


def extract_tables(sql):
    def is_subselect(parsed):
        if not parsed.is_group:
            return False
        return any(item.ttype is DML and item.value.upper() == "SELECT" for item in parsed.tokens)

    def extract_from_part(parsed):
        from_seen = False
        insert_seen = False
        into_seen = False
        update_seen = False
        delete_seen = False
        delete_from_seen = False
        # insert_tablename = ''
        # print 'hi'
        for item in parsed.tokens:
            # print('%s %s|%s(%s , %s)' % (item,str(into_seen),str(from_seen),type(item), item.ttype))

            if item.is_group:
                # print 'group'
                for x in extract_from_part(item):
                    yield x
            if into_seen and isinstance(item, (Identifier, Function)):
                # print('@@@ found a input name')
                yield item
                # if item.ttype is Punctuation:
                #    #print('@@@ found a punctuation')
                #    yield item
                # elif isinstance(item, Identifier):
                #    print('@@@ drill down')
                #    for x in extract_from_part(item, True):
                #        yield x
                # elif isinstance(item, Function):
                #    yield item
                # insert_tablename = insert_tablename+item.value
                # elif item.ttype is Punctuation and item.value.upper() == '.':
                # insert_tablename = insert_tablename+item.value
                #    yield item
                # elif isinstance(item, Function) and item.is_group:
                #    print('########## %s' % item)
                #    for item3 in item.tokens:
                #        #print('##########  %s %s (%s)' % (item3,type(item3),item3.ttype))
                #        if item3.ttype is Name:
                #            print(' found identifier %s' % item3)
                #            yield item3
                insert_seen = False
                into_seen = False
                #           yield item3
            if insert_seen and item.ttype is Keyword and item.value.upper() == "INTO":
                into_seen = True
                # print('found it')
            if update_seen:
                # print('%s %s(%s , %s)' % (item,str(update_seen),type(item), item.ttype))
                if item.ttype is Keyword and item.value.upper() in ["SET"]:
                    # print('@@@ end of update')
                    update_seen = False
                elif is_subselect(item):
                    # print('@@@ is subselect')
                    for x in extract_from_part(item):
                        yield x
                elif isinstance(item, (Identifier, Function)):
                    # print('@@@ found a update name')
                    yield item

                #           yield item3
            if delete_from_seen and isinstance(item, (Identifier, Function)):
                # print('%s %s(%s , %s)' % (item,str(into_seen),type(item), item.ttype))
                # print('@@@ found a delete name')
                yield item
                delete_from_seen = False
                delete_seen = False
            #           yield item3
            if delete_seen and item.ttype is Keyword and item.value.upper() == "FROM":
                delete_from_seen = True
            if from_seen:
                # print 'from'
                if is_subselect(item):
                    for x in extract_from_part(item):
                        yield x
                elif item.ttype is Keyword and item.value.upper() in [
                    "ORDER",
                    "GROUP",
                    "BY",
                    "HAVING",
                ]:
                    from_seen = False
                else:
                    # print('@@@  found select name')
                    yield item
            if item.ttype is DML and item.value.upper() == "INSERT":
                insert_seen = True
            if item.ttype is DML and item.value.upper() == "UPDATE":
                update_seen = True
            if item.ttype is DML and item.value.upper() == "DELETE":
                delete_seen = True
            if item.ttype is Keyword and item.value.upper() == "FROM":
                from_seen = True

    def valid_identifier(item):
        # return True
        ll = item.tokens
        # remove trailing and leading whitespaces
        if not (ll[0].ttype == Name or len(ll) % 2 == 1):
            return False
        ii = 1
        while ii < len(ll):
            if ll[ii + 1].ttype != Name or ll[ii].ttype != Punctuation:
                return False
            ii = ii + 2
        return True

    def extract_table_identifiers(token_stream, statement):
        if statement.get_type() == "SELECT":
            for item in token_stream:
                # print('%s %s' % (type(item),str(item)))
                if isinstance(item, IdentifierList):
                    for identifier in item.get_identifiers():
                        if valid_identifier(identifier):
                            value = identifier.value.replace('"', "").lower()
                            yield value
                            # yield identifier
                elif isinstance(item, Identifier) and valid_identifier(item):
                    value = item.value.replace('"', "").lower()
                    yield value
                    # yield item
        elif (
            statement.get_type() == "INSERT"
            or statement.get_type() == "DELETE"
            or statement.get_type() == "UPDATE"
        ):
            # print('&&&&found insert')
            for item in token_stream:
                # print('%s %s' % (type(item),str(item)))
                if isinstance(item, (Function, Identifier)):
                    # print('########## %s' % item)
                    # print('-------- %s' % item.value.split('(')[0])
                    value = item.value.split("(")[0].strip()
                    value = value.split(" ")[0].strip()
                    if len(str(value)) > 0:
                        yield value

    if sql is None or len(sql) == 0:
        return None

    # let's handle multiple statements in one sql string
    extracted_tables = []
    statements = sqlparse.parse(sql)

    for statement in statements:
        # print statement.get_type()
        if statement.get_type() != "UNKNOWN":
            stream = extract_from_part(statement)
            # print(list(extract_table_identifiers(stream, statement)))
            extracted_tables.append(set(list(extract_table_identifiers(stream, statement))))
            # extracted_tables.append(set(list(stream)))

            # for item in (extract_table_identifiers(stream)):
            #     print item
    # print(list(itertools.chain(*extracted_tables)))
    return list(itertools.chain(*extracted_tables))


# extracted_tables = []
# statements = (sqlparse.parse(sql))
# extract_tables3(sql)


def extract_statement_type2(sql):
    def max_statement_type(parsed):
        if not parsed.is_group:
            return False
        return any(item.ttype is DML and item.value.upper() == "SELECT" for item in parsed.tokens)

    if sql is None or len(sql) == 0:
        return None
    statements = sqlparse.parse(sql)
    res = False
    for statement in statements:
        if statement.get_type() != "UNKNOWN":
            res = res or max_statement_type(statement)
    return res


def extract_statement_type(sql):
    if sql is None or len(sql) == 0:
        return None
    statements = sqlparse.parse(sql)
    res = []
    for statement in statements:
        res.append(statement.get_type())
    if len(res) == 0:
        res = None
    return res


# q='''
# insert into mv_utc_produce_raw
# SELECT '${machine}' as machine,
# '${facility}' as facility,
# data_::json ->> 'DefectCode'::text as defectcode,
#    '${PartNo}' as partnumber,
#                CASE
#                    WHEN a.maxpartpercycle IS NULL THEN 1
#                    ELSE a.maxpartpercycle
#                END AS count,
#    replace(concat(substring('${ts}', 0, 14), ':00'),'T',' ') AS utc_timestamp_hour,
#    substring('${ts}', 0, 11) AS utc_timestamp_date,#
# '${ts}'::timestamp as utc_timestam#p
#   FROM
#   ( SELECT DISTINCT
# case when length('${data}') = 0 then '{"DefectCode":"-1"}' else '${data}' end as data_,
# b.maxpartpercycle as maxpartpercycle
#                      FROM tbl_pt_device_equipment_v1 b
#                      WHERE b.active_ = 1 AND b.signalid::text = 'ECP'::text
#                      AND b.assetid::text = '${machine}'::text)a
#'''
# extract_tables(q)
