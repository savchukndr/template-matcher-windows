import redis
import base64


class Redis:

    def __init__(self, key):
        self.r = redis.Redis(host='localhost')
        self.key = key

    def get_image(self):
        imgdata = base64.b64decode(self.r.get(self.key))
        filename = 'C:\\Users\\savch\\PycharmProjects\\template-matcher\\data\\image\\image.jpg'
        with open(filename, 'wb') as f:
            f.write(imgdata)


if __name__ == "__main__":
    rd = Redis('2018/07/27-19:51:17_sava_1')
    rd.get_image()
