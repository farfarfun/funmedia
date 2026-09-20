_douyin = ["douyin", "dy"]
_tiktok = ["tiktok", "tk"]
_weibo = ["weibo", "wb"]
_twitter = ["twitter", "x"]

# youtube/instagram/bilibili/twitch/neteasy_music/little_red_book were
# declared here but have no funmedia/apps/<platform>/ implementation --
# see farfarfun/todo-list#155. Removed rather than left as dead entries
# that silently fail to resolve as a CLI command.
__all__ = [
    "_douyin",
    "_tiktok",
    "_weibo",
    "_twitter",
]
