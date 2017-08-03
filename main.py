# coding:utf-8

from instagram_spider import Instagram_Spider

# url = 'https://www.instagram.com/stronger917/'
# ins = Instagram_Spider(url, url.split('/')[-2])

# ins.main()

urls = {
    'zhaoliying': 'https://www.instagram.com/zhaoliyingofficial/',
    'linxinru': 'https://www.instagram.com/loveruby_official/',
    'chenqiaoen': 'https://www.instagram.com/joe_chenn/',
    'liyifeng':'https://www.instagram.com/liyifengofficial/',
    'yangyang':'https://www.instagram.com/yangyangfavour/',
    'dengchao':'https://www.instagram.com/dengchaoxueba/',
    'wangkai':'https://www.instagram.com/wangkai_kw/',
    'jingboran':'https://www.instagram.com/xxjingboxx/'
}
for name in urls:
    print name,urls[name]
    ins = Instagram_Spider(urls[name], name)
    ins.main()
