from amazon.api import AmazonAPI
import pdb
import os

amazon = AmazonAPI(aws_key=os.environ['AMAZON_ACCESS_KEY'],
                   aws_secret=os.environ['AMAZON_SECRET_KEY'],
                   aws_associate_tag=os.environ['AMAZON_ASSOC_TAG'])


def search(item, category):
    # pdb.set_trace()
    products = amazon.search(Keywords=item, SearchIndex=category)
    return products


def search_limit(num, item, category):
    products = amazon.search_n(num, Keywords=item, SearchIndex=category)
    return products


def convert_list(items):
    item_list = []
    for item in items:
        item_list.append(item)
    return item_list


def print_items(items):
    for i, item in enumerate(items):
        print i, item.sales_rank, item.title


def lookup(item):
    product = amazon.lookup(ItemId=item)
    return product


def get_similar(item):
    products = amazon.similarity_lookup(ItemId=item)
    return products