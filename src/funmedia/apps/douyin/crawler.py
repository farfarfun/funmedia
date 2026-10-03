import gzip
import traceback

from funmedia.crawlers.base_crawler import BaseCrawler, WebSocketCrawler
from funmedia.i18n.translator import _
from funmedia.log.logger import logger
from funmedia.utils.utils import BaseEndpointManager, mask_sensitive_url
from google.protobuf import json_format
from google.protobuf.message import DecodeError

from .api import DouyinAPIEndpoints as dyendpoint
from .model import (
    FollowingUserLive,
    LiveImFetch,
    LiveWebcast,
    LoginCheckQr,
    LoginGetQr,
    PostDetail,
    QueryUser,
    UserCollection,
    UserCollects,
    UserCollectsVideo,
    UserFollower,
    UserFollowing,
    UserLike,
    UserLive,
    UserLive2,
    UserMix,
    UserMusicCollection,
    UserPost,
    UserProfile,
)
from .proto.douyin_webcast_pb2 import (
    ChatMessage,
    CommonTextMessage,
    FansClubMessage,
    GiftMessage,
    LikeMessage,
    MatchAgainstScoreMessage,
    MemberMessage,
    PushFrame,
    Response,
    RoomMessage,
    RoomUserSeqMessage,
    SocialMessage,
    UpdateFanTicketMessage,
)
from .utils import (
    ABogusManager,
    ClientConfManager,
    TokenManager,
    XBogusManager,
)


