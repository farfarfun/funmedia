import pytest
from funmedia.apps.tiktok.model import UserPost
from funmedia.apps.tiktok.filter import UserPostFilter
from funmedia.apps.tiktok.crawler import TiktokCrawler
from funmedia.utils.conf_manager import TestConfigManager


@pytest.fixture
def cookie_fixture():
    return TestConfigManager.get_test_config("tiktok")


@pytest.mark.asyncio
async def test_crawler_by_secUid(cookie_fixture):
    async with TiktokCrawler(cookie_fixture) as crawler:
        params = UserPost(
            cursor=0,
            count=5,
            secUid="MS4wLjABAAAAREbjjYuEFoUJN86G9f2byGC_LSOTz4N7BGdreT_8Cro-NkzZYf_nxpDpLp9R6ElJ",
        )
        response = await crawler.fetch_user_post(params)
        assert response, "Failed to fetch user post"

        video = UserPostFilter(response)
        video_id = video.aweme_id
        assert video_id, "Failed to extract video ID"
