M = {
    # --- 시스템 로그 ---
    "LOG_BOT_READY": "Logged in as {user} (ID: {user_id})",
    "LOG_TASK_START": "[Task] Running SEC check loop...",
    "LOG_TASK_NO_CHANNEL": "[Task] Could not find dedicated channel {channel_id} for ticker {ticker}",
    "LOG_TASK_ERR_CHECK": "[Task] Error checking ticker {ticker}: {err}",
    "LOG_SEC_ERR_FETCH": "[sec_checker] ERROR fetching submissions for {ticker}: {err}",
    "LOG_SEC_ERR_CIK": "[sec_checker] ERROR getting CIK for {ticker}: {err}",
    "LOG_SEC_SAVED": "[sec_checker] Saved new filing {access_no} for {ticker}",
    "LOG_SEC_ERR_SAVE": "[sec_checker] ERROR saving filing {access_no} for {ticker}: {err}",
    "LOG_MAIN_NO_TOKEN": "에러: .env 파일에 DISCORD_TOKEN이 설정되지 않았습니다.",
    "LOG_MAIN_START": "디스코드 봇을 시작합니다...",

    # --- 디스코드 UI (Embed) ---
    "EMBED_NEW_FILING_TITLE": "새로운 SEC 공시 알림: {ticker} ({form_type})",
    "EMBED_NEW_FILING_DESC": "{ticker}의 새로운 {form_type} 공시가 등록되었습니다.",
    "EMBED_FIELD_DATE": "공시일(Filing Date)",
    "EMBED_FIELD_ACC_NO": "문서 번호(Accession No)",
    "EMBED_FIELD_ACCEPTED": "접수 일시(Accepted At)",
    "EMBED_VALUE_NA": "N/A",
    "MENTION_NEW_FILING": "@here 새로운 공시가 등록되었습니다!",
    
    # --- 디스코드 방 설정 상수 ---
    "CATEGORY_NAME": "SEC 알림",

    # --- 명령어 응답 ---
    "CMD_WARN_CHAT_DISABLED": "{mention}, 현재 방에서는 채팅을 칠 수 없어요.",
    "CMD_ERR_INVALID_TICKER": "❌ `{ticker}` 종목은 SEC 데이터베이스에 등록되어 있지 않거나 잘못된 티커입니다. 다시 확인해 주세요.",
    "CMD_SUB_SUCCESS": "✅ `{ticker}` 종목의 알림을 구독했습니다! ({channel_mention} 채널에서 알림 수신)",
    "CMD_SUB_ALREADY": "⚠️ 이미 `{ticker}` 종목의 알림을 구독 중입니다. ({channel_mention})",
    "CMD_UNSUB_SUCCESS": "✅ `{ticker}` 종목의 알림 구독을 취소했습니다. 해당 종목 채널에서 제외되었습니다.",
    "CMD_UNSUB_NOT_SUBBED": "⚠️ `{ticker}` 종목을 구독 중이지 않습니다.",
    "CMD_LIST_RESULT": "📄 현재 구독 목록: {ticker_list}",
    "CMD_LIST_EMPTY": "📄 현재 구독 중인 종목이 없습니다.",

    # --- 테스트 명령어 응답 ---
    "CMD_TEST_NO_ROOM": "⚠️ `{ticker}` 종목의 알림방이 존재하지 않습니다. 누군가 구독해야 방이 생성됩니다.",
    "CMD_TEST_NO_CHANNEL": "⚠️ `{ticker}` 종목의 채널을 찾을 수 없습니다.",
    "CMD_TEST_EMBED_TITLE": "새로운 SEC 공시 알림: {ticker} (8-K 테스트)",
    "CMD_TEST_EMBED_DESC": "{ticker}의 새로운 8-K 공시가 등록되었습니다. (이것은 테스트 알림입니다)",
    "CMD_TEST_MENTION": "@here 🔔 [테스트] 새로운 공시가 등록되었습니다!",
    "CMD_TEST_SUCCESS": "✅ `{ticker}` 종목 방에 테스트 공시 알림을 전송했습니다.",
}
