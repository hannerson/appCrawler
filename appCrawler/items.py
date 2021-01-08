# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class searchItem(scrapy.Item):
    # define the fields for your item here like:
    keyword_id = scrapy.Field()
    keyword = scrapy.Field()
    creator = scrapy.Field()
    source_id = scrapy.Field()
    name = scrapy.Field()
    artist = scrapy.Field()
    source_name = scrapy.Field()
    play_num = scrapy.Field()
    sub_num = scrapy.Field()
    fans_num = scrapy.Field()
    fav_num = scrapy.Field()
    comment_num = scrapy.Field()
    finished = scrapy.Field()
    fee_type = scrapy.Field()
    intro = scrapy.Field()
    created_at = scrapy.Field(serializer=str)
    pass

class WebmonitorItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
