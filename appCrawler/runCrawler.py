import sys,os
import json,string,logging
import traceback
from importlib import import_module
from scrapy.utils.spider import iter_spider_classes
from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError
from scrapy import signals
from twisted.internet import reactor
from scrapy.crawler import Crawler,CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings
import scrapy

logger = logging.getLogger(__name__)

def __import__file(spidername):
	curdir,curfile = os.path.split(os.path.abspath(__file__))
	print (curdir)
	abspath = os.path.abspath(curdir + "/spiders/" + spidername + ".py")
	if not os.path.exists(abspath):
		raise ValueError("Has no such spider file:%s" % (abspath))
	dirname, file = os.path.split(abspath)
	fname, fext = os.path.splitext(file)
	print (dirname, file)
	logging.info(dirname)

	try:
		module = import_module("spiders."+fname)
		return module
	except Exception as e:
		traceback.print_exc()


def run(args):
	print (args)
	if len(args) != 1:
		raise UsageError()
	scrapy.utils.log.configure_logging()
	spidername = args[0]
	spider_module = __import__file(spidername)
	sp_classes = list(iter_spider_classes(spider_module))
	if not sp_classes:
		raise UsageError("No spider found : %s\n" % spidername)
	spidercls = sp_classes.pop()

	settings = get_project_settings()
	process = CrawlerProcess(settings=settings)
	process.crawl(spidercls)
	process.start()

run(sys.argv[1:])
