# Scrapy settings for vazylive project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from shutil import which
import requests
import random


BOT_NAME = "vazylive"
SPIDER_MODULES = ["vazylive.spiders"]
NEWSPIDER_MODULE = "vazylive.spiders"

SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('chromedriver')
# SELENIUM_DRIVER_ARGUMENTS = ['-headless']  # '--headless' if using chrome instead of firefox
SELENIUM_DRIVER_ARGUMENTS = []

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "vazylive (+http://www.yourdomain.com)"
excluded_useragents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 Safari/537.31",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36"
]

data = requests.get("https://raw.githubusercontent.com/tamimibrahim17/List-of-user-agents/master/Chrome.txt").content
data = str(data).split('\\n')

user_agents = [ua for ua in data[3:len(data) - 1] if ua not in excluded_useragents]
USER_AGENTS = user_agents

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 200
DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS_PER_DOMAIN = 1
RANDOMIZE_DOWNLOAD_DELAY = False

# CENTRIS
# CONCURRENT_REQUESTS = 200
# # DOWNLOAD_DELAY_RANGE = (2, 5)
# CONCURRENT_REQUESTS_PER_DOMAIN = 1
# RANDOMIZE_DOWNLOAD_DELAY = False

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    # "Accept-Language": "'en-US,en;q=0.9'",
    "User-Agent": random.choice(USER_AGENTS),
    "Referer": "",  # Will be dynamically set in the spider
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    "scrapy.spidermiddlewares.httperror.HttpErrorMiddleware": 50,
    "scrapy.spidermiddlewares.offsite.OffsiteMiddleware": 51,
    "scrapy.spidermiddlewares.referer.RefererMiddleware": 52,
    "scrapy.spidermiddlewares.urllength.UrlLengthMiddleware": 53,
    "scrapy.spidermiddlewares.depth.DepthMiddleware": 54,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 91,
    'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 92,
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 93,
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 94,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 95,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 96,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 97,
    'scrapy.downloadermiddlewares.stats.DownloaderStats': 98,
    'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 99,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 100,
    'scrapy_selenium.SeleniumMiddleware': 101
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'vazylive.pipelines.StreetAddressWriterPipeline': 100,
    # 'vazylive.pipelines.MongoDBPipeline': 300,
    # 'vazylive.pipelines.vazylivePipeline': 400,
    # 'vazylive.pipelines.JsonWriterPipeline': 500,
    # 'vazylive.pipelines.CsvWriterPipeline': 600,
}
MONGO_URI = "mongodb+srv://vlive:XgbjYqoVHayH38Nb@vlive.nqxve9o.mongodb.net/vlive?retryWrites=true&w=majority"
MONGO_DATABASE = 'vlive'

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5.0
AUTOTHROTTLE_MAX_DELAY = 60.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.5
AUTOTHROTTLE_DEBUG = False


# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [301, 302]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DUPEFILTER_DEBUG = True
ROTATING_PROXY_ENABLED = False
# LOG_ENABLED = False

