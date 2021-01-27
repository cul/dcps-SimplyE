import ia_opds_functions as ia
import dcps_utils as util
from pprint import pprint
from sheetFeeder import dataSheet


base_url = 'https://ebooksbeta.lyrasistechnology.org/columbia/book/URI%2Furn%3Ax-internet-archive%3Aebooks-app%3Aitem%3A'


def main():

    sheet_id = '1X4e52glzKJjRpiOb7S6b4bOzyhTfjHCVlfjPosdABKM'

    the_info = [
        {'name': 'AveryTrade', 'file': 'output/ia/ia_avt_feed.pickle'},
        {'name': 'Carnegie', 'file': 'output/ia/ia_ccny_feed.pickle'},
        {'name': 'Durst', 'file': 'output/ia/ia_durst_feed.pickle'},
        {'name': 'MedicalHeritage', 'file': 'output/ia/ia_med_feed.pickle'},
        {'name': 'MissionaryResearch', 'file': 'output/ia/ia_mrp_feed.pickle'},
        {'name': 'MuslimWorld', 'file': 'output/ia/ia_mwm_feed.pickle'},
        {'name': 'WWI', 'file': 'output/ia/ia_wwi_feed.pickle'},
    ]

    the_out_sheet = dataSheet(sheet_id, 'Combined!A:Z')
    the_out_sheet.clear()

    the_heads = ['collection', 'bibid', 'href', 'label']
    the_data = [the_heads]
    for i in the_info:
        the_links = get_links(i['file'])
        the_data += [[i['name'], r[0], r[1], r[2]] for r in the_links]

    post = the_out_sheet.appendData(the_data)
    print(post)

    quit()
    # post = the_out_sheet.appendData(get_links('output/ia/ia_ll_1931.pickle'))
    # print(post)
    # post = the_out_sheet.appendData(get_links('output/ia/ia_ll_1932.pickle'))
    # print(post)
    # post = the_out_sheet.appendData(get_links('output/ia/ia_ll_1933.pickle'))
    # print(post)
    # post = the_out_sheet.appendData(get_links('output/ia/ia_ll_1934.pickle'))
    # print(post)
    # post = the_out_sheet.appendData(get_links('output/ia/ia_ll_1935.pickle'))
    # print(post)
    # post = the_out_sheet.appendData(get_links('output/ia/ia_ll_1936.pickle'))
    # print(post)
    # post = the_out_sheet.appendData(get_links('output/ia/ia_ll_1937.pickle'))
    # print(post)

    quit()


def get_links(pickle_file):
    feed_data = util.unpickle_it(pickle_file)
    results = []
    for r in feed_data:
        r_bibid = r['cul_metadata']['bibid']
        r_id = r['identifier']
        r_href = base_url + r_id
        r_label = r['cul_metadata']['label']
        results.append([r_bibid, r_href, r_label])
    return results


if __name__ == "__main__":
    main()
