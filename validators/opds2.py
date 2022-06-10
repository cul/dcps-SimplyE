import logging
import re
import requests
import sys

from webpub_manifest_parser.core import ManifestParser, ManifestParserResult
from webpub_manifest_parser.opds2 import OPDS2FeedParserFactory

def stream_manifest(stream_id, encoding="utf-8"):
    url_pattern = re.compile('^https?://*', re.IGNORECASE)
    if (url_pattern.match(stream_id)):
        response = requests.get(stream_id, stream=True)
        return response.raw
    else:
        return open(stream_id, "r", encoding="utf-8")

def parsing_errors(manifest_stream, log_level=logging.WARNING):
    # logging.root.level = logging.DEBUG
    logging.getLogger("webpub_manifest_parser.opds2").level = log_level

    parser_factory = OPDS2FeedParserFactory()
    parser = parser_factory.create()

    return parser.parse_stream(manifest_stream).errors

def validate(stream_id, encoding="utf-8", log_level=logging.WARNING):
    return len(parsing_errors(stream_manifest(stream_id, encoding), log_level)) == 0

def main():
    validate(sys.argv[1], log_level=logging.WARNING)
    quit()

if __name__ == "__main__":
    main()
