import sys
import os
import numpy as np
import cv2
from scipy.ndimage import maximum_filter
import sys

from PostgreSQL import PostgreSQL
from Redis import Redis
from random import randint
from Estimate import estimate


class Main:

    def __init__(self, image_key, shelf_count):
        self.image_key = image_key
        self.shelf_count = int(shelf_count)
        # self.image_key = '2018/07/27-19:44:31_sava_1'

    @staticmethod
    def rotate_image(img, side=90):
        (h, w) = img.shape[:2]
        center = (w / 2, h / 2)
        M = cv2.getRotationMatrix2D(center, side, 1.0)
        return cv2.warpAffine(img, M, (w, h))

    @staticmethod
    def downsize(img, img_tpl, width, height):
        print("start down")
        print("shape 1", img.shape[1])
        print("shape 0", img.shape[0])
        for x in range(0, 10000, 100):
            try:
                r = (float(width) - x) / img.shape[1]
                dim = (width - x, int(img.shape[0] * r))

                if x == 0:
                    img_res = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
                    # img_res = cv2.resize(img, dim)
                else:
                    img_res = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
                    # img_res = cv2.resize(img, dim)
                    # cv2.imwrite(
                    #     "C:\\Users\\savch\\PycharmProjects\\template-matcher\\data\\result\\QQQ{}.jpg".format(x), img_res)
                # Match map building

                match_map = cv2.matchTemplate(img_res, img_tpl, cv2.TM_CCOEFF_NORMED)
            except Exception as e:
                print("end down", e)
                return []

            max_match_map = np.max(match_map)  # The value of the map for the region closest to the template
            print("x = {}, map = {}".format(x, max_match_map))
            if max_match_map < 0.77:
                if x == 10000:
                    return []
            else:
                return match_map, max_match_map

    @staticmethod
    def upsize(img, img_tpl, width, height):
        print("start up")
        for x in range(0, 10000, 100):
            try:
                r = (float(width) + x) / img.shape[1]
                dim = (width + x, int(img.shape[0] * r))

                if x == 0:
                    img_res = cv2.resize(img, (width, height), interpolation=cv2.INTER_CUBIC)
                    # img_res = cv2.resize(img, (width, height))
                else:
                    img_res = cv2.resize(img, dim, interpolation=cv2.INTER_CUBIC)
                    # img_res = cv2.resize(img, dim)
                    # cv2.imwrite(
                    #     "C:\\Users\\savch\\PycharmProjects\\template-matcher\\data\\result\\LLL{}.jpg".format(x),
                    #     img_res)
                # Match map building

                match_map = cv2.matchTemplate(img_res, img_tpl, cv2.TM_CCOEFF_NORMED)
            except Exception as e:
                print("end down", e)
                return []

            max_match_map = np.max(match_map)  # The value of the map for the region closest to the template
            print("x = {}, map = {}".format(x, max_match_map))
            if max_match_map < 0.77:
                if x == 10000:
                    return []
            else:
                return match_map, max_match_map

    @staticmethod
    def find_templ(img, img_tpl):
        # img_canny = cv2.Canny(img, 100, 200)
        # img_tpl_canny = cv2.Canny(img_tpl, 200, 400)
        #
        # # cv2.imwrite(
        # #     "C:\\Users\\savch\\PycharmProjects\\template-matcher\\data\\result\\res1.jpg", img_canny)
        # cv2.imwrite(
        #     "C:\\Users\\savch\\PycharmProjects\\template-matcher\\data\\result\\res.jpg", img_tpl_canny)
        #####################
        # Template shape
        global max_match_map

        f = False
        for degree in [0, 90, 270]:
            img_tpl = main.rotate_image(img_tpl, degree)
            h, w = img_tpl.shape
            height, width = img.shape

            tpl = main.downsize(img, img_tpl, width, height)
            if not tpl:
                tpl = main.upsize(img, img_tpl, width, height)
                if not tpl:
                    f = False
                else:
                    f = True
                    match_map = tpl[0]
                    max_match_map = tpl[1]
                    break
            else:
                f = True
                match_map = tpl[0]
                max_match_map = tpl[1]
                break

        if not f:
            return []




        a = 0.7  # Coefficient of "similarity", 0 - all, 1 - exact match

        # Cut the map on the threshold
        match_map = (match_map >= max_match_map * a) * match_map

        # Select local max on the map
        match_map_max = maximum_filter(match_map, size=min(w, h))
        # Areas closest to the pattern
        match_map = np.where((match_map == match_map_max), match_map, 0)

        # Coordinates of local max
        ii = np.nonzero(match_map)
        rr = tuple(zip(*ii))

        res = [[c[1], c[0], w, h] for c in rr]

        return res

    # Draw a frames of matches found
    @staticmethod
    def draw_frames(img, coord):
        res = img.copy()
        for c in coord:
            top_left = (c[0], c[1])
            bottom_right = (c[0] + c[2], c[1] + c[3])
            cv2.rectangle(res, top_left, bottom_right, color=(0, 0, 255), thickness=5)
        return res

    # Crop enter image into shelfs
    @staticmethod
    def crop_image(img_path, n):
        crop_image_folder = "C:\\Users\\savch\\PycharmProjects\\template-matcher\\data\\shelf_image\\"
        # image from device
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        h, w = img.shape
        new_img_h = h // n
        start_h = 0
        for x in range(1, n + 1):
            crop_img = img[start_h:start_h + new_img_h, 0:w]
            tn = os.path.splitext(os.path.basename(img_path))[0]
            cv2.imwrite(
                "C:\\Users\\savch\\PycharmProjects\\template-matcher\\data\\shelf_image\\s_{}_{}.jpg".format(tn, x),
                crop_img)
            start_h += new_img_h

        return [os.path.join(crop_image_folder, b)
                for b in os.listdir(crop_image_folder)
                if os.path.isfile(os.path.join(crop_image_folder, b))]

    # Get agreement id
    @staticmethod
    def get_agreement_id(id_agreement_data):
        postgres = PostgreSQL()
        return postgres.select_agreement_id(id_agreement_data)

    def main(self):
        # Connect to redis and get image to proceed
        # postgres = PostgreSQL()
        # agreement_id = postgres.select_agreement_id(self.image_key)
        # product_title = postgres.select_product_title(str(agreement_id[0]))
        # product_type_title = postgres.select_product_type_tytle(product_title[0])
        global match_count, shelf
        # redis = Redis(self.image_key)
        # redis.get_image()

        # TODO: change to image
        enter_image_path = "C:\\Users\\savch\\PycharmProjects\\template-matcher\\data\\image\\image2.jpg"
        # enter_image_path = "C:\\Users\\savch\\PycharmProjects\\template-matcher\\data\\image\\0000.jpg"
        template_image_folder = "C:\\Users\\savch\\PycharmProjects\\template-matcher\\data\\template\\alcohol"
        # template_image_folder = "C:\\Users\\savch\\PycharmProjects\\template-matcher\\data\\template\\{}".format(product_type_title[0])
        print(template_image_folder)

        # template image
        templ = [os.path.join(template_image_folder, b) for b in os.listdir(template_image_folder) if
                 os.path.isfile(os.path.join(template_image_folder, b))]
        # templ = [template for template in templ if template == "C:\\Users\\savch\\PycharmProjects\\template-matcher\\data\\template\\{}\\{}.jpg".format(product_type_title[0], product_title[0])]
        templ = [template for template in templ if
                 template == "C:\\Users\\savch\\PycharmProjects\\template-matcher\\data\\template\\{}\\{}.jpg".format(
                     "alcohol", "t2")]


        # shelf count
        # shelf_count = 2
        crop_image_list = self.crop_image(enter_image_path, self.shelf_count)

        res_list = []
        match_count = 0
        for t in templ:

            img_tpl = cv2.imread(t, cv2.IMREAD_GRAYSCALE)

            for img in crop_image_list:
                shelf = int(img[len(img) - 5:len(img) - 4])
                img_gray = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
                coord = self.find_templ(img_gray, img_tpl)

                # Match count on the shelf
                match_count = len(coord)

                img_res = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
                img_res = self.draw_frames(img_res, coord)
                tn = os.path.splitext(os.path.basename(img))[0]
                if len(coord) != 0:
                    cv2.imwrite(
                        "C:\\Users\\savch\\PycharmProjects\\template-matcher\\data\\result\\res_{}.jpg".format(
                            randint(0, 1000)), img_res)
                # for c in coord:
                #     print(c)

                if len(coord) != 0:
                    res_list.append(("res_{}_{}.jpg".format(tn, match_count), shelf, match_count))
                if match_count != 0:
                    break
            print(match_count)

        # estimate(self.image_key, match_count, shelf)

                # print("- - - - - - - - - - - - - - -")


if __name__ == "__main__":
    # print("OpenCV ", cv2.__version__)
    # sys.exit(main())
    main = Main(image_key="2018/07/28-17:37:06_sava_3", shelf_count=1)
    # main = Main(image_key=sys.argv[1], shelf_count=sys.argv[2])
    main.main()
