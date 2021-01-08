# -*- coding: utf-8 -*-
import sys,os
import json,string,logging
import traceback
from importlib import import_module
from scrapy.utils.spider import iter_spider_classes
from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError


class Command(ScrapyCommand):
	requires_project = True
	def syntax(self):
		return "<spidername>"
	def short_desc(self):
		return "Run a self-contained spider"
	def run(self, args, opts):
		if len(args) != 1:
			raise UsageError()
		spidername = args[0]
		spider_module = __import__file(spidername)
		sp_classes = list(iter_spider_classes(spider_module))
		if not sp_classes:
			raise UsageError("No spider found : %s\n" % spidername)
		spidercls = sp_classes.pop()

		self.crawler_process.crawl(spidercls, **opts.__dict__)
		self.crawler_process.start()
		if self.crawler_process.bootstrap_failed:
			self.exitcode = 1
