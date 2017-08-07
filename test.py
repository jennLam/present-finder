from amazon.api import AmazonAPI
import os

amazon = AmazonAPI(aws_key=os.environ['AMAZON_ACCESS_KEY'],
                   aws_secret=os.environ['AMAZON_SECRET_KEY'],
                   aws_associate_tag=os.environ['AMAZON_ASSOC_TAG'])