class DouyinCrawler(BaseCrawler):
    def __init__(
        self,
        kwargs: dict = ...,
    ):
        # 需要与cli同步
        proxies = kwargs.get("proxies", {"http://": None, "https://": None})
        self.headers = kwargs.get("headers", {}) | {"Cookie": kwargs["cookie"]}
        if ClientConfManager.encryption() == "ab":
            self.bogus_manager = ABogusManager
        else:
            self.bogus_manager = XBogusManager
        super().__init__(proxies=proxies, crawler_headers=self.headers)

    async def fetch_user_profile(self, params: UserProfile):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_DETAIL,
            params.model_dump(),
        )
        logger.debug(_("用户信息接口地址：{0}").format(mask_sensitive_url(endpoint)))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_post(self, params: UserPost):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_POST,
            params.model_dump(),
        )
        logger.debug(_("主页作品接口地址：{0}").format(mask_sensitive_url(endpoint)))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_like(self, params: UserLike):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_FAVORITE_A,
            params.model_dump(),
        )
        logger.debug(
            _("主页喜欢作品接口地址：{0}").format(mask_sensitive_url(endpoint))
        )
        return await self._fetch_get_json(endpoint)

    async def fetch_user_collection(self, params: UserCollection):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_COLLECTION,
            params.model_dump(),
        )
        logger.debug(
            _("主页收藏作品接口地址：{0}").format(mask_sensitive_url(endpoint))
        )
        return await self._fetch_post_json(endpoint, params.model_dump())

    async def fetch_user_collects(self, params: UserCollects):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_COLLECTS,
            params.model_dump(),
        )
        logger.debug(_("收藏夹接口地址：{0}").format(mask_sensitive_url(endpoint)))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_collects_video(self, params: UserCollectsVideo):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_COLLECTS_VIDEO,
            params.model_dump(),
        )
        logger.debug(_("收藏夹作品接口地址：{0}").format(mask_sensitive_url(endpoint)))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_music_collection(self, params: UserMusicCollection):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_MUSIC_COLLECTION,
            params.model_dump(),
        )
        logger.debug(_("音乐收藏接口地址：{0}").format(mask_sensitive_url(endpoint)))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_mix(self, params: UserMix):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.MIX_AWEME,
            params.model_dump(),
        )
        logger.debug(_("合集作品接口地址：{0}").format(mask_sensitive_url(endpoint)))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_detail(self, params: PostDetail):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.POST_DETAIL,
            params.model_dump(),
        )
        logger.debug(_("作品详情接口地址：{0}").format(mask_sensitive_url(endpoint)))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_comment(self, params: PostDetail):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.POST_COMMENT,
            params.model_dump(),
        )
        logger.debug(_("作品评论接口地址：{0}").format(mask_sensitive_url(endpoint)))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_feed(self, params: PostDetail):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.TAB_FEED,
            params.model_dump(),
        )
        logger.debug(
            _("首页推荐作品接口地址：{0}").format(mask_sensitive_url(endpoint))
        )
        return await self._fetch_get_json(endpoint)

    async def fetch_follow_feed(self, params: PostDetail):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.FOLLOW_FEED,
            params.model_dump(),
        )
        logger.debug(_("关注作品接口地址：{0}").format(mask_sensitive_url(endpoint)))
        return await self._fetch_get_json(endpoint)

    async def fetch_friend_feed(self, params: PostDetail):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.FRIEND_FEED,
            params.model_dump(),
        )
        logger.debug(_("朋友作品接口地址：{0}").format(mask_sensitive_url(endpoint)))
        return await self._fetch_post_json(endpoint)

    async def fetch_post_related(self, params: PostDetail):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.POST_RELATED,
            params.model_dump(),
        )
        logger.debug(
            _("相关推荐作品接口地址：{0}").format(mask_sensitive_url(endpoint))
        )
        return await self._fetch_get_json(endpoint)

    async def fetch_live(self, params: UserLive):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.LIVE_INFO,
            params.model_dump(),
        )
        logger.debug(_("直播接口地址：{0}").format(mask_sensitive_url(endpoint)))
        return await self._fetch_get_json(endpoint)

    async def fetch_live_room_id(self, params: UserLive2):
        original_headers = self.aclient.headers.copy()
        try:
            # 避免invalid session
            self.aclient.headers.update({"Cookie": ""})
            endpoint = self.bogus_manager.model_2_endpoint(
                self.headers.get("User-Agent"),
                dyendpoint.LIVE_INFO_ROOM_ID,
                params.model_dump(),
            )
            logger.debug(
                _("直播接口地址（room_id）：{0}").format(mask_sensitive_url(endpoint))
            )
            return await self._fetch_get_json(endpoint)
        finally:
            self.aclient.headers = original_headers

    async def fetch_following_live(self, params: FollowingUserLive):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.FOLLOW_USER_LIVE,
            params.model_dump(),
        )
        logger.debug(
            _("关注用户直播接口地址：{0}").format(mask_sensitive_url(endpoint))
        )
        return await self._fetch_get_json(endpoint)

    async def fetch_locate_post(self, params: UserPost):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.LOCATE_POST,
            params.model_dump(),
        )
        logger.debug(
            _("定位上一次作品接口地址：{0}").format(mask_sensitive_url(endpoint))
        )
        return await self._fetch_get_json(endpoint)

    async def fetch_login_qrcode(self, parms: LoginGetQr):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.SSO_LOGIN_GET_QR,
            parms.model_dump(),
        )
        logger.debug(
            _("SSO获取二维码接口地址：{0}").format(mask_sensitive_url(endpoint))
        )
        return await self._fetch_get_json(endpoint)

    async def fetch_check_qrcode(self, parms: LoginCheckQr):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.SSO_LOGIN_CHECK_QR,
            parms.model_dump(),
        )
        logger.debug(
            _("SSO检查扫码状态接口地址：{0}").format(mask_sensitive_url(endpoint))
        )
        return await self._fetch_response(endpoint)

    async def fetch_check_login(self, parms: LoginCheckQr):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.SSO_LOGIN_CHECK_LOGIN,
            parms.model_dump(),
        )
        logger.debug(
            _("SSO检查登录状态接口地址：{0}").format(mask_sensitive_url(endpoint))
        )
        return await self._fetch_get_json(endpoint)

    async def fetch_user_following(self, params: UserFollowing):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_FOLLOWING,
            params.model_dump(),
        )
        logger.debug(
            _("用户关注列表接口地址：{0}").format(mask_sensitive_url(endpoint))
        )
        return await self._fetch_get_json(endpoint)

    async def fetch_user_follower(self, params: UserFollower):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_FOLLOWER,
            params.model_dump(),
        )
        logger.debug(
            _("用户粉丝列表接口地址：{0}").format(mask_sensitive_url(endpoint))
        )
        return await self._fetch_get_json(endpoint)

    async def fetch_live_im_fetch(self, params: LiveImFetch):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.LIVE_IM_FETCH,
            params.model_dump(),
        )
        logger.debug(
            _("直播弹幕初始化接口地址：{0}").format(mask_sensitive_url(endpoint))
        )
        return await self._fetch_get_json(endpoint)

    async def fetch_query_user(self, params: QueryUser):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.QUERY_USER,
            params.model_dump(),
        )
        logger.debug(_("查询用户接口地址：{0}").format(mask_sensitive_url(endpoint)))
        return await self._fetch_get_json(endpoint)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class DouyinWebSocketCrawler(WebSocketCrawler):
    def __init__(self, kwargs: dict = ..., callbacks: dict = None):
        # 需要与cli同步
        self.headers = kwargs.get("headers", {}) | {
            "Cookie": f"ttwid={TokenManager.gen_ttwid()};"
        }
        self.callbacks = callbacks or {}
        self.timeout = kwargs.get("timeout", 10)
        super().__init__(
            wss_headers=self.headers, callbacks=self.callbacks, timeout=self.timeout
        )

    async def fetch_live_danmaku(self, params: LiveWebcast):
        endpoint = BaseEndpointManager.model_2_endpoint(
            dyendpoint.LIVE_IM_WSS,
            params.model_dump(),
        )
        logger.debug(_("直播弹幕接口地址：{0}").format(mask_sensitive_url(endpoint)))
        await self.connect_websocket(endpoint)
        return await self.receive_messages()

    async def handle_wss_message(self, message: bytes):
        """
        处理 WebSocket 消息

        Args:
            message (bytes): WebSocket 消息的字节数据
        """
        # 协议解析边界：PushFrame/gzip/Response 任一步失败都说明消息本身损坏或不兼容，
        # 只记录具体异常类型与上下文，丢弃该条消息，不影响后续消息的接收。
        try:
            wss_package = PushFrame()
            wss_package.ParseFromString(message)
            log_id = wss_package.logId
            decompressed = gzip.decompress(wss_package.payload)
            payload_package = Response()
            payload_package.ParseFromString(decompressed)
        except DecodeError as exc:
            logger.error(
                _("解析 WebSocket 消息失败（protobuf 解码错误）：{0}").format(exc)
            )
            return
        except OSError as exc:
            logger.error(_("解析 WebSocket 消息失败（gzip 解压错误）：{0}").format(exc))
            return

        # 发送 ack 包：网络边界，失败时记录并继续处理已收到的消息
        if payload_package.needAck:
            try:
                await self.send_ack(log_id, payload_package.internalExt)
            except Exception as exc:
                logger.error(_("发送 ack 包失败：{0}").format(exc))

        # 处理每个消息
        for msg in payload_package.messagesList:
            method = msg.method
            payload = msg.payload

            # 回调执行边界：回调由调用方注入，可能是任意用户代码，
            # 单个回调异常不应中断其余消息/回调的处理，但需要记录是哪个回调失败。
            if method in self.callbacks:
                try:
                    await self.callbacks[method](data=payload)
                except Exception as exc:
                    logger.error(
                        _("回调函数处理消息失败：method={0}，异常：{1}").format(
                            method, exc
                        )
                    )
                    logger.debug(traceback.format_exc())
            else:
                logger.warning(_("未找到对应的回调函数处理消息：{0}").format(method))

    async def send_ack(self, log_id: str, internal_ext: str):
        """
        发送 ack 包

        Args:
            log_id: 日志ID
            internal_ext: 内部扩展信息
        """
        ack = PushFrame()
        ack.logId = log_id
        ack.payloadType = internal_ext
        data = ack.SerializeToString()
        logger.debug(_("[SendAck] [💓发送ack包]"))
        await self.websocket.send(data)

    async def send_ping(self):
        """
        发送 ping 包
        """
        ping = PushFrame()
        ping.payloadType = "hb"
        data = ping.SerializeToString()
        logger.debug(_("[SendPing] [📤发送ping包]"))
        await self.websocket.ping(data)

    async def on_message(self, message):
        await self.handle_wss_message(message)

    async def on_error(self, message):
        return await super().on_error(message)

    async def on_close(self, message):
        return await super().on_close(message)

    async def on_open(self):
        return await super().on_open()

    # 定义所有的回调消息函数
    @classmethod
    async def WebcastRoomMessage(cls, data: bytes):
        roomMessage = RoomMessage()
        roomMessage.ParseFromString(data)
        data_dict = json_format.MessageToDict(
            roomMessage, preserving_proto_field_name=True
        )
        logger.info(
            _("[WebcastRoomMessage] [🏠房间消息] ｜ {0}").format(data_dict.get("room"))
        )
        return data_dict

    @classmethod
    async def WebcastLikeMessage(cls, data: bytes):
        likeMessage = LikeMessage()
        likeMessage.ParseFromString(data)
        data_dict = json_format.MessageToDict(
            likeMessage, preserving_proto_field_name=True
        )
        logger.info(
            "[WebcastLikeMessage] [👍点赞消息] ｜ "
            + "[用户Id：{0}] [当前用户点赞：{1}] [总点赞：{2}]".format(
                data_dict.get("user").get("id"),
                data_dict.get("count"),
                data_dict.get("total"),
            )
        )
        return data_dict

    @classmethod
    async def WebcastMemberMessage(cls, data: bytes):
        memberMessage = MemberMessage()
        memberMessage.ParseFromString(data)
        data_dict = json_format.MessageToDict(
            memberMessage, preserving_proto_field_name=True
        )
        logger.info(
            f"[WebcastMemberMessage] [🚺观众加入消息] ｜ [用户Id：{data_dict.get('user').get('id')} 用户名：{data_dict.get('user').get('nickname')}]"
        )
        return data_dict

    @classmethod
    async def WebcastChatMessage(cls, data: bytes):
        chatMessage = ChatMessage()
        chatMessage.ParseFromString(data)
        data_dict = json_format.MessageToDict(
            chatMessage, preserving_proto_field_name=True
        )
        logger.info(
            _("[WebcastChatMessage] [💬聊天消息] ｜ {0}").format(
                data_dict.get("content")
            )
        )
        return data

    @classmethod
    async def WebcastGiftMessage(cls, data: bytes):
        giftMessage = GiftMessage()
        giftMessage.ParseFromString(data)
        data_dict = json_format.MessageToDict(
            giftMessage, preserving_proto_field_name=True
        )
        logger.info(
            _("[WebcastGiftMessage] [🎁礼物消息] | [{0}]").format(
                data_dict.get("common").get("describe")
            )
        )
        return data_dict

    @classmethod
    async def WebcastSocialMessage(cls, data: bytes):
        socialMessage = SocialMessage()
        socialMessage.ParseFromString(data)
        data_dict = json_format.MessageToDict(
            socialMessage, preserving_proto_field_name=True
        )
        logger.info(
            _("[WebcastSocialMessage] [➕用户关注消息] | [{0}]").format(
                data_dict.get("user").get("id")
            )
        )
        return data_dict

    @classmethod
    async def WebcastRoomUserSeqMessage(cls, data: bytes):
        roomUserSeqMessage = RoomUserSeqMessage()
        roomUserSeqMessage.ParseFromString(data)
        data_dict = json_format.MessageToDict(
            roomUserSeqMessage, preserving_proto_field_name=True
        )

        logger.info(
            _("[WebcastRoomUserSeqMessage] [👥在线观众排行榜] | [{0} {1} {2}]").format(
                data_dict.get("ranksList")[0].get("user").get("id"),
                data_dict.get("ranksList")[1].get("user").get("id"),
                data_dict.get("ranksList")[2].get("user").get("id"),
            )
        )
        return data_dict

    @classmethod
    async def WebcastUpdateFanTicketMessage(cls, data: bytes):
        updateFanTicketMessage = UpdateFanTicketMessage()
        updateFanTicketMessage.ParseFromString(data)
        data_dict = json_format.MessageToDict(
            updateFanTicketMessage, preserving_proto_field_name=True
        )

        logger.info(
            _("[WebcastUpdateFanTicketMessage] [🎟️粉丝票更新消息] | [{0}]").format(
                data_dict.get("roomFanTicketCount")
            )
        )
        return data_dict

    @classmethod
    async def WebcastCommonTextMessage(cls, data: bytes):
        commonTextMessage = CommonTextMessage()
        commonTextMessage.ParseFromString(data)
        data_dict = json_format.MessageToDict(
            commonTextMessage, preserving_proto_field_name=True
        )

        logger.info(
            _("[WebcastCommonTextMessage] [📝文本消息] | [{0}]").format(data_dict)
        )
        return data_dict

    @classmethod
    async def WebcastMatchAgainstScoreMessage(cls, data: bytes):
        matchAgainstScoreMessage = MatchAgainstScoreMessage()
        matchAgainstScoreMessage.ParseFromString(data)
        data_dict = json_format.MessageToDict(
            matchAgainstScoreMessage, preserving_proto_field_name=True
        )

        logger.info(
            _("[WebcastMatchAgainstScoreMessage] [🏆对战积分消息] | [{0}]").format(
                data_dict
            )
        )
        return data_dict

    @classmethod
    async def WebcastFansclubMessage(cls, data: bytes):
        fansClubMessage = FansClubMessage()
        fansClubMessage.ParseFromString(data)
        data_dict = json_format.MessageToDict(
            fansClubMessage, preserving_proto_field_name=True
        )

        logger.info(
            _("[WebcastFansclubMessage] [🎉粉丝团消息] | [{0}]").format(
                data_dict.get("content")
            )
        )
        return data_dict

    async def __aenter__(self):
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)
