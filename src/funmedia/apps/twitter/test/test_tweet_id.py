import pytest
from funmedia.apps.twitter.utils import TweetIdFetcher
from funmedia.exceptions.api_exceptions import (
    APINotFoundError,
)


class FakeResponse:
    text = "https://twitter.com/example/status/1777291676568166526"

    def raise_for_status(self):
        pass


class FakeClient:
    def __init__(self, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def get(self, *args, **kwargs):
        return FakeResponse()


@pytest.mark.asyncio
class TestTweetIdFetcher:
    async def test_get_tweet_id(self, monkeypatch):
        monkeypatch.setattr(
            "funmedia.apps.twitter.utils.httpx.AsyncHTTPTransport",
            lambda **kwargs: None,
        )
        monkeypatch.setattr(
            "funmedia.apps.twitter.utils.httpx.AsyncClient", FakeClient
        )
        tweet_link = "https://twitter.com/realDonaldTrump/status/1265255835124539392"
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = "https://twitter.com/realDonaldTrump/status/1265255835124539392/"
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = (
            "https://twitter.com/realDonaldTrump/status/1265255835124539392/?test=123"
        )
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = (
            "https://twitter.com/realDonaldTrump/status/1265255835124539392/%$#"
        )
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = (
            "https://www.twitter.com/realDonaldTrump/status/1265255835124539392"
        )
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = "https://www.twitter.com/realDonaldTrump/status/1265255835124539392?test=123"
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = (
            "https://www.twitter.com/realDonaldTrump/status/1265255835124539392/"
        )
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = "https://www.twitter.com/realDonaldTrump/status/1265255835124539392/?test=123"
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = (
            "https://www.twitter.com/realDonaldTrump/status/1265255835124539392/%$#"
        )
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = "twitter.com/realDonaldTrump/status/1265255835124539392"
        with pytest.raises(APINotFoundError):
            await TweetIdFetcher.get_tweet_id(tweet_link)

        tweet_link = "https://t.co/1dBHtrG72J"
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1777291676568166526"
