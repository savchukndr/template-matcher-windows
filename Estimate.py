from PostgreSQL import PostgreSQL
import re
import time
import datetime


def estimate(image_key, product_count, product_shelf_position):
    postgres = PostgreSQL()
    agreement_data = postgres.select_agreement_data(image_key=image_key)
    searchObj = re.search(r'[^_]+$', image_key)
    ts = time.time()

    image_id = image_key
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y/%m/%d-%H:%M:%S')
    agrement_data_id = int(searchObj.group())

    agreement_product_count = int(agreement_data[0])
    agreement_product_shelf_position = int(agreement_data[1])

    if product_count == 0:
        is_product_on_exposition = "False"
        is_product_visible = "False"
        is_distributor_visible = "False"
        product_count_db = "False"
        product_localization = "False"
    else:
        is_product_on_exposition = "True"
        is_product_visible = "True"
        is_distributor_visible = "True"
        if product_count != agreement_product_count:
            product_count_db = "False"
        else:
            product_count_db = "True"
        if product_shelf_position != agreement_product_shelf_position:
            product_localization = "False"
        else:
            product_localization = "True"

    if is_product_on_exposition == "True" and product_localization == "True" and \
            is_product_visible == "True" and is_distributor_visible == "True" and product_count_db == "True":
        image_proc_estimation = "Good"
    else:
        image_proc_estimation = "Bad"

    postgres.insert_result(
        [product_count_db, is_product_on_exposition, product_localization, is_product_visible, is_distributor_visible,
         date, image_proc_estimation, image_id, agrement_data_id])

    # print("agreement_id:", agrement_data_id)
    # print("image_id:", image_id)
    # print("date:", date)
    #
    # print("agreement_product_count:", agreement_product_count)
    # print("agreement_product_shelf_position:", agreement_product_shelf_position)
    #
    # print("image_product_count: ", product_count)
    # print("image_product_shelf_position:", product_shelf_position)
