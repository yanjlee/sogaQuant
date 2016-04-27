# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field


class WdspiderItem(Item):
    # define the fields for your item here like:
    # name = Field()
    question = Field()
    question_detail = Field()
    topics = Field()
    answers = Field()
    answers_text = Field()
    signcc = Field()
    callback = Field()


class BdWordsItem(Item):
    hash_str = Field()
    word = Field()
    link = Field()
