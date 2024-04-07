from urllib import parse
class UrlManager(object):
    #初始化，待爬取URL和已爬取URL
    def __init__(self):
        self.new_urls = set()
        self.old_urls = set()
    #添加新URL进管理器
    def add_new_url(self, url):
        if url is None:
            return
        if url not in self.new_urls and url not in self.old_urls:
            self.new_urls.add(url)
    #批量添加URLS
    def add_new_urls(self, urls):
        if urls is None or len(urls) == 0:
            return
        for url in urls:
            self.add_new_url(url)
    def has_new_url(self):
        return len(self.new_urls) != 0
    #pop方法可以把其中的一个URL给弹出，并且移除
    def get_new_url(self):
        new_url = self.new_urls.pop()
        self.old_urls.add(new_url)
        return new_url

    def get_search_name(self,url):
        names = url.split('/')
        return parse.unquote(names[4])

    def create_url(self,name):
        encodename = parse.quote(str(name))
        return "https://baike.baidu.com/item/" + encodename


