#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://lovetypes.tw"
ADSENSE_ACCOUNT = "ca-pub-4093856660317740"
CONTACT_EMAIL = "contact@lovetypes.tw"
UPDATED = "2026-06-05"
ASSET_VERSION = "20260611-funnel-observe"
CSS_ASSET = f"/shared-{ASSET_VERSION}.css"
INTERACTIONS_ASSET = f"/site-interactions-{ASSET_VERSION}.js"
AFFILIATE_ASSET = f"/deferred-external-{ASSET_VERSION}.js"
QUIZ_DATA_LANGS = ("zh", "en", "ja", "ko", "es")
QUIZ_DATA_ASSETS = {lang: f"/quiz-data-{lang}-{ASSET_VERSION}.js" for lang in QUIZ_DATA_LANGS}
STATIC_SOURCE_DIR = ROOT / "tools" / "static"
STATIC_ASSET_SOURCES = {
    "shared.css": CSS_ASSET,
    "site-interactions.js": INTERACTIONS_ASSET,
    "deferred-external.js": AFFILIATE_ASSET,
}


FONT_CSS = ""


IMAGE_DIMENSIONS = {
    "/assets/lovetypes/backgrounds/guardian-garden-mobile.webp": (900, 506),
    "/assets/lovetypes/backgrounds/guardian-garden.webp": (1920, 1080),
    "/assets/lovetypes/share/claire-og.jpg": (1200, 630),
    "/assets/lovetypes/share/dora-og.jpg": (1200, 630),
    "/assets/lovetypes/share/guide-toolkit-og.jpg": (1200, 630),
    "/assets/lovetypes/share/iris-og.jpg": (1200, 630),
    "/assets/lovetypes/share/noah-og.jpg": (1200, 630),
    "/assets/lovetypes/share/vivian-og.jpg": (1200, 630),
    "/assets/lovetypes/share/claire-story-en.webp": (1080, 1920),
    "/assets/lovetypes/share/claire-story-es.webp": (1080, 1920),
    "/assets/lovetypes/share/claire-story-ja.webp": (1080, 1920),
    "/assets/lovetypes/share/claire-story-ko.webp": (1080, 1920),
    "/assets/lovetypes/share/claire-story-zh.webp": (1080, 1920),
    "/assets/lovetypes/share/dora-story-en.webp": (1080, 1920),
    "/assets/lovetypes/share/dora-story-es.webp": (1080, 1920),
    "/assets/lovetypes/share/dora-story-ja.webp": (1080, 1920),
    "/assets/lovetypes/share/dora-story-ko.webp": (1080, 1920),
    "/assets/lovetypes/share/dora-story-zh.webp": (1080, 1920),
    "/assets/lovetypes/share/iris-story-en.webp": (1080, 1920),
    "/assets/lovetypes/share/iris-story-es.webp": (1080, 1920),
    "/assets/lovetypes/share/iris-story-ja.webp": (1080, 1920),
    "/assets/lovetypes/share/iris-story-ko.webp": (1080, 1920),
    "/assets/lovetypes/share/iris-story-zh.webp": (1080, 1920),
    "/assets/lovetypes/share/noah-story-en.webp": (1080, 1920),
    "/assets/lovetypes/share/noah-story-es.webp": (1080, 1920),
    "/assets/lovetypes/share/noah-story-ja.webp": (1080, 1920),
    "/assets/lovetypes/share/noah-story-ko.webp": (1080, 1920),
    "/assets/lovetypes/share/noah-story-zh.webp": (1080, 1920),
    "/assets/lovetypes/share/vivian-story-en.webp": (1080, 1920),
    "/assets/lovetypes/share/vivian-story-es.webp": (1080, 1920),
    "/assets/lovetypes/share/vivian-story-ja.webp": (1080, 1920),
    "/assets/lovetypes/share/vivian-story-ko.webp": (1080, 1920),
    "/assets/lovetypes/share/vivian-story-zh.webp": (1080, 1920),
    "/assets/lovetypes/guardians/claire.webp": (720, 1007),
    "/assets/lovetypes/guardians/cards/claire-card.webp": (400, 560),
    "/assets/lovetypes/guardians/cards/dora-card.webp": (409, 560),
    "/assets/lovetypes/guardians/cards/iris-card.webp": (528, 560),
    "/assets/lovetypes/guardians/cards/noah-card.webp": (560, 538),
    "/assets/lovetypes/guardians/cards/vivian-card.webp": (450, 560),
    "/assets/lovetypes/guardians/dora.webp": (736, 1007),
    "/assets/lovetypes/guardians/iris.webp": (966, 1024),
    "/assets/lovetypes/guardians/noah.webp": (1066, 1024),
    "/assets/lovetypes/guardians/vivian.webp": (823, 1024),
    "/assets/lovetypes/props/affirmation-feather-pen.webp": (285, 235),
    "/assets/lovetypes/props/gifts-ribboned-gift-box.webp": (215, 190),
    "/assets/lovetypes/props/quality-time-lantern.webp": (100, 195),
    "/assets/lovetypes/props/service-tool-pouch.webp": (250, 135),
    "/assets/lovetypes/props/touch-golden-hug-glow.webp": (305, 180),
    "/luna-yoga-music/images/feminine.webp": (1536, 1024),
    "/luna-yoga-music/images/healing.webp": (1536, 1024),
    "/luna-yoga-music/images/hero.webp": (881, 881),
    "/luna-yoga-music/images/icon.webp": (1024, 1024),
    "/luna-yoga-music/images/morning.webp": (1536, 1024),
    "/luna-yoga-music/images/sleep.webp": (1536, 1024),
    "/luna-yoga-music/images/stress.webp": (1536, 1024),
}


LANGS = {
    "zh": {
        "code": "zh-TW",
        "prefix": "",
        "name": "繁體中文",
        "brand": "LoveTypes 情感守護者宇宙",
        "tagline": "走進心語庭園，把愛之語測驗結果翻成聽得懂、做得到、能修復錯頻的關係練習。",
        "start": "開始認領儀式",
        "map": "地圖",
        "guides": "深度指南",
        "guardians": "守護者",
        "theory": "理論",
        "resources": "旅人補給",
        "about": "關於",
        "contact": "聯絡",
        "privacy": "隱私",
        "terms": "條款",
        "read": "閱讀指南",
        "learn_more": "了解更多",
        "practice": "今日練習",
        "skip_content": "跳到主要內容",
        "primary_nav": "主要導覽",
        "language_menu": "語言選單",
        "breadcrumb_label": "頁面路徑",
        "updated_label": "更新日期",
        "boundary": "內容邊界",
        "boundary_text": "LoveTypes 的守護者與心語庭園是自我理解與關係溝通的隱喻工具，不提供心理諮商、醫療建議、法律建議或個別關係診斷。若你正面臨暴力、控制、創傷或高風險處境，請先離開高風險場域，尋求可信任的人與專業支援。",
        "home_title": "LoveTypes｜五種愛之語測驗與關係溝通指南",
        "home_desc": "LoveTypes 將五種愛之語化為五位情感守護者，帶你在心語庭園中認領被愛入口、辨認錯頻，並練習伴侶溝通與關係修復。",
        "guide_index_title": "LoveTypes 守護者指南｜把愛之語帶回真實關係",
        "guide_index_desc": "閱讀心語庭園裡的五種愛之語指南：測驗結果、吵架修復、遠距陪伴、界線、安全感與伴侶對話練習。",
        "trust_intro": "LoveTypes 是一座以五種愛之語為地圖的心語庭園，透過五位情感守護者、情境測驗與實作指南，幫助你辨認被愛需求、錯頻傷口與可說出口的下一步。",
        "resources_desc": "旅人補給整理心語庭園的指南入口、五位守護者頁面、Luna 音樂、愛之語理論與實作練習，讓你快速找到下一盞燈。",
        "contact_desc": "聯絡 LoveTypes 團隊，回報內容修正、隱私疑問、合作需求，或指出心語庭園中需要修復的頁面。",
        "privacy_desc": f"LoveTypes 隱私政策，說明資料使用、第三方服務與聯絡方式。更新日期 {UPDATED}。",
        "terms_desc": f"LoveTypes 使用條款，說明內容邊界、智慧財產、免責與網站使用規則。更新日期 {UPDATED}。",
        "luna_title": "Luna Yoga Music｜關係反思與放鬆音樂",
        "luna_desc": "Luna Yoga Music 提供適合書寫、放鬆與關係反思的安定音樂，像心語庭園夜晚的一盞低光。",
    },
    "en": {
        "code": "en",
        "prefix": "en",
        "name": "English",
        "brand": "LoveTypes Emotion Guardians",
        "tagline": "Step into the Heart Garden and translate your love-language result into clear words, small actions, boundaries, and repair for emotional misfrequency.",
        "start": "Begin recognition",
        "map": "Map",
        "guides": "Guides",
        "guardians": "Guardians",
        "theory": "Theory",
        "resources": "Resources",
        "about": "About",
        "contact": "Contact",
        "privacy": "Privacy",
        "terms": "Terms",
        "read": "Read guide",
        "learn_more": "Learn more",
        "practice": "Today practice",
        "skip_content": "Skip to content",
        "primary_nav": "Primary navigation",
        "language_menu": "Language menu",
        "breadcrumb_label": "Breadcrumb",
        "updated_label": "Updated",
        "boundary": "Editorial boundary",
        "boundary_text": "The LoveTypes guardians and Heart Garden are metaphor tools for self-reflection and relationship communication. They are not therapy, medical advice, legal advice, or a relationship diagnosis. If you are facing violence, coercive control, trauma, or urgent risk, seek trusted local and professional support first.",
        "home_title": "LoveTypes | Love Language Quiz and Relationship Guides",
        "home_desc": "LoveTypes turns the five love languages into emotion guardians, helping you enter the Heart Garden, name your loved doorway, spot misfrequency, and practice repair.",
        "guide_index_title": "LoveTypes Guardian Guides | Bring Love Languages Into Real Relationships",
        "guide_index_desc": "Explore Heart Garden guides for quiz results, conflict repair, long-distance presence, boundaries, emotional needs, and partner conversations.",
        "trust_intro": "LoveTypes is a Heart Garden mapped by the five love languages. Guardians, scenario prompts, and practical guides help you name needs, wounds, and next words.",
        "resources_desc": "Browse Heart Garden guide paths, guardian profiles, love-language theory notes, and practical exercises so you can find the next lamp on the path.",
        "contact_desc": "Contact LoveTypes for content corrections, privacy questions, partnership concerns, or pages in the Heart Garden that need repair.",
        "privacy_desc": f"LoveTypes privacy policy covering data use, third-party services, and contact options. Updated {UPDATED}.",
        "terms_desc": f"LoveTypes terms of use covering content boundaries, intellectual property, disclaimers, and site rules. Updated {UPDATED}.",
        "luna_title": "Luna Yoga Music | Calm Audio for Reflection",
        "luna_desc": "Luna Yoga Music offers calm companion audio for journaling, decompression, and relationship reflection, like a low lamp in the Heart Garden at night.",
    },
    "ja": {
        "code": "ja",
        "prefix": "ja",
        "name": "日本語",
        "brand": "LoveTypes 感情の守護者",
        "tagline": "心語の庭に入り、愛の言語の結果を、伝わる言葉・小さな行動・境界線・すれ違いの修復へ翻訳するガイド。",
        "start": "認領の儀式を始める",
        "map": "マップ",
        "guides": "ガイド",
        "guardians": "守護者",
        "theory": "理論",
        "resources": "リソース",
        "about": "このサイトについて",
        "contact": "連絡",
        "privacy": "プライバシー",
        "terms": "利用規約",
        "read": "ガイドを読む",
        "learn_more": "詳しく見る",
        "practice": "今日の練習",
        "skip_content": "本文へ移動",
        "primary_nav": "主要ナビゲーション",
        "language_menu": "言語メニュー",
        "breadcrumb_label": "パンくずリスト",
        "updated_label": "更新日",
        "boundary": "内容の範囲",
        "boundary_text": "LoveTypes の守護者と心語の庭は、自己理解と関係コミュニケーションのための比喩ツールです。心理療法、医療助言、法律助言、個別の関係診断ではありません。暴力、支配、トラウマ、緊急の危険がある場合は、まず信頼できる人や専門機関に相談してください。",
        "home_title": "LoveTypes｜愛の言語診断と関係コミュニケーションガイド",
        "home_desc": "LoveTypes は五つの愛の言語を五人の感情の守護者に変え、心語の庭で愛される入口、すれ違い、会話と修復の練習を見つけるガイドです。",
        "guide_index_title": "LoveTypes 守護者ガイド｜愛の言語を現実の関係へ",
        "guide_index_desc": "心語の庭のガイドで、診断結果、衝突後の修復、遠距離の在り方、境界線、安心感、パートナーとの会話を扱います。",
        "trust_intro": "LoveTypes は五つの愛の言語を地図にした心語の庭です。五人の感情の守護者、状況型の内省、実用的なガイドを通じて、愛される入口、すれ違いの傷、次に言える言葉を見つけます。",
        "resources_desc": "心語の庭のガイド入口、五人の守護者プロフィール、愛の言語の理論、実践練習をまとめ、次の灯りを見つけやすくします。",
        "contact_desc": "内容修正、プライバシー、提携、または心語の庭で修復が必要なページについて LoveTypes に連絡できます。",
        "privacy_desc": f"データ利用、第三者サービス、連絡方法を説明する LoveTypes プライバシーポリシー。更新日 {UPDATED}。",
        "terms_desc": f"内容の範囲、知的財産、免責、サイト利用ルールを説明する LoveTypes 利用規約。更新日 {UPDATED}。",
        "luna_title": "Luna Yoga Music｜内省のための静かな音楽",
        "luna_desc": "Luna Yoga Music は、日記、緊張をほどく時間、関係のふり返りに寄り添う静かな音楽です。心語の庭の夜にともる低い灯りのように。",
    },
    "ko": {
        "code": "ko",
        "prefix": "ko",
        "name": "한국어",
        "brand": "LoveTypes 감정 수호자",
        "tagline": "마음의 정원에 들어가 사랑의 언어 결과를 들리는 말, 작은 행동, 경계, 어긋남의 회복으로 번역하는 가이드.",
        "start": "인정 의식 시작하기",
        "map": "지도",
        "guides": "가이드",
        "guardians": "수호자",
        "theory": "이론",
        "resources": "자료",
        "about": "소개",
        "contact": "연락",
        "privacy": "개인정보",
        "terms": "이용약관",
        "read": "가이드 읽기",
        "learn_more": "더 알아보기",
        "practice": "오늘의 연습",
        "skip_content": "본문으로 이동",
        "primary_nav": "주요 탐색",
        "language_menu": "언어 메뉴",
        "breadcrumb_label": "이동 경로",
        "updated_label": "업데이트",
        "boundary": "콘텐츠 범위",
        "boundary_text": "LoveTypes의 수호자와 마음의 정원은 자기 이해와 관계 대화를 위한 은유적 도구입니다. 심리상담, 의료 조언, 법률 조언, 개별 관계 진단을 제공하지 않습니다. 폭력, 통제, 트라우마, 긴급 위험이 있다면 먼저 신뢰할 수 있는 사람과 전문 기관의 도움을 받으세요.",
        "home_title": "LoveTypes｜사랑의 언어 테스트와 관계 대화 가이드",
        "home_desc": "LoveTypes는 다섯 가지 사랑의 언어를 다섯 감정 수호자로 풀어내며, 마음의 정원에서 사랑받는 입구와 어긋남을 알아차리고 대화와 회복을 연습하게 돕습니다.",
        "guide_index_title": "LoveTypes 수호자 가이드｜사랑의 언어를 실제 관계로",
        "guide_index_desc": "마음의 정원 가이드에서 테스트 결과, 갈등 회복, 장거리의 존재감, 경계, 안전감, 파트너 대화를 다룹니다.",
        "trust_intro": "LoveTypes는 다섯 가지 사랑의 언어를 지도로 삼은 마음의 정원입니다. 다섯 감정 수호자, 상황형 성찰, 실용 가이드를 통해 사랑받는 욕구, 어긋남의 상처, 다음에 말할 수 있는 문장을 정리합니다.",
        "resources_desc": "마음의 정원 가이드 입구, 다섯 수호자 프로필, 사랑의 언어 이론, 실천 연습을 모아 다음 등불을 찾기 쉽게 합니다.",
        "contact_desc": "콘텐츠 수정, 개인정보 문의, 협업, 또는 마음의 정원에서 수리가 필요한 페이지를 LoveTypes에 알릴 수 있습니다.",
        "privacy_desc": f"데이터 사용, 제3자 서비스, 연락 방법을 설명하는 LoveTypes 개인정보 처리방침. 업데이트 {UPDATED}.",
        "terms_desc": f"콘텐츠 범위, 지식재산권, 면책, 사이트 이용 규칙을 설명하는 LoveTypes 이용약관. 업데이트 {UPDATED}.",
        "luna_title": "Luna Yoga Music｜성찰을 위한 차분한 음악",
        "luna_desc": "Luna Yoga Music은 기록, 긴장 완화, 관계 성찰에 어울리는 차분한 음악입니다. 밤의 마음의 정원에 켜진 낮은 등불처럼 함께합니다.",
    },
    "es": {
        "code": "es",
        "prefix": "es",
        "name": "Español",
        "brand": "LoveTypes Guardianas Emocionales",
        "tagline": "Entra al Jardín del Corazón y traduce tu resultado de lenguaje del amor en palabras claras, acciones pequeñas, límites y reparación del desajuste.",
        "start": "Iniciar reconocimiento",
        "map": "Mapa",
        "guides": "Guías",
        "guardians": "Guardianas",
        "theory": "Teoría",
        "resources": "Recursos",
        "about": "Acerca de",
        "contact": "Contacto",
        "privacy": "Privacidad",
        "terms": "Términos",
        "read": "Leer guía",
        "learn_more": "Ver más",
        "practice": "Práctica de hoy",
        "skip_content": "Saltar al contenido",
        "primary_nav": "Navegación principal",
        "language_menu": "Menú de idioma",
        "breadcrumb_label": "Ruta de navegación",
        "updated_label": "Actualización",
        "boundary": "Límite editorial",
        "boundary_text": "Las guardianas de LoveTypes y el Jardín del Corazón son herramientas metafóricas para la autorreflexión y la comunicación relacional. No ofrecen terapia, consejo médico, consejo legal ni diagnóstico individual. Si enfrentas violencia, control, trauma o riesgo urgente, busca primero apoyo profesional y personas de confianza.",
        "home_title": "LoveTypes | Test de lenguajes del amor y guías de relación",
        "home_desc": "LoveTypes convierte los cinco lenguajes del amor en guardianas emocionales para entrar al Jardín del Corazón, reconocer tu entrada al amor y practicar reparación.",
        "guide_index_title": "Guías de Guardianas LoveTypes | Lleva los lenguajes del amor a la vida real",
        "guide_index_desc": "Explora las guías del Jardín del Corazón sobre resultados, reparación de conflictos, presencia a distancia, límites, seguridad emocional y conversaciones de pareja.",
        "trust_intro": "LoveTypes es un Jardín del Corazón guiado por cinco lenguajes del amor. Sus guardianas, escenas y guías ayudan a nombrar necesidades, heridas y próximas palabras.",
        "resources_desc": "Encuentra entradas del Jardín del Corazón, perfiles de guardianas, teoría de lenguajes del amor y ejercicios prácticos para hallar la siguiente luz del camino.",
        "contact_desc": "Contacta a LoveTypes para correcciones de contenido, privacidad, colaboraciones o páginas del Jardín del Corazón que necesiten reparación.",
        "privacy_desc": f"Política de privacidad de LoveTypes sobre datos, servicios de terceros y contacto. Actualizada {UPDATED}.",
        "terms_desc": f"Términos de uso de LoveTypes sobre límites de contenido, propiedad intelectual, descargos y reglas del sitio. Actualizados {UPDATED}.",
        "luna_title": "Luna Yoga Music | Audio tranquilo para reflexionar",
        "luna_desc": "Luna Yoga Music ofrece audio tranquilo para escribir, descomprimir y reflexionar sobre relaciones, como una luz baja en el Jardín del Corazón de noche.",
    },
}

OG_LOCALES = {
    "zh": "zh_TW",
    "en": "en_US",
    "ja": "ja_JP",
    "ko": "ko_KR",
    "es": "es_ES",
}


RESOURCE_CARDS = {
    "zh": [
        ("guides", "守護者深度指南", "把測驗結果、錯頻、界線與修復練習整理成可直接閱讀的路線。"),
        ("repair-plan", "7 日心語修復計畫", "把守護者結果帶進一週練習：整理傷口、開口請求、選擇補給與回顧修復。"),
        ("keepsakes", "守護者收藏室", "保存五位守護者故事卡，作為分享、日記與未來收藏型補給的入口。"),
        ("characters/iris", "五位情感守護者", "從艾莉絲、諾雅、薇薇安、克萊兒與朵拉開始，找到你最容易接收愛的入口。"),
        ("luna-yoga-music", "Luna Yoga Music", "夜晚、書寫、伸展與關係反思時可使用的安定音樂補給。"),
        ("theory", "愛之語理論", "回到五種愛之語的基礎，理解為什麼有愛仍可能錯頻。"),
        ("contact", "聯絡與回報", "回報壞頁面、錯字、合作需求，或告訴我們哪盞燈需要重新點亮。"),
    ],
    "en": [
        ("guides", "Guardian guides", "Read paths for results, misfrequency, boundaries, and repair practices."),
        ("repair-plan", "7-Day Heart-Language Repair Plan", "Carry your guardian result through one week of reflection, requests, supplies, and repair review."),
        ("keepsakes", "Guardian Keepsake Hall", "Save the five guardian story cards for sharing, journaling, and future collectible supplies."),
        ("characters/iris", "Five emotion guardians", "Begin with Iris, Noah, Vivian, Claire, and Dora to find your doorway to receiving love."),
        ("luna-yoga-music", "Luna Yoga Music", "Calm audio supplies for night reflection, journaling, stretching, and relationship review."),
        ("theory", "Love-language theory", "Return to the five love languages and why love can still arrive out of frequency."),
        ("contact", "Contact and reports", "Report broken pages, corrections, partnership questions, or a lamp that needs relighting."),
    ],
    "ja": [
        ("guides", "守護者ガイド", "診断結果、すれ違い、境界線、修復練習を読むための入口です。"),
        ("repair-plan", "7日間の心語修復プラン", "守護者の結果を一週間の内省、お願い、補給、修復レビューへつなげます。"),
        ("keepsakes", "守護者コレクション室", "五人の守護者ストーリーカードを保存し、共有、日記、今後のコレクション補給の入口にします。"),
        ("characters/iris", "五人の感情の守護者", "アイリス、ノア、ヴィヴィアン、クレア、ドラから、愛を受け取る入口を探します。"),
        ("luna-yoga-music", "Luna Yoga Music", "夜の内省、日記、ストレッチ、関係のふり返りに寄り添う静かな音楽。"),
        ("theory", "愛の言語の理論", "五つの愛の言語と、愛があってもすれ違う理由に戻ります。"),
        ("contact", "連絡と報告", "壊れたページ、修正、提携、もう一度灯したいページを知らせる入口です。"),
    ],
    "ko": [
        ("guides", "수호자 가이드", "결과, 어긋남, 경계, 회복 연습을 읽기 쉽게 모은 입구입니다."),
        ("repair-plan", "7일 마음 언어 회복 계획", "수호자 결과를 일주일의 성찰, 요청, 보급, 회복 점검으로 이어 갑니다."),
        ("keepsakes", "수호자 소장실", "다섯 수호자 스토리 카드를 저장해 공유, 관계 일기, 향후 소장형 보급의 입구로 사용합니다."),
        ("characters/iris", "다섯 감정 수호자", "아이리스, 노아, 비비안, 클레어, 도라에서 사랑을 받는 입구를 찾습니다."),
        ("luna-yoga-music", "Luna Yoga Music", "밤의 성찰, 기록, 스트레칭, 관계 돌아보기에 어울리는 차분한 음악입니다."),
        ("theory", "사랑의 언어 이론", "다섯 가지 사랑의 언어와 사랑이 있어도 어긋나는 이유로 돌아갑니다."),
        ("contact", "연락과 제보", "깨진 페이지, 수정, 협업 문의, 다시 켜야 할 등불을 알려 주세요."),
    ],
    "es": [
        ("guides", "Guías de guardianas", "Entradas para resultados, desajustes, límites y prácticas de reparación."),
        ("repair-plan", "Plan de reparación de 7 días", "Lleva tu resultado por una semana de reflexión, petición, recursos y revisión de reparación."),
        ("keepsakes", "Sala de recuerdos", "Guarda las cinco tarjetas de guardianas para compartir, escribir y preparar futuros recursos coleccionables."),
        ("characters/iris", "Cinco guardianas emocionales", "Empieza con Iris, Noah, Vivian, Claire y Dora para encontrar tu entrada al amor."),
        ("luna-yoga-music", "Luna Yoga Music", "Audio tranquilo para reflexión nocturna, escritura, estiramiento y revisión relacional."),
        ("theory", "Teoría de lenguajes del amor", "Vuelve a los cinco lenguajes del amor y a por qué el amor puede llegar desajustado."),
        ("contact", "Contacto y reportes", "Reporta páginas rotas, correcciones, colaboraciones o una luz que deba volver a encenderse."),
    ],
}


LUNA_CONTENT = {
    "zh": {
        "badge": "MOONLIGHT SUPPLY",
        "headline": "在心語庭園的夜裡，讓 Luna 陪你慢慢回到自己。",
        "intro": "Luna Yoga Music 是 LoveTypes 的旅人補給之一，為書寫、伸展、睡前放鬆與關係反思準備一盞低光。它不取代對話，卻能讓你在開口前先把心安放好。",
        "primary": "進入旅人補給",
        "secondary": "閱讀修復指南",
        "sections": [
            ("morning", "晨間整理", "用溫柔節奏把昨夜殘留的情緒放下，重新辨認今天需要被照顧的愛之語。"),
            ("stress", "壓力降噪", "當關係訊息太密、心裡太吵時，先讓身體回到穩定，再決定下一句話。"),
            ("sleep", "夜間收束", "睡前不急著解決所有問題，只把今天的感受收進比較安全的位置。"),
        ],
    },
    "en": {
        "badge": "MOONLIGHT SUPPLY",
        "headline": "At night in the Heart Garden, Luna helps you return to yourself slowly.",
        "intro": "Luna Yoga Music is one of the LoveTypes traveler supplies: a low lamp for journaling, stretching, decompression, sleep, and relationship reflection before the next conversation.",
        "primary": "Open supplies",
        "secondary": "Read repair guides",
        "sections": [
            ("morning", "Morning reset", "Use a gentle rhythm to put down last night's residue and notice which love language needs care today."),
            ("stress", "Stress quieting", "When messages feel too dense and the heart is noisy, steady the body before choosing the next words."),
            ("sleep", "Night closure", "Before sleep, you do not need to solve everything. Place today's feelings somewhere safer first."),
        ],
    },
    "ja": {
        "badge": "MOONLIGHT SUPPLY",
        "headline": "心語の庭の夜に、Luna がゆっくり自分へ戻る時間をつくります。",
        "intro": "Luna Yoga Music は LoveTypes の旅人の補給です。日記、ストレッチ、緊張をほどく時間、眠る前の内省、次の会話の前に灯す低い明かりです。",
        "primary": "補給を見る",
        "secondary": "修復ガイドを読む",
        "sections": [
            ("morning", "朝のリセット", "やさしいリズムで昨夜の感情を置き、今日ケアしたい愛の言語に気づきます。"),
            ("stress", "ストレスを静める", "言葉が多すぎて心が騒ぐ時、次の一言を選ぶ前に体を安定させます。"),
            ("sleep", "夜の終わり", "眠る前にすべてを解決しなくても大丈夫。今日の気持ちを安全な場所へ移します。"),
        ],
    },
    "ko": {
        "badge": "MOONLIGHT SUPPLY",
        "headline": "마음의 정원 밤에 Luna가 천천히 자신에게 돌아오게 돕습니다.",
        "intro": "Luna Yoga Music은 LoveTypes의 여행자 보급품입니다. 기록, 스트레칭, 긴장 완화, 잠들기 전 성찰, 다음 대화 전 켜 두는 낮은 등불입니다.",
        "primary": "보급품 보기",
        "secondary": "회복 가이드 읽기",
        "sections": [
            ("morning", "아침 정리", "부드러운 리듬으로 밤의 잔여 감정을 내려놓고 오늘 돌볼 사랑의 언어를 알아차립니다."),
            ("stress", "스트레스 낮추기", "메시지가 빽빽하고 마음이 시끄러울 때, 다음 말을 고르기 전에 몸을 안정시킵니다."),
            ("sleep", "밤의 마무리", "잠들기 전 모든 문제를 해결하지 않아도 됩니다. 오늘의 감정을 더 안전한 곳에 둡니다."),
        ],
    },
    "es": {
        "badge": "MOONLIGHT SUPPLY",
        "headline": "De noche en el Jardín del Corazón, Luna te ayuda a volver despacio a ti.",
        "intro": "Luna Yoga Music es una provisión de viaje de LoveTypes: una luz baja para escribir, estirar, descomprimir, dormir y reflexionar antes de la próxima conversación.",
        "primary": "Abrir recursos",
        "secondary": "Leer reparación",
        "sections": [
            ("morning", "Reinicio de mañana", "Usa un ritmo suave para soltar lo que quedó de la noche y notar qué lenguaje del amor necesita cuidado."),
            ("stress", "Bajar el ruido", "Cuando los mensajes pesan y el corazón está ruidoso, estabiliza el cuerpo antes de elegir las palabras."),
            ("sleep", "Cierre nocturno", "Antes de dormir no hace falta resolver todo. Primero deja las emociones del día en un lugar más seguro."),
        ],
    },
}


AFFILIATE_DISCLOSURE = {
    "zh": "本頁部分連結為聯盟行銷連結，購買後本站可能獲得少量佣金，不影響你的購買價格。",
    "en": "Some links on this page are affiliate links. We may earn a small commission without changing your purchase price.",
    "ja": "このページにはアフィリエイトリンクが含まれます。購入価格は変わりませんが、当サイトに少額の報酬が入る場合があります。",
    "ko": "이 페이지에는 제휴 링크가 포함되어 있으며, 구매 가격에는 영향을 주지 않고 사이트가 소정의 수수료를 받을 수 있습니다.",
    "es": "Esta página contiene enlaces de afiliado. Podemos recibir una pequeña comisión sin cambiar tu precio de compra.",
}


AFFILIATE_COPY = {
    "zh": {
        "eyebrow": "BOOK RELICS",
        "title": "守護者旅程的延伸書卷",
        "intro": "如果角色頁讓你感覺被理解，這些書能幫你把那份理解變成日常裡能使用的語言。",
        "button": "前往博客來",
        "fit": "適合",
        "limit": "使用提醒",
        "routes": "對應守護者路線",
        "fallback": "外部書店偶爾會阻擋自動檢查或跨區連線；如果按鈕打不開，請用書名與作者到博客來或你常用的書店搜尋。",
    },
    "en": {
        "eyebrow": "BOOK RELICS",
        "title": "Reading for the guardian journey",
        "intro": "If a guardian page helped you feel seen, these books can help turn that insight into everyday language and repair.",
        "button": "Open bookstore",
        "fit": "Best for",
        "limit": "Use with",
        "routes": "Guardian routes",
        "fallback": "External bookstores may block automated checks or some regions. If the button does not open, search the title and author in your preferred bookstore.",
    },
    "ja": {
        "eyebrow": "BOOK RELICS",
        "title": "守護者の旅を深める本",
        "intro": "守護者ページで理解された感覚があったなら、これらの本はその理解を日常の言葉と修復へつなげます。",
        "button": "書店を見る",
        "fit": "向いている人",
        "limit": "使い方",
        "routes": "対応する守護者ルート",
        "fallback": "外部書店は自動チェックや一部地域からの接続を止める場合があります。開けない時は、書名と著者名で普段使う書店を検索してください。",
    },
    "ko": {
        "eyebrow": "BOOK RELICS",
        "title": "수호자 여정을 이어 가는 책",
        "intro": "수호자 페이지에서 이해받는 느낌이 있었다면, 이 책들은 그 이해를 일상의 말과 회복으로 옮기는 데 도움을 줍니다.",
        "button": "서점 열기",
        "fit": "추천 대상",
        "limit": "사용 팁",
        "routes": "연결 수호자 루트",
        "fallback": "외부 서점은 자동 검사나 일부 지역 접속을 막을 수 있습니다. 버튼이 열리지 않으면 제목과 저자를 사용해 자주 쓰는 서점에서 검색하세요.",
    },
    "es": {
        "eyebrow": "BOOK RELICS",
        "title": "Libros para continuar el viaje de las guardianas",
        "intro": "Si una página de guardiana te hizo sentir vista, estos libros ayudan a llevar esa comprensión a palabras y reparación cotidiana.",
        "button": "Abrir librería",
        "fit": "Ideal para",
        "limit": "Úsalo con",
        "routes": "Rutas de guardianas",
        "fallback": "Las librerías externas pueden bloquear revisiones automáticas o algunas regiones. Si el botón no abre, busca el título y el autor en tu librería habitual.",
    },
}


AFFILIATE_BOOKS = [
    {
        "emoji": "💕",
        "tag": {"zh": "原著 · 必讀", "en": "Core text", "ja": "原典", "ko": "핵심 원전", "es": "Texto base"},
        "title": {"zh": "愛的五種語言：增訂版", "en": "The 5 Love Languages", "ja": "愛を伝える5つの方法", "ko": "5가지 사랑의 언어", "es": "Los 5 lenguajes del amor"},
        "author": "Gary Chapman",
        "desc": {
            "zh": "愛之語理論的源頭，適合把五位守護者重新接回原始框架。",
            "en": "The source text behind the love-language framework and a useful bridge back from the five guardians.",
            "ja": "愛の言語フレームの原点で、五人の守護者を理論へつなぎ直す本です。",
            "ko": "사랑의 언어 프레임의 출발점으로, 다섯 수호자를 원래 이론과 연결해 줍니다.",
            "es": "El texto base de los lenguajes del amor y un puente para conectar las guardianas con el marco original.",
        },
        "fit": {
            "zh": "第一次接觸愛之語的人。",
            "en": "Readers meeting love languages for the first time.",
            "ja": "愛の言語に初めて触れる人。",
            "ko": "사랑의 언어를 처음 접하는 사람.",
            "es": "Personas que conocen por primera vez los lenguajes del amor.",
        },
        "limit": {
            "zh": "把例子翻成自己的文化、語氣與關係狀態。",
            "en": "Translate examples into your own culture, tone, and relationship context.",
            "ja": "例を自分の文化、言い方、関係の状況に翻訳してください。",
            "ko": "예시를 자신의 문화, 말투, 관계 상황에 맞게 번역하세요.",
            "es": "Traduce los ejemplos a tu cultura, tono y situación relacional.",
        },
        "url": "https://www.books.com.tw/exep/assp.php/arthur0858/products/0010842854?utm_source=arthur0858&utm_medium=ap-books&utm_content=recommend&utm_campaign=ap-202604",
    },
    {
        "emoji": "💬",
        "tag": {"zh": "溝通技巧", "en": "Communication", "ja": "対話", "ko": "대화", "es": "Comunicación"},
        "title": {"zh": "非暴力溝通", "en": "Nonviolent Communication", "ja": "非暴力コミュニケーション", "ko": "비폭력 대화", "es": "Comunicación no violenta"},
        "author": "Marshall B. Rosenberg",
        "desc": {
            "zh": "把感受、需求與請求分開，讓愛之語不再說成指責。",
            "en": "Separates observations, feelings, needs, and requests so care does not come out as blame.",
            "ja": "観察、感情、ニーズ、リクエストを分け、思いやりを責め言葉にしない練習です。",
            "ko": "관찰, 감정, 욕구, 요청을 분리해 배려가 비난으로 들리지 않게 돕습니다.",
            "es": "Distingue observaciones, sentimientos, necesidades y peticiones para que el cuidado no suene a culpa.",
        },
        "fit": {
            "zh": "需求清楚，卻常說成指責或冷戰的人。",
            "en": "People who know their need but express it as criticism or withdrawal.",
            "ja": "ニーズはあるのに責めや沈黙になりやすい人。",
            "ko": "욕구는 알지만 비난이나 침묵으로 표현하기 쉬운 사람.",
            "es": "Quien conoce su necesidad pero la expresa como crítica o distancia.",
        },
        "limit": {
            "zh": "先練習一句話，不必一次重寫整段關係。",
            "en": "Practice one sentence first; do not rewrite the whole relationship at once.",
            "ja": "まず一文だけ練習し、関係全体を一度に直そうとしないでください。",
            "ko": "한 문장부터 연습하고 관계 전체를 한 번에 고치려 하지 마세요.",
            "es": "Practica una frase primero; no intentes reescribir toda la relación de una vez.",
        },
        "url": "https://www.books.com.tw/exep/assp.php/arthur0858/products/0010882950?utm_source=arthur0858&utm_medium=ap-books&utm_content=recommend&utm_campaign=ap-202604",
    },
    {
        "emoji": "🧠",
        "tag": {"zh": "依附理論", "en": "Attachment", "ja": "愛着", "ko": "애착", "es": "Apego"},
        "title": {"zh": "依附：為什麼我們愛得這麼難", "en": "Attached", "ja": "添付された愛着の理解", "ko": "애착의 이해", "es": "Maneras de amar"},
        "author": "Amir Levine, Rachel Heller",
        "desc": {
            "zh": "理解靠近、退縮與不安如何改變你接收愛的方式。",
            "en": "Helps explain how closeness, distance, and insecurity shape the way love is received.",
            "ja": "近づきたい気持ち、距離、不安が愛の受け取り方をどう変えるかを理解します。",
            "ko": "가까움, 거리감, 불안이 사랑을 받는 방식을 어떻게 바꾸는지 이해하게 합니다.",
            "es": "Explica cómo la cercanía, la distancia y la inseguridad cambian la forma de recibir amor.",
        },
        "fit": {
            "zh": "常在靠近與退縮之間反覆的人。",
            "en": "Readers who swing between pursuit and withdrawal.",
            "ja": "近づくことと引くことを繰り返しやすい人。",
            "ko": "다가감과 물러남 사이를 반복하는 사람.",
            "es": "Quien oscila entre acercarse y retirarse.",
        },
        "limit": {
            "zh": "依附不是身分標籤，而是看見不安時的保護策略。",
            "en": "Attachment is not an identity label; use it to notice protective strategies.",
            "ja": "愛着は身分ラベルではなく、不安時の守り方を見る道具です。",
            "ko": "애착은 정체성 라벨이 아니라 불안할 때의 보호 전략을 보는 도구입니다.",
            "es": "El apego no es una etiqueta fija; sirve para observar estrategias de protección.",
        },
        "url": "https://www.books.com.tw/exep/assp.php/arthur0858/products/0010836544?utm_source=arthur0858&utm_medium=ap-books&utm_content=recommend&utm_campaign=ap-202604",
    },
    {
        "emoji": "💑",
        "tag": {"zh": "伴侶關係", "en": "Couples", "ja": "パートナー", "ko": "커플", "es": "Pareja"},
        "title": {"zh": "讓愛長久：七個原則", "en": "The Seven Principles for Making Marriage Work", "ja": "愛を長続きさせる七つの原則", "ko": "관계를 오래 가게 하는 일곱 원칙", "es": "Siete principios para hacer que el matrimonio funcione"},
        "author": "John Gottman",
        "desc": {
            "zh": "把理解變成長期互動習慣，從欣賞、修復與愛情地圖開始。",
            "en": "Turns insight into long-term habits through fondness, repair, and love maps.",
            "ja": "理解を長期的な習慣へ変え、感謝、修復、愛情地図から始めます。",
            "ko": "이해를 장기적 습관으로 옮기며, 감사, 회복, 사랑 지도에서 시작합니다.",
            "es": "Convierte la comprensión en hábitos duraderos mediante aprecio, reparación y mapas del amor.",
        },
        "fit": {
            "zh": "想把情感理解變成互動習慣的伴侶。",
            "en": "Partners who want emotional insight to become daily practice.",
            "ja": "感情理解を日常の習慣にしたいパートナー。",
            "ko": "감정 이해를 일상의 습관으로 만들고 싶은 파트너.",
            "es": "Parejas que quieren convertir la comprensión emocional en práctica diaria.",
        },
        "limit": {
            "zh": "從一個日常習慣開始，不必一次修完所有問題。",
            "en": "Begin with one habit; do not try to repair everything at once.",
            "ja": "一つの習慣から始め、すべてを一度に直そうとしないでください。",
            "ko": "하나의 습관부터 시작하고 모든 문제를 한 번에 고치려 하지 마세요.",
            "es": "Empieza con un hábito; no intentes reparar todo de una vez.",
        },
        "url": "https://www.books.com.tw/exep/assp.php/arthur0858/products/0010826394?utm_source=arthur0858&utm_medium=ap-books&utm_content=recommend&utm_campaign=ap-202604",
    },
]


QUIZ_LABELS = {
    "zh": {
        "eyebrow": "DESTINY RITUAL",
        "title": "15 道心語命運儀式",
        "intro": "不用註冊，依直覺選出最能讓你感到被愛的回應。完成後會認領一位情感守護者，並得到分數、下一步練習與延伸路線。",
        "start": "開始 15 題儀式",
        "question": "心語",
        "progress": "第 {current} 題，共 {total} 題",
        "next": "下一題",
        "see": "查看守護者結果",
        "result_label": "你的情感守護者",
        "score_title": "五種愛之語分布",
        "tips_title": "下一步練習",
        "compass_title": "結果行動羅盤",
        "pass_title": "守護者補給通行證",
        "pass_code": "通行域",
        "free_step": "先做免費練習",
        "luna_step": "情緒太滿時",
        "book_step": "準備深讀時",
        "book_intro": "延伸書卷",
        "luna_action": "開啟 Luna 夜間補給",
        "book_action": "查看補給書卷",
        "saved_title": "繼續上次的守護者路線",
        "saved_intro": "你的上次結果只保存在這台裝置的瀏覽器。可以直接回到修復計畫、Luna 或補給路線。",
        "guide_resume_title": "帶著上次守護者讀這篇",
        "guide_resume_intro": "讀完這篇後，可以回到你的修復計畫、守護者頁或個人補給路線，把靈感接成下一步。",
        "guardian_resume_title": "你的守護者已認領",
        "guardian_resume_intro": "這台裝置保留了上次測驗結果。從這裡回到你的守護者、補給路線、修復計畫與收藏卡。",
        "guardian_resume_match": "這是你上次認領的守護者。先看傷口與修復任務，再決定下一步補給。",
        "guardian_resume_other": "你正在閱讀另一位守護者。若要回到自己的路線，可以從這裡返回上次結果。",
        "saved_plan": "回到修復計畫",
        "saved_luna": "開啟 Luna",
        "saved_route": "查看補給路線",
        "saved_card": "開啟守護者卡",
        "saved_contact": "提出補給需求",
        "saved_copy": "複製分享文字",
        "saved_clear": "清除上次結果",
        "routes_title": "延伸路線",
        "guardian_link": "閱讀守護者頁",
        "guide_link": "閱讀對應指南",
        "resources_link": "開啟旅人補給",
        "supply_action": "選擇這條補給路線",
        "primary_route": "取得我的守護者補給路線",
        "secondary_plan": "填入 7 日修復計畫",
        "next_pack_title": "你的下一步補給包",
        "next_pack_intro": "先做一個免費任務，再用 Luna 降噪，最後只在合適時選一個延伸書卷。",
        "retake": "重新測驗",
        "copy": "複製結果",
        "copied": "已複製",
        "copy_manual": "無法自動複製，請手動複製這段文字",
        "copy_unavailable": "請手動複製",
        "share": "分享守護者卡",
        "shared": "已開啟分享",
        "share_prefix": "我的 LoveTypes 情感守護者是",
        "tie": "雙重愛之語訊號",
        "boundary": "這是自我理解工具，不是診斷。若關係中有暴力、控制或高風險處境，請優先尋求可信任的人與專業協助。",
    },
    "en": {
        "eyebrow": "DESTINY RITUAL",
        "title": "15 Heart-Language Prompts",
        "intro": "No signup. Choose the response that most helps you feel loved. At the end you claim an emotion guardian, scores, next practice, and a route to keep reading.",
        "start": "Start 15 prompts",
        "question": "Prompt",
        "progress": "Question {current} of {total}",
        "next": "Next",
        "see": "See guardian result",
        "result_label": "Your emotion guardian",
        "score_title": "Five love-language signal",
        "tips_title": "Next practices",
        "compass_title": "Result action compass",
        "pass_title": "Guardian supply pass",
        "pass_code": "Domain pass",
        "free_step": "Start with a free practice",
        "luna_step": "When feelings are loud",
        "book_step": "When ready to go deeper",
        "book_intro": "Extended book supply",
        "luna_action": "Open Luna night supply",
        "book_action": "View supply book",
        "saved_title": "Continue your last guardian route",
        "saved_intro": "Your last result is saved only in this browser on this device. Return to the repair plan, Luna, or your supply route.",
        "guide_resume_title": "Read this with your last guardian",
        "guide_resume_intro": "After this guide, return to your repair plan, guardian page, or personal supply route so the insight becomes a next step.",
        "guardian_resume_title": "Your guardian is claimed",
        "guardian_resume_intro": "This device has your last quiz result. Return to your guardian, supply route, repair plan, and keepsake card from here.",
        "guardian_resume_match": "This is the guardian you claimed last time. Read the wound and repair task first, then choose the next supply.",
        "guardian_resume_other": "You are reading another guardian. Use this doorway to return to your own route.",
        "saved_plan": "Return to repair plan",
        "saved_luna": "Open Luna",
        "saved_route": "View supply route",
        "saved_card": "Open guardian card",
        "saved_contact": "Request supply",
        "saved_copy": "Copy share text",
        "saved_clear": "Clear last result",
        "routes_title": "Continue the path",
        "guardian_link": "Read guardian page",
        "guide_link": "Read matching guide",
        "resources_link": "Open resources",
        "supply_action": "Choose this supply route",
        "primary_route": "Get my guardian supply route",
        "secondary_plan": "Fill the 7-day repair plan",
        "next_pack_title": "Your next-step supply pack",
        "next_pack_intro": "Start with one free task, use Luna to lower the noise, then choose one extended book only if it fits.",
        "retake": "Retake",
        "copy": "Copy result",
        "copied": "Copied",
        "copy_manual": "Automatic copy is unavailable. Copy this text manually.",
        "copy_unavailable": "Copy manually",
        "share": "Share guardian card",
        "shared": "Share opened",
        "share_prefix": "My LoveTypes emotion guardian is",
        "tie": "Blended love-language signal",
        "boundary": "This is a reflection tool, not a diagnosis. If a relationship includes violence, control, or urgent risk, seek trusted and professional support first.",
    },
    "ja": {
        "eyebrow": "DESTINY RITUAL",
        "title": "15 の心語リチュアル",
        "intro": "登録不要。愛されていると感じやすい返答を直感で選びます。最後に感情の守護者、分布、次の練習、読む道筋が出ます。",
        "start": "15問を始める",
        "question": "心語",
        "progress": "{total} 問中 {current} 問目",
        "next": "次へ",
        "see": "守護者の結果を見る",
        "result_label": "あなたの感情の守護者",
        "score_title": "五つの愛の言語の分布",
        "tips_title": "次の練習",
        "compass_title": "結果アクションコンパス",
        "pass_title": "守護者の補給パス",
        "pass_code": "通行する分域",
        "free_step": "まず無料の練習",
        "luna_step": "感情が大きい時",
        "book_step": "深く読みたい時",
        "book_intro": "補給の本",
        "luna_action": "Luna の夜の補給を開く",
        "book_action": "補給の本を見る",
        "saved_title": "前回の守護者ルートを続ける",
        "saved_intro": "前回の結果はこの端末のブラウザだけに保存されています。修復プラン、Luna、補給ルートへ戻れます。",
        "guide_resume_title": "前回の守護者と一緒に読む",
        "guide_resume_intro": "読み終えたら、修復プラン、守護者ページ、補給ルートへ戻り、気づきを次の一歩につなげられます。",
        "guardian_resume_title": "守護者を認領済みです",
        "guardian_resume_intro": "この端末には前回の診断結果が残っています。守護者、補給ルート、修復プラン、カードへ戻れます。",
        "guardian_resume_match": "これは前回認領した守護者です。傷口と修復課題を読んでから、次の補給を選べます。",
        "guardian_resume_other": "別の守護者を読んでいます。自分のルートへ戻る時は、ここから前回の結果へ戻れます。",
        "saved_plan": "修復プランへ戻る",
        "saved_luna": "Luna を開く",
        "saved_route": "補給ルートを見る",
        "saved_card": "守護者カードを開く",
        "saved_contact": "補給を希望する",
        "saved_copy": "共有文をコピー",
        "saved_clear": "前回の結果を消す",
        "routes_title": "続きを読む道筋",
        "guardian_link": "守護者ページを読む",
        "guide_link": "対応ガイドを読む",
        "resources_link": "リソースを開く",
        "supply_action": "この補給ルートを選ぶ",
        "primary_route": "守護者の補給ルートを受け取る",
        "secondary_plan": "7日間の修復プランへ記入",
        "next_pack_title": "次の一歩の補給パック",
        "next_pack_intro": "まず無料の課題を一つ行い、Luna で感情の音量を下げ、合う時だけ本を一つ選びます。",
        "retake": "もう一度",
        "copy": "結果をコピー",
        "copied": "コピー済み",
        "copy_manual": "自動コピーできません。手動でこの文をコピーしてください。",
        "copy_unavailable": "手動でコピー",
        "share": "守護者カードを共有",
        "shared": "共有を開きました",
        "share_prefix": "私の LoveTypes 感情の守護者は",
        "tie": "混合した愛の言語シグナル",
        "boundary": "これは自己理解の道具であり、診断ではありません。暴力、支配、緊急の危険がある場合は、まず信頼できる人や専門機関に相談してください。",
    },
    "ko": {
        "eyebrow": "DESTINY RITUAL",
        "title": "15개의 마음 언어 의식",
        "intro": "가입 없이 가장 사랑받는다고 느끼는 반응을 고르세요. 끝나면 감정 수호자, 점수, 다음 연습, 이어 읽을 길이 나옵니다.",
        "start": "15문항 시작",
        "question": "마음 언어",
        "progress": "{total}개 중 {current}번",
        "next": "다음",
        "see": "수호자 결과 보기",
        "result_label": "나의 감정 수호자",
        "score_title": "다섯 사랑의 언어 분포",
        "tips_title": "다음 연습",
        "compass_title": "결과 행동 나침반",
        "pass_title": "수호자 보급 패스",
        "pass_code": "통행 분역",
        "free_step": "무료 연습부터",
        "luna_step": "감정이 클 때",
        "book_step": "더 깊이 읽을 때",
        "book_intro": "확장 보급 책",
        "luna_action": "Luna 밤 보급 열기",
        "book_action": "보급 책 보기",
        "saved_title": "지난 수호자 루트 이어가기",
        "saved_intro": "지난 결과는 이 기기의 브라우저에만 저장됩니다. 회복 계획, Luna, 보급 루트로 바로 돌아갈 수 있습니다.",
        "guide_resume_title": "지난 수호자와 함께 읽기",
        "guide_resume_intro": "이 글을 읽은 뒤 회복 계획, 수호자 페이지, 개인 보급 루트로 돌아가 다음 행동으로 이어갈 수 있습니다.",
        "guardian_resume_title": "나의 수호자가 선택되었습니다",
        "guardian_resume_intro": "이 기기에 지난 테스트 결과가 남아 있습니다. 수호자, 보급 루트, 회복 계획, 카드로 돌아갈 수 있습니다.",
        "guardian_resume_match": "지난번 선택한 수호자입니다. 상처와 회복 과제를 먼저 읽고 다음 보급을 고르세요.",
        "guardian_resume_other": "다른 수호자 페이지를 읽고 있습니다. 내 루트로 돌아가려면 여기에서 지난 결과로 이동하세요.",
        "saved_plan": "회복 계획으로 돌아가기",
        "saved_luna": "Luna 열기",
        "saved_route": "보급 루트 보기",
        "saved_card": "수호자 카드 열기",
        "saved_contact": "보급 요청하기",
        "saved_copy": "공유 문구 복사",
        "saved_clear": "지난 결과 지우기",
        "routes_title": "이어 갈 길",
        "guardian_link": "수호자 페이지 읽기",
        "guide_link": "관련 가이드 읽기",
        "resources_link": "자료 열기",
        "supply_action": "이 보급 루트 선택",
        "primary_route": "내 수호자 보급 루트 받기",
        "secondary_plan": "7일 회복 계획 채우기",
        "next_pack_title": "나의 다음 단계 보급 팩",
        "next_pack_intro": "무료 과제 하나부터 시작하고 Luna로 감정 소음을 낮춘 뒤, 맞을 때만 책 하나를 고르세요.",
        "retake": "다시 하기",
        "copy": "결과 복사",
        "copied": "복사됨",
        "copy_manual": "자동 복사가 어렵습니다. 이 문구를 직접 복사해 주세요.",
        "copy_unavailable": "직접 복사",
        "share": "수호자 카드 공유",
        "shared": "공유 열림",
        "share_prefix": "나의 LoveTypes 감정 수호자는",
        "tie": "혼합 사랑의 언어 신호",
        "boundary": "이것은 자기 이해 도구이며 진단이 아닙니다. 폭력, 통제, 긴급 위험이 있다면 먼저 신뢰할 수 있는 사람과 전문 지원을 찾으세요.",
    },
    "es": {
        "eyebrow": "DESTINY RITUAL",
        "title": "15 señales del corazón",
        "intro": "Sin registro. Elige la respuesta que más te hace sentir amada. Al final reclamas una guardiana emocional, puntajes, práctica y una ruta para seguir leyendo.",
        "start": "Iniciar 15 señales",
        "question": "Señal",
        "progress": "Pregunta {current} de {total}",
        "next": "Siguiente",
        "see": "Ver guardiana",
        "result_label": "Tu guardiana emocional",
        "score_title": "Distribución de lenguajes del amor",
        "tips_title": "Próximas prácticas",
        "compass_title": "Brújula de acción del resultado",
        "pass_title": "Pase de suministro de guardiana",
        "pass_code": "Dominio de paso",
        "free_step": "Empieza con práctica gratuita",
        "luna_step": "Cuando la emoción está alta",
        "book_step": "Cuando quieras profundizar",
        "book_intro": "Libro de suministro",
        "luna_action": "Abrir suministro nocturno Luna",
        "book_action": "Ver libro de suministro",
        "saved_title": "Continuar tu última ruta",
        "saved_intro": "Tu último resultado se guarda solo en este navegador y dispositivo. Puedes volver al plan, Luna o tu ruta de suministro.",
        "guide_resume_title": "Lee esto con tu última guardiana",
        "guide_resume_intro": "Después de la guía, vuelve a tu plan, página de guardiana o ruta de suministro para convertir la idea en siguiente paso.",
        "guardian_resume_title": "Tu guardiana está reclamada",
        "guardian_resume_intro": "Este dispositivo conserva tu último resultado. Vuelve a tu guardiana, ruta, plan y tarjeta desde aquí.",
        "guardian_resume_match": "Esta es la guardiana que reclamaste. Lee la herida y la tarea de reparación antes de elegir el siguiente recurso.",
        "guardian_resume_other": "Estás leyendo otra guardiana. Usa esta puerta para volver a tu propia ruta.",
        "saved_plan": "Volver al plan",
        "saved_luna": "Abrir Luna",
        "saved_route": "Ver ruta",
        "saved_card": "Abrir tarjeta",
        "saved_contact": "Pedir recurso",
        "saved_copy": "Copiar texto",
        "saved_clear": "Borrar resultado",
        "routes_title": "Continuar el camino",
        "guardian_link": "Leer página de guardiana",
        "guide_link": "Leer guía relacionada",
        "resources_link": "Abrir recursos",
        "supply_action": "Elegir esta ruta",
        "primary_route": "Obtener mi ruta de guardiana",
        "secondary_plan": "Completar plan de 7 días",
        "next_pack_title": "Tu pack de siguiente paso",
        "next_pack_intro": "Empieza con una tarea gratuita, usa Luna para bajar el ruido y elige un libro solo si encaja.",
        "retake": "Repetir",
        "copy": "Copiar resultado",
        "copied": "Copiado",
        "copy_manual": "La copia automática no está disponible. Copia este texto manualmente.",
        "copy_unavailable": "Copia manual",
        "share": "Compartir tarjeta",
        "shared": "Compartir abierto",
        "share_prefix": "Mi guardiana emocional LoveTypes es",
        "tie": "Señal combinada de lenguajes",
        "boundary": "Esto es una herramienta de reflexión, no un diagnóstico. Si hay violencia, control o riesgo urgente, busca primero apoyo profesional y de confianza.",
    },
}


QUIZ_TYPES = {
    "W": {"slug": "iris", "guide": "words-of-affirmation-scripts", "color": "#bd5260"},
    "T": {"slug": "noah", "guide": "quality-time-long-distance", "color": "#7666a8"},
    "G": {"slug": "vivian", "guide": "gifts-are-not-materialism", "color": "#b78b45"},
    "S": {"slug": "claire", "guide": "acts-of-service-boundaries", "color": "#6b7f6a"},
    "P": {"slug": "dora", "guide": "physical-touch-consent-safety", "color": "#c66b72"},
}


QUIZ_QUESTIONS = {
    "zh": [
        ("你心情不好的時候，哪一種靠近最像一盞燈？", ["跟你說：我在，你不是一個人", "關掉手機，安靜陪你坐著", "帶著你喜歡的小東西出現", "默默幫你把混亂收拾好", "先確認你願意，再給你一個擁抱"]),
        ("吵架和好後，什麼讓你覺得真的被接回來？", ["對方清楚說出歉意與珍惜", "坐下來把剛才的錯頻聊完", "用一個小心意提醒你被記得", "做一件具體的事補回承諾", "牽住你的手，讓身體也放鬆"]),
        ("生日或紀念日，你最重視哪個訊號？", ["一段寫得很用心的文字", "一整段不被打擾的共處", "對方記得你提過的小願望", "行程和細節都被妥善安排", "自然的靠近與溫度"]),
        ("忙碌一週後，哪種愛最能幫你恢復？", ["被肯定最近真的很努力", "一起慢慢散步或看完一部片", "收到一杯你最近常想喝的飲料", "有人先把晚餐或家務處理好", "靠著對方休息一下"]),
        ("最容易讓你感到不被重視的是？", ["很少被感謝或正向回應", "對方陪你時總是分心", "重要日子完全沒有任何表示", "責任總是落在你身上", "對方幾乎不主動靠近"]),
        ("旅行時，你最想被留下的記憶是？", ["那些真心話與稱讚", "全程專注探索彼此", "被挑了一個有意義的紀念物", "不用操心就有人處理細節", "牽手走在陌生街道"]),
        ("你最感謝伴侶哪種特質？", ["總能說出你需要聽的話", "和你說話時很專注", "記得你隨口提過的喜歡", "默默把生活照顧得更輕", "知道什麼時候給你安全的靠近"]),
        ("日常裡哪一幕最甜？", ["睡前一句今天看見你的努力", "下班後一起聊今天發生的事", "沒有原因的一朵花或小點心", "對方主動處理你不想面對的小事", "走路時自然牽住你的手"]),
        ("你覺得真正的愛比較像？", ["被語言溫柔接住", "有人願意把時間留給你", "在細節裡發現對方記得你", "有人讓你的生活輕一點", "身體先感到安全"]),
        ("生病或低潮時，哪個照顧最窩心？", ["一直傳訊息關心與鼓勵", "陪你看醫生或整晚聽你說", "帶來你會舒服一點的小物", "買藥、煮粥、整理環境", "握著你的手陪你休息"]),
        ("你最希望對方什麼時候想起你？", ["用一段文字說今天想到你", "再忙也留一段只屬於你們的時間", "路過時帶回你曾說想要的東西", "你忙到不行時主動接手", "見面第一秒先給你安心的靠近"]),
        ("完美約會的核心是？", ["有幾句話讓你想記下來", "手機收起來，只在彼此身上", "有主題、有心意、有小驚喜", "細節安排好，你只要出現", "整段時間都有舒適的親近"]),
        ("如果對方說想讓你開心，你希望接下來是？", ["說一段讓你感動的話", "把今天的時間完整留給你", "拿出一份精心準備的小禮物", "解決最近困擾你的一件事", "先問你可不可以抱抱你"]),
        ("遠距時，什麼最像我們還在一起？", ["每天一句真心想念", "固定視訊且不分心", "收到裝滿你喜歡之物的包裹", "對方遠端幫你處理麻煩", "見面時被好好擁抱"]),
        ("你最想學會怎麼表達需求？", ["把需要說成清楚而溫柔的話", "約定固定的專心時段", "讓對方知道心意比價格重要", "把需要幫忙的事說具體", "把同意與舒服說清楚"]),
    ],
    "en": [
        ("When your heart is low, which response feels most like a lamp?", ["Words that say you are not alone", "Undistracted time beside you", "A small thing that proves you were remembered", "Quiet help that restores order", "A hug after checking consent"]),
        ("After conflict, what helps you feel reconnected?", ["A clear apology and appreciation", "Time to talk through the misfrequency", "A small meaningful gesture", "A concrete repair action", "A safe hand held in yours"]),
        ("On a meaningful day, what matters most?", ["A carefully written message", "A pocket of protected time", "A gift tied to something you mentioned", "Details handled with care", "Warm and natural closeness"]),
        ("After a hard week, what restores you?", ["Being affirmed for your effort", "A slow walk or movie together", "A favorite drink brought to you", "Dinner or chores handled first", "Resting close to someone safe"]),
        ("What most easily feels like being unseen?", ["No thanks or positive words", "Distracted company", "No sign on important days", "All responsibility falling on you", "Almost no initiated closeness"]),
        ("On a trip, what memory would stay with you?", ["Honest words and praise", "Focused exploring together", "A meaningful keepsake", "Details handled for you", "Holding hands in a new street"]),
        ("What trait are you most grateful for?", ["They say the words you need", "They listen with full attention", "They remember tiny preferences", "They make life lighter", "They know when safe closeness helps"]),
        ("Which ordinary moment feels sweetest?", ["A bedtime sentence naming your effort", "Talking after work", "A small treat for no reason", "Help with a task you avoided", "A natural hand held while walking"]),
        ("Real love feels most like:", ["Being held by language", "Someone saving time for you", "Being remembered in details", "Life getting a little lighter", "The body feeling safe"]),
        ("When sick or low, what care reaches you?", ["Messages of care and encouragement", "Being accompanied and heard", "Small comforts brought to you", "Medicine, food, and space handled", "A hand held while you rest"]),
        ("When do you most want to be remembered?", ["A message saying something reminded them of you", "A protected time even when busy", "A small thing brought back from passing by", "Help when you are overloaded", "Safe closeness at the first hello"]),
        ("What is the core of a perfect date?", ["Words you want to keep", "Phones away and full attention", "Theme, meaning, and a small surprise", "Details planned so you can arrive", "Comfortable closeness throughout"]),
        ("If they say they want to make you happy, next you hope they:", ["Say something moving", "Give you the day fully", "Bring out a thoughtful small gift", "Solve one stressful thing", "Ask if they can hold you"]),
        ("In distance, what keeps the bond alive?", ["Daily honest words of missing you", "Regular calls without distraction", "A package full of remembered details", "Remote help with practical trouble", "A real embrace when reunited"]),
        ("What need do you want to express better?", ["Clear and kind words", "A fixed time for full presence", "Meaning over price", "Specific requests for help", "Consent and comfort around touch"]),
    ],
    "ja": [
        ("心が沈む時、どの近づき方が灯りに感じますか？", ["一人じゃないと言ってくれる", "集中してそばにいてくれる", "覚えていてくれた小さなもの", "静かに混乱を整えてくれる", "同意を確かめて抱きしめる"]),
        ("衝突後、何でつながり直したと感じますか？", ["明確な謝罪と大切に思う言葉", "すれ違いを話す時間", "意味のある小さな心遣い", "具体的な修復行動", "安心できる手のぬくもり"]),
        ("大切な日に一番響くものは？", ["丁寧に書かれたメッセージ", "守られた二人の時間", "話したことを覚えた贈り物", "細部まで整えられた準備", "自然な近さと温度"]),
        ("疲れた一週間の後、何が回復になりますか？", ["努力を言葉で認められる", "一緒に散歩や映画", "好きな飲み物を持って来る", "食事や家事を先にしてくれる", "安心して寄りかかる"]),
        ("見てもらえていないと感じやすいのは？", ["感謝や肯定がない", "一緒にいても上の空", "大事な日に何もない", "責任が自分に偏る", "相手から近づいてこない"]),
        ("旅で残したい記憶は？", ["本音の言葉と称賛", "集中して一緒に探索する", "意味のある記念品", "細部を任せられる", "知らない道で手をつなぐ"]),
        ("相手のどんな特質に感謝しますか？", ["必要な言葉をくれる", "集中して聞いてくれる", "小さな好みを覚えている", "生活を軽くしてくれる", "安全な近さを知っている"]),
        ("日常で一番甘い場面は？", ["寝る前の肯定の一言", "仕事後に話す時間", "理由のない小さなおやつ", "避けていた用事を助ける", "歩く時に自然に手をつなぐ"]),
        ("本当の愛に近い感覚は？", ["言葉に受け止められる", "時間を残してくれる", "細部に覚えている証がある", "生活が少し軽くなる", "身体が安全を感じる"]),
        ("体調不良や落ち込みの時、届くケアは？", ["励ましの連絡", "付き添い、聞いてくれる", "楽になる小物", "薬や食事や片付け", "手を握って休ませる"]),
        ("いつ思い出してほしいですか？", ["思い出したと文章で伝える", "忙しくても二人の時間を作る", "通りがかりに好きなものを買う", "忙しい時に引き受ける", "会った瞬間の安心する近さ"]),
        ("理想のデートの核は？", ["残したい言葉がある", "スマホをしまい集中する", "テーマと小さな驚き", "準備されていて現れるだけ", "心地よい近さが続く"]),
        ("相手が喜ばせたいと言ったら？", ["心に残る言葉を言う", "一日を空けてくれる", "考えた小さな贈り物", "困りごとを一つ解決", "抱きしめていいか聞く"]),
        ("遠距離でつながりを感じるのは？", ["毎日の素直な言葉", "集中した定期通話", "好みが詰まった荷物", "遠くからの実務的な助け", "再会時の抱擁"]),
        ("どのニーズを表現したいですか？", ["明確で優しい言葉", "集中する時間の約束", "値段より意味", "具体的な手助けの依頼", "同意と心地よさ"]),
    ],
    "ko": [
        ("마음이 낮을 때 어떤 다가옴이 등불처럼 느껴지나요?", ["혼자가 아니라고 말해 주기", "방해 없이 곁에 있기", "기억했다는 작은 선물", "조용히 상황을 정리해 주기", "동의를 확인한 뒤 안아 주기"]),
        ("갈등 후 무엇이 다시 이어졌다고 느끼게 하나요?", ["분명한 사과와 소중하다는 말", "어긋남을 이야기할 시간", "의미 있는 작은 마음", "구체적인 회복 행동", "안전하게 잡아 주는 손"]),
        ("중요한 날 가장 와닿는 신호는?", ["정성 들인 메시지", "보호된 둘만의 시간", "말했던 것을 기억한 선물", "세심하게 준비된 일정", "자연스러운 가까움과 온도"]),
        ("힘든 한 주 뒤 무엇이 회복이 되나요?", ["노력을 인정받는 말", "함께 산책하거나 영화 보기", "좋아하는 음료를 가져오기", "저녁이나 집안일을 먼저 처리", "안전하게 기대어 쉬기"]),
        ("무시당한다고 느끼기 쉬운 것은?", ["감사와 긍정이 없음", "함께 있어도 산만함", "중요한 날 아무 표시 없음", "책임이 내게만 몰림", "상대가 거의 다가오지 않음"]),
        ("여행에서 남기고 싶은 기억은?", ["진심 어린 말과 칭찬", "서로에게 집중한 탐험", "의미 있는 기념품", "세부를 대신 챙겨 줌", "낯선 거리에서 손잡기"]),
        ("상대의 어떤 점에 감사하나요?", ["필요한 말을 해 줌", "온전히 들어 줌", "작은 취향을 기억함", "삶을 가볍게 해 줌", "안전한 가까움을 앎"]),
        ("일상에서 가장 달콤한 장면은?", ["잠들기 전 노력 알아주기", "퇴근 후 대화", "이유 없는 작은 간식", "피하던 일을 도와줌", "걸을 때 자연스럽게 손잡기"]),
        ("진짜 사랑에 가까운 느낌은?", ["말로 다정하게 받아들여짐", "시간을 남겨 줌", "세부에서 기억됨", "삶이 조금 가벼워짐", "몸이 안전하다고 느낌"]),
        ("아프거나 힘들 때 어떤 돌봄이 닿나요?", ["격려와 안부 메시지", "함께 가고 들어 줌", "편해지는 작은 것", "약, 음식, 공간 정리", "손을 잡고 쉬게 해 줌"]),
        ("언제 기억되길 바라나요?", ["생각났다고 글로 전하기", "바빠도 둘만의 시간 만들기", "지나가다 좋아하는 것 사 오기", "바쁠 때 대신 맡아 주기", "만나자마자 안전한 가까움"]),
        ("완벽한 데이트의 핵심은?", ["기억하고 싶은 말", "폰을 내려놓고 집중", "주제와 작은 놀라움", "세부가 준비되어 있음", "편안한 가까움이 계속됨"]),
        ("상대가 기쁘게 해 주고 싶다고 하면?", ["감동적인 말을 함", "하루를 온전히 내어 줌", "생각한 작은 선물", "스트레스 하나를 해결", "안아도 되는지 물음"]),
        ("장거리에서 무엇이 우리를 이어 주나요?", ["매일의 진심 어린 말", "집중한 정기 통화", "취향이 담긴 택배", "멀리서 실질적으로 도와줌", "다시 만났을 때의 포옹"]),
        ("어떤 욕구를 더 잘 말하고 싶나요?", ["분명하고 다정한 말", "온전히 함께하는 시간", "가격보다 의미", "구체적인 도움 요청", "동의와 편안함"]),
    ],
    "es": [
        ("Cuando estás mal, qué gesto se siente como una luz?", ["Palabras que dicen no estás sola", "Tiempo sin distracciones", "Un detalle que prueba que te recuerdan", "Ayuda silenciosa que ordena", "Un abrazo después de pedir permiso"]),
        ("Después de un conflicto, qué reconecta?", ["Disculpa clara y aprecio", "Tiempo para hablar el desajuste", "Un gesto pequeño con sentido", "Una acción concreta de reparación", "Una mano segura en la tuya"]),
        ("En un día importante, qué importa más?", ["Un mensaje cuidado", "Tiempo protegido para dos", "Un regalo ligado a algo que dijiste", "Detalles bien preparados", "Cercanía cálida y natural"]),
        ("Después de una semana dura, qué restaura?", ["Reconocimiento por tu esfuerzo", "Caminar o ver algo juntas", "Tu bebida favorita", "Cena o tareas resueltas", "Descansar cerca de alguien seguro"]),
        ("Qué te hace sentir menos vista?", ["No recibir gracias ni palabras buenas", "Compañía distraída", "Nada en días importantes", "Toda la responsabilidad sobre ti", "Casi ninguna cercanía iniciada"]),
        ("En un viaje, qué memoria queda?", ["Palabras honestas y elogios", "Explorar con atención mutua", "Un recuerdo significativo", "Detalles resueltos por ti", "Tomarse la mano en una calle nueva"]),
        ("Qué rasgo agradeces más?", ["Dice las palabras que necesitas", "Escucha con toda atención", "Recuerda preferencias pequeñas", "Hace la vida más ligera", "Sabe cuándo la cercanía segura ayuda"]),
        ("Qué momento cotidiano es más dulce?", ["Una frase antes de dormir", "Hablar después del trabajo", "Un detalle sin motivo", "Ayuda con algo evitado", "Tomarse la mano al caminar"]),
        ("El amor real se parece más a:", ["Ser sostenida por palabras", "Alguien guarda tiempo para ti", "Ser recordada en detalles", "La vida se vuelve más ligera", "El cuerpo se siente seguro"]),
        ("Cuando estás enferma o triste, qué cuidado llega?", ["Mensajes de ánimo", "Acompañarte y escucharte", "Pequeñas comodidades", "Medicina, comida y espacio resueltos", "Una mano mientras descansas"]),
        ("Cuándo quieres ser recordada?", ["Un mensaje diciendo pensé en ti", "Tiempo protegido aunque haya ocupación", "Traer algo que te gusta", "Ayuda cuando estás saturada", "Cercanía segura al saludarse"]),
        ("Cuál es el núcleo de una cita perfecta?", ["Palabras que quieres guardar", "Teléfonos lejos y atención plena", "Tema, sentido y pequeña sorpresa", "Detalles listos para solo llegar", "Cercanía cómoda todo el tiempo"]),
        ("Si quiere hacerte feliz, esperas que:", ["Diga algo que te toque", "Te entregue el día completo", "Saque un regalo pensado", "Resuelva algo estresante", "Pregunte si puede abrazarte"]),
        ("A distancia, qué mantiene el vínculo?", ["Palabras honestas diarias", "Llamadas regulares sin distracción", "Un paquete lleno de detalles", "Ayuda práctica desde lejos", "Un abrazo al reencontrarse"]),
        ("Qué necesidad quieres expresar mejor?", ["Palabras claras y amables", "Tiempo fijo de presencia", "Sentido sobre precio", "Peticiones concretas de ayuda", "Consentimiento y comodidad"]),
    ],
}


QUIZ_TIPS = {
    "zh": {
        "W": ["今天說出一件具體感謝，不用華麗，只要準確。", "需要鼓勵時直接說：我想聽你肯定我哪裡做得好。"],
        "T": ["約一段無手機時光，讓在場變成可感覺的承諾。", "用十五分鐘問彼此：這週哪一刻最像我們在一起？"],
        "G": ["記下一個對方隨口提過的小喜歡，讓被記得有形狀。", "提醒彼此：我重視的是心意與觀察，不是價格。"],
        "S": ["把想被幫忙的事說成具體請求，而不是考驗。", "每週交換一件小事，讓承諾回到日常。"],
        "P": ["先問舒服與同意，再讓靠近成為安全。", "建立一個短短的告別或睡前靠近儀式。"],
    },
    "en": {
        "W": ["Name one specific appreciation today.", "Ask directly for the encouragement you need."],
        "T": ["Protect one phone-free pocket of time.", "Ask what moment this week felt most like together."],
        "G": ["Record one tiny preference and make remembrance visible.", "Say clearly that meaning matters more than price."],
        "S": ["Make help a specific request, not a test.", "Trade one small support action each week."],
        "P": ["Ask for comfort and consent before closeness.", "Create a short goodbye or bedtime closeness ritual."],
    },
    "ja": {
        "W": ["今日、具体的な感謝を一つ伝える。", "必要な励ましを直接お願いする。"],
        "T": ["スマホなしの時間を一つ守る。", "今週一番一緒にいると感じた瞬間を聞く。"],
        "G": ["小さな好みを記録し、覚えている形にする。", "値段より意味が大事だと伝える。"],
        "S": ["手伝ってほしいことを具体的に頼む。", "毎週一つ小さな支援を交換する。"],
        "P": ["近づく前に心地よさと同意を確かめる。", "短い別れ際や就寝前の近さを作る。"],
    },
    "ko": {
        "W": ["오늘 구체적인 감사 하나를 말하기.", "필요한 격려를 직접 요청하기."],
        "T": ["휴대폰 없는 시간을 하나 지키기.", "이번 주 함께 있다고 느낀 순간을 묻기."],
        "G": ["작은 취향을 기록해 기억을 보이게 하기.", "가격보다 의미가 중요하다고 말하기."],
        "S": ["도움이 필요한 일을 구체적으로 요청하기.", "매주 작은 도움 하나를 주고받기."],
        "P": ["가까워지기 전 편안함과 동의를 확인하기.", "짧은 인사나 잠들기 전 가까움 만들기."],
    },
    "es": {
        "W": ["Nombra hoy una gratitud específica.", "Pide directamente el ánimo que necesitas."],
        "T": ["Protege un tiempo sin teléfono.", "Pregunta qué momento de la semana se sintió más juntos."],
        "G": ["Anota una preferencia pequeña y haz visible el recuerdo.", "Di que el sentido importa más que el precio."],
        "S": ["Convierte la ayuda en petición concreta, no prueba.", "Intercambien una acción pequeña de apoyo cada semana."],
        "P": ["Pregunta comodidad y consentimiento antes de acercarte.", "Crea un breve ritual de despedida o noche."],
    },
}


THEORY_FAQ = {
    "zh": [
        ("什麼是五種愛之語？", "五種愛之語是一套關係溝通框架，用肯定言詞、優質時光、接受禮物、服務行動與身體接觸，描述人們表達與接收愛的常見方式。LoveTypes 把它翻成五位守護者，讓理解更容易被記住。"),
        ("命運儀式需要多久？", "首頁儀式共有 15 道心語，通常 2 到 3 分鐘可完成。結果適合拿來開啟對話，不適合作為固定標籤。"),
        ("愛之語會改變嗎？", "會。壓力、關係階段、遠距、創傷經驗或生活角色變化，都可能讓你當下最需要的愛之語不同。"),
        ("如果伴侶和我的守護者不同怎麼辦？", "差異不是失敗，而是翻譯任務。先說明自己如何接收愛，再請對方示範他們能做的小行動。"),
    ],
    "en": [
        ("What are the five love languages?", "They are a relationship communication framework for words of affirmation, quality time, receiving gifts, acts of service, and physical touch. LoveTypes turns them into five guardians so the ideas are easier to remember and use."),
        ("How long does the ritual take?", "The homepage ritual has 15 prompts and usually takes 2 to 3 minutes. Use the result to start a conversation, not as a fixed label."),
        ("Can a love language change?", "Yes. Stress, relationship stage, distance, past hurt, and life roles can shift what helps you feel loved right now."),
        ("What if my partner has a different guardian?", "Difference is not failure; it is translation work. Name how you receive love, then ask for one small action the other person can actually do."),
    ],
    "ja": [
        ("五つの愛の言語とは？", "肯定の言葉、上質な時間、贈り物、奉仕の行動、身体的なふれあいで、愛の表現と受け取り方を整理する関係コミュニケーションの枠組みです。"),
        ("リチュアルはどれくらいかかりますか？", "首頁のリチュアルは 15 問で、通常 2 から 3 分です。結果は会話の入口であり、固定ラベルではありません。"),
        ("愛の言語は変わりますか？", "変わります。ストレス、関係段階、距離、過去の傷、生活役割によって、今必要な愛の言語は変化します。"),
        ("相手と守護者が違う時は？", "違いは失敗ではなく翻訳です。自分がどう受け取るかを伝え、相手ができる小さな行動を一つ決めます。"),
    ],
    "ko": [
        ("다섯 가지 사랑의 언어란?", "인정의 말, 함께하는 시간, 선물 받기, 봉사의 행동, 스킨십으로 사랑을 표현하고 받는 방식을 정리하는 관계 대화 프레임입니다."),
        ("의식은 얼마나 걸리나요?", "홈의 의식은 15문항이며 보통 2-3분이면 끝납니다. 결과는 대화의 시작점이지 고정 라벨이 아닙니다."),
        ("사랑의 언어는 바뀔 수 있나요?", "네. 스트레스, 관계 단계, 거리, 과거 상처, 생활 역할에 따라 지금 필요한 사랑의 언어가 달라질 수 있습니다."),
        ("상대와 수호자가 다르면?", "차이는 실패가 아니라 번역 과제입니다. 내가 사랑을 받는 방식을 말하고, 상대가 할 수 있는 작은 행동 하나를 정하세요."),
    ],
    "es": [
        ("Qué son los cinco lenguajes del amor?", "Son un marco de comunicación relacional: palabras de afirmación, tiempo de calidad, recibir regalos, actos de servicio y contacto físico. LoveTypes los convierte en guardianas para recordarlos y usarlos mejor."),
        ("Cuánto dura el ritual?", "El ritual de inicio tiene 15 señales y suele tomar 2 a 3 minutos. Usa el resultado para iniciar conversación, no como etiqueta fija."),
        ("Puede cambiar un lenguaje del amor?", "Sí. Estrés, etapa de relación, distancia, heridas previas y roles de vida pueden cambiar lo que hoy te hace sentir amada."),
        ("Qué pasa si mi pareja tiene otra guardiana?", "La diferencia no es fracaso; es traducción. Nombra cómo recibes amor y pide una acción pequeña que la otra persona sí pueda hacer."),
    ],
}


LUNA_USE_CASES = {
    "zh": [
        ("睡前反思", "把白天沒說完的感受放進比較安靜的位置，不急著做判斷。"),
        ("吵架後冷卻", "先讓身體降噪，再回到一句可被接住的修復請求。"),
        ("關係日記", "用 Luna 當背景，記下今天哪一種愛之語最需要被照顧。"),
        ("測驗後整理", "完成命運儀式後，陪你把守護者結果整理成下一步。"),
    ],
    "en": [
        ("Before sleep", "Place the day's unfinished feelings somewhere quieter before judging them."),
        ("After conflict", "Let the body settle before returning to one repair request someone can receive."),
        ("Relationship journal", "Use Luna as a background while noting which love language needed care today."),
        ("After the ritual", "After the quiz, turn the guardian result into one next step."),
    ],
    "ja": [
        ("眠る前の内省", "判断を急がず、日中に残った感情を静かな場所へ置きます。"),
        ("衝突後の冷却", "体を落ち着かせてから、届く修復のお願いへ戻ります。"),
        ("関係日記", "Luna を背景に、今日ケアしたい愛の言語を書き留めます。"),
        ("診断後の整理", "儀式の結果を、守護者から次の一歩へ整理します。"),
    ],
    "ko": [
        ("잠들기 전 성찰", "하루의 남은 감정을 조용한 곳에 두고 판단을 서두르지 않습니다."),
        ("다툼 뒤 식히기", "몸을 먼저 안정시킨 뒤 받을 수 있는 회복 요청으로 돌아갑니다."),
        ("관계 일기", "Luna를 배경으로 오늘 어떤 사랑의 언어가 돌봄이 필요했는지 적습니다."),
        ("의식 뒤 정리", "테스트 결과를 수호자에서 다음 한 걸음으로 정리합니다."),
    ],
    "es": [
        ("Antes de dormir", "Deja las emociones pendientes del día en un lugar más tranquilo antes de juzgarlas."),
        ("Después del conflicto", "Permite que el cuerpo se calme antes de volver a una petición de reparación recibible."),
        ("Diario relacional", "Usa Luna de fondo mientras anotas qué lenguaje del amor necesitó cuidado hoy."),
        ("Después del ritual", "Después del test, convierte el resultado de guardiana en un siguiente paso."),
    ],
}


LUNA_USE_CASE_ACTIONS = {
    "zh": [
        ("寫進修復計畫", "repair-plan"),
        ("閱讀修復指南", "guides/repair-after-conflict"),
        ("查看補給路線", "resources"),
        ("回到命運儀式", "#quiz-section"),
    ],
    "en": [
        ("Use repair plan", "repair-plan"),
        ("Read repair guide", "guides/repair-after-conflict"),
        ("View supply route", "resources"),
        ("Return to ritual", "#quiz-section"),
    ],
    "ja": [
        ("修復プランへ", "repair-plan"),
        ("修復ガイドを読む", "guides/repair-after-conflict"),
        ("補給ルートを見る", "resources"),
        ("リチュアルへ戻る", "#quiz-section"),
    ],
    "ko": [
        ("회복 계획 쓰기", "repair-plan"),
        ("회복 가이드 읽기", "guides/repair-after-conflict"),
        ("보급 루트 보기", "resources"),
        ("의식으로 돌아가기", "#quiz-section"),
    ],
    "es": [
        ("Usar plan", "repair-plan"),
        ("Leer reparación", "guides/repair-after-conflict"),
        ("Ver ruta", "resources"),
        ("Volver al ritual", "#quiz-section"),
    ],
}


LUNA_NIGHT_PROTOCOL = {
    "zh": {
        "eyebrow": "NIGHT SUPPLY PROTOCOL",
        "title": "三種時刻，選一盞 Luna 低光",
        "intro": "Luna 的用途不是把關係問題聽到消失，而是讓你在情緒最滿的時候，還能選一個可行的下一步。",
        "steps": [
            ("1", "睡前整理", "先聽一段安定音樂，把今天最刺的一句話寫成感受，不急著傳出去。", "寫進修復計畫", "repair-plan"),
            ("2", "衝突後降噪", "讓身體慢下來，再把抱怨翻成一句可被接住的小請求。", "閱讀修復指南", "guides/repair-after-conflict"),
            ("3", "測驗後承接", "如果剛認領守護者，先選對應補給路線，不一次買齊或修完整段關係。", "選補給路線", "resources"),
        ],
    },
    "en": {
        "eyebrow": "NIGHT SUPPLY PROTOCOL",
        "title": "Three moments, one low Luna light",
        "intro": "Luna is not for listening relationship problems away. It helps you choose one doable next step when feelings are loud.",
        "steps": [
            ("1", "Before sleep", "Listen briefly, then write the sharpest sentence of the day as a feeling before sending nothing yet.", "Use repair plan", "repair-plan"),
            ("2", "After conflict", "Slow the body down, then translate one complaint into a small request someone can receive.", "Read repair guide", "guides/repair-after-conflict"),
            ("3", "After the quiz", "If you just recognized a guardian, choose the matching supply route instead of trying to fix everything.", "Choose supply route", "resources"),
        ],
    },
    "ja": {
        "eyebrow": "NIGHT SUPPLY PROTOCOL",
        "title": "三つの場面に、Luna の低い灯りを一つ",
        "intro": "Luna は関係の問題を音楽で消すためではありません。感情が大きい時に、できる次の一歩を選ぶための灯りです。",
        "steps": [
            ("1", "眠る前の整理", "短く聴いてから、今日いちばん刺さった言葉を送らずに感情として書きます。", "修復プランへ", "repair-plan"),
            ("2", "衝突後の静けさ", "身体をゆっくりさせ、文句を相手が受け取れる小さなお願いへ翻訳します。", "修復ガイドを読む", "guides/repair-after-conflict"),
            ("3", "診断後の受け止め", "守護者を認領したら、すべてを直そうとせず対応する補給ルートを一つ選びます。", "補給ルートを選ぶ", "resources"),
        ],
    },
    "ko": {
        "eyebrow": "NIGHT SUPPLY PROTOCOL",
        "title": "세 순간에 Luna의 낮은 등불 하나",
        "intro": "Luna는 관계 문제를 음악으로 없애는 도구가 아닙니다. 감정이 클 때 가능한 다음 한 걸음을 고르게 돕습니다.",
        "steps": [
            ("1", "잠들기 전 정리", "짧게 들은 뒤 오늘 가장 아팠던 문장을 보내지 말고 감정으로 적습니다.", "회복 계획 쓰기", "repair-plan"),
            ("2", "다툼 뒤 낮추기", "몸을 늦춘 다음 불평 하나를 받을 수 있는 작은 요청으로 바꿉니다.", "회복 가이드 읽기", "guides/repair-after-conflict"),
            ("3", "테스트 뒤 연결", "수호자를 확인했다면 모든 것을 고치려 하지 말고 맞는 보급 루트를 하나 고릅니다.", "보급 루트 선택", "resources"),
        ],
    },
    "es": {
        "eyebrow": "NIGHT SUPPLY PROTOCOL",
        "title": "Tres momentos, una luz baja de Luna",
        "intro": "Luna no sirve para borrar problemas de relación con música. Ayuda a elegir un siguiente paso posible cuando las emociones están altas.",
        "steps": [
            ("1", "Antes de dormir", "Escucha un momento y escribe la frase más punzante del día como emoción, sin enviarla todavía.", "Usar plan", "repair-plan"),
            ("2", "Después del conflicto", "Baja el ritmo del cuerpo y traduce una queja en una petición pequeña y recibible.", "Leer reparación", "guides/repair-after-conflict"),
            ("3", "Después del test", "Si acabas de reconocer una guardiana, elige su ruta de suministro sin intentar arreglar todo.", "Elegir ruta", "resources"),
        ],
    },
}


LUNA_GUARDIAN_FLOW = {
    "zh": {
        "eyebrow": "GUARDIAN NIGHT SUPPLY",
        "title": "依你的守護者，選一種夜間整理方式",
        "intro": "Luna 不替你解決關係，但能把情緒降到可以書寫、可以開口、可以選補給的音量。",
        "practice": "今晚整理",
        "repair": "寫進修復計畫",
        "route": "查看補給路線",
        "items": {
            "iris": "把想聽見的肯定句寫下來，先分清楚：我需要被看見，還是需要對方立刻同意我。",
            "noah": "回想今天哪一刻最需要陪伴，把「希望你在」縮成一個十五分鐘可完成的邀請。",
            "vivian": "記下一個被記得或沒被記得的細節，確認你要的是心意證據，不是價格證明。",
            "claire": "把疲憊拆成一件具體可請求的事，寫下時間、動作與完成標準。",
            "dora": "先感覺身體是否安全，再寫下一句同意與靠近的界線句。",
        },
    },
    "en": {
        "eyebrow": "GUARDIAN NIGHT SUPPLY",
        "title": "Choose a night practice by guardian",
        "intro": "Luna does not fix the relationship for you. It lowers the noise so you can write, ask, and choose one supply clearly.",
        "practice": "Tonight's practice",
        "repair": "Add to repair plan",
        "route": "View supply route",
        "items": {
            "iris": "Write the affirmation you want to hear, then separate being seen from needing immediate agreement.",
            "noah": "Name the moment you needed presence today, then shrink it into one fifteen-minute invitation.",
            "vivian": "Record one remembered or missed detail, and check whether you need proof of care rather than proof of price.",
            "claire": "Break tiredness into one concrete request with time, action, and a done condition.",
            "dora": "Notice whether your body feels safe, then write one consent and closeness boundary sentence.",
        },
    },
    "ja": {
        "eyebrow": "GUARDIAN NIGHT SUPPLY",
        "title": "守護者ごとに夜の整え方を選ぶ",
        "intro": "Luna は関係を代わりに直しません。書く、頼む、補給を一つ選ぶために、感情の音量を下げる灯りです。",
        "practice": "今夜の整理",
        "repair": "修復プランへ書く",
        "route": "補給ルートを見る",
        "items": {
            "iris": "聞きたい肯定の言葉を書き、自分は見てもらいたいのか、すぐ同意してほしいのかを分けます。",
            "noah": "今日いちばん一緒にいてほしかった瞬間を、一つの十五分の誘いへ縮めます。",
            "vivian": "覚えてもらえた、または忘れられた細部を書き、欲しいのが価格ではなく心意の証拠か確認します。",
            "claire": "疲れを一つの具体的なお願いに分け、時間、行動、完了条件を書きます。",
            "dora": "身体が安全かを先に感じ、同意と近さの境界文を一つ書きます。",
        },
    },
    "ko": {
        "eyebrow": "GUARDIAN NIGHT SUPPLY",
        "title": "수호자에 맞는 밤 정리법 선택",
        "intro": "Luna가 관계를 대신 고치지는 않습니다. 쓰고, 요청하고, 보급 하나를 고를 수 있도록 감정의 소음을 낮춥니다.",
        "practice": "오늘 밤 정리",
        "repair": "회복 계획에 쓰기",
        "route": "보급 루트 보기",
        "items": {
            "iris": "듣고 싶은 인정의 말을 쓰고, 보이고 싶은 것과 즉시 동의받고 싶은 것을 나눕니다.",
            "noah": "오늘 가장 함께 있어 주길 바란 순간을 15분 초대로 줄입니다.",
            "vivian": "기억되었거나 놓친 세부를 적고, 가격 증명이 아니라 마음의 증거가 필요한지 확인합니다.",
            "claire": "피로를 시간, 행동, 완료 기준이 있는 구체적 요청 하나로 나눕니다.",
            "dora": "몸이 안전한지 먼저 느끼고, 동의와 가까움의 경계 문장을 하나 씁니다.",
        },
    },
    "es": {
        "eyebrow": "GUARDIAN NIGHT SUPPLY",
        "title": "Elige una práctica nocturna por guardiana",
        "intro": "Luna no arregla la relación por ti. Baja el ruido para que puedas escribir, pedir y elegir un recurso con claridad.",
        "practice": "Práctica de esta noche",
        "repair": "Añadir al plan",
        "route": "Ver ruta de suministro",
        "items": {
            "iris": "Escribe la afirmación que quieres oír y separa ser vista de necesitar acuerdo inmediato.",
            "noah": "Nombra el momento en que necesitaste presencia y conviértelo en una invitación de quince minutos.",
            "vivian": "Anota un detalle recordado u olvidado y revisa si necesitas prueba de cuidado, no de precio.",
            "claire": "Convierte el cansancio en una petición concreta con tiempo, acción y condición de terminado.",
            "dora": "Nota si tu cuerpo se siente seguro y escribe una frase de consentimiento y límite de cercanía.",
        },
    },
}


LUNA_OFFER = {
    "zh": {
        "eyebrow": "LUNA SUPPLY ENTRY",
        "title": "先免費聆聽，再留下夜間補給需求",
        "intro": "Luna 目前先作為免費聆聽與關係整理入口。練習卡已可在收藏室列印；若你需要離線音檔、桌布或睡前流程，請用信箱留下需求。未來補給會以不承諾療效、不取代諮商的方式呈現。",
        "items": [
            ("免費聆聽", "先用公開音樂陪你睡前書寫、吵架後冷卻，確認這種節奏是否真的適合你。"),
            ("接回守護者路線", "聽完後回到你的守護者補給路線，只選一個小任務，不把所有問題一次修完。"),
            ("未來補給通知", "如果你想要 Luna 離線音檔、手機桌布或睡前流程，可以先用聯絡信箱留下需求。"),
        ],
        "listen": "免費聆聽 Luna",
        "resources": "回到補給站",
        "contact": "加入夜間補給需求",
    },
    "en": {
        "eyebrow": "LUNA SUPPLY ENTRY",
        "title": "Listen free first, then request a night supply pack",
        "intro": "Luna is currently a free listening and reflection doorway. Printable practice cards already live in the keepsake hall; if you want offline audio, wallpapers, or bedtime flows, use the contact inbox. Future supplies will support repair without promising outcomes or replacing counseling.",
        "items": [
            ("Free listening", "Use the public music for bedtime journaling or post-conflict cooling, then notice whether the rhythm truly fits you."),
            ("Return to your route", "After listening, return to your guardian supply route and choose one small task instead of repairing everything at once."),
            ("Future supply note", "If you want offline Luna audio, phone wallpapers, or bedtime flows, use the contact inbox to tell us what would help."),
        ],
        "listen": "Listen to Luna free",
        "resources": "Return to supplies",
        "contact": "Request night supply",
    },
    "ja": {
        "eyebrow": "LUNA SUPPLY ENTRY",
        "title": "まず無料で聴き、夜の補給希望を送る",
        "intro": "Luna は現在、無料で聴ける内省の入口です。印刷できる練習カードはコレクション室にあります。オフライン音源、壁紙、就寝前フローが必要なら連絡先へ希望を送れます。今後の補給も効果を約束せず、相談支援の代わりにはしません。",
        "items": [
            ("無料で聴く", "公開音楽を就寝前の日記や衝突後の静けさに使い、このリズムが自分に合うか確かめます。"),
            ("守護者ルートへ戻る", "聴いた後は守護者の補給ルートへ戻り、一つの小さな課題だけを選びます。"),
            ("今後の補給希望", "Luna のオフライン音源、スマホ壁紙、就寝前フローが必要なら、連絡先へ希望を送れます。"),
        ],
        "listen": "Luna を無料で聴く",
        "resources": "補給へ戻る",
        "contact": "夜の補給を希望する",
    },
    "ko": {
        "eyebrow": "LUNA SUPPLY ENTRY",
        "title": "먼저 무료로 듣고 밤 보급 요청 남기기",
        "intro": "Luna는 현재 무료 청취와 관계 성찰의 입구입니다. 인쇄용 연습 카드는 이미 소장실에 있습니다. 오프라인 음원, 배경화면, 잠들기 전 흐름이 필요하다면 연락 메일로 알려 주세요. 향후 보급도 결과를 약속하거나 상담을 대신하지 않습니다.",
        "items": [
            ("무료 청취", "공개 음악을 잠들기 전 기록이나 다툼 뒤 진정에 사용하고, 이 리듬이 정말 맞는지 확인합니다."),
            ("수호자 루트로 돌아가기", "들은 뒤에는 수호자 보급 루트로 돌아가 작은 과제 하나만 고릅니다."),
            ("미래 보급 알림", "Luna 오프라인 음원, 휴대폰 배경화면, 잠들기 전 흐름이 필요하다면 연락 메일로 알려 주세요."),
        ],
        "listen": "Luna 무료 듣기",
        "resources": "보급소로 돌아가기",
        "contact": "밤 보급 요청하기",
    },
    "es": {
        "eyebrow": "LUNA SUPPLY ENTRY",
        "title": "Escucha gratis primero y pide un recurso nocturno",
        "intro": "Luna funciona ahora como entrada gratuita de escucha y reflexión. Las tarjetas imprimibles ya están en la sala de recuerdos; si quieres audio sin conexión, fondos o rutinas nocturnas, usa el correo de contacto. Cualquier recurso futuro apoyará la práctica sin prometer resultados ni reemplazar terapia.",
        "items": [
            ("Escucha gratis", "Usa la música pública para escribir antes de dormir o enfriar después de un conflicto y nota si el ritmo te sirve."),
            ("Vuelve a tu ruta", "Después de escuchar, vuelve a la ruta de tu guardiana y elige una tarea pequeña, no todo a la vez."),
            ("Aviso de recursos futuros", "Si quieres audio Luna sin conexión, fondos móviles o rutinas nocturnas, usa el correo de contacto para decirnos qué ayudaría."),
        ],
        "listen": "Escuchar Luna gratis",
        "resources": "Volver a recursos",
        "contact": "Pedir recurso nocturno",
    },
}


LUNA_RESUME = {
    "zh": {
        "eyebrow": "YOUR NIGHT SUPPLY",
        "title": "今晚跟著你的守護者降噪",
        "intro": "你上次的測驗結果可以直接變成今晚的整理方式。先讓情緒安靜，再把一個小任務寫進修復計畫。",
        "practice": "今晚練習",
        "repair": "寫進修復計畫",
        "route": "查看補給路線",
        "book": "延伸書卷",
    },
    "en": {
        "eyebrow": "YOUR NIGHT SUPPLY",
        "title": "Let your guardian guide tonight's calm",
        "intro": "Your last quiz result can become tonight's reflection path. Lower the noise first, then place one small task into the repair plan.",
        "practice": "Tonight's practice",
        "repair": "Add to repair plan",
        "route": "View supply route",
        "book": "Extended book",
    },
    "ja": {
        "eyebrow": "YOUR NIGHT SUPPLY",
        "title": "今夜は守護者に合わせて静める",
        "intro": "前回の診断結果を、今夜の内省ルートにできます。まず感情の音量を下げ、小さな課題を修復プランへ置きます。",
        "practice": "今夜の練習",
        "repair": "修復プランへ書く",
        "route": "補給ルートを見る",
        "book": "本で深める",
    },
    "ko": {
        "eyebrow": "YOUR NIGHT SUPPLY",
        "title": "오늘 밤은 수호자에 맞춰 낮추기",
        "intro": "마지막 테스트 결과를 오늘 밤 성찰 루트로 바꿀 수 있습니다. 먼저 소음을 낮추고 작은 과제 하나를 회복 계획에 적으세요.",
        "practice": "오늘 밤 연습",
        "repair": "회복 계획에 쓰기",
        "route": "보급 루트 보기",
        "book": "책으로 더 보기",
    },
    "es": {
        "eyebrow": "YOUR NIGHT SUPPLY",
        "title": "Deja que tu guardiana calme esta noche",
        "intro": "Tu último resultado puede convertirse en la ruta de reflexión de esta noche. Baja el ruido primero y coloca una tarea pequeña en el plan.",
        "practice": "Práctica de esta noche",
        "repair": "Añadir al plan",
        "route": "Ver ruta",
        "book": "Libro para seguir",
    },
}


CONTACT_REQUESTS = {
    "zh": {
        "eyebrow": "REQUEST COMPASS",
        "title": "加入守護者補給等待清單",
        "intro": "如果你是從 Luna、收藏室或守護者補給路線來到這裡，請先選一種需求寄信。練習卡已可免費列印；這裡會幫我們判斷下一批自有補給應優先整理離線音檔、手機桌布、短儀式，還是印刷收藏包。",
        "items": [
            ("Luna 下載包", "希望能離線聆聽、收藏音檔，或把 Luna 放進固定睡前儀式。"),
            ("手機桌布", "希望把自己的守護者留在鎖定畫面，作為睡前、衝突後或關係日記的入口。"),
            ("短儀式或印刷包", "希望有 5 到 10 分鐘流程，或把五張守護者練習卡整理成可收藏的印刷包。"),
        ],
        "note": "來信時可附上你的守護者、想使用的情境、裝置與願意收藏的格式。LoveTypes 不提供緊急支援、醫療建議或諮商替代。",
        "cta": "寄出補給等待清單需求",
        "subject": "LoveTypes 守護者補給等待清單",
        "body": "我的守護者：\n我想優先收到的補給：Luna 下載包 / 手機桌布 / 短儀式或印刷包\n使用情境：\n使用裝置：\n我會願意收藏的格式：\n",
    },
    "en": {
        "eyebrow": "REQUEST COMPASS",
        "title": "Join the guardian supply waitlist",
        "intro": "If you arrived from Luna, keepsakes, or a guardian supply route, choose one request before writing. Printable practice cards are already free; this helps us decide whether offline audio, wallpapers, short rituals, or printed collectible packs should be prepared next.",
        "items": [
            ("Luna download pack", "You want offline listening, a saved audio set, or a stable bedtime ritual with Luna."),
            ("Phone wallpaper", "You want your guardian on the lock screen as a doorway for bedtime, post-conflict cooling, or relationship journaling."),
            ("Short ritual or printed pack", "You want a 5 to 10 minute sequence or a collectible printed set of the five guardian practice cards."),
        ],
        "note": "Include your guardian, use case, device, and the format you would actually keep. LoveTypes does not provide emergency support, medical advice, or a replacement for counseling.",
        "cta": "Send supply waitlist request",
        "subject": "LoveTypes guardian supply waitlist",
        "body": "My guardian:\nSupply I want first: Luna download pack / phone wallpaper / short ritual or printed pack\nUse case:\nDevice:\nFormat I would actually keep:\n",
    },
    "ja": {
        "eyebrow": "REQUEST COMPASS",
        "title": "守護者補給の待機リストへ希望を送る",
        "intro": "Luna、コレクション室、守護者の補給ルートから来た場合は、一つの希望を選んで送ってください。印刷できる練習カードはすでに無料です。ここではオフライン音源、壁紙、短い儀式、印刷コレクションの優先順位を判断します。",
        "items": [
            ("Luna ダウンロードパック", "オフラインで聴きたい、音源を保存したい、Luna を就寝前の儀式に入れたい。"),
            ("スマホ壁紙", "守護者をロック画面に置き、就寝前、衝突後、関係日記の入口にしたい。"),
            ("短い儀式や印刷セット", "5 から 10 分の手順、または五枚の守護者練習カードを印刷コレクションとして残したい。"),
        ],
        "note": "守護者、使いたい場面、端末、実際に保存したい形式を書ける範囲で添えてください。LoveTypes は緊急支援、医療助言、相談支援の代替を提供しません。",
        "cta": "補給待機リストへ送る",
        "subject": "LoveTypes 守護者補給の待機リスト",
        "body": "私の守護者：\n最初にほしい補給：Luna ダウンロードパック / スマホ壁紙 / 短い儀式や印刷セット\n使いたい場面：\n端末：\n実際に保存したい形式：\n",
    },
    "ko": {
        "eyebrow": "REQUEST COMPASS",
        "title": "수호자 보급 대기 목록에 요청 남기기",
        "intro": "Luna, 소장실, 수호자 보급 루트에서 왔다면 한 가지 요청을 골라 보내 주세요. 인쇄용 연습 카드는 이미 무료입니다. 여기서는 오프라인 음원, 배경화면, 짧은 의식, 인쇄 소장팩 중 무엇을 먼저 준비할지 판단합니다.",
        "items": [
            ("Luna 다운로드 팩", "오프라인으로 듣거나 음원을 보관하고, Luna를 고정된 잠들기 전 의식에 넣고 싶을 때."),
            ("휴대폰 배경화면", "수호자를 잠금 화면에 두고 잠들기 전, 다툼 뒤, 관계 일기의 입구로 쓰고 싶을 때."),
            ("짧은 의식 또는 인쇄 세트", "5-10분 순서나 다섯 수호자 연습 카드를 인쇄 소장팩으로 남기고 싶을 때."),
        ],
        "note": "가능하다면 수호자, 사용 장면, 기기, 실제로 보관할 형식을 함께 적어 주세요. LoveTypes는 긴급 지원, 의료 조언, 상담 대체를 제공하지 않습니다.",
        "cta": "보급 대기 목록 요청 보내기",
        "subject": "LoveTypes 수호자 보급 대기 목록",
        "body": "나의 수호자:\n먼저 받고 싶은 보급: Luna 다운로드 팩 / 휴대폰 배경화면 / 짧은 의식 또는 인쇄 세트\n사용 장면:\n기기:\n실제로 보관할 형식:\n",
    },
    "es": {
        "eyebrow": "REQUEST COMPASS",
        "title": "Únete a la lista de recursos de guardianas",
        "intro": "Si llegaste desde Luna, recuerdos o una ruta de guardiana, elige una petición antes de escribir. Las tarjetas imprimibles ya son gratuitas; esto nos ayuda a decidir si preparar después audio sin conexión, fondos, rituales breves o packs impresos.",
        "items": [
            ("Pack Luna descargable", "Quieres escuchar sin conexión, guardar los audios o usar Luna como ritual estable antes de dormir."),
            ("Fondo móvil", "Quieres llevar tu guardiana en la pantalla de bloqueo como entrada para dormir, calmarte o escribir un diario de relación."),
            ("Ritual breve o pack impreso", "Quieres una secuencia de 5 a 10 minutos o un set impreso coleccionable de las cinco tarjetas de práctica."),
        ],
        "note": "Incluye tu guardiana, situación de uso, dispositivo y el formato que guardarías de verdad. LoveTypes no ofrece apoyo de emergencia, consejo médico ni sustituto de terapia.",
        "cta": "Enviar petición de lista",
        "subject": "Lista de espera de recursos LoveTypes",
        "body": "Mi guardiana:\nRecurso que quiero primero: Pack Luna descargable / fondo móvil / ritual breve o pack impreso\nSituación de uso:\nDispositivo:\nFormato que guardaría de verdad:\n",
    },
}


CONTACT_SUBJECT_LABELS = {
    "zh": "建議郵件主旨",
    "en": "Suggested email subject",
    "ja": "推奨メール件名",
    "ko": "권장 메일 제목",
    "es": "Asunto sugerido",
}

CONTACT_TEMPLATE_LABELS = {
    "zh": {"label": "可複製信件模板", "copy": "複製模板", "copied": "已複製"},
    "en": {"label": "Copyable email template", "copy": "Copy template", "copied": "Copied"},
    "ja": {"label": "コピーできるメール本文", "copy": "本文をコピー", "copied": "コピーしました"},
    "ko": {"label": "복사 가능한 메일 템플릿", "copy": "템플릿 복사", "copied": "복사됨"},
    "es": {"label": "Plantilla copiable", "copy": "Copiar plantilla", "copied": "Copiado"},
}


CONTACT_RESULT_HANDOFF = {
    "zh": {
        "eyebrow": "RESULT HANDOFF",
        "title": "用上次測驗結果寄出補給需求",
        "intro": "這台裝置保存了你的守護者結果。你可以把結果、補給路線與想要的收藏物一起帶進信件，不必重新整理。",
        "subject": "LoveTypes 守護者補給需求",
        "send": "寄出個人化補給需求",
        "copy": "複製個人化需求",
        "copied": "已複製需求",
        "route": "查看補給路線",
        "card": "開啟收藏卡",
        "plan": "回到修復計畫",
        "clear": "清除上次結果",
        "guardian": "我的守護者",
        "supply": "補給路線",
        "mission": "免費任務",
        "luna": "Luna 使用場景",
        "keepsake": "想要的收藏物",
        "context": "我想使用在這個情境",
        "keepsake_hint": "手機桌布 / 7 分鐘短儀式 / Luna 下載包 / 印刷收藏包",
    },
    "en": {
        "eyebrow": "RESULT HANDOFF",
        "title": "Send a supply request from your last result",
        "intro": "This device has your guardian result. Carry the result, route, and collectible request into one email without rebuilding the context.",
        "subject": "LoveTypes guardian supply request",
        "send": "Send personalized supply request",
        "copy": "Copy personalized request",
        "copied": "Request copied",
        "route": "View supply route",
        "card": "Open keepsake card",
        "plan": "Return to repair plan",
        "clear": "Clear last result",
        "guardian": "My guardian",
        "supply": "Supply route",
        "mission": "Free task",
        "luna": "Luna use case",
        "keepsake": "Collectible I want",
        "context": "I would use it in this situation",
        "keepsake_hint": "Mobile wallpaper / 7-minute ritual / Luna download pack / printed collectible pack",
    },
    "ja": {
        "eyebrow": "RESULT HANDOFF",
        "title": "前回の結果から補給リクエストを送る",
        "intro": "この端末には守護者の結果が残っています。結果、補給ルート、欲しいコレクションを一つのメールに入れられます。",
        "subject": "LoveTypes 守護者の補給リクエスト",
        "send": "個別補給リクエストを送る",
        "copy": "個別リクエストをコピー",
        "copied": "コピーしました",
        "route": "補給ルートを見る",
        "card": "コレクションカードを開く",
        "plan": "修復プランへ戻る",
        "clear": "前回の結果を消す",
        "guardian": "私の守護者",
        "supply": "補給ルート",
        "mission": "無料の課題",
        "luna": "Luna の使用場面",
        "keepsake": "欲しいコレクション",
        "context": "この場面で使いたい",
        "keepsake_hint": "スマホ壁紙 / 7分の短い儀式 / Luna ダウンロード / 印刷コレクション",
    },
    "ko": {
        "eyebrow": "RESULT HANDOFF",
        "title": "지난 결과로 보급 요청 보내기",
        "intro": "이 기기에 수호자 결과가 남아 있습니다. 결과, 보급 루트, 원하는 소장물을 한 메일에 담을 수 있습니다.",
        "subject": "LoveTypes 수호자 보급 요청",
        "send": "개인화 보급 요청 보내기",
        "copy": "개인화 요청 복사",
        "copied": "요청 복사됨",
        "route": "보급 루트 보기",
        "card": "소장 카드 열기",
        "plan": "회복 계획으로 돌아가기",
        "clear": "지난 결과 지우기",
        "guardian": "나의 수호자",
        "supply": "보급 루트",
        "mission": "무료 과제",
        "luna": "Luna 사용 장면",
        "keepsake": "원하는 소장물",
        "context": "이 상황에서 사용하고 싶어요",
        "keepsake_hint": "모바일 배경화면 / 7분 짧은 의식 / Luna 다운로드 팩 / 인쇄 소장팩",
    },
    "es": {
        "eyebrow": "RESULT HANDOFF",
        "title": "Enviar una solicitud desde tu último resultado",
        "intro": "Este dispositivo conserva tu resultado. Puedes llevar la guardiana, ruta y recurso coleccionable a un solo correo.",
        "subject": "Solicitud de recurso de guardiana LoveTypes",
        "send": "Enviar solicitud personalizada",
        "copy": "Copiar solicitud personalizada",
        "copied": "Solicitud copiada",
        "route": "Ver ruta",
        "card": "Abrir tarjeta",
        "plan": "Volver al plan",
        "clear": "Borrar resultado",
        "guardian": "Mi guardiana",
        "supply": "Ruta de recurso",
        "mission": "Tarea gratuita",
        "luna": "Uso de Luna",
        "keepsake": "Recurso coleccionable que quiero",
        "context": "Lo usaría en esta situación",
        "keepsake_hint": "Fondo móvil / ritual de 7 minutos / pack Luna / pack impreso",
    },
}


CONTACT_REPAIR_REPORTS = {
    "zh": {
        "eyebrow": "GARDEN REPAIR DESK",
        "title": "回報庭園中需要修復的地方",
        "intro": "如果你在 LoveTypes 途中遇到斷掉的路、錯頻的翻譯、無法點開的補給，或手機版閱讀不順，請把位置寄給我們。這會直接進入下一輪網站修復清單。",
        "items": [
            ("頁面或測驗異常", "例如按鈕無反應、結果沒有顯示、頁面跳轉錯誤，或某個守護者入口無法開啟。"),
            ("補給或聯盟連結問題", "例如書卷連結失效、導向不明、價格或地區資訊看起來不一致。"),
            ("翻譯與語氣錯頻", "例如多語頁內容重複、角色語氣不一致，或某段文字不符合守護者宇宙設定。"),
            ("手機版與無障礙", "例如文字太擠、卡片過長、焦點不清楚、圖片遮住內容，或螢幕閱讀體驗不佳。"),
        ],
        "note": "來信時請附上頁面網址、裝置與瀏覽器、你預期看到什麼、實際發生什麼。這個信箱處理網站修復與內容回報，不提供緊急支援或諮商替代。",
        "cta": "回報網站修復線索",
        "subject": "LoveTypes 網站修復回報",
        "body": "頁面網址：\n裝置與瀏覽器：\n我預期看到：\n實際發生：\n補充截圖或說明：\n",
    },
    "en": {
        "eyebrow": "GARDEN REPAIR DESK",
        "title": "Report a place in the garden that needs repair",
        "intro": "If a path breaks while you move through LoveTypes, send us the location. Broken pages, off-tone translations, stuck supply links, and rough mobile reading all go into the next repair pass.",
        "items": [
            ("Page or quiz issue", "A button does not respond, the result does not appear, navigation lands in the wrong place, or a guardian entrance will not open."),
            ("Supply or affiliate link", "A book link is broken, the destination feels unclear, or price and regional information look inconsistent."),
            ("Translation or tone mismatch", "A multilingual page repeats content, a guardian voice feels inconsistent, or a paragraph does not fit the guardian universe."),
            ("Mobile and accessibility", "Text feels cramped, cards run too long, focus is unclear, images cover content, or screen-reader flow feels rough."),
        ],
        "note": "Please include the page URL, device and browser, what you expected, and what happened instead. This inbox handles site repair and content reports, not emergency support or counseling replacement.",
        "cta": "Send site repair report",
        "subject": "LoveTypes site repair report",
        "body": "Page URL:\nDevice and browser:\nWhat I expected:\nWhat happened instead:\nExtra screenshot or notes:\n",
    },
    "ja": {
        "eyebrow": "GARDEN REPAIR DESK",
        "title": "庭園で修復が必要な場所を知らせる",
        "intro": "LoveTypes を歩く途中で道が途切れたら、その場所を送ってください。壊れたページ、声のずれた翻訳、開けない補給リンク、読みにくいモバイル表示を次の修復リストに入れます。",
        "items": [
            ("ページや診断の不具合", "ボタンが反応しない、結果が出ない、遷移先が違う、守護者入口が開かない場合。"),
            ("補給やアフィリエイトリンク", "本のリンク切れ、遷移先が分かりにくい、価格や地域情報が合わないように見える場合。"),
            ("翻訳や語り口のずれ", "多言語ページの内容が重複している、守護者の声が揃っていない、世界観に合わない段落がある場合。"),
            ("モバイルとアクセシビリティ", "文字が詰まる、カードが長すぎる、フォーカスが分かりにくい、画像が内容を隠す、読み上げの流れが悪い場合。"),
        ],
        "note": "ページ URL、端末とブラウザ、期待した表示、実際に起きたことを添えてください。この窓口はサイト修復と内容回報用で、緊急支援や相談支援の代替ではありません。",
        "cta": "サイト修復を報告する",
        "subject": "LoveTypes サイト修復の報告",
        "body": "ページ URL：\n端末とブラウザ：\n期待した表示：\n実際に起きたこと：\n補足スクリーンショットやメモ：\n",
    },
    "ko": {
        "eyebrow": "GARDEN REPAIR DESK",
        "title": "정원이 수리해야 할 곳을 알려 주세요",
        "intro": "LoveTypes를 지나가다 길이 끊기거나 번역의 결이 어긋나거나 보급 링크가 열리지 않거나 모바일 읽기가 불편하면 위치를 보내 주세요. 다음 수리 목록에 반영합니다.",
        "items": [
            ("페이지나 테스트 오류", "버튼이 반응하지 않거나 결과가 나오지 않거나 이동 경로가 잘못되거나 수호자 입구가 열리지 않을 때."),
            ("보급 또는 제휴 링크 문제", "책 링크가 끊겼거나 목적지가 불분명하거나 가격과 지역 정보가 맞지 않아 보일 때."),
            ("번역과 목소리의 어긋남", "다국어 페이지 내용이 반복되거나 수호자의 말투가 맞지 않거나 세계관과 맞지 않는 문장이 있을 때."),
            ("모바일과 접근성", "글자가 답답하거나 카드가 너무 길거나 초점이 불명확하거나 이미지가 내용을 가리거나 스크린 리더 흐름이 불편할 때."),
        ],
        "note": "페이지 URL, 기기와 브라우저, 기대한 모습, 실제로 일어난 일을 함께 적어 주세요. 이 메일은 사이트 수리와 콘텐츠 제보용이며 긴급 지원이나 상담 대체를 제공하지 않습니다.",
        "cta": "사이트 수리 제보 보내기",
        "subject": "LoveTypes 사이트 수리 제보",
        "body": "페이지 URL:\n기기와 브라우저:\n기대한 모습:\n실제로 일어난 일:\n추가 스크린샷 또는 메모:\n",
    },
    "es": {
        "eyebrow": "GARDEN REPAIR DESK",
        "title": "Avisa qué parte del jardín necesita reparación",
        "intro": "Si un camino se rompe dentro de LoveTypes, envíanos la ubicación. Páginas rotas, traducciones fuera de tono, enlaces de recursos atascados y lectura móvil incómoda entran en la siguiente reparación.",
        "items": [
            ("Problema de página o test", "Un botón no responde, el resultado no aparece, la navegación llega a un lugar incorrecto o una entrada de guardiana no abre."),
            ("Recurso o enlace afiliado", "Un enlace de libro está roto, el destino no queda claro o la información de precio y región parece inconsistente."),
            ("Traducción o tono desalineado", "Una página multilingüe repite contenido, la voz de una guardiana no coincide o un párrafo no encaja con el universo."),
            ("Móvil y accesibilidad", "El texto queda apretado, las tarjetas son demasiado largas, el foco no es claro, una imagen tapa contenido o la lectura asistida se siente difícil."),
        ],
        "note": "Incluye la URL, dispositivo y navegador, qué esperabas ver y qué ocurrió. Este buzón atiende reparación del sitio y reportes de contenido; no ofrece apoyo de emergencia ni sustituye terapia.",
        "cta": "Enviar reporte de reparación",
        "subject": "Reporte de reparación del sitio LoveTypes",
        "body": "URL de la página:\nDispositivo y navegador:\nQué esperaba ver:\nQué ocurrió:\nCaptura o notas extra:\n",
    },
}


RESOURCE_PATHS = {
    "zh": [("先測驗", "完成 15 道心語，確認目前最需要被接收的愛之語。"), ("再讀守護者", "從結果頁進入對應角色，理解自己為什麼容易在這裡受傷。"), ("最後選補給", "依照當下狀態選擇指南、書卷或 Luna 音樂，不一次修完整座庭園。")],
    "en": [("Take the ritual", "Answer 15 prompts to see the love language you most need received now."), ("Read the guardian", "Use the result page to understand why this area can feel tender."), ("Choose supplies", "Pick a guide, book, or Luna audio for the current moment, not the whole relationship at once.")],
    "ja": [("まず診断", "15問で今いちばん受け取りたい愛の言語を見ます。"), ("守護者を読む", "結果ページから、その領域がなぜ傷つきやすいかを理解します。"), ("補給を選ぶ", "今の状態に合うガイド、本、Luna 音楽を一つ選びます。")],
    "ko": [("먼저 의식", "15문항으로 지금 가장 받고 싶은 사랑의 언어를 봅니다."), ("수호자 읽기", "결과 페이지에서 왜 이 영역이 예민한지 이해합니다."), ("자료 선택", "지금 상태에 맞는 가이드, 책, Luna 음악 중 하나를 고릅니다.")],
    "es": [("Primero ritual", "Responde 15 señales para ver qué lenguaje necesitas recibir ahora."), ("Lee la guardiana", "Desde el resultado entiende por qué esa zona puede doler."), ("Elige recursos", "Toma una guía, libro o audio Luna para el momento actual, no toda la relación de una vez.")],
}


SUPPLY_ENTRY = {
    "zh": {
        "eyebrow": "從結果出發",
        "title": "先取得路線，再選補給",
        "intro": "旅人補給不是書單入口，而是把你的守護者結果接到一個可執行的小任務。先確認路線，再慢慢選指南、Luna 或延伸書卷。",
        "items": [
            ("還沒有結果", "先完成 15 道心語，讓補給站知道該把你帶往哪位守護者。", "開始認領儀式", ""),
            ("已經知道守護者", "直接跳到五條補給路線，選最符合此刻狀態的一條。", "查看五路線", "#supply-routes"),
            ("現在需要安定", "先進入 Luna 夜間補給，把情緒降噪後再決定是否閱讀或購買。", "開啟 Luna", "luna-yoga-music"),
        ],
    },
    "en": {
        "eyebrow": "START FROM YOUR RESULT",
        "title": "Get your route before choosing supplies",
        "intro": "Resources are not just a book list. They turn your guardian result into one doable task, then help you choose a guide, Luna, or an extended book slowly.",
        "items": [
            ("No result yet", "Answer the 15 prompts first so the station knows which guardian route to open.", "Start quiz", ""),
            ("I know my guardian", "Jump to the five supply routes and choose the one that fits this moment.", "View routes", "#supply-routes"),
            ("I need calm first", "Open Luna night supply, lower the noise, then decide whether to read or buy.", "Open Luna", "luna-yoga-music"),
        ],
    },
    "ja": {
        "eyebrow": "結果から始める",
        "title": "結果からルートを決めて補給を選ぶ",
        "intro": "リソースは本の一覧ではありません。守護者の結果を小さな行動へつなぎ、ガイド、Luna、本をゆっくり選ぶための入口です。",
        "items": [
            ("まだ結果がない", "まず15問に答え、どの守護者ルートを開くかを確認します。", "診断を始める", ""),
            ("守護者が分かっている", "五つの補給ルートへ進み、今に合う一つを選びます。", "ルートを見る", "#supply-routes"),
            ("先に落ち着きたい", "Luna の夜の補給で感情のノイズを下げてから、読むか購入するかを決めます。", "Luna を開く", "luna-yoga-music"),
        ],
    },
    "ko": {
        "eyebrow": "결과에서 시작",
        "title": "결과로 루트를 정한 뒤 보급을 고르기",
        "intro": "자료는 단순한 책 목록이 아닙니다. 수호자 결과를 작은 행동 하나로 연결하고, 가이드, Luna, 책을 천천히 고르게 합니다.",
        "items": [
            ("아직 결과가 없다면", "먼저 15문항을 완료해 어떤 수호자 루트를 열지 확인하세요.", "테스트 시작", ""),
            ("수호자를 알고 있다면", "다섯 보급 루트로 이동해 지금 상태에 맞는 하나를 고르세요.", "루트 보기", "#supply-routes"),
            ("먼저 안정이 필요하다면", "Luna 밤 보급으로 감정의 소음을 낮춘 뒤 읽거나 구매할지 결정하세요.", "Luna 열기", "luna-yoga-music"),
        ],
    },
    "es": {
        "eyebrow": "EMPIEZA DESDE TU RESULTADO",
        "title": "Obtén tu ruta antes de elegir recursos",
        "intro": "Recursos no es solo una lista de libros. Convierte tu resultado de guardiana en una tarea posible y luego te ayuda a elegir guía, Luna o libro con calma.",
        "items": [
            ("Aún no tengo resultado", "Responde primero las 15 señales para saber qué ruta de guardiana abrir.", "Iniciar test", ""),
            ("Ya conozco mi guardiana", "Salta a las cinco rutas y elige la que encaja con este momento.", "Ver rutas", "#supply-routes"),
            ("Necesito calma primero", "Abre Luna nocturna, baja el ruido y después decide si leer o comprar.", "Abrir Luna", "luna-yoga-music"),
        ],
    },
}


SECTION_LABELS = {
    "zh": {
        "heart_garden_supplies": "心語庭園補給站",
        "supply_route": "補給路線",
        "traveler_supply": "旅人補給",
        "related_guides": "相關指南",
        "five_guardians": "五位守護者",
        "moonlight_supply": "月光補給",
        "book_relics": "延伸書卷",
        "destiny_ritual": "命運儀式",
        "night_supply_protocol": "夜間補給流程",
        "guardian_night_supply": "守護者夜間補給",
        "luna_supply_entry": "Luna 補給入口",
        "your_night_supply": "你的夜間補給",
        "request_compass": "需求羅盤",
        "garden_repair_desk": "庭園修復台",
        "guardian_compass": "守護者羅盤",
        "choose_by_current_need": "依此刻需求選擇",
        "reading_compass": "閱讀羅盤",
        "guardian_reading_routes": "守護者閱讀路線",
        "supply_compass": "補給羅盤",
        "starter_kit": "初始補給包",
        "supply_wishlist": "補給願望清單",
        "guardian_keepsakes": "守護者收藏卡",
        "guardian_keepsake_hall": "守護者收藏室",
        "heart_garden_pass": "心語庭園通行印",
        "five_domain_theory_compass": "五分域理論羅盤",
        "heart_garden_trust_charter": "心語庭園信任憑證",
        "garden_journey": "庭園旅程",
        "heart_garden_map": "心語庭園地圖",
        "heart_garden_portals": "心語庭園入口",
        "after_ritual": "儀式之後",
        "main_routes": "主要路線",
        "function_rooms": "功能房間",
        "five_domains": "五個分域",
        "field_guides": "分域指南",
        "trust_routes": "信任路線",
        "return_path": "返回路線",
        "safety_boundary_map": "安全邊界地圖",
        "full_policy_notes": "完整政策筆記",
        "home_field_notes": "心語庭園筆記",
        "universe_promise": "宇宙承諾",
        "guardian_field_guides": "守護者分域指南",
        "heart_garden_field_guide": "心語庭園指南",
        "week_route": "一週練習路線",
        "printable_worksheet": "可列印練習表",
        "guardian_routes": "守護者路線",
        "calm_paths": "安定路徑",
        "night_heart_supply": "夜間心語補給",
        "luna_night_supply": "Luna 夜間補給",
        "about_lovetypes": "關於 LoveTypes",
        "love_language_theory": "愛之語理論",
        "love_language_faq": "愛之語 FAQ",
        "keepsake_ritual_route": "收藏祝福返回",
        "keepsake_use_route": "保存分享返回",
        "seven_day_heart_plan": "7 日心語修復計畫",
        "heart_garden_archive": "心語庭園歸檔",
        "not_found_garden": "404 心語庭園",
        "safe_routes": "安全返回路線",
    },
    "en": {
        "heart_garden_supplies": "HEART GARDEN SUPPLIES",
        "supply_route": "SUPPLY ROUTE",
        "traveler_supply": "TRAVELER SUPPLY",
        "related_guides": "RELATED GUIDES",
        "five_guardians": "FIVE GUARDIANS",
        "moonlight_supply": "MOONLIGHT SUPPLY",
        "book_relics": "BOOK RELICS",
        "destiny_ritual": "DESTINY RITUAL",
        "night_supply_protocol": "NIGHT SUPPLY PROTOCOL",
        "guardian_night_supply": "GUARDIAN NIGHT SUPPLY",
        "luna_supply_entry": "LUNA SUPPLY ENTRY",
        "your_night_supply": "YOUR NIGHT SUPPLY",
        "request_compass": "REQUEST COMPASS",
        "garden_repair_desk": "GARDEN REPAIR DESK",
        "guardian_compass": "GUARDIAN COMPASS",
        "choose_by_current_need": "CHOOSE BY CURRENT NEED",
        "reading_compass": "READING COMPASS",
        "guardian_reading_routes": "GUARDIAN READING ROUTES",
        "supply_compass": "SUPPLY COMPASS",
        "starter_kit": "STARTER KIT",
        "supply_wishlist": "SUPPLY WISHLIST",
        "guardian_keepsakes": "GUARDIAN KEEPSAKES",
        "guardian_keepsake_hall": "GUARDIAN KEEPSAKE HALL",
        "heart_garden_pass": "HEART GARDEN PASS",
        "five_domain_theory_compass": "FIVE-DOMAIN THEORY COMPASS",
        "heart_garden_trust_charter": "HEART GARDEN TRUST CHARTER",
        "garden_journey": "GARDEN JOURNEY",
        "heart_garden_map": "HEART GARDEN MAP",
        "heart_garden_portals": "HEART GARDEN PORTALS",
        "after_ritual": "AFTER THE RITUAL",
        "main_routes": "MAIN ROUTES",
        "function_rooms": "FUNCTION ROOMS",
        "five_domains": "FIVE DOMAINS",
        "field_guides": "FIELD GUIDES",
        "trust_routes": "TRUST ROUTES",
        "return_path": "RETURN PATH",
        "safety_boundary_map": "SAFETY BOUNDARY MAP",
        "full_policy_notes": "FULL POLICY NOTES",
        "home_field_notes": "HEART GARDEN FIELD NOTES",
        "universe_promise": "UNIVERSE PROMISE",
        "guardian_field_guides": "GUARDIAN FIELD GUIDES",
        "heart_garden_field_guide": "HEART GARDEN FIELD GUIDE",
        "week_route": "WEEK ROUTE",
        "printable_worksheet": "PRINTABLE WORKSHEET",
        "guardian_routes": "GUARDIAN ROUTES",
        "calm_paths": "CALM PATHS",
        "night_heart_supply": "NIGHT HEART SUPPLY",
        "luna_night_supply": "LUNA NIGHT SUPPLY",
        "about_lovetypes": "ABOUT LOVETYPES",
        "love_language_theory": "LOVE LANGUAGE THEORY",
        "love_language_faq": "LOVE LANGUAGE FAQ",
        "keepsake_ritual_route": "SAVE · BLESS · RETURN",
        "keepsake_use_route": "SAVE · SHARE · RETURN",
        "seven_day_heart_plan": "7-DAY HEART-LANGUAGE PLAN",
        "heart_garden_archive": "HEART GARDEN ARCHIVE",
        "not_found_garden": "404 HEART GARDEN",
        "safe_routes": "SAFE ROUTES",
    },
    "ja": {
        "heart_garden_supplies": "心語の庭の補給所",
        "supply_route": "補給ルート",
        "traveler_supply": "旅人の補給",
        "related_guides": "関連ガイド",
        "five_guardians": "五人の守護者",
        "moonlight_supply": "月光の補給",
        "book_relics": "本の遺物",
        "destiny_ritual": "運命の儀式",
        "night_supply_protocol": "夜の補給手順",
        "guardian_night_supply": "守護者の夜の補給",
        "luna_supply_entry": "Luna 補給入口",
        "your_night_supply": "あなたの夜の補給",
        "request_compass": "リクエスト羅針盤",
        "garden_repair_desk": "庭の修復デスク",
        "guardian_compass": "守護者羅針盤",
        "choose_by_current_need": "今の必要から選ぶ",
        "reading_compass": "読書羅針盤",
        "guardian_reading_routes": "守護者の読書ルート",
        "supply_compass": "補給羅針盤",
        "starter_kit": "初期補給セット",
        "supply_wishlist": "補給ウィッシュリスト",
        "guardian_keepsakes": "守護者コレクション",
        "guardian_keepsake_hall": "守護者コレクション室",
        "heart_garden_pass": "心語の庭の通行印",
        "five_domain_theory_compass": "五分域の理論羅針盤",
        "heart_garden_trust_charter": "心語の庭の信頼憲章",
        "garden_journey": "庭の旅路",
        "heart_garden_map": "心語の庭マップ",
        "heart_garden_portals": "心語の庭の入口",
        "after_ritual": "儀式のあと",
        "main_routes": "主要ルート",
        "function_rooms": "機能室",
        "five_domains": "五つの分域",
        "field_guides": "分域ガイド",
        "trust_routes": "信頼ルート",
        "return_path": "戻る道",
        "safety_boundary_map": "安全境界マップ",
        "full_policy_notes": "詳しいポリシー",
        "home_field_notes": "心語の庭ノート",
        "universe_promise": "宇宙の約束",
        "guardian_field_guides": "守護者分域ガイド",
        "heart_garden_field_guide": "心語の庭ガイド",
        "week_route": "一週間の練習ルート",
        "printable_worksheet": "印刷できるワークシート",
        "guardian_routes": "守護者ルート",
        "calm_paths": "静けさの道",
        "night_heart_supply": "夜の心語補給",
        "luna_night_supply": "Luna 夜の補給",
        "about_lovetypes": "LoveTypes について",
        "love_language_theory": "愛の言語の理論",
        "love_language_faq": "愛の言語 FAQ",
        "keepsake_ritual_route": "保存・祝福・戻る",
        "keepsake_use_route": "保存・共有・戻る",
        "seven_day_heart_plan": "7日間の心語修復プラン",
        "heart_garden_archive": "心語の庭アーカイブ",
        "not_found_garden": "404 心語の庭",
        "safe_routes": "安全な戻り道",
    },
    "ko": {
        "heart_garden_supplies": "마음의 정원 보급소",
        "supply_route": "보급 루트",
        "traveler_supply": "여행자 보급",
        "related_guides": "관련 가이드",
        "five_guardians": "다섯 수호자",
        "moonlight_supply": "달빛 보급",
        "book_relics": "확장 서책",
        "destiny_ritual": "운명 의식",
        "night_supply_protocol": "밤 보급 절차",
        "guardian_night_supply": "수호자 밤 보급",
        "luna_supply_entry": "Luna 보급 입구",
        "your_night_supply": "나의 밤 보급",
        "request_compass": "요청 나침반",
        "garden_repair_desk": "정원 수리 데스크",
        "guardian_compass": "수호자 나침반",
        "choose_by_current_need": "지금 필요한 것으로 선택",
        "reading_compass": "읽기 나침반",
        "guardian_reading_routes": "수호자 읽기 루트",
        "supply_compass": "보급 나침반",
        "starter_kit": "시작 보급 세트",
        "supply_wishlist": "보급 위시리스트",
        "guardian_keepsakes": "수호자 소장 카드",
        "guardian_keepsake_hall": "수호자 소장실",
        "heart_garden_pass": "마음 정원 통행 표식",
        "five_domain_theory_compass": "다섯 영역 이론 나침반",
        "heart_garden_trust_charter": "마음 정원 신뢰 헌장",
        "garden_journey": "정원 여정",
        "heart_garden_map": "마음의 정원 지도",
        "heart_garden_portals": "마음 정원 입구",
        "after_ritual": "의식 이후",
        "main_routes": "주요 루트",
        "function_rooms": "기능 방",
        "five_domains": "다섯 영역",
        "field_guides": "영역 가이드",
        "trust_routes": "신뢰 루트",
        "return_path": "돌아가는 길",
        "safety_boundary_map": "안전 경계 지도",
        "full_policy_notes": "전체 정책 안내",
        "home_field_notes": "마음 정원 노트",
        "universe_promise": "세계관의 약속",
        "guardian_field_guides": "수호자 영역 가이드",
        "heart_garden_field_guide": "마음 정원 가이드",
        "week_route": "일주일 연습 루트",
        "printable_worksheet": "인쇄용 연습지",
        "guardian_routes": "수호자 루트",
        "calm_paths": "차분한 경로",
        "night_heart_supply": "밤 마음 보급",
        "luna_night_supply": "Luna 밤 보급",
        "about_lovetypes": "LoveTypes 소개",
        "love_language_theory": "사랑의 언어 이론",
        "love_language_faq": "사랑의 언어 FAQ",
        "keepsake_ritual_route": "저장 · 축복 · 복귀",
        "keepsake_use_route": "저장 · 공유 · 복귀",
        "seven_day_heart_plan": "7일 마음 언어 회복 계획",
        "heart_garden_archive": "마음 정원 보관소",
        "not_found_garden": "404 마음 정원",
        "safe_routes": "안전한 복귀 루트",
    },
    "es": {
        "heart_garden_supplies": "SUMINISTROS DEL JARDÍN",
        "supply_route": "RUTA DE SUMINISTRO",
        "traveler_supply": "PROVISIÓN DE VIAJE",
        "related_guides": "GUÍAS RELACIONADAS",
        "five_guardians": "CINCO GUARDIANAS",
        "moonlight_supply": "SUMINISTRO DE LUNA",
        "book_relics": "LIBROS RELICARIO",
        "destiny_ritual": "RITUAL DE DESTINO",
        "night_supply_protocol": "PROTOCOLO NOCTURNO",
        "guardian_night_supply": "SUMINISTRO NOCTURNO",
        "luna_supply_entry": "ENTRADA LUNA",
        "your_night_supply": "TU SUMINISTRO NOCTURNO",
        "request_compass": "BRÚJULA DE PETICIONES",
        "garden_repair_desk": "MESA DE REPARACIÓN",
        "guardian_compass": "BRÚJULA GUARDIANA",
        "choose_by_current_need": "ELIGE POR NECESIDAD",
        "reading_compass": "BRÚJULA DE LECTURA",
        "guardian_reading_routes": "RUTAS DE LECTURA",
        "supply_compass": "BRÚJULA DE RECURSOS",
        "starter_kit": "KIT INICIAL",
        "supply_wishlist": "LISTA DE RECURSOS",
        "guardian_keepsakes": "RECUERDOS DE GUARDIANAS",
        "guardian_keepsake_hall": "SALA DE RECUERDOS",
        "heart_garden_pass": "PASE DEL JARDÍN",
        "five_domain_theory_compass": "BRÚJULA DE CINCO DOMINIOS",
        "heart_garden_trust_charter": "CARTA DE CONFIANZA",
        "garden_journey": "VIAJE DEL JARDÍN",
        "heart_garden_map": "MAPA DEL JARDÍN",
        "heart_garden_portals": "PORTALES DEL JARDÍN",
        "after_ritual": "DESPUÉS DEL RITUAL",
        "main_routes": "RUTAS PRINCIPALES",
        "function_rooms": "SALAS FUNCIONALES",
        "five_domains": "CINCO DOMINIOS",
        "field_guides": "GUÍAS DE DOMINIO",
        "trust_routes": "RUTAS DE CONFIANZA",
        "return_path": "CAMINO DE VUELTA",
        "safety_boundary_map": "MAPA DE LÍMITES",
        "full_policy_notes": "NOTAS DE POLÍTICA",
        "home_field_notes": "NOTAS DEL JARDÍN",
        "universe_promise": "PROMESA DEL UNIVERSO",
        "guardian_field_guides": "GUÍAS DE GUARDIANAS",
        "heart_garden_field_guide": "GUÍA DEL JARDÍN",
        "week_route": "RUTA SEMANAL",
        "printable_worksheet": "HOJA IMPRIMIBLE",
        "guardian_routes": "RUTAS DE GUARDIANAS",
        "calm_paths": "RUTAS DE CALMA",
        "night_heart_supply": "SUMINISTRO NOCTURNO",
        "luna_night_supply": "LUNA NOCTURNA",
        "about_lovetypes": "ACERCA DE LOVETYPES",
        "love_language_theory": "TEORÍA DE LENGUAJES",
        "love_language_faq": "FAQ DE LENGUAJES",
        "keepsake_ritual_route": "GUARDAR · BENDECIR · VOLVER",
        "keepsake_use_route": "GUARDAR · COMPARTIR · VOLVER",
        "seven_day_heart_plan": "PLAN DE 7 DÍAS",
        "heart_garden_archive": "ARCHIVO DEL JARDÍN",
        "not_found_garden": "404 JARDÍN DEL CORAZÓN",
        "safe_routes": "RUTAS SEGURAS",
    },
}


GUARDIAN_ENTRY = {
    "zh": {
        "eyebrow": "GUARDIAN COMPASS",
        "title": "先確認你要進入哪個分域",
        "intro": "五位守護者不是靜態角色列表。先知道你現在最需要哪種愛之語，再進入對應分域、修復任務與補給路線。",
        "items": [
            ("還不知道守護者", "先完成 15 道心語，讓結果把你帶到最需要被接住的分域。", "開始認領儀式", ""),
            ("想先看五個分域", "瀏覽五域星圖，選一位最像你此刻需求的守護者。", "查看五域星圖", "#guardian-map"),
            ("已經知道守護者", "直接前往旅人補給，接上指南、7 日修復計畫與 Luna 夜間補給。", "前往補給站", "resources"),
        ],
    },
    "en": {
        "eyebrow": "GUARDIAN COMPASS",
        "title": "Choose the domain before entering",
        "intro": "The five guardians are not a static character list. Find the love language you need most now, then enter the matching domain, repair task, and supply route.",
        "items": [
            ("I do not know my guardian", "Take the 15 prompts first so the result points to the domain that needs care.", "Start quiz", ""),
            ("I want to browse first", "Scan the five-domain map and choose the guardian closest to what you need now.", "View map", "#guardian-map"),
            ("I already know my guardian", "Go to resources and continue into guides, the 7-day repair plan, and Luna night supply.", "Open resources", "resources"),
        ],
    },
    "ja": {
        "eyebrow": "GUARDIAN COMPASS",
        "title": "入る分域を先に確認する",
        "intro": "五人の守護者は静的な一覧ではありません。今いちばん必要な愛の言語を見つけ、対応する分域、修復課題、補給ルートへ進みます。",
        "items": [
            ("まだ守護者が分からない", "まず15問に答え、今ケアが必要な分域を結果で確認します。", "診断を始める", ""),
            ("先に五つの分域を見る", "五領域の地図を見て、今の必要に近い守護者を選びます。", "地図を見る", "#guardian-map"),
            ("守護者が分かっている", "リソースへ進み、ガイド、7日間の修復プラン、Luna の夜の補給へつなげます。", "リソースへ", "resources"),
        ],
    },
    "ko": {
        "eyebrow": "GUARDIAN COMPASS",
        "title": "들어갈 영역을 먼저 확인하기",
        "intro": "다섯 수호자는 고정된 캐릭터 목록이 아닙니다. 지금 가장 필요한 사랑의 언어를 찾고, 맞는 영역, 회복 과제, 보급 루트로 이어가세요.",
        "items": [
            ("아직 수호자를 모른다면", "먼저 15문항을 완료해 지금 돌봄이 필요한 영역을 확인하세요.", "테스트 시작", ""),
            ("먼저 다섯 영역을 보고 싶다면", "다섯 영역 지도를 보고 지금 필요에 가까운 수호자를 고르세요.", "지도 보기", "#guardian-map"),
            ("수호자를 알고 있다면", "자료로 이동해 가이드, 7일 회복 계획, Luna 밤 보급으로 이어가세요.", "자료 열기", "resources"),
        ],
    },
    "es": {
        "eyebrow": "GUARDIAN COMPASS",
        "title": "Elige el dominio antes de entrar",
        "intro": "Las cinco guardianas no son una lista estática. Encuentra el lenguaje del amor que necesitas ahora y entra al dominio, tarea de reparación y ruta de suministro correspondiente.",
        "items": [
            ("Aún no conozco mi guardiana", "Responde las 15 señales para que el resultado muestre el dominio que necesita cuidado.", "Iniciar test", ""),
            ("Quiero mirar primero", "Explora el mapa de cinco dominios y elige la guardiana más cercana a tu necesidad actual.", "Ver mapa", "#guardian-map"),
            ("Ya conozco mi guardiana", "Ve a recursos y continúa con guías, plan de 7 días y suministro nocturno Luna.", "Abrir recursos", "resources"),
        ],
    },
}


GUARDIAN_NEED_ROUTER = {
    "zh": {
        "eyebrow": "CHOOSE BY CURRENT NEED",
        "title": "如果你現在需要的是……",
        "intro": "不用先背五種愛之語。從此刻最明顯的缺口出發，進入對應守護者分域，再接上修復任務與補給路線。",
        "open": "進入分域",
        "supply": "補給路線",
        "items": {
            "iris": ("想被一句話穩穩接住", "當沉默讓你懷疑自己是否重要，先進入艾莉絲的晨曦玻璃花園。"),
            "noah": ("想要完整陪伴與專注", "當碎片時間讓你覺得孤單，諾雅會把你帶到安靜的星海圖書館。"),
            "vivian": ("想確認對方真的記得你", "當重要細節被遺忘，薇薇安的月光記憶工坊會整理心意與線索。"),
            "claire": ("想把承諾變成行動", "當照顧都落在你身上，克萊兒的溫室修復間會把需求翻成可做的一步。"),
            "dora": ("想在安全界線裡靠近", "當身體先緊繃或退後，朵拉的玫瑰金聖域會先確認同意與節奏。"),
        },
    },
    "en": {
        "eyebrow": "CHOOSE BY CURRENT NEED",
        "title": "If what you need right now is...",
        "intro": "You do not need to memorize the five love languages first. Start from the clearest gap, enter the guardian domain, then continue to a repair task and supply route.",
        "open": "Enter domain",
        "supply": "Supply route",
        "items": {
            "iris": ("To feel held by one sentence", "When silence makes you doubt your importance, enter Iris's dawn glass garden first."),
            "noah": ("Focused time and presence", "When fragmented attention feels lonely, Noah opens the quiet star-sea library."),
            "vivian": ("Proof that you are remembered", "When meaningful details are missed, Vivian's moonlit memory workshop gathers the signs."),
            "claire": ("Promises turned into action", "When care falls only on you, Claire's greenhouse repair room turns need into one doable step."),
            "dora": ("Closeness within safe boundaries", "When the body tightens or steps back first, Dora's rose-gold sanctuary begins with consent and rhythm."),
        },
    },
    "ja": {
        "eyebrow": "CHOOSE BY CURRENT NEED",
        "title": "今必要なのが……なら",
        "intro": "先に五つの愛の言語を覚える必要はありません。今いちばん目立つ欠けから入り、守護者の分域、修復課題、補給ルートへ進みます。",
        "open": "分域へ入る",
        "supply": "補給ルート",
        "items": {
            "iris": ("一言でしっかり受け止められたい", "沈黙で自分の大切さを疑う時は、アイリスの朝光ガラス庭園へ。"),
            "noah": ("集中した時間と同席がほしい", "細切れの時間が孤独に感じる時、ノアの静かな星海図書館が入口になります。"),
            "vivian": ("覚えていてくれた証がほしい", "大切な細部が抜け落ちる時、ヴィヴィアンの月光記憶工房が心意を整理します。"),
            "claire": ("約束を行動にしてほしい", "ケアが自分だけに偏る時、クレアの温室修復室が願いを一つの行動へ変えます。"),
            "dora": ("安全な境界の中で近づきたい", "身体が先にこわばる時、ドラのローズゴールド聖域は同意とリズムから始めます。"),
        },
    },
    "ko": {
        "eyebrow": "CHOOSE BY CURRENT NEED",
        "title": "지금 필요한 것이……라면",
        "intro": "다섯 사랑의 언어를 먼저 외울 필요는 없습니다. 지금 가장 분명한 빈틈에서 시작해 수호자 영역, 회복 과제, 보급 루트로 이어가세요.",
        "open": "영역으로 들어가기",
        "supply": "보급 루트",
        "items": {
            "iris": ("한 문장으로 단단히 받아들여지고 싶다", "침묵 때문에 내가 중요한지 의심될 때는 아이리스의 새벽 유리 정원으로 들어가세요."),
            "noah": ("온전한 시간과 집중이 필요하다", "조각난 시간이 외롭게 느껴질 때 노아의 조용한 별바다 도서관이 입구가 됩니다."),
            "vivian": ("나를 기억한다는 표시가 필요하다", "중요한 세부가 잊힐 때 비비안의 달빛 기억 공방이 마음의 단서를 정리합니다."),
            "claire": ("약속이 행동이 되길 바란다", "돌봄이 나에게만 쏠릴 때 클레어의 온실 회복실이 요구를 실행 가능한 한 걸음으로 바꿉니다."),
            "dora": ("안전한 경계 안에서 가까워지고 싶다", "몸이 먼저 긴장하거나 물러설 때 도라의 로즈골드 성역은 동의와 리듬에서 시작합니다."),
        },
    },
    "es": {
        "eyebrow": "CHOOSE BY CURRENT NEED",
        "title": "Si ahora necesitas...",
        "intro": "No necesitas memorizar primero los cinco lenguajes del amor. Empieza por la falta más clara, entra al dominio guardián y continúa con reparación y suministro.",
        "open": "Entrar al dominio",
        "supply": "Ruta de suministro",
        "items": {
            "iris": ("Sentirte sostenida por una frase", "Cuando el silencio te hace dudar de tu importancia, entra primero al jardín de cristal de Iris."),
            "noah": ("Tiempo completo y presencia", "Cuando la atención fragmentada se siente sola, Noah abre la biblioteca tranquila del mar de estrellas."),
            "vivian": ("Señales de que te recuerdan", "Cuando se olvidan detalles importantes, el taller lunar de Vivian reúne las pistas del cariño."),
            "claire": ("Promesas convertidas en acción", "Cuando el cuidado cae solo sobre ti, el invernadero de Claire vuelve la necesidad un paso posible."),
            "dora": ("Cercanía con límites seguros", "Cuando el cuerpo se tensa o retrocede primero, el santuario rosa dorado de Dora empieza por consentimiento y ritmo."),
        },
    },
}


GUIDE_INDEX_COMPASS = {
    "zh": {
        "eyebrow": "READING COMPASS",
        "title": "先找到守護者，再選一篇指南",
        "intro": "指南不是一次讀完的文章庫。先確認你的心語入口，再把閱讀接到一個可執行的小任務。",
        "steps": [
            ("1", "還不知道自己是哪位守護者", "先完成 15 道心語命運儀式，再回來讀對應指南。", "開始測驗", ""),
            ("2", "已經知道守護者", "進入角色頁，看你的錯頻傷口、修復任務與專屬補給路線。", "查看守護者", "characters"),
            ("3", "準備把閱讀變成行動", "把指南裡的一句話放進 7 日修復計畫，再選一本書卷或 Luna 夜間補給。", "打開修復計畫", "repair-plan"),
        ],
    },
    "en": {
        "eyebrow": "READING COMPASS",
        "title": "Find your guardian before choosing a guide",
        "intro": "The guides are not a pile to finish. Start with your heart-language doorway, then turn one page into one doable task.",
        "steps": [
            ("1", "If you do not know your guardian yet", "Answer the 15 prompts first, then return to the matching guide.", "Start quiz", ""),
            ("2", "If you already know your guardian", "Open the character page to see the wound, repair task, and personal supply route.", "View guardians", "characters"),
            ("3", "If you are ready to act", "Put one sentence from a guide into the 7-day repair plan, then choose a book or Luna night supply.", "Open repair plan", "repair-plan"),
        ],
    },
    "ja": {
        "eyebrow": "READING COMPASS",
        "title": "守護者を見つけてからガイドを選ぶ",
        "intro": "ガイドは全部読むための倉庫ではありません。まず心語の入口を確認し、一つのページを一つの小さな行動へつなげます。",
        "steps": [
            ("1", "まだ守護者が分からない時", "15問の心語リチュアルを行い、対応するガイドへ戻ります。", "診断を始める", ""),
            ("2", "守護者が分かっている時", "キャラクターページで、すれ違いの傷、修復課題、補給ルートを確認します。", "守護者を見る", "characters"),
            ("3", "行動へ移したい時", "ガイドの一文を7日間の修復プランへ入れ、本または Luna の夜の補給を一つ選びます。", "修復プランを開く", "repair-plan"),
        ],
    },
    "ko": {
        "eyebrow": "READING COMPASS",
        "title": "수호자를 찾고 가이드를 고르기",
        "intro": "가이드는 한 번에 다 읽는 목록이 아닙니다. 먼저 나의 마음 언어 입구를 확인하고, 한 페이지를 작은 행동 하나로 이어가세요.",
        "steps": [
            ("1", "아직 수호자를 모른다면", "15문항 의식을 먼저 완료한 뒤 연결 가이드로 돌아오세요.", "테스트 시작", ""),
            ("2", "이미 수호자를 안다면", "캐릭터 페이지에서 어긋남 상처, 회복 과제, 개인 보급 루트를 확인하세요.", "수호자 보기", "characters"),
            ("3", "읽은 내용을 행동으로 옮긴다면", "가이드의 한 문장을 7일 회복 계획에 넣고 책이나 Luna 밤 보급 하나를 고르세요.", "회복 계획 열기", "repair-plan"),
        ],
    },
    "es": {
        "eyebrow": "READING COMPASS",
        "title": "Encuentra tu guardiana antes de elegir guía",
        "intro": "Las guías no son una lista para terminar. Empieza por tu puerta de lenguaje del corazón y convierte una página en una tarea posible.",
        "steps": [
            ("1", "Si aún no conoces tu guardiana", "Responde las 15 señales primero y vuelve a la guía correspondiente.", "Iniciar test", ""),
            ("2", "Si ya conoces tu guardiana", "Abre la página de personaje para ver herida, tarea de reparación y ruta de suministro.", "Ver guardianas", "characters"),
            ("3", "Si estás lista para actuar", "Pon una frase de la guía en el plan de 7 días y elige un libro o suministro Luna.", "Abrir plan", "repair-plan"),
        ],
    },
}


GUIDE_DOMAIN_ROUTES = {
    "zh": {
        "eyebrow": "GUARDIAN READING ROUTES",
        "title": "五條守護者閱讀路線",
        "intro": "如果你已經感覺到自己的缺口，可以直接從守護者分域進入對應指南。每條路線都接上角色、練習與補給，不會只停在閱讀。",
        "read": "閱讀指南",
        "guardian": "進入分域",
        "supply": "補給路線",
        "practice": "先做這一步",
    },
    "en": {
        "eyebrow": "GUARDIAN READING ROUTES",
        "title": "Five Guardian Reading Routes",
        "intro": "If you already feel the gap, enter through the matching guardian domain. Each route connects a guide, character page, practice, and supply path.",
        "read": "Read guide",
        "guardian": "Enter domain",
        "supply": "Supply route",
        "practice": "First practice",
    },
    "ja": {
        "eyebrow": "GUARDIAN READING ROUTES",
        "title": "五つの守護者読書ルート",
        "intro": "すでに欠けが見えているなら、対応する守護者の分域から入れます。各ルートはガイド、人物ページ、練習、補給へつながります。",
        "read": "ガイドを読む",
        "guardian": "分域へ入る",
        "supply": "補給ルート",
        "practice": "最初の練習",
    },
    "ko": {
        "eyebrow": "GUARDIAN READING ROUTES",
        "title": "다섯 수호자 읽기 루트",
        "intro": "이미 빈틈이 느껴진다면 맞는 수호자 영역에서 시작하세요. 각 루트는 가이드, 캐릭터 페이지, 연습, 보급 길로 이어집니다.",
        "read": "가이드 읽기",
        "guardian": "영역으로 들어가기",
        "supply": "보급 루트",
        "practice": "먼저 할 연습",
    },
    "es": {
        "eyebrow": "GUARDIAN READING ROUTES",
        "title": "Cinco rutas de lectura guardiana",
        "intro": "Si ya sientes la falta principal, entra por el dominio guardián correspondiente. Cada ruta conecta guía, personaje, práctica y suministro.",
        "read": "Leer guía",
        "guardian": "Entrar al dominio",
        "supply": "Ruta de suministro",
        "practice": "Primera práctica",
    },
}


SUPPLY_DECISION = {
    "zh": {
        "eyebrow": "SUPPLY COMPASS",
        "title": "先免費練習，再決定是否補給",
        "intro": "把消費放在修復流程後面。先用免費內容確認需要，再選一個能支持你持續練習的補給。",
        "steps": [
            ("1", "先做一個免費小任務", "從測驗結果、守護者頁或指南裡選一個 24 小時內能完成的小行動。"),
            ("2", "需要整理情緒時用 Luna", "睡前、吵架後或寫關係日記時，用 Luna 幫情緒降噪，不急著購買書卷。"),
            ("3", "需要長期理解再選書卷", "只有在你願意慢慢讀、慢慢練時，才把書當成延伸補給。"),
        ],
        "matrix_title": "我現在該選哪一種補給？",
        "matrix": [
            ("先不要買", "只是想知道下一步，或情緒還很滿。", "做免費任務", "repair-plan"),
            ("需要夜間降噪", "睡前、吵架後、寫日記時需要先冷卻。", "開啟 Luna", "luna-yoga-music"),
            ("需要長期練習", "願意慢慢讀、慢慢做，才考慮一本延伸書卷。", "查看書卷", "#affiliate-books"),
            ("想要自有素材", "想要桌布、Luna 下載包、短儀式或印刷收藏包。", "提出需求", "contact/#luna-supply-request"),
        ],
    },
    "en": {
        "eyebrow": "SUPPLY COMPASS",
        "title": "Practice free first, then choose a supply",
        "intro": "Put spending after repair. Start with free content, confirm the need, then choose one supply that helps you keep practicing.",
        "steps": [
            ("1", "Do one free small task", "Choose one action from the quiz result, guardian page, or guide that can be done within 24 hours."),
            ("2", "Use Luna when feelings need sorting", "At night, after conflict, or while journaling, let Luna quiet the noise before buying books."),
            ("3", "Choose a book for longer learning", "Only use a book as extended supply when you are ready to read slowly and practice slowly."),
        ],
        "matrix_title": "Which supply should I choose now?",
        "matrix": [
            ("Do not buy yet", "You only need the next step, or your emotions are still too loud.", "Use free task", "repair-plan"),
            ("Need night calm", "You need to cool down before sleep, after conflict, or while journaling.", "Open Luna", "luna-yoga-music"),
            ("Need long practice", "You are ready to read slowly and practice slowly with one book.", "View books", "#affiliate-books"),
            ("Want owned assets", "You want wallpapers, Luna downloads, short rituals, or printed packs.", "Send request", "contact/#luna-supply-request"),
        ],
    },
    "ja": {
        "eyebrow": "SUPPLY COMPASS",
        "title": "まず無料で練習し、それから補給を選ぶ",
        "intro": "消費は修復の後ろに置きます。無料の内容で必要を確かめてから、練習を続けるための補給を一つ選びます。",
        "steps": [
            ("1", "無料の小さな課題を一つ行う", "診断結果、守護者ページ、ガイドから、二十四時間以内にできる行動を一つ選びます。"),
            ("2", "感情整理には Luna を使う", "眠る前、衝突後、関係日記を書く時に Luna で心を静め、本を急いで買わないようにします。"),
            ("3", "長く学びたい時だけ本を選ぶ", "ゆっくり読み、ゆっくり練習する準備がある時だけ、本を延長補給にします。"),
        ],
        "matrix_title": "今はどの補給を選ぶ？",
        "matrix": [
            ("まだ買わない", "次の一歩だけ必要、または感情が大きすぎる時。", "無料課題へ", "repair-plan"),
            ("夜に静めたい", "就寝前、衝突後、日記を書く前に冷静になりたい時。", "Luna を開く", "luna-yoga-music"),
            ("長く練習したい", "ゆっくり読み、ゆっくり練習する準備がある時だけ本へ。", "本を見る", "#affiliate-books"),
            ("自有素材がほしい", "壁紙、Luna ダウンロード、短い儀式、印刷セットがほしい時。", "希望を送る", "contact/#luna-supply-request"),
        ],
    },
    "ko": {
        "eyebrow": "SUPPLY COMPASS",
        "title": "먼저 무료로 연습하고 보급을 고르기",
        "intro": "소비는 회복 과정 뒤에 둡니다. 무료 콘텐츠로 필요를 확인한 뒤 계속 연습하게 돕는 보급 하나만 고르세요.",
        "steps": [
            ("1", "무료 작은 과제 하나 하기", "테스트 결과, 수호자 페이지, 가이드에서 24시간 안에 할 수 있는 행동 하나를 고릅니다."),
            ("2", "감정 정리가 필요할 때 Luna 사용", "잠들기 전, 다툼 뒤, 관계 일기를 쓸 때 Luna로 감정을 낮추고 책 구매를 서두르지 않습니다."),
            ("3", "장기 이해가 필요할 때 책 선택", "천천히 읽고 천천히 연습할 준비가 되었을 때만 책을 확장 보급으로 사용합니다."),
        ],
        "matrix_title": "지금 어떤 보급을 고를까요?",
        "matrix": [
            ("아직 사지 않기", "다음 단계만 필요하거나 감정이 아직 큰 상태입니다.", "무료 과제 하기", "repair-plan"),
            ("밤에 낮추기", "잠들기 전, 다툼 뒤, 일기 전에 먼저 진정이 필요합니다.", "Luna 열기", "luna-yoga-music"),
            ("길게 연습하기", "천천히 읽고 천천히 연습할 준비가 되었을 때만 책을 봅니다.", "책 보기", "#affiliate-books"),
            ("자체 자료 원함", "배경화면, Luna 다운로드, 짧은 의식, 인쇄팩을 원합니다.", "요청 보내기", "contact/#luna-supply-request"),
        ],
    },
    "es": {
        "eyebrow": "SUPPLY COMPASS",
        "title": "Practica gratis primero, luego elige un recurso",
        "intro": "Pon el consumo después de la reparación. Empieza con contenido gratuito, confirma la necesidad y elige un solo recurso para seguir practicando.",
        "steps": [
            ("1", "Haz una tarea pequeña gratuita", "Elige una acción del resultado, la página de guardiana o una guía que puedas hacer en 24 horas."),
            ("2", "Usa Luna para ordenar emociones", "De noche, después de un conflicto o al escribir diario, deja que Luna calme el ruido antes de comprar libros."),
            ("3", "Elige un libro para aprendizaje largo", "Usa un libro como recurso extendido solo si estás lista para leer y practicar despacio."),
        ],
        "matrix_title": "Qué recurso conviene ahora?",
        "matrix": [
            ("No comprar todavía", "Solo necesitas el siguiente paso o la emoción sigue muy alta.", "Usar tarea gratis", "repair-plan"),
            ("Calma nocturna", "Necesitas enfriar antes de dormir, después de un conflicto o al escribir.", "Abrir Luna", "luna-yoga-music"),
            ("Práctica larga", "Estás lista para leer y practicar despacio con un solo libro.", "Ver libros", "#affiliate-books"),
            ("Quiero recursos propios", "Quieres fondos, descargas Luna, rituales breves o packs impresos.", "Enviar petición", "contact/#luna-supply-request"),
        ],
    },
}


STARTER_KIT = {
    "zh": {
        "eyebrow": "STARTER KIT",
        "title": "你的守護者初始補給包",
        "intro": "不要一次把所有補給都帶走。先收下一張守護者卡、一個 24 小時任務、一盞夜間低光，再決定是否需要書卷。",
        "steps": [
            ("1", "先保存身分", "把守護者卡存起來，讓結果從一段文字變成可以回訪與分享的標記。", "打開收藏室", "keepsakes"),
            ("2", "做一個小任務", "把你的補給任務放進 7 日修復計畫，只選一件 24 小時內能完成的事。", "使用修復計畫", "repair-plan"),
            ("3", "夜晚先降噪", "情緒太滿時先用 Luna 整理，再決定要開口、等待，還是回到補給路線。", "開啟 Luna", "luna-yoga-music"),
            ("4", "再選延伸補給", "如果你願意慢慢練，再依守護者選一條路線與一本書卷，不需要全部購買。", "查看五路線", "#supply-routes"),
        ],
    },
    "en": {
        "eyebrow": "STARTER KIT",
        "title": "Your guardian starter kit",
        "intro": "Do not carry every supply at once. Save one guardian card, choose one 24-hour task, use one night light, then decide whether a book fits.",
        "steps": [
            ("1", "Save the identity", "Keep your guardian card so the result becomes something revisitable and shareable.", "Open keepsakes", "keepsakes"),
            ("2", "Do one small task", "Place your supply mission inside the 7-day repair plan and choose one action possible within 24 hours.", "Use repair plan", "repair-plan"),
            ("3", "Lower the night noise", "When feelings are loud, use Luna first, then decide whether to speak, wait, or return to the route.", "Open Luna", "luna-yoga-music"),
            ("4", "Choose deeper supply", "If you are ready to practice slowly, choose one guardian route and one book. You do not need all of them.", "View routes", "#supply-routes"),
        ],
    },
    "ja": {
        "eyebrow": "STARTER KIT",
        "title": "守護者の初期補給セット",
        "intro": "すべての補給を一度に持たなくて大丈夫です。守護者カード、一つの24時間課題、一つの夜の灯りを選び、その後で本が必要か決めます。",
        "steps": [
            ("1", "まず結果を保存する", "守護者カードを保存し、結果を戻って見られ、共有できる印にします。", "コレクション室へ", "keepsakes"),
            ("2", "小さな課題を一つ行う", "補給ミッションを7日間の修復プランに入れ、24時間以内にできる行動だけを選びます。", "修復プランを使う", "repair-plan"),
            ("3", "夜の雑音を下げる", "感情が大きい時は Luna で整え、話すか、待つか、補給ルートに戻るかを選びます。", "Luna を開く", "luna-yoga-music"),
            ("4", "深い補給を選ぶ", "ゆっくり練習する準備ができたら、守護者ルートと本を一つだけ選びます。全部は必要ありません。", "五つのルートを見る", "#supply-routes"),
        ],
    },
    "ko": {
        "eyebrow": "STARTER KIT",
        "title": "나의 수호자 시작 보급 세트",
        "intro": "모든 보급을 한 번에 가져가지 않아도 됩니다. 수호자 카드 하나, 24시간 과제 하나, 밤의 등불 하나를 고른 뒤 책이 필요한지 결정하세요.",
        "steps": [
            ("1", "정체성 먼저 저장", "수호자 카드를 저장해 결과를 다시 보고 공유할 수 있는 표시로 만듭니다.", "소장실 열기", "keepsakes"),
            ("2", "작은 과제 하나 하기", "보급 미션을 7일 회복 계획에 넣고 24시간 안에 가능한 행동 하나만 고릅니다.", "회복 계획 쓰기", "repair-plan"),
            ("3", "밤의 소음 낮추기", "감정이 클 때는 Luna로 먼저 정리한 뒤 말할지, 기다릴지, 보급 루트로 돌아갈지 고릅니다.", "Luna 열기", "luna-yoga-music"),
            ("4", "깊은 보급 선택", "천천히 연습할 준비가 되었다면 수호자 루트 하나와 책 한 권만 고르세요. 전부 필요하지 않습니다.", "다섯 루트 보기", "#supply-routes"),
        ],
    },
    "es": {
        "eyebrow": "STARTER KIT",
        "title": "Tu kit inicial de guardiana",
        "intro": "No lleves todos los recursos a la vez. Guarda una tarjeta, elige una tarea de 24 horas, usa una luz nocturna y luego decide si un libro encaja.",
        "steps": [
            ("1", "Guarda la identidad", "Conserva tu tarjeta de guardiana para que el resultado sea algo que puedas revisar y compartir.", "Abrir recuerdos", "keepsakes"),
            ("2", "Haz una tarea pequeña", "Lleva tu misión al plan de 7 días y elige una acción posible dentro de 24 horas.", "Usar plan", "repair-plan"),
            ("3", "Baja el ruido nocturno", "Cuando la emoción esté alta, usa Luna primero y luego decide si hablar, esperar o volver a la ruta.", "Abrir Luna", "luna-yoga-music"),
            ("4", "Elige recurso profundo", "Si estás lista para practicar despacio, elige una ruta de guardiana y un libro. No necesitas todos.", "Ver rutas", "#supply-routes"),
        ],
    },
}


SUPPLY_WISHLIST = {
    "zh": {
        "eyebrow": "SUPPLY WISHLIST",
        "title": "下一批自有補給，先開哪一道門？",
        "intro": "如果書卷還不是你現在需要的補給，可以直接選一位守護者，告訴我們你會留下哪種素材。練習卡已在收藏室免費開放；這裡會成為 LoveTypes 下一批桌布、Luna 下載包、短儀式與印刷收藏包的優先訊號。",
        "format_label": "可做成",
        "formats": ["手機桌布", "Luna 下載包", "7 分鐘短儀式", "印刷收藏包"],
        "request": "投票給這條補給",
        "note": "來信不需要提供測驗分數；寫下守護者、使用情境與你希望帶走的素材即可。LoveTypes 不承諾療效，也不取代諮商。",
        "subject": "LoveTypes 守護者補給願望清單",
        "body": "我想優先看到的守護者補給：",
        "body_context": "我會在這個情境使用：",
    },
    "en": {
        "eyebrow": "SUPPLY WISHLIST",
        "title": "Which owned supply gate should open next?",
        "intro": "If a book is not the supply you need right now, choose one guardian and tell us which material you would actually keep. Printable cards are already free in the keepsake hall; this signal helps prioritize future wallpapers, Luna downloads, short rituals, and printed collectible packs.",
        "format_label": "Could become",
        "formats": ["Phone wallpaper", "Luna download pack", "7-minute ritual", "Printed collectible pack"],
        "request": "Vote for this supply",
        "note": "You do not need to send quiz scores. Include the guardian, use case, and the material you would actually keep. LoveTypes does not promise outcomes or replace counseling.",
        "subject": "LoveTypes guardian supply wishlist",
        "body": "The guardian supply I want prioritized:",
        "body_context": "I would use it when:",
    },
    "ja": {
        "eyebrow": "SUPPLY WISHLIST",
        "title": "次に開く自有補給の扉は？",
        "intro": "本が今の補給ではない場合、守護者を一人選び、実際に保存したい素材を教えてください。印刷できる練習カードはコレクション室で無料公開済みです。その声は LoveTypes の壁紙、Luna ダウンロード、短い儀式、印刷コレクションの優先順位になります。",
        "format_label": "制作候補",
        "formats": ["スマホ壁紙", "Luna ダウンロード", "7分の短い儀式", "印刷コレクション"],
        "request": "この補給に投票する",
        "note": "診断スコアは不要です。守護者、使いたい場面、実際に保存したい素材を書いてください。LoveTypes は効果を約束せず、相談支援の代わりにもなりません。",
        "subject": "LoveTypes 守護者補給の希望リスト",
        "body": "優先してほしい守護者補給：",
        "body_context": "使いたい場面：",
    },
    "ko": {
        "eyebrow": "SUPPLY WISHLIST",
        "title": "다음 자체 보급 문은 어디를 먼저 열까요?",
        "intro": "지금 책이 필요한 보급이 아니라면, 수호자 한 명을 고르고 실제로 보관할 자료를 알려 주세요. 인쇄용 연습 카드는 이미 소장실에서 무료로 열려 있습니다. 그 신호가 LoveTypes 배경화면, Luna 다운로드, 짧은 의식, 인쇄 소장팩의 우선순위가 됩니다.",
        "format_label": "제작 후보",
        "formats": ["휴대폰 배경화면", "Luna 다운로드 팩", "7분 짧은 의식", "인쇄 소장팩"],
        "request": "이 보급에 투표하기",
        "note": "테스트 점수는 보내지 않아도 됩니다. 수호자, 사용 장면, 실제로 보관하고 싶은 자료를 적어 주세요. LoveTypes는 결과를 약속하거나 상담을 대신하지 않습니다.",
        "subject": "LoveTypes 수호자 보급 희망 목록",
        "body": "우선 제작되길 바라는 수호자 보급:",
        "body_context": "이럴 때 사용하고 싶어요:",
    },
    "es": {
        "eyebrow": "SUPPLY WISHLIST",
        "title": "Qué puerta de recursos propios debería abrirse después?",
        "intro": "Si un libro no es el recurso que necesitas ahora, elige una guardiana y dinos qué material guardarías de verdad. Las tarjetas imprimibles ya están gratis en la sala de recuerdos; esta señal ayuda a priorizar futuros fondos, descargas Luna, rituales breves y packs impresos.",
        "format_label": "Podría ser",
        "formats": ["Fondo móvil", "Pack Luna", "Ritual de 7 minutos", "Pack impreso"],
        "request": "Votar por este recurso",
        "note": "No necesitas enviar puntajes. Incluye la guardiana, el uso y el material que realmente guardarías. LoveTypes no promete resultados ni reemplaza terapia.",
        "subject": "Lista de deseos de recursos de guardiana LoveTypes",
        "body": "El recurso de guardiana que quiero priorizar:",
        "body_context": "Lo usaría cuando:",
    },
}


SUPPLY_PRODUCT_STACK = {
    "zh": {
        "label": "可帶走的補給包",
        "free": "免費收藏物",
        "free_desc": "先保存守護者卡，讓結果變成可回訪的入口。",
        "owned": "自有素材需求",
        "owned_desc": "投票給桌布、Luna 下載包、短儀式或印刷包，告訴我們下一批素材優先順序。",
        "night": "Luna 夜間承接",
        "night_desc": "情緒太滿時先降噪，再回到一個小任務。",
        "contact": "帶著結果寄出需求",
        "contact_desc": "把守護者、補給路線與想要的素材格式一起帶進聯絡信。",
        "template_note": "信件會自帶守護者、今日任務與下一批想要的素材格式。",
    },
    "en": {
        "label": "Supply pack to take with you",
        "free": "Free keepsake",
        "free_desc": "Save the guardian card first so the result becomes a route you can revisit.",
        "owned": "Owned asset request",
        "owned_desc": "Vote for a wallpaper, Luna download, short ritual, or printed pack so we know what to build next.",
        "night": "Luna night handoff",
        "night_desc": "Lower the emotional noise first, then return to one small task.",
        "contact": "Send request with result",
        "contact_desc": "Carry your guardian, supply route, and preferred asset format into one email.",
        "template_note": "The email carries your guardian, today task, and next preferred asset format.",
    },
    "ja": {
        "label": "持ち帰れる補給セット",
        "free": "無料コレクション",
        "free_desc": "守護者カードを保存し、結果へ戻る入口にします。",
        "owned": "自有素材の希望",
        "owned_desc": "壁紙、Luna、短い儀式、印刷セットに投票できます。",
        "night": "Luna 夜の受け皿",
        "night_desc": "感情を下げ、小さな課題へ戻ります。",
        "contact": "結果と一緒に希望を送る",
        "contact_desc": "守護者、補給ルート、希望素材を一通に入れます。",
        "template_note": "メールには守護者、今日の課題、希望素材が入ります。",
    },
    "ko": {
        "label": "가져갈 수 있는 보급 팩",
        "free": "무료 소장물",
        "free_desc": "먼저 수호자 카드를 저장해 결과를 다시 찾을 수 있는 입구로 만듭니다.",
        "owned": "자체 자료 요청",
        "owned_desc": "배경화면, Luna 다운로드, 짧은 의식, 인쇄팩 중 무엇을 다음에 만들지 투표합니다.",
        "night": "Luna 밤 연결",
        "night_desc": "감정의 소음을 낮춘 뒤 작은 과제 하나로 돌아갑니다.",
        "contact": "결과와 함께 요청 보내기",
        "contact_desc": "수호자, 보급 루트, 원하는 자료 형식을 한 메일에 담습니다.",
        "template_note": "메일에는 수호자, 오늘 과제, 다음에 원하는 자료 형식이 담깁니다.",
    },
    "es": {
        "label": "Paquete de recursos para llevar",
        "free": "Recuerdo gratis",
        "free_desc": "Guarda primero la tarjeta para volver a tu resultado cuando lo necesites.",
        "owned": "Solicitud de recurso propio",
        "owned_desc": "Vota por fondo, descarga Luna, ritual breve o pack impreso para decidir qué crear después.",
        "night": "Paso nocturno Luna",
        "night_desc": "Baja el ruido emocional y vuelve a una tarea pequeña.",
        "contact": "Enviar solicitud con resultado",
        "contact_desc": "Lleva tu guardiana, ruta y formato preferido a un solo correo.",
        "template_note": "El correo incluye tu guardiana, tarea de hoy y el próximo formato preferido.",
    },
}


SUPPLY_LABELS = {
    "zh": {
        "eyebrow": "守護者補給路線",
        "title": "五位守護者補給站",
        "intro": "依照你的守護者選一條路線：先讀對應指南，再做一個小任務，最後選擇書卷或 Luna 夜間補給。補給是輔助修復，不是療效承諾。",
        "route": "你的補給路線",
        "guide": "對應指南",
        "fit_supply": "適合你的補給",
        "wound": "你的錯頻傷口",
        "repair": "你的修復任務",
        "practice": "今日小任務",
        "supply": "補給建議",
        "read_guide": "閱讀對應指南",
        "open_luna": "開啟 Luna",
        "free_keepsake": "免費收藏卡",
        "request_supply": "提出補給需求",
        "copy_route": "複製此路線",
        "route_copied": "已複製補給路線",
        "route_summary_title": "LoveTypes 守護者補給路線",
        "route_summary_guardian": "守護者",
        "route_summary_practice": "今日任務",
        "route_summary_supply": "補給建議",
        "route_summary_book": "延伸書卷",
        "quick_route": "守護者下一步",
        "deeper_route": "深入補給路線",
        "choose": "如何選擇補給",
        "choose_text": "先選一個最貼近當下狀態的補給，不要一次買齊或讀完所有內容；如果關係正處於危險、控制、暴力或高壓狀態，請先尋求真人與專業支持。",
        "not_now": "不適合購買的時機",
        "not_now_text": "如果你只是想用商品替代道歉、逼對方改變，或在情緒很滿時衝動下單，請先回到指南裡的一個小請求。LoveTypes 的補給只適合支持覺察與練習。",
    },
    "en": {
        "eyebrow": "GUARDIAN SUPPLY ROUTES",
        "title": "Five Guardian Supply Routes",
        "intro": "Choose a route by guardian: read the matching guide, practice one small task, then pick a book or Luna night supply. Supplies support repair; they do not promise outcomes.",
        "route": "Your supply route",
        "guide": "Matching guide",
        "fit_supply": "Supply that fits you",
        "wound": "Your misfrequency wound",
        "repair": "Your repair task",
        "practice": "Small task today",
        "supply": "Supply suggestion",
        "read_guide": "Read guide",
        "open_luna": "Open Luna",
        "free_keepsake": "Free keepsake card",
        "request_supply": "Request this supply",
        "copy_route": "Copy this route",
        "route_copied": "Supply route copied",
        "route_summary_title": "LoveTypes guardian supply route",
        "route_summary_guardian": "Guardian",
        "route_summary_practice": "Today task",
        "route_summary_supply": "Supply suggestion",
        "route_summary_book": "Extended book",
        "quick_route": "Guardian next steps",
        "deeper_route": "Deeper supply route",
        "choose": "How to choose supplies",
        "choose_text": "Choose one supply that fits the current moment. Do not buy or read everything at once. If the relationship involves danger, control, violence, or acute pressure, seek trusted people and professional support first.",
        "not_now": "When not to buy",
        "not_now_text": "Pause if you want a product to replace an apology, force someone to change, or soothe a purchase impulse. LoveTypes supplies are for reflection and practice.",
    },
    "ja": {
        "eyebrow": "守護者の補給ルート",
        "title": "五人の守護者の補給ルート",
        "intro": "守護者ごとに、対応ガイド、小さな練習、本または Luna の夜の補給を選びます。補給は修復を支えるもので、結果を約束するものではありません。",
        "route": "あなたの補給ルート",
        "guide": "対応ガイド",
        "fit_supply": "あなたに合う補給",
        "wound": "あなたのすれ違いの傷",
        "repair": "あなたの修復課題",
        "practice": "今日の小さな課題",
        "supply": "補給の提案",
        "read_guide": "ガイドを読む",
        "open_luna": "Luna を開く",
        "free_keepsake": "無料カード",
        "request_supply": "補給を希望する",
        "copy_route": "このルートをコピー",
        "route_copied": "補給ルートをコピーしました",
        "route_summary_title": "LoveTypes 守護者の補給ルート",
        "route_summary_guardian": "守護者",
        "route_summary_practice": "今日の課題",
        "route_summary_supply": "補給の提案",
        "route_summary_book": "本で深める",
        "quick_route": "守護者の次の一歩",
        "deeper_route": "深い補給ルート",
        "choose": "補給の選び方",
        "choose_text": "今の状態に一番近い補給を一つだけ選びます。すべてを一度に買ったり読んだりしないでください。危険、支配、暴力、強い圧力がある場合は、まず信頼できる人と専門支援へ。",
        "not_now": "購入しない方がよい時",
        "not_now_text": "謝罪の代わりに商品を使いたい、相手を変えたい、衝動で買いたい時は一度止まります。LoveTypes の補給は気づきと練習を支えるものです。",
    },
    "ko": {
        "eyebrow": "수호자 보급 루트",
        "title": "다섯 수호자 보급 루트",
        "intro": "수호자에 맞춰 가이드, 작은 연습, 책 또는 Luna 밤 보급을 고르세요. 보급은 회복을 돕는 도구이며 결과를 약속하지 않습니다.",
        "route": "나의 보급 루트",
        "guide": "연결 가이드",
        "fit_supply": "나에게 맞는 보급",
        "wound": "나의 어긋남 상처",
        "repair": "나의 회복 과제",
        "practice": "오늘의 작은 과제",
        "supply": "보급 제안",
        "read_guide": "가이드 읽기",
        "open_luna": "Luna 열기",
        "free_keepsake": "무료 소장 카드",
        "request_supply": "보급 요청하기",
        "copy_route": "이 루트 복사",
        "route_copied": "보급 루트가 복사됨",
        "route_summary_title": "LoveTypes 수호자 보급 루트",
        "route_summary_guardian": "수호자",
        "route_summary_practice": "오늘의 과제",
        "route_summary_supply": "보급 제안",
        "route_summary_book": "확장 책",
        "quick_route": "수호자 다음 단계",
        "deeper_route": "심화 보급 루트",
        "choose": "보급을 고르는 법",
        "choose_text": "지금 상태에 가장 맞는 보급 하나만 고르세요. 한 번에 모두 사거나 읽지 마세요. 위험, 통제, 폭력, 큰 압박이 있다면 먼저 믿을 수 있는 사람과 전문 지원을 찾으세요.",
        "not_now": "구매하지 않는 편이 좋은 때",
        "not_now_text": "상품으로 사과를 대신하거나 상대를 바꾸려 하거나 감정이 큰 상태에서 충동 구매하려 한다면 멈추세요. LoveTypes 보급은 성찰과 연습을 돕는 도구입니다.",
    },
    "es": {
        "eyebrow": "RUTAS DE SUMINISTRO",
        "title": "Rutas de suministro de las cinco guardianas",
        "intro": "Elige una ruta por guardiana: guía correspondiente, una práctica pequeña y luego un libro o suministro nocturno Luna. Los recursos apoyan la reparación; no prometen resultados.",
        "route": "Tu ruta de suministro",
        "guide": "Guía correspondiente",
        "fit_supply": "Recurso adecuado para ti",
        "wound": "Tu herida de desajuste",
        "repair": "Tu tarea de reparación",
        "practice": "Tarea pequeña de hoy",
        "supply": "Sugerencia de recurso",
        "read_guide": "Leer guía",
        "open_luna": "Abrir Luna",
        "free_keepsake": "Tarjeta gratis",
        "request_supply": "Pedir este recurso",
        "copy_route": "Copiar esta ruta",
        "route_copied": "Ruta copiada",
        "route_summary_title": "Ruta de suministro LoveTypes",
        "route_summary_guardian": "Guardiana",
        "route_summary_practice": "Tarea de hoy",
        "route_summary_supply": "Sugerencia de recurso",
        "route_summary_book": "Libro extendido",
        "quick_route": "Siguientes pasos de la guardiana",
        "deeper_route": "Ruta de suministro profunda",
        "choose": "Cómo elegir recursos",
        "choose_text": "Elige un recurso que encaje con este momento. No compres ni leas todo de una vez. Si hay peligro, control, violencia o presión intensa, busca primero personas confiables y apoyo profesional.",
        "not_now": "Cuándo no comprar",
        "not_now_text": "Pausa si quieres que un producto reemplace una disculpa, obligue a alguien a cambiar o calme una compra impulsiva. Los recursos LoveTypes son para reflexión y práctica.",
    },
}


SUPPLY_ROUTES = {
    "iris": {
        "book": 1,
        "zh": ("艾莉絲語言補給", "把想被看見的心翻成一句準確、可被接住的話。", "容易把沒被肯定解讀成不被珍惜，或把需要說成測驗。", "今天寫下三句具體肯定：看見、感謝、承認，不使用空泛稱讚。", "先用非暴力溝通拆開感受與請求，再回到艾莉絲的句型練習。"),
        "en": ("Iris Word Supply", "Turn the need to be seen into one accurate sentence someone can receive.", "You may read missing affirmation as not being valued, or turn a need into a test.", "Write three specific affirmations today: seeing, gratitude, and recognition.", "Use Nonviolent Communication to separate feeling from request, then practice Iris scripts."),
        "ja": ("アイリス言葉の補給", "見てもらいたい心を、相手が受け取れる一文へ翻訳します。", "肯定されないことを大切にされていないと読み、ニーズを試す形にしやすい。", "今日、見る、感謝する、認めるの三つの具体的な肯定を書きます。", "非暴力コミュニケーションで感情とお願いを分け、アイリスの句型へ戻ります。"),
        "ko": ("아이리스 말의 보급", "정확히 보이고 싶은 마음을 받을 수 있는 한 문장으로 바꿉니다.", "인정이 없으면 소중하지 않다고 읽거나 욕구를 시험처럼 만들기 쉽습니다.", "오늘 보기, 감사, 인정의 구체적인 말 세 문장을 쓰세요.", "비폭력 대화로 감정과 요청을 나눈 뒤 아이리스 문장으로 연습하세요."),
        "es": ("Suministro de palabras Iris", "Convierte la necesidad de ser vista en una frase precisa que pueda recibirse.", "Puedes leer la falta de afirmación como falta de valor, o convertir una necesidad en prueba.", "Escribe hoy tres afirmaciones concretas: ver, agradecer y reconocer.", "Usa Comunicación no violenta para separar emoción y petición, luego practica frases de Iris."),
    },
    "noah": {
        "book": 3,
        "zh": ("諾雅陪伴補給", "把陪伴從口頭承諾變成一段真正留下來的時間。", "最痛的錯頻通常是人在旁邊，心卻沒有到場。", "安排十五分鐘無手機共處，只問一個問題：這週哪一刻最像我們在一起？", "用長期關係習慣補強優質時光，讓在場不只靠心情。"),
        "en": ("Noah Presence Supply", "Turn promised company into time where both people truly stay.", "The tender wound is often presence without attention.", "Protect fifteen phone-free minutes and ask one question: when did we feel most together this week?", "Use relationship-habit reading to make quality time less dependent on mood."),
        "ja": ("ノア同在の補給", "一緒にいる約束を、本当に留まる時間へ変えます。", "痛みは、隣にいるのに心が不在なことから生まれやすい。", "スマホなしの十五分を作り、今週一番一緒に感じた瞬間を聞きます。", "関係習慣の本で上質な時間を気分任せにしない土台を作ります。"),
        "ko": ("노아 함께함 보급", "함께하겠다는 말을 진짜 머무는 시간으로 바꿉니다.", "가장 아픈 어긋남은 곁에 있지만 마음이 없는 순간입니다.", "휴대폰 없는 15분을 정하고 이번 주 가장 함께였던 순간을 묻습니다.", "관계 습관을 통해 함께하는 시간을 기분에만 맡기지 않게 합니다."),
        "es": ("Suministro de presencia Noah", "Convierte la compañía prometida en tiempo donde ambas personas se quedan de verdad.", "La herida suele ser presencia sin atención.", "Protege quince minutos sin teléfono y pregunta cuándo se sintieron más juntas esta semana.", "Usa hábitos de relación para que el tiempo de calidad no dependa solo del ánimo."),
    },
    "vivian": {
        "book": 0,
        "zh": ("薇薇安心意補給", "把禮物從價格拉回記得、觀察與細節。", "容易在重要日子沒有表示時，感覺自己沒有被放在心上。", "記下一個對方隨口提過的小喜歡，並用低成本方式讓它被看見。", "回到愛之語原典，確認禮物型重視的是記得，不是昂貴。"),
        "en": ("Vivian Memory Supply", "Bring gifts back from price to remembrance, observation, and detail.", "You may feel unheld when important days pass with no sign.", "Record one tiny preference and make it visible in a low-cost way.", "Return to the core love-language text to separate remembrance from expense."),
        "ja": ("ヴィヴィアン記憶の補給", "贈り物を値段ではなく、覚えていること、観察、細部へ戻します。", "大切な日に何もないと、心に置かれていないと感じやすい。", "相手の小さな好みを一つ記録し、低コストで見える形にします。", "愛の言語の原典へ戻り、贈り物型が重視するのは高価さではなく記憶だと確認します。"),
        "ko": ("비비안 기억 보급", "선물을 가격이 아니라 기억, 관찰, 세부로 돌려놓습니다.", "중요한 날 아무 표시가 없으면 마음에 없다고 느끼기 쉽습니다.", "상대가 흘려 말한 작은 취향 하나를 적고 낮은 비용으로 보이게 하세요.", "사랑의 언어 원전으로 돌아가 선물형이 비싼 것보다 기억을 중시함을 확인하세요."),
        "es": ("Suministro de memoria Vivian", "Devuelve los regalos del precio al recuerdo, la observación y los detalles.", "Puede doler cuando los días importantes pasan sin señal.", "Anota una preferencia pequeña y hazla visible de bajo costo.", "Vuelve al texto base para separar recuerdo de gasto."),
    },
    "claire": {
        "book": 3,
        "zh": ("克萊兒行動補給", "把承諾放回日常，讓照顧不再只由一個人承擔。", "容易把沒有人主動分擔，感覺成自己不值得被照顧。", "把一件想被幫忙的事寫成具體請求：時間、動作、完成標準。", "用伴侶習慣書卷建立分工，不讓服務行動變成情緒勞動。"),
        "en": ("Claire Action Supply", "Return promises to daily life so care is not carried by one person alone.", "When nobody shares the load, it can feel like you are not worth care.", "Turn one desired help into a concrete request: time, action, and done condition.", "Use couple-habit reading to keep service from becoming emotional labor."),
        "ja": ("クレア行動の補給", "約束を日常へ戻し、ケアを一人だけで抱えないようにします。", "誰も分担しない時、自分はケアされる価値がないと感じやすい。", "助けてほしいことを、時間、行動、完了条件つきの具体的なお願いにします。", "パートナー習慣の本で、奉仕を感情労働にしない分担を作ります。"),
        "ko": ("클레어 행동 보급", "약속을 일상으로 돌려놓아 돌봄을 한 사람만 지지 않게 합니다.", "아무도 나누지 않으면 돌봄 받을 가치가 없다고 느끼기 쉽습니다.", "도움이 필요한 일을 시간, 행동, 완료 기준이 있는 요청으로 쓰세요.", "커플 습관 책으로 봉사가 감정 노동이 되지 않게 분담을 만드세요."),
        "es": ("Suministro de acción Claire", "Devuelve las promesas a la vida diaria para que el cuidado no lo cargue una sola persona.", "Cuando nadie comparte la carga, puede sentirse como no valer cuidado.", "Convierte una ayuda deseada en petición concreta: tiempo, acción y condición de terminado.", "Usa hábitos de pareja para que el servicio no se vuelva trabajo emocional."),
    },
    "dora": {
        "book": 2,
        "zh": ("朵拉安全補給", "讓靠近先回到同意、身體安全與穩定節奏。", "容易在靠近太快、太突然或沒有確認時，身體先關門。", "建立一個安全靠近句：我現在可以抱你嗎？如果不行，我可以坐在旁邊。", "用依附理解靠近與退縮，再搭配 Luna 做睡前降噪。"),
        "en": ("Dora Safety Supply", "Bring closeness back to consent, body safety, and a stable rhythm.", "When closeness is sudden or unchecked, the body may close first.", "Create one safe closeness sentence: can I hold you now? If not, I can sit beside you.", "Use attachment reading for pursuit and withdrawal, then pair with Luna at night."),
        "ja": ("ドラ安全の補給", "近さを同意、身体の安全、安定したリズムへ戻します。", "近づき方が急すぎる、確認がない時、身体が先に閉じやすい。", "安全な近づきの一文を作ります。今抱きしめてもいい？無理なら隣に座るね。", "愛着の理解で近づきと退き方を見て、夜は Luna と組み合わせます。"),
        "ko": ("도라 안전 보급", "가까움을 동의, 몸의 안전, 안정된 리듬으로 돌립니다.", "가까움이 갑작스럽거나 확인이 없으면 몸이 먼저 닫힐 수 있습니다.", "안전한 가까움 문장을 만드세요. 지금 안아도 돼? 아니면 옆에 앉아 있을게.", "애착으로 다가감과 물러남을 이해하고 밤에는 Luna와 함께 낮추세요."),
        "es": ("Suministro de seguridad Dora", "Devuelve la cercanía al consentimiento, la seguridad corporal y un ritmo estable.", "Cuando la cercanía llega rápido o sin confirmar, el cuerpo puede cerrarse primero.", "Crea una frase segura: puedo abrazarte ahora? Si no, puedo sentarme a tu lado.", "Usa lectura de apego para acercamiento y retirada, y acompaña con Luna de noche."),
    },
}


COLLECTOR_LABELS = {
    "zh": {
        "eyebrow": "GUARDIAN KEEPSAKES",
        "title": "守護者收藏卡",
        "intro": "把測驗結果從一個答案變成可以保存、分享與回看的入口。先收藏你的守護者卡，再回到補給路線做一個小任務。",
        "card": "你的守護者卡",
        "open": "開啟收藏卡",
        "download": "保存圖片",
        "hall": "前往收藏室",
        "story": "生成分享卡",
        "story_kicker": "情感守護者收藏",
        "story_cta": "lovetypes.tw/keepsakes",
        "story_error": "生成失敗",
        "route": "回到補給路線",
        "plan": "填入修復計畫",
        "share_hint": "適合發限動、傳給伴侶，或放進關係日記作為今天的心語入口。",
    },
    "en": {
        "eyebrow": "GUARDIAN KEEPSAKES",
        "title": "Guardian Keepsake Cards",
        "intro": "Turn the quiz result into something you can save, share, and revisit. Keep your guardian card, then return to one small supply task.",
        "card": "Your guardian card",
        "open": "Open card",
        "download": "Save image",
        "hall": "Open keepsake hall",
        "story": "Create story card",
        "story_kicker": "Emotion Guardian Keepsake",
        "story_cta": "lovetypes.tw/keepsakes",
        "story_error": "Image failed",
        "route": "Return to supply route",
        "plan": "Fill repair plan",
        "share_hint": "Use it in Stories, send it to a partner, or place it in a relationship journal as today's heart-language doorway.",
    },
    "ja": {
        "eyebrow": "GUARDIAN KEEPSAKES",
        "title": "守護者コレクションカード",
        "intro": "診断結果を、保存し、共有し、後から見返せる入口にします。守護者カードを残し、小さな補給課題へ戻ります。",
        "card": "あなたの守護者カード",
        "open": "カードを開く",
        "download": "画像を保存",
        "hall": "コレクション室へ",
        "story": "共有カードを生成",
        "story_kicker": "感情の守護者コレクション",
        "story_cta": "lovetypes.tw/keepsakes",
        "story_error": "生成できません",
        "route": "補給ルートへ戻る",
        "plan": "修復プランへ",
        "share_hint": "ストーリー、パートナーへの共有、関係日記の今日の入口として使えます。",
    },
    "ko": {
        "eyebrow": "GUARDIAN KEEPSAKES",
        "title": "수호자 소장 카드",
        "intro": "테스트 결과를 저장하고 공유하고 다시 볼 수 있는 입구로 바꿉니다. 수호자 카드를 남기고 작은 보급 과제로 돌아가세요.",
        "card": "나의 수호자 카드",
        "open": "카드 열기",
        "download": "이미지 저장",
        "hall": "소장실로 가기",
        "story": "공유 카드 만들기",
        "story_kicker": "감정 수호자 소장",
        "story_cta": "lovetypes.tw/keepsakes",
        "story_error": "생성 실패",
        "route": "보급 루트로 돌아가기",
        "plan": "회복 계획 쓰기",
        "share_hint": "스토리, 파트너에게 보내기, 관계 일기의 오늘 마음 언어 입구로 사용할 수 있습니다.",
    },
    "es": {
        "eyebrow": "GUARDIAN KEEPSAKES",
        "title": "Tarjetas de recuerdo de guardianas",
        "intro": "Convierte el resultado en algo que puedas guardar, compartir y volver a mirar. Conserva tu tarjeta y regresa a una tarea pequeña.",
        "card": "Tu tarjeta de guardiana",
        "open": "Abrir tarjeta",
        "download": "Guardar imagen",
        "hall": "Abrir sala",
        "story": "Crear historia",
        "story_kicker": "Recuerdo de guardiana emocional",
        "story_cta": "lovetypes.tw/keepsakes",
        "story_error": "No se pudo crear",
        "route": "Volver a la ruta",
        "plan": "Usar plan",
        "share_hint": "Úsala en historias, envíala a una pareja o ponla en tu diario relacional como puerta de lenguaje del corazón.",
    },
}


KEEPSAKES_PAGE = {
    "zh": {
        "title": "守護者收藏室",
        "desc": "集中保存 LoveTypes 五位守護者故事卡，讓測驗結果成為可以分享、回看與延伸補給的收藏入口。",
        "eyebrow": "GUARDIAN KEEPSAKE HALL",
        "intro": "每張卡都是一個心語入口：適合發限動、傳給伴侶、放進關係日記，或作為未來守護者補給與低價收藏商品的基礎。",
        "free_title": "免費帶走五張守護者收藏物",
        "free_intro": "目前所有守護者故事卡與練習卡都可免費開啟與保存。先把最像你的那張留下來，未來若推出桌布、Luna 下載包或印刷收藏包，也會從這裡延伸。",
        "free_items": [
            ("保存圖片", "每張卡都可直接開啟原圖或下載，適合放進手機相簿與關係日記。"),
            ("分享入口", "可生成分享卡，把守護者結果變成一句可被理解的心語。"),
            ("未來收藏基底", "桌布、Luna 下載包、短儀式與印刷收藏包會優先從這五張免費收藏物延伸。"),
        ],
        "asset_title": "五位守護者免費收藏物",
        "asset_intro": "每位守護者先提供一張可保存故事卡與一張可列印練習卡，並標記未來最適合延伸的桌布與 Luna 補給格式。",
        "asset_formats": ["故事卡", "可列印練習卡", "手機桌布候補", "Luna 下載包候補"],
        "asset_request": "索取這位守護者補給",
        "practice_title": "五張守護者可列印練習卡",
        "practice_intro": "把守護者結果整理成一張短卡：看見錯頻傷口、寫下一個修復任務、選一個補給。可列印或直接存成 PDF。",
        "practice_open": "開啟練習卡",
        "practice_print": "列印 / 存成 PDF",
        "practice_wound": "錯頻傷口",
        "practice_mission": "今日修復任務",
        "practice_supply": "延伸補給",
        "practice_blank": "我的一句心語",
        "how_title": "怎麼使用收藏卡",
        "steps": [
            ("保存", "先保存最像你的守護者卡，讓測驗結果不只是一次性的答案。"),
            ("分享", "分享時補上一句具體請求：我想被理解的是哪一種愛的入口。"),
            ("回訪", "一週後回來看同一張卡，檢查你是否真的完成一個小修復任務。"),
        ],
        "safety_title": "收藏不是要求",
        "safety_text": "收藏卡是提醒與對話入口，不是要求伴侶立刻照做的憑證。若你正處在不安全、被控制或被逼迫的關係裡，請先尋求可信任的人與專業支援。",
        "quiz": "重新測驗",
        "resources": "回到補給站",
    },
    "en": {
        "title": "Guardian Keepsake Hall",
        "desc": "Save the five LoveTypes guardian story cards so your quiz result becomes something shareable, revisitable, and ready for future supply assets.",
        "eyebrow": "GUARDIAN KEEPSAKE HALL",
        "intro": "Each card is a heart-language doorway: use it in Stories, send it to a partner, place it in a relationship journal, or keep it as the base for future collectible supplies.",
        "free_title": "Take five free guardian keepsakes",
        "free_intro": "All guardian story cards and practice cards are free to open and save now. Keep the one that feels closest to you; future wallpapers, Luna downloads, or printed collectible packs can grow from this hall.",
        "free_items": [
            ("Save the image", "Open or download each card for your phone album or relationship journal."),
            ("Share doorway", "Create a story card so the result becomes one heart-language sentence someone can understand."),
            ("Future collectible base", "Wallpapers, Luna downloads, short rituals, and printed collectible packs will grow from these free keepsakes first."),
        ],
        "asset_title": "Five free guardian keepsakes",
        "asset_intro": "Each guardian starts with one savable story card, one printable practice card, and a clear signal for future wallpapers and Luna supply formats.",
        "asset_formats": ["Story card", "Printable practice card", "Phone wallpaper candidate", "Luna download pack candidate"],
        "asset_request": "Request this guardian supply",
        "practice_title": "Five printable guardian practice cards",
        "practice_intro": "Turn the guardian result into a short card: name the wound, write one repair task, and choose one supply. Print it or save it as PDF.",
        "practice_open": "Open practice card",
        "practice_print": "Print / save PDF",
        "practice_wound": "Misfrequency wound",
        "practice_mission": "Today repair task",
        "practice_supply": "Extended supply",
        "practice_blank": "My one heart-language line",
        "how_title": "How to use the cards",
        "steps": [
            ("Save", "Keep the guardian card that feels most like you so the result is not a one-time answer."),
            ("Share", "Add one concrete request when you share: what doorway to feeling loved do you want understood?"),
            ("Return", "Come back after a week and check whether you completed one small repair task."),
        ],
        "safety_title": "A keepsake is not a demand",
        "safety_text": "The card is a reminder and conversation doorway, not proof that a partner must immediately comply. If the relationship is unsafe, controlling, or coercive, seek trusted and professional support first.",
        "quiz": "Retake quiz",
        "resources": "Return to supplies",
    },
    "ja": {
        "title": "守護者コレクション室",
        "desc": "LoveTypes の五人の守護者ストーリーカードを保存し、診断結果を共有、再訪、今後の補給資産へつなげる入口にします。",
        "eyebrow": "GUARDIAN KEEPSAKE HALL",
        "intro": "それぞれのカードは心語の入口です。ストーリー、パートナーへの共有、関係日記、今後のコレクション補給の土台として使えます。",
        "free_title": "五枚の守護者カードを無料で持ち帰る",
        "free_intro": "現在、すべての守護者ストーリーカードと練習カードを無料で開き、保存できます。一番近い一枚を残し、今後の壁紙、Luna ダウンロード、印刷コレクションの土台にできます。",
        "free_items": [
            ("画像を保存", "各カードは開く、またはダウンロードして、スマホや関係日記に残せます。"),
            ("共有入口", "共有カードを作り、結果を理解されやすい心語の一文にします。"),
            ("今後の土台", "壁紙、Luna ダウンロード、短い儀式、印刷コレクションはこの無料カードから優先して広げます。"),
        ],
        "asset_title": "五人の守護者の無料コレクション",
        "asset_intro": "各守護者に保存できるストーリーカードと印刷できる練習カードを用意し、今後の壁紙と Luna 補給形式へつなげます。",
        "asset_formats": ["ストーリーカード", "印刷できる練習カード", "スマホ壁紙候補", "Luna ダウンロード候補"],
        "asset_request": "この守護者の補給を希望する",
        "practice_title": "五人の守護者の印刷できる練習カード",
        "practice_intro": "守護者の結果を短いカードにします。すれ違いの傷、修復課題、補給を一つずつ書き、印刷または PDF 保存できます。",
        "practice_open": "練習カードを開く",
        "practice_print": "印刷 / PDF 保存",
        "practice_wound": "すれ違いの傷",
        "practice_mission": "今日の修復課題",
        "practice_supply": "延長補給",
        "practice_blank": "私の心語の一文",
        "how_title": "カードの使い方",
        "steps": [
            ("保存", "一番自分に近い守護者カードを保存し、結果を一回きりの答えで終わらせません。"),
            ("共有", "共有するときは、理解してほしい愛の入口を一つ具体的なお願いにします。"),
            ("再訪", "一週間後に同じカードへ戻り、小さな修復課題を一つ実行できたか確認します。"),
        ],
        "safety_title": "コレクションは要求ではありません",
        "safety_text": "カードは思い出すための入口であり、相手にすぐ従わせる証明ではありません。不安全、支配、強制がある場合は、まず信頼できる人や専門機関に相談してください。",
        "quiz": "もう一度診断",
        "resources": "補給へ戻る",
    },
    "ko": {
        "title": "수호자 소장실",
        "desc": "LoveTypes 다섯 수호자 스토리 카드를 저장해 테스트 결과를 공유, 재방문, 향후 보급 자산으로 이어지는 입구로 만듭니다.",
        "eyebrow": "GUARDIAN KEEPSAKE HALL",
        "intro": "각 카드는 마음 언어의 입구입니다. 스토리, 파트너에게 보내기, 관계 일기, 향후 소장형 보급의 기반으로 사용할 수 있습니다.",
        "free_title": "다섯 수호자 소장물을 무료로 가져가기",
        "free_intro": "현재 모든 수호자 스토리 카드와 연습 카드는 무료로 열고 저장할 수 있습니다. 가장 나다운 한 장을 남기고, 향후 배경화면, Luna 다운로드, 인쇄 소장팩의 기반으로 사용할 수 있습니다.",
        "free_items": [
            ("이미지 저장", "각 카드는 열거나 내려받아 휴대폰 앨범과 관계 일기에 둘 수 있습니다."),
            ("공유 입구", "공유 카드를 만들어 결과를 이해 가능한 마음 언어 한 문장으로 바꿉니다."),
            ("미래 소장 기반", "배경화면, Luna 다운로드, 짧은 의식, 인쇄 소장팩은 이 무료 소장물에서 먼저 확장됩니다."),
        ],
        "asset_title": "다섯 수호자 무료 소장물",
        "asset_intro": "각 수호자마다 저장 가능한 스토리 카드와 인쇄용 연습 카드를 제공하고, 향후 배경화면과 Luna 보급 형식으로 확장합니다.",
        "asset_formats": ["스토리 카드", "인쇄용 연습 카드", "휴대폰 배경화면 후보", "Luna 다운로드 후보"],
        "asset_request": "이 수호자 보급 요청하기",
        "practice_title": "다섯 수호자 인쇄용 연습 카드",
        "practice_intro": "수호자 결과를 짧은 카드로 정리합니다. 어긋남 상처, 회복 과제, 보급 하나를 적고 인쇄하거나 PDF로 저장하세요.",
        "practice_open": "연습 카드 열기",
        "practice_print": "인쇄 / PDF 저장",
        "practice_wound": "어긋남 상처",
        "practice_mission": "오늘의 회복 과제",
        "practice_supply": "확장 보급",
        "practice_blank": "나의 마음 언어 한 줄",
        "how_title": "카드 사용법",
        "steps": [
            ("저장", "가장 나다운 수호자 카드를 저장해 결과가 한 번의 답으로 끝나지 않게 합니다."),
            ("공유", "공유할 때 이해받고 싶은 사랑의 입구를 한 가지 구체적인 요청으로 덧붙입니다."),
            ("다시 보기", "일주일 뒤 같은 카드로 돌아와 작은 회복 과제를 하나 했는지 확인합니다."),
        ],
        "safety_title": "소장은 요구가 아닙니다",
        "safety_text": "카드는 기억과 대화의 입구이지, 파트너가 즉시 따라야 한다는 증거가 아닙니다. 안전하지 않거나 통제, 강요가 있다면 먼저 믿을 수 있는 사람과 전문 지원을 찾으세요.",
        "quiz": "다시 테스트",
        "resources": "보급으로 돌아가기",
    },
    "es": {
        "title": "Sala de recuerdos de guardianas",
        "desc": "Guarda las cinco tarjetas de guardianas LoveTypes para convertir tu resultado en algo compartible, revisitable y listo para futuros recursos coleccionables.",
        "eyebrow": "GUARDIAN KEEPSAKE HALL",
        "intro": "Cada tarjeta es una puerta de lenguaje del corazón: úsala en historias, envíala a una pareja, ponla en tu diario relacional o guárdala como base para futuros recursos coleccionables.",
        "free_title": "Llévate cinco recuerdos gratis",
        "free_intro": "Todas las tarjetas de historia y práctica pueden abrirse y guardarse gratis. Conserva la que más se parece a ti; futuros fondos, descargas Luna o packs impresos pueden crecer desde aquí.",
        "free_items": [
            ("Guardar imagen", "Abre o descarga cada tarjeta para tu álbum móvil o diario relacional."),
            ("Puerta para compartir", "Crea una historia para convertir el resultado en una frase de lenguaje del corazón."),
            ("Base coleccionable futura", "Fondos, descargas Luna, rituales breves y packs impresos crecerán primero desde estos recuerdos gratis."),
        ],
        "asset_title": "Cinco recuerdos gratis de guardianas",
        "asset_intro": "Cada guardiana empieza con una tarjeta de historia guardable, una tarjeta imprimible y una señal clara para futuros fondos y packs Luna.",
        "asset_formats": ["Tarjeta de historia", "Tarjeta imprimible", "Candidato a fondo móvil", "Candidato a pack Luna"],
        "asset_request": "Pedir recurso de esta guardiana",
        "practice_title": "Cinco tarjetas imprimibles de guardianas",
        "practice_intro": "Convierte el resultado en una tarjeta breve: nombra la herida, escribe una tarea de reparación y elige un recurso. Imprímela o guárdala como PDF.",
        "practice_open": "Abrir tarjeta práctica",
        "practice_print": "Imprimir / guardar PDF",
        "practice_wound": "Herida de desajuste",
        "practice_mission": "Tarea de reparación de hoy",
        "practice_supply": "Recurso extendido",
        "practice_blank": "Mi frase de lenguaje del corazón",
        "how_title": "Cómo usar las tarjetas",
        "steps": [
            ("Guardar", "Conserva la tarjeta que más se parece a ti para que el resultado no sea una respuesta de una sola vez."),
            ("Compartir", "Añade una petición concreta al compartir: qué entrada al amor quieres que se entienda?"),
            ("Volver", "Regresa después de una semana y revisa si completaste una pequeña tarea de reparación."),
        ],
        "safety_title": "Un recuerdo no es una exigencia",
        "safety_text": "La tarjeta es recordatorio y puerta de conversación, no prueba de que una pareja deba obedecer de inmediato. Si hay inseguridad, control o coerción, busca primero apoyo confiable y profesional.",
        "quiz": "Repetir test",
        "resources": "Volver a recursos",
    },
}


KEEPSAKE_RITUAL = {
    "zh": {
        "eyebrow": "SAVE · BLESS · RETURN",
        "title": "收藏儀式路線",
        "intro": "收藏卡不是終點，而是一張可回訪的心語通行證。把它放進日常前，先完成四個輕量步驟。",
        "steps": [
            ("保存身分", "選一張最像你的守護者卡，讓測驗結果成為可回看的身分標記。", "查看五張卡", "#keepsake-card-iris"),
            ("寫下一句心語", "把今天最想被理解的一句話寫進日記，避免只丟出結果讓對方猜。", "填入修復計畫", "repair-plan"),
            ("分享前補上界線", "傳給伴侶或發限動前，加上一句：這是我的入口，不是你的考卷。", "閱讀關係邊界", "about"),
            ("回到補給任務", "收藏後回到對應補給路線，完成一個免費任務，再決定是否需要書卷或 Luna。", "前往補給站", "resources"),
        ],
    },
    "en": {
        "eyebrow": "SAVE · BLESS · RETURN",
        "title": "Keepsake ritual route",
        "intro": "A card is not the endpoint. It is a heart-language pass you can return to, after four light steps.",
        "steps": [
            ("Save the identity", "Choose the guardian card that feels closest to you, so the result becomes a revisitable identity mark.", "View cards", "#keepsake-card-iris"),
            ("Write one line", "Put the sentence you most want understood into a journal instead of making the result do all the work.", "Use repair plan", "repair-plan"),
            ("Add a boundary", "Before sending or posting, add: this is my doorway, not your exam.", "Read boundaries", "about"),
            ("Return to supplies", "After saving, go back to the matching supply route, do one free task, then decide whether a book or Luna helps.", "Open supplies", "resources"),
        ],
    },
    "ja": {
        "eyebrow": "SAVE · BLESS · RETURN",
        "title": "コレクション儀式ルート",
        "intro": "カードは終点ではなく、戻ってこられる心語の通行証です。日常に置く前に、四つの軽い手順を通します。",
        "steps": [
            ("身分を保存", "一番自分に近い守護者カードを選び、結果を見返せる身分の印にします。", "五枚を見る", "#keepsake-card-iris"),
            ("一文を書く", "理解してほしい一文を日記に書き、結果だけを相手に渡して推測させません。", "修復プランへ", "repair-plan"),
            ("境界を添える", "送る前に、これは私の入口であって、あなたへの試験ではない、と一言添えます。", "境界を読む", "about"),
            ("補給へ戻る", "保存したら対応する補給ルートへ戻り、無料課題を一つ行ってから本や Luna を選びます。", "補給へ", "resources"),
        ],
    },
    "ko": {
        "eyebrow": "SAVE · BLESS · RETURN",
        "title": "소장 의식 루트",
        "intro": "카드는 끝이 아니라 다시 돌아올 수 있는 마음 언어 통행증입니다. 일상에 두기 전 네 단계를 가볍게 지나가세요.",
        "steps": [
            ("정체성 저장", "가장 나다운 수호자 카드를 골라 결과를 다시 볼 수 있는 정체성 표식으로 만듭니다.", "카드 보기", "#keepsake-card-iris"),
            ("한 줄 쓰기", "가장 이해받고 싶은 문장을 일기에 적어 결과만 던지고 상대가 맞히게 하지 않습니다.", "회복 계획 쓰기", "repair-plan"),
            ("경계 덧붙이기", "보내거나 올리기 전에 덧붙이세요. 이것은 나의 입구이지 당신의 시험지가 아니야.", "경계 읽기", "about"),
            ("보급으로 복귀", "저장 후 맞는 보급 루트로 돌아가 무료 과제를 하나 하고 책이나 Luna가 필요한지 정하세요.", "보급 열기", "resources"),
        ],
    },
    "es": {
        "eyebrow": "SAVE · BLESS · RETURN",
        "title": "Ruta ritual del recuerdo",
        "intro": "La tarjeta no es el final. Es un pase de lenguaje del corazón al que puedes volver después de cuatro pasos ligeros.",
        "steps": [
            ("Guardar identidad", "Elige la tarjeta que más se parece a ti para que el resultado sea una marca revisitable.", "Ver tarjetas", "#keepsake-card-iris"),
            ("Escribir una línea", "Lleva al diario la frase que más quieres que se entienda, en vez de hacer que el resultado cargue todo.", "Usar plan", "repair-plan"),
            ("Añadir límite", "Antes de enviar o publicar, añade: esta es mi puerta, no tu examen.", "Leer límites", "about"),
            ("Volver a recursos", "Después de guardar, vuelve a la ruta de suministro, haz una tarea gratuita y decide si un libro o Luna ayuda.", "Abrir recursos", "resources"),
        ],
    },
}


REPAIR_PLAN = {
    "zh": {
        "eyebrow": "7-DAY HEART-LANGUAGE PLAN",
        "title": "7 日心語修復計畫",
        "desc": "完成測驗後，不必立刻修完整段關係。用七天把守護者結果變成一張可回訪的練習路線：先看見傷口，再提出小請求，最後選一個補給支持你持續練習。",
        "days_title": "一週練習路線",
        "guardian_title": "依守護者調整任務",
        "start": "開始測驗",
        "resources": "打開補給站",
        "download": "保存這週路線",
        "asset_title": "免費修復卡包",
        "asset_intro": "把這週路線整理成三份可以帶走的工具：先收下守護者卡，再填工作表，最後只在需要時申請補給。這是進入守護者宇宙後最輕量的實作包。",
        "asset_items": [
            ("守護者收藏卡", "保存你的守護者故事圖，作為本週修復路線的入口。", "keepsakes", "打開收藏室"),
            ("7 日可列印工作表", "把錯頻、請求與補給寫成一頁，列印或存成 PDF。", "#repair-worksheet", "填寫工作表"),
            ("補給申請", "需要更明確的下一步時，留下你的守護者路線與想要的補給。", "contact#luna-supply-request", "申請補給"),
        ],
        "worksheet_title": "本週心語工作表",
        "worksheet_intro": "填下這四格，再列印或存成 PDF。它不是要你一次處理所有關係問題，而是留下下一次可以回來看的修復線索。",
        "print": "列印 / 存成 PDF",
        "autosave": "此工作表只會暫存在這台裝置的瀏覽器，不會送出到 LoveTypes。",
        "saved": "已自動保存",
        "clear": "清除本機內容",
        "cleared": "已清除",
        "copy_summary": "複製本週回顧",
        "summary_title": "LoveTypes 本週心語回顧",
        "summary_guardian": "守護者路線",
        "summary_next": "下一步補給",
        "summary_copied": "已複製回顧",
        "summary_empty": "先填寫一格，再複製回顧",
        "resume_title": "繼續你的 7 日路線",
        "resume_intro": "你上次認領的守護者可以直接帶入這份工作表。先做今天的小任務，再視情況選 Luna、補給站或延伸書卷。",
        "resume_fill": "帶入工作表",
        "resume_plan": "跳到守護者任務",
        "fields": [("我的守護者結果", "例如：艾莉絲，肯定的言詞"), ("這週最明顯的錯頻", "寫一個具體場景，不寫全部舊帳"), ("我真正想提出的小請求", "縮成 24 小時內可做到的一步"), ("我選擇的補給", "指南、Luna、書卷或一張收藏卡")],
        "days": [
            ("第 1 天", "認領你的守護者", "寫下結果、分數最高的愛之語，以及最近一次感覺沒被接住的場景。"),
            ("第 2 天", "命名錯頻傷口", "把受傷翻成一句話：我不是在要求完美，我是在乎哪一種被愛入口。"),
            ("第 3 天", "縮小成一個請求", "把需求縮成 24 小時內可以做到的一步，不把它說成考驗。"),
            ("第 4 天", "選一個補給", "回到旅人補給站，選指南、書卷或 Luna，不一次買齊或讀完整座庭園。"),
            ("第 5 天", "練習一段對話", "用守護者句型說出感受、需求與小請求，避免用類型替代溝通。"),
            ("第 6 天", "觀察回應", "記錄對方做得到、做不到或誤解的地方，把它當作下一次翻譯的資料。"),
            ("第 7 天", "回顧修復", "保留有效的做法，放下無效的期待，選下一週要繼續練的一個入口。"),
        ],
    },
    "en": {
        "eyebrow": "7-DAY HEART-LANGUAGE PLAN",
        "title": "7-Day Heart-Language Repair Plan",
        "desc": "After the quiz, use seven days to turn your guardian result into a revisitable route: notice the wound, ask for one small action, and choose one supply for practice.",
        "days_title": "One-week practice route",
        "guardian_title": "Adjust by guardian",
        "start": "Start quiz",
        "resources": "Open supply station",
        "download": "Save this route",
        "asset_title": "Free Repair Card Pack",
        "asset_intro": "Turn this week into three portable tools: save your guardian card, fill the worksheet, then request supply only when it truly helps. This is the lightest take-away from the guardian universe.",
        "asset_items": [
            ("Guardian keepsake card", "Save your guardian story image as the doorway back into this week's route.", "keepsakes", "Open keepsakes"),
            ("7-day printable worksheet", "Put the misfrequency, request, and chosen supply onto one page for print or PDF.", "#repair-worksheet", "Fill worksheet"),
            ("Supply request", "When you need a clearer next step, send your guardian route and the supply you want.", "contact#luna-supply-request", "Request supply"),
        ],
        "worksheet_title": "This Week's Heart-Language Worksheet",
        "worksheet_intro": "Fill these four fields, then print or save as PDF. It is not meant to solve every relationship issue at once; it leaves repair clues you can revisit.",
        "print": "Print / save as PDF",
        "autosave": "This worksheet is saved only in this browser on this device. It is not sent to LoveTypes.",
        "saved": "Autosaved",
        "clear": "Clear local notes",
        "cleared": "Cleared",
        "copy_summary": "Copy weekly review",
        "summary_title": "LoveTypes weekly heart-language review",
        "summary_guardian": "Guardian route",
        "summary_next": "Next supply",
        "summary_copied": "Review copied",
        "summary_empty": "Fill at least one field before copying",
        "resume_title": "Continue your 7-day route",
        "resume_intro": "Your last guardian result can be carried into this worksheet. Start with today's small task, then choose Luna, the supply station, or an extended book only if it fits.",
        "resume_fill": "Fill worksheet",
        "resume_plan": "Jump to guardian task",
        "fields": [("My guardian result", "Example: Iris, words of affirmation"), ("This week's clearest misfrequency", "Name one concrete scene, not every old wound"), ("The small request I actually want to make", "Shrink it into one step possible within 24 hours"), ("The supply I choose", "Guide, Luna, book, or keepsake card")],
        "days": [
            ("Day 1", "Claim your guardian", "Write down the result, the strongest love language, and one recent moment when you did not feel received."),
            ("Day 2", "Name the wound", "Translate hurt into one sentence: I am not asking for perfection; I care about this doorway to love."),
            ("Day 3", "Shrink the request", "Turn the need into one step that can happen within 24 hours, without making it a test."),
            ("Day 4", "Choose one supply", "Return to the supply station and pick one guide, book, or Luna path instead of trying everything at once."),
            ("Day 5", "Practice one conversation", "Name feeling, need, and one small request through your guardian language."),
            ("Day 6", "Observe the response", "Record what worked, what did not, and what was misunderstood. Treat it as material for the next translation."),
            ("Day 7", "Review repair", "Keep the useful action, release one unhelpful expectation, and choose next week's doorway."),
        ],
    },
    "ja": {
        "eyebrow": "7-DAY HEART-LANGUAGE PLAN",
        "title": "7日間の心語修復プラン",
        "desc": "診断後、関係全体をすぐ修復する必要はありません。七日間で守護者の結果を見返せる練習ルートにします。傷を見つけ、小さなお願いにし、補給を一つ選びます。",
        "days_title": "一週間の練習ルート",
        "guardian_title": "守護者別の調整",
        "start": "診断を始める",
        "resources": "補給ステーションを開く",
        "download": "このルートを保存",
        "asset_title": "無料修復カードパック",
        "asset_intro": "今週のルートを持ち帰れる三つの道具にします。守護者カードを保存し、ワークシートを埋め、必要な時だけ補給を申請します。",
        "asset_items": [
            ("守護者コレクションカード", "守護者のストーリー画像を保存し、今週のルートへ戻る入口にします。", "keepsakes", "コレクション室を開く"),
            ("7日間の印刷ワークシート", "すれ違い、お願い、選ぶ補給を一枚にまとめ、印刷または PDF 保存します。", "#repair-worksheet", "ワークシートを書く"),
            ("補給リクエスト", "次の一歩をより明確にしたい時、守護者ルートと欲しい補給を送ります。", "contact#luna-supply-request", "補給を申請"),
        ],
        "worksheet_title": "今週の心語ワークシート",
        "worksheet_intro": "四つの欄を埋め、印刷または PDF として保存します。すべての問題を一度に扱うのではなく、戻って見られる修復の手がかりを残します。",
        "print": "印刷 / PDF 保存",
        "autosave": "このワークシートはこの端末のブラウザ内にだけ保存され、LoveTypes へ送信されません。",
        "saved": "自動保存済み",
        "clear": "ローカル内容を消去",
        "cleared": "消去しました",
        "copy_summary": "今週の振り返りをコピー",
        "summary_title": "LoveTypes 今週の心語レビュー",
        "summary_guardian": "守護者ルート",
        "summary_next": "次の補給",
        "summary_copied": "振り返りをコピーしました",
        "summary_empty": "一つ以上入力してからコピーしてください",
        "resume_title": "7日間のルートを続ける",
        "resume_intro": "前回の守護者結果をこのワークシートへ引き継げます。今日の小さな課題から始め、必要なら Luna、補給ステーション、または本を一つ選びます。",
        "resume_fill": "ワークシートへ入れる",
        "resume_plan": "守護者課題へ移動",
        "fields": [("私の守護者結果", "例：アイリス、肯定の言葉"), ("今週いちばん明確なすれ違い", "具体的な場面を一つだけ書きます"), ("本当に伝えたい小さなお願い", "二十四時間以内にできる一歩へ縮めます"), ("選ぶ補給", "ガイド、Luna、本、守護者カード")],
        "days": [
            ("1日目", "守護者を認領する", "結果、もっとも強い愛の言語、最近受け取られなかった場面を書きます。"),
            ("2日目", "すれ違いの傷に名前をつける", "傷つきを一文にします。完璧を求めたいのではなく、この入口を大切にしたい。"),
            ("3日目", "お願いを小さくする", "ニーズを二十四時間以内にできる一歩へ縮め、試す形にしません。"),
            ("4日目", "補給を一つ選ぶ", "補給ステーションに戻り、ガイド、本、Luna のどれか一つを選びます。"),
            ("5日目", "会話を一つ練習する", "守護者の言語で感情、ニーズ、小さなお願いを伝えます。"),
            ("6日目", "反応を観察する", "できたこと、難しかったこと、誤解されたことを記録し、次の翻訳材料にします。"),
            ("7日目", "修復を見直す", "有効だった行動を残し、役に立たない期待を一つ手放し、来週の入口を選びます。"),
        ],
    },
    "ko": {
        "eyebrow": "7-DAY HEART-LANGUAGE PLAN",
        "title": "7일 마음 언어 회복 계획",
        "desc": "테스트 뒤 관계 전체를 한 번에 고칠 필요는 없습니다. 일주일 동안 수호자 결과를 다시 볼 수 있는 연습 루트로 바꾸세요. 상처를 보고, 작은 요청을 만들고, 보급 하나를 선택합니다.",
        "days_title": "일주일 연습 루트",
        "guardian_title": "수호자별 조정",
        "start": "테스트 시작",
        "resources": "보급소 열기",
        "download": "이 루트 저장",
        "asset_title": "무료 회복 카드 팩",
        "asset_intro": "이번 주 루트를 가져갈 수 있는 세 가지 도구로 정리합니다. 수호자 카드를 저장하고, 워크시트를 채운 뒤, 필요할 때만 보급을 신청하세요.",
        "asset_items": [
            ("수호자 소장 카드", "수호자 이야기 이미지를 저장해 이번 주 루트로 돌아오는 입구로 둡니다.", "keepsakes", "소장실 열기"),
            ("7일 인쇄 워크시트", "어긋남, 요청, 선택한 보급을 한 장에 적어 인쇄하거나 PDF로 저장합니다.", "#repair-worksheet", "워크시트 작성"),
            ("보급 신청", "다음 한 걸음이 더 필요할 때 수호자 루트와 원하는 보급을 보냅니다.", "contact#luna-supply-request", "보급 신청"),
        ],
        "worksheet_title": "이번 주 마음 언어 워크시트",
        "worksheet_intro": "네 칸을 채운 뒤 인쇄하거나 PDF로 저장하세요. 모든 관계 문제를 한 번에 해결하려는 것이 아니라 다시 볼 수 있는 회복 단서를 남기는 도구입니다.",
        "print": "인쇄 / PDF 저장",
        "autosave": "이 워크시트는 이 기기의 브라우저에만 저장되며 LoveTypes로 전송되지 않습니다.",
        "saved": "자동 저장됨",
        "clear": "로컬 내용 지우기",
        "cleared": "지워짐",
        "copy_summary": "이번 주 회고 복사",
        "summary_title": "LoveTypes 이번 주 마음 언어 회고",
        "summary_guardian": "수호자 루트",
        "summary_next": "다음 보급",
        "summary_copied": "회고가 복사됨",
        "summary_empty": "한 칸 이상 입력한 뒤 복사하세요",
        "resume_title": "7일 루트 이어가기",
        "resume_intro": "마지막 수호자 결과를 이 워크시트로 가져올 수 있습니다. 오늘의 작은 과제부터 시작하고, 필요할 때 Luna, 보급소, 책 중 하나를 선택하세요.",
        "resume_fill": "워크시트에 넣기",
        "resume_plan": "수호자 과제로 이동",
        "fields": [("나의 수호자 결과", "예: 아이리스, 인정의 말"), ("이번 주 가장 분명한 어긋남", "구체적인 장면 하나만 씁니다"), ("내가 실제로 말하고 싶은 작은 요청", "24시간 안에 가능한 한 걸음으로 줄입니다"), ("내가 선택한 보급", "가이드, Luna, 책, 수호자 카드")],
        "days": [
            ("1일차", "수호자 인정하기", "결과, 가장 강한 사랑의 언어, 최근 받지 못했다고 느낀 장면을 적습니다."),
            ("2일차", "어긋남 상처 이름 붙이기", "상처를 한 문장으로 바꿉니다. 완벽을 바라는 것이 아니라 이 사랑의 입구를 중요하게 여깁니다."),
            ("3일차", "요청 줄이기", "욕구를 24시간 안에 가능한 한 걸음으로 줄이고 시험처럼 만들지 않습니다."),
            ("4일차", "보급 하나 선택", "보급소로 돌아가 가이드, 책, Luna 중 하나만 고릅니다."),
            ("5일차", "대화 하나 연습", "수호자의 언어로 감정, 욕구, 작은 요청을 말합니다."),
            ("6일차", "반응 관찰", "된 것, 어려운 것, 오해된 것을 기록해 다음 번역의 자료로 삼습니다."),
            ("7일차", "회복 점검", "효과가 있던 행동을 남기고 도움이 안 되는 기대 하나를 내려놓고 다음 주 입구를 고릅니다."),
        ],
    },
    "es": {
        "eyebrow": "7-DAY HEART-LANGUAGE PLAN",
        "title": "Plan de reparación de 7 días",
        "desc": "Después del test, usa siete días para convertir tu resultado en una ruta revisitable: mira la herida, pide una acción pequeña y elige un recurso.",
        "days_title": "Ruta de práctica semanal",
        "guardian_title": "Ajusta por guardiana",
        "start": "Iniciar test",
        "resources": "Abrir recursos",
        "download": "Guardar esta ruta",
        "asset_title": "Pack gratuito de reparación",
        "asset_intro": "Convierte esta semana en tres herramientas portátiles: guarda tu tarjeta de guardiana, completa la hoja y pide apoyo solo cuando de verdad ayude.",
        "asset_items": [
            ("Tarjeta de guardiana", "Guarda la imagen de historia de tu guardiana como puerta de regreso a esta ruta.", "keepsakes", "Abrir colección"),
            ("Hoja imprimible de 7 días", "Pon el desajuste, la petición y el recurso elegido en una página para imprimir o PDF.", "#repair-worksheet", "Completar hoja"),
            ("Solicitud de recurso", "Cuando necesites un siguiente paso más claro, envía tu ruta de guardiana y el apoyo que quieres.", "contact#luna-supply-request", "Pedir recurso"),
        ],
        "worksheet_title": "Hoja de trabajo de esta semana",
        "worksheet_intro": "Completa estos cuatro campos y luego imprime o guarda como PDF. No busca resolver toda la relación de una vez; deja pistas de reparación para volver a mirar.",
        "print": "Imprimir / guardar PDF",
        "autosave": "Esta hoja se guarda solo en este navegador y dispositivo. No se envía a LoveTypes.",
        "saved": "Autoguardado",
        "clear": "Borrar notas locales",
        "cleared": "Borrado",
        "copy_summary": "Copiar revisión semanal",
        "summary_title": "Revisión semanal LoveTypes",
        "summary_guardian": "Ruta de guardiana",
        "summary_next": "Próximo recurso",
        "summary_copied": "Revisión copiada",
        "summary_empty": "Completa al menos un campo antes de copiar",
        "resume_title": "Continúa tu ruta de 7 días",
        "resume_intro": "Tu última guardiana puede entrar en esta hoja. Empieza con la tarea pequeña de hoy y luego elige Luna, recursos o un libro solo si encaja.",
        "resume_fill": "Completar hoja",
        "resume_plan": "Ir a tarea de guardiana",
        "fields": [("Mi resultado de guardiana", "Ejemplo: Iris, palabras de afirmación"), ("El desajuste más claro de esta semana", "Nombra una escena concreta, no todas las heridas"), ("La petición pequeña que quiero hacer", "Redúcela a un paso posible dentro de 24 horas"), ("El recurso que elijo", "Guía, Luna, libro o tarjeta de recuerdo")],
        "days": [
            ("Día 1", "Reclama tu guardiana", "Escribe el resultado, el lenguaje más fuerte y un momento reciente en que no te sentiste recibida."),
            ("Día 2", "Nombra la herida", "Traduce el dolor en una frase: no pido perfección; me importa esta puerta para recibir amor."),
            ("Día 3", "Reduce la petición", "Convierte la necesidad en un paso posible dentro de 24 horas, sin volverlo una prueba."),
            ("Día 4", "Elige un recurso", "Vuelve a recursos y elige una guía, libro o camino Luna en vez de intentar todo a la vez."),
            ("Día 5", "Practica una conversación", "Nombra emoción, necesidad y una petición pequeña con el lenguaje de tu guardiana."),
            ("Día 6", "Observa la respuesta", "Registra qué funcionó, qué no, y qué se malentendió. Úsalo para la próxima traducción."),
            ("Día 7", "Revisa la reparación", "Conserva la acción útil, suelta una expectativa inútil y elige la puerta de la próxima semana."),
        ],
    },
}


GUARDIANS = {
    "iris": {
        "asset": "/assets/lovetypes/guardians/iris.webp",
        "card_asset": "/assets/lovetypes/guardians/cards/iris-card.webp",
        "prop": "/assets/lovetypes/props/affirmation-feather-pen.webp",
        "zh": ("艾莉絲", "肯定的言詞", "她在晨曦玻璃花園守護被準確看見的心，替那些等很久的話點亮名字。"),
        "en": ("Iris", "Words of affirmation", "In the dawn-glass garden, she guards the heart that longs to be seen clearly and gives names to words that waited too long."),
        "ja": ("アイリス", "肯定の言葉", "夜明けのガラス庭園で、正確に見てもらいたい心を守り、長く待っていた言葉に名前を与えます。"),
        "ko": ("아이리스", "인정의 말", "새벽 유리 정원에서 정확히 보이고 싶은 마음을 지키며, 오래 기다린 말들에 이름을 붙여 줍니다."),
        "es": ("Iris", "Palabras de afirmación", "En el jardín de cristal del amanecer, protege el corazón que quiere ser visto con precisión y da nombre a palabras que esperaron demasiado."),
    },
    "noah": {
        "asset": "/assets/lovetypes/guardians/noah.webp",
        "card_asset": "/assets/lovetypes/guardians/cards/noah-card.webp",
        "prop": "/assets/lovetypes/props/quality-time-lantern.webp",
        "zh": ("諾雅", "優質的時光", "她航行在星海書庫與安靜海面之間，守護真正留在彼此身邊的時間。"),
        "en": ("Noah", "Quality time", "Between the star-sea library and a quiet shore, she guards the kind of time where two people truly stay."),
        "ja": ("ノア", "上質な時間", "星海の書庫と静かな海辺のあいだを進み、二人が本当にそこに留まる時間を守ります。"),
        "ko": ("노아", "함께하는 시간", "별바다 서고와 고요한 해변 사이를 항해하며, 두 사람이 진짜로 머무는 시간을 지킵니다."),
        "es": ("Noah", "Tiempo de calidad", "Entre la biblioteca del mar estelar y una orilla tranquila, protege el tiempo en que dos personas realmente se quedan."),
    },
    "vivian": {
        "asset": "/assets/lovetypes/guardians/vivian.webp",
        "card_asset": "/assets/lovetypes/guardians/cards/vivian-card.webp",
        "prop": "/assets/lovetypes/props/gifts-ribboned-gift-box.webp",
        "zh": ("薇薇安", "接受禮物", "她在月光記憶工坊收藏被想起的證據，讓心意停在細節，而不是價格。"),
        "en": ("Vivian", "Receiving gifts", "In the moonlit memory workshop, she collects proof of being remembered and keeps meaning in details, not price."),
        "ja": ("ヴィヴィアン", "贈り物", "月光の記憶工房で、思い出してもらえた証を集め、心意を値段ではなく細部に残します。"),
        "ko": ("비비안", "선물 받기", "달빛 기억 공방에서 떠올려졌다는 증거를 모으고, 마음을 가격이 아니라 세부에 머물게 합니다."),
        "es": ("Vivian", "Recibir regalos", "En el taller de memoria bajo la luna, guarda pruebas de haber sido recordada y deja el significado en los detalles, no en el precio."),
    },
    "claire": {
        "asset": "/assets/lovetypes/guardians/claire.webp",
        "card_asset": "/assets/lovetypes/guardians/cards/claire-card.webp",
        "prop": "/assets/lovetypes/props/service-tool-pouch.webp",
        "zh": ("克萊兒", "服務的行動", "她守著不停修復的溫室，把承諾放回日常，讓疲憊不再只由一個人撐住。"),
        "en": ("Claire", "Acts of service", "In a greenhouse of ongoing repair, she returns promises to daily life so one tired person does not hold everything alone."),
        "ja": ("クレア", "奉仕の行動", "修復の続く温室を守り、約束を日常へ戻して、疲れを一人だけで抱えないようにします。"),
        "ko": ("클레어", "봉사의 행동", "계속 수리되는 온실을 지키며 약속을 일상으로 돌려놓고, 피로를 한 사람만 버티지 않게 합니다."),
        "es": ("Claire", "Actos de servicio", "En un invernadero siempre en reparación, devuelve las promesas a la vida diaria para que una sola persona cansada no sostenga todo."),
    },
    "dora": {
        "asset": "/assets/lovetypes/guardians/dora.webp",
        "card_asset": "/assets/lovetypes/guardians/cards/dora-card.webp",
        "prop": "/assets/lovetypes/props/touch-golden-hug-glow.webp",
        "zh": ("朵拉", "身體的接觸", "她在柔暖聖域守護經過同意的靠近，讓身體重新記得安全的溫度。"),
        "en": ("Dora", "Physical touch", "In a warm sanctuary, she guards closeness after consent and helps the body remember the temperature of safety."),
        "ja": ("ドーラ", "身体的なふれあい", "やわらかな聖域で、同意の後にある近さを守り、身体が安全の温度を思い出すよう助けます。"),
        "ko": ("도라", "스킨십", "따뜻한 성역에서 동의 이후의 가까움을 지키며 몸이 안전의 온도를 다시 기억하게 합니다."),
        "es": ("Dora", "Contacto físico", "En un santuario cálido, protege la cercanía después del consentimiento y ayuda al cuerpo a recordar la temperatura de la seguridad."),
    },
}


GUARDIAN_DOMAINS = {
    "iris": {
        "accent": "#943743",
        "glow": "#f0c778",
        "motif": "dawn-glass-garden",
        "zh": ("晨曦玻璃花園", "羽筆與手寫光會把等很久的話照亮。", "進入艾莉絲的語言宇宙"),
        "en": ("Dawn-Glass Garden", "Feather-pen light gives shape to words that waited too long.", "Enter Iris' word universe"),
        "ja": ("夜明けのガラス庭園", "羽根ペンと手書きの光が、長く待った言葉を照らします。", "アイリスの言葉の宇宙へ"),
        "ko": ("새벽 유리 정원", "깃펜과 손글씨 빛이 오래 기다린 말을 밝힙니다.", "아이리스의 말 우주로"),
        "es": ("Jardín de cristal del amanecer", "La luz de pluma da forma a palabras que esperaron demasiado.", "Entrar al universo de Iris"),
    },
    "noah": {
        "accent": "#50417b",
        "glow": "#b8c7e8",
        "motif": "star-sea-library",
        "zh": ("星海圖書館", "星圖與安靜海面保存真正留在彼此身邊的時間。", "進入諾雅的時間宇宙"),
        "en": ("Star-Sea Library", "Star maps and quiet water preserve time where two people truly stay.", "Enter Noah's time universe"),
        "ja": ("星海の図書館", "星図と静かな水面が、二人が本当に留まる時間を守ります。", "ノアの時間の宇宙へ"),
        "ko": ("별바다 도서관", "별지도와 고요한 수면이 진짜 머무는 시간을 지킵니다.", "노아의 시간 우주로"),
        "es": ("Biblioteca del mar estelar", "Mapas de estrellas y agua quieta guardan el tiempo de quedarse.", "Entrar al universo de Noah"),
    },
    "vivian": {
        "accent": "#76501c",
        "glow": "#e9b2a0",
        "motif": "moonlit-memory-workshop",
        "zh": ("月光記憶工坊", "緞帶、票根與禮物盒收藏被想起的證據。", "進入薇薇安的記憶宇宙"),
        "en": ("Moonlit Memory Workshop", "Ribbons, ticket stubs, and boxes keep proof of being remembered.", "Enter Vivian's memory universe"),
        "ja": ("月光の記憶工房", "リボン、半券、小箱が思い出された証を集めます。", "ヴィヴィアンの記憶の宇宙へ"),
        "ko": ("달빛 기억 공방", "리본, 표 조각, 상자가 떠올려졌다는 증거를 모읍니다.", "비비안의 기억 우주로"),
        "es": ("Taller de memoria lunar", "Cintas, boletos y cajas guardan pruebas de haber sido recordada.", "Entrar al universo de Vivian"),
    },
    "claire": {
        "accent": "#435a43",
        "glow": "#d8c79a",
        "motif": "greenhouse-repair-room",
        "zh": ("溫室修復間", "工具袋與暖白燈把承諾放回日常。", "進入克萊兒的行動宇宙"),
        "en": ("Greenhouse Repair Room", "Tool pouches and warm work lights return promises to daily life.", "Enter Claire's action universe"),
        "ja": ("温室の修復室", "道具袋と暖かな作業灯が、約束を日常へ戻します。", "クレアの行動の宇宙へ"),
        "ko": ("온실 수리실", "도구 주머니와 따뜻한 작업등이 약속을 일상으로 돌립니다.", "클레어의 행동 우주로"),
        "es": ("Invernadero de reparación", "Herramientas y luz cálida devuelven promesas a lo cotidiano.", "Entrar al universo de Claire"),
    },
    "dora": {
        "accent": "#923e4a",
        "glow": "#f0b49c",
        "motif": "rose-gold-safe-sanctuary",
        "zh": ("玫瑰金安全聖域", "柔軟布料與暖光守護經過同意的靠近。", "進入朵拉的溫度宇宙"),
        "en": ("Rose-Gold Safe Sanctuary", "Soft fabric and warm light guard closeness after consent.", "Enter Dora's warmth universe"),
        "ja": ("ローズゴールドの安全な聖域", "柔らかな布と暖光が、同意のある近さを守ります。", "ドーラの温度の宇宙へ"),
        "ko": ("로즈골드 안전 성역", "부드러운 천과 따뜻한 빛이 동의 이후의 가까움을 지킵니다.", "도라의 온기 우주로"),
        "es": ("Santuario seguro rosa dorado", "Tela suave y luz cálida protegen la cercanía con consentimiento.", "Entrar al universo de Dora"),
    },
}


GUIDES = [
    {
        "slug": "share-your-result",
        "guardian": "iris",
        "zh": ("測驗結果怎麼跟伴侶說", "把守護者結果從有趣分享，翻成對方聽得懂的真實需求。"),
        "en": ("How to Share Your Result With a Partner", "Turn your guardian result from a fun share into a real need the other person can hear."),
        "ja": ("結果をパートナーに伝える方法", "守護者の結果を、楽しい共有から相手に届く本当のニーズへ翻訳します。"),
        "ko": ("결과를 파트너에게 말하는 방법", "수호자 결과를 재미있는 공유에서 상대가 들을 수 있는 진짜 욕구로 번역합니다."),
        "es": ("Cómo compartir tu resultado con tu pareja", "Convierte tu resultado de guardiana en una necesidad real que la otra persona pueda escuchar."),
    },
    {
        "slug": "repair-after-conflict",
        "guardian": "noah",
        "zh": ("吵架後的五種愛之語修復法", "在錯頻的霧散去之前，用五種愛之語把道歉、時間、行動與安全感接回來。"),
        "en": ("Repair After Conflict With Five Love Languages", "Before the mist of misfrequency settles, reconnect apology, time, action, memory, and safety in a language your partner can receive."),
        "ja": ("衝突後に五つの愛の言語で修復する", "すれ違いの霧が濃くなる前に、謝罪、時間、行動、記憶、安全を相手が受け取れる形でつなぎ直します。"),
        "ko": ("갈등 후 다섯 가지 사랑의 언어로 회복하기", "어긋남의 안개가 짙어지기 전에 사과, 시간, 행동, 기억, 안전감을 상대가 받을 수 있는 언어로 다시 잇습니다."),
        "es": ("Reparar después de un conflicto con cinco lenguajes", "Antes de que la niebla del desajuste se cierre, reconecta disculpa, tiempo, acción, memoria y seguridad en un idioma que la otra persona pueda recibir."),
    },
    {
        "slug": "words-of-affirmation-scripts",
        "guardian": "iris",
        "zh": ("肯定言詞的具體句型", "跟著艾莉絲把空泛稱讚拆成看見、感謝、承認與承諾。"),
        "en": ("Practical Scripts for Words of Affirmation", "Follow Iris to turn vague praise into being seen, thanked, acknowledged, and promised to."),
        "ja": ("肯定の言葉の実用フレーズ", "アイリスと一緒に、曖昧な褒め言葉を、見ていること、感謝、承認、約束へ分けます。"),
        "ko": ("인정의 말을 위한 실제 문장", "아이리스와 함께 막연한 칭찬을 알아봄, 감사, 인정, 약속으로 나눕니다."),
        "es": ("Frases prácticas para palabras de afirmación", "Sigue a Iris para convertir elogios vagos en ser vista, gratitud, reconocimiento y compromiso."),
    },
    {
        "slug": "acts-of-service-boundaries",
        "guardian": "claire",
        "zh": ("服務行動與情緒勞動界線", "跟著克萊兒分辨照顧、分擔、討好與被消耗，讓行動不變成壓迫。"),
        "en": ("Acts of Service and Emotional Labor Boundaries", "Follow Claire to tell care, support, people-pleasing, and exhaustion apart before action becomes pressure."),
        "ja": ("奉仕の行動と感情労働の境界線", "クレアと一緒に、ケア、支援、迎合、消耗を区別し、行動が圧力にならないようにします。"),
        "ko": ("봉사의 행동과 감정 노동의 경계", "클레어와 함께 돌봄, 분담, 맞춰주기, 소진을 구분해 행동이 압박이 되지 않게 합니다."),
        "es": ("Actos de servicio y límites del trabajo emocional", "Sigue a Claire para distinguir cuidado, apoyo, complacencia y agotamiento antes de que la acción se vuelva presión."),
    },
    {
        "slug": "gifts-are-not-materialism",
        "guardian": "vivian",
        "zh": ("禮物型不是物質", "跟著薇薇安看見禮物背後的記得、觀察與珍惜，而不是價格。"),
        "en": ("Receiving Gifts Is Not Materialism", "Follow Vivian to see the memory, attention, and care behind a gift rather than its price."),
        "ja": ("贈り物タイプは物質主義ではない", "ヴィヴィアンと一緒に、贈り物の奥にある記憶、観察、大切にする気持ちを見ます。"),
        "ko": ("선물형은 물질주의가 아니다", "비비안과 함께 선물 뒤의 기억, 관찰, 소중히 여김을 봅니다. 가격이 아니라 세부를 봅니다."),
        "es": ("Recibir regalos no es materialismo", "Sigue a Vivian para ver la memoria, atención y cuidado detrás del regalo, no su precio."),
    },
    {
        "slug": "quality-time-long-distance",
        "guardian": "noah",
        "zh": ("優質時光與遠距關係", "跟著諾雅在距離裡留下燈，設計能被感覺到的日常在場。"),
        "en": ("Quality Time in Long-Distance Relationships", "Follow Noah to leave a lamp inside distance and design daily presence that can actually be felt."),
        "ja": ("遠距離関係の上質な時間", "ノアと一緒に、距離の中に灯りを残し、感じられる日常の存在を設計します。"),
        "ko": ("장거리 관계에서 함께하는 시간", "노아와 함께 거리 속에 등불을 남기고 실제로 느껴지는 일상의 존재감을 설계합니다."),
        "es": ("Tiempo de calidad en relaciones a distancia", "Sigue a Noah para dejar una luz dentro de la distancia y diseñar presencia cotidiana que sí pueda sentirse."),
    },
    {
        "slug": "physical-touch-consent-safety",
        "guardian": "dora",
        "zh": ("身體接觸、同意與安全感", "跟著朵拉把靠近放回同意裡，讓親密先成為安全，再成為溫度。"),
        "en": ("Physical Touch, Consent, and Safety", "Follow Dora to return closeness to consent, so intimacy becomes safety before it becomes warmth."),
        "ja": ("身体的なふれあい、同意、安全感", "ドーラと一緒に、近さを同意へ戻し、親密さが温度になる前に安全になるよう整えます。"),
        "ko": ("스킨십, 동의, 안전감", "도라와 함께 가까움을 동의로 되돌리고, 친밀함이 온도가 되기 전에 먼저 안전이 되게 합니다."),
        "es": ("Contacto físico, consentimiento y seguridad", "Sigue a Dora para devolver la cercanía al consentimiento, de modo que la intimidad sea seguridad antes de ser temperatura."),
    },
    {
        "slug": "weekly-relationship-review",
        "guardian": "claire",
        "zh": ("每週關係回顧問題", "用十五分鐘巡視心語庭園，整理被愛時刻、錯頻片刻與下一步小約定。"),
        "en": ("Weekly Relationship Review Questions", "Use fifteen minutes to walk the Heart Garden: loved moments, misfrequency moments, and one small next agreement."),
        "ja": ("週一回の関係ふり返り質問", "十五分で心語の庭を歩き、愛された瞬間、すれ違い、小さな次の約束を整理します。"),
        "ko": ("매주 관계 점검 질문", "15분 동안 마음의 정원을 걸으며 사랑받은 순간, 어긋난 순간, 다음 작은 약속을 정리합니다."),
        "es": ("Preguntas semanales para revisar la relación", "Usa quince minutos para recorrer el Jardín del Corazón: momentos de amor, desajustes y un pequeño acuerdo siguiente."),
    },
    {
        "slug": "emotional-needs-checklist",
        "guardian": "vivian",
        "zh": ("情感需求自我檢查表", "把心裡模糊的霧，拆成可說出口的需要、界線與請求。"),
        "en": ("Emotional Needs Self-Checklist", "Turn the vague mist inside your heart into needs, boundaries, and requests you can actually name."),
        "ja": ("感情ニーズのセルフチェック", "心の中の曖昧な霧を、言葉にできるニーズ、境界線、お願いへ分けます。"),
        "ko": ("정서적 욕구 자기 체크리스트", "마음속 막연한 안개를 말할 수 있는 욕구, 경계, 요청으로 나눕니다."),
        "es": ("Lista de revisión de necesidades emocionales", "Convierte la niebla vaga del corazón en necesidades, límites y peticiones que sí puedes nombrar."),
    },
    {
        "slug": "misfrequency-examples",
        "guardian": "iris",
        "zh": ("五種愛之語錯頻案例", "看懂你明明帶著愛靠近，對方卻沒有收到的錯頻原因。"),
        "en": ("Love-Language Misfrequency Examples", "See why you can approach with love and still miss the way another person receives it."),
        "ja": ("愛の言語のすれ違い例", "愛を持って近づいているのに、相手に届かないすれ違いの理由を理解します。"),
        "ko": ("사랑의 언어 어긋남 사례", "사랑을 가지고 다가갔는데도 상대가 받지 못한 어긋남의 이유를 봅니다."),
        "es": ("Ejemplos de desajuste en lenguajes del amor", "Entiende por qué puedes acercarte con amor y aun así no llegar en la forma que la otra persona recibe."),
    },
    {
        "slug": "relationship-stages",
        "guardian": "noah",
        "zh": ("單身、曖昧、交往、遠距如何使用結果", "不同關係季節，適合不同的守護者解讀方式與行動尺度。"),
        "en": ("Using Your Result Across Relationship Stages", "Different relationship seasons need different guardian readings and different scales of action."),
        "ja": ("関係段階ごとの結果の使い方", "関係の季節ごとに、守護者の読み方と行動の大きさは変わります。"),
        "ko": ("관계 단계별 결과 활용법", "관계의 계절마다 수호자를 읽는 방식과 행동의 크기가 달라집니다."),
        "es": ("Usar tu resultado en distintas etapas de relación", "Cada estación de relación necesita una lectura distinta de las guardianas y una escala distinta de acción."),
    },
    {
        "slug": "healthy-boundaries",
        "guardian": "dora",
        "zh": ("健康界線與關係安全", "心語庭園也需要邊界：愛之語不能取代尊重、同意、責任分擔與安全。"),
        "en": ("Healthy Boundaries and Relationship Safety", "The Heart Garden needs boundaries too: love languages cannot replace respect, consent, shared responsibility, and safety."),
        "ja": ("健康な境界線と関係の安全", "心語の庭にも境界線が必要です。愛の言語は尊重、同意、責任、安全の代わりにはなりません。"),
        "ko": ("건강한 경계와 관계 안전", "마음의 정원에도 경계가 필요합니다. 사랑의 언어는 존중, 동의, 책임 분담, 안전을 대신할 수 없습니다."),
        "es": ("Límites saludables y seguridad relacional", "El Jardín del Corazón también necesita límites: los lenguajes del amor no reemplazan respeto, consentimiento, responsabilidad compartida y seguridad."),
    },
]


LEGACY_ZH_GUIDES = [
    ("before-sharing-result", "分享結果前，先把心語入口說清楚", "把測驗結果分享給伴侶或朋友前，先整理你真正希望被理解、被接住的地方。", "share-your-result"),
    ("claire-acts-of-service", "克萊兒：把承諾放回日常溫室", "從克萊兒的守護者視角理解行動、承諾、分擔與情緒勞動界線。", "acts-of-service-boundaries"),
    ("conflict-repair-worksheet", "錯頻修復工作表", "用五個步驟整理受傷片刻、修復語言與下一次衝突前的安全約定。", "repair-after-conflict"),
    ("dialogue-scripts", "守護者對話句型集", "用可以直接開口的句型，把測驗結果變成不指責、可承擔的小請求。", "words-of-affirmation-scripts"),
    ("dora-physical-touch", "朵拉：同意之後的安全靠近", "從朵拉的守護者視角理解親密、同意、身體安定與界線。", "physical-touch-consent-safety"),
    ("guardian-pairings", "守護者配對與錯頻地圖", "看懂不同愛之語相遇時，哪一段路最容易起霧、誤解或失去訊號。", "misfrequency-examples"),
    ("heart-garden", "心語庭園：整理你的被愛入口", "把被愛入口、情感傷口與可練習行動放回一張清楚地圖。", "emotional-needs-checklist"),
    ("iris-words-of-affirmation", "艾莉絲：把等很久的話說清楚", "從艾莉絲的守護者視角理解具體肯定、感謝、承認與被看見。", "words-of-affirmation-scripts"),
    ("love-language-examples", "五種愛之語在日常裡如何發光", "用日常情境理解肯定、陪伴、禮物、行動與身體接觸如何被接收。", "misfrequency-examples"),
    ("misfrequency", "愛之語錯頻：為什麼你付出很多卻沒被收到", "整理常見錯頻案例，讓善意變成對方真的能接收的形式。", "misfrequency-examples"),
    ("noah-quality-time", "諾雅：在星海裡留下專注陪伴", "從諾雅的守護者視角理解專心、同在、等待與遠距連結。", "quality-time-long-distance"),
    ("relationship-review-questions", "伴侶每週心語回顧問題", "用十五分鐘回顧被愛時刻、錯頻片刻、修復需求與下週小約定。", "weekly-relationship-review"),
    ("use-your-result", "測驗結果怎麼真正用在關係裡", "把守護者結果從有趣標籤，變成能說出口的需要、界線與行動。", "share-your-result"),
    ("vivian-receiving-gifts", "薇薇安：禮物是被記得的證據", "從薇薇安的守護者視角理解心意、細節、儀式感與被珍惜的感覺。", "gifts-are-not-materialism"),
]


TOPIC_DETAILS = {
    "zh": {
        "why": "為什麼這很重要",
        "notice": "先辨認你的真實需求",
        "scripts": "可以直接使用的句型",
        "practice": "可執行練習",
        "mistakes": "常見誤區",
        "next": "下一步閱讀",
        "reflection": "反思問題",
    },
    "en": {
        "why": "Why this matters",
        "notice": "Name the real need first",
        "scripts": "Scripts you can use",
        "practice": "Practical exercise",
        "mistakes": "Common mistakes",
        "next": "Read next",
        "reflection": "Reflection questions",
    },
    "ja": {
        "why": "なぜ大切なのか",
        "notice": "本当のニーズを先に見つける",
        "scripts": "そのまま使える言葉",
        "practice": "実践練習",
        "mistakes": "よくある誤解",
        "next": "次に読む",
        "reflection": "ふり返り質問",
    },
    "ko": {
        "why": "왜 중요한가",
        "notice": "먼저 진짜 욕구를 알아차리기",
        "scripts": "바로 쓸 수 있는 문장",
        "practice": "실천 연습",
        "mistakes": "흔한 오해",
        "next": "다음 읽기",
        "reflection": "성찰 질문",
    },
    "es": {
        "why": "Por qué importa",
        "notice": "Nombra primero la necesidad real",
        "scripts": "Frases que puedes usar",
        "practice": "Ejercicio práctico",
        "mistakes": "Errores comunes",
        "next": "Leer después",
        "reflection": "Preguntas de reflexión",
    },
}


GUIDE_ACTION_BRIDGE = {
    "zh": {
        "eyebrow": "把這篇指南帶進守護者路線",
        "title": "下一步，讓這盞燈變成可執行的修復",
        "intro": "如果這篇指南點中了你的狀態，先認回守護者，再拿一份補給與一個 7 日練習。不要一次修完整座庭園，先讓一條路變清楚。",
        "guardian_label": "認回守護者",
        "guardian_text": "看懂這位守護者守護的需求、錯頻傷口與修復任務。",
        "route_label": "取得補給路線",
        "route_text": "依照這位守護者選一份免費任務、Luna 使用場景與延伸書卷。",
        "plan_label": "填入 7 日修復",
        "plan_text": "把今天讀到的句子放進一週內可完成的小約定。",
        "luna_label": "夜晚先降噪",
        "luna_text": "如果讀完後情緒太滿，先用 Luna 把這份理解整理成一句可寫下的心語。",
        "guardian_cta": "進入守護者頁",
        "route_cta": "查看補給路線",
        "plan_cta": "開始修復計畫",
        "luna_cta": "開啟 Luna",
    },
    "en": {
        "eyebrow": "Carry this guide into a guardian route",
        "title": "Next, turn this lamp into a practical repair",
        "intro": "If this guide names your current state, return to the guardian first, then take one supply route and one 7-day practice. Do not repair the whole garden at once; make one path clear.",
        "guardian_label": "Return to the guardian",
        "guardian_text": "Understand the need, misfrequency wound, and repair mission this guardian protects.",
        "route_label": "Get the supply route",
        "route_text": "Choose one free task, Luna use case, and deeper book scroll for this guardian.",
        "plan_label": "Fill the 7-day repair",
        "plan_text": "Place the sentence you found today into a small agreement you can practice this week.",
        "luna_label": "Lower the night noise",
        "luna_text": "If feelings are loud after reading, use Luna to turn this insight into one line you can write down.",
        "guardian_cta": "Enter guardian page",
        "route_cta": "View supply route",
        "plan_cta": "Start repair plan",
        "luna_cta": "Open Luna",
    },
    "ja": {
        "eyebrow": "このガイドを守護者ルートへつなぐ",
        "title": "次に、この灯りを実行できる修復へ変える",
        "intro": "このガイドが今の状態に触れたなら、まず守護者へ戻り、補給ルートと 7 日の練習を一つ選びます。庭全体を一度に直さず、一つの道を見えやすくします。",
        "guardian_label": "守護者へ戻る",
        "guardian_text": "この守護者が守るニーズ、すれ違いの傷、修復任務を理解します。",
        "route_label": "補給ルートを受け取る",
        "route_text": "この守護者に合う無料タスク、Luna の使い方、深める本を一つ選びます。",
        "plan_label": "7 日修復に入れる",
        "plan_text": "今日見つけた言葉を、今週練習できる小さな約束へ置きます。",
        "luna_label": "夜の雑音を下げる",
        "luna_text": "読んだ後に感情が大きい時は、Luna でこの理解を一文に整えます。",
        "guardian_cta": "守護者ページへ",
        "route_cta": "補給ルートを見る",
        "plan_cta": "修復計画を始める",
        "luna_cta": "Luna を開く",
    },
    "ko": {
        "eyebrow": "이 가이드를 수호자 루트로 이어가기",
        "title": "다음으로, 이 등불을 실행 가능한 회복으로 바꾸기",
        "intro": "이 가이드가 지금의 상태를 짚었다면 먼저 수호자에게 돌아가고, 보급 루트 하나와 7일 연습 하나를 가져가세요. 정원 전체를 한 번에 고치기보다 한 길을 선명하게 만드세요.",
        "guardian_label": "수호자 다시 보기",
        "guardian_text": "이 수호자가 지키는 욕구, 어긋남의 상처, 회복 과제를 이해합니다.",
        "route_label": "보급 루트 받기",
        "route_text": "이 수호자에게 맞는 무료 과제, Luna 사용 장면, 더 깊은 책 한 권을 고릅니다.",
        "plan_label": "7일 회복에 넣기",
        "plan_text": "오늘 찾은 문장을 이번 주 실천할 수 있는 작은 약속에 넣습니다.",
        "luna_label": "밤의 소음 낮추기",
        "luna_text": "읽은 뒤 감정이 크다면 Luna로 이 이해를 적을 수 있는 한 문장으로 정리하세요.",
        "guardian_cta": "수호자 페이지로",
        "route_cta": "보급 루트 보기",
        "plan_cta": "회복 계획 시작",
        "luna_cta": "Luna 열기",
    },
    "es": {
        "eyebrow": "Lleva esta guía a una ruta de guardiana",
        "title": "Después, convierte esta luz en una reparación práctica",
        "intro": "Si esta guía nombra tu estado actual, vuelve primero a la guardiana y toma una ruta de recursos y una práctica de 7 días. No repares todo el jardín a la vez; aclara un camino.",
        "guardian_label": "Volver a la guardiana",
        "guardian_text": "Comprende la necesidad, herida de desajuste y misión de reparación que protege esta guardiana.",
        "route_label": "Tomar la ruta de recursos",
        "route_text": "Elige una tarea gratis, un uso de Luna y un libro para profundizar con esta guardiana.",
        "plan_label": "Completar la reparación de 7 días",
        "plan_text": "Coloca la frase de hoy en un pequeño acuerdo que puedas practicar esta semana.",
        "luna_label": "Bajar el ruido nocturno",
        "luna_text": "Si la emoción queda alta después de leer, usa Luna para convertir esta idea en una línea escrita.",
        "guardian_cta": "Entrar a la guardiana",
        "route_cta": "Ver ruta de recursos",
        "plan_cta": "Iniciar plan de reparación",
        "luna_cta": "Abrir Luna",
    },
}


TRUST_ACTION_ROUTES = {
    "zh": {
        "about": {
            "eyebrow": "從信任回到行動",
            "title": "確認邊界後，選一條安全的心語路線",
            "intro": "如果你已經理解 LoveTypes 的內容來源、商業揭露與安全邊界，可以從這裡回到實際練習，不需要把自己套進任何固定類型。",
            "items": [
                ("01", "先做 15 道心語儀式", "用情境題辨認此刻最容易接收愛的入口。", "開始測驗", ""),
                ("02", "認識五位守護者", "看見每種愛之語背後的錯頻傷口與修復任務。", "查看守護者", "characters"),
                ("03", "閱讀深度指南", "把被愛需求翻成可以開口、可以承擔的句子。", "閱讀指南", "guides"),
                ("04", "回報或聯絡", "若內容需要修正、合作或隱私協助，直接寫信給我們。", "聯絡我們", "contact"),
            ],
        },
        "theory": {
            "eyebrow": "從理論進入練習",
            "title": "理解五種愛之語後，把它放進一週修復",
            "intro": "理論只是一張地圖。真正讓關係變清楚的，是你能否把一個錯頻片刻翻成守護者、請求與下一步補給。",
            "items": [
                ("01", "開始命運儀式", "先用 15 題確認目前最亮的愛之語訊號。", "開始測驗", ""),
                ("02", "對照五位守護者", "把抽象理論放回艾莉絲、諾雅、薇薇安、克萊兒與朵拉。", "查看守護者", "characters"),
                ("03", "寫進 7 日修復", "把今天理解的一句話放進可執行的一週練習。", "使用修復計畫", "repair-plan"),
                ("04", "選一條補給路線", "需要書卷、Luna 或免費任務時，再依守護者拿補給。", "前往旅人補給", "resources"),
            ],
        },
    },
    "en": {
        "about": {
            "eyebrow": "From trust back to action",
            "title": "After checking the boundaries, choose a safe Heart Garden route",
            "intro": "Once you understand how LoveTypes handles content, disclosure, and safety, return to practice without treating any result as a fixed identity.",
            "items": [
                ("01", "Take the 15-prompt ritual", "Use scenario prompts to name the doorway where love is easiest to receive right now.", "Start quiz", ""),
                ("02", "Meet the five guardians", "See the wound and repair mission behind each love language.", "View guardians", "characters"),
                ("03", "Read practical guides", "Translate emotional needs into words that can be spoken and carried.", "Read guides", "guides"),
                ("04", "Report or contact", "For corrections, partnership, privacy, or broken pages, contact us directly.", "Contact us", "contact"),
            ],
        },
        "theory": {
            "eyebrow": "From theory into practice",
            "title": "After learning the five love languages, place them inside a repair week",
            "intro": "Theory is only a map. The relationship becomes clearer when one misfrequency moment becomes a guardian, a request, and a next supply.",
            "items": [
                ("01", "Start the destiny ritual", "Use 15 prompts to confirm the love-language signal that is brightest now.", "Start quiz", ""),
                ("02", "Compare the guardians", "Place abstract theory back into Iris, Noah, Vivian, Claire, and Dora.", "View guardians", "characters"),
                ("03", "Use the 7-day repair", "Turn one sentence from today into a practical week-long exercise.", "Use repair plan", "repair-plan"),
                ("04", "Choose a supply route", "When you need a book, Luna, or a free task, take one guardian supply.", "Open resources", "resources"),
            ],
        },
    },
    "ja": {
        "about": {
            "eyebrow": "信頼から行動へ戻る",
            "title": "境界線を確認したら、安全な心語ルートを一つ選ぶ",
            "intro": "LoveTypes の内容、開示、安全の考え方を確認したら、結果を固定された身分にせず、実際の練習へ戻れます。",
            "items": [
                ("01", "15 問の心語リチュアル", "状況型の質問で、今いちばん受け取りやすい愛の入口を見つけます。", "診断を始める", ""),
                ("02", "五人の守護者を見る", "それぞれの愛の言語にある傷と修復任務を理解します。", "守護者を見る", "characters"),
                ("03", "実用ガイドを読む", "感情的なニーズを、言えて持てる言葉へ翻訳します。", "ガイドを読む", "guides"),
                ("04", "連絡・報告する", "修正、提携、プライバシー、ページ不具合は直接ご連絡ください。", "連絡する", "contact"),
            ],
        },
        "theory": {
            "eyebrow": "理論から練習へ",
            "title": "五つの愛の言語を理解したら、一週間の修復へ入れる",
            "intro": "理論は地図にすぎません。すれ違いの一場面を守護者、お願い、次の補給へ変える時、関係は少し見えやすくなります。",
            "items": [
                ("01", "運命のリチュアルを始める", "15 問で今いちばん明るい愛の言語の信号を確認します。", "診断を始める", ""),
                ("02", "守護者と照らし合わせる", "抽象的な理論をアイリス、ノア、ヴィヴィアン、クレア、ドーラへ戻します。", "守護者を見る", "characters"),
                ("03", "7日間修復へ書く", "今日理解した一文を、実行できる一週間の練習へ入れます。", "修復プランを使う", "repair-plan"),
                ("04", "補給ルートを選ぶ", "本、Luna、無料タスクが必要な時、守護者に合う補給を一つ選びます。", "リソースへ", "resources"),
            ],
        },
    },
    "ko": {
        "about": {
            "eyebrow": "신뢰에서 다시 행동으로",
            "title": "경계를 확인했다면 안전한 마음 언어 루트 하나를 고르기",
            "intro": "LoveTypes의 콘텐츠, 고지, 안전 경계를 이해했다면 어떤 결과도 고정된 정체성으로 삼지 않고 실제 연습으로 돌아갈 수 있습니다.",
            "items": [
                ("01", "15문항 마음 언어 의식", "상황형 질문으로 지금 가장 받기 쉬운 사랑의 입구를 확인합니다.", "테스트 시작", ""),
                ("02", "다섯 수호자 만나기", "각 사랑의 언어 뒤의 상처와 회복 과제를 봅니다.", "수호자 보기", "characters"),
                ("03", "실용 가이드 읽기", "정서적 욕구를 말할 수 있고 함께 감당할 수 있는 문장으로 번역합니다.", "가이드 읽기", "guides"),
                ("04", "문의 또는 신고", "수정, 협업, 개인정보, 깨진 페이지는 직접 연락해 주세요.", "연락하기", "contact"),
            ],
        },
        "theory": {
            "eyebrow": "이론에서 연습으로",
            "title": "다섯 가지 사랑의 언어를 이해했다면 일주일 회복에 넣기",
            "intro": "이론은 지도일 뿐입니다. 한 번의 어긋남을 수호자, 요청, 다음 보급으로 바꿀 때 관계가 더 선명해집니다.",
            "items": [
                ("01", "운명 의식 시작", "15문항으로 지금 가장 밝은 사랑의 언어 신호를 확인합니다.", "테스트 시작", ""),
                ("02", "수호자와 대조하기", "추상적인 이론을 아이리스, 노아, 비비안, 클레어, 도라로 되돌립니다.", "수호자 보기", "characters"),
                ("03", "7일 회복에 쓰기", "오늘 이해한 한 문장을 실행 가능한 일주일 연습으로 옮깁니다.", "회복 계획 쓰기", "repair-plan"),
                ("04", "보급 루트 선택", "책, Luna, 무료 과제가 필요할 때 수호자에 맞는 보급 하나를 선택합니다.", "자료 열기", "resources"),
            ],
        },
    },
    "es": {
        "about": {
            "eyebrow": "De la confianza a la acción",
            "title": "Después de revisar los límites, elige una ruta segura del Jardín",
            "intro": "Cuando entiendes cómo LoveTypes maneja contenido, divulgación y seguridad, puedes volver a practicar sin convertir ningún resultado en identidad fija.",
            "items": [
                ("01", "Haz el ritual de 15 preguntas", "Usa escenas concretas para nombrar la puerta donde el amor se recibe mejor ahora.", "Empezar test", ""),
                ("02", "Conoce las cinco guardianas", "Mira la herida y la misión de reparación detrás de cada lenguaje.", "Ver guardianas", "characters"),
                ("03", "Lee guías prácticas", "Traduce necesidades emocionales en palabras que puedan decirse y sostenerse.", "Leer guías", "guides"),
                ("04", "Reporta o contacta", "Para correcciones, colaboración, privacidad o páginas rotas, escríbenos.", "Contactar", "contact"),
            ],
        },
        "theory": {
            "eyebrow": "De la teoría a la práctica",
            "title": "Después de aprender los cinco lenguajes, llévalos a una semana de reparación",
            "intro": "La teoría solo es un mapa. La relación se aclara cuando un desajuste se convierte en guardiana, petición y próximo recurso.",
            "items": [
                ("01", "Inicia el ritual de destino", "Usa 15 preguntas para confirmar la señal de amor más clara ahora.", "Empezar test", ""),
                ("02", "Compara las guardianas", "Devuelve la teoría abstracta a Iris, Noah, Vivian, Claire y Dora.", "Ver guardianas", "characters"),
                ("03", "Usa la reparación de 7 días", "Convierte una frase de hoy en una práctica semanal concreta.", "Usar plan", "repair-plan"),
                ("04", "Elige una ruta de recursos", "Cuando necesites libro, Luna o tarea gratis, toma un recurso de guardiana.", "Abrir recursos", "resources"),
            ],
        },
    },
}


ABOUT_GARDEN_PASS = {
    "zh": {
        "eyebrow": "HEART GARDEN PASS",
        "title": "進入心語庭園前，先拿到三枚通行印",
        "intro": "關於頁不只是網站說明，而是讓旅人知道這座守護者宇宙怎麼被維護、怎麼使用、哪些地方不能被拿來取代真實求助。",
        "cards": [
            ("01", "內容來源印", "每一盞燈都要回到真實關係情境、五種愛之語與可練習的小行動。"),
            ("02", "旅程路線印", "測驗結果會接到守護者、指南、7 日修復、旅人補給與 Luna，而不是停在一張標籤。"),
            ("03", "安全邊界印", "LoveTypes 不承諾療效、不取代諮商；遇到暴力、控制、創傷或急迫危險時，先找可信任的人與專業支援。"),
        ],
    },
    "en": {
        "eyebrow": "HEART GARDEN PASS",
        "title": "Before entering the Heart Garden, collect three passage marks",
        "intro": "The about page is not only site information. It tells travelers how this guardian universe is maintained, how to use it, and where it must not replace real-world support.",
        "cards": [
            ("01", "Source mark", "Every lamp should return to a real relationship situation, the five love languages, and one small practice."),
            ("02", "Journey mark", "A quiz result connects to a guardian, guides, the 7-day repair plan, supplies, and Luna instead of stopping at a label."),
            ("03", "Safety mark", "LoveTypes does not promise outcomes or replace counseling. For violence, control, trauma, or urgent danger, seek trusted people and professional support first."),
        ],
    },
    "ja": {
        "eyebrow": "HEART GARDEN PASS",
        "title": "心語の庭に入る前に、三つの通行印を確認する",
        "intro": "このページはサイト説明だけではありません。守護者の宇宙がどう維持され、どう使われ、どこで現実の支援を優先すべきかを示します。",
        "cards": [
            ("01", "内容の印", "すべての灯りは実際の関係場面、五つの愛の言語、小さな練習へ戻ります。"),
            ("02", "旅路の印", "診断結果は守護者、ガイド、7日間修復、補給、Luna へつながり、ラベルで止まりません。"),
            ("03", "安全の印", "LoveTypes は効果を約束せず、相談支援の代わりではありません。暴力、支配、トラウマ、緊急の危険では信頼できる人と専門家を優先してください。"),
        ],
    },
    "ko": {
        "eyebrow": "HEART GARDEN PASS",
        "title": "마음의 정원에 들어가기 전 세 가지 통행 표식을 확인하기",
        "intro": "소개 페이지는 단순한 사이트 설명이 아닙니다. 이 수호자 세계가 어떻게 관리되고, 어떻게 쓰이며, 어디에서 실제 지원을 우선해야 하는지 보여 줍니다.",
        "cards": [
            ("01", "내용 표식", "모든 등불은 실제 관계 상황, 다섯 가지 사랑의 언어, 작은 연습으로 돌아가야 합니다."),
            ("02", "여정 표식", "테스트 결과는 수호자, 가이드, 7일 회복, 보급, Luna로 이어지며 라벨에서 멈추지 않습니다."),
            ("03", "안전 표식", "LoveTypes는 결과를 약속하거나 상담을 대신하지 않습니다. 폭력, 통제, 트라우마, 긴급 위험에서는 신뢰할 사람과 전문가 지원을 먼저 찾으세요."),
        ],
    },
    "es": {
        "eyebrow": "HEART GARDEN PASS",
        "title": "Antes de entrar al Jardín, reúne tres marcas de paso",
        "intro": "La página acerca de no es solo información del sitio. Explica cómo se mantiene este universo de guardianas, cómo usarlo y dónde no debe reemplazar apoyo real.",
        "cards": [
            ("01", "Marca de origen", "Cada luz debe volver a una situación real de relación, los cinco lenguajes del amor y una práctica pequeña."),
            ("02", "Marca de viaje", "El resultado del test conecta con guardiana, guías, plan de 7 días, recursos y Luna; no termina en una etiqueta."),
            ("03", "Marca de seguridad", "LoveTypes no promete resultados ni reemplaza terapia. Ante violencia, control, trauma o peligro urgente, busca primero personas de confianza y apoyo profesional."),
        ],
    },
}


SIMPLE_PAGE_DISPLAY_TITLES = {
    "zh": {
        "about": "關於心語庭園",
        "theory": "愛之語理論",
    },
    "en": {
        "about": "About the Heart Garden",
        "theory": "Love-Language Theory",
    },
    "ja": {
        "about": "心語の庭について",
        "theory": "愛の言語の理論",
    },
    "ko": {
        "about": "마음의 정원 소개",
        "theory": "사랑의 언어 이론",
    },
    "es": {
        "about": "Acerca del Jardín del Corazón",
        "theory": "Teoría de los lenguajes del amor",
    },
}


THEORY_DOMAIN_COMPASS = {
    "zh": {
        "eyebrow": "FIVE-DOMAIN THEORY COMPASS",
        "title": "把五種愛之語放進五個守護者分域",
        "intro": "理論如果停在名詞，很快會變成考題。把它放回分域，就能看見每一種愛之語需要被怎麼接收、怎麼修復、怎麼選補給。",
        "cta": "進入分域",
    },
    "en": {
        "eyebrow": "FIVE-DOMAIN THEORY COMPASS",
        "title": "Place the five love languages inside five guardian domains",
        "intro": "When theory stays as vocabulary, it becomes a quiz. Put it back into the domains so each love language shows how it is received, repaired, and supplied.",
        "cta": "Enter domain",
    },
    "ja": {
        "eyebrow": "FIVE-DOMAIN THEORY COMPASS",
        "title": "五つの愛の言語を五つの守護者分域へ置く",
        "intro": "理論が言葉だけで止まると、テストの答えになってしまいます。分域へ戻すと、受け取り方、修復、補給の選び方が見えます。",
        "cta": "分域へ",
    },
    "ko": {
        "eyebrow": "FIVE-DOMAIN THEORY COMPASS",
        "title": "다섯 가지 사랑의 언어를 다섯 수호자 영역에 놓기",
        "intro": "이론이 용어로만 남으면 시험 문제가 됩니다. 영역으로 돌려놓으면 각 언어를 어떻게 받고, 회복하고, 보급할지 보입니다.",
        "cta": "영역으로",
    },
    "es": {
        "eyebrow": "FIVE-DOMAIN THEORY COMPASS",
        "title": "Coloca los cinco lenguajes dentro de cinco dominios guardianes",
        "intro": "Cuando la teoría queda como vocabulario, se vuelve examen. Al devolverla a los dominios, cada lenguaje muestra cómo recibirlo, repararlo y elegir recursos.",
        "cta": "Entrar al dominio",
    },
}


PRACTICAL_COPY = {
    "zh": {
        "why": "在心語庭園裡，關係裡的痛感常不是沒有愛，而是愛在抵達前就錯頻了。你用自己的方式努力發光，對方卻沒有接收到那盞燈。LoveTypes 把五種愛之語化為五位守護者，目的不是替人貼標籤，而是幫你看見：此刻最需要被翻譯的愛，是話語、時間、心意、行動，還是安全的靠近。",
        "notice": "開始之前，先把「我希望對方懂我」放在心語庭園的入口，拆成三句話：我現在最缺的是什麼？我最害怕被誤解的地方是什麼？如果對方只能點亮一盞小燈，哪一個行動最能讓我安心？",
        "scripts": ["我不是要你猜我的心，我想把這次錯頻翻成更清楚的需要。", "如果你願意，我希望我們先從一個小約定開始，不一次修完整座庭園。", "我需要的不是完美回應，而是知道你願意把這盞燈放在心上。"],
        "practice": "今天只選一個具體情境，不要一次翻出所有舊帳。寫下觸發事件、身體或情緒的反應、背後的愛之語需求，以及一個對方能在二十四小時內做到的小請求。這不是考驗對方，而是在替關係留下一條可走的路。",
        "mistakes": "不要把守護者結果當作命令，也不要用「我就是這一型」停止溝通。守護者只是入口，不是身分證。真正重要的是你們能不能把需求翻成彼此都願意承擔的小行動，讓錯頻有機會被修復。",
        "reflection": ["我最容易用哪一種方式付出，卻忽略對方真正接收的語言？", "這次受傷比較像哪一種錯頻：沒被看見、沒被陪伴、沒被記得、沒被分擔，還是身體不安全？", "如果我把需求說得更具體，能不能少一點委屈、試探與猜測？"],
    },
    "en": {
        "why": "In the Heart Garden, relationship pain is often not the absence of love. Love becomes misfrequency before it arrives: one person shines in their own way, while the other never receives that lamp. LoveTypes turns the five love languages into five guardians so you can see what needs translation now: words, time, keepsakes, action, or safe closeness.",
        "notice": "Before starting, place the wish to be understood at the gate of the Heart Garden and split it into three sentences: what do I need most right now, where do I fear being misunderstood, and what one small lamp of action would help me feel safer?",
        "scripts": ["I do not want you to guess my heart; I want to translate this misfrequency into a clearer need.", "If you are willing, I would like us to begin with one small agreement, not repair the whole garden at once.", "I do not need a perfect response. I need to know you are willing to keep this lamp in mind."],
        "practice": "Choose one concrete situation today. Write the trigger, your body or emotional response, the love-language need underneath it, and one request the other person could realistically do within twenty-four hours. This is not a test; it is a path the relationship can walk.",
        "mistakes": "Do not use a guardian result as a command, and do not say 'this is just my type' to stop the conversation. A guardian is a doorway, not an identity card. The real work is translating needs into small actions both people can carry.",
        "reflection": ["Which love language do I naturally give while missing what the other person receives?", "Which misfrequency hurt most this time: not being seen, not being accompanied, not being remembered, not being helped, or not feeling safe in closeness?", "Would more specific requests reduce resentment, testing, and guessing?"],
    },
    "ja": {
        "why": "心語の庭では、関係の痛みは愛がないからではなく、届く前に愛がすれ違ってしまうことから起こります。自分の方法で光っているのに、相手にはその灯りが届かない。LoveTypes は五つの愛の言語を五人の守護者に変え、今翻訳が必要なのは言葉、時間、心意、行動、安全な近さのどれかを見つけます。",
        "notice": "始める前に、「わかってほしい」という願いを心語の庭の入口に置き、三つに分けます。今いちばん足りないものは何か。どこを誤解されるのが怖いか。相手が一つだけ小さな灯りをともすなら、何が安心につながるか。",
        "scripts": ["心を当ててほしいのではなく、このすれ違いをもっと明確なニーズへ翻訳したい。", "よければ、庭全体を一度に直すのではなく、小さな約束を一つだけ始めたい。", "完璧な返事ではなく、この灯りを心に置いてくれていると知りたい。"],
        "practice": "今日は一つの具体的な場面だけを選びます。きっかけ、身体や感情の反応、その下にある愛の言語のニーズ、そして二十四時間以内にできる小さなお願いを書いてください。これは相手を試すことではなく、関係が歩ける道を残すことです。",
        "mistakes": "守護者の結果を命令として使わないでください。「私はこのタイプだから」で会話を止めることも避けます。守護者は入口であり、身分証ではありません。本当に大切なのはニーズを二人で持てる小さな行動へ翻訳することです。",
        "reflection": ["私はどの愛の言語で与えがちで、相手が受け取る言語を見逃しているか。", "今回いちばん痛かったすれ違いは、見てもらえないこと、伴走されないこと、覚えてもらえないこと、分担されないこと、身体が安全でないことのどれか。", "お願いを具体的にすれば、我慢、試し行動、推測は減るか。"],
    },
    "ko": {
        "why": "마음의 정원에서 관계의 아픔은 사랑이 없어서가 아니라 사랑이 도착하기 전에 어긋나기 때문에 생깁니다. 한 사람은 자기 방식으로 빛나지만, 다른 사람은 그 등불을 받지 못합니다. LoveTypes는 다섯 가지 사랑의 언어를 다섯 수호자로 바꾸어 지금 번역이 필요한 사랑이 말, 시간, 마음, 행동, 안전한 가까움 중 무엇인지 보게 합니다.",
        "notice": "시작하기 전에 '나를 이해해 줬으면 좋겠다'는 바람을 마음의 정원 입구에 놓고 세 문장으로 나누세요. 지금 가장 필요한 것은 무엇인가, 어떤 부분이 오해될까 두려운가, 상대가 작은 등불 하나를 켠다면 어떤 행동이 가장 안심되는가.",
        "scripts": ["내 마음을 맞혀 달라는 것이 아니라 이번 어긋남을 더 분명한 욕구로 번역하고 싶어.", "괜찮다면 정원 전체를 한 번에 고치기보다 작은 약속 하나부터 시작하고 싶어.", "완벽한 답보다 이 등불을 마음에 두고 있다는 것을 알고 싶어."],
        "practice": "오늘은 구체적인 상황 하나만 고르세요. 계기, 몸이나 감정의 반응, 그 아래의 사랑의 언어 욕구, 그리고 24시간 안에 현실적으로 할 수 있는 작은 요청을 적습니다. 이것은 상대를 시험하는 것이 아니라 관계가 걸어갈 길을 남기는 일입니다.",
        "mistakes": "수호자 결과를 명령처럼 쓰지 마세요. '나는 원래 이 타입이야'라고 말하며 대화를 멈추는 것도 피해야 합니다. 수호자는 입구일 뿐, 신분증이 아닙니다. 중요한 것은 욕구를 둘이 함께 짊어질 수 있는 작은 행동으로 번역하는 것입니다.",
        "reflection": ["나는 어떤 사랑의 언어로 주로 표현하면서 상대가 받는 언어를 놓치고 있을까?", "이번에 가장 아팠던 어긋남은 보이지 않음, 함께 있지 않음, 기억되지 않음, 분담되지 않음, 몸이 안전하지 않음 중 무엇일까?", "요청을 더 구체적으로 말하면 서운함, 시험, 추측이 줄어들까?"],
    },
    "es": {
        "why": "En el Jardín del Corazón, el dolor relacional muchas veces no nace de la falta de amor, sino de un amor que se desajusta antes de llegar. Una persona brilla a su manera, mientras la otra no recibe esa luz. LoveTypes convierte los cinco lenguajes del amor en cinco guardianas para ver qué necesita traducción ahora: palabras, tiempo, memoria, acción o cercanía segura.",
        "notice": "Antes de empezar, deja el deseo de ser entendida en la entrada del Jardín del Corazón y divídelo en tres frases: qué necesito ahora, dónde temo ser malinterpretada y qué pequeña luz de acción me ayudaría a sentir más seguridad.",
        "scripts": ["No quiero que adivines mi corazón; quiero traducir este desajuste en una necesidad más clara.", "Si estás dispuesto/a, me gustaría empezar con un acuerdo pequeño, no reparar todo el jardín de una vez.", "No necesito una respuesta perfecta. Necesito saber que estás dispuesto/a a cuidar esta luz."],
        "practice": "Elige hoy una situación concreta. Escribe el detonante, la respuesta del cuerpo o de la emoción, la necesidad de lenguaje del amor que hay debajo y una petición realista para las próximas veinticuatro horas. No es una prueba; es un camino que la relación puede caminar.",
        "mistakes": "No uses el resultado de una guardiana como una orden ni como una excusa para cerrar la conversación. Una guardiana es una puerta, no una identidad fija. El trabajo real es traducir necesidades en acciones pequeñas que ambas personas puedan sostener.",
        "reflection": ["¿Qué lenguaje suelo ofrecer mientras pierdo de vista el que la otra persona recibe?", "¿Qué desajuste dolió más esta vez: no ser vista, no ser acompañada, no ser recordada, no ser apoyada o no sentir seguridad corporal?", "¿Si hago peticiones más concretas, disminuirán el resentimiento, las pruebas y las suposiciones?"],
    },
}


PAGE_SECTIONS = {
    "zh": {
        "how": "在真實關係裡會怎麼出現",
        "need": "背後真正想被理解的需要",
        "use": "怎麼把結果用得更好",
        "editorial": "我們如何維護內容",
        "disclosure": "商業與資料揭露",
        "contact_help": "你可以如何聯絡我們",
    },
    "en": {
        "how": "How this appears in real relationships",
        "need": "The need underneath",
        "use": "How to use the result well",
        "editorial": "How we maintain the content",
        "disclosure": "Commercial and data disclosure",
        "contact_help": "How to contact us",
    },
    "ja": {
        "how": "実際の関係でどう現れるか",
        "need": "その下にある本当のニーズ",
        "use": "結果をよりよく使う方法",
        "editorial": "内容の維持方法",
        "disclosure": "商業・データの開示",
        "contact_help": "連絡方法",
    },
    "ko": {
        "how": "실제 관계에서 어떻게 나타나는가",
        "need": "그 아래의 진짜 욕구",
        "use": "결과를 더 잘 사용하는 방법",
        "editorial": "콘텐츠를 관리하는 방식",
        "disclosure": "상업 및 데이터 고지",
        "contact_help": "연락 방법",
    },
    "es": {
        "how": "Cómo aparece en relaciones reales",
        "need": "La necesidad que hay debajo",
        "use": "Cómo usar bien el resultado",
        "editorial": "Cómo mantenemos el contenido",
        "disclosure": "Divulgación comercial y de datos",
        "contact_help": "Cómo contactarnos",
    },
}


CHARACTER_INDEX_COPY = {
    "zh": {
        "title": "五位情感守護者總覽 | LoveTypes",
        "desc": "認識艾莉絲、諾雅、薇薇安、克萊兒與朵拉五位情感守護者，對應肯定言詞、優質時光、接受禮物、服務行動與身體接觸，找到你的測驗結果、錯頻傷口、修復任務與下一條補給路線。",
        "h1": "五位情感守護者總覽",
        "intro": "每位守護者都是一種被愛入口，也是一條修復路線。先看見你最容易接收愛的方式，再選擇對應指南、練習與旅人補給。",
        "map_title": "從守護者進入你的下一步",
        "map_intro": "如果你已完成測驗，直接打開結果對應的守護者；如果還沒有，先從五位角色的語氣與傷口辨認哪一盞燈最像你。",
    },
    "en": {
        "title": "Five Emotion Guardians Overview | LoveTypes",
        "desc": "Meet Iris, Noah, Vivian, Claire, and Dora, then choose the guide, wound, repair mission, and supply route that fit your LoveTypes result.",
        "h1": "Five Emotion Guardians Overview",
        "intro": "Each guardian is a doorway for receiving love and a route for repair. Start with the love language that feels most tender, then continue into a guide, practice, or supply path.",
        "map_title": "Use the guardians to choose your next step",
        "map_intro": "If you already took the quiz, open the matching guardian. If not, read the five voices and wounds first, then begin with the lamp that feels closest.",
    },
    "ja": {
        "title": "五人の感情の守護者一覧 | LoveTypes",
        "desc": "アイリス、ノア、ヴィヴィアン、クレア、ドラの五人の感情の守護者を紹介します。肯定の言葉、上質な時間、贈り物、奉仕の行動、身体的なふれあいから、診断結果、すれ違いの傷、次の補給ルートを選べます。",
        "h1": "五人の感情の守護者一覧",
        "intro": "それぞれの守護者は、愛を受け取る入口であり、修復へ向かう道です。いちばん傷つきやすい愛の言語から、ガイド、練習、補給ルートへ進めます。",
        "map_title": "守護者から次の一歩を選ぶ",
        "map_intro": "すでに診断を終えたなら、結果に合う守護者を開いてください。まだなら、五人の声と傷を読み、近く感じる灯りから始めます。",
    },
    "ko": {
        "title": "다섯 감정 수호자 한눈에 보기 | LoveTypes",
        "desc": "아이리스, 노아, 비비안, 클레어, 도라 다섯 감정 수호자를 소개합니다. 인정의 말, 함께하는 시간, 선물 받기, 봉사의 행동, 스킨십에 맞춰 테스트 결과, 어긋남의 상처, 다음 보급 루트를 찾을 수 있습니다.",
        "h1": "다섯 감정 수호자 한눈에 보기",
        "intro": "각 수호자는 사랑을 받는 입구이자 회복으로 이어지는 길입니다. 가장 예민하게 느껴지는 사랑의 언어에서 가이드, 연습, 보급 루트로 이어가세요.",
        "map_title": "수호자로 다음 단계를 고르기",
        "map_intro": "이미 테스트를 했다면 결과에 맞는 수호자를 여세요. 아직이라면 다섯 목소리와 상처를 읽고 가장 가까운 등불부터 시작하세요.",
    },
    "es": {
        "title": "Resumen de las Cinco Guardianas Emocionales | LoveTypes",
        "desc": "Conoce a Iris, Noah, Vivian, Claire y Dora, y elige la guía, herida, misión de reparación y ruta de suministro que corresponde a tu resultado LoveTypes.",
        "h1": "Resumen de las Cinco Guardianas Emocionales",
        "intro": "Cada guardiana es una entrada para recibir amor y una ruta de reparación. Empieza por el lenguaje que se siente más sensible y continúa hacia una guía, práctica o suministro.",
        "map_title": "Usa las guardianas para elegir tu siguiente paso",
        "map_intro": "Si ya hiciste el test, abre la guardiana que corresponde. Si no, lee primero las cinco voces y heridas, y empieza por la luz que se sienta más cercana.",
    },
}


SITE_COPY = {
    "zh": {
        "guardian_use": "{name}是心語庭園裡的一扇門，不是固定身份。你可以用這位守護者說明什麼讓你感到安全、哪一種錯頻最容易刺痛你，以及哪一個小行動能讓關心更容易被你收到。",
        "editorial": "每一個 LoveTypes 頁面都先從一個真實關係問題出發，再把問題帶回五種愛之語、心語庭園的守護者隱喻，以及讀者不需要註冊帳號也能嘗試的小練習。我們維持反思式語氣，而不是診斷式語氣；當頁面太薄、太重複，或太偏向導流而不是讀者價值時，就會重新整理，讓每盞燈都能指向實際修復。",
        "disclosure": "LoveTypes 會在相關頁面揭露流量分析、聯盟連結或廣告資訊。旅人補給頁可能包含聯盟連結；若你透過這些連結購買，本站可能獲得少量佣金，但不影響你的購買價格。網站仍保留清楚的所有權、聯絡、sitemap 與政策資訊，方便讀者與搜尋/廣告審核系統確認這座心語庭園的來源與邊界。",
        "contact": "若要回報內容修正、隱私問題、合作疑慮或壞頁面，請使用 <a href=\"/contact/#site-repair-report\">聯絡頁修復回報入口</a>。有效回報最好附上頁面網址、裝置、瀏覽器，以及你認為需要重新點亮或修復的句子或段落。",
    },
    "en": {
        "guardian_use": "{name} is a doorway in the Heart Garden, not a fixed identity. Use this guardian to describe what helps you feel safe, which misfrequency hurts most, and what small action would make care easier to receive.",
        "editorial": "Every LoveTypes page begins with a real relationship question, then brings it back to the five love languages, the Heart Garden guardian metaphor, and a small exercise a reader can try without an account. We keep the tone reflective rather than diagnostic; when a page is thin, repetitive, or too promotional, we revise it so every lamp points toward practical repair.",
        "disclosure": "LoveTypes discloses measurement, affiliate links, or advertising information where those services are used. The Resources page may contain affiliate links; if you purchase through them, this site may earn a small commission at no extra cost to you. Clear ownership, contact, sitemap, and policy information remain available so readers and crawlers can understand the source and boundary of this Heart Garden.",
        "contact": "For content corrections, privacy questions, partnership concerns, or broken-page reports, use the <a href=\"/en/contact/#site-repair-report\">site repair report route</a>. Helpful reports include the page URL, device, browser, and the sentence or section you believe should be relit or repaired.",
    },
    "ja": {
        "guardian_use": "{name} は心語の庭にある一つの扉であり、固定された身分ではありません。この守護者を使って、何が安心につながるのか、どのすれ違いがいちばん痛むのか、どんな小さな行動なら思いやりを受け取りやすいのかを説明できます。",
        "editorial": "LoveTypes の各ページは、実際の関係で起こる問いから始まり、五つの愛の言語、心語の庭の守護者の比喩、そして登録なしで試せる小さな練習へつなげます。診断ではなく内省の語り口を保ち、内容が薄い、重複している、読者価値より誘導が強いと判断したページは、実際の修復に向かう灯りになるよう更新します。",
        "disclosure": "LoveTypes では、利用しているページでアクセス解析、アフィリエイトリンク、広告に関する情報を開示します。リソースページにはアフィリエイトリンクが含まれる場合があり、購入時に価格は変わりませんが、当サイトに少額の報酬が入ることがあります。所有者情報、連絡先、サイトマップ、ポリシー情報も確認できるようにしています。",
        "contact": "内容修正、プライバシー、提携、ページ不具合に関する連絡は <a href=\"/ja/contact/#site-repair-report\">サイト修復の報告入口</a> からお願いします。ページ URL、端末、ブラウザ、もう一度灯すべき、または修復すべき文や段落があると確認しやすくなります。",
    },
    "ko": {
        "guardian_use": "{name}는 마음의 정원에 있는 하나의 문이지 고정된 정체성이 아닙니다. 이 수호자를 통해 무엇이 나를 안전하게 하는지, 어떤 어긋남이 가장 아픈지, 어떤 작은 행동이 배려를 더 쉽게 받게 하는지 말할 수 있습니다.",
        "editorial": "LoveTypes의 각 페이지는 실제 관계 질문에서 시작해 다섯 가지 사랑의 언어, 마음의 정원 수호자 은유, 계정 없이도 시도할 수 있는 작은 연습으로 이어집니다. 진단이 아니라 성찰의 어조를 유지하며, 내용이 얇거나 반복적이거나 독자 가치보다 홍보가 강한 페이지는 실제 회복을 향한 등불이 되도록 다시 정리합니다.",
        "disclosure": "LoveTypes는 해당 서비스가 사용되는 페이지에서 분석, 제휴 링크, 광고 관련 정보를 고지합니다. 자료 페이지에는 제휴 링크가 포함될 수 있으며, 이를 통해 구매하면 구매 가격은 변하지 않지만 사이트가 소정의 수수료를 받을 수 있습니다. 소유권, 연락처, 사이트맵, 정책 정보도 계속 확인할 수 있습니다.",
        "contact": "콘텐츠 수정, 개인정보, 협업 문의, 깨진 페이지 신고는 <a href=\"/ko/contact/#site-repair-report\">사이트 수리 제보 입구</a>로 보내 주세요. 페이지 URL, 기기, 브라우저, 다시 켜거나 수리해야 할 문장이나 단락을 함께 보내면 확인이 빠릅니다.",
    },
    "es": {
        "guardian_use": "{name} es una puerta del Jardín del Corazón, no una identidad fija. Puedes usar esta guardiana para explicar qué te ayuda a sentir seguridad, qué desajuste te duele más y qué pequeña acción vuelve el cuidado más fácil de recibir.",
        "editorial": "Cada página de LoveTypes empieza con una pregunta real de relación y la lleva de vuelta a los cinco lenguajes del amor, la metáfora de las guardianas del Jardín del Corazón y un ejercicio pequeño que la persona puede probar sin crear una cuenta. Mantenemos un tono reflexivo, no diagnóstico, y revisamos las páginas demasiado delgadas, repetitivas o promocionales para que cada luz apunte a una reparación práctica.",
        "disclosure": "LoveTypes divulga información sobre medición, enlaces afiliados o publicidad en las páginas donde se usan esos servicios. La página de Recursos puede contener enlaces afiliados; si compras a través de ellos, el sitio puede recibir una pequeña comisión sin cambiar tu precio. La propiedad, contacto, sitemap y políticas siguen disponibles para explicar el origen y los límites de este Jardín del Corazón.",
        "contact": "Para correcciones de contenido, privacidad, colaboraciones o páginas rotas, usa la <a href=\"/es/contact/#site-repair-report\">ruta de reporte de reparación</a>. Un reporte útil incluye URL, dispositivo, navegador y la frase o sección que debería volver a encenderse o repararse.",
    },
}


ABOUT_SECTIONS = {
    "zh": [
        ("我們是誰", "LoveTypes 是一座以五種愛之語為地圖的心語庭園，將關係裡常見的被愛需求翻成五位情感守護者、15 道心語測驗與可實作的溝通指南。網站的目標不是替人貼標籤，而是讓你更容易說出：我怎麼接收愛、哪裡容易錯頻、下一步可以怎麼修復。"),
        ("內容怎麼產生與維護", "每一篇指南都從真實關係情境出發，再回到五種愛之語、情感安全、界線與日常練習。當頁面太薄、重複、過度導流，或沒有指向實際修復時，就會重新整理。LoveTypes 維持反思式語氣，不把測驗結果包裝成診斷。"),
        ("商業與資料揭露", SITE_COPY["zh"]["disclosure"]),
        ("聯絡與修正", SITE_COPY["zh"]["contact"]),
    ],
    "en": [
        ("Who we are", "LoveTypes is a Heart Garden mapped by the five love languages. It translates common needs for receiving love into five emotion guardians, a 15-prompt ritual, and practical relationship guides. The goal is not to label people, but to help you name how you receive love, where misfrequency hurts, and what repair can look like next."),
        ("How content is made and maintained", "Each guide starts from a real relationship situation, then returns to love-language theory, emotional safety, boundaries, and daily practice. Pages that become thin, repetitive, too promotional, or disconnected from practical repair are revised. LoveTypes keeps a reflective tone and does not present quiz results as diagnosis."),
        ("Commercial and data disclosure", SITE_COPY["en"]["disclosure"]),
        ("Contact and corrections", SITE_COPY["en"]["contact"]),
    ],
    "ja": [
        ("LoveTypes について", "LoveTypes は五つの愛の言語を地図にした心語の庭です。愛されるニーズを五人の感情の守護者、15 問のリチュアル、実践できる関係ガイドへ翻訳します。目的は人を分類することではなく、自分がどう愛を受け取るか、どこですれ違いやすいか、次にどう修復できるかを言葉にしやすくすることです。"),
        ("内容の作成と維持", "各ガイドは実際の関係場面から始まり、愛の言語、感情的安全、境界線、日常の練習へ戻ります。内容が薄い、重複している、宣伝に寄りすぎている、実際の修復につながらないページは更新します。LoveTypes は診断ではなく内省の語り口を保ちます。"),
        ("商業・データの開示", SITE_COPY["ja"]["disclosure"]),
        ("連絡と修正", SITE_COPY["ja"]["contact"]),
    ],
    "ko": [
        ("LoveTypes 소개", "LoveTypes는 다섯 가지 사랑의 언어를 지도로 삼은 마음의 정원입니다. 사랑받고 싶은 욕구를 다섯 감정 수호자, 15문항 의식, 실제 관계 가이드로 번역합니다. 목적은 사람을 분류하는 것이 아니라 내가 사랑을 받는 방식, 어긋남이 아픈 지점, 다음 회복 행동을 말하기 쉽게 만드는 것입니다."),
        ("콘텐츠 제작과 관리", "각 가이드는 실제 관계 상황에서 시작해 사랑의 언어, 정서적 안전, 경계, 일상 연습으로 돌아갑니다. 내용이 얇거나 반복적이거나 지나치게 홍보적이거나 실제 회복과 연결되지 않는 페이지는 다시 정리합니다. LoveTypes는 진단이 아니라 성찰의 어조를 유지합니다."),
        ("상업 및 데이터 고지", SITE_COPY["ko"]["disclosure"]),
        ("연락과 수정", SITE_COPY["ko"]["contact"]),
    ],
    "es": [
        ("Quiénes somos", "LoveTypes es un Jardín del Corazón trazado por los cinco lenguajes del amor. Traduce necesidades comunes de recibir amor en cinco guardianas emocionales, un ritual de 15 señales y guías prácticas de relación. El objetivo no es etiquetar personas, sino ayudarte a nombrar cómo recibes amor, dónde duele el desajuste y qué reparación puede venir después."),
        ("Cómo se crea y mantiene el contenido", "Cada guía parte de una situación real de relación y vuelve a la teoría de lenguajes del amor, seguridad emocional, límites y práctica diaria. Las páginas delgadas, repetitivas, demasiado promocionales o desconectadas de la reparación práctica se revisan. LoveTypes mantiene un tono reflexivo y no presenta los resultados como diagnóstico."),
        ("Divulgación comercial y de datos", SITE_COPY["es"]["disclosure"]),
        ("Contacto y correcciones", SITE_COPY["es"]["contact"]),
    ],
}


ABOUT_TRUST_CHARTER = {
    "zh": {
        "eyebrow": "HEART GARDEN TRUST CHARTER",
        "title": "心語庭園信任憑證",
        "intro": "進入守護者宇宙前，先看清楚這座庭園如何照顧內容、測驗、補給與聯絡修正。信任感本身也是關係修復的一部分。",
        "cards": [
            ("01", "內容會回到真實情境", "指南必須能對應實際關係困惑，並提供可練習的小行動；太薄、重複或只剩氣氛的頁面會被整理。", "guides", "閱讀指南"),
            ("02", "測驗不是診斷", "15 道心語只指出此刻最容易被點亮的愛之語入口，不用來貼標籤、要求伴侶照單全收，或取代專業協助。", "theory", "了解理論"),
            ("03", "補給不鼓勵過度購買", "旅人補給與延伸書卷會標示聯盟揭露，購買只應作為修復輔助；若你正在衝動消費，先使用免費任務。", "resources", "查看補給"),
            ("04", "可以要求修正", "若你發現錯字、過時資訊、破圖、無法開啟的連結，或需要合作與隱私聯絡，可以直接回報給庭園維護者。", "contact", "聯絡我們"),
        ],
    },
    "en": {
        "eyebrow": "HEART GARDEN TRUST CHARTER",
        "title": "Heart Garden trust charter",
        "intro": "Before entering the guardian universe, this charter shows how LoveTypes handles content, quiz boundaries, supplies, and corrections. Trust is part of repair.",
        "cards": [
            ("01", "Content returns to real situations", "Guides must connect to a relationship question and offer a small practice. Thin, repetitive, or atmosphere-only pages are revised.", "guides", "Read guides"),
            ("02", "The quiz is not diagnosis", "The 15 prompts point to the love-language doorway that feels lit right now. They are not labels, demands, or substitutes for professional care.", "theory", "Learn theory"),
            ("03", "Supplies should not push overbuying", "Traveler supplies and book scrolls keep affiliate disclosure visible. Purchases are repair aids; if you feel impulsive, start with a free task.", "resources", "View supplies"),
            ("04", "Corrections are welcome", "Report typos, outdated passages, broken images, broken links, privacy questions, or collaboration requests to the garden maintainer.", "contact", "Contact us"),
        ],
    },
    "ja": {
        "eyebrow": "HEART GARDEN TRUST CHARTER",
        "title": "心語の庭の信頼憲章",
        "intro": "守護者の宇宙に入る前に、この庭が内容、診断結果の境界、補給、修正依頼をどう扱うかを示します。信頼も修復の一部です。",
        "cards": [
            ("01", "内容は現実の場面へ戻る", "ガイドは関係の悩みとつながり、小さな練習を提示します。薄い、重複する、雰囲気だけのページは見直します。", "guides", "ガイドを読む"),
            ("02", "診断ではありません", "15 問は今もっとも灯りやすい愛の言語の入口を示します。固定ラベル、要求、専門的支援の代わりにはしません。", "theory", "理論を見る"),
            ("03", "補給は買いすぎを促しません", "旅人補給と書卷にはアフィリエイト開示を残します。購入は修復の補助であり、衝動的な時は無料タスクから始めてください。", "resources", "補給を見る"),
            ("04", "修正を受け付けます", "誤字、古い情報、画像やリンクの不具合、プライバシー、協業の相談は庭の管理者へ連絡できます。", "contact", "連絡する"),
        ],
    },
    "ko": {
        "eyebrow": "HEART GARDEN TRUST CHARTER",
        "title": "마음 정원 신뢰 헌장",
        "intro": "수호자 세계에 들어가기 전에 이 정원이 콘텐츠, 결과의 경계, 보급, 수정 요청을 어떻게 다루는지 보여 줍니다. 신뢰도 회복의 일부입니다.",
        "cards": [
            ("01", "콘텐츠는 실제 상황으로 돌아갑니다", "가이드는 관계 질문과 연결되고 작은 연습을 제공해야 합니다. 얇거나 반복적이거나 분위기만 있는 페이지는 정리합니다.", "guides", "가이드 읽기"),
            ("02", "퀴즈는 진단이 아닙니다", "15문항은 지금 가장 쉽게 켜지는 사랑의 언어 입구를 가리킵니다. 고정 라벨, 요구, 전문 지원의 대체물이 아닙니다.", "theory", "이론 보기"),
            ("03", "보급은 과소비를 권하지 않습니다", "여행자 보급과 책 추천에는 제휴 고지를 유지합니다. 구매는 회복 보조이며, 충동적이라면 무료 과제부터 시작하세요.", "resources", "보급 보기"),
            ("04", "수정을 요청할 수 있습니다", "오타, 오래된 정보, 깨진 이미지나 링크, 개인정보, 협업 문의는 정원 관리자에게 보낼 수 있습니다.", "contact", "연락하기"),
        ],
    },
    "es": {
        "eyebrow": "HEART GARDEN TRUST CHARTER",
        "title": "Carta de confianza del Jardín",
        "intro": "Antes de entrar al universo de guardianas, esta carta explica cómo LoveTypes cuida contenido, límites del resultado, recursos y correcciones. La confianza también repara.",
        "cards": [
            ("01", "El contenido vuelve a situaciones reales", "Las guías deben responder a una duda de relación y ofrecer una práctica pequeña. Las páginas delgadas, repetidas o solo atmosféricas se revisan.", "guides", "Leer guías"),
            ("02", "El test no es diagnóstico", "Las 15 señales muestran la puerta de lenguaje del amor más encendida ahora. No son etiquetas, exigencias ni sustituto de apoyo profesional.", "theory", "Ver teoría"),
            ("03", "Los recursos no empujan compras excesivas", "Los suministros y libros mantienen divulgación de afiliados. Comprar solo debe apoyar la reparación; si hay impulso, empieza gratis.", "resources", "Ver recursos"),
            ("04", "Puedes pedir correcciones", "Reporta erratas, información antigua, imágenes o enlaces rotos, privacidad o colaboraciones a quien mantiene el Jardín.", "contact", "Contactar"),
        ],
    },
}


THEORY_SECTIONS = {
    "zh": [
        ("五種愛之語是什麼", "五種愛之語把人們表達與接收愛的常見方式整理成五個入口：肯定言詞、優質時光、接受禮物、服務行動與身體接觸。它不是人格分類，而是一套關係溝通語彙，幫助你把模糊的委屈翻成可討論的需求。"),
        ("五位守護者怎麼對應", "艾莉絲守護被準確看見的肯定言詞；諾雅守護真正同在的優質時光；薇薇安守護被記得的心意；克萊兒守護把承諾放回日常的服務行動；朵拉守護經過同意、讓身體感到安全的靠近。"),
        ("測驗結果怎麼讀", "15 道心語測驗只反映此刻最容易被點亮或最容易受傷的入口。結果適合拿來開啟對話、選擇指南與設計小行動，不適合拿來要求對方照單全收，也不代表你永遠只有一種愛之語。"),
        ("錯頻修復的核心", "錯頻不是誰比較不愛，而是發出的愛和接收的方式沒有接上。修復時先說明感受，再指出背後的愛之語需求，最後提出一個對方能在短時間內做到的小請求。"),
    ],
    "en": [
        ("What the five love languages mean", "The five love languages organize common ways people express and receive love: words of affirmation, quality time, receiving gifts, acts of service, and physical touch. They are not a personality system; they are a communication vocabulary for turning vague hurt into discussable needs."),
        ("How the guardians map to the theory", "Iris guards words that help a person feel clearly seen. Noah guards time where two people are truly present. Vivian guards the proof of being remembered. Claire guards promises returned to daily action. Dora guards consensual closeness that helps the body feel safe."),
        ("How to read a quiz result", "The 15-prompt ritual reflects the doorway that feels easiest to light up or easiest to wound right now. Use the result to start a conversation, choose a guide, and design one small action. Do not use it as a demand, a permanent label, or proof that you only have one love language."),
        ("The core of misfrequency repair", "Misfrequency does not mean someone loves less. It means the love being sent and the way love is received are not connecting. Repair begins by naming the feeling, then the love-language need underneath it, then one small request the other person can try soon."),
    ],
    "ja": [
        ("五つの愛の言語とは", "五つの愛の言語は、愛を表す方法と受け取る方法を、肯定の言葉、上質な時間、贈り物、奉仕の行動、身体的なふれあいに整理する枠組みです。人格分類ではなく、曖昧な痛みを話し合えるニーズへ変えるための語彙です。"),
        ("守護者との対応", "アイリスは正確に見てもらう肯定の言葉を守ります。ノアは本当に一緒にいる時間を守ります。ヴィヴィアンは思い出してもらえた証を守ります。クレアは約束を日常の行動へ戻します。ドラは同意に基づく、安全な近さを守ります。"),
        ("診断結果の読み方", "15 問のリチュアルは、今もっとも灯りやすい、または傷つきやすい入口を示します。結果は会話、ガイド選び、小さな行動設計に使うもので、相手への要求や固定ラベルではありません。"),
        ("すれ違い修復の中心", "すれ違いは愛が少ないという意味ではなく、送る愛と受け取る方法が接続していない状態です。修復ではまず感情を名づけ、その下の愛の言語のニーズを伝え、近いうちに試せる小さなお願いを一つ出します。"),
    ],
    "ko": [
        ("다섯 가지 사랑의 언어란", "다섯 가지 사랑의 언어는 사랑을 표현하고 받는 방식을 인정의 말, 함께하는 시간, 선물 받기, 봉사의 행동, 스킨십으로 정리하는 틀입니다. 성격 분류가 아니라 흐릿한 서운함을 말할 수 있는 욕구로 바꾸는 대화 언어입니다."),
        ("수호자와의 대응", "아이리스는 정확히 보이는 인정의 말을 지킵니다. 노아는 진짜로 함께 있는 시간을 지킵니다. 비비안은 기억되었다는 증거를 지킵니다. 클레어는 약속을 일상의 행동으로 돌려놓습니다. 도라는 동의와 안전이 있는 가까움을 지킵니다."),
        ("결과를 읽는 법", "15문항 의식은 지금 가장 쉽게 켜지거나 가장 쉽게 다치는 입구를 보여 줍니다. 결과는 대화를 시작하고 가이드를 고르며 작은 행동을 설계하는 데 쓰는 것이지, 요구나 고정 라벨이 아닙니다."),
        ("어긋남 회복의 핵심", "어긋남은 누가 덜 사랑한다는 뜻이 아니라 보내는 사랑과 받는 방식이 연결되지 않은 상태입니다. 회복은 감정을 말하고, 그 아래의 사랑의 언어 욕구를 밝히고, 가까운 시간 안에 시도할 작은 요청 하나를 정하는 데서 시작합니다."),
    ],
    "es": [
        ("Qué significan los cinco lenguajes", "Los cinco lenguajes del amor ordenan formas comunes de expresar y recibir amor: palabras de afirmación, tiempo de calidad, recibir regalos, actos de servicio y contacto físico. No son una clasificación de personalidad, sino vocabulario para convertir una herida vaga en una necesidad conversable."),
        ("Cómo se conectan con las guardianas", "Iris protege las palabras que hacen sentir vista a una persona. Noah protege el tiempo de presencia real. Vivian protege la prueba de haber sido recordada. Claire devuelve las promesas a acciones diarias. Dora protege la cercanía consensuada que ayuda al cuerpo a sentirse seguro."),
        ("Cómo leer el resultado", "El ritual de 15 señales muestra la puerta que ahora se enciende o se hiere con más facilidad. Usa el resultado para iniciar conversación, elegir una guía y diseñar una acción pequeña. No lo uses como exigencia, etiqueta permanente ni prueba de que solo tienes un lenguaje."),
        ("El centro de reparar el desajuste", "El desajuste no significa que alguien ame menos. Significa que el amor enviado y la forma de recibirlo no se conectan. La reparación empieza nombrando el sentimiento, luego la necesidad de lenguaje del amor y finalmente una petición pequeña que la otra persona pueda probar pronto."),
    ],
}


def lang_url(lang: str, path: str = "") -> str:
    prefix = LANGS[lang]["prefix"]
    clean = path.strip("/")
    if prefix:
        return f"/{prefix}/{clean}/" if clean else f"/{prefix}/"
    return f"/{clean}/" if clean else "/"


def abs_url(lang: str, path: str = "") -> str:
    return DOMAIN + lang_url(lang, path).rstrip("/") + "/"


def about_trust_charter(lang: str) -> str:
    copy = ABOUT_TRUST_CHARTER[lang]
    cards = []
    for mark, title, text, slug, cta in copy["cards"]:
        cards.append(
            f"""
<article class="about-trust-card">
  <span>{escape(mark)}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(text)}</p>
  <a href="{lang_url(lang, slug)}">{escape(cta)}</a>
</article>
"""
        )
    return f"""
<section class="section about-trust-charter" data-about-trust>
  <div class="section-head">
    <div>
      <p class="eyebrow">{escape(copy["eyebrow"])}</p>
      <h2>{escape(copy["title"])}</h2>
      <p>{escape(copy["intro"])}</p>
    </div>
  </div>
  <div class="about-trust-grid">
    {''.join(cards)}
  </div>
</section>
"""


def policy_compass_section(lang: str, slug: str) -> str:
    copy = POLICY_COMPASS_COPY[lang]
    cards = []
    for idx, (heading, body_text) in enumerate(POLICY_SECTIONS[lang][slug], start=1):
        cards.append(
            f"""
<article class="policy-compass-card">
  <span>{idx:02d}</span>
  <h3>{escape(heading)}</h3>
  <p>{escape(copy["card_hint"].format(number=idx))}</p>
</article>
"""
        )
    return f"""
<section class="section policy-compass-section" data-policy-compass>
  <div class="section-head">
    <div>
      <p class="eyebrow">{escape(copy["eyebrow"])}</p>
      <h2>{escape(copy["title"])}</h2>
      <p>{escape(copy["intro"])}</p>
    </div>
  </div>
  <div class="policy-compass-grid">
    {''.join(cards)}
  </div>
</section>
"""


def policy_detail_section(lang: str, slug: str) -> str:
    copy = POLICY_COMPASS_COPY[lang]
    articles = []
    for idx, (heading, body_text) in enumerate(POLICY_SECTIONS[lang][slug], start=1):
        articles.append(
            f"""
<article class="policy-detail-card">
  <span>{idx:02d}</span>
  <div>
    <h3>{escape(heading)}</h3>
    <p>{escape(body_text)}</p>
  </div>
</article>
"""
        )
    return f"""
<section class="section policy-detail-section" data-policy-detail>
  <div class="section-head">
    <div>
      <p class="eyebrow">{escape(copy["detail_eyebrow"])}</p>
      <h2>{escape(copy["detail_title"])}</h2>
      <p>{escape(copy["detail_intro"])}</p>
    </div>
  </div>
  <div class="policy-detail-list">
    {''.join(articles)}
  </div>
</section>
"""


def policy_contact_route(lang: str, slug: str) -> str:
    if slug not in {"privacy", "terms"}:
        return ""
    copy = POLICY_CONTACT_CTA[lang]
    return f"""
<section class="section article-body standalone policy-contact-route">
  <h2>{escape(copy["title"])}</h2>
  <p>{escape(copy["intro"])}</p>
  <div class="hero-actions"><a class="primary-btn" href="{lang_url(lang, "contact")}#site-repair-report">{escape(copy["cta"])}</a></div>
</section>
"""


def trust_hero_actions(lang: str, slug: str) -> str:
    t = LANGS[lang]
    if slug == "about":
        actions = [
            ("primary-btn", "quiz", lang_url(lang) + "#quiz-section", t["start"]),
            ("secondary-btn", "guardians", lang_url(lang, "characters"), t["guardians"]),
            ("secondary-btn", "theory", lang_url(lang, "theory"), t["theory"]),
        ]
    elif slug == "contact":
        request = CONTACT_REQUESTS[lang]
        repair = CONTACT_REPAIR_REPORTS[lang]
        actions = [
            ("primary-btn", "luna-request", "#luna-supply-request", request["cta"]),
            ("secondary-btn", "site-repair", "#site-repair-report", repair["cta"]),
            ("secondary-btn", "map", lang_url(lang, "garden-map"), t["map"]),
        ]
    else:
        copy = POLICY_CONTACT_CTA[lang]
        actions = [
            ("primary-btn", "site-repair", lang_url(lang, "contact") + "#site-repair-report", copy["cta"]),
            ("secondary-btn", "map", lang_url(lang, "garden-map"), t["map"]),
            ("secondary-btn", "about", lang_url(lang, "about"), t["about"]),
        ]
    links = "".join(
        f'<a class="{button_class}" href="{href}" data-trust-hero-link="{escape(key)}">{escape(label)}</a>'
        for button_class, key, href, label in actions
    )
    return f'<div class="hero-actions" data-trust-hero-actions="{escape(slug)}">{links}</div>'


def page_path(lang: str, path: str = "") -> Path:
    prefix = LANGS[lang]["prefix"]
    parts = []
    if prefix:
        parts.append(prefix)
    if path:
        parts.extend(path.strip("/").split("/"))
    return ROOT.joinpath(*parts, "index.html") if parts else ROOT / "index.html"


def img_tag(src: str, alt: str, class_name: str = "", lazy: bool = True, priority: bool = False) -> str:
    width, height = IMAGE_DIMENSIONS.get(src, ("", ""))
    attrs = [
        f'src="{src}"',
        f'alt="{escape(alt)}"',
    ]
    if width and height:
        attrs += [f'width="{width}"', f'height="{height}"']
    if priority:
        attrs.append('loading="eager"')
        attrs.append('fetchpriority="high"')
        attrs.append('decoding="async"')
    elif lazy:
        attrs.append('loading="lazy"')
        attrs.append('decoding="async"')
        attrs.append('fetchpriority="low"')
    else:
        attrs.append('loading="eager"')
        attrs.append('decoding="async"')
    if class_name:
        attrs.append(f'class="{class_name}"')
    return "<img " + " ".join(attrs) + " />"


def responsive_img_tag(
    src: str,
    mobile_src: str,
    alt: str,
    class_name: str = "",
    lazy: bool = True,
    priority: bool = False,
) -> str:
    if mobile_src == src:
        return img_tag(src, alt, class_name, lazy, priority)
    mobile_width, mobile_height = IMAGE_DIMENSIONS.get(mobile_src, ("", ""))
    source_attrs = ['media="(max-width: 720px)"', f'srcset="{mobile_src}"']
    if mobile_width and mobile_height:
        source_attrs += [f'width="{mobile_width}"', f'height="{mobile_height}"']
    return f"<picture><source {' '.join(source_attrs)} />{img_tag(src, alt, class_name, lazy, priority)}</picture>"


def json_text(value: str) -> str:
    return escape(value).replace('"', '\\"')


def nav(lang: str, active: str = "", path: str = "", alternate_path: str | None = None) -> str:
    t = LANGS[lang]
    language_path = alternate_path if alternate_path is not None else path
    items = [
        (lang_url(lang, "garden-map"), t["map"]),
        (lang_url(lang, "guides"), t["guides"]),
        (lang_url(lang, "characters"), t["guardians"]),
        (lang_url(lang, "theory"), t["theory"]),
        (lang_url(lang, "resources"), t["resources"]),
        (lang_url(lang, "about"), t["about"]),
    ]
    links = "".join(
        f'<a class="active" href="{href}" aria-current="page">{escape(label)}</a>' if active == label
        else f'<a href="{href}">{escape(label)}</a>'
        for href, label in items
    )
    lang_links = "".join(
        f'<a class="active" href="{lang_url(code, language_path)}" lang="{cfg["code"]}" aria-current="page">{cfg["name"]}</a>'
        if code == lang
        else f'<a href="{lang_url(code, language_path)}" lang="{cfg["code"]}">{cfg["name"]}</a>'
        for code, cfg in LANGS.items()
    )
    return f"""
<header class="site-nav">
  <a class="brand" href="{lang_url(lang)}" aria-label="{escape(t["brand"])}"><span>LoveTypes</span></a>
  <nav class="nav-links" aria-label="{escape(t["primary_nav"])}">{links}</nav>
  <details class="language-menu">
    <summary aria-label="{escape(t["language_menu"])}"><span></span></summary>
    <div class="language-switcher">{lang_links}</div>
  </details>
</header>
"""


def footer(lang: str) -> str:
    t = LANGS[lang]
    cards = [
        (lang_url(lang, "garden-map"), GARDEN_MAP[lang]["title"], GARDEN_MAP[lang]["desc"]),
        (lang_url(lang, "characters"), CHARACTER_INDEX_COPY[lang]["h1"], CHARACTER_INDEX_COPY[lang]["intro"]),
        (lang_url(lang, "resources"), t["resources"], t["resources_desc"]),
        (lang_url(lang, "guides"), t["guides"], t["guide_index_desc"]),
        (lang_url(lang, "repair-plan"), REPAIR_PLAN[lang]["title"], REPAIR_PLAN[lang]["desc"]),
    ]
    card_html = "".join(f'<a href="{href}"><strong>{escape(title)}</strong><span>{escape(desc)}</span></a>' for href, title, desc in cards)
    return f"""
<footer class="site-footer">
  <div class="footer-grid">{card_html}</div>
  <p>© 2026 LoveTypes · <a href="{lang_url(lang, "privacy")}">{escape(t["privacy"])}</a> · <a href="{lang_url(lang, "terms")}">{escape(t["terms"])}</a> · <a href="{lang_url(lang, "contact")}">{escape(t["contact"])}</a></p>
</footer>
"""


def crumb_title(title: str) -> str:
    return title.split(" | ")[0].split("｜")[0].strip()


def breadcrumb_items(lang: str, path: str, title: str) -> list[tuple[str, str]]:
    if not path:
        return []
    t = LANGS[lang]
    section_titles = {
        "guides": t["guides"],
        "characters": t["guardians"],
        "resources": t["resources"],
        "garden-map": GARDEN_MAP[lang]["title"],
        "repair-plan": REPAIR_PLAN[lang]["title"],
        "keepsakes": KEEPSAKES_PAGE[lang]["title"],
        "luna-yoga-music": t["luna_title"],
        "theory": t["theory"],
        "about": t["about"],
        "contact": t["contact"],
        "privacy": t["privacy"],
        "terms": t["terms"],
    }
    parts = path.strip("/").split("/")
    items = [(t["brand"], lang_url(lang))]
    if len(parts) > 1 and parts[0] in section_titles:
        items.append((section_titles[parts[0]], lang_url(lang, parts[0])))
    items.append((crumb_title(title) or section_titles.get(parts[0], title), lang_url(lang, path)))
    return items


def breadcrumb_nav(lang: str, path: str, title: str) -> str:
    items = breadcrumb_items(lang, path, title)
    if not items:
        return ""
    links = []
    for idx, (label, href) in enumerate(items):
        if idx == len(items) - 1:
            links.append(f'<span aria-current="page">{escape(label)}</span>')
        else:
            links.append(f'<a href="{href}">{escape(label)}</a>')
    return f'<nav class="breadcrumb" aria-label="{escape(LANGS[lang]["breadcrumb_label"])}">{"<span>/</span>".join(links)}</nav>'


def breadcrumb_schema(lang: str, path: str, title: str) -> str:
    items = breadcrumb_items(lang, path, title)
    if not items:
        return ""
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index,
                "name": label,
                "item": f"{DOMAIN}{href}",
            }
            for index, (label, href) in enumerate(items, start=1)
        ],
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False, separators=(",", ":"))}</script>'


def json_ld(data: dict) -> str:
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False, separators=(",", ":"))}</script>'


def organization_ref() -> dict:
    return {"@type": "Organization", "@id": f"{DOMAIN}/#organization", "name": "LoveTypes", "url": f"{DOMAIN}/"}


def website_ref(lang: str) -> dict:
    return {"@type": "WebSite", "@id": f"{abs_url(lang)}#website", "name": LANGS[lang]["brand"], "url": abs_url(lang)}


def organization_schema(lang: str) -> str:
    t = LANGS[lang]
    return json_ld({
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": f"{DOMAIN}/#organization",
        "name": "LoveTypes",
        "url": f"{DOMAIN}/",
        "logo": f"{DOMAIN}/apple-touch-icon.png",
        "email": CONTACT_EMAIL,
        "description": t["trust_intro"],
        "contactPoint": {
            "@type": "ContactPoint",
            "email": CONTACT_EMAIL,
            "contactType": "content corrections and privacy inquiries",
            "availableLanguage": ["zh-TW", "en", "ja", "ko", "es"],
        },
        "publishingPrinciples": abs_url(lang, "about"),
        "privacyPolicy": abs_url(lang, "privacy"),
    })


def item_list_schema(name: str, description: str, items: list[tuple[str, str]]) -> str:
    return json_ld({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "description": description,
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index,
                "name": item_name,
                "url": item_url,
            }
            for index, (item_name, item_url) in enumerate(items, start=1)
        ],
    })


def head(
    lang: str,
    title: str,
    desc: str,
    path: str = "",
    page_type: str = "website",
    image: str = "/og-cover.jpg",
    alternate_path: str | None = None,
    canonical_path: str | None = None,
    robots: str = "index, follow, max-image-preview:large",
) -> str:
    canonical = abs_url(lang, canonical_path if canonical_path is not None else path)
    alternate_target = alternate_path if alternate_path is not None else path
    alternates = "\n".join(f'  <link rel="alternate" hreflang="{cfg["code"]}" href="{abs_url(code, alternate_target)}" />' for code, cfg in LANGS.items())
    alternates += f'\n  <link rel="alternate" hreflang="x-default" href="{abs_url("zh", alternate_target)}" />'
    og_locale = OG_LOCALES[lang]
    og_locale_alternates = "\n".join(
        f'  <meta property="og:locale:alternate" content="{locale}" />'
        for code, locale in OG_LOCALES.items()
        if code != lang
    )
    image_width, image_height = IMAGE_DIMENSIONS.get(image, (1200, 630))
    hero_preload = ""
    if path == "":
        hero_preload = """  <link rel="preload" as="image" href="/assets/lovetypes/backgrounds/guardian-garden-mobile.webp" media="(max-width: 720px)" fetchpriority="high" />
  <link rel="preload" as="image" href="/assets/lovetypes/backgrounds/guardian-garden.webp" media="(min-width: 721px)" fetchpriority="high" />
"""
    return f"""<!DOCTYPE html>
<html lang="{LANGS[lang]["code"]}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="google-adsense-account" content="{ADSENSE_ACCOUNT}" />
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(desc)}" />
  <meta name="robots" content="{escape(robots)}" />
  <link rel="canonical" href="{canonical}" />
{alternates}
  <link rel="icon" href="/favicon.ico" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />
  <link rel="alternate" type="application/rss+xml" title="LoveTypes 守護者指南" href="/feed.xml" />
  <meta name="theme-color" content="#7a4d6d" />
  <meta property="og:type" content="{page_type}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:title" content="{escape(title)}" />
  <meta property="og:description" content="{escape(desc)}" />
  <meta property="og:image" content="{DOMAIN}{image}" />
  <meta property="og:image:width" content="{image_width}" />
  <meta property="og:image:height" content="{image_height}" />
  <meta property="og:locale" content="{og_locale}" />
{og_locale_alternates}
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{DOMAIN}{image}" />
{hero_preload}  <link rel="stylesheet" href="{CSS_ASSET}" />
</head>
"""


def layout(
    lang: str,
    title: str,
    desc: str,
    path: str,
    body: str,
    active: str = "",
    page_type: str = "website",
    image: str = "/og-cover.jpg",
    schema: str = "",
    affiliate: bool = False,
    alternate_path: str | None = None,
    canonical_path: str | None = None,
    robots: str = "index, follow, max-image-preview:large",
) -> str:
    external_script = ""
    if affiliate:
        external_script = f'\n<script src="{AFFILIATE_ASSET}" data-affiliate defer></script>'
    return head(lang, title, desc, path, page_type, image, alternate_path, canonical_path, robots) + f"""<body>
<a class="skip-link" href="#main">{escape(LANGS[lang]["skip_content"])}</a>
{nav(lang, active, path, alternate_path)}
{organization_schema(lang)}
{schema}
{breadcrumb_schema(lang, path, title)}
{breadcrumb_nav(lang, path, title)}
<main id="main" tabindex="-1">
{body}
</main>
{footer(lang)}
<script src="{INTERACTIONS_ASSET}" defer></script>
{external_script}
</body>
</html>
"""


def write(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def cleanup_versioned_assets() -> None:
    for legacy_name in STATIC_ASSET_SOURCES:
        legacy_path = ROOT / legacy_name
        if legacy_path.exists():
            legacy_path.unlink()
    for source_name, target in STATIC_ASSET_SOURCES.items():
        prefix, suffix = source_name.rsplit(".", 1)
        current_name = Path(target.lstrip("/")).name
        for asset in ROOT.glob(f"{prefix}-*.{suffix}"):
            if asset.name != current_name:
                asset.unlink()
    current_quiz_names = {Path(asset.lstrip("/")).name for asset in QUIZ_DATA_ASSETS.values()}
    for asset in ROOT.glob("quiz-data-*.js"):
        if asset.name not in current_quiz_names:
            asset.unlink()


def quiz_data_script_tag(lang: str) -> str:
    return f'<script src="{QUIZ_DATA_ASSETS[lang]}"></script>'


def guide_card(lang: str, guide: dict) -> str:
    title, desc = guide[lang]
    guardian = GUARDIANS[guide["guardian"]][lang][0]
    return f"""
<a class="content-card" href="{lang_url(lang, "guides/" + guide["slug"])}">
  <span class="eyebrow">{escape(guardian)}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
  <span class="card-link">{escape(LANGS[lang]["read"])}</span>
</a>
"""


def character_card(lang: str, slug: str, data: dict, current_slug: str = "") -> str:
    name, typ, desc = data[lang]
    domain_title, domain_desc, domain_cta = GUARDIAN_DOMAINS[slug][lang]
    domain = GUARDIAN_DOMAINS[slug]
    current = slug == current_slug
    attrs = 'class="guardian-card is-current" aria-current="page"' if current else 'class="guardian-card"'
    prop_alt = f"{name} {domain_title}"
    card_asset = data.get("card_asset", data["asset"])
    guardian_image = img_tag(card_asset, name)
    return f"""
<a {attrs} href="{lang_url(lang, "characters/" + slug)}" data-guardian-domain="{slug}" style="--domain-accent:{domain["accent"]};--domain-glow:{domain["glow"]}">
  {guardian_image}
  <div>
    <span>{escape(typ)}</span>
    <h3>{escape(name)}</h3>
    <p class="domain-title">{escape(domain_title)}</p>
    <p>{escape(domain_desc)}</p>
    <small>{escape(domain_cta)}</small>
    {img_tag(data["prop"], prop_alt, "guardian-prop")}
  </div>
</a>
"""


def character_link_card(lang: str, slug: str, data: dict, current_slug: str = "") -> str:
    name, typ, _desc = data[lang]
    domain_title, _domain_desc, domain_cta = GUARDIAN_DOMAINS[slug][lang]
    domain = GUARDIAN_DOMAINS[slug]
    current = slug == current_slug
    attrs = 'class="guardian-card is-current" aria-current="page"' if current else 'class="guardian-card"'
    card_asset = data.get("card_asset", data["asset"])
    guardian_image = img_tag(card_asset, name)
    return f"""
<a {attrs} href="{lang_url(lang, "characters/" + slug)}" data-guardian-domain="{slug}" style="--domain-accent:{domain["accent"]};--domain-glow:{domain["glow"]}">
  {guardian_image}
  <div><span>{escape(typ)}</span><h3>{escape(name)}</h3><p class="domain-title">{escape(domain_title)}</p><small>{escape(domain_cta)}</small></div>
</a>
"""


def supply_route(lang: str, slug: str) -> dict:
    route = SUPPLY_ROUTES[slug]
    title, desc, wound, mission, supply = route[lang]
    guide_slug = next(meta["guide"] for meta in QUIZ_TYPES.values() if meta["slug"] == slug)
    guide = next(g for g in GUIDES if g["slug"] == guide_slug)
    return {
        "slug": slug,
        "title": title,
        "desc": desc,
        "wound": wound,
        "mission": mission,
        "supply": supply,
        "guide": guide,
        "book": AFFILIATE_BOOKS[route["book"]],
        "guardian": GUARDIANS[slug],
    }


def supply_request_href(lang: str, slug: str) -> str:
    labels = SUPPLY_LABELS[lang]
    wishlist = SUPPLY_WISHLIST[lang]
    route = supply_route(lang, slug)
    guardian_name, _guardian_type, _guardian_desc = route["guardian"][lang]
    request_subject = quote(wishlist["subject"])
    request_body = quote(
        f'{wishlist["body"]} {guardian_name} · {route["title"]}\n'
        f'{labels["practice"]}: {route["mission"]}\n'
        f'{labels["supply"]}: {route["supply"]}\n'
        f'{wishlist["format_label"]}: {", ".join(wishlist["formats"])}\n'
        f'{wishlist["body_context"]} \n\n'
    )
    return f"mailto:contact@lovetypes.tw?subject={request_subject}&body={request_body}"


def supply_product_pack(lang: str, slug: str) -> dict:
    product = SUPPLY_PRODUCT_STACK[lang]
    return {
        "label": product["label"],
        "note": product["template_note"],
        "items": [
            {
                "number": "1",
                "title": product["free"],
                "desc": product["free_desc"],
                "href": lang_url(lang, "keepsakes") + f"#keepsake-card-{slug}",
            },
            {
                "number": "2",
                "title": product["owned"],
                "desc": product["owned_desc"],
                "href": supply_request_href(lang, slug),
            },
            {
                "number": "3",
                "title": product["night"],
                "desc": product["night_desc"],
                "href": lang_url(lang, "luna-yoga-music") + f"#luna-{slug}",
            },
            {
                "number": "4",
                "title": product["contact"],
                "desc": product["contact_desc"],
                "href": lang_url(lang, "contact") + "#luna-supply-request",
            },
        ],
    }


def supply_route_card(lang: str, slug: str) -> str:
    labels = SUPPLY_LABELS[lang]
    product = SUPPLY_PRODUCT_STACK[lang]
    route = supply_route(lang, slug)
    guardian_name, guardian_type, _guardian_desc = route["guardian"][lang]
    book = route["book"]
    guide = route["guide"]
    summary = {
        "title": route["title"],
        "guardian": f"{guardian_name} · {guardian_type}",
        "practice": route["mission"],
        "supply": route["supply"],
        "book": f'{book["title"][lang]} · {book["author"]}',
        "url": abs_url(lang, "resources") + f"#supply-{slug}",
    }
    summary_json = escape(json.dumps(summary, ensure_ascii=False))
    request_href = supply_request_href(lang, slug)
    product_items = [
        (product["free"], product["free_desc"], lang_url(lang, "keepsakes") + f"#keepsake-card-{slug}"),
        (product["owned"], product["owned_desc"], request_href),
        (product["night"], product["night_desc"], lang_url(lang, "luna-yoga-music") + f"#luna-{slug}"),
        (product["contact"], product["contact_desc"], lang_url(lang, "contact") + "#luna-supply-request"),
    ]
    product_cards = "".join(
        f'<li><a href="{escape(href)}"><strong>{escape(title)}</strong><span>{escape(desc)}</span></a></li>'
        for title, desc, href in product_items
    )
    return f"""
<article class="supply-route-card" id="supply-{slug}">
  {img_tag(route["guardian"]["prop"], route["title"])}
  <div class="supply-route-copy">
    <p class="eyebrow">{escape(guardian_name)} · {escape(guardian_type)}</p>
    <h3>{escape(route["title"])}</h3>
    <p>{escape(route["desc"])}</p>
    <dl>
      <div><dt>{escape(labels["practice"])}</dt><dd>{escape(route["mission"])}</dd></div>
      <div><dt>{escape(labels["supply"])}</dt><dd>{escape(route["supply"])}</dd></div>
    </dl>
    <p class="supply-book-note"><strong>{escape(book["title"][lang])}</strong> · {escape(book["author"])}</p>
    <div class="supply-format-block supply-product-stack" data-supply-product-stack>
      <span>{escape(product["label"])}</span>
      <ul class="supply-format-list">{product_cards}</ul>
      <small>{escape(product["template_note"])}</small>
    </div>
  </div>
  <div class="supply-route-actions">
    <a class="primary-btn" href="{lang_url(lang, "guides/" + guide["slug"])}">{escape(labels["read_guide"])}</a>
    <a class="secondary-btn" href="{lang_url(lang, "luna-yoga-music")}#luna-{slug}">{escape(labels["open_luna"])}</a>
    <a class="secondary-btn" href="{lang_url(lang, "keepsakes")}#keepsake-card-{slug}">{escape(labels["free_keepsake"])}</a>
    <a class="secondary-btn" href="{request_href}" data-funnel-event="supply_route_mailto">{escape(labels["request_supply"])}</a>
    <button class="secondary-btn" type="button" data-copy-supply-route data-funnel-event="supply_route_copy" data-route-summary="{summary_json}">{escape(labels["copy_route"])}</button>
    <a class="secondary-btn" href="{book["url"]}" target="_blank" rel="noopener noreferrer sponsored" data-funnel-event="supply_route_affiliate_book">{escape(AFFILIATE_COPY[lang]["button"])}</a>
  </div>
</article>
"""


def supply_quick_route_nav(lang: str) -> str:
    labels = SUPPLY_LABELS[lang]
    t = LANGS[lang]
    cards = []
    for slug, data in GUARDIANS.items():
        route = supply_route(lang, slug)
        name, typ, _desc = data[lang]
        domain = GUARDIAN_DOMAINS[slug]
        cards.append(f"""
<a class="supply-quick-card" href="#supply-{slug}" data-guardian-domain="{slug}" style="--domain-accent:{domain["accent"]};--domain-glow:{domain["glow"]}">
  {img_tag(data["prop"], f"{name} {route['title']}", "supply-quick-prop")}
  <span class="eyebrow">{escape(name)} · {escape(typ)}</span>
  <h3>{escape(route["title"])}</h3>
  <p>{escape(route["desc"])}</p>
  <strong>{escape(labels["route"])}</strong>
</a>
""")
    return f"""
<section class="section supply-quick-routes supply-domain-routes" data-supply-domain-strip>
  <div class="section-head">
    <div><p class="eyebrow">{escape(labels["title"])}</p><h2>{escape(labels["quick_route"])}</h2></div>
    <a href="{lang_url(lang)}#quiz-section">{escape(t["start"])}</a>
  </div>
  <p class="section-intro">{escape(labels["intro"])}</p>
  <div class="supply-quick-grid">{"".join(cards)}</div>
</section>
"""


def supply_decision_matrix(lang: str) -> str:
    decision = SUPPLY_DECISION[lang]
    cards = []
    for index, (title, desc, action, target) in enumerate(decision["matrix"], start=1):
        if target.startswith("#"):
            href = lang_url(lang, "resources") + target
        elif "#" in target:
            route, anchor = target.split("#", 1)
            href = lang_url(lang, route) + f"#{anchor}"
        else:
            href = lang_url(lang, target)
        cards.append(f"""
<article class="supply-decision-card" data-supply-decision-card>
  <span>{index:02d}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
  <a class="secondary-btn" href="{href}" data-funnel-event="supply_decision_matrix">{escape(action)}</a>
</article>
""")
    return f"""
<section class="section supply-decision-matrix" data-supply-decision-matrix>
  <div class="section-head"><div><p class="eyebrow">{escape(decision["eyebrow"])}</p><h2>{escape(decision["matrix_title"])}</h2></div></div>
  <div class="supply-compass-grid supply-decision-grid">{"".join(cards)}</div>
</section>
"""


def supply_entry_section(lang: str) -> str:
    entry = SUPPLY_ENTRY[lang]
    cards = []
    for title, desc, action, target in entry["items"]:
        if target.startswith("#"):
            href = target
            action_key = "routes" if target == "#supply-routes" else "anchor"
        elif target:
            href = lang_url(lang, target)
            action_key = "luna" if target == "luna-yoga-music" else target
        else:
            href = lang_url(lang) + "#quiz-section"
            action_key = "quiz"
        cards.append(f"""
<article data-supply-entry-card="{escape(action_key)}">
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
  <a href="{href}" data-supply-entry-link="{escape(action_key)}" data-default-href="{href}">{escape(action)}</a>
</article>
""")
    return f"""
<section class="section supply-entry" id="supply-start">
  <div class="section-head"><div><p class="eyebrow">{escape(entry["eyebrow"])}</p><h2>{escape(entry["title"])}</h2></div></div>
  <p class="section-intro">{escape(entry["intro"])}</p>
  <div class="supply-entry-grid">{"".join(cards)}</div>
</section>
"""


def supply_hero_actions(lang: str) -> str:
    actions = []
    for index, (_title, _desc, action, target) in enumerate(SUPPLY_ENTRY[lang]["items"]):
        if target.startswith("#"):
            href = target
            action_key = "routes" if target == "#supply-routes" else "anchor"
        elif target:
            href = lang_url(lang, target)
            action_key = "luna" if target == "luna-yoga-music" else target
        else:
            href = lang_url(lang) + "#quiz-section"
            action_key = "quiz"
        button_class = "primary-btn" if index == 0 else "secondary-btn"
        actions.append(
            f'<a class="{button_class}" href="{href}" data-supply-hero-link="{escape(action_key)}">{escape(action)}</a>'
        )
    return f'<div class="hero-actions" data-supply-hero-actions>{"".join(actions)}</div>'


UNIVERSE_COPY = {
    "zh": ("五域宇宙入口", "從心語庭園進入五個分域，選一盞最像你此刻需要的光。", "五域星圖", "每位守護者不是分類標籤，而是一個可以進入、停留、練習的情感分域。"),
    "en": ("Five Universe Gates", "Enter five domains from the Heart Garden and choose the light closest to what you need now.", "Five-Domain Star Map", "Each guardian is not a label, but an emotional domain you can enter, stay in, and practice with."),
    "ja": ("五つの宇宙入口", "心語の庭から五つの領域へ入り、今必要な光を一つ選びます。", "五領域の星図", "守護者は分類ではなく、入って留まり、練習できる感情の領域です。"),
    "ko": ("다섯 우주 입구", "마음의 정원에서 다섯 영역으로 들어가 지금 필요한 빛을 하나 고릅니다.", "다섯 영역 별지도", "수호자는 분류표가 아니라 들어가 머물고 연습하는 감정 영역입니다."),
    "es": ("Cinco portales de universo", "Entra a cinco dominios desde el Jardín del Corazón y elige la luz que más necesitas ahora.", "Mapa estelar de cinco dominios", "Cada guardiana no es una etiqueta, sino un dominio emocional para entrar, quedarse y practicar."),
}


HOME_JOURNEY = {
    "zh": {
        "eyebrow": "GARDEN JOURNEY",
        "title": "第一次進入心語庭園，可以照這條路走",
        "intro": "不需要一次讀完整座宇宙。先完成命運儀式，再認出守護者，接著選一個補給，最後把它放進一個可執行的修復週期。",
        "steps": [
            ("01", "完成命運儀式", "用 15 道心語辨認你最容易感到被愛的入口。", "開始測驗", "#quiz-section"),
            ("02", "拜訪五個分域", "看見艾莉絲、諾雅、薇薇安、克萊兒、朵拉各自守護的關係語言。", "看守護者", "characters"),
            ("03", "領取一個補給", "依照結果拿走對應指南、小任務、書卷或 Luna 夜間補給。", "前往補給站", "resources"),
            ("04", "寫下 7 日修復", "把感受變成一次小請求、一段冷卻時間與一個可完成行動。", "打開修復計畫", "repair-plan"),
        ],
    },
    "en": {
        "eyebrow": "GARDEN JOURNEY",
        "title": "If this is your first time in the Heart Garden, follow this route",
        "intro": "You do not need to read the whole universe at once. Complete the ritual, recognize your guardian, choose one supply, then place it into a practical repair week.",
        "steps": [
            ("01", "Complete the ritual", "Use 15 heart-language prompts to recognize the doorway where love reaches you fastest.", "Start quiz", "#quiz-section"),
            ("02", "Visit five domains", "Meet Iris, Noah, Vivian, Claire, and Dora as five relationship languages you can enter.", "See guardians", "characters"),
            ("03", "Take one supply", "Carry the matching guide, small task, book route, or Luna night support from your result.", "Open supplies", "resources"),
            ("04", "Write a 7-day repair", "Turn the feeling into one small request, a cool-down rhythm, and one doable action.", "Open repair plan", "repair-plan"),
        ],
    },
    "ja": {
        "eyebrow": "GARDEN JOURNEY",
        "title": "初めて心語の庭に入るなら、この順番で進みます",
        "intro": "宇宙全体を一度に読む必要はありません。儀式を終え、守護者を認め、補給を一つ選び、それを実行できる修復週間に入れます。",
        "steps": [
            ("01", "儀式を完了する", "15 の心語で、愛が届きやすい入口を見つけます。", "診断を始める", "#quiz-section"),
            ("02", "五つの領域を訪れる", "アイリス、ノア、ヴィヴィアン、クレア、ドラが守る関係の言語を見ます。", "守護者を見る", "characters"),
            ("03", "補給を一つ受け取る", "結果に合わせて、ガイド、小さな課題、本、または Luna の夜の補給を選びます。", "補給站へ", "resources"),
            ("04", "7日間の修復を書く", "感情を小さな依頼、冷却の時間、実行できる行動に変えます。", "修復プランへ", "repair-plan"),
        ],
    },
    "ko": {
        "eyebrow": "GARDEN JOURNEY",
        "title": "마음의 정원에 처음 들어온다면 이 길을 따라가세요",
        "intro": "우주 전체를 한 번에 읽지 않아도 됩니다. 의식을 마치고, 수호자를 알아본 뒤, 보급 하나를 고르고 실행 가능한 회복 주간에 넣으세요.",
        "steps": [
            ("01", "운명 의식 완료", "15개의 마음 언어 질문으로 사랑이 가장 빨리 닿는 입구를 알아봅니다.", "테스트 시작", "#quiz-section"),
            ("02", "다섯 영역 방문", "아이리스, 노아, 비비안, 클레어, 도라가 지키는 관계 언어를 봅니다.", "수호자 보기", "characters"),
            ("03", "보급 하나 받기", "결과에 맞는 가이드, 작은 과제, 책 루트, Luna 밤 보급을 하나 고릅니다.", "보급소 열기", "resources"),
            ("04", "7일 회복 쓰기", "감정을 작은 요청, 식히는 리듬, 실행 가능한 행동으로 바꿉니다.", "회복 계획 열기", "repair-plan"),
        ],
    },
    "es": {
        "eyebrow": "GARDEN JOURNEY",
        "title": "Si entras por primera vez al Jardín del Corazón, sigue esta ruta",
        "intro": "No necesitas leer todo el universo de una vez. Completa el ritual, reconoce tu guardiana, elige un recurso y llévalo a una semana de reparación práctica.",
        "steps": [
            ("01", "Completa el ritual", "Usa 15 preguntas de lenguaje del corazón para reconocer la puerta donde el amor llega más rápido.", "Empezar test", "#quiz-section"),
            ("02", "Visita cinco dominios", "Conoce a Iris, Noah, Vivian, Claire y Dora como cinco lenguajes relacionales.", "Ver guardianas", "characters"),
            ("03", "Toma un recurso", "Lleva una guía, tarea, libro o apoyo nocturno de Luna según tu resultado.", "Abrir recursos", "resources"),
            ("04", "Escribe 7 días", "Convierte la emoción en una petición pequeña, un ritmo de calma y una acción posible.", "Abrir plan", "repair-plan"),
        ],
    },
}


GARDEN_MAP = {
    "zh": {
        "title": "心語庭園地圖",
        "desc": "把 LoveTypes 的測驗、五位守護者、深度指南、旅人補給、Luna、修復計畫與信任頁整理成一張可探索的地圖。",
        "eyebrow": "HEART GARDEN MAP",
        "intro": "如果你不知道下一步該去哪裡，先從這張地圖選一盞燈。每條路都會回到同一個核心：辨認需求、說清楚、做一個小修復。",
        "resume_title": "你的守護者地圖已亮起",
        "resume_intro": "這台裝置保留了上次測驗結果。可以直接回到你的補給路線、修復計畫、收藏卡或 Luna，不必重新找入口。",
        "handoff_title": "認領守護者後，照這個順序走",
        "handoff_intro": "測驗結果不是終點，而是一張通行證。先接住當下的需求，再把它放進可回訪、可練習、可冷卻的路線。",
        "routes_title": "四條主要路線",
        "tools_title": "三個功能房間",
        "guardians_title": "五個分域入口",
        "guides_title": "常用指南燈塔",
        "trust_title": "信任與邊界",
        "routes": [
            ("認領守護者", "從首頁測驗開始，取得你的主要守護者與個人化下一步。", "開始測驗", "#quiz-section"),
            ("走進五域", "直接查看五位守護者與各自的錯頻傷口、修復任務。", "查看守護者", "characters"),
            ("拿一份補給", "依照守護者選指南、任務、Luna 或延伸書卷。", "前往補給站", "resources"),
            ("寫成修復週期", "把情緒整理成 7 日練習，不一次修完整段關係。", "打開修復計畫", "repair-plan"),
        ],
        "tools": [
            ("7 日修復計畫", "把測驗結果寫成一週內能完成的小修復。", "打開修復計畫", "repair-plan"),
            ("守護者收藏室", "保存五位守護者卡片，讓結果變成可回訪、可分享的標記。", "前往收藏室", "keepsakes"),
            ("Luna 夜間補給", "睡前、冷卻或書寫時，用低光音樂先降低情緒噪音。", "開啟 Luna", "luna-yoga-music"),
        ],
        "handoff": [
            ("01", "先拿專屬補給", "依守護者進入補給站，取得一個任務、一篇指南與一份延伸書卷。", "resources"),
            ("02", "寫成七日修復", "把情緒翻成小請求與可完成行動，避免只停在結果標籤。", "repair-plan"),
            ("03", "收藏你的守護者", "把守護者卡片留下來，之後回訪時能快速找回自己的入口。", "keepsakes"),
            ("04", "夜間低光整理", "睡前或爭執後，用 Luna 降低情緒噪音，再回到修復計畫。", "luna-yoga-music"),
        ],
        "trust_routes": [
            ("關於心語庭園", "理解 LoveTypes 的宇宙觀、內容邊界與適合使用方式。", "about"),
            ("愛之語理論", "回到五種愛之語的溝通框架，理解它不是人格標籤。", "theory"),
            ("聯絡與修復頁面", "回報錯誤、合作、素材授權或需要修復的頁面。", "contact"),
            ("隱私與條款", "查看資料、聯盟揭露、內容限制與使用邊界。", "privacy"),
        ],
    },
    "en": {
        "title": "Heart Garden Map",
        "desc": "A readable map of the LoveTypes quiz, five guardians, field guides, supplies, Luna, repair plan, and trust pages.",
        "eyebrow": "HEART GARDEN MAP",
        "intro": "If you are not sure where to go next, choose one lamp from this map. Every route returns to the same core: name the need, say it clearly, and practice one small repair.",
        "resume_title": "Your guardian map is lit",
        "resume_intro": "This device has your last quiz result. Return directly to your supply route, repair plan, keepsake card, or Luna without finding the doorway again.",
        "handoff_title": "After recognizing your guardian, follow this order",
        "handoff_intro": "The quiz result is not the finish line. It is a pass that helps you hold the current need, then place it into a route you can revisit, practice, and cool down with.",
        "routes_title": "Four main routes",
        "tools_title": "Three function rooms",
        "guardians_title": "Five domain gates",
        "guides_title": "Useful guide lamps",
        "trust_title": "Trust and boundaries",
        "routes": [
            ("Recognize your guardian", "Start with the homepage quiz and receive a guardian plus personal next steps.", "Start quiz", "#quiz-section"),
            ("Enter five domains", "See the five guardians, misfrequency wounds, and repair missions.", "View guardians", "characters"),
            ("Take one supply", "Choose a guide, task, Luna path, or book route by guardian.", "Open supplies", "resources"),
            ("Make a repair week", "Turn the emotion into seven days of practice without repairing everything at once.", "Open repair plan", "repair-plan"),
        ],
        "tools": [
            ("7-Day Repair Plan", "Turn your result into one week of small repair practice.", "Open repair plan", "repair-plan"),
            ("Guardian Keepsake Hall", "Save the five guardian cards as a revisitable and shareable marker.", "Open keepsakes", "keepsakes"),
            ("Luna Night Supply", "Use low-light audio before sleep, cooling down, or journaling.", "Open Luna", "luna-yoga-music"),
        ],
        "handoff": [
            ("01", "Take your supply first", "Enter the supply station by guardian and receive one task, one guide, and one book route.", "resources"),
            ("02", "Write a 7-day repair", "Translate emotion into one small request and one doable action, instead of stopping at a label.", "repair-plan"),
            ("03", "Save your guardian", "Keep the guardian card so returning visitors can find their doorway quickly.", "keepsakes"),
            ("04", "Cool down at night", "Use Luna before sleep or after conflict, then return to the repair plan.", "luna-yoga-music"),
        ],
        "trust_routes": [
            ("About the Heart Garden", "Understand the LoveTypes universe, content boundary, and best use cases.", "about"),
            ("Love-language theory", "Return to the communication framework behind the five languages.", "theory"),
            ("Contact and page repair", "Report mistakes, partnerships, asset permissions, or pages that need repair.", "contact"),
            ("Privacy and terms", "Review data, affiliate disclosure, content limits, and usage boundaries.", "privacy"),
        ],
    },
    "ja": {
        "title": "心語の庭マップ",
        "desc": "LoveTypes の診断、五人の守護者、ガイド、補給、Luna、修復プラン、信頼ページを一枚の地図にまとめます。",
        "eyebrow": "HEART GARDEN MAP",
        "intro": "次にどこへ進むか迷ったら、この地図から一つの灯りを選んでください。どの道も、必要を名づけ、言葉にし、小さな修復へ戻ります。",
        "resume_title": "あなたの守護者地図が灯っています",
        "resume_intro": "この端末には前回の診断結果が残っています。補給ルート、修復プラン、カード、Luna へすぐ戻れます。",
        "handoff_title": "守護者を認領した後は、この順番で進みます",
        "handoff_intro": "診断結果は終点ではなく通行証です。今の必要を受け止め、戻れて、練習でき、冷却できる道へ置きます。",
        "routes_title": "四つの主要ルート",
        "tools_title": "三つの機能室",
        "guardians_title": "五つの領域入口",
        "guides_title": "よく使うガイド",
        "trust_title": "信頼と境界",
        "routes": [
            ("守護者を認領する", "ホームの診断から、主な守護者と個人の次の一歩を受け取ります。", "診断を始める", "#quiz-section"),
            ("五つの領域へ入る", "五人の守護者、すれ違いの傷、修復課題を見ます。", "守護者を見る", "characters"),
            ("補給を一つ選ぶ", "守護者に合わせて、ガイド、課題、Luna、本のルートを選びます。", "補給へ", "resources"),
            ("修復週間にする", "感情を七日間の練習へ変え、一度にすべてを直そうとしません。", "修復プランへ", "repair-plan"),
        ],
        "tools": [
            ("7日間の修復プラン", "結果を一週間でできる小さな修復練習へ変えます。", "修復プランへ", "repair-plan"),
            ("守護者コレクション室", "五人の守護者カードを保存し、戻って見られる印にします。", "コレクション室へ", "keepsakes"),
            ("Luna 夜の補給", "眠る前、冷却、日記の時間に、低い音で感情のノイズを下げます。", "Luna を開く", "luna-yoga-music"),
        ],
        "handoff": [
            ("01", "まず補給を受け取る", "守護者に合わせて補給站へ入り、課題、ガイド、本のルートを一つ受け取ります。", "resources"),
            ("02", "7日間の修復を書く", "結果のラベルで止まらず、感情を小さな依頼と実行できる行動へ変えます。", "repair-plan"),
            ("03", "守護者を保存する", "守護者カードを残し、次に戻った時すぐ入口を見つけます。", "keepsakes"),
            ("04", "夜に冷却する", "眠る前や衝突後に Luna で感情のノイズを下げ、修復プランへ戻ります。", "luna-yoga-music"),
        ],
        "trust_routes": [
            ("心語の庭について", "LoveTypes の世界観、内容の範囲、使い方を理解します。", "about"),
            ("愛の言語理論", "五つの言語の背後にあるコミュニケーション枠組みに戻ります。", "theory"),
            ("連絡とページ修復", "誤り、協力、素材許可、修復が必要なページを知らせます。", "contact"),
            ("プライバシーと規約", "データ、アフィリエイト開示、内容制限、利用境界を確認します。", "privacy"),
        ],
    },
    "ko": {
        "title": "마음의 정원 지도",
        "desc": "LoveTypes 테스트, 다섯 수호자, 가이드, 보급, Luna, 회복 계획, 신뢰 페이지를 한 장의 지도로 정리합니다.",
        "eyebrow": "HEART GARDEN MAP",
        "intro": "다음에 어디로 갈지 모르겠다면 이 지도에서 등불 하나를 고르세요. 모든 길은 필요를 이름 붙이고, 분명히 말하고, 작은 회복을 연습하는 곳으로 돌아옵니다.",
        "resume_title": "나의 수호자 지도가 켜졌습니다",
        "resume_intro": "이 기기에 지난 테스트 결과가 남아 있습니다. 보급 루트, 회복 계획, 소장 카드, Luna 로 바로 돌아갈 수 있습니다.",
        "handoff_title": "수호자를 알아본 뒤에는 이 순서로 가세요",
        "handoff_intro": "테스트 결과는 끝이 아니라 통행증입니다. 지금의 필요를 붙잡고 다시 보고, 연습하고, 식힐 수 있는 길에 놓으세요.",
        "routes_title": "네 가지 주요 길",
        "tools_title": "세 가지 기능실",
        "guardians_title": "다섯 영역 입구",
        "guides_title": "자주 쓰는 가이드 등불",
        "trust_title": "신뢰와 경계",
        "routes": [
            ("수호자 알아보기", "홈 테스트에서 주요 수호자와 개인 다음 단계를 받습니다.", "테스트 시작", "#quiz-section"),
            ("다섯 영역 들어가기", "다섯 수호자, 어긋남의 상처, 회복 임무를 봅니다.", "수호자 보기", "characters"),
            ("보급 하나 선택", "수호자에 맞는 가이드, 과제, Luna, 책 루트를 고릅니다.", "보급 열기", "resources"),
            ("회복 주간 만들기", "감정을 7일 연습으로 바꾸고 한 번에 모든 것을 고치려 하지 않습니다.", "회복 계획 열기", "repair-plan"),
        ],
        "tools": [
            ("7일 회복 계획", "결과를 일주일 안에 해볼 작은 회복 연습으로 바꿉니다.", "회복 계획 열기", "repair-plan"),
            ("수호자 소장실", "다섯 수호자 카드를 저장해 다시 보고 공유할 표시로 만듭니다.", "소장실 열기", "keepsakes"),
            ("Luna 밤 보급", "잠들기 전, 식히는 시간, 기록할 때 낮은 음악으로 감정 소음을 낮춥니다.", "Luna 열기", "luna-yoga-music"),
        ],
        "handoff": [
            ("01", "먼저 보급 받기", "수호자에 맞춰 보급소로 들어가 과제 하나, 가이드 하나, 책 루트 하나를 받습니다.", "resources"),
            ("02", "7일 회복 쓰기", "결과 이름에서 멈추지 않고 감정을 작은 요청과 가능한 행동으로 바꿉니다.", "repair-plan"),
            ("03", "수호자 저장하기", "수호자 카드를 남겨 다음 방문 때 자신의 입구를 빠르게 찾습니다.", "keepsakes"),
            ("04", "밤에 낮추기", "잠들기 전이나 다툰 뒤 Luna 로 감정 소음을 낮추고 회복 계획으로 돌아갑니다.", "luna-yoga-music"),
        ],
        "trust_routes": [
            ("마음의 정원 소개", "LoveTypes 세계관, 콘텐츠 범위, 사용 방식을 이해합니다.", "about"),
            ("사랑의 언어 이론", "다섯 언어 뒤의 대화 프레임으로 돌아갑니다.", "theory"),
            ("연락과 페이지 수정", "오류, 협업, 자료 허가, 수정이 필요한 페이지를 알립니다.", "contact"),
            ("개인정보와 약관", "자료, 제휴 공개, 콘텐츠 제한, 이용 경계를 확인합니다.", "privacy"),
        ],
    },
    "es": {
        "title": "Mapa del Jardín del Corazón",
        "desc": "Un mapa legible del test LoveTypes, las cinco guardianas, guías, recursos, Luna, plan de reparación y páginas de confianza.",
        "eyebrow": "HEART GARDEN MAP",
        "intro": "Si no sabes adónde ir después, elige una luz en este mapa. Cada ruta vuelve al mismo centro: nombrar la necesidad, decirla con claridad y practicar una reparación pequeña.",
        "resume_title": "Tu mapa de guardiana está encendido",
        "resume_intro": "Este dispositivo conserva tu último resultado. Vuelve directo a tu ruta, plan, tarjeta o Luna sin buscar la puerta otra vez.",
        "handoff_title": "Después de reconocer tu guardiana, sigue este orden",
        "handoff_intro": "El resultado no es el final. Es un pase para sostener la necesidad actual y llevarla a una ruta que puedas revisar, practicar y enfriar.",
        "routes_title": "Cuatro rutas principales",
        "tools_title": "Tres salas funcionales",
        "guardians_title": "Cinco puertas de dominio",
        "guides_title": "Guías útiles",
        "trust_title": "Confianza y límites",
        "routes": [
            ("Reconocer tu guardiana", "Empieza con el test de inicio y recibe una guardiana con siguientes pasos.", "Empezar test", "#quiz-section"),
            ("Entrar a cinco dominios", "Ve las cinco guardianas, heridas de desajuste y misiones de reparación.", "Ver guardianas", "characters"),
            ("Tomar un recurso", "Elige guía, tarea, Luna o libro según tu guardiana.", "Abrir recursos", "resources"),
            ("Crear una semana", "Convierte la emoción en siete días de práctica sin arreglar todo a la vez.", "Abrir plan", "repair-plan"),
        ],
        "tools": [
            ("Plan de 7 días", "Convierte tu resultado en una semana de reparación pequeña.", "Abrir plan", "repair-plan"),
            ("Sala de recuerdos", "Guarda las cinco tarjetas para volver a ellas y compartirlas.", "Abrir recuerdos", "keepsakes"),
            ("Luna nocturna", "Usa audio de baja luz antes de dormir, enfriar o escribir.", "Abrir Luna", "luna-yoga-music"),
        ],
        "handoff": [
            ("01", "Toma tu recurso", "Entra al puesto de recursos por guardiana y recibe una tarea, una guía y una ruta de libro.", "resources"),
            ("02", "Escribe 7 días", "Traduce la emoción en una petición pequeña y una acción posible, no solo en una etiqueta.", "repair-plan"),
            ("03", "Guarda tu guardiana", "Conserva la tarjeta para encontrar rápido tu puerta cuando vuelvas.", "keepsakes"),
            ("04", "Enfría por la noche", "Usa Luna antes de dormir o después de un conflicto, y vuelve al plan de reparación.", "luna-yoga-music"),
        ],
        "trust_routes": [
            ("Sobre el Jardín", "Entiende el universo LoveTypes, sus límites y mejores usos.", "about"),
            ("Teoría de lenguajes", "Vuelve al marco de comunicación detrás de los cinco lenguajes.", "theory"),
            ("Contacto y reparación", "Reporta errores, colaboraciones, permisos de recursos o páginas por corregir.", "contact"),
            ("Privacidad y términos", "Revisa datos, afiliados, límites de contenido y condiciones de uso.", "privacy"),
        ],
    },
}


def home_journey_section(lang: str) -> str:
    copy = HOME_JOURNEY[lang]
    cards = []
    for number, title, desc, action, target in copy["steps"]:
        href = target if target.startswith("#") else lang_url(lang, target)
        cards.append(f"""
<article class="home-journey-card">
  <span>{escape(number)}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
  <a href="{href}">{escape(action)}</a>
</article>
""")
    return f"""
<section class="section home-journey-section" data-home-journey>
  <div class="section-head"><div><p class="eyebrow">{escape(copy["eyebrow"])}</p><h2>{escape(copy["title"])}</h2></div><a href="{lang_url(lang, "garden-map")}">{escape(GARDEN_MAP[lang]["title"])}</a></div>
  <p class="section-intro">{escape(copy["intro"])}</p>
  <div class="home-journey-grid">{"".join(cards)}</div>
</section>
"""


def universe_gate_section(lang: str) -> str:
    title, intro, _map_title, _map_intro = UNIVERSE_COPY[lang]
    section_labels = SECTION_LABELS[lang]
    cards = []
    for slug, guardian in GUARDIANS.items():
        name, typ, _desc = guardian[lang]
        domain_title, domain_desc, domain_cta = GUARDIAN_DOMAINS[slug][lang]
        domain = GUARDIAN_DOMAINS[slug]
        prop = img_tag(guardian["prop"], f"{name} {domain_title}", "universe-gate-prop")
        cards.append(f"""
<a class="universe-gate-card" href="{lang_url(lang, "characters/" + slug)}" data-guardian-domain="{slug}" style="--domain-accent:{domain["accent"]};--domain-glow:{domain["glow"]}">
  <div class="universe-gate-art">{prop}</div>
  <div class="universe-gate-copy">
    <span>{escape(typ)}</span>
    <strong>{escape(domain_title)}</strong>
    <p>{escape(domain_desc)}</p>
  </div>
  <small>{escape(domain_cta)} · {escape(name)}</small>
</a>
""")
    return f"""
<section class="section universe-gates" data-universe-gates>
  <div class="section-head"><div><p class="eyebrow">{escape(section_labels["heart_garden_portals"])}</p><h2>{escape(title)}</h2></div><a href="{lang_url(lang, "characters")}">{escape(LANGS[lang]["guardians"])}</a></div>
  <p class="section-intro">{escape(intro)}</p>
  <div class="universe-gate-grid">{"".join(cards)}</div>
</section>
"""


def universe_map_section(lang: str) -> str:
    _title, _intro, map_title, map_intro = UNIVERSE_COPY[lang]
    section_labels = SECTION_LABELS[lang]
    cards = "".join(character_card(lang, slug, data) for slug, data in GUARDIANS.items())
    return f"""
<section class="section universe-map-section" id="guardian-map" data-universe-map>
  <div class="section-head"><div><p class="eyebrow">{escape(section_labels["heart_garden_map"])}</p><h2>{escape(map_title)}</h2></div><a href="{lang_url(lang, "resources")}">{escape(LANGS[lang]["resources"])}</a></div>
  <p class="section-intro">{escape(map_intro)}</p>
  <div class="guardian-grid universe-map-grid">{cards}</div>
</section>
"""


def garden_map_page(lang: str) -> None:
    t = LANGS[lang]
    copy = GARDEN_MAP[lang]
    section_labels = SECTION_LABELS[lang]

    def map_href(target: str) -> str:
        return lang_url(lang) + target if target.startswith("#") else lang_url(lang, target)

    def abs_map_href(target: str) -> str:
        return abs_url(lang) + target if target.startswith("#") else abs_url(lang, target)

    route_cards = "".join(f"""
<a class="garden-map-route-card" href="{map_href(target)}">
  <span>{escape(action)}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
</a>
""" for title, desc, action, target in copy["routes"])

    handoff_cards = "".join(f"""
<a class="garden-map-handoff-card" href="{lang_url(lang, target)}">
  <span>{escape(number)}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
</a>
""" for number, title, desc, target in copy["handoff"])

    tool_cards = "".join(f"""
<a class="garden-map-tool-card" href="{lang_url(lang, target)}">
  <span>{escape(action)}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
</a>
""" for title, desc, action, target in copy["tools"])

    guardian_cards = "".join(character_card(lang, slug, data) for slug, data in GUARDIANS.items())
    guide_cards = "".join(guide_card(lang, guide) for guide in GUIDES)

    trust_cards = "".join(f"""
<a class="garden-map-trust-card" href="{lang_url(lang, path)}">
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
</a>
""" for title, desc, path in copy["trust_routes"])

    body = f"""
<section class="page-hero compact garden-map-hero">
  <p class="eyebrow">{escape(copy["eyebrow"])}</p>
  <h1>{escape(copy["title"])}</h1>
  <p>{escape(copy["intro"])}</p>
  <div class="hero-actions"><a class="primary-btn" href="{lang_url(lang)}#quiz-section">{escape(t["start"])}</a><a class="secondary-btn" href="{lang_url(lang, "characters")}">{escape(t["guardians"])}</a></div>
</section>
<section class="section garden-map-result-resume" data-garden-map-saved hidden aria-live="polite"></section>
<section class="section garden-map-handoff" data-garden-map-handoff>
  <div class="section-head"><div><p class="eyebrow">{escape(section_labels["after_ritual"])}</p><h2>{escape(copy["handoff_title"])}</h2></div><a href="{lang_url(lang, "resources")}">{escape(t["resources"])}</a></div>
  <p class="section-intro">{escape(copy["handoff_intro"])}</p>
  <div class="garden-map-handoff-grid">{handoff_cards}</div>
</section>
<section class="section garden-map-routes" data-garden-map-routes>
  <div class="section-head"><div><p class="eyebrow">{escape(section_labels["main_routes"])}</p><h2>{escape(copy["routes_title"])}</h2></div></div>
  <div class="garden-map-route-grid">{route_cards}</div>
</section>
<section class="section garden-map-tools" data-garden-map-tools>
  <div class="section-head"><div><p class="eyebrow">{escape(section_labels["function_rooms"])}</p><h2>{escape(copy["tools_title"])}</h2></div><a href="{lang_url(lang, "repair-plan")}">{escape(REPAIR_PLAN[lang]["title"])}</a></div>
  <div class="garden-map-tool-grid">{tool_cards}</div>
</section>
<section class="section garden-map-guardians" data-garden-map-guardians>
  <div class="section-head"><div><p class="eyebrow">{escape(section_labels["five_domains"])}</p><h2>{escape(copy["guardians_title"])}</h2></div><a href="{lang_url(lang, "characters")}">{escape(t["guardians"])}</a></div>
  <div class="guardian-grid compact">{guardian_cards}</div>
</section>
<section class="section garden-map-guides" data-garden-map-guides>
  <div class="section-head"><div><p class="eyebrow">{escape(section_labels["field_guides"])}</p><h2>{escape(copy["guides_title"])}</h2></div><a href="{lang_url(lang, "guides")}">{escape(t["guides"])}</a></div>
  <div class="card-grid">{guide_cards}</div>
</section>
<section class="section garden-map-trust" data-garden-map-trust>
  <div class="section-head"><div><p class="eyebrow">{escape(section_labels["trust_routes"])}</p><h2>{escape(copy["trust_title"])}</h2></div><a href="{lang_url(lang, "contact")}">{escape(t["contact"])}</a></div>
  <div class="garden-map-trust-grid">{trust_cards}</div>
</section>
<section class="section note-section"><h2>{escape(t["boundary"])}</h2><p>{escape(t["boundary_text"])}</p></section>
{garden_map_resume_script(lang)}
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"CollectionPage","name":"{escape(copy["title"])}","description":"{escape(copy["desc"])}","url":"{abs_url(lang, "garden-map")}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
    list_items = [(title, abs_map_href(target)) for title, _desc, _action, target in copy["routes"]]
    schema += item_list_schema(copy["routes_title"], copy["intro"], list_items)
    page_title = f"{copy['title']} | LoveTypes" if lang == "zh" else f"{copy['title']} | LoveTypes {t['name']}"
    write(page_path(lang, "garden-map"), layout(lang, page_title, copy["desc"], "garden-map", body, t["map"], "website", "/og-cover.jpg", schema))


def garden_map_resume_script(lang: str) -> str:
    copy = GARDEN_MAP[lang]
    resume_title = json.dumps(copy["resume_title"], ensure_ascii=False)
    resume_intro = json.dumps(copy["resume_intro"], ensure_ascii=False)
    return f"""
{quiz_data_script_tag(lang)}
<script>
(() => {{
  const quiz = window.__LOVETYPES_QUIZ_DATA;
  if (!quiz) return;
  const resumeTitle = {resume_title};
  const resumeIntro = {resume_intro};
  const box = document.querySelector('[data-garden-map-saved]');
  if (!box) return;
  const homePath = new URL(quiz.shareUrl).pathname;
  const storageKeys = ["lovetypes:{lang}:quiz-result", `lovetypes:${{homePath}}:quiz-result`];

  function readSavedResult() {{
    try {{
      for (const key of storageKeys) {{
        const saved = JSON.parse(localStorage.getItem(key) || 'null');
        const primaryKey = saved && (saved.primaryKey || saved.type);
        if (primaryKey && quiz.results[primaryKey]) return {{ ...saved, primaryKey }};
      }}
    }} catch (_error) {{}}
    return null;
  }}

  function clearSavedResult() {{
    storageKeys.forEach((key) => localStorage.removeItem(key));
    box.hidden = true;
    box.innerHTML = '';
  }}

  const saved = readSavedResult();
  if (!saved) return;
  const result = quiz.results[saved.primaryKey];
  box.innerHTML = `
    <article class="garden-map-resume-card pass-resume-card" id="map-${{result.slug}}" style="--result-accent:${{result.domainAccent || result.color}};--domain-glow:${{result.domainGlow || result.color}}">
      <img src="${{result.resultImage}}" alt="${{result.name}}" width="${{result.resultImageWidth}}" height="${{result.resultImageHeight}}" loading="lazy" decoding="async" fetchpriority="low">
      <div>
        <div class="resume-pass-stamp" data-resume-pass-stamp>
          <img class="resume-pass-prop" src="${{result.domainProp}}" alt="${{result.domainTitle}}" width="${{result.domainPropWidth}}" height="${{result.domainPropHeight}}" loading="lazy" decoding="async" fetchpriority="low">
          <span>${{quiz.labels.pass_title}}</span>
          <strong>${{result.domainTitle}}</strong>
        </div>
        <p class="eyebrow">${{resumeTitle}}</p>
        <h2>${{result.name}} · ${{result.type}}</h2>
        <p>${{resumeIntro}}</p>
        <p><strong>${{result.supplyTitle}}</strong> · ${{result.supplyMission}}</p>
        <div class="garden-map-resume-actions">
          <a class="primary-btn" href="${{result.resourceUrl}}" data-garden-map-route>${{quiz.labels.saved_route}}</a>
          <a class="secondary-btn" href="${{result.planUrl}}" data-garden-map-plan>${{quiz.labels.saved_plan}}</a>
          <a class="secondary-btn" href="${{result.lunaUrl}}" data-garden-map-luna>${{quiz.labels.saved_luna}}</a>
          <a class="secondary-btn" href="${{result.collectorHallUrl}}" data-garden-map-keepsake>${{quiz.labels.saved_card}}</a>
          <a class="secondary-btn" href="${{result.contactUrl}}" data-garden-map-contact>${{quiz.labels.saved_contact}}</a>
          <a class="secondary-btn" href="${{result.guardianUrl}}" data-garden-map-guardian>${{quiz.labels.guardian_link}}</a>
          <button class="secondary-btn" type="button" data-clear-garden-map-result>${{quiz.labels.saved_clear}}</button>
        </div>
      </div>
    </article>`;
  box.hidden = false;
  box.querySelector('[data-clear-garden-map-result]')?.addEventListener('click', clearSavedResult);
  if (location.hash === `#map-${{result.slug}}`) {{
    const focusResume = () => box.scrollIntoView({{ behavior: 'auto', block: 'start' }});
    window.requestAnimationFrame(focusResume);
    window.setTimeout(focusResume, 120);
    window.setTimeout(focusResume, 420);
  }}
}})();
</script>
"""


def supply_wishlist_section(lang: str) -> str:
    labels = SUPPLY_WISHLIST[lang]
    template_labels = CONTACT_TEMPLATE_LABELS[lang]
    cards = []
    for slug, data in GUARDIANS.items():
        route = supply_route(lang, slug)
        guardian_name, guardian_type, _guardian_desc = data[lang]
        accent = next(meta["color"] for meta in QUIZ_TYPES.values() if meta["slug"] == slug)
        format_items = "".join(f"<li>{escape(item)}</li>" for item in labels["formats"])
        subject = quote(labels["subject"])
        body_text = (
            f'{labels["body"]} {guardian_name} · {route["title"]}\n'
            f'{labels["format_label"]}: {", ".join(labels["formats"])}\n'
            f'{labels["body_context"]} \n\n'
        )
        body = quote(body_text)
        cards.append(f"""
<article class="supply-wishlist-card" data-supply-owned-card style="--route-accent:{accent}">
  {img_tag(data["prop"], route["title"])}
  <div>
    <p class="eyebrow">{escape(guardian_name)} · {escape(guardian_type)}</p>
    <h3>{escape(route["title"])}</h3>
    <p class="supply-wishlist-mission">{escape(route["mission"])}</p>
    <div class="supply-format-block">
      <span>{escape(labels["format_label"])}</span>
      <ul class="supply-format-list">{format_items}</ul>
    </div>
    <div class="supply-route-actions">
      <a class="supply-signal-link" href="mailto:contact@lovetypes.tw?subject={subject}&body={body}" data-funnel-event="supply_wishlist_mailto">{escape(labels["request"])}</a>
      <button class="secondary-btn" type="button" data-copy-contact-template data-funnel-event="supply_wishlist_copy" data-copy-text="{escape(body_text)}">{escape(template_labels["copy"])}</button>
    </div>
  </div>
</article>
""")
    return f"""
<section class="section supply-wishlist-section" data-supply-owned-signal>
  <div class="section-head"><div><p class="eyebrow">{escape(labels["eyebrow"])}</p><h2>{escape(labels["title"])}</h2></div><a href="{lang_url(lang, "contact")}">{escape(LANGS[lang]["contact"])}</a></div>
  <p class="section-intro">{escape(labels["intro"])}</p>
  <div class="supply-wishlist-grid">{"".join(cards)}</div>
  <p class="supply-wishlist-note">{escape(labels["note"])}</p>
</section>
{contact_template_copy_script(lang)}
"""


def starter_kit_section(lang: str) -> str:
    labels = STARTER_KIT[lang]
    cards = []
    for number, title, desc, action, target in labels["steps"]:
        href = target if target.startswith("#") else lang_url(lang, target)
        cards.append(f"""
<article class="starter-kit-card">
  <span>{escape(number)}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
  <a href="{href}">{escape(action)}</a>
</article>
""")
    return f"""
<section class="section starter-kit-section">
  <div class="section-head"><div><p class="eyebrow">{escape(labels["eyebrow"])}</p><h2>{escape(labels["title"])}</h2></div></div>
  <p class="section-intro">{escape(labels["intro"])}</p>
  <div class="starter-kit-grid">{"".join(cards)}</div>
</section>
"""


def guardian_story_image(lang: str, slug: str) -> str:
    return f"/assets/lovetypes/share/{slug}-story-{lang}.webp"


def guardian_story_cta(lang: str, slug: str) -> str:
    return "lovetypes.tw" + lang_url(lang, "keepsakes").rstrip("/") + f"/#keepsake-{slug}"


def guardian_result_image(slug: str, fallback: str) -> str:
    return fallback


def starter_kit_payload(lang: str, supply_url: str = "#supply-routes") -> dict:
    labels = STARTER_KIT[lang]
    steps = []
    for number, title, desc, action, target in labels["steps"]:
        href = supply_url if target.startswith("#") else lang_url(lang, target)
        steps.append({
            "number": number,
            "title": title,
            "desc": desc,
            "action": action,
            "href": href,
        })
    return {
        "eyebrow": labels["eyebrow"],
        "title": labels["title"],
        "intro": labels["intro"],
        "steps": steps,
    }


def collector_card(lang: str, slug: str, compact: bool = False) -> str:
    labels = COLLECTOR_LABELS[lang]
    guardian = GUARDIANS[slug]
    route = supply_route(lang, slug)
    name, typ, _desc = guardian[lang]
    class_name = "collector-card compact" if compact else "collector-card"
    image = guardian_story_image(lang, slug)
    image_label = f"{labels['open']}：{name} {labels['card']}"
    route_href = f"{lang_url(lang, 'resources')}#supply-{slug}"
    plan_href = f"{lang_url(lang, 'repair-plan')}#plan-{slug}"
    story_cta = guardian_story_cta(lang, slug)
    data_attrs = (
        f'data-story-name="{escape(name)}" '
        f'data-story-title="{escape(typ)}" '
        f'data-story-quote="{escape(route["mission"])}" '
        f'data-story-image="{escape(guardian["asset"])}" '
        f'data-story-slug="{escape(slug)}" '
        f'data-story-kicker="{escape(labels["story_kicker"])}" '
        f'data-story-cta="{escape(story_cta)}" '
        f'data-story-error="{escape(labels["story_error"])}"'
    )
    return f"""
<span id="keepsake-{slug}" class="anchor-offset" aria-hidden="true"></span>
<article class="{class_name}" id="keepsake-card-{slug}">
  <a class="collector-image-link" href="{image}" target="_blank" rel="noopener noreferrer" aria-label="{escape(image_label)}">
    {img_tag(image, f"{name} {labels['card']}")}
  </a>
  <div>
    <p class="eyebrow">{escape(typ)}</p>
    <h3>{escape(name)}</h3>
    <p>{escape(route["desc"])}</p>
    <div class="collector-actions">
      <a class="primary-btn" href="{route_href}">{escape(labels["route"])}</a>
      <a class="secondary-btn" href="{plan_href}">{escape(labels["plan"])}</a>
      <a class="secondary-btn" href="{lang_url(lang, "keepsakes")}#practice-card-{slug}" data-funnel-event="collector_practice_card">{escape(KEEPSAKES_PAGE[lang]["practice_open"])}</a>
      <a class="secondary-btn" href="{image}" target="_blank" rel="noopener noreferrer">{escape(labels["open"])}</a>
      <a class="secondary-btn" href="{image}" download>{escape(labels["download"])}</a>
      <a class="secondary-btn" href="{supply_request_href(lang, slug)}" data-funnel-event="collector_supply_mailto">{escape(SUPPLY_LABELS[lang]["request_supply"])}</a>
      <button class="secondary-btn" type="button" data-result-action="story" data-funnel-event="keepsake_story_generate" {data_attrs}>{escape(labels["story"])}</button>
    </div>
  </div>
</article>
"""


def collector_section(lang: str, current_slug: str = "") -> str:
    labels = COLLECTOR_LABELS[lang]
    slugs = [current_slug] if current_slug else list(GUARDIANS.keys())
    cards = "".join(collector_card(lang, slug, compact=bool(current_slug)) for slug in slugs)
    route_link = f"{lang_url(lang, 'resources')}#supply-{current_slug}" if current_slug else lang_url(lang, "resources")
    return f"""
<section class="section collector-section">
  <div class="section-head">
    <div><p class="eyebrow">{escape(labels["eyebrow"])}</p><h2>{escape(labels["title"])}</h2></div>
    <a href="{route_link}">{escape(labels["route"])}</a>
  </div>
  <p class="section-intro">{escape(labels["intro"])} {escape(labels["share_hint"])}</p>
  <div class="collector-grid">{cards}</div>
</section>
"""


def keepsake_shelf_section(lang: str) -> str:
    labels = COLLECTOR_LABELS[lang]
    cards = []
    for slug, guardian in GUARDIANS.items():
        name, typ, _desc = guardian[lang]
        domain = GUARDIAN_DOMAINS[slug]
        image = guardian_story_image(lang, slug)
        cards.append(f"""
<a class="keepsake-shelf-card" href="#keepsake-card-{slug}" data-guardian-domain="{slug}" style="--domain-accent:{domain["accent"]};--domain-glow:{domain["glow"]}">
  {img_tag(image, f"{name} {labels['card']}", "keepsake-shelf-image")}
  <span>{escape(typ)}</span>
  <strong>{escape(name)}</strong>
</a>
""")
    return f"""
<section class="section keepsake-shelf-section" data-keepsake-shelf>
  <div class="keepsake-shelf-grid">{"".join(cards)}</div>
</section>
"""


def keepsake_ritual_section(lang: str) -> str:
    labels = KEEPSAKE_RITUAL[lang]
    cards = []
    for idx, (title, desc, action, target) in enumerate(labels["steps"], start=1):
        href = target if target.startswith("#") else lang_url(lang, target)
        cards.append(f"""
<article class="keepsake-ritual-card">
  <span>{idx}</span>
  <div>
    <h3>{escape(title)}</h3>
    <p>{escape(desc)}</p>
    <a href="{href}">{escape(action)}</a>
  </div>
</article>
""")
    return f"""
<section class="section keepsake-ritual-section" data-keepsake-ritual>
  <div class="section-head">
    <div>
      <p class="eyebrow">{escape(labels["eyebrow"])}</p>
      <h2>{escape(labels["title"])}</h2>
    </div>
  </div>
  <p class="section-intro">{escape(labels["intro"])}</p>
  <div class="keepsake-ritual-grid">{"".join(cards)}</div>
</section>
"""


def contact_template_copy_script(lang: str) -> str:
    copied = json.dumps(CONTACT_TEMPLATE_LABELS[lang]["copied"], ensure_ascii=False)
    return f"""
<script>
(() => {{
  const copied = {copied};
  document.querySelectorAll('[data-copy-contact-template]').forEach((button) => {{
    const original = button.textContent;
    button.addEventListener('click', async () => {{
      const text = button.getAttribute('data-copy-text') || '';
      try {{
        if (navigator.clipboard?.writeText && window.isSecureContext) {{
          await navigator.clipboard.writeText(text);
        }} else {{
          const area = document.createElement('textarea');
          area.value = text;
          area.setAttribute('readonly', '');
          area.style.position = 'fixed';
          area.style.left = '-9999px';
          document.body.appendChild(area);
          area.select();
          document.execCommand('copy');
          area.remove();
        }}
        button.textContent = copied;
        window.setTimeout(() => button.textContent = original, 1600);
      }} catch (_error) {{
        window.prompt(original, text);
      }}
    }});
  }});
}})();
</script>
"""


def contact_result_handoff_script(lang: str) -> str:
    labels = json.dumps(CONTACT_RESULT_HANDOFF[lang], ensure_ascii=False)
    return f"""
{quiz_data_script_tag(lang)}
<script>
(() => {{
  const quiz = window.__LOVETYPES_QUIZ_DATA;
  const labels = {labels};
  const box = document.querySelector('[data-contact-saved]');
  if (!quiz || !box) return;
  const homePath = new URL(quiz.shareUrl).pathname;
  const storageKeys = ["lovetypes:{lang}:quiz-result", `lovetypes:${{location.pathname}}:quiz-result`, `lovetypes:${{homePath}}:quiz-result`];

  function readSavedResult() {{
    try {{
      for (const key of storageKeys) {{
        const saved = JSON.parse(localStorage.getItem(key) || 'null');
        const primaryKey = saved && (saved.primaryKey || saved.type);
        if (primaryKey && quiz.results[primaryKey]) return {{ ...saved, primaryKey }};
      }}
    }} catch (_error) {{}}
    return null;
  }}

  function clearSavedResult() {{
    storageKeys.forEach((key) => localStorage.removeItem(key));
    box.hidden = true;
    box.innerHTML = '';
  }}

  async function copyText(text, button) {{
    const original = button.textContent;
    try {{
      if (navigator.clipboard?.writeText && window.isSecureContext) {{
        await navigator.clipboard.writeText(text);
      }} else {{
        const area = document.createElement('textarea');
        area.value = text;
        area.setAttribute('readonly', '');
        area.style.position = 'fixed';
        area.style.left = '-9999px';
        document.body.appendChild(area);
        area.select();
        document.execCommand('copy');
        area.remove();
      }}
      button.textContent = labels.copied;
      window.setTimeout(() => button.textContent = original, 1600);
    }} catch (_error) {{
      window.prompt(labels.copy, text);
    }}
  }}

  const saved = readSavedResult();
  if (!saved) return;
  const result = quiz.results[saved.primaryKey];
  const body = [
    `${{labels.guardian}}: ${{result.name}} · ${{result.type}}`,
    `${{labels.supply}}: ${{result.supplyTitle}}`,
    `${{labels.mission}}: ${{result.supplyMission}}`,
    `${{labels.luna}}: ${{result.lunaUrl}}`,
    `${{labels.keepsake}}: ${{labels.keepsake_hint}}`,
    `${{labels.context}}: `,
    '',
    `${{labels.route}}: ${{result.resourceUrl}}`,
    `${{labels.card}}: ${{result.collectorHallUrl}}`,
    `${{labels.plan}}: ${{result.planUrl}}`
  ].join('\\n');
  const href = `mailto:contact@lovetypes.tw?subject=${{encodeURIComponent(labels.subject)}}&body=${{encodeURIComponent(body)}}`;
  box.innerHTML = `
    <article class="contact-result-card garden-map-resume-card pass-resume-card" id="contact-result-${{result.slug}}" style="--result-accent:${{result.domainAccent || result.color}};--domain-glow:${{result.domainGlow || result.color}}">
      <img src="${{result.resultImage}}" alt="${{result.name}}" width="${{result.resultImageWidth}}" height="${{result.resultImageHeight}}" loading="lazy" decoding="async" fetchpriority="low">
      <div>
        <div class="resume-pass-stamp" data-resume-pass-stamp>
          <img class="resume-pass-prop" src="${{result.domainProp}}" alt="${{result.domainTitle}}" width="${{result.domainPropWidth}}" height="${{result.domainPropHeight}}" loading="lazy" decoding="async" fetchpriority="low">
          <span>${{quiz.labels.pass_title}}</span>
          <strong>${{result.domainTitle}}</strong>
        </div>
        <p class="eyebrow">${{labels.eyebrow}}</p>
        <h2>${{result.name}} · ${{result.type}}</h2>
        <p>${{labels.intro}}</p>
        <p><strong>${{result.supplyTitle}}</strong> · ${{result.supplyMission}}</p>
        <div class="contact-result-actions garden-map-resume-actions">
          <a class="primary-btn" href="${{href}}" data-contact-resume-send>${{labels.send}}</a>
          <button class="secondary-btn" type="button" data-contact-copy-result data-contact-resume-copy>${{labels.copy}}</button>
          <a class="secondary-btn" href="${{result.resourceUrl}}" data-contact-resume-route>${{labels.route}}</a>
          <a class="secondary-btn" href="${{result.collectorHallUrl}}" data-contact-resume-keepsake>${{labels.card}}</a>
          <a class="secondary-btn" href="${{result.planUrl}}" data-contact-resume-plan>${{labels.plan}}</a>
          <button class="secondary-btn" type="button" data-clear-contact-result>${{labels.clear}}</button>
        </div>
      </div>
    </article>`;
  box.hidden = false;
  box.querySelector('[data-contact-copy-result]')?.addEventListener('click', (event) => copyText(body, event.currentTarget));
  box.querySelector('[data-clear-contact-result]')?.addEventListener('click', clearSavedResult);
}})();
</script>
"""


def keepsake_waitlist_section(lang: str) -> str:
    request = CONTACT_REQUESTS[lang]
    subject_label = CONTACT_SUBJECT_LABELS[lang]
    template_labels = CONTACT_TEMPLATE_LABELS[lang]
    request_subject = request["subject"]
    request_subject_href = quote(request_subject)
    request_body_href = quote(request["body"])
    request_cards = "".join(
        f"<article><span>{idx}</span><h3>{escape(title)}</h3><p>{escape(body)}</p></article>"
        for idx, (title, body) in enumerate(request["items"], 1)
    )
    return f"""
<section class="section contact-request-section keepsake-waitlist-section" id="keepsake-supply-waitlist" data-keepsake-waitlist>
  <div class="section-head"><div><p class="eyebrow">{escape(request["eyebrow"])}</p><h2>{escape(request["title"])}</h2></div><a href="{lang_url(lang, "contact")}#luna-supply-request">{escape(LANGS[lang]["contact"])}</a></div>
  <p class="section-intro">{escape(request["intro"])}</p>
  <div class="contact-request-grid">{request_cards}</div>
  <div class="contact-request-note">
    <p>{escape(request["note"])}</p>
    <p class="contact-request-subject"><strong>{escape(subject_label)}</strong><code>{escape(request_subject)}</code></p>
    <div class="contact-request-subject contact-request-template"><strong>{escape(template_labels["label"])}</strong><code>{escape(request["body"])}</code><button class="secondary-btn" type="button" data-copy-contact-template data-funnel-event="keepsake_waitlist_copy" data-copy-text="{escape(request["body"])}">{escape(template_labels["copy"])}</button></div>
    <a class="primary-btn" href="mailto:contact@lovetypes.tw?subject={request_subject_href}&body={request_body_href}" data-funnel-event="keepsake_waitlist_mailto">{escape(request["cta"])}</a>
  </div>
</section>
{contact_template_copy_script(lang)}
"""


def keepsake_free_asset_section(lang: str) -> str:
    labels = KEEPSAKES_PAGE[lang]
    format_items = "".join(f"<li>{escape(item)}</li>" for item in labels["asset_formats"])
    cards = []
    for slug, guardian in GUARDIANS.items():
        name, typ, _desc = guardian[lang]
        route = supply_route(lang, slug)
        domain = GUARDIAN_DOMAINS[slug]
        story_image = guardian_story_image(lang, slug)
        story_width, story_height = IMAGE_DIMENSIONS.get(story_image, ("", ""))
        cards.append(f"""
<article class="collector-card compact" id="free-keepsake-{slug}" data-free-keepsake-asset="{slug}" style="--domain-accent:{domain["accent"]};--domain-glow:{domain["glow"]}">
  <img src="{story_image}" alt="{escape(name)} {escape(labels["asset_formats"][0])}" width="{story_width}" height="{story_height}" loading="lazy" decoding="async" fetchpriority="low">
  <div>
    <p class="eyebrow">{escape(typ)}</p>
    <h3>{escape(name)} · {escape(route["title"])}</h3>
    <p>{escape(route["mission"])}</p>
    <ul class="keepsake-asset-format-list">{format_items}</ul>
    <div class="collector-actions">
      <a href="{story_image}" target="_blank" rel="noopener noreferrer">{escape(COLLECTOR_LABELS[lang]["open"])}</a>
      <a href="{story_image}" download>{escape(COLLECTOR_LABELS[lang]["download"])}</a>
      <a href="{lang_url(lang, "contact")}#luna-supply-request">{escape(labels["asset_request"])}</a>
    </div>
  </div>
</article>
""")
    return f"""
<section class="section keepsake-free-assets" data-free-keepsake-assets>
  <div class="section-head">
    <div><p class="eyebrow">{escape(SECTION_LABELS[lang]["guardian_keepsakes"])}</p><h2>{escape(labels["asset_title"])}</h2></div>
    <a href="{lang_url(lang, "contact")}#luna-supply-request">{escape(labels["asset_request"])}</a>
  </div>
  <p class="section-intro">{escape(labels["asset_intro"])}</p>
  <div class="collector-grid compact-grid">{"".join(cards)}</div>
</section>
"""


def keepsake_practice_card_section(lang: str) -> str:
    labels = KEEPSAKES_PAGE[lang]
    section_labels = SECTION_LABELS[lang]
    cards = []
    for slug, guardian in GUARDIANS.items():
        name, typ, _desc = guardian[lang]
        route = supply_route(lang, slug)
        domain = GUARDIAN_DOMAINS[slug]
        cards.append(f"""
<article class="collector-card compact" id="practice-card-{slug}" data-keepsake-practice-card="{slug}" style="--domain-accent:{domain["accent"]};--domain-glow:{domain["glow"]}">
  {img_tag(guardian["prop"], f"{name} {route['title']}", "domain-prop")}
  <div>
    <p class="eyebrow">{escape(typ)}</p>
    <h3>{escape(name)} · {escape(route["title"])}</h3>
    <p><strong>{escape(labels["practice_wound"])}</strong><br>{escape(route["wound"])}</p>
    <p><strong>{escape(labels["practice_mission"])}</strong><br>{escape(route["mission"])}</p>
    <p><strong>{escape(labels["practice_supply"])}</strong><br>{escape(route["supply"])}</p>
    <p><strong>{escape(labels["practice_blank"])}</strong><br>______________________________</p>
    <div class="collector-actions">
      <a class="primary-btn" href="{lang_url(lang, "repair-plan")}#plan-{slug}" data-funnel-event="practice_card_repair_plan">{escape(COLLECTOR_LABELS[lang]["plan"])}</a>
      <a class="secondary-btn" href="{lang_url(lang, "resources")}#supply-{slug}" data-funnel-event="practice_card_supply_route">{escape(COLLECTOR_LABELS[lang]["route"])}</a>
      <button class="secondary-btn" type="button" onclick="window.print()" data-funnel-event="practice_card_print">{escape(labels["practice_print"])}</button>
    </div>
  </div>
</article>
""")
    return f"""
<section class="section keepsake-practice-cards" data-keepsake-practice-cards>
  <div class="section-head">
    <div><p class="eyebrow">{escape(section_labels["printable_worksheet"])}</p><h2>{escape(labels["practice_title"])}</h2></div>
    <button class="secondary-btn print-button" type="button" onclick="window.print()">{escape(labels["practice_print"])}</button>
  </div>
  <p class="section-intro">{escape(labels["practice_intro"])}</p>
  <div class="collector-grid compact-grid">{"".join(cards)}</div>
</section>
"""


def keepsake_resume_script(lang: str) -> str:
    request_supply_label = json.dumps(SUPPLY_LABELS[lang]["request_supply"], ensure_ascii=False)
    contact_request_url = json.dumps(lang_url(lang, "contact") + "#luna-supply-request", ensure_ascii=False)
    return f"""
{quiz_data_script_tag(lang)}
<script>
(() => {{
  const quiz = window.__LOVETYPES_QUIZ_DATA;
  const requestSupplyLabel = {request_supply_label};
  const contactRequestUrl = {contact_request_url};
  if (!quiz) return;
  const box = document.querySelector('[data-keepsake-saved]');
  if (!box) return;
  const homePath = new URL(quiz.shareUrl).pathname;
  const storageKeys = ["lovetypes:{lang}:quiz-result", `lovetypes:${{location.pathname}}:quiz-result`, `lovetypes:${{homePath}}:quiz-result`];

  function readSavedResult() {{
    try {{
      for (const key of storageKeys) {{
        const saved = JSON.parse(localStorage.getItem(key) || 'null');
        const primaryKey = saved && (saved.primaryKey || saved.type);
        if (primaryKey && quiz.results[primaryKey]) return {{ ...saved, primaryKey }};
      }}
    }} catch (error) {{}}
    return null;
  }}

  function clearSavedResult() {{
    storageKeys.forEach((key) => localStorage.removeItem(key));
    box.hidden = true;
    box.innerHTML = '';
  }}

  const saved = readSavedResult();
  if (!saved) return;
  const result = quiz.results[saved.primaryKey];
  box.innerHTML = `
    <article class="keepsake-resume-card pass-resume-card" id="keepsake-resume-${{result.slug}}" style="--result-accent:${{result.domainAccent || result.color}};--domain-glow:${{result.domainGlow || result.color}}">
      <a class="keepsake-resume-image" href="${{result.storyImage}}" target="_blank" rel="noopener noreferrer" aria-label="${{result.collectorOpen}}：${{result.name}} ${{result.collectorTitle}}">
        <img src="${{result.storyImage}}" alt="${{result.collectorTitle}} ${{result.name}}" width="${{result.storyImageWidth}}" height="${{result.storyImageHeight}}" loading="eager" decoding="async" fetchpriority="high">
      </a>
      <div>
        <div class="resume-pass-stamp" data-resume-pass-stamp>
          <img class="resume-pass-prop" src="${{result.domainProp}}" alt="${{result.domainTitle}}" width="${{result.domainPropWidth}}" height="${{result.domainPropHeight}}" loading="lazy" decoding="async" fetchpriority="low">
          <span>${{quiz.labels.pass_title}}</span>
          <strong>${{result.domainTitle}}</strong>
        </div>
        <p class="eyebrow">${{result.collectorTitle}}</p>
        <h2>${{result.name}} · ${{result.type}}</h2>
        <p>${{result.collectorHint}}</p>
        <p><strong>${{result.supplyTitle}}</strong> · ${{result.supplyMission}}</p>
        <div class="keepsake-resume-actions">
          <a class="primary-btn" href="${{result.planUrl}}" data-keepsake-plan>${{quiz.labels.saved_plan}}</a>
          <a class="secondary-btn" href="${{result.contactUrl || contactRequestUrl}}" data-keepsake-contact>${{requestSupplyLabel}}</a>
          <a class="secondary-btn" href="${{result.lunaUrl}}" data-keepsake-luna>${{quiz.labels.saved_luna}}</a>
          <a class="secondary-btn" href="${{result.resourceUrl}}" data-keepsake-route>${{quiz.labels.saved_route}}</a>
          <a class="secondary-btn" href="${{result.guardianUrl}}" data-keepsake-guardian>${{quiz.labels.guardian_link}}</a>
          <a class="secondary-btn" href="#practice-card-${{result.slug}}" data-keepsake-practice data-funnel-event="keepsake_resume_practice_card">${{quiz.labels.saved_plan}}</a>
          <a class="secondary-btn" href="${{result.storyImage}}" target="_blank" rel="noopener noreferrer">${{result.collectorOpen}}</a>
          <a class="secondary-btn" href="${{result.storyImage}}" download>${{result.collectorSave}}</a>
          <button class="secondary-btn" type="button" data-result-action="story" data-funnel-event="keepsake_resume_story_generate" data-story-name="${{result.name}}" data-story-title="${{result.type}}" data-story-quote="${{result.supplyMission}}" data-story-image="${{result.resultImage}}" data-story-slug="${{result.slug}}" data-story-kicker="${{result.collectorStoryKicker}}" data-story-cta="${{result.collectorStoryCta}}" data-story-error="${{result.collectorStoryError}}">${{result.collectorStory}}</button>
          <a class="secondary-btn" href="${{result.collectorHallUrl}}" data-keepsake-keepsake>${{result.collectorHall}}</a>
          <button class="secondary-btn" type="button" data-clear-keepsake-result>${{quiz.labels.saved_clear}}</button>
        </div>
      </div>
    </article>`;
  box.hidden = false;
  box.querySelector('[data-clear-keepsake-result]').addEventListener('click', clearSavedResult);
  if (location.hash === `#keepsake-${{result.slug}}`) {{
    const focusResume = () => box.scrollIntoView({{ behavior: 'auto', block: 'start' }});
    window.requestAnimationFrame(focusResume);
    window.setTimeout(focusResume, 120);
    window.setTimeout(focusResume, 420);
  }}
}})();
</script>
"""


def keepsakes_page(lang: str) -> None:
    labels = KEEPSAKES_PAGE[lang]
    t = LANGS[lang]
    free_cards = "".join(f"""
<article>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
</article>
""" for title, desc in labels["free_items"])
    steps = "".join(f"""
<article>
  <span>{idx}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
</article>
""" for idx, (title, desc) in enumerate(labels["steps"], start=1))
    body = f"""
<section class="page-hero compact keepsake-hero">
  <p class="eyebrow">{escape(labels["eyebrow"])}</p>
  <h1>{escape(labels["title"])}</h1>
  <p>{escape(labels["intro"])}</p>
  <div class="hero-actions">
    <a class="primary-btn" href="{lang_url(lang)}#quiz-section">{escape(labels["quiz"])}</a>
    <a class="secondary-btn" href="{lang_url(lang, "resources")}">{escape(labels["resources"])}</a>
  </div>
</section>
<section class="section keepsake-personal-resume" data-keepsake-saved hidden aria-live="polite"></section>
<section class="section keepsake-free-section supply-panel-section">
  <div class="section-head"><div><p class="eyebrow">{escape(SECTION_LABELS[lang]["guardian_keepsakes"])}</p><h2>{escape(labels["free_title"])}</h2></div><a href="#keepsake-card-iris">{escape(COLLECTOR_LABELS[lang]["open"])}</a></div>
  <p class="section-intro">{escape(labels["free_intro"])}</p>
  <div class="supply-panel-grid">{free_cards}</div>
</section>
{keepsake_free_asset_section(lang)}
{keepsake_practice_card_section(lang)}
{keepsake_shelf_section(lang)}
{keepsake_ritual_section(lang)}
{keepsake_waitlist_section(lang)}
{collector_section(lang)}
<section class="section keepsake-use-section">
  <div class="section-head"><div><p class="eyebrow">{escape(SECTION_LABELS[lang]["keepsake_use_route"])}</p><h2>{escape(labels["how_title"])}</h2></div></div>
  <div class="keepsake-use-grid">{steps}</div>
</section>
<section class="section intro-grid keepsake-safety">
  <div><h2>{escape(labels["safety_title"])}</h2><p>{escape(labels["safety_text"])}</p></div>
  <div><h2>{escape(t["boundary"])}</h2><p>{escape(t["boundary_text"])}</p></div>
</section>
{keepsake_resume_script(lang)}
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"CollectionPage","name":"{escape(labels["title"])}","description":"{escape(labels["desc"])}","url":"{abs_url(lang, "keepsakes")}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
    page_title = f"{labels['title']} | LoveTypes" if lang == "zh" else f"{labels['title']} | LoveTypes {t['name']}"
    write(page_path(lang, "keepsakes"), layout(lang, page_title, labels["desc"], "keepsakes", body, t["resources"], "website", "/og-cover.jpg", schema))


def guardian_entry_section(lang: str) -> str:
    entry = GUARDIAN_ENTRY[lang]
    cards = []
    for number, (title, desc, action, target) in enumerate(entry["items"], start=1):
        if target.startswith("#"):
            href = target
        elif target:
            href = lang_url(lang, target)
        else:
            href = lang_url(lang) + "#quiz-section"
        cards.append(f"""
    <article>
      <span>{number}</span>
      <h3>{escape(title)}</h3>
      <p>{escape(desc)}</p>
      <a href="{href}">{escape(action)}</a>
    </article>
""")
    return f"""
<section class="section guide-index-compass guardian-entry-section" id="guardian-start">
  <div class="section-head">
    <div><p class="eyebrow">{escape(entry["eyebrow"])}</p><h2>{escape(entry["title"])}</h2></div>
    <a href="{lang_url(lang, "resources")}">{escape(LANGS[lang]["resources"])}</a>
  </div>
  <p class="section-intro">{escape(entry["intro"])}</p>
  <div class="guide-compass-grid guardian-entry-grid">{"".join(cards)}</div>
</section>
"""


def guardian_need_router_section(lang: str) -> str:
    copy = GUARDIAN_NEED_ROUTER[lang]
    cards = []
    for slug, guardian in GUARDIANS.items():
        name, typ, _desc = guardian[lang]
        domain = GUARDIAN_DOMAINS[slug]
        need, body_text = copy["items"][slug]
        cards.append(f"""
<article class="guardian-need-card" data-guardian-domain="{slug}" style="--domain-accent:{domain["accent"]};--domain-glow:{domain["glow"]}">
  {img_tag(guardian["prop"], f"{name} {need}", "guardian-need-prop")}
  <span>{escape(typ)}</span>
  <h3>{escape(need)}</h3>
  <p>{escape(body_text)}</p>
  <div>
    <a href="{lang_url(lang, "characters/" + slug)}">{escape(copy["open"])}：{escape(name)}</a>
    <a href="{lang_url(lang, "resources")}#supply-{slug}">{escape(copy["supply"])}</a>
  </div>
</article>
""")
    return f"""
<section class="section guardian-need-section" data-guardian-need-router>
  <div class="section-head">
    <div><p class="eyebrow">{escape(copy["eyebrow"])}</p><h2>{escape(copy["title"])}</h2></div>
    <a href="{lang_url(lang)}#quiz-section">{escape(LANGS[lang]["start"])}</a>
  </div>
  <p class="section-intro">{escape(copy["intro"])}</p>
  <div class="guardian-need-grid">{"".join(cards)}</div>
</section>
"""


def guide_index_compass(lang: str) -> str:
    compass = GUIDE_INDEX_COMPASS[lang]
    cards = []
    for number, title, desc, action, target in compass["steps"]:
        href = f"{lang_url(lang)}#quiz-section" if not target else lang_url(lang, target)
        cards.append(f"""
    <article>
      <span>{escape(number)}</span>
      <h3>{escape(title)}</h3>
      <p>{escape(desc)}</p>
      <a href="{href}">{escape(action)}</a>
    </article>
""")
    return f"""
<section class="section guide-index-compass">
  <div class="section-head">
    <div><p class="eyebrow">{escape(compass["eyebrow"])}</p><h2>{escape(compass["title"])}</h2></div>
    <a href="{lang_url(lang, "resources")}">{escape(LANGS[lang]["resources"])}</a>
  </div>
  <p class="section-intro">{escape(compass["intro"])}</p>
  <div class="guide-compass-grid">{"".join(cards)}</div>
</section>
"""


def guide_domain_routes_section(lang: str) -> str:
    copy = GUIDE_DOMAIN_ROUTES[lang]
    cards = []
    for slug, guardian in GUARDIANS.items():
        route = supply_route(lang, slug)
        guide = route["guide"]
        name, typ, _desc = guardian[lang]
        guide_title, guide_desc = guide[lang]
        domain = GUARDIAN_DOMAINS[slug]
        cards.append(f"""
<article class="guide-domain-card" data-guardian-domain="{slug}" style="--domain-accent:{domain["accent"]};--domain-glow:{domain["glow"]}">
  {img_tag(guardian["prop"], f"{name} {guide_title}", "guide-domain-prop")}
  <span>{escape(name)} · {escape(typ)}</span>
  <h3>{escape(guide_title)}</h3>
  <p>{escape(guide_desc)}</p>
  <dl>
    <div><dt>{escape(copy["practice"])}</dt><dd>{escape(route["mission"])}</dd></div>
  </dl>
  <div class="guide-domain-actions">
    <a href="{lang_url(lang, "guides/" + guide["slug"])}">{escape(copy["read"])}</a>
    <a href="{lang_url(lang, "characters/" + slug)}">{escape(copy["guardian"])}</a>
    <a href="{lang_url(lang, "resources")}#supply-{slug}">{escape(copy["supply"])}</a>
  </div>
</article>
""")
    return f"""
<section class="section guide-domain-section" data-guide-domain-routes>
  <div class="section-head">
    <div><p class="eyebrow">{escape(copy["eyebrow"])}</p><h2>{escape(copy["title"])}</h2></div>
    <a href="{lang_url(lang, "characters")}">{escape(LANGS[lang]["guardians"])}</a>
  </div>
  <p class="section-intro">{escape(copy["intro"])}</p>
  <div class="guide-domain-grid">{"".join(cards)}</div>
</section>
"""


def character_supply_panel(lang: str, slug: str) -> str:
    labels = SUPPLY_LABELS[lang]
    route = supply_route(lang, slug)
    guide = route["guide"]
    book = route["book"]
    return f"""
<section class="section supply-panel-section">
  <div class="section-head">
    <div><p class="eyebrow">{escape(route["title"])}</p><h2>{escape(labels["deeper_route"])}</h2></div>
    <a href="{lang_url(lang, "resources")}#supply-{slug}">{escape(LANGS[lang]["resources"])}</a>
  </div>
  <p class="section-intro">{escape(route["desc"])}</p>
  <div class="supply-panel-grid">
    <article><span>{escape(labels["fit_supply"])}</span><h3>{escape(book["title"][lang])}</h3><p>{escape(route["supply"])}</p></article>
    <article><span>{escape(labels["wound"])}</span><h3>{escape(labels["wound"])}</h3><p>{escape(route["wound"])}</p></article>
    <article><span>{escape(labels["repair"])}</span><h3>{escape(labels["practice"])}</h3><p>{escape(route["mission"])}</p></article>
  </div>
  <div class="supply-panel-actions">
    <a class="primary-btn" href="{lang_url(lang, "resources")}#supply-{slug}">{escape(labels["route"])}</a>
    <a class="secondary-btn" href="{lang_url(lang, "guides/" + guide["slug"])}">{escape(labels["read_guide"])}</a>
    <a class="secondary-btn" href="{lang_url(lang, "luna-yoga-music")}#luna-{slug}">{escape(labels["open_luna"])}</a>
    <a class="secondary-btn" href="{book["url"]}" target="_blank" rel="noopener noreferrer sponsored">{escape(AFFILIATE_COPY[lang]["button"])}</a>
  </div>
  <p class="affiliate-disclosure">{escape(AFFILIATE_DISCLOSURE[lang])}</p>
</section>
"""


def character_route_snapshot(lang: str, slug: str) -> str:
    labels = SUPPLY_LABELS[lang]
    collector = COLLECTOR_LABELS[lang]
    route = supply_route(lang, slug)
    guide = route["guide"]
    book = route["book"]
    guardian_name, guardian_type, _guardian_desc = route["guardian"][lang]
    guide_title, guide_desc = guide[lang]
    intro_joiner = "。" if lang == "zh" else ". "
    return f"""
<section class="section guardian-route-snapshot">
  <div class="section-head">
    <div><p class="eyebrow">{escape(route["title"])}</p><h2>{escape(labels["quick_route"])}</h2></div>
    <a href="{lang_url(lang, "resources")}#supply-{slug}">{escape(labels["fit_supply"])}</a>
  </div>
  <p class="section-intro">{escape(guardian_name)} · {escape(guardian_type)}{intro_joiner}{escape(route["desc"])}</p>
  <div class="guardian-route-grid">
    <article>
      <span>{escape(labels["guide"])}</span>
      <h3>{escape(guide_title)}</h3>
      <p>{escape(guide_desc)}</p>
      <a href="{lang_url(lang, "guides/" + guide["slug"])}">{escape(labels["read_guide"])}</a>
    </article>
    <article>
      <span>{escape(labels["repair"])}</span>
      <h3>{escape(REPAIR_PLAN[lang]["title"])}</h3>
      <p>{escape(route["mission"])}</p>
      <a href="{lang_url(lang, "repair-plan")}#plan-{slug}">{escape(REPAIR_PLAN[lang]["title"])}</a>
    </article>
    <article>
      <span>{escape(labels["supply"])}</span>
      <h3>{escape(book["title"][lang])}</h3>
      <p>{escape(route["supply"])}</p>
      <a href="{lang_url(lang, "resources")}#supply-{slug}">{escape(labels["route"])}</a>
    </article>
    <article>
      <span>{escape(collector["eyebrow"])}</span>
      <h3>{escape(labels["free_keepsake"])}</h3>
      <p>{escape(collector["share_hint"])}</p>
      <a href="{lang_url(lang, "keepsakes")}#keepsake-{slug}">{escape(collector["open"])}</a>
      <a href="{supply_request_href(lang, slug)}">{escape(labels["request_supply"])}</a>
    </article>
  </div>
</section>
"""


def guide_detail_copy(lang: str, title: str, desc: str, guardian: tuple[str, str, str]) -> dict:
    name, typ, guardian_desc = guardian
    templates = {
        "zh": {
            "lede": "{title} 不是一篇通用提醒，而是把「{desc}」放進 {name} 的守護視角：先辨認這種愛之語在哪裡錯頻，再把它翻成對方能接住的一步。",
            "why": "當主題來到「{title}」時，重點不是證明誰比較用心，而是看見 {typ} 如何在日常裡被聽見、被忽略，或被誤解。{guardian_desc}",
            "notice": "閱讀這頁時，先找一個最近發生的場景：哪一句話、哪一段時間、哪個行動或哪種靠近，讓「{desc}」變得特別明顯？",
            "practice": "今天只為「{title}」設計一個小練習：把需求說成一句可執行請求，再把完成時間縮到二十四小時內，讓修復不必等到情緒耗盡。",
            "mistakes": "不要把「{title}」當成要求對方立刻改變的證據。它比較像一張地圖，提醒你在 {name} 守護的入口前，把感受、界線與請求分開說清楚。",
            "scripts": ["我想談的不是對錯，而是「{desc}」這件事對我代表什麼。", "如果我們只修「{title}」裡的一小步，我希望先從這個可做到的行動開始。", "我需要你理解的不是標籤，而是 {name} 守護的這個情境裡，我怎麼接收愛。"],
            "reflection": ["「{title}」提到的情境，最像我最近哪一次錯頻？", "面對「{desc}」，我希望對方具體做什麼，而不是只猜我的感受？", "如果我用 {typ} 的語言表達，請求會不會更清楚？"],
        },
        "en": {
            "lede": "{title} is not a generic reminder. It places \"{desc}\" inside {name}'s guardian lens so you can name where this love language misses and translate it into one receivable step.",
            "why": "When the topic is {title}, the point is not proving who cares more. It is seeing how {typ} is heard, missed, or misunderstood in daily life. {guardian_desc}",
            "notice": "As you read, choose one recent scene: which word, stretch of time, action, keepsake, or kind of closeness made \"{desc}\" feel especially visible?",
            "practice": "Design one small practice for {title} today. Turn the need into a request someone can act on, then keep the timeframe within twenty-four hours.",
            "mistakes": "Do not use {title} as evidence that someone must immediately change. Treat it as a map for separating feeling, boundary, and request at {name}'s doorway.",
            "scripts": ["I am not trying to decide who is right; I want to explain what \"{desc}\" means to me.", "If we repair only one small step in {title}, I would like to begin with this doable action.", "I need you to understand the {name} situation, not just the label."],
            "reflection": ["Which recent misfrequency looks most like {title}?", "For \"{desc}\", what do I want the other person to do specifically instead of guessing my feelings?", "Would the request become clearer if I used the language of {typ}?"],
        },
        "ja": {
            "lede": "「{title}」は一般的な注意書きではありません。「{desc}」を {name} の守護者視点に置き、この愛の言語がどこですれ違い、どの一歩なら届くかを見ます。",
            "why": "「{title}」で大切なのは、誰がより頑張ったかを証明することではありません。{typ} が日常でどう届き、見落とされ、誤解されるかを見ることです。{guardian_desc}",
            "notice": "読みながら最近の場面を一つ選びます。どの言葉、時間、行動、記憶、近さが「{desc}」をはっきりさせましたか。",
            "practice": "今日は「{title}」のために小さな練習を一つだけ作ります。ニーズを実行できるお願いに変え、二十四時間以内に試せる形へ縮めます。",
            "mistakes": "「{title}」を、相手がすぐ変わるべき証拠として使わないでください。{name} の入口で、感情、境界線、お願いを分ける地図として使います。",
            "scripts": ["正しさを決めたいのではなく、「{desc}」が私にとって何を意味するかを話したい。", "「{title}」で一つだけ修復するなら、まずこの小さな行動から始めたい。", "理解してほしいのはラベルではなく、{name} が守るこの場面で私がどう愛を受け取るかです。"],
            "reflection": ["「{title}」の場面は、最近のどのすれ違いに近いか。", "「{desc}」について、相手に察してほしいのではなく具体的に何をしてほしいか。", "{typ} の言語で言えば、お願いはもっと明確になるか。"],
        },
        "ko": {
            "lede": "{title}은 일반적인 조언이 아닙니다. \"{desc}\"를 {name}의 수호자 관점에 놓고, 이 사랑의 언어가 어디에서 어긋나는지와 어떤 한 걸음이면 받을 수 있는지 봅니다.",
            "why": "{title}에서 중요한 것은 누가 더 애썼는지 증명하는 일이 아닙니다. {typ}이 일상에서 어떻게 들리고, 놓치고, 오해되는지 보는 것입니다. {guardian_desc}",
            "notice": "읽으면서 최근 장면 하나를 고르세요. 어떤 말, 시간, 행동, 기억, 가까움이 \"{desc}\"를 특히 분명하게 만들었나요?",
            "practice": "오늘은 {title}을 위한 작은 연습 하나만 설계하세요. 욕구를 실행 가능한 요청으로 바꾸고, 24시간 안에 해볼 수 있을 만큼 작게 줄입니다.",
            "mistakes": "{title}을 상대가 즉시 바뀌어야 한다는 증거로 쓰지 마세요. {name}의 입구에서 감정, 경계, 요청을 나누는 지도로 사용하세요.",
            "scripts": ["옳고 그름을 가리려는 게 아니라 \"{desc}\"가 나에게 무엇을 의미하는지 말하고 싶어.", "{title}에서 한 걸음만 회복한다면 이 작은 행동부터 시작하고 싶어.", "내가 이해받고 싶은 것은 라벨이 아니라 {name}가 지키는 이 상황에서 사랑을 받는 방식이야."],
            "reflection": ["{title}의 장면은 최근 어떤 어긋남과 가장 닮았나?", "\"{desc}\"에 대해 상대가 추측하기보다 구체적으로 무엇을 해 주길 바라나?", "{typ}의 언어로 말하면 요청이 더 분명해질까?"],
        },
        "es": {
            "lede": "{title} no es un recordatorio genérico. Coloca \"{desc}\" dentro de la mirada de {name} para nombrar dónde se desajusta este lenguaje y traducirlo en un paso que sí pueda recibirse.",
            "why": "Cuando el tema es {title}, no se trata de probar quién cuida más. Se trata de ver cómo {typ} se escucha, se pierde o se malinterpreta en la vida diaria. {guardian_desc}",
            "notice": "Mientras lees, elige una escena reciente: ¿qué palabra, tiempo, acción, recuerdo o cercanía hizo que \"{desc}\" se volviera especialmente visible?",
            "practice": "Diseña hoy una práctica pequeña para {title}. Convierte la necesidad en una petición posible y mantén el plazo dentro de veinticuatro horas.",
            "mistakes": "No uses {title} como prueba de que alguien debe cambiar de inmediato. Úsalo como mapa para separar emoción, límite y petición en la puerta de {name}.",
            "scripts": ["No quiero decidir quién tiene razón; quiero explicar qué significa para mí \"{desc}\".", "Si reparamos solo un paso pequeño de {title}, me gustaría empezar con esta acción posible.", "Necesito que entiendas la situación de {name}, no solo la etiqueta."],
            "reflection": ["¿Qué desajuste reciente se parece más a {title}?", "Para \"{desc}\", ¿qué quiero que la otra persona haga concretamente en lugar de adivinar mis emociones?", "¿La petición sería más clara si uso el lenguaje de {typ}?"],
        },
    }
    raw = templates[lang]
    values = {"title": title, "desc": desc, "name": name, "typ": typ, "guardian_desc": guardian_desc}
    return {key: [item.format(**values) for item in value] if isinstance(value, list) else value.format(**values) for key, value in raw.items()}


def character_detail_copy(lang: str, name: str, typ: str, desc: str) -> dict:
    templates = {
        "zh": {
            "how": "{name} 的頁面聚焦在 {typ} 如何讓人感到被愛。當這個入口被忽略時，受傷常不是來自大事件，而是來自那些沒有被說清楚、沒有被留下、或沒有被安全接住的細節。",
            "need": "{name} 守護的不是任性要求，而是一種希望被理解的接收方式。你可以用這頁辨認：我需要被看見的是什麼、我害怕哪種錯頻、哪個小行動最能讓我安心。",
            "practice": "今天用 {name} 的方式練習一次：先說出感受，再說出 {typ} 的需求，最後只提出一個對方能做到的小請求。",
            "scripts": ["我想用 {typ} 的語言說清楚這件事。", "對我來說，這不是小題大作，而是我接收愛的入口。", "如果你願意，我希望先從一個小行動開始。"],
            "reflection": ["我最近一次沒有被接住，是不是和 {typ} 有關？", "{name} 的提醒能不能幫我把要求縮小成可執行的一步？", "我有沒有把需要說成指責，而不是請求？"],
        },
        "en": {
            "how": "{name}'s page focuses on how {typ} helps someone feel loved. When this doorway is missed, the hurt often comes from small details that were not named, kept, shared, or safely received.",
            "need": "{name} does not guard a demand; this guardian protects a way of receiving care. Use the page to name what needs to be seen, which misfrequency feels tender, and what small action would help.",
            "practice": "Practice once through {name}'s lens today: name the feeling, name the need in the language of {typ}, then ask for one small action the other person can do.",
            "scripts": ["I want to explain this through the language of {typ}.", "This is not me making it too big; this is one doorway where I receive love.", "If you are willing, I would like to start with one small action."],
            "reflection": ["Was my latest moment of not feeling received connected to {typ}?", "Can {name}'s reminder help me shrink the request into one doable step?", "Did I state a need as blame instead of a request?"],
        },
        "ja": {
            "how": "{name} のページは、{typ} がどのように愛されている感覚につながるかを扱います。この入口が見落とされる時、傷つきは大事件ではなく、言葉にされない、残されない、安全に受け取られない細部から生まれます。",
            "need": "{name} が守るのはわがままな要求ではなく、ケアを受け取る一つの方法です。このページで、何を見てほしいのか、どのすれ違いが痛むのか、どんな小さな行動が助けになるのかを整理できます。",
            "practice": "今日は {name} の視点で一度練習します。感情を名づけ、{typ} のニーズを伝え、相手ができる小さな行動を一つだけお願いします。",
            "scripts": ["このことを {typ} の言語で説明したい。", "大げさにしたいのではなく、ここが私の愛を受け取る入口です。", "よければ、小さな行動を一つだけ始めたい。"],
            "reflection": ["最近受け取られなかった感覚は {typ} と関係しているか。", "{name} の視点でお願いを一つの行動へ小さくできるか。", "ニーズをお願いではなく責め言葉として言っていないか。"],
        },
        "ko": {
            "how": "{name} 페이지는 {typ}이 어떻게 사랑받는 감각으로 이어지는지 다룹니다. 이 입구가 놓치면 상처는 큰 사건보다 말해지지 않거나 남겨지지 않거나 안전하게 받지 못한 세부에서 생깁니다.",
            "need": "{name}가 지키는 것은 고집스러운 요구가 아니라 돌봄을 받는 방식입니다. 이 페이지로 무엇이 보이길 바라는지, 어떤 어긋남이 아픈지, 어떤 작은 행동이 도움이 되는지 정리할 수 있습니다.",
            "practice": "오늘 {name}의 관점으로 한 번 연습하세요. 감정을 말하고, {typ}의 욕구를 밝히고, 상대가 할 수 있는 작은 행동 하나만 요청합니다.",
            "scripts": ["이 일을 {typ}의 언어로 설명하고 싶어.", "이건 과장하려는 게 아니라 내가 사랑을 받는 입구야.", "괜찮다면 작은 행동 하나부터 시작하고 싶어."],
            "reflection": ["최근 받지 못했다고 느낀 순간은 {typ}과 관련이 있나?", "{name}의 시선으로 요청을 실행 가능한 한 걸음으로 줄일 수 있나?", "욕구를 요청이 아니라 비난처럼 말하고 있지는 않나?"],
        },
        "es": {
            "how": "La página de {name} se centra en cómo {typ} ayuda a una persona a sentirse amada. Cuando esta puerta se pierde, el dolor suele venir de detalles que no fueron nombrados, guardados, compartidos o recibidos con seguridad.",
            "need": "{name} no protege una exigencia; protege una forma de recibir cuidado. Usa la página para nombrar qué necesita verse, qué desajuste duele y qué acción pequeña ayudaría.",
            "practice": "Practica hoy una vez desde la mirada de {name}: nombra el sentimiento, nombra la necesidad en el lenguaje de {typ} y pide una acción pequeña que la otra persona pueda hacer.",
            "scripts": ["Quiero explicar esto con el lenguaje de {typ}.", "No estoy exagerando; esta es una puerta por donde recibo amor.", "Si estás dispuesto/a, me gustaría empezar con una acción pequeña."],
            "reflection": ["Mi último momento de no sentirme recibida estuvo conectado con {typ}?", "La mirada de {name} puede ayudarme a convertir la petición en un paso posible?", "Estoy diciendo una necesidad como culpa en vez de petición?"],
        },
    }
    raw = templates[lang]
    values = {"name": name, "typ": typ, "desc": desc}
    return {key: [item.format(**values) for item in value] if isinstance(value, list) else value.format(**values) for key, value in raw.items()}


POLICY_SECTIONS = {
    "zh": {
        "contact": [
            ("可以聯絡我們的事情", "如果頁面內容、守護者對應、語言版本、聯盟連結或可用性出現問題，請寄到 contact@lovetypes.tw。描述你看到的頁面網址、裝置與需要修正的地方，能讓我們更快回到心語庭園裡補上缺口。"),
            ("合作與素材授權", "品牌合作、素材引用、教學或媒體需求可以用同一個信箱提出。LoveTypes 會先確認合作是否符合五守護者宇宙觀、讀者信任與清楚揭露原則，再決定是否進一步討論。"),
            ("不適合透過本站處理的狀況", "LoveTypes 無法提供緊急諮商、醫療、法律或個案診斷。如果你正處於危急、暴力、騷擾或自傷風險，請優先尋求當地緊急資源與專業協助。"),
        ],
        "privacy": [
            ("我們收集什麼", "LoveTypes 目前不要求註冊帳號，也不要求你提交測驗結果才能閱讀內容。你主動寄信給我們時，信件地址與內容只會用於回覆、修正問題或處理你提出的請求。"),
            ("第三方服務", "網站可能使用託管、分析、聯盟行銷或外部連結服務。這些服務可能依各自政策處理技術資料，例如瀏覽器資訊、來源網址或點擊紀錄；我們會避免把它們設計成辨識個人情感狀態的工具。"),
            ("資料請求與刪除", "若你曾透過 contact@lovetypes.tw 聯絡我們，可以要求查詢、更正或刪除相關通信紀錄。我們會在合理範圍內處理，除非法律、安全或防濫用需求要求保留最少必要紀錄。"),
        ],
        "terms": [
            ("內容用途", "LoveTypes 的測驗、指南與守護者設定是自我理解與關係溝通工具。你可以用它們整理語言、準備對話與練習修復，但不應把結果當成永久標籤或判定一段關係的唯一依據。"),
            ("責任邊界", "本站內容不能取代心理治療、醫療、法律、財務或危機介入建議。任何基於本站內容做出的行動，都需要結合你的真實情境、雙方同意與必要的專業支持。"),
            ("智慧財產與外部連結", "LoveTypes 的文字、角色設定、圖片與版面屬於網站內容資產，除合理引用外請勿未經許可大量重製。外部與聯盟連結會帶你離開本站，購買與使用條款由各服務自行負責。"),
        ],
    },
    "en": {
        "contact": [
            ("What to Send Us", "If a page, guardian match, language version, affiliate link, or accessibility detail looks wrong, write to contact@lovetypes.tw. Include the page URL, device, and what needs correction so we can repair that corner of the Heart Garden clearly."),
            ("Partnerships and Assets", "Use the same inbox for brand inquiries, media requests, teaching use, or asset permissions. LoveTypes reviews whether a request fits the five-guardian world, reader trust, and clear disclosure before discussing next steps."),
            ("What This Site Cannot Handle", "LoveTypes cannot provide emergency counseling, medical care, legal advice, or individual diagnosis. If you face danger, violence, harassment, or self-harm risk, contact local emergency and professional resources first."),
        ],
        "privacy": [
            ("What We Collect", "LoveTypes does not currently require accounts, and you do not need to submit quiz results to read the site. If you email us, your address and message are used to reply, correct issues, or handle the request you made."),
            ("Third-Party Services", "The site may use hosting, analytics, affiliate, or external link services. These services may process technical data such as browser information, referrers, or click records under their own policies; we avoid designing them to identify personal emotional states."),
            ("Access and Deletion", "If you contacted us through contact@lovetypes.tw, you may ask to access, correct, or delete related communication records. We will handle reasonable requests unless law, safety, or abuse-prevention needs require minimal retention."),
        ],
        "terms": [
            ("How to Use the Content", "LoveTypes quizzes, guides, and guardian stories are tools for self-understanding and relationship conversation. Use them to organize language, prepare dialogue, and practice repair, not as permanent labels or the sole judgment of a relationship."),
            ("Responsibility Boundary", "The site does not replace therapy, medical care, legal advice, financial advice, or crisis support. Actions based on this content should account for real context, consent from everyone involved, and professional support when needed."),
            ("Intellectual Property and Links", "LoveTypes text, character settings, images, and layouts are site assets. Please do not reproduce them at scale without permission beyond reasonable citation. External and affiliate links take you away from this site, and their purchases or terms are handled by each service."),
        ],
    },
    "ja": {
        "contact": [
            ("連絡できる内容", "ページ内容、守護者の対応、言語版、アフィリエイトリンク、使いやすさに問題がある場合は contact@lovetypes.tw へお送りください。URL、端末、修正点を書いていただくと、心語庭園の欠けた場所を早く直せます。"),
            ("協力と素材利用", "ブランド連携、取材、教育利用、素材許可も同じ連絡先で受け付けます。LoveTypes は五守護者の世界観、読者の信頼、明確な開示に合うかを確認してから次の相談に進みます。"),
            ("本站で扱えないこと", "LoveTypes は緊急相談、医療、法律助言、個別診断を提供できません。危険、暴力、嫌がらせ、自傷リスクがある場合は、まず地域の緊急窓口と専門家に連絡してください。"),
        ],
        "privacy": [
            ("収集する情報", "LoveTypes は現在アカウント登録を求めず、測験結果を送信しなくても読むことができます。あなたがメールを送った場合、アドレスと本文は返信、修正、依頼対応のために使います。"),
            ("第三者サービス", "サイトはホスティング、分析、アフィリエイト、外部リンクサービスを使うことがあります。これらは各自の方針に従い、ブラウザ情報、参照元、クリック記録などの技術情報を扱う場合があります。個人の感情状態を識別する設計にはしません。"),
            ("確認と削除", "contact@lovetypes.tw に連絡したことがある場合、関連する通信記録の確認、修正、削除を依頼できます。法律、安全、不正利用防止のために最小限の保持が必要な場合を除き、合理的に対応します。"),
        ],
        "terms": [
            ("内容の使い方", "LoveTypes の測験、ガイド、守護者設定は自己理解と関係の対話のための道具です。言葉を整理し、会話を準備し、修復を練習するために使い、永続的なラベルや関係判断の唯一の根拠にはしないでください。"),
            ("責任の境界", "本站は心理療法、医療、法律、財務、危機介入の助言を代替しません。内容に基づく行動は、現実の状況、関係者の同意、必要な専門支援を合わせて考えてください。"),
            ("知的財産とリンク", "LoveTypes の文章、キャラクター設定、画像、レイアウトはサイト資産です。合理的な引用を超える大量複製は許可なく行わないでください。外部リンクやアフィリエイトリンク先の購入・規約は各サービスの責任です。"),
        ],
    },
    "ko": {
        "contact": [
            ("문의할 수 있는 내용", "페이지 내용, 수호자 연결, 언어 버전, 제휴 링크, 접근성에 문제가 있으면 contact@lovetypes.tw 로 보내 주세요. 페이지 주소, 기기, 수정이 필요한 부분을 적어 주면 마음 정원의 빈틈을 더 빨리 고칠 수 있습니다."),
            ("협업과 자료 사용", "브랜드 협업, 미디어 요청, 교육 활용, 자료 허가도 같은 메일로 보낼 수 있습니다. LoveTypes는 요청이 다섯 수호자 세계관, 독자 신뢰, 명확한 공개 원칙에 맞는지 먼저 확인합니다."),
            ("이 사이트가 처리할 수 없는 일", "LoveTypes는 긴급 상담, 의료, 법률 조언, 개인 진단을 제공하지 않습니다. 위험, 폭력, 괴롭힘, 자해 위험이 있다면 먼저 지역 긴급 자원과 전문가의 도움을 구하세요."),
        ],
        "privacy": [
            ("수집하는 정보", "LoveTypes는 현재 계정 가입을 요구하지 않으며, 테스트 결과를 제출하지 않아도 콘텐츠를 읽을 수 있습니다. 사용자가 메일을 보낼 경우 주소와 내용은 답변, 문제 수정, 요청 처리에만 사용됩니다."),
            ("제3자 서비스", "사이트는 호스팅, 분석, 제휴, 외부 링크 서비스를 사용할 수 있습니다. 이러한 서비스는 각자의 정책에 따라 브라우저 정보, 유입 주소, 클릭 기록 같은 기술 자료를 처리할 수 있으며, 개인의 감정 상태를 식별하도록 설계하지 않습니다."),
            ("조회와 삭제 요청", "contact@lovetypes.tw 로 연락한 적이 있다면 관련 통신 기록의 조회, 수정, 삭제를 요청할 수 있습니다. 법률, 안전, 남용 방지를 위해 최소 보관이 필요한 경우를 제외하고 합리적으로 처리합니다."),
        ],
        "terms": [
            ("콘텐츠 사용", "LoveTypes의 테스트, 가이드, 수호자 설정은 자기 이해와 관계 대화를 돕는 도구입니다. 언어를 정리하고 대화를 준비하며 회복을 연습하는 데 사용하되, 영구 라벨이나 관계 판단의 유일한 근거로 삼지 마세요."),
            ("책임의 경계", "이 사이트는 심리치료, 의료, 법률, 재정, 위기 개입 조언을 대신하지 않습니다. 콘텐츠를 바탕으로 한 행동은 실제 상황, 모두의 동의, 필요한 전문 지원을 함께 고려해야 합니다."),
            ("지식재산과 외부 링크", "LoveTypes의 글, 캐릭터 설정, 이미지, 레이아웃은 사이트 콘텐츠 자산입니다. 합리적 인용을 넘는 대량 복제는 허가 없이 하지 마세요. 외부 및 제휴 링크의 구매와 약관은 각 서비스가 책임집니다."),
        ],
    },
    "es": {
        "contact": [
            ("Qué Puedes Enviarnos", "Si una página, correspondencia de guardián, versión de idioma, enlace afiliado o detalle de accesibilidad parece incorrecto, escribe a contact@lovetypes.tw. Incluye la URL, el dispositivo y lo que debe corregirse para reparar esa parte del Jardín del Corazón."),
            ("Colaboraciones y Recursos", "Usa el mismo correo para propuestas de marca, medios, uso educativo o permisos de material. LoveTypes revisa si la solicitud encaja con el mundo de los cinco guardianes, la confianza del lector y una divulgación clara antes de avanzar."),
            ("Lo Que Este Sitio No Atiende", "LoveTypes no ofrece consejería de emergencia, atención médica, asesoría legal ni diagnóstico individual. Si hay peligro, violencia, acoso o riesgo de autolesión, busca primero recursos locales de emergencia y apoyo profesional."),
        ],
        "privacy": [
            ("Qué Recopilamos", "LoveTypes actualmente no requiere cuentas, y no necesitas enviar resultados del test para leer el sitio. Si nos escribes, tu dirección y mensaje se usan para responder, corregir problemas o atender la solicitud que hiciste."),
            ("Servicios de Terceros", "El sitio puede usar servicios de alojamiento, analítica, afiliación o enlaces externos. Estos servicios pueden procesar datos técnicos como navegador, referencia o clics bajo sus propias políticas; evitamos diseñarlos para identificar estados emocionales personales."),
            ("Acceso y Eliminación", "Si contactaste a contact@lovetypes.tw, puedes pedir acceso, corrección o eliminación de registros relacionados. Atenderemos solicitudes razonables salvo que la ley, la seguridad o la prevención de abuso requieran conservar lo mínimo necesario."),
        ],
        "terms": [
            ("Uso del Contenido", "Los tests, guías e historias de guardianes de LoveTypes son herramientas de autocomprensión y conversación relacional. Úsalos para ordenar lenguaje, preparar diálogo y practicar reparación, no como etiquetas permanentes ni como único juicio de una relación."),
            ("Límite de Responsabilidad", "El sitio no reemplaza terapia, atención médica, asesoría legal, financiera ni apoyo de crisis. Toda acción basada en este contenido debe considerar el contexto real, el consentimiento de las personas involucradas y apoyo profesional cuando haga falta."),
            ("Propiedad Intelectual y Enlaces", "Los textos, personajes, imágenes y diseños de LoveTypes son activos del sitio. No los reproduzcas a gran escala sin permiso más allá de una cita razonable. Los enlaces externos y afiliados te llevan fuera del sitio, y sus compras o términos dependen de cada servicio."),
        ],
    },
}


POLICY_CONTACT_CTA = {
    "zh": {
        "title": "需要我們修復某個角落？",
        "intro": "如果你想要求資料修正、刪除通信紀錄、回報條款不清楚，或指出外部連結與可用性問題，請走同一個修復回報入口。",
        "cta": "前往修復回報入口",
    },
    "en": {
        "title": "Need us to repair a corner of the site?",
        "intro": "For data corrections, deletion requests, unclear terms, external-link issues, or accessibility problems, use the same repair report route.",
        "cta": "Open repair report route",
    },
    "ja": {
        "title": "サイト内で修復が必要な場所がありますか？",
        "intro": "データ修正、通信記録の削除依頼、規約の不明点、外部リンクや使いやすさの問題は、同じ修復報告入口から送れます。",
        "cta": "修復報告入口へ",
    },
    "ko": {
        "title": "사이트에서 수리할 곳이 있나요?",
        "intro": "자료 수정, 통신 기록 삭제 요청, 약관의 불명확한 부분, 외부 링크나 접근성 문제는 같은 수리 제보 입구로 보낼 수 있습니다.",
        "cta": "수리 제보 입구 열기",
    },
    "es": {
        "title": "¿Necesitas que reparemos una parte del sitio?",
        "intro": "Para correcciones de datos, solicitudes de eliminación, términos poco claros, enlaces externos o problemas de accesibilidad, usa la misma ruta de reporte.",
        "cta": "Abrir ruta de reparación",
    },
}


NOT_FOUND_COPY = {
    "zh": {
        "title": "這盞燈暫時不在地圖上 | LoveTypes",
        "desc": "LoveTypes 自訂 404 頁面，協助迷路的旅人回到測驗、守護者總覽、旅人補給或聯絡頁。",
        "eyebrow": "404 HEART GARDEN",
        "heading": "這盞燈暫時不在地圖上",
        "intro": "你抵達的路徑可能已移動、改名，或還沒有被放進心語庭園。先回到一條可靠的路線，不需要在迷霧裡停太久。",
        "safe_routes": "選一條回到庭園的路",
        "return_path": "RETURN PATH",
        "guardians": "查看五位守護者",
        "home_text": "回到首頁完成 15 道心語認領儀式。",
        "guardians_text": "從艾莉絲、諾雅、薇薇安、克萊兒與朵拉重新找到入口。",
        "resources_text": "前往守護者補給路線，選一個可實作的下一步。",
        "contact_text": "如果這是壞連結，告訴我們需要修復的頁面。",
    },
    "en": {
        "title": "This light is not on the map yet | LoveTypes",
        "desc": "LoveTypes custom 404 page that guides lost travelers back to the quiz, guardians, resources, or contact route.",
        "eyebrow": "404 HEART GARDEN",
        "heading": "This light is not on the map yet",
        "intro": "The path you reached may have moved, changed names, or not yet been placed in the Heart Garden. Choose a reliable route instead of staying in the fog.",
        "safe_routes": "Choose a route back to the garden",
        "return_path": "RETURN PATH",
        "guardians": "View the five guardians",
        "home_text": "Return home and complete the 15-question claiming ritual.",
        "guardians_text": "Find your way back through Iris, Noah, Vivian, Claire, and Dora.",
        "resources_text": "Open a guardian supply route and choose one practical next step.",
        "contact_text": "If this is a broken link, tell us which page needs repair.",
    },
    "ja": {
        "title": "この灯りはまだ地図にありません | LoveTypes",
        "desc": "LoveTypes のカスタム 404 ページ。迷った旅人を測定、守護者、リソース、連絡ページへ案内します。",
        "eyebrow": "404 HEART GARDEN",
        "heading": "この灯りはまだ地図にありません",
        "intro": "到着した道は移動したか、名前が変わったか、まだ心語庭園に置かれていない可能性があります。霧の中に留まらず、確かな道へ戻りましょう。",
        "safe_routes": "庭園へ戻る道を選ぶ",
        "return_path": "RETURN PATH",
        "guardians": "五人の守護者を見る",
        "home_text": "ホームへ戻り、15問の認領儀式を完了します。",
        "guardians_text": "アイリス、ノア、ヴィヴィアン、クレア、ドラから入口を探します。",
        "resources_text": "守護者の補給ルートへ進み、実行できる次の一歩を選びます。",
        "contact_text": "壊れたリンクなら、修復が必要なページを教えてください。",
    },
    "ko": {
        "title": "이 불빛은 아직 지도에 없습니다 | LoveTypes",
        "desc": "LoveTypes 맞춤 404 페이지입니다. 길을 잃은 여행자를 테스트, 수호자, 자료, 연락 경로로 안내합니다.",
        "eyebrow": "404 HEART GARDEN",
        "heading": "이 불빛은 아직 지도에 없습니다",
        "intro": "도착한 길이 이동되었거나 이름이 바뀌었거나 아직 마음 언어 정원에 놓이지 않았을 수 있습니다. 안개 속에 오래 머물지 말고 확실한 길로 돌아가세요.",
        "safe_routes": "정원으로 돌아갈 길 선택하기",
        "return_path": "RETURN PATH",
        "guardians": "다섯 수호자 보기",
        "home_text": "홈으로 돌아가 15문항 인정 의식을 완료합니다.",
        "guardians_text": "아이리스, 노아, 비비안, 클레어, 도라를 통해 다시 입구를 찾습니다.",
        "resources_text": "수호자 보급 루트로 이동해 실행 가능한 다음 한 걸음을 고릅니다.",
        "contact_text": "깨진 링크라면 수리가 필요한 페이지를 알려 주세요.",
    },
    "es": {
        "title": "Esta luz aún no está en el mapa | LoveTypes",
        "desc": "Página 404 personalizada de LoveTypes para guiar a visitantes perdidos hacia el test, las guardianas, recursos o contacto.",
        "eyebrow": "404 HEART GARDEN",
        "heading": "Esta luz aún no está en el mapa",
        "intro": "La ruta que abriste quizá se movió, cambió de nombre o todavía no está dentro del Jardín del Corazón. Vuelve a un camino confiable sin quedarte en la niebla.",
        "safe_routes": "Elige una ruta para volver al jardín",
        "return_path": "RETURN PATH",
        "guardians": "Ver las cinco guardianas",
        "home_text": "Volver al inicio y completar el ritual de 15 preguntas.",
        "guardians_text": "Reencuentra la entrada con Iris, Noah, Vivian, Claire y Dora.",
        "resources_text": "Abre una ruta de recursos de guardiana y elige un siguiente paso práctico.",
        "contact_text": "Si es un enlace roto, dinos qué página necesita reparación.",
    },
}


POLICY_COMPASS_COPY = {
    "zh": {
        "eyebrow": "SAFETY BOUNDARY MAP",
        "title": "安全邊界星圖",
        "intro": "先用三個邊界看清楚這座心語庭園如何處理聯絡、資料、內容責任與外部連結，再往下閱讀完整條文。",
        "card_hint": "這是本頁第 {number} 個信任邊界，完整說明在下方條文。",
        "detail_eyebrow": "FULL POLICY NOTES",
        "detail_title": "完整條文",
        "detail_intro": "以下內容把導讀星圖展開成可執行的規則，方便你判斷什麼可以期待、什麼需要改走專業支援。",
    },
    "en": {
        "eyebrow": "SAFETY BOUNDARY MAP",
        "title": "Safety boundary map",
        "intro": "Start with three boundaries for contact, data, responsibility, and external links before reading the full policy details below.",
        "card_hint": "This is trust boundary {number}; the full note appears below.",
        "detail_eyebrow": "FULL POLICY NOTES",
        "detail_title": "Full policy notes",
        "detail_intro": "The notes below expand the map into usable rules, so you can see what to expect and when professional support is the right path.",
    },
    "ja": {
        "eyebrow": "SAFETY BOUNDARY MAP",
        "title": "安全境界の星図",
        "intro": "連絡、データ、内容責任、外部リンクについて、この庭が守る三つの境界を先に確認してから詳細を読めます。",
        "card_hint": "これは本ページの信頼境界 {number} です。詳しい説明は下の条文にあります。",
        "detail_eyebrow": "FULL POLICY NOTES",
        "detail_title": "詳細条文",
        "detail_intro": "下の内容では星図を具体的な規則に展開し、期待できることと専門支援へ進むべき場面を確認できます。",
    },
    "ko": {
        "eyebrow": "SAFETY BOUNDARY MAP",
        "title": "안전 경계 지도",
        "intro": "연락, 데이터, 콘텐츠 책임, 외부 링크에 대해 이 정원이 지키는 세 가지 경계를 먼저 보고 자세한 내용을 읽을 수 있습니다.",
        "card_hint": "이 항목은 본 페이지의 신뢰 경계 {number}입니다. 자세한 설명은 아래 조항에 있습니다.",
        "detail_eyebrow": "FULL POLICY NOTES",
        "detail_title": "전체 조항",
        "detail_intro": "아래 내용은 지도를 실행 가능한 규칙으로 풀어, 무엇을 기대할 수 있고 언제 전문 지원이 필요한지 확인하게 합니다.",
    },
    "es": {
        "eyebrow": "SAFETY BOUNDARY MAP",
        "title": "Mapa de límites seguros",
        "intro": "Empieza con tres límites sobre contacto, datos, responsabilidad y enlaces externos antes de leer los detalles completos.",
        "card_hint": "Este es el límite de confianza {number}; la nota completa aparece abajo.",
        "detail_eyebrow": "FULL POLICY NOTES",
        "detail_title": "Notas completas de política",
        "detail_intro": "Las notas siguientes convierten el mapa en reglas utilizables, para saber qué esperar y cuándo corresponde apoyo profesional.",
    },
}


def quiz_payload(lang: str) -> str:
    type_order = ["W", "T", "G", "S", "P"]
    questions = []
    for text, options in QUIZ_QUESTIONS[lang]:
        questions.append({
            "text": text,
            "options": [{"text": option, "type": type_order[idx]} for idx, option in enumerate(options)],
        })
    results = {}
    for key, meta in QUIZ_TYPES.items():
        guardian = GUARDIANS[meta["slug"]]
        name, typ, desc = guardian[lang]
        domain_title, domain_desc, domain_cta = GUARDIAN_DOMAINS[meta["slug"]][lang]
        domain = GUARDIAN_DOMAINS[meta["slug"]]
        guide = next(g for g in GUIDES if g["slug"] == meta["guide"])
        route = supply_route(lang, meta["slug"])
        resource_url = lang_url(lang, "resources") + f"#supply-{meta['slug']}"
        image_width, image_height = IMAGE_DIMENSIONS.get(guardian["asset"], ("", ""))
        result_image = guardian_result_image(meta["slug"], guardian["asset"])
        result_image_width, result_image_height = IMAGE_DIMENSIONS.get(result_image, (image_width, image_height))
        story_image = guardian_story_image(lang, meta["slug"])
        story_width, story_height = IMAGE_DIMENSIONS.get(story_image, ("", ""))
        domain_prop_width, domain_prop_height = IMAGE_DIMENSIONS.get(guardian["prop"], ("", ""))
        results[key] = {
            "name": name,
            "type": typ,
            "desc": desc,
            "image": guardian["asset"],
            "imageWidth": image_width,
            "imageHeight": image_height,
            "resultImage": result_image,
            "resultImageWidth": result_image_width,
            "resultImageHeight": result_image_height,
            "color": meta["color"],
            "domainTitle": domain_title,
            "domainDesc": domain_desc,
            "domainCta": domain_cta,
            "domainAccent": domain["accent"],
            "domainGlow": domain["glow"],
            "domainMotif": domain["motif"],
            "domainProp": guardian["prop"],
            "domainPropWidth": domain_prop_width,
            "domainPropHeight": domain_prop_height,
            "guardianUrl": lang_url(lang, "characters/" + meta["slug"]),
            "guideUrl": lang_url(lang, "guides/" + meta["guide"]) + f"#guide-{meta['slug']}",
            "guideTitle": guide[lang][0],
            "resourceUrl": resource_url,
            "contactUrl": lang_url(lang, "contact") + "#luna-supply-request",
            "supplyTitle": route["title"],
            "supplyDesc": route["desc"],
            "supplyMission": route["mission"],
            "supplyText": route["supply"],
            "supplyBook": route["book"]["title"][lang],
            "supplyBookUrl": route["book"]["url"],
            "lunaUrl": lang_url(lang, "luna-yoga-music") + f"#luna-{meta['slug']}",
            "storyImage": story_image,
            "storyImageWidth": story_width,
            "storyImageHeight": story_height,
            "slug": meta["slug"],
            "collectorTitle": COLLECTOR_LABELS[lang]["card"],
            "collectorHint": COLLECTOR_LABELS[lang]["share_hint"],
            "collectorOpen": COLLECTOR_LABELS[lang]["open"],
            "collectorSave": COLLECTOR_LABELS[lang]["download"],
            "collectorHall": COLLECTOR_LABELS[lang]["hall"],
            "collectorHallUrl": lang_url(lang, "keepsakes") + f"#keepsake-{meta['slug']}",
            "collectorStory": COLLECTOR_LABELS[lang]["story"],
            "collectorStoryKicker": COLLECTOR_LABELS[lang]["story_kicker"],
            "collectorStoryCta": guardian_story_cta(lang, meta["slug"]),
            "collectorStoryError": COLLECTOR_LABELS[lang]["story_error"],
            "planUrl": lang_url(lang, "repair-plan") + f"#plan-{meta['slug']}",
            "planLabel": REPAIR_PLAN[lang]["title"],
            "tips": QUIZ_TIPS[lang][key],
            "starterKit": starter_kit_payload(lang, resource_url),
            "supplyProductPack": supply_product_pack(lang, meta["slug"]),
        }
    payload = {
        "labels": QUIZ_LABELS[lang],
        "questions": questions,
        "results": results,
        "order": type_order,
        "shareUrl": DOMAIN + lang_url(lang).rstrip("/") + "/",
        "affiliateDisclosure": AFFILIATE_DISCLOSURE[lang],
        "affiliateButton": AFFILIATE_COPY[lang]["button"],
        "supplySafety": {
            "chooseTitle": SUPPLY_LABELS[lang]["choose"],
            "chooseText": SUPPLY_LABELS[lang]["choose_text"],
            "notNowTitle": SUPPLY_LABELS[lang]["not_now"],
            "notNowText": SUPPLY_LABELS[lang]["not_now_text"],
        },
    }
    return json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")


def quiz_script(lang: str) -> str:
    return f"""
{quiz_data_script_tag(lang)}
<script>
(() => {{
  const quiz = window.__LOVETYPES_QUIZ_DATA;
  if (!quiz) return;
  const root = document.querySelector('[data-quiz-root]');
  if (!root) return;
  const intro = root.querySelector('[data-quiz-intro]');
  const quizBox = root.querySelector('[data-quiz-box]');
  const resultBox = root.querySelector('[data-quiz-result]');
  const savedBox = root.querySelector('[data-quiz-saved]');
  const homeResumeBox = document.querySelector('[data-home-saved]');
  const startButtons = root.querySelectorAll('[data-quiz-start]');
  const storageKey = `lovetypes:${{location.pathname}}:quiz-result`;
  const sharedStorageKey = "lovetypes:{lang}:quiz-result";
  const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const scrollBehavior = reduceMotion ? 'auto' : 'smooth';
  let current = 0;
  let selected = null;
  const answers = [];
  const preloadedResultImages = new Map();

  function show(el) {{ el.hidden = false; }}
  function hide(el) {{ el.hidden = true; }}
  function primeResultImage(result) {{
    if (!result.resultImage) return Promise.resolve();
    if (preloadedResultImages.has(result.resultImage)) return preloadedResultImages.get(result.resultImage);
    const image = new Image();
    image.decoding = 'async';
    image.fetchPriority = 'high';
    image.src = result.resultImage;
    const ready = image.decode
      ? image.decode().catch(() => undefined)
      : new Promise((resolve) => {{
          image.onload = resolve;
          image.onerror = resolve;
        }});
    preloadedResultImages.set(result.resultImage, ready);
    return ready;
  }}
  function preloadResultImages() {{
    Object.values(quiz.results).forEach((result) => {{
      primeResultImage(result);
    }});
  }}
  function readSavedResult() {{
    try {{
      const saved = JSON.parse(localStorage.getItem(sharedStorageKey) || localStorage.getItem(storageKey) || 'null');
      return saved && quiz.results[saved.primaryKey] ? saved : null;
    }} catch (error) {{
      return null;
    }}
  }}
  async function copyShareText(text, button) {{
    const originalText = button.textContent;
    const mark = (label) => {{
      button.textContent = label;
      window.setTimeout(() => {{ button.textContent = originalText; }}, 2400);
    }};
    try {{
      if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('clipboard-unavailable');
      await navigator.clipboard.writeText(text);
      mark(quiz.labels.copied);
      return;
    }} catch (error) {{
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.setAttribute('readonly', '');
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      textarea.style.pointerEvents = 'none';
      document.body.appendChild(textarea);
      textarea.select();
      try {{
        const copied = document.execCommand('copy');
        mark(copied ? quiz.labels.copied : quiz.labels.copy_unavailable);
      }} catch (fallbackError) {{
        window.prompt(quiz.labels.copy_manual, text);
        mark(quiz.labels.copy_unavailable);
      }} finally {{
        textarea.remove();
      }}
    }}
  }}
  async function shareGuardianResult(result, text, url, button) {{
    const originalText = button.textContent;
    const mark = (label) => {{
      button.textContent = label;
      window.setTimeout(() => {{ button.textContent = originalText; }}, 2400);
    }};
    if (navigator.share) {{
      try {{
        await navigator.share({{ title: `${{result.name}} · ${{result.type}}`, text, url }});
        mark(quiz.labels.shared);
        return;
      }} catch (error) {{
        if (error && error.name === 'AbortError') return;
      }}
    }}
    await copyShareText(text, button);
  }}
  function renderSavedResultCard(box, result, savedShareText, cardUrl, variant) {{
    if (!box) return;
    const articleClass = variant === 'home'
      ? 'quiz-saved-card home-resume-card pass-resume-card'
      : 'quiz-saved-card pass-resume-card';
    const actionsClass = variant === 'home'
      ? 'quiz-saved-actions home-resume-actions'
      : 'quiz-saved-actions';
    box.innerHTML = `
      <article class="${{articleClass}}" style="--result-accent:${{result.domainAccent || result.color}};--domain-glow:${{result.domainGlow || result.color}}">
        <img src="${{result.resultImage}}" alt="${{result.name}}" width="${{result.resultImageWidth}}" height="${{result.resultImageHeight}}" loading="lazy" decoding="async" fetchpriority="low">
        <div>
          <div class="resume-pass-stamp" data-resume-pass-stamp>
            <img class="resume-pass-prop" src="${{result.domainProp}}" alt="${{result.domainTitle}}" width="${{result.domainPropWidth}}" height="${{result.domainPropHeight}}" loading="lazy" decoding="async" fetchpriority="low">
            <span>${{quiz.labels.pass_title}}</span>
            <strong>${{result.domainTitle}}</strong>
          </div>
          <p class="eyebrow">${{quiz.labels.saved_title}}</p>
          <h3>${{result.name}} · ${{result.type}}</h3>
          <p>${{quiz.labels.saved_intro}}</p>
          <p><strong>${{quiz.labels.next_pack_title}}</strong> · ${{result.supplyTitle}}</p>
          <p class="eyebrow">${{result.supplyProductPack.label}}</p>
          <div class="${{actionsClass}}" data-home-saved-product-pack>
            ${{result.supplyProductPack.items.map((item) => `<a href="${{item.href}}" data-home-saved-product-link>${{item.title}}</a>`).join('')}}
          </div>
          <div class="callout safety supply-pack-safety-note" data-home-saved-supply-safety>
            <strong>${{quiz.supplySafety.notNowTitle}}</strong>
            <p>${{quiz.supplySafety.notNowText}}</p>
          </div>
          <div class="${{actionsClass}}">
            <a href="${{result.resourceUrl}}" data-home-resume-route>${{quiz.labels.saved_route}}</a>
            <a href="${{result.planUrl}}" data-home-saved-plan data-home-resume-plan>${{quiz.labels.saved_plan}}</a>
            <a href="${{result.lunaUrl}}" data-home-resume-luna>${{quiz.labels.saved_luna}}</a>
            <a href="${{result.collectorHallUrl}}" data-home-saved-keepsake data-home-resume-keepsake>${{quiz.labels.saved_card}}</a>
            <a href="${{result.contactUrl}}" data-home-resume-contact>${{quiz.labels.saved_contact}}</a>
            <a href="${{result.guardianUrl}}" data-home-resume-guardian>${{quiz.labels.guardian_link}}</a>
            <button type="button" data-result-action="story" data-funnel-event="home_resume_story_generate" data-story-name="${{result.name}}" data-story-title="${{result.type}}" data-story-quote="${{result.supplyMission}}" data-story-image="${{result.resultImage}}" data-story-slug="${{result.slug}}" data-story-kicker="${{result.collectorStoryKicker}}" data-story-cta="${{result.collectorStoryCta}}" data-story-error="${{result.collectorStoryError}}">${{result.collectorStory}}</button>
            <button type="button" data-share-saved-result>${{quiz.labels.share}}</button>
            <button type="button" data-copy-saved-result>${{quiz.labels.saved_copy}}</button>
            <button type="button" data-clear-saved-result ${{variant === 'home' ? 'data-clear-home-result' : ''}}>${{quiz.labels.saved_clear}}</button>
          </div>
        </div>
      </article>`;
    show(box);
    box.querySelector('[data-share-saved-result]')?.addEventListener('click', async (event) => {{
      await shareGuardianResult(result, savedShareText, cardUrl, event.currentTarget);
    }});
    box.querySelector('[data-copy-saved-result]')?.addEventListener('click', async (event) => {{
      await copyShareText(savedShareText, event.currentTarget);
    }});
    box.querySelector('[data-clear-saved-result]')?.addEventListener('click', clearSavedResult);
  }}
  function clearSavedResult() {{
    localStorage.removeItem(storageKey);
    localStorage.removeItem(sharedStorageKey);
    renderSavedResult();
  }}
  function renderSavedResult() {{
    const saved = readSavedResult();
    if (!saved) {{
      [savedBox, homeResumeBox].forEach((box) => {{
        if (!box) return;
        hide(box);
        box.innerHTML = '';
      }});
      return;
    }}
    const result = quiz.results[saved.primaryKey];
    const cardUrl = new URL(result.storyImage, location.origin).href;
    const savedShareText = `${{quiz.labels.share_prefix}}：${{result.name}}｜${{result.type}} ${{cardUrl}}`;
    renderSavedResultCard(homeResumeBox, result, savedShareText, cardUrl, 'home');
    renderSavedResultCard(savedBox, result, savedShareText, cardUrl, 'quiz');
  }}
  function progressText() {{
    return quiz.labels.progress.replace('{{current}}', String(current + 1)).replace('{{total}}', String(quiz.questions.length));
  }}
  function renderQuestion() {{
    const q = quiz.questions[current];
    const questionId = `quiz-question-${{current + 1}}`;
    const progressPercent = Math.round((current + 1) / quiz.questions.length * 100);
    quizBox.innerHTML = `
      <div class="quiz-progress ritual-progress"><div class="quiz-progress-bar" role="progressbar" aria-valuemin="0" aria-valuemax="${{quiz.questions.length}}" aria-valuenow="${{current + 1}}" aria-label="${{progressText()}}"><span style="width:${{progressPercent}}%"></span></div><p>${{progressText()}}</p></div>
      <article class="quiz-card ritual-question-card" aria-labelledby="${{questionId}}">
        <p class="eyebrow">${{quiz.labels.question}} ${{current + 1}}</p>
        <h3 id="${{questionId}}">${{q.text}}</h3>
        <div class="quiz-options" role="group" aria-labelledby="${{questionId}}">
          ${{q.options.map((opt, idx) => `<button type="button" class="quiz-option" data-type="${{opt.type}}" aria-pressed="false"><span>${{idx + 1}}</span>${{opt.text}}</button>`).join('')}}
        </div>
        <button type="button" class="primary-btn quiz-next" disabled>${{current === quiz.questions.length - 1 ? quiz.labels.see : quiz.labels.next}}</button>
      </article>`;
    selected = null;
    quizBox.querySelectorAll('.quiz-option').forEach((button) => {{
      button.addEventListener('click', () => {{
        selected = button.dataset.type;
        quizBox.querySelectorAll('.quiz-option').forEach((item) => {{
          item.classList.remove('selected');
          item.setAttribute('aria-pressed', 'false');
        }});
        button.classList.add('selected');
        button.setAttribute('aria-pressed', 'true');
        quizBox.querySelector('.quiz-next').disabled = false;
      }});
    }});
    quizBox.querySelector('.quiz-next').addEventListener('click', () => {{
      if (!selected) return;
      answers.push(selected);
      current += 1;
      if (current < quiz.questions.length) renderQuestion();
      else renderResult();
    }});
  }}
  async function renderResult() {{
    const counts = Object.fromEntries(quiz.order.map((key) => [key, 0]));
    answers.forEach((key) => counts[key] += 1);
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    const primaryKey = sorted[0][0];
    const secondaryKey = sorted[1] && sorted[1][1] === sorted[0][1] ? sorted[1][0] : null;
    const result = quiz.results[primaryKey];
    const total = answers.length || 1;
    const cardUrl = new URL(result.storyImage, location.origin).href;
    const shareText = `${{quiz.labels.share_prefix}}：${{result.name}}｜${{result.type}} ${{cardUrl}}`;
    await primeResultImage(result);
    hide(quizBox);
    window.lovetypesLastResult = {{
      name: result.name,
      title: result.type,
      quote: result.supplyMission,
      image: result.resultImage,
      slug: result.slug
    }};
    try {{
      localStorage.setItem(storageKey, JSON.stringify({{ primaryKey, savedAt: new Date().toISOString() }}));
      localStorage.setItem(sharedStorageKey, JSON.stringify({{ primaryKey, savedAt: new Date().toISOString() }}));
    }} catch (error) {{}}
    resultBox.innerHTML = `
      <article class="quiz-result-card ritual-reveal-card" data-result-guardian="${{result.slug}}" style="--result-accent:${{result.color}}">
        <img src="${{result.resultImage}}" alt="${{result.name}}" width="${{result.resultImageWidth}}" height="${{result.resultImageHeight}}" loading="eager" decoding="async" fetchpriority="high">
        <div class="quiz-result-copy">
          <p class="eyebrow">${{quiz.labels.result_label}}</p>
          <h3>${{result.name}}</h3>
          <span class="result-type">${{result.type}}${{secondaryKey ? ' · ' + quiz.labels.tie : ''}}</span>
          <p>${{result.desc}}</p>
        </div>
      </article>
      <nav class="quiz-route-card" aria-label="${{quiz.labels.routes_title}}">
        <a class="primary-btn" href="${{result.resourceUrl}}" data-conversion-route>${{quiz.labels.primary_route}}</a>
        <a class="secondary-btn" href="${{result.planUrl}}" data-conversion-plan>${{quiz.labels.secondary_plan}}</a>
        <a class="secondary-btn" href="${{result.lunaUrl}}" data-conversion-luna>${{quiz.labels.luna_action}}</a>
        <a class="secondary-btn" href="${{result.collectorHallUrl}}" data-conversion-keepsake>${{quiz.labels.saved_card}}</a>
        <a class="secondary-btn" href="${{result.contactUrl}}" data-conversion-contact>${{quiz.labels.saved_contact}}</a>
        <a class="secondary-btn" href="${{result.guideUrl}}" data-conversion-guide>${{quiz.labels.guide_link}}</a>
        <a class="secondary-btn" href="${{result.guardianUrl}}">${{quiz.labels.guardian_link}}</a>
      </nav>
      <section class="quiz-score-card"><h3>${{quiz.labels.score_title}}</h3>
        ${{sorted.map(([key, count]) => {{
          const item = quiz.results[key];
          const pct = Math.round(count / total * 100);
          return `<div class="score-row"><div><span>${{item.type}}</span><strong>${{pct}}%</strong></div><div class="score-bar"><span style="width:${{pct}}%; background:${{item.color}}"></span></div></div>`;
        }}).join('')}}
      </section>
      <section class="quiz-advice-card"><h3>${{quiz.labels.tips_title}}</h3><ul>${{result.tips.map((tip) => `<li>${{tip}}</li>`).join('')}}</ul></section>
      <section class="quiz-action-compass guardian-supply-pass" aria-label="${{quiz.labels.compass_title}}" data-supply-pass style="--result-accent:${{result.domainAccent || result.color}};--domain-glow:${{result.domainGlow || result.color}}">
        <div class="supply-pass-head">
          <div>
            <p class="eyebrow">${{quiz.labels.pass_title}}</p>
            <h3>${{quiz.labels.next_pack_title}}</h3>
            <p>${{quiz.labels.next_pack_intro}}</p>
          </div>
          <div class="supply-pass-stamp" aria-label="${{quiz.labels.pass_code}}">
            <img src="${{result.domainProp}}" alt="${{result.domainTitle}}" width="${{result.domainPropWidth}}" height="${{result.domainPropHeight}}" loading="lazy" decoding="async" fetchpriority="low">
            <span>${{result.domainTitle}}</span>
          </div>
        </div>
        <p class="supply-pass-domain">${{result.domainDesc}}</p>
        <div class="quiz-action-grid">
          <article>
            <span>1</span>
            <h4>${{quiz.labels.free_step}}</h4>
            <p>${{result.supplyMission}}</p>
            <a href="${{result.planUrl}}">${{result.planLabel}}</a>
          </article>
          <article>
            <span>2</span>
            <h4>${{quiz.labels.luna_step}}</h4>
            <p>${{result.supplyText}}</p>
            <a href="${{result.lunaUrl}}">${{quiz.labels.luna_action}}</a>
          </article>
          <article>
            <span>3</span>
            <h4>${{quiz.labels.book_step}}</h4>
            <p>${{quiz.labels.book_intro}}：${{result.supplyBook}}</p>
            <a href="${{result.supplyBookUrl}}" target="_blank" rel="noopener noreferrer sponsored" data-conversion-book>${{quiz.affiliateButton}}</a>
          </article>
        </div>
        <p class="affiliate-disclosure">${{quiz.affiliateDisclosure}}</p>
      </section>
      <section class="quiz-action-compass guardian-supply-pass" aria-label="${{result.supplyProductPack.label}}" data-quiz-product-pack style="--result-accent:${{result.domainAccent || result.color}};--domain-glow:${{result.domainGlow || result.color}}">
        <div class="quiz-action-head">
          <p class="eyebrow">${{result.supplyProductPack.label}}</p>
          <h3>${{result.supplyTitle}}</h3>
        </div>
        <p class="supply-pass-domain">${{result.supplyProductPack.note}}</p>
        <div class="quiz-action-grid">
          ${{result.supplyProductPack.items.map((item) => `
            <article>
              <span>${{item.number}}</span>
              <h4>${{item.title}}</h4>
              <p>${{item.desc}}</p>
              <a href="${{item.href}}" data-quiz-product-pack-link>${{item.title}}</a>
            </article>
          `).join('')}}
        </div>
        <div class="callout safety supply-pack-safety-note" data-quiz-supply-safety>
          <strong>${{quiz.supplySafety.chooseTitle}}</strong>
          <p>${{quiz.supplySafety.chooseText}}</p>
          <strong>${{quiz.supplySafety.notNowTitle}}</strong>
          <p>${{quiz.supplySafety.notNowText}}</p>
        </div>
      </section>
      <section class="quiz-starter-kit" aria-label="${{result.starterKit.title}}">
        <div class="quiz-action-head">
          <p class="eyebrow">${{result.starterKit.eyebrow}}</p>
          <h3>${{result.starterKit.title}}</h3>
        </div>
        <p>${{result.starterKit.intro}}</p>
        <div class="quiz-starter-grid">
          ${{result.starterKit.steps.map((step) => `
            <article>
              <span>${{step.number}}</span>
              <h4>${{step.title}}</h4>
              <p>${{step.desc}}</p>
              <a href="${{step.href}}">${{step.action}}</a>
            </article>
          `).join('')}}
        </div>
      </section>
      <section class="quiz-supply-card">
        <p class="eyebrow">${{quiz.labels.resources_link}}</p>
        <h3>${{result.supplyTitle}}</h3>
        <p>${{result.supplyDesc}}</p>
        <ul><li>${{result.supplyMission}}</li><li>${{result.supplyText}}</li><li>${{result.supplyBook}}</li></ul>
        <p class="affiliate-disclosure">${{quiz.affiliateDisclosure}}</p>
        <a class="primary-btn" href="${{result.resourceUrl}}">${{quiz.labels.primary_route}}</a>
      </section>
      <section class="quiz-collector-card">
        <img src="${{result.storyImage}}" alt="${{result.collectorTitle}} ${{result.name}}" width="${{result.storyImageWidth}}" height="${{result.storyImageHeight}}" loading="lazy" decoding="async" fetchpriority="low">
        <div>
          <p class="eyebrow">${{result.collectorTitle}}</p>
          <h3>${{result.name}}</h3>
          <p>${{result.collectorHint}}</p>
          <div class="quiz-collector-actions">
            <a class="primary-btn" href="${{result.storyImage}}" target="_blank" rel="noopener noreferrer">${{result.collectorOpen}}</a>
            <a class="secondary-btn" href="${{result.storyImage}}" download>${{result.collectorSave}}</a>
            <button class="secondary-btn" type="button" data-result-action="story" data-funnel-event="quiz_result_story_generate" data-story-kicker="${{result.collectorStoryKicker}}" data-story-cta="${{result.collectorStoryCta}}" data-story-error="${{result.collectorStoryError}}">${{result.collectorStory}}</button>
            <a class="secondary-btn" href="${{result.collectorHallUrl}}" data-conversion-collector-keepsake>${{result.collectorHall}}</a>
          </div>
        </div>
      </section>
      <div class="quiz-tools"><button type="button" class="secondary-btn" data-share-result>${{quiz.labels.share}}</button><button type="button" class="secondary-btn" data-copy-result>${{quiz.labels.copy}}</button><button type="button" class="secondary-btn" data-retake>${{quiz.labels.retake}}</button></div>
      <p class="quiz-boundary">${{quiz.labels.boundary}}</p>`;
    show(resultBox);
    resultBox.querySelector('[data-retake]').addEventListener('click', startQuiz);
    resultBox.querySelector('[data-share-result]').addEventListener('click', async (event) => {{
      await shareGuardianResult(result, shareText, cardUrl, event.currentTarget);
    }});
    resultBox.querySelector('[data-copy-result]').addEventListener('click', async (event) => {{
      await copyShareText(shareText, event.currentTarget);
    }});
    if (savedBox) {{
      hide(savedBox);
      savedBox.innerHTML = '';
    }}
    resultBox.scrollIntoView({{ behavior: scrollBehavior, block: 'start' }});
  }}
  function startQuiz() {{
    localStorage.removeItem(storageKey);
    localStorage.removeItem(sharedStorageKey);
    renderSavedResult();
    preloadResultImages();
    current = 0;
    selected = null;
    answers.length = 0;
    hide(intro);
    hide(resultBox);
    show(quizBox);
    renderQuestion();
    quizBox.scrollIntoView({{ behavior: scrollBehavior, block: 'start' }});
  }}
  startButtons.forEach((button) => button.addEventListener('click', startQuiz));
  renderSavedResult();
}})();
</script>
"""


def supply_resume_script(lang: str) -> str:
    bookstore_label = AFFILIATE_COPY[lang]["button"]
    not_now_title = json.dumps(SUPPLY_LABELS[lang]["not_now"], ensure_ascii=False)
    not_now_text = json.dumps(SUPPLY_LABELS[lang]["not_now_text"], ensure_ascii=False)
    return f"""
{quiz_data_script_tag(lang)}
<script>
(() => {{
  const quiz = window.__LOVETYPES_QUIZ_DATA;
  if (!quiz) return;
  const bookstoreLabel = "{escape(bookstore_label)}";
  const notNowTitle = {not_now_title};
  const notNowText = {not_now_text};
  const box = document.querySelector('[data-supply-saved]');
  if (!box) return;
  const homePath = new URL(quiz.shareUrl).pathname;
  const storageKeys = ["lovetypes:{lang}:quiz-result", `lovetypes:${{location.pathname}}:quiz-result`, `lovetypes:${{homePath}}:quiz-result`];

  function readSavedResult() {{
    try {{
      for (const key of storageKeys) {{
        const saved = JSON.parse(localStorage.getItem(key) || 'null');
        if (saved && quiz.results[saved.primaryKey]) return saved;
      }}
    }} catch (error) {{}}
    return null;
  }}

  function resetEntryLinks() {{
    document.querySelectorAll('[data-supply-entry-link][data-default-href]').forEach((link) => {{
      link.setAttribute('href', link.getAttribute('data-default-href'));
      link.closest('[data-supply-entry-card]')?.removeAttribute('data-supply-entry-personalized');
    }});
  }}

  function clearSavedResult() {{
    storageKeys.forEach((key) => localStorage.removeItem(key));
    box.hidden = true;
    box.innerHTML = '';
    resetEntryLinks();
  }}

  function personalizeEntryLinks(result) {{
    const routeLink = document.querySelector('[data-supply-entry-link="routes"]');
    const lunaLink = document.querySelector('[data-supply-entry-link="luna"]');
    if (routeLink) {{
      routeLink.setAttribute('href', result.resourceUrl);
      routeLink.closest('[data-supply-entry-card]')?.setAttribute('data-supply-entry-personalized', 'true');
    }}
    if (lunaLink) {{
      lunaLink.setAttribute('href', result.lunaUrl);
      lunaLink.closest('[data-supply-entry-card]')?.setAttribute('data-supply-entry-personalized', 'true');
    }}
  }}

  const saved = readSavedResult();
  if (!saved) return;
  const result = quiz.results[saved.primaryKey];
  personalizeEntryLinks(result);
  const resumeSteps = [
    {{
      number: "1",
      title: quiz.labels.free_step,
      desc: result.supplyMission,
      href: result.planUrl,
      action: result.planLabel
    }},
    {{
      number: "2",
      title: quiz.labels.luna_step,
      desc: result.supplyText,
      href: result.lunaUrl,
      action: quiz.labels.luna_action
    }},
    {{
      number: "3",
      title: quiz.labels.book_step,
      desc: `${{quiz.labels.book_intro}}：${{result.supplyBook}}`,
      href: result.supplyBookUrl,
      action: bookstoreLabel,
      external: true
    }}
  ];
  box.innerHTML = `
    <article class="quiz-saved-card supply-resume-card pass-resume-card" style="--result-accent:${{result.domainAccent || result.color}};--domain-glow:${{result.domainGlow || result.color}}">
      <img class="supply-resume-portrait" src="${{result.resultImage}}" alt="${{result.name}}" width="${{result.resultImageWidth}}" height="${{result.resultImageHeight}}" loading="eager" decoding="async" fetchpriority="high">
      <div>
        <div class="resume-pass-stamp" data-resume-pass-stamp>
          <img class="resume-pass-prop" src="${{result.domainProp}}" alt="${{result.domainTitle}}" width="${{result.domainPropWidth}}" height="${{result.domainPropHeight}}" loading="lazy" decoding="async" fetchpriority="low">
          <span>${{quiz.labels.pass_title}}</span>
          <strong>${{result.domainTitle}}</strong>
        </div>
        <p class="eyebrow">${{quiz.labels.saved_title}}</p>
        <h2>${{result.supplyTitle}}</h2>
        <p>${{result.name}} · ${{result.type}}</p>
        <p class="resume-domain-line">${{result.domainDesc}}</p>
        <p>${{result.supplyDesc}}</p>
        <div class="supply-resume-next">
          ${{resumeSteps.map((step) => `
            <section>
              <span>${{step.number}}</span>
              <h3>${{step.title}}</h3>
              <p>${{step.desc}}</p>
              <a href="${{step.href}}" ${{step.external ? 'target="_blank" rel="noopener noreferrer sponsored"' : ''}}>${{step.action}}</a>
            </section>
          `).join('')}}
        </div>
        <div class="callout safety">
          <strong>${{notNowTitle}}</strong>
          <p>${{notNowText}}</p>
        </div>
        <div class="quiz-saved-actions">
          <a href="${{result.resourceUrl}}" data-supply-resume-route>${{quiz.labels.saved_route}}</a>
          <a href="${{result.planUrl}}" data-supply-resume-plan>${{quiz.labels.saved_plan}}</a>
          <a href="${{result.lunaUrl}}" data-supply-resume-luna>${{quiz.labels.saved_luna}}</a>
          <a href="${{result.collectorHallUrl}}" data-supply-resume-keepsake>${{quiz.labels.saved_card}}</a>
          <a href="${{result.contactUrl}}" data-supply-resume-contact>${{quiz.labels.saved_contact}}</a>
          <a href="${{result.guardianUrl}}" data-supply-resume-guardian>${{quiz.labels.guardian_link}}</a>
          <button type="button" data-clear-supply-result>${{quiz.labels.saved_clear}}</button>
        </div>
      </div>
    </article>`;
  box.hidden = false;
  box.querySelector('[data-clear-supply-result]').addEventListener('click', clearSavedResult);
  if (location.hash === `#supply-${{result.slug}}`) {{
    const focusResume = () => box.scrollIntoView({{ behavior: 'auto', block: 'start' }});
    window.requestAnimationFrame(focusResume);
    window.setTimeout(focusResume, 120);
    window.setTimeout(focusResume, 420);
  }}
}})();
</script>
"""


def supply_route_receipt_script(lang: str) -> str:
    labels = SUPPLY_LABELS[lang]
    summary_title = json.dumps(labels["route_summary_title"], ensure_ascii=False)
    summary_guardian = json.dumps(labels["route_summary_guardian"], ensure_ascii=False)
    summary_practice = json.dumps(labels["route_summary_practice"], ensure_ascii=False)
    summary_supply = json.dumps(labels["route_summary_supply"], ensure_ascii=False)
    summary_book = json.dumps(labels["route_summary_book"], ensure_ascii=False)
    copied = json.dumps(labels["route_copied"], ensure_ascii=False)
    return f"""
<script>
(() => {{
  const buttons = [...document.querySelectorAll('[data-copy-supply-route]')];
  if (!buttons.length) return;
  const labels = {{
    title: {summary_title},
    guardian: {summary_guardian},
    practice: {summary_practice},
    supply: {summary_supply},
    book: {summary_book},
    copied: {copied}
  }};

  async function copyText(text) {{
    if (navigator.clipboard?.writeText && window.isSecureContext) {{
      await navigator.clipboard.writeText(text);
      return;
    }}
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.left = '-9999px';
    document.body.appendChild(area);
    area.select();
    document.execCommand('copy');
    area.remove();
  }}

  function buildReceipt(route) {{
    return [
      labels.title,
      `${{labels.guardian}}: ${{route.guardian}}`,
      route.title,
      `${{labels.practice}}: ${{route.practice}}`,
      `${{labels.supply}}: ${{route.supply}}`,
      `${{labels.book}}: ${{route.book}}`,
      route.url
    ].filter(Boolean).join('\\n');
  }}

  buttons.forEach((button) => {{
    const original = button.textContent;
    button.addEventListener('click', async () => {{
      try {{
        const route = JSON.parse(button.dataset.routeSummary || '{{}}');
        await copyText(buildReceipt(route));
        button.textContent = labels.copied;
        window.setTimeout(() => {{ button.textContent = original; }}, 1800);
      }} catch (_error) {{
        button.textContent = original;
      }}
    }});
  }});
}})();
</script>
"""


def guide_resume_script(lang: str) -> str:
    return f"""
{quiz_data_script_tag(lang)}
<script>
(() => {{
  const quiz = window.__LOVETYPES_QUIZ_DATA;
  if (!quiz) return;
  const box = document.querySelector('[data-guide-saved]');
  if (!box) return;
  const homePath = new URL(quiz.shareUrl).pathname;
  const storageKeys = ["lovetypes:{lang}:quiz-result", `lovetypes:${{location.pathname}}:quiz-result`, `lovetypes:${{homePath}}:quiz-result`];

  function readSavedResult() {{
    try {{
      for (const key of storageKeys) {{
        const saved = JSON.parse(localStorage.getItem(key) || 'null');
        if (saved && quiz.results[saved.primaryKey]) return saved;
      }}
    }} catch (error) {{}}
    return null;
  }}

  function clearSavedResult() {{
    storageKeys.forEach((key) => localStorage.removeItem(key));
    box.hidden = true;
    box.innerHTML = '';
  }}

  const saved = readSavedResult();
  if (!saved) return;
  const result = quiz.results[saved.primaryKey];
  box.innerHTML = `
    <article class="quiz-saved-card guide-resume-card pass-resume-card" id="guide-resume-${{result.slug}}" style="--result-accent:${{result.domainAccent || result.color}};--domain-glow:${{result.domainGlow || result.color}}">
      <img src="${{result.resultImage}}" alt="${{result.name}}" width="${{result.resultImageWidth}}" height="${{result.resultImageHeight}}" loading="lazy" decoding="async" fetchpriority="low">
      <div>
        <div class="resume-pass-stamp" data-resume-pass-stamp>
          <img class="resume-pass-prop" src="${{result.domainProp}}" alt="${{result.domainTitle}}" width="${{result.domainPropWidth}}" height="${{result.domainPropHeight}}" loading="lazy" decoding="async" fetchpriority="low">
          <span>${{quiz.labels.pass_title}}</span>
          <strong>${{result.domainTitle}}</strong>
        </div>
        <p class="eyebrow">${{quiz.labels.guide_resume_title}}</p>
        <h2>${{result.name}} · ${{result.type}}</h2>
        <p>${{quiz.labels.guide_resume_intro}}</p>
        <div class="quiz-saved-actions">
          <a href="${{result.planUrl}}" data-guide-resume-plan>${{quiz.labels.saved_plan}}</a>
          <a href="${{result.resourceUrl}}" data-guide-resume-route>${{quiz.labels.saved_route}}</a>
          <a href="${{result.lunaUrl}}" data-guide-resume-luna>${{quiz.labels.saved_luna}}</a>
          <a href="${{result.collectorHallUrl}}" data-guide-resume-keepsake>${{quiz.labels.saved_card}}</a>
          <a href="${{result.contactUrl}}" data-guide-resume-contact>${{quiz.labels.saved_contact}}</a>
          <a href="${{result.guardianUrl}}" data-guide-resume-guardian>${{quiz.labels.guardian_link}}</a>
          <button type="button" data-clear-guide-result>${{quiz.labels.saved_clear}}</button>
        </div>
      </div>
    </article>`;
  box.hidden = false;
  box.querySelector('[data-clear-guide-result]').addEventListener('click', clearSavedResult);
  if (location.hash === `#guide-${{result.slug}}`) {{
    const focusResume = () => box.scrollIntoView({{ behavior: 'auto', block: 'start' }});
    window.requestAnimationFrame(focusResume);
    window.setTimeout(focusResume, 120);
    window.setTimeout(focusResume, 420);
  }}
}})();
</script>
"""


def guardian_resume_script(lang: str, current_slug: str = "") -> str:
    current = json.dumps(current_slug)
    return f"""
{quiz_data_script_tag(lang)}
<script>
(() => {{
  const quiz = window.__LOVETYPES_QUIZ_DATA;
  if (!quiz) return;
  const currentSlug = {current};
  const box = document.querySelector('[data-guardian-saved]');
  if (!box) return;
  const homePath = new URL(quiz.shareUrl).pathname;
  const storageKeys = ["lovetypes:{lang}:quiz-result", `lovetypes:${{location.pathname}}:quiz-result`, `lovetypes:${{homePath}}:quiz-result`];

  function normalizeSaved(saved) {{
    if (!saved || typeof saved !== 'object') return null;
    const primaryKey = saved.primaryKey || saved.type;
    if (!primaryKey || !quiz.results[primaryKey]) return null;
    return {{ ...saved, primaryKey }};
  }}

  function readSavedResult() {{
    try {{
      for (const key of storageKeys) {{
        const saved = normalizeSaved(JSON.parse(localStorage.getItem(key) || 'null'));
        if (saved) return saved;
      }}
    }} catch (error) {{}}
    return null;
  }}

  function clearSavedResult() {{
    storageKeys.forEach((key) => localStorage.removeItem(key));
    box.hidden = true;
    box.innerHTML = '';
  }}

  const saved = readSavedResult();
  if (!saved) return;
  const result = quiz.results[saved.primaryKey];
  const isCurrent = currentSlug && currentSlug === result.slug;
  const intro = currentSlug
    ? (isCurrent ? quiz.labels.guardian_resume_match : quiz.labels.guardian_resume_other)
    : quiz.labels.guardian_resume_intro;
  const primaryHref = currentSlug && !isCurrent ? result.guardianUrl : result.resourceUrl;
  const primaryLabel = currentSlug && !isCurrent ? quiz.labels.guardian_link : quiz.labels.saved_route;
  box.innerHTML = `
    <article class="guardian-resume-card pass-resume-card" id="guardian-result-${{result.slug}}" style="--result-accent:${{result.domainAccent || result.color}};--domain-glow:${{result.domainGlow || result.color}}">
      <img src="${{result.resultImage}}" alt="${{result.name}}" width="${{result.resultImageWidth}}" height="${{result.resultImageHeight}}" loading="lazy" decoding="async" fetchpriority="low">
      <div>
        <div class="resume-pass-stamp" data-resume-pass-stamp>
          <img class="resume-pass-prop" src="${{result.domainProp}}" alt="${{result.domainTitle}}" width="${{result.domainPropWidth}}" height="${{result.domainPropHeight}}" loading="lazy" decoding="async" fetchpriority="low">
          <span>${{quiz.labels.pass_title}}</span>
          <strong>${{result.domainTitle}}</strong>
        </div>
        <p class="eyebrow">${{quiz.labels.guardian_resume_title}}</p>
        <h2>${{result.name}} · ${{result.type}}</h2>
        <p>${{intro}}</p>
        <p class="resume-domain-line">${{result.domainDesc}}</p>
        <div class="guardian-resume-actions">
          <a class="primary-btn" href="${{primaryHref}}" data-guardian-resume-primary>${{primaryLabel}}</a>
          <a class="secondary-btn" href="${{result.guardianUrl}}" data-guardian-resume-guardian>${{quiz.labels.guardian_link}}</a>
          <a class="secondary-btn" href="${{result.planUrl}}" data-guardian-resume-plan>${{quiz.labels.saved_plan}}</a>
          <a class="secondary-btn" href="${{result.collectorHallUrl}}" data-guardian-resume-keepsake>${{quiz.labels.saved_card}}</a>
          <a class="secondary-btn" href="${{result.lunaUrl}}" data-guardian-resume-luna>${{quiz.labels.saved_luna}}</a>
          <a class="secondary-btn" href="${{result.contactUrl}}" data-guardian-resume-contact>${{quiz.labels.saved_contact}}</a>
          <button class="secondary-btn" type="button" data-clear-guardian-result>${{quiz.labels.saved_clear}}</button>
        </div>
      </div>
    </article>`;
  box.hidden = false;
  box.querySelector('[data-clear-guardian-result]').addEventListener('click', clearSavedResult);
  if (location.hash === `#guardian-result-${{result.slug}}`) {{
    const focusResume = () => box.scrollIntoView({{ behavior: 'auto', block: 'start' }});
    window.requestAnimationFrame(focusResume);
    window.setTimeout(focusResume, 120);
    window.setTimeout(focusResume, 420);
  }}
}})();
</script>
"""


def home(lang: str) -> None:
    t = LANGS[lang]
    quiz = QUIZ_LABELS[lang]
    section_labels = SECTION_LABELS[lang]
    guide_cards = "".join(guide_card(lang, g) for g in GUIDES[:6])
    guardian_cards = "".join(character_card(lang, slug, data) for slug, data in GUARDIANS.items())
    body = f"""
<section class="hero">
  <div class="hero-copy">
    <p class="eyebrow">{escape(section_labels["home_field_notes"])}</p>
    <h1>{escape(t["brand"])}</h1>
    <p class="lead">{escape(t["tagline"])}</p>
    <div class="hero-actions"><a class="primary-btn" href="#quiz-section">{escape(t["start"])}</a><a class="secondary-btn" href="{lang_url(lang, "garden-map")}">{escape(t["map"])}</a></div>
  </div>
  <picture><source media="(max-width: 720px)" srcset="/assets/lovetypes/backgrounds/guardian-garden-mobile.webp" width="900" height="506" />{img_tag("/assets/lovetypes/backgrounds/guardian-garden.webp", "LoveTypes guardian garden", lazy=False, priority=True)}</picture>
</section>
{universe_gate_section(lang)}
<section class="section quiz-saved home-result-resume" data-home-saved hidden aria-live="polite"></section>
{home_journey_section(lang)}
<section class="section intro-grid">
  <div><p class="eyebrow">{escape(section_labels["universe_promise"])}</p><h2>{escape(section_labels["home_field_notes"])}</h2><p>{escape(t["trust_intro"])}</p></div>
  <div class="text-stack"><p>{escape(PRACTICAL_COPY[lang]["why"])}</p><p>{escape(PRACTICAL_COPY[lang]["notice"])}</p></div>
</section>
<section class="section" id="guides-section"><div class="section-head"><p class="eyebrow">{escape(section_labels["guardian_field_guides"])}</p><h2>{escape(t["guides"])}</h2><a href="{lang_url(lang, "guides")}">{escape(t["learn_more"])}</a></div><div class="card-grid">{guide_cards}</div></section>
<section class="section" id="types-section"><div class="section-head"><p class="eyebrow">{escape(section_labels["five_guardians"])}</p><h2>{escape(t["guardians"])}</h2><a href="{lang_url(lang, "characters")}">{escape(t["learn_more"])}</a></div><div class="guardian-grid">{guardian_cards}</div></section>
<section class="quiz-band" id="quiz-section" tabindex="-1">
  <div class="quiz-shell" data-quiz-root>
    <div class="quiz-intro" data-quiz-intro>
      <p class="eyebrow">{escape(quiz["eyebrow"])}</p>
      <h2>{escape(quiz["title"])}</h2>
      <p>{escape(quiz["intro"])}</p>
      <button type="button" class="primary-btn" data-quiz-start>{escape(quiz["start"])}</button>
    </div>
    <div class="quiz-saved" data-quiz-saved hidden aria-live="polite"></div>
    <div class="quiz-stage" data-quiz-box hidden aria-live="polite"></div>
    <div class="quiz-result" data-quiz-result hidden aria-live="polite"></div>
  </div>
</section>
"""
    schema = json_ld({
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": f"{abs_url(lang)}#website",
        "name": t["brand"],
        "url": abs_url(lang),
        "inLanguage": t["code"],
        "dateModified": UPDATED,
        "publisher": organization_ref(),
    })
    write(page_path(lang), layout(lang, t["home_title"], t["home_desc"], "", body + quiz_script(lang), "", "website", "/og-cover.jpg", schema))


def characters_index_page(lang: str) -> None:
    t = LANGS[lang]
    copy = CHARACTER_INDEX_COPY[lang]
    section_labels = SECTION_LABELS[lang]
    title = copy["title"]
    desc = copy["desc"]
    body = f"""
<section class="page-hero compact guardian-index-hero">
  <p class="eyebrow">{escape(section_labels["five_guardians"])}</p>
  <h1>{escape(copy["h1"])}</h1>
  <p>{escape(copy["intro"])}</p>
  <div class="hero-actions"><a class="primary-btn" href="{lang_url(lang)}#quiz-section">{escape(t["start"])}</a><a class="secondary-btn" href="{lang_url(lang, "guides")}">{escape(t["guides"])}</a></div>
</section>
<section class="section guardian-result-resume" data-guardian-saved hidden aria-live="polite"></section>
{guardian_entry_section(lang)}
{guardian_need_router_section(lang)}
{universe_map_section(lang)}
<section class="section intro-grid">
  <div><h2>{escape(PAGE_SECTIONS[lang]["how"])}</h2><p>{escape(PRACTICAL_COPY[lang]["why"])}</p></div>
  <div class="text-stack"><h2>{escape(PAGE_SECTIONS[lang]["need"])}</h2><p>{escape(PRACTICAL_COPY[lang]["notice"])}</p><p>{escape(PRACTICAL_COPY[lang]["practice"])}</p></div>
</section>
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"CollectionPage","name":"{escape(copy["h1"])}","description":"{escape(desc)}","url":"{abs_url(lang, "characters")}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
    guardian_items = [(data[lang][0], abs_url(lang, "characters/" + slug)) for slug, data in GUARDIANS.items()]
    schema += item_list_schema(copy["h1"], desc, guardian_items)
    write(page_path(lang, "characters"), layout(lang, title, desc, "characters", body + guardian_resume_script(lang), t["guardians"], "website", "/og-cover.jpg", schema))


def guides_index(lang: str) -> None:
    t = LANGS[lang]
    section_labels = SECTION_LABELS[lang]
    cards = "".join(guide_card(lang, g) for g in GUIDES)
    body = f"""
<section class="page-hero compact"><p class="eyebrow">{escape(section_labels["heart_garden_field_guide"])}</p><h1>{escape(t["guide_index_title"])}</h1><p>{escape(t["guide_index_desc"])}</p><div class="hero-actions" data-guide-index-actions><a class="primary-btn" data-guide-index-link="quiz" href="{lang_url(lang)}#quiz-section">{escape(t["start"])}</a><a class="secondary-btn" data-guide-index-link="guardians" href="{lang_url(lang, "characters")}">{escape(t["guardians"])}</a><a class="secondary-btn" data-guide-index-link="resources" href="{lang_url(lang, "resources")}">{escape(t["resources"])}</a></div></section>
{guide_index_compass(lang)}
{guide_domain_routes_section(lang)}
<section class="section"><div class="card-grid wide">{cards}</div></section>
<section class="section note-section"><h2>{escape(t["boundary"])}</h2><p>{escape(t["boundary_text"])}</p></section>
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"CollectionPage","name":"{escape(t["guide_index_title"])}","description":"{escape(t["guide_index_desc"])}","url":"{abs_url(lang, "guides")}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
    guide_items = [(guide[lang][0], abs_url(lang, "guides/" + guide["slug"])) for guide in GUIDES]
    schema += item_list_schema(t["guide_index_title"], t["guide_index_desc"], guide_items)
    write(page_path(lang, "guides"), layout(lang, t["guide_index_title"], t["guide_index_desc"], "guides", body, t["guides"], "website", "/og-cover.jpg", schema))


def guide_action_bridge(lang: str, guide: dict) -> str:
    copy = GUIDE_ACTION_BRIDGE[lang]
    slug = guide["guardian"]
    guardian_name = GUARDIANS[slug][lang][0]
    route = supply_route(lang, slug)
    actions = [
        (
            "01",
            copy["guardian_label"],
            copy["guardian_text"],
            copy["guardian_cta"],
            lang_url(lang, f"characters/{slug}"),
        ),
        (
            "02",
            copy["route_label"],
            f'{copy["route_text"]} {route["title"]}',
            copy["route_cta"],
            f'{lang_url(lang, "resources")}#supply-{slug}',
        ),
        (
            "03",
            copy["plan_label"],
            copy["plan_text"],
            copy["plan_cta"],
            f'{lang_url(lang, "repair-plan")}#plan-{slug}',
        ),
        (
            "04",
            copy["luna_label"],
            copy["luna_text"],
            copy["luna_cta"],
            f'{lang_url(lang, "luna-yoga-music")}#luna-{slug}',
        ),
    ]
    cards = "".join(
        f"""
<article class="guide-action-card">
  <span>{step}</span>
  <h3>{escape(label)}</h3>
  <p>{escape(text)}</p>
  <a href="{href}">{escape(cta)}</a>
</article>
"""
        for step, label, text, cta, href in actions
    )
    return f"""
<span id="guide-{slug}" class="anchor-offset" aria-hidden="true"></span>
<section class="section guide-action-bridge" id="guide-action-bridge" data-guide-action-bridge style="--guardian-accent:{GUARDIAN_DOMAINS[slug]["accent"]}">
  <div class="section-intro">
    <p class="eyebrow">{escape(copy["eyebrow"])}</p>
    <h2>{escape(copy["title"])}</h2>
    <p>{escape(copy["intro"])}</p>
    <p class="guide-action-guardian">{escape(guardian_name)}</p>
  </div>
  <div class="guide-action-grid">{cards}</div>
</section>
"""


def trust_action_routes(lang: str, slug: str) -> str:
    copy = TRUST_ACTION_ROUTES[lang][slug]
    section_labels = SECTION_LABELS[lang]
    heading = section_labels["trust_routes"] if slug == "about" else section_labels["week_route"]
    cards = []
    for step, title, desc, cta, target in copy["items"]:
        href = f"{lang_url(lang)}#quiz-section" if not target else lang_url(lang, target)
        cards.append(f"""
<article class="trust-action-card">
  <span>{escape(step)}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
  <a href="{href}">{escape(cta)}</a>
</article>
""")
    return f"""
<section class="section trust-action-section" id="trust-action-routes">
  <div class="section-head">
    <div><p class="eyebrow">{escape(copy["eyebrow"])}</p><h2>{escape(heading)}</h2><p>{escape(copy["title"])}</p></div>
  </div>
  <p class="trust-action-intro">{escape(copy["intro"])}</p>
  <div class="trust-action-grid">{"".join(cards)}</div>
</section>
"""


def guide_page(lang: str, guide: dict, index: int) -> None:
    t = LANGS[lang]
    labels = TOPIC_DETAILS[lang]
    title, desc = guide[lang]
    guardian = GUARDIANS[guide["guardian"]][lang]
    detail = guide_detail_copy(lang, title, desc, guardian)
    related = [g for g in GUIDES if g["slug"] != guide["slug"]]
    next_a = related[(index + 1) % len(related)]
    next_b = related[(index + 4) % len(related)]
    scripts = "".join(f"<li>{escape(item)}</li>" for item in detail["scripts"])
    reflections = "".join(f"<li>{escape(item)}</li>" for item in detail["reflection"])
    body = f"""
<section class="article-hero">
  <div><p class="eyebrow">{escape(guardian[1])}</p><h1>{escape(title)}</h1><p>{escape(desc)}</p></div>
  {img_tag(GUARDIANS[guide["guardian"]]["prop"], guardian[1], lazy=False, priority=True)}
</section>
<section class="section guide-personal-resume" data-guide-saved hidden aria-live="polite"></section>
<section class="article-shell">
  <article class="article-body">
    <p class="lede">{escape(detail["lede"])}</p>
    <h2>{escape(labels["why"])}</h2><p>{escape(detail["why"])}</p>
    <h2>{escape(labels["notice"])}</h2><p>{escape(detail["notice"])}</p>
    <h2>{escape(labels["scripts"])}</h2><ul>{scripts}</ul>
    <h2>{escape(labels["practice"])}</h2><p>{escape(detail["practice"])}</p>
    <div class="callout"><strong>{escape(t["practice"])}</strong><p>{escape(guardian[2])}</p></div>
    <h2>{escape(labels["mistakes"])}</h2><p>{escape(detail["mistakes"])}</p>
    <h2>{escape(labels["reflection"])}</h2><ol>{reflections}</ol>
    <div class="callout safety"><strong>{escape(t["boundary"])}</strong><p>{escape(t["boundary_text"])}</p></div>
  </article>
  <aside class="article-side">
    <h2>{escape(labels["next"])}</h2>
    {guide_card(lang, next_a)}
    {guide_card(lang, next_b)}
  </aside>
</section>
{guide_action_bridge(lang, guide)}
"""
    schema = json_ld({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc,
        "url": abs_url(lang, "guides/" + guide["slug"]),
        "inLanguage": t["code"],
        "dateModified": UPDATED,
        "image": f"{DOMAIN}/assets/lovetypes/share/guide-toolkit-og.jpg",
        "author": organization_ref(),
        "publisher": organization_ref(),
        "isPartOf": website_ref(lang),
        "mainEntityOfPage": {"@type": "WebPage", "@id": abs_url(lang, "guides/" + guide["slug"])},
    })
    write(page_path(lang, "guides/" + guide["slug"]), layout(lang, title, desc, "guides/" + guide["slug"], body + guide_resume_script(lang), t["guides"], "article", "/assets/lovetypes/share/guide-toolkit-og.jpg", schema))


def legacy_zh_guide_page(slug: str, title: str, desc: str, canonical_target: str) -> None:
    lang = "zh"
    t = LANGS[lang]
    related = next(g for g in GUIDES if g["slug"] == canonical_target)
    related_title, _related_desc = related[lang]
    guardian_slug = related["guardian"]
    guardian_name = GUARDIANS[guardian_slug][lang][0]
    guardian = GUARDIANS[related["guardian"]][lang]
    detail = guide_detail_copy(lang, title, desc, guardian)
    canonical_path = "guides/" + canonical_target
    supply_href = f'{lang_url(lang, "resources")}#supply-{guardian_slug}'
    plan_href = f'{lang_url(lang, "repair-plan")}#plan-{guardian_slug}'
    body = f"""
<section class="article-hero">
  <div><p class="eyebrow">{escape(SECTION_LABELS[lang]["heart_garden_archive"])}</p><h1>{escape(title)}</h1><p>{escape(desc)}</p></div>
  {img_tag("/assets/lovetypes/share/guide-toolkit-og.jpg", "LoveTypes guide", lazy=False)}
</section>
<section class="section note-section archive-forward">
  <h2>這是舊版心語入口</h2>
  <p>這一頁保留給從舊連結抵達的旅人；目前主要路線已整理到「{escape(related_title)}」。如果你已經知道自己靠近 {escape(guardian_name)} 的分域，也可以直接接上補給或修復計畫。</p>
  <div class="hero-actions legacy-forward-actions" data-legacy-forward-actions>
    <a class="primary-btn" data-legacy-forward-link="formal" href="{lang_url(lang, canonical_path)}">前往正式指南</a>
    <a class="secondary-btn" data-legacy-forward-link="supply" href="{supply_href}">取得{escape(guardian_name)}補給</a>
    <a class="secondary-btn" data-legacy-forward-link="repair" href="{plan_href}">填入 7 日修復</a>
  </div>
</section>
<section class="section guide-personal-resume" data-guide-saved hidden aria-live="polite"></section>
<section class="article-shell">
  <article class="article-body">
    <p class="lede">{escape(desc)} 這一頁保留原有主題，並把它放回心語庭園的語境：先辨認錯頻，再找到能被接收的修復方式。</p>
    <h2>先把守護者結果翻成真實需求</h2>
    <p>{escape(detail["notice"])}</p>
    <h2>把理解變成一盞可以點亮的小燈</h2>
    <p>{escape(detail["practice"])}</p>
    <h2>可以直接開口的句型</h2>
    <ul>{"".join(f"<li>{escape(item)}</li>" for item in detail["scripts"])}</ul>
    <h2>不要讓守護者類型取代溝通</h2>
    <p>{escape(detail["mistakes"])}</p>
    <div class="callout safety"><strong>{escape(t["boundary"])}</strong><p>{escape(t["boundary_text"])}</p></div>
  </article>
  <aside class="article-side"><h2>延伸閱讀</h2>{guide_card(lang, related)}</aside>
</section>
{guide_action_bridge(lang, related)}
"""
    schema = json_ld({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc,
        "url": abs_url(lang, canonical_path),
        "inLanguage": t["code"],
        "dateModified": UPDATED,
        "image": f"{DOMAIN}/assets/lovetypes/share/guide-toolkit-og.jpg",
        "author": organization_ref(),
        "publisher": organization_ref(),
        "isPartOf": website_ref(lang),
        "mainEntityOfPage": {"@type": "WebPage", "@id": abs_url(lang, canonical_path)},
    })
    write(page_path(lang, "guides/" + slug), layout(lang, title, desc, "guides/" + slug, body + guide_resume_script(lang), t["guides"], "article", "/assets/lovetypes/share/guide-toolkit-og.jpg", schema, alternate_path=canonical_path, canonical_path=canonical_path, robots="noindex, follow"))


def character_page(lang: str, slug: str, data: dict) -> None:
    t = LANGS[lang]
    labels = PAGE_SECTIONS[lang]
    section_labels = SECTION_LABELS[lang]
    name, typ, desc = data[lang]
    domain_title, domain_desc, domain_cta = GUARDIAN_DOMAINS[slug][lang]
    domain = GUARDIAN_DOMAINS[slug]
    detail = character_detail_copy(lang, name, typ, desc)
    related_guides = [g for g in GUIDES if g["guardian"] == slug][:3]
    related_html = "".join(guide_card(lang, g) for g in related_guides)
    guardian_nav = "".join(character_link_card(lang, item_slug, item_data, slug) for item_slug, item_data in GUARDIANS.items())
    scripts = "".join(f"<li>{escape(item)}</li>" for item in detail["scripts"])
    reflections = "".join(f"<li>{escape(item)}</li>" for item in detail["reflection"])
    body = f"""
<section class="guardian-hero guardian-domain-hero" data-guardian-domain="{slug}" style="--domain-accent:{domain["accent"]};--domain-glow:{domain["glow"]}">
  <div><p class="eyebrow">{escape(typ)}</p><h1>{escape(name)}</h1><p class="domain-title">{escape(domain_title)}</p><p>{escape(desc)}</p><p>{escape(domain_desc)}</p><div class="hero-actions"><a class="primary-btn" href="{lang_url(lang, "resources")}#supply-{slug}">{escape(SUPPLY_LABELS[lang]["route"])}</a><a class="secondary-btn" href="{lang_url(lang)}#quiz-section">{escape(t["start"])}</a><a class="secondary-btn" href="{lang_url(lang, "characters")}">{escape(t["guardians"])}</a></div></div>
  {img_tag(data["asset"], name, lazy=False, priority=True)}
</section>
<section class="section guardian-result-resume" data-guardian-saved hidden aria-live="polite"></section>
<section class="section domain-rune-section" data-domain-marker>
  <div class="domain-rune-card" style="--domain-accent:{domain["accent"]};--domain-glow:{domain["glow"]}">
    {img_tag(data["prop"], domain_title)}
    <div><p class="eyebrow">{escape(domain_title)}</p><h2>{escape(domain_cta)}</h2><p>{escape(domain_desc)}</p></div>
  </div>
</section>
{character_route_snapshot(lang, slug)}
<section class="section intro-grid">
  <div><h2>{escape(labels["how"])}</h2><p>{escape(detail["how"])}</p><p>{escape(desc)}</p></div>
  <div class="text-stack"><h2>{escape(labels["need"])}</h2><p>{escape(detail["need"])}</p><p>{escape(detail["practice"])}</p></div>
</section>
<section class="section article-body standalone">
  <h2>{escape(labels["use"])}</h2>
  <p>{SITE_COPY[lang]["guardian_use"].format(name=escape(name))}</p>
  <h2>{escape(TOPIC_DETAILS[lang]["scripts"])}</h2>
  <ul>{scripts}</ul>
  <h2>{escape(TOPIC_DETAILS[lang]["reflection"])}</h2>
  <ol>{reflections}</ol>
  <div class="callout safety"><strong>{escape(t["boundary"])}</strong><p>{escape(t["boundary_text"])}</p></div>
</section>
{character_supply_panel(lang, slug)}
{collector_section(lang, slug)}
<section class="section"><div class="section-head"><p class="eyebrow">{escape(section_labels["related_guides"])}</p><h2>{escape(t["read"])}</h2></div><div class="card-grid">{related_html}</div></section>
<section class="section guardian-nav-section"><div class="section-head"><p class="eyebrow">{escape(section_labels["five_guardians"])}</p><h2>{escape(t["guardians"])}</h2><a href="{lang_url(lang, "characters")}">{escape(t["learn_more"])}</a></div><div class="guardian-grid compact">{guardian_nav}</div></section>
"""
    schema = json_ld({
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "name": name,
        "description": desc,
        "url": abs_url(lang, "characters/" + slug),
        "inLanguage": t["code"],
        "image": f"{DOMAIN}/assets/lovetypes/share/{slug}-og.jpg",
        "about": {"@type": "Thing", "name": typ},
        "dateModified": UPDATED,
        "isPartOf": website_ref(lang),
    })
    write(page_path(lang, "characters/" + slug), layout(lang, f"{name} | {typ} | LoveTypes", desc, "characters/" + slug, body + guardian_resume_script(lang, slug), t["guardians"], "profile", f"/assets/lovetypes/share/{slug}-og.jpg", schema))


def resources_page(lang: str) -> None:
    t = LANGS[lang]
    section_labels = SECTION_LABELS[lang]
    affiliate_labels = AFFILIATE_COPY[lang]
    supply_labels = SUPPLY_LABELS[lang]
    decision = SUPPLY_DECISION[lang]
    resource_steps = "".join(f"<article><span>{idx}</span><h3>{escape(title)}</h3><p>{escape(desc)}</p></article>" for idx, (title, desc) in enumerate(RESOURCE_PATHS[lang], start=1))
    decision_steps = "".join(f"<article><span>{escape(number)}</span><h3>{escape(title)}</h3><p>{escape(desc)}</p></article>" for number, title, desc in decision["steps"])
    supply_cards = "".join(supply_route_card(lang, slug) for slug in GUARDIANS)
    cards = []
    for path, title, desc in RESOURCE_CARDS[lang]:
        image = ""
        if path == "luna-yoga-music":
            image = f'  {img_tag("/luna-yoga-music/images/icon.webp", title)}\n'
        cards.append(f"""
<a class="content-card resource-card" href="{lang_url(lang, path)}">
{image}  <span class="eyebrow">{escape(section_labels["traveler_supply"])}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
  <span class="card-link">{escape(t["learn_more"])}</span>
</a>
""")
    book_cards = []
    for book_index, book in enumerate(AFFILIATE_BOOKS):
        matching_routes = []
        for slug in GUARDIANS:
            if SUPPLY_ROUTES[slug]["book"] != book_index:
                continue
            route = supply_route(lang, slug)
            guardian_name, _guardian_type, _guardian_desc = route["guardian"][lang]
            matching_routes.append(f'<a class="affiliate-route-tag" href="#supply-{slug}">{escape(guardian_name)} · {escape(route["title"])}</a>')
        route_tags = "".join(matching_routes)
        book_cards.append(f"""
<article class="affiliate-book-card">
  <div class="affiliate-book-icon">{escape(book["emoji"])}</div>
  <span class="eyebrow">{escape(book["tag"][lang])}</span>
  <h3>{escape(book["title"][lang])}</h3>
  <p class="affiliate-author">{escape(book["author"])}</p>
  <p>{escape(book["desc"][lang])}</p>
  <p><strong>{escape(affiliate_labels["fit"])}:</strong> {escape(book["fit"][lang])}</p>
  <p><strong>{escape(affiliate_labels["limit"])}:</strong> {escape(book["limit"][lang])}</p>
  <div class="affiliate-route-match"><span>{escape(affiliate_labels["routes"])}</span><div>{route_tags}</div></div>
  <a class="primary-btn affiliate-book-link" href="{book["url"]}" target="_blank" rel="noopener noreferrer sponsored">{escape(affiliate_labels["button"])}</a>
</article>
""")
    body = f"""
<section class="page-hero compact supply-hero"><p class="eyebrow">{escape(section_labels["heart_garden_supplies"])}</p><h1>{escape(t["resources"])}</h1><p>{escape(t["resources_desc"])}</p>{supply_hero_actions(lang)}<p class="affiliate-disclosure">{escape(AFFILIATE_DISCLOSURE[lang])}</p></section>
<section class="section quiz-saved supply-personal-resume" data-supply-saved hidden aria-live="polite"></section>
{supply_quick_route_nav(lang)}
{supply_entry_section(lang)}
<section class="section resource-path"><div><p class="eyebrow">{escape(section_labels["supply_route"])}</p><h2>{escape(section_labels["main_routes"])}</h2><p class="section-intro">{escape(t["resources_desc"])}</p></div><div class="resource-steps">{resource_steps}</div></section>
<section class="section supply-compass">
  <div class="section-head"><div><p class="eyebrow">{escape(decision["eyebrow"])}</p><h2>{escape(decision["title"])}</h2></div></div>
  <p class="section-intro">{escape(decision["intro"])}</p>
  <div class="supply-compass-grid">{decision_steps}</div>
</section>
{supply_decision_matrix(lang)}
{starter_kit_section(lang)}
<section class="section supply-routes" id="supply-routes">
  <div class="section-head"><div><p class="eyebrow">{escape(supply_labels["eyebrow"])}</p><h2>{escape(supply_labels["title"])}</h2></div></div>
  <p class="section-intro">{escape(supply_labels["intro"])}</p>
  <div class="supply-route-grid">{supply_cards}</div>
</section>
<section class="section intro-grid supply-trust">
  <div><h2>{escape(supply_labels["choose"])}</h2><p>{escape(supply_labels["choose_text"])}</p></div>
  <div><h2>{escape(supply_labels["not_now"])}</h2><p>{escape(supply_labels["not_now_text"])}</p></div>
</section>
{supply_wishlist_section(lang)}
{collector_section(lang)}
<section class="section"><div class="card-grid wide">{"".join(cards)}</div></section>
<section class="section affiliate-books" id="affiliate-books"><div class="section-head"><p class="eyebrow">{escape(affiliate_labels["eyebrow"])}</p><h2>{escape(affiliate_labels["title"])}</h2></div><p>{escape(affiliate_labels["intro"])}</p><div class="affiliate-book-grid">{"".join(book_cards)}</div><p class="affiliate-disclosure">{escape(AFFILIATE_DISCLOSURE[lang])}</p><p class="affiliate-link-note">{escape(affiliate_labels["fallback"])}</p></section>
<section class="section note-section"><h2>{escape(t["boundary"])}</h2><p>{escape(t["boundary_text"])}</p></section>
{supply_resume_script(lang)}
{supply_route_receipt_script(lang)}
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"CollectionPage","name":"{escape(t["resources"])}","description":"{escape(t["resources_desc"])}","url":"{abs_url(lang, "resources")}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
    route_items = [(supply_route(lang, slug)["title"], abs_url(lang, "resources") + f"#supply-{slug}") for slug in GUARDIANS]
    schema += item_list_schema(supply_labels["title"], supply_labels["intro"], route_items)
    page_title = f"{t['resources']} | LoveTypes" if lang == "zh" else f"{t['resources']} | LoveTypes {t['name']}"
    write(page_path(lang, "resources"), layout(lang, page_title, t["resources_desc"], "resources", body, t["resources"], "website", "/og-cover.jpg", schema, affiliate=True))


def repair_worksheet_script(lang: str) -> str:
    plan = REPAIR_PLAN[lang]
    saved = json.dumps(plan["saved"], ensure_ascii=False)
    cleared = json.dumps(plan["cleared"], ensure_ascii=False)
    copy_summary = json.dumps(plan["copy_summary"], ensure_ascii=False)
    summary_title = json.dumps(plan["summary_title"], ensure_ascii=False)
    summary_guardian = json.dumps(plan["summary_guardian"], ensure_ascii=False)
    summary_next = json.dumps(plan["summary_next"], ensure_ascii=False)
    summary_copied = json.dumps(plan["summary_copied"], ensure_ascii=False)
    summary_empty = json.dumps(plan["summary_empty"], ensure_ascii=False)
    field_labels = json.dumps([field[0] for field in plan["fields"]], ensure_ascii=False)
    resume_title = json.dumps(plan["resume_title"], ensure_ascii=False)
    resume_intro = json.dumps(plan["resume_intro"], ensure_ascii=False)
    resume_fill = json.dumps(plan["resume_fill"], ensure_ascii=False)
    resume_plan = json.dumps(plan["resume_plan"], ensure_ascii=False)
    bookstore_label = json.dumps(AFFILIATE_COPY[lang]["button"], ensure_ascii=False)
    return f"""
{quiz_data_script_tag(lang)}
<script>
(() => {{
  const quiz = window.__LOVETYPES_QUIZ_DATA;
  if (!quiz) return;
  const resumeTitle = {resume_title};
  const resumeIntro = {resume_intro};
  const resumeFill = {resume_fill};
  const resumePlan = {resume_plan};
  const bookstoreLabel = {bookstore_label};
  const copySummaryLabel = {copy_summary};
  const summaryTitle = {summary_title};
  const summaryGuardian = {summary_guardian};
  const summaryNext = {summary_next};
  const summaryCopied = {summary_copied};
  const summaryEmpty = {summary_empty};
  const fieldLabels = {field_labels};
  const form = document.querySelector('[data-repair-worksheet]');
  if (!form) return;
  const fields = [...form.querySelectorAll('textarea[data-field]')];
  const status = document.querySelector('[data-worksheet-status]');
  const clearButton = document.querySelector('[data-clear-worksheet]');
  const copyButton = document.querySelector('[data-copy-worksheet-summary]');
  const resumeBox = document.querySelector('[data-repair-saved]');
  const key = `lovetypes:${{location.pathname}}:repair-worksheet`;
  const homePath = new URL(quiz.shareUrl).pathname;
  const resultKeys = ["lovetypes:{lang}:quiz-result", `lovetypes:${{homePath}}:quiz-result`];
  const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const scrollBehavior = reduceMotion ? 'auto' : 'smooth';
  let timer = 0;

  function setStatus(message) {{
    if (status) status.textContent = message;
  }}

  function readStorage() {{
    try {{
      return JSON.parse(localStorage.getItem(key) || '[]');
    }} catch (_error) {{
      return [];
    }}
  }}

  function writeStorage() {{
    try {{
      localStorage.setItem(key, JSON.stringify(fields.map((field) => field.value)));
      setStatus({saved});
    }} catch (_error) {{
      return;
    }}
  }}

  function readSavedResult() {{
    try {{
      for (const resultKey of resultKeys) {{
        const savedResult = JSON.parse(localStorage.getItem(resultKey) || 'null');
        const primaryKey = savedResult && (savedResult.primaryKey || savedResult.type);
        if (primaryKey && quiz.results[primaryKey]) return {{ ...savedResult, primaryKey }};
      }}
    }} catch (_error) {{}}
    return null;
  }}

  function fillFromResult(result) {{
    const values = [
      `${{result.name}} · ${{result.type}}`,
      result.supplyDesc,
      result.supplyMission,
      `${{result.supplyTitle}} · ${{result.supplyBook}}`
    ];
    fields.forEach((field, index) => {{
      if (!field.value.trim()) field.value = values[index] || '';
    }});
    writeStorage();
    form.scrollIntoView({{ behavior: scrollBehavior, block: 'start' }});
  }}

  async function copyText(text) {{
    if (navigator.clipboard?.writeText && window.isSecureContext) {{
      await navigator.clipboard.writeText(text);
      return;
    }}
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.left = '-9999px';
    document.body.appendChild(area);
    area.select();
    document.execCommand('copy');
    area.remove();
  }}

  function buildSummary() {{
    const savedResult = readSavedResult();
    const result = savedResult ? quiz.results[savedResult.primaryKey] : null;
    const values = fields.map((field) => field.value.trim());
    if (!values.some(Boolean) && !result) return '';
    const lines = [summaryTitle];
    if (result) {{
      lines.push(`${{summaryGuardian}}: ${{result.name}} · ${{result.type}}`);
      lines.push(`${{summaryNext}}: ${{result.supplyTitle}} · ${{result.supplyMission}}`);
    }}
    values.forEach((value, index) => {{
      if (value) lines.push(`${{fieldLabels[index]}}: ${{value}}`);
    }});
    lines.push(location.href);
    return lines.join('\\n');
  }}

  async function copySummary() {{
    window.clearTimeout(timer);
    try {{
      localStorage.setItem(key, JSON.stringify(fields.map((field) => field.value)));
    }} catch (_error) {{}}
    const summary = buildSummary();
    if (!summary) {{
      setStatus(summaryEmpty);
      fields[0]?.focus();
      return;
    }}
    try {{
      await copyText(summary);
      setStatus(summaryCopied);
    }} catch (_error) {{
      setStatus(summaryEmpty);
    }}
  }}

  function renderResume() {{
    if (!resumeBox) return;
    const savedResult = readSavedResult();
    if (!savedResult) return;
    const result = quiz.results[savedResult.primaryKey];
    resumeBox.innerHTML = `
      <article class="repair-resume-card pass-resume-card" style="--result-accent:${{result.domainAccent || result.color}};--domain-glow:${{result.domainGlow || result.color}}">
        <img src="${{result.resultImage}}" alt="${{result.name}}" width="${{result.resultImageWidth}}" height="${{result.resultImageHeight}}" loading="lazy" decoding="async" fetchpriority="low">
        <div>
          <div class="resume-pass-stamp" data-resume-pass-stamp>
            <img class="resume-pass-prop" src="${{result.domainProp}}" alt="${{result.domainTitle}}" width="${{result.domainPropWidth}}" height="${{result.domainPropHeight}}" loading="lazy" decoding="async" fetchpriority="low">
            <span>${{quiz.labels.pass_title}}</span>
            <strong>${{result.domainTitle}}</strong>
          </div>
          <p class="eyebrow">${{resumeTitle}}</p>
          <h2>${{result.name}} · ${{result.type}}</h2>
          <p>${{resumeIntro}}</p>
          <p><strong>${{result.supplyTitle}}</strong> · ${{result.supplyMission}}</p>
          <div class="repair-resume-actions">
            <button class="primary-btn" type="button" data-fill-repair>${{resumeFill}}</button>
            <a class="secondary-btn" href="${{result.resourceUrl}}" data-repair-resume-route>${{quiz.labels.saved_route}}</a>
            <a class="secondary-btn" href="${{result.planUrl}}" data-repair-resume-plan>${{resumePlan}}</a>
            <a class="secondary-btn" href="${{result.lunaUrl}}" data-repair-resume-luna>${{quiz.labels.saved_luna}}</a>
            <a class="secondary-btn" href="${{result.collectorHallUrl}}" data-repair-resume-keepsake>${{result.collectorHall}}</a>
            <a class="secondary-btn" href="${{result.contactUrl}}" data-repair-resume-contact>${{quiz.labels.saved_contact}}</a>
            <a class="secondary-btn" href="${{result.supplyBookUrl}}" target="_blank" rel="noopener noreferrer sponsored">${{bookstoreLabel}}</a>
          </div>
        </div>
      </article>`;
    resumeBox.hidden = false;
    resumeBox.querySelector('[data-fill-repair]')?.addEventListener('click', () => fillFromResult(result));
    const slug = result.planUrl.split('#plan-')[1] || '';
    if (location.hash === `#plan-${{slug}}`) {{
      const focusResume = () => resumeBox.scrollIntoView({{ behavior: 'auto', block: 'start' }});
      window.requestAnimationFrame(focusResume);
      window.setTimeout(focusResume, 120);
      window.setTimeout(focusResume, 420);
    }}
  }}

  readStorage().forEach((value, index) => {{
    if (fields[index]) fields[index].value = value;
  }});

  form.addEventListener('input', () => {{
    window.clearTimeout(timer);
    timer = window.setTimeout(writeStorage, 140);
  }});

  clearButton?.addEventListener('click', () => {{
    fields.forEach((field) => field.value = '');
    try {{
      localStorage.removeItem(key);
    }} catch (_error) {{
      return;
    }}
    setStatus({cleared});
  }});
  copyButton?.addEventListener('click', copySummary);
  if (copyButton) copyButton.textContent = copySummaryLabel;
  renderResume();
}})();
</script>
"""


def repair_plan_page(lang: str) -> None:
    t = LANGS[lang]
    plan = REPAIR_PLAN[lang]
    section_labels = SECTION_LABELS[lang]
    def repair_asset_url(route: str) -> str:
        if route.startswith("#"):
            return route
        if "#" in route:
            page, anchor = route.split("#", 1)
            return f"{lang_url(lang, page).rstrip('/')}#{anchor}"
        return lang_url(lang, route)

    asset_cards = "".join(f"""
<article class="repair-asset-card">
  <span>{escape(label)}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
  <a class="secondary-btn" href="{repair_asset_url(route)}">{escape(cta)}</a>
</article>
""" for label, (title, desc, route, cta) in zip(("01", "02", "03"), plan["asset_items"]))
    days = "".join(f"""
<article>
  <span>{escape(day)}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
</article>
""" for day, title, desc in plan["days"])
    worksheet_fields = "".join(f"""
<label>
  <span>{escape(label)}</span>
  <textarea data-field="{idx}" aria-label="{escape(label)}" autocomplete="off" placeholder="{escape(placeholder)}"></textarea>
</label>
""" for idx, (label, placeholder) in enumerate(plan["fields"]))
    guardian_rows = []
    for slug in GUARDIANS:
        route = supply_route(lang, slug)
        name, typ, _guardian_desc = route["guardian"][lang]
        book = route["book"]
        guardian_rows.append(f"""
<article class="repair-guardian-card" id="plan-{slug}">
  {img_tag(route["guardian"]["prop"], route["title"])}
  <div>
    <p class="eyebrow">{escape(name)} · {escape(typ)}</p>
    <h3>{escape(route["title"])}</h3>
    <p>{escape(route["wound"])}</p>
    <p><strong>{escape(SUPPLY_LABELS[lang]["repair"])}:</strong> {escape(route["mission"])}</p>
    <div class="repair-plan-actions">
      <a class="primary-btn" href="{lang_url(lang, "resources")}#supply-{slug}">{escape(REPAIR_PLAN[lang]["resources"])}</a>
      <a class="secondary-btn" href="{lang_url(lang, "characters/" + slug)}">{escape(t["guardians"])}</a>
      <a class="secondary-btn" href="{lang_url(lang, "luna-yoga-music")}#luna-{slug}">{escape(SUPPLY_LABELS[lang]["open_luna"])}</a>
      <a class="secondary-btn" href="{book["url"]}" target="_blank" rel="noopener noreferrer sponsored">{escape(AFFILIATE_COPY[lang]["button"])}</a>
    </div>
  </div>
</article>
""")
    body = f"""
<section class="page-hero compact repair-plan-hero">
  <p class="eyebrow">{escape(plan["eyebrow"])}</p>
  <h1>{escape(plan["title"])}</h1>
  <p>{escape(plan["desc"])}</p>
  <div class="hero-actions"><a class="primary-btn" href="{lang_url(lang)}#quiz-section">{escape(plan["start"])}</a><a class="secondary-btn" href="{lang_url(lang, "resources")}">{escape(plan["resources"])}</a><a class="secondary-btn" href="#repair-card-pack">{escape(plan["download"])}</a></div>
</section>
<section class="section repair-result-resume" data-repair-saved hidden aria-live="polite"></section>
<section class="section repair-asset-section supply-panel-section" id="repair-card-pack">
  <div class="section-head"><div><p class="eyebrow">{escape(section_labels["printable_worksheet"])}</p><h2>{escape(plan["asset_title"])}</h2></div><a href="{lang_url(lang, "contact").rstrip('/')}#luna-supply-request">{escape(plan["asset_items"][2][3])}</a></div>
  <p class="section-intro">{escape(plan["asset_intro"])}</p>
  <div class="supply-panel-grid repair-asset-grid">{asset_cards}</div>
</section>
<section class="section repair-plan-section">
  <div class="section-head"><div><p class="eyebrow">{escape(section_labels["week_route"])}</p><h2>{escape(plan["days_title"])}</h2></div><a href="{lang_url(lang, "resources")}">{escape(plan["resources"])}</a></div>
  <div class="repair-day-grid">{days}</div>
</section>
<section class="section repair-worksheet-section" id="repair-worksheet">
  <div class="section-head"><div><p class="eyebrow">{escape(section_labels["printable_worksheet"])}</p><h2>{escape(plan["worksheet_title"])}</h2></div><button class="secondary-btn print-button" type="button" onclick="window.print()">{escape(plan["print"])}</button></div>
  <p class="section-intro">{escape(plan["worksheet_intro"])}</p>
  <div class="worksheet-meta"><p>{escape(plan["autosave"])}</p><div><span data-worksheet-status role="status" aria-live="polite">{escape(plan["saved"])}</span><button class="primary-btn compact-action" type="button" data-copy-worksheet-summary>{escape(plan["copy_summary"])}</button><button class="secondary-btn" type="button" data-clear-worksheet>{escape(plan["clear"])}</button></div></div>
  <form class="repair-worksheet" data-repair-worksheet>{worksheet_fields}</form>
</section>
{repair_worksheet_script(lang)}
<section class="section repair-guardian-section">
  <div class="section-head"><div><p class="eyebrow">{escape(section_labels["guardian_routes"])}</p><h2>{escape(plan["guardian_title"])}</h2></div><a href="{lang_url(lang)}#quiz-section">{escape(plan["start"])}</a></div>
  <div class="repair-guardian-grid">{"".join(guardian_rows)}</div>
  <p class="affiliate-disclosure">{escape(AFFILIATE_DISCLOSURE[lang])}</p>
</section>
<section class="section intro-grid">
  <div><h2>{escape(t["boundary"])}</h2><p>{escape(t["boundary_text"])}</p></div>
  <div class="text-stack"><h2>{escape(SUPPLY_LABELS[lang]["not_now"])}</h2><p>{escape(SUPPLY_LABELS[lang]["not_now_text"])}</p></div>
</section>
"""
    schema = json_ld({
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": plan["title"],
        "description": plan["desc"],
        "url": abs_url(lang, "repair-plan"),
        "inLanguage": t["code"],
        "dateModified": UPDATED,
        "isPartOf": {"@type": "WebSite", "name": "LoveTypes", "url": f"{DOMAIN}/"},
        "step": [
            {"@type": "HowToStep", "position": idx, "name": title, "text": desc}
            for idx, (_day, title, desc) in enumerate(plan["days"], start=1)
        ],
    })
    page_title = f"{plan['title']} | LoveTypes" if lang == "zh" else f"{plan['title']} | LoveTypes {t['name']}"
    write(page_path(lang, "repair-plan"), layout(lang, page_title, plan["desc"], "repair-plan", body, plan["title"], "article", "/assets/lovetypes/share/guide-toolkit-og.jpg", schema))


def luna_resume_script(lang: str) -> str:
    labels = LUNA_RESUME[lang]
    flow = LUNA_GUARDIAN_FLOW[lang]
    return f"""
{quiz_data_script_tag(lang)}
<script>
(() => {{
  const quiz = window.__LOVETYPES_QUIZ_DATA;
  if (!quiz) return;
  const labels = {json.dumps(labels, ensure_ascii=False)};
  const practices = {json.dumps(flow["items"], ensure_ascii=False)};
  const box = document.querySelector('[data-luna-saved]');
  if (!box) return;
  const homePath = new URL(quiz.shareUrl).pathname;
  const storageKeys = ["lovetypes:{lang}:quiz-result", `lovetypes:${{homePath}}:quiz-result`];

  function readSavedResult() {{
    try {{
      for (const key of storageKeys) {{
        const saved = JSON.parse(localStorage.getItem(key) || 'null');
        if (saved && quiz.results[saved.primaryKey]) return saved;
      }}
    }} catch (_error) {{}}
    return null;
  }}

  const saved = readSavedResult();
  if (!saved) return;
  const result = quiz.results[saved.primaryKey];
  const slug = result.resourceUrl.split('#supply-')[1] || '';
  const practice = practices[slug] || result.supplyMission;
  box.innerHTML = `
    <article class="luna-resume-card pass-resume-card" style="--result-accent:${{result.domainAccent || result.color}};--domain-glow:${{result.domainGlow || result.color}}">
      <img src="${{result.resultImage}}" alt="${{result.name}}" width="${{result.resultImageWidth}}" height="${{result.resultImageHeight}}" loading="lazy" decoding="async" fetchpriority="low">
      <div>
        <div class="resume-pass-stamp" data-resume-pass-stamp>
          <img class="resume-pass-prop" src="${{result.domainProp}}" alt="${{result.domainTitle}}" width="${{result.domainPropWidth}}" height="${{result.domainPropHeight}}" loading="lazy" decoding="async" fetchpriority="low">
          <span>${{quiz.labels.pass_title}}</span>
          <strong>${{result.domainTitle}}</strong>
        </div>
        <p class="eyebrow">${{labels.eyebrow}}</p>
        <h2>${{labels.title}}</h2>
        <p>${{labels.intro}}</p>
        <p><strong>${{result.name}} · ${{result.type}}</strong></p>
        <p><strong>${{labels.practice}}:</strong> ${{practice}}</p>
        <div class="luna-resume-actions">
          <a class="primary-btn" href="${{result.planUrl}}" data-luna-resume-plan>${{labels.repair}}</a>
          <a class="secondary-btn" href="${{result.resourceUrl}}" data-luna-resume-route>${{labels.route}}</a>
          <a class="secondary-btn" href="${{result.lunaUrl}}" data-luna-resume-luna>${{quiz.labels.saved_luna}}</a>
          <a class="secondary-btn" href="${{result.collectorHallUrl}}" data-luna-resume-keepsake>${{quiz.labels.saved_card}}</a>
          <a class="secondary-btn" href="${{result.contactUrl}}" data-luna-resume-contact>${{quiz.labels.saved_contact}}</a>
          <a class="secondary-btn" href="${{result.supplyBookUrl}}" target="_blank" rel="noopener noreferrer sponsored">${{labels.book}}</a>
        </div>
      </div>
    </article>`;
  box.hidden = false;
  if (location.hash === `#luna-${{slug}}`) {{
    const focusResume = () => box.scrollIntoView({{ behavior: 'auto', block: 'start' }});
    window.requestAnimationFrame(focusResume);
    window.setTimeout(focusResume, 120);
    window.setTimeout(focusResume, 420);
  }}
}})();
</script>
"""


def luna_night_protocol(lang: str) -> str:
    protocol = LUNA_NIGHT_PROTOCOL[lang]
    cards = []
    for number, title, desc, action, target in protocol["steps"]:
        cards.append(f"""
<article>
  <span>{escape(number)}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
  <a href="{lang_url(lang, target)}">{escape(action)}</a>
</article>
""")
    return f"""
<section class="section luna-night-protocol">
  <div class="section-head">
    <div><p class="eyebrow">{escape(protocol["eyebrow"])}</p><h2>{escape(protocol["title"])}</h2></div>
    <a href="{lang_url(lang)}#quiz-section">{escape(LANGS[lang]["start"])}</a>
  </div>
  <p class="section-intro">{escape(protocol["intro"])}</p>
  <div class="luna-protocol-grid">{"".join(cards)}</div>
</section>
"""


def luna_offer_section(lang: str) -> str:
    offer = LUNA_OFFER[lang]
    cards = "".join(f"""
<article>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
</article>
""" for title, desc in offer["items"])
    return f"""
<section class="section luna-offer-section">
  <div class="section-head"><div><p class="eyebrow">{escape(offer["eyebrow"])}</p><h2>{escape(offer["title"])}</h2></div></div>
  <p class="section-intro">{escape(offer["intro"])}</p>
  <div class="luna-offer-grid">{cards}</div>
  <div class="luna-offer-actions">
    <a class="primary-btn" href="https://www.youtube.com/channel/UCPeQjvN9q2kY2s09PuRSL6w" target="_blank" rel="noopener noreferrer" data-funnel-event="luna_offer_listen">{escape(offer["listen"])}</a>
    <a class="secondary-btn" href="{lang_url(lang, "resources")}" data-funnel-event="luna_offer_resources">{escape(offer["resources"])}</a>
    <a class="secondary-btn" href="{lang_url(lang, "contact")}#luna-supply-request" data-funnel-event="luna_offer_contact">{escape(offer["contact"])}</a>
  </div>
</section>
"""


def luna_page(lang: str) -> None:
    t = LANGS[lang]
    luna = LUNA_CONTENT[lang]
    flow = LUNA_GUARDIAN_FLOW[lang]
    offer = LUNA_OFFER[lang]
    section_labels = SECTION_LABELS[lang]
    use_case_actions = LUNA_USE_CASE_ACTIONS[lang]
    def use_case_href(target: str) -> str:
        return f"{lang_url(lang)}{target}" if target.startswith("#") else lang_url(lang, target)
    use_cases = "".join(
        f'<article><h3>{escape(title)}</h3><p>{escape(desc)}</p><a class="supply-signal-link" href="{use_case_href(target)}" data-funnel-event="luna_use_case_action">{escape(action)}</a></article>'
        for (title, desc), (action, target) in zip(LUNA_USE_CASES[lang], use_case_actions)
    )
    guardian_flow_cards = []
    for slug, data in GUARDIANS.items():
        name, typ, _desc = data[lang]
        guardian_flow_cards.append(f"""
<article class="luna-guardian-card" id="luna-{slug}">
  {img_tag(data["asset"], name)}
  <div>
    <p class="eyebrow">{escape(typ)}</p>
    <h3>{escape(name)}</h3>
    <p><strong>{escape(flow["practice"])}:</strong> {escape(flow["items"][slug])}</p>
    <div class="luna-guardian-actions">
      <a href="{lang_url(lang, "repair-plan")}#plan-{slug}">{escape(flow["repair"])}</a>
      <a href="{lang_url(lang, "resources")}#supply-{slug}">{escape(flow["route"])}</a>
    </div>
  </div>
</article>
""")
    section_cards = []
    for image_slug, title, desc in luna["sections"]:
        section_cards.append(f"""
<article class="luna-card">
  {img_tag(f"/luna-yoga-music/images/{image_slug}.webp", title)}
  <div><h3>{escape(title)}</h3><p>{escape(desc)}</p></div>
</article>
""")
    body = f"""
<section class="luna-hero">
  <div class="luna-copy">
    <p class="eyebrow">{escape(luna["badge"])}</p>
    <h1>{escape(t["luna_title"])}</h1>
    <p class="lead">{escape(luna["headline"])}</p>
    <p>{escape(luna["intro"])}</p>
    <div class="hero-actions"><a class="primary-btn" href="https://www.youtube.com/channel/UCPeQjvN9q2kY2s09PuRSL6w" target="_blank" rel="noopener noreferrer">{escape(offer["listen"])}</a><a class="secondary-btn" href="{lang_url(lang, "resources")}">{escape(luna["primary"])}</a><a class="secondary-btn" href="{lang_url(lang, "contact")}#luna-supply-request">{escape(offer["contact"])}</a></div>
  </div>
  <div class="luna-orb">{img_tag("/luna-yoga-music/images/hero.webp", "Luna Yoga Music", lazy=False, priority=True)}</div>
</section>
<section class="section luna-result-resume" data-luna-saved hidden aria-live="polite"></section>
{luna_night_protocol(lang)}
<section class="section luna-strip">
  <div><p class="eyebrow">{escape(section_labels["calm_paths"])}</p><h2>{escape(t["luna_title"])}</h2><p class="section-intro">{escape(t["luna_desc"])}</p></div>
  <div class="luna-card-grid">{"".join(section_cards)}</div>
</section>
<section class="section luna-use-cases">
  <div class="section-head"><div><p class="eyebrow">{escape(section_labels["night_heart_supply"])}</p><h2>{escape(section_labels["luna_night_supply"])}</h2><p>{escape(luna["headline"])}</p></div><a href="{lang_url(lang, "resources")}">{escape(luna["primary"])}</a></div>
  <div class="luna-use-grid">{use_cases}</div>
</section>
{luna_offer_section(lang)}
<section class="section luna-guardian-flow">
  <div class="section-head"><div><p class="eyebrow">{escape(flow["eyebrow"])}</p><h2>{escape(flow["title"])}</h2></div><a href="{lang_url(lang)}#quiz-section">{escape(t["start"])}</a></div>
  <p class="section-intro">{escape(flow["intro"])}</p>
  <div class="luna-guardian-grid">{"".join(guardian_flow_cards)}</div>
</section>
<section class="section intro-grid">
  <div><h2>{escape(t["boundary"])}</h2><p>{escape(t["boundary_text"])}</p></div>
  <div class="text-stack"><h2>{escape(PAGE_SECTIONS[lang]["use"])}</h2><p>{escape(PRACTICAL_COPY[lang]["practice"])}</p></div>
</section>
{luna_resume_script(lang)}
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"{escape(t["luna_title"])}","description":"{escape(t["luna_desc"])}","url":"{abs_url(lang, "luna-yoga-music")}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
    page_title = f"{t['luna_title']} | LoveTypes" if lang == "zh" else f"{t['luna_title']} | LoveTypes {t['name']}"
    write(page_path(lang, "luna-yoga-music"), layout(lang, page_title, t["luna_desc"], "luna-yoga-music", body, t["resources"], "website", "/og-cover.jpg", schema))


def luna_alias_page(lang: str) -> None:
    t = LANGS[lang]
    luna = LUNA_CONTENT[lang]
    section_labels = SECTION_LABELS[lang]
    target = lang_url(lang, "luna-yoga-music")
    use_cases = "".join(f"<article><h3>{escape(title)}</h3><p>{escape(desc)}</p></article>" for title, desc in LUNA_USE_CASES[lang])
    body = f"""
<section class="page-hero compact">
  <p class="eyebrow">{escape(section_labels["luna_night_supply"])}</p>
  <h1>{escape(t["luna_title"])}</h1>
  <p>{escape(luna["headline"])}</p>
  <div class="hero-actions"><a class="primary-btn" href="{target}">{escape(t["luna_title"])}</a><a class="secondary-btn" href="{lang_url(lang, "resources")}">{escape(t["resources"])}</a><a class="secondary-btn" href="{lang_url(lang, "repair-plan")}">{escape(REPAIR_PLAN[lang]["title"])}</a></div>
</section>
<section class="section note-section">
  <h2>{escape(luna["headline"])}</h2>
  <p>{escape(luna["intro"])}</p>
  <p>{escape(t["luna_desc"])}</p>
</section>
{luna_night_protocol(lang)}
<section class="section luna-use-cases">
  <div class="section-head"><div><p class="eyebrow">{escape(section_labels["night_heart_supply"])}</p><h2>{escape(section_labels["luna_night_supply"])}</h2><p>{escape(t["luna_desc"])}</p></div><a href="{target}">{escape(t["luna_title"])}</a></div>
  <div class="luna-use-grid">{use_cases}</div>
</section>
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"{escape(t["luna_title"])}","description":"{escape(t["luna_desc"])}","url":"{abs_url(lang, "luna-yoga-music")}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
    page_title = f"{t['luna_title']} | LoveTypes" if lang == "zh" else f"{t['luna_title']} | LoveTypes {t['name']}"
    write(page_path(lang, "luna"), layout(lang, page_title, t["luna_desc"], "luna", body, t["resources"], "website", "/og-cover.jpg", schema, alternate_path="luna", canonical_path="luna-yoga-music", robots="noindex, follow"))


def contact_request_section(lang: str) -> str:
    request = CONTACT_REQUESTS[lang]
    repair = CONTACT_REPAIR_REPORTS[lang]
    subject_label = CONTACT_SUBJECT_LABELS[lang]
    template_labels = CONTACT_TEMPLATE_LABELS[lang]
    request_subject = request["subject"]
    repair_subject = repair["subject"]
    request_subject_href = quote(request_subject)
    repair_subject_href = quote(repair_subject)
    request_body_href = quote(request["body"])
    repair_body_href = quote(repair["body"])
    copy_label = escape(template_labels["copy"])
    template_label = escape(template_labels["label"])

    request_cards = "".join(
        f"<article><span>{idx}</span><h3>{escape(title)}</h3><p>{escape(body)}</p></article>"
        for idx, (title, body) in enumerate(request["items"], 1)
    )
    repair_cards = "".join(
        f"<article><span>{idx}</span><h3>{escape(title)}</h3><p>{escape(body)}</p></article>"
        for idx, (title, body) in enumerate(repair["items"], 1)
    )
    return f"""
<section class="section contact-result-handoff" data-contact-saved hidden aria-live="polite"></section>
<section class="section contact-request-section" id="luna-supply-request">
  <div class="section-head"><div><p class="eyebrow">{escape(request["eyebrow"])}</p><h2>{escape(request["title"])}</h2></div></div>
  <p class="section-intro">{escape(request["intro"])}</p>
  <div class="contact-request-grid">{request_cards}</div>
  <div class="contact-request-note">
    <p>{escape(request["note"])}</p>
    <p class="contact-request-subject"><strong>{escape(subject_label)}</strong><code>{escape(request_subject)}</code></p>
    <div class="contact-request-subject contact-request-template"><strong>{template_label}</strong><code>{escape(request["body"])}</code><button class="secondary-btn" type="button" data-copy-contact-template data-funnel-event="contact_supply_template_copy" data-copy-text="{escape(request["body"])}">{copy_label}</button></div>
    <a class="primary-btn" href="mailto:contact@lovetypes.tw?subject={request_subject_href}&body={request_body_href}" data-funnel-event="contact_supply_mailto">{escape(request["cta"])}</a>
  </div>
</section>
<section class="section contact-request-section" id="site-repair-report">
  <div class="section-head"><div><p class="eyebrow">{escape(repair["eyebrow"])}</p><h2>{escape(repair["title"])}</h2></div></div>
  <p class="section-intro">{escape(repair["intro"])}</p>
  <div class="contact-request-grid">{repair_cards}</div>
  <div class="contact-request-note">
    <p>{escape(repair["note"])}</p>
    <p class="contact-request-subject"><strong>{escape(subject_label)}</strong><code>{escape(repair_subject)}</code></p>
    <div class="contact-request-subject contact-request-template"><strong>{template_label}</strong><code>{escape(repair["body"])}</code><button class="secondary-btn" type="button" data-copy-contact-template data-funnel-event="contact_repair_template_copy" data-copy-text="{escape(repair["body"])}">{copy_label}</button></div>
    <a class="primary-btn ghost" href="mailto:contact@lovetypes.tw?subject={repair_subject_href}&body={repair_body_href}" data-funnel-event="contact_repair_mailto">{escape(repair["cta"])}</a>
  </div>
</section>
{contact_template_copy_script(lang)}
{contact_result_handoff_script(lang)}
"""


def about_garden_pass(lang: str) -> str:
    copy = ABOUT_GARDEN_PASS[lang]
    cards = "".join(
        f"""
<article class="garden-pass-card">
  <span>{escape(idx)}</span>
  <h3>{escape(title)}</h3>
  <p>{escape(desc)}</p>
</article>
"""
        for idx, title, desc in copy["cards"]
    )
    return f"""
<section class="section garden-pass-section" data-about-garden-pass>
  <div class="section-head"><div><p class="eyebrow">{escape(copy["eyebrow"])}</p><h2>{escape(copy["title"])}</h2></div></div>
  <p class="section-intro">{escape(copy["intro"])}</p>
  <div class="garden-pass-grid">{cards}</div>
</section>
"""


def theory_domain_compass(lang: str) -> str:
    copy = THEORY_DOMAIN_COMPASS[lang]
    cards = []
    for slug, guardian in GUARDIANS.items():
        name, typ, _desc = guardian[lang]
        domain_title, domain_desc, _domain_cta = GUARDIAN_DOMAINS[slug][lang]
        domain = GUARDIAN_DOMAINS[slug]
        cards.append(f"""
<a class="theory-domain-card" href="{lang_url(lang, "characters/" + slug)}" data-guardian-domain="{slug}" style="--domain-accent:{domain["accent"]};--domain-glow:{domain["glow"]}">
  {img_tag(guardian["prop"], f"{name} {domain_title}", "theory-domain-prop")}
  <div>
    <span>{escape(typ)}</span>
    <h3>{escape(domain_title)}</h3>
    <p>{escape(domain_desc)}</p>
    <small>{escape(copy["cta"])} · {escape(name)}</small>
  </div>
</a>
""")
    return f"""
<section class="section theory-domain-compass" data-theory-domain-compass>
  <div class="section-head"><div><p class="eyebrow">{escape(copy["eyebrow"])}</p><h2>{escape(copy["title"])}</h2></div><a href="{lang_url(lang, "characters")}">{escape(LANGS[lang]["guardians"])}</a></div>
  <p class="section-intro">{escape(copy["intro"])}</p>
  <div class="theory-domain-grid">{"".join(cards)}</div>
</section>
"""


def simple_page(lang: str, slug: str) -> None:
    t = LANGS[lang]
    labels = PAGE_SECTIONS[lang]
    copy = PRACTICAL_COPY[lang]
    section_labels = SECTION_LABELS[lang]
    titles = {
        "theory": (SIMPLE_PAGE_DISPLAY_TITLES[lang]["theory"], t["tagline"]),
        "resources": (t["resources"], t["resources_desc"]),
        "about": (SIMPLE_PAGE_DISPLAY_TITLES[lang]["about"], t["trust_intro"]),
        "contact": (t["contact"], t["contact_desc"]),
        "privacy": (t["privacy"], t["privacy_desc"]),
        "terms": (t["terms"], t["terms_desc"]),
        "luna-yoga-music": (t["luna_title"], t["luna_desc"]),
    }
    title, desc = titles[slug]
    if slug == "about":
        about_items = "".join(f"<h2>{escape(heading)}</h2><p>{body_text}</p>" for heading, body_text in ABOUT_SECTIONS[lang])
        body = f"""
<section class="page-hero compact"><p class="eyebrow">{escape(section_labels["about_lovetypes"])}</p><h1>{escape(title)}</h1><p>{escape(desc)}</p>{trust_hero_actions(lang, slug)}</section>
{about_garden_pass(lang)}
<section class="section article-body standalone">
  {about_items}
  <h2>{escape(t["boundary"])}</h2>
  <p>{escape(t["boundary_text"])}</p>
  <div class="callout"><strong>LoveTypes</strong><p>{escape(PRACTICAL_COPY[lang]["mistakes"])}</p></div>
</section>
{about_trust_charter(lang)}
{trust_action_routes(lang, "about")}
"""
        schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"AboutPage","name":"{escape(title)}","description":"{escape(desc)}","url":"{abs_url(lang, slug)}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
        page_title = f"{title} | LoveTypes" if lang == "zh" else f"{title} | LoveTypes {t['name']}"
        write(page_path(lang, slug), layout(lang, page_title, desc, slug, body, t["about"], "website", "/og-cover.jpg", schema))
        return
    if slug == "theory":
        theory_items = "".join(f"<h2>{escape(heading)}</h2><p>{escape(body_text)}</p>" for heading, body_text in THEORY_SECTIONS[lang])
        guardian_cards = "".join(character_card(lang, guardian_slug, guardian_data) for guardian_slug, guardian_data in GUARDIANS.items())
        faq_items = "".join(f"<article><h3>{escape(q)}</h3><p>{escape(a)}</p></article>" for q, a in THEORY_FAQ[lang])
        body = f"""
<section class="page-hero compact"><p class="eyebrow">{escape(section_labels["love_language_theory"])}</p><h1>{escape(title)}</h1><p>{escape(desc)}</p><div class="hero-actions"><a class="primary-btn" href="{lang_url(lang)}#quiz-section">{escape(t["start"])}</a><a class="secondary-btn" href="{lang_url(lang, "characters")}">{escape(t["guardians"])}</a></div></section>
{theory_domain_compass(lang)}
<section class="section article-body standalone">
  {theory_items}
  <h2>{escape(t["boundary"])}</h2>
  <p>{escape(t["boundary_text"])}</p>
</section>
<section class="section guardian-nav-section"><div class="section-head"><p class="eyebrow">{escape(section_labels["five_guardians"])}</p><h2>{escape(t["guardians"])}</h2><a href="{lang_url(lang, "characters")}">{escape(t["learn_more"])}</a></div><div class="guardian-grid compact">{guardian_cards}</div></section>
<section class="section faq-section"><div class="section-head"><p class="eyebrow">{escape(section_labels["love_language_faq"])}</p><h2>{escape(t["theory"])}</h2></div><div class="faq-grid">{faq_items}</div></section>
{trust_action_routes(lang, "theory")}
"""
        schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"{escape(title)}","description":"{escape(desc)}","url":"{abs_url(lang, slug)}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","about":{{"@type":"Thing","name":"Five love languages"}},"isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
        page_title = f"{title} | LoveTypes" if lang == "zh" else f"{title} | LoveTypes {t['name']}"
        write(page_path(lang, slug), layout(lang, page_title, desc, slug, body, t["theory"], "website", "/og-cover.jpg", schema))
        return
    extra = ""
    if slug == "contact":
        extra = '<p class="contact-line"><a href="mailto:contact@lovetypes.tw">contact@lovetypes.tw</a></p>'
    if slug in {"privacy", "terms"}:
        extra = f"<p><strong>{escape(t['updated_label'])}:</strong> {UPDATED}</p>"
    if slug in {"contact", "privacy", "terms"}:
        schema_type = {"contact": "ContactPage", "privacy": "WebPage", "terms": "WebPage"}[slug]
        contact_requests = contact_request_section(lang) if slug == "contact" else ""
        policy_contact = policy_contact_route(lang, slug)
        policy_contact_markup = f"{policy_contact}\n" if policy_contact else ""
        body = f"""
<section class="page-hero compact"><p class="eyebrow">LOVETYPES</p><h1>{escape(title)}</h1><p>{escape(desc)}</p>{trust_hero_actions(lang, slug)}{extra}</section>
{contact_requests}
{policy_compass_section(lang, slug)}
{policy_detail_section(lang, slug)}
{policy_contact_markup}<section class="section article-body standalone policy-boundary-note">
  <h2>{escape(t["boundary"])}</h2>
  <p>{escape(t["boundary_text"])}</p>
</section>
"""
        schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"{schema_type}","name":"{escape(title)}","description":"{escape(desc)}","url":"{abs_url(lang, slug)}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
        page_title = f"{title} | LoveTypes" if lang == "zh" else f"{title} | LoveTypes {t['name']}"
        write(page_path(lang, slug), layout(lang, page_title, desc, slug, body, title, "website", "/og-cover.jpg", schema))
        return
    body = f"""
<section class="page-hero compact"><p class="eyebrow">LOVETYPES</p><h1>{escape(title)}</h1><p>{escape(desc)}</p>{extra}</section>
<section class="section article-body standalone">
  <h2>{escape(t["trust_intro"])}</h2>
  <p>{escape(copy["why"])}</p>
  <p>{escape(copy["notice"])}</p>
  <h2>{escape(labels["editorial"])}</h2>
  <p>{SITE_COPY[lang]["editorial"]}</p>
  <h2>{escape(labels["use"])}</h2>
  <p>{escape(copy["practice"])}</p>
  <h2>{escape(t["boundary"])}</h2>
  <p>{escape(t["boundary_text"])}</p>
  <h2>{escape(labels["disclosure"])}</h2>
  <p>{SITE_COPY[lang]["disclosure"]}</p>
  <h2>{escape(labels["contact_help"])}</h2>
  <p>{SITE_COPY[lang]["contact"]}</p>
  <div class="callout"><strong>LoveTypes</strong><p>{escape(copy["mistakes"])}</p></div>
</section>
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"{escape(title)}","description":"{escape(desc)}","url":"{abs_url(lang, slug)}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
    page_title = f"{title} | LoveTypes" if lang == "zh" else f"{title} | LoveTypes {t['name']}"
    write(page_path(lang, slug), layout(lang, page_title, desc, slug, body, title, "website", "/og-cover.jpg", schema))


def write_css() -> None:
    css_path = STATIC_SOURCE_DIR / "shared.css"
    css = css_path.read_text(encoding="utf-8")
    write(ROOT / CSS_ASSET.lstrip("/"), css.strip() + "\n")


def write_versioned_scripts() -> None:
    for source, target in (
        ("site-interactions.js", INTERACTIONS_ASSET),
        ("deferred-external.js", AFFILIATE_ASSET),
    ):
        script = (STATIC_SOURCE_DIR / source).read_text(encoding="utf-8")
        write(ROOT / target.lstrip("/"), script.strip() + "\n")


def write_quiz_data_assets() -> None:
    for lang in LANGS:
        payload = quiz_payload(lang)
        script = (
            "window.__LOVETYPES_QUIZ_DATA = "
            + payload
            + ";\n"
        )
        write(ROOT / QUIZ_DATA_ASSETS[lang].lstrip("/"), script)


def write_404_page() -> None:
    lang = "zh"
    t = LANGS[lang]
    copy = NOT_FOUND_COPY[lang]
    title = copy["title"]
    desc = copy["desc"]

    def route_set(code: str) -> list[dict]:
        labels = LANGS[code]
        not_found = NOT_FOUND_COPY[code]
        return [
            {"key": "home", "href": lang_url(code), "label": labels["start"], "text": not_found["home_text"]},
            {"key": "guardians", "href": lang_url(code, "characters"), "label": not_found["guardians"], "text": not_found["guardians_text"]},
            {"key": "resources", "href": lang_url(code, "resources"), "label": labels["resources"], "text": not_found["resources_text"]},
            {"key": "contact", "href": lang_url(code, "contact"), "label": labels["contact"], "text": not_found["contact_text"]},
        ]

    routes = route_set(lang)
    route_payload = {
        code: {
            **NOT_FOUND_COPY[code],
            "html_lang": LANGS[code]["code"],
            "start": LANGS[code]["start"],
            "guides": LANGS[code]["guides"],
            "contact": LANGS[code]["contact"],
            "boundary": LANGS[code]["boundary"],
            "boundary_text": LANGS[code]["boundary_text"],
            "safe_routes_eyebrow": SECTION_LABELS[code]["safe_routes"],
            "guides_href": lang_url(code, "guides"),
            "quiz_href": lang_url(code) + "#quiz-section",
            "contact_href": lang_url(code, "contact"),
            "routes": route_set(code),
        }
        for code in LANGS
    }
    copy_json = json.dumps(route_payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    cards = "".join(f"""
<a class="content-card" href="{route["href"]}" data-not-found-route="{route["key"]}">
  <span class="eyebrow" data-not-found-field="return_path">{escape(copy["return_path"])}</span>
  <h3 data-not-found-field="route_label">{escape(route["label"])}</h3>
  <p data-not-found-field="route_text">{escape(route["text"])}</p>
</a>
""" for route in routes)
    script = f"""
<script type="application/json" id="not-found-copy">{copy_json}</script>
<script>
(() => {{
  const el = document.getElementById('not-found-copy');
  if (!el) return;
  const copy = JSON.parse(el.textContent || '{{}}');
  const segment = window.location.pathname.split('/').filter(Boolean)[0];
  const lang = Object.prototype.hasOwnProperty.call(copy, segment) ? segment : 'zh';
  const data = copy[lang] || copy.zh;
  const setText = (selector, value) => {{
    const node = document.querySelector(selector);
    if (node && value) node.textContent = value;
  }};
  const setHref = (selector, value) => {{
    const node = document.querySelector(selector);
    if (node && value) node.setAttribute('href', value);
  }};
  document.documentElement.lang = data.html_lang || 'zh-TW';
  if (data.title) document.title = data.title;
  const description = document.querySelector('meta[name="description"]');
  if (description && data.desc) description.setAttribute('content', data.desc);
  setText('[data-not-found-field="eyebrow"]', data.eyebrow);
  setText('[data-not-found-field="heading"]', data.heading);
  setText('[data-not-found-field="intro"]', data.intro);
  setText('[data-not-found-field="start"]', data.start);
  setText('[data-not-found-field="guides"]', data.guides);
  setText('[data-not-found-field="safe_routes_eyebrow"]', data.safe_routes_eyebrow);
  setText('[data-not-found-field="safe_routes"]', data.safe_routes);
  setText('[data-not-found-field="contact_link"]', data.contact);
  setText('[data-not-found-field="boundary"]', data.boundary);
  setText('[data-not-found-field="boundary_text"]', data.boundary_text);
  setHref('[data-not-found-field="start"]', data.quiz_href);
  setHref('[data-not-found-field="guides"]', data.guides_href);
  setHref('[data-not-found-field="contact_link"]', data.contact_href);
  (data.routes || []).forEach((route) => {{
    const card = document.querySelector(`[data-not-found-route="${{route.key}}"]`);
    if (!card) return;
    card.setAttribute('href', route.href);
    const returnPath = card.querySelector('[data-not-found-field="return_path"]');
    const label = card.querySelector('[data-not-found-field="route_label"]');
    const text = card.querySelector('[data-not-found-field="route_text"]');
    if (returnPath) returnPath.textContent = data.return_path;
    if (label) label.textContent = route.label;
    if (text) text.textContent = route.text;
  }});
}})();
</script>
"""
    body = f"""
<section class="page-hero compact">
  <p class="eyebrow" data-not-found-field="eyebrow">{escape(copy["eyebrow"])}</p>
  <h1 data-not-found-field="heading">{escape(copy["heading"])}</h1>
  <p data-not-found-field="intro">{escape(copy["intro"])}</p>
  <div class="hero-actions"><a class="primary-btn" href="{lang_url(lang)}#quiz-section" data-not-found-field="start">{escape(t["start"])}</a><a class="secondary-btn" href="{lang_url(lang, "guides")}" data-not-found-field="guides">{escape(t["guides"])}</a></div>
</section>
<section class="section">
  <div class="section-head"><div><p class="eyebrow" data-not-found-field="safe_routes_eyebrow">{escape(SECTION_LABELS[lang]["safe_routes"])}</p><h2 data-not-found-field="safe_routes">{escape(copy["safe_routes"])}</h2></div><a href="{lang_url(lang, "contact")}" data-not-found-field="contact_link">{escape(t["contact"])}</a></div>
  <div class="card-grid">{cards}</div>
</section>
<section class="section note-section"><h2 data-not-found-field="boundary">{escape(t["boundary"])}</h2><p data-not-found-field="boundary_text">{escape(t["boundary_text"])}</p></section>
{script}
"""
    page = layout(lang, title, desc, "", body, "", "website", "/og-cover.jpg", "", robots="noindex, follow")
    write(ROOT / "404.html", page)


def write_llms_txt() -> None:
    guardian_lines = []
    for slug, data in GUARDIANS.items():
        zh_name, zh_language, zh_desc = data["zh"]
        en_name, en_language, _ = data["en"]
        guardian_lines.append(f"- {zh_name} / {en_name} ({zh_language} / {en_language}): {zh_desc} {DOMAIN}/characters/{slug}/")

    guide_lines = []
    for guide in GUIDES:
        title, desc = guide["zh"]
        guardian = GUARDIANS[guide["guardian"]]["zh"][0]
        guide_lines.append(f"- {title}: {desc} Guardian: {guardian}. {DOMAIN}/guides/{guide['slug']}/")

    content = f"""# LoveTypes - Heart Garden Emotion Guardians

> LoveTypes is a multilingual relationship-reflection site that translates the five love languages into the Heart Garden and five emotion guardians. The core experience is a 15-question guardian recognition ritual, followed by personalized guides, repair practices, guardian supply routes, Luna night support, and keepsake assets.

## Canonical Site

- Production: {DOMAIN}/
- Last updated: {UPDATED}
- Primary language: Traditional Chinese
- Additional entry points: {DOMAIN}/en/ , {DOMAIN}/ja/ , {DOMAIN}/ko/ , {DOMAIN}/es/

## Core Concept

LoveTypes uses the five love languages as reflective communication tools, not as medical, therapeutic, legal, or diagnostic advice. The site vocabulary includes the Heart Garden, guardian recognition ritual, misfrequency repair, traveler supplies, Luna night support, and guardian keepsakes.

## Five Guardians

{chr(10).join(guardian_lines)}

## High-Value Pages

- Quiz and home entrance: {DOMAIN}/
- Human-readable Heart Garden map: {DOMAIN}/garden-map/
- Guardian overview: {DOMAIN}/characters/
- Field guides: {DOMAIN}/guides/
- Guardian supply routes and affiliate resources: {DOMAIN}/resources/
- Misfrequency repair plan: {DOMAIN}/repair-plan/
- Guardian keepsakes: {DOMAIN}/keepsakes/
- Luna night support: {DOMAIN}/luna-yoga-music/
- About the Heart Garden: {DOMAIN}/about/
- Five love languages theory: {DOMAIN}/theory/
- Contact: {DOMAIN}/contact/
- Privacy policy: {DOMAIN}/privacy/
- Terms: {DOMAIN}/terms/

## Guide Index

{chr(10).join(guide_lines)}

## Commercial and Safety Boundaries

- Affiliate links are kept on the Resources page and are disclosed there.
- No full-site advertising script is enabled before approval boundaries are clear.
- Recommendations are framed as relationship reflection and practical repair support, not guaranteed outcomes.
- Luna content is positioned as night reflection, cooling down after conflict, journaling, and post-quiz emotional sorting.
- Contact email: contact@lovetypes.tw
"""
    write(ROOT / "llms.txt", content)


def write_site_manifest() -> None:
    manifest = {
        "name": "LoveTypes 情感守護者宇宙",
        "short_name": "LoveTypes",
        "description": "五種愛之語測驗、情感守護者、錯頻修復與旅人補給。",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#fff7fb",
        "theme_color": "#7a4d6d",
        "orientation": "portrait-primary",
        "lang": "zh-TW",
        "categories": ["lifestyle", "education"],
        "icons": [
            {"src": "/favicon.ico", "sizes": "16x16 24x24 32x32", "type": "image/x-icon"},
            {"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
        "shortcuts": [
            {"name": "開始認領儀式", "url": "/#quiz-section", "description": "完成 15 道心語題目，找到你的情感守護者。"},
            {"name": "心語庭園地圖", "url": "/garden-map/", "description": "查看測驗、守護者、指南、補給與修復計畫的完整入口。"},
            {"name": "五位守護者", "url": "/characters/", "description": "查看艾莉絲、諾雅、薇薇安、克萊兒與朵拉。"},
        ],
    }
    write(ROOT / "site.webmanifest", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def write_feed_xml() -> None:
    items = []
    for guide in GUIDES:
        title, desc = guide["zh"]
        guardian_name, guardian_language, guardian_desc = GUARDIANS[guide["guardian"]]["zh"]
        url = abs_url("zh", f"guides/{guide['slug']}")
        item_desc = f"{desc} 對應守護者：{guardian_name}（{guardian_language}）。{guardian_desc}"
        items.append(f"""    <item>
      <title>{xml_escape(title)}</title>
      <link>{xml_escape(url)}</link>
      <guid isPermaLink="true">{xml_escape(url)}</guid>
      <description>{xml_escape(item_desc)}</description>
      <category>{xml_escape(guardian_name)}</category>
      <pubDate>{date.fromisoformat(UPDATED).strftime("%a, %d %b %Y 00:00:00 +0000")}</pubDate>
    </item>""")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>LoveTypes 守護者指南</title>
    <link>{DOMAIN}/guides/</link>
    <description>LoveTypes 心語庭園的五種愛之語、情感守護者、錯頻修復與關係練習指南。</description>
    <language>zh-TW</language>
    <lastBuildDate>{date.fromisoformat(UPDATED).strftime("%a, %d %b %Y 00:00:00 +0000")}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""
    write(ROOT / "feed.xml", feed)


def write_security_txt() -> None:
    content = f"""Contact: mailto:{CONTACT_EMAIL}
Expires: 2027-05-31T00:00:00Z
Preferred-Languages: zh-TW, en
Canonical: {DOMAIN}/.well-known/security.txt
Policy: {DOMAIN}/privacy/
"""
    write(ROOT / ".well-known/security.txt", content)
    write(ROOT / "security.txt", content)


def write_ads_txt() -> None:
    write(ROOT / "ads.txt", f"google.com, {ADSENSE_ACCOUNT}, DIRECT, f08c47fec0942fa0\n")


def write_redirects() -> None:
    redirect_lines = [
        "/.well-known/security.txt /security.txt 200",
        "/luna/ /luna-yoga-music/ 301",
        "/images/characters/iris.webp /assets/lovetypes/guardians/iris.webp 301",
        "/images/characters/noah.webp /assets/lovetypes/guardians/noah.webp 301",
        "/images/characters/vivian.webp /assets/lovetypes/guardians/vivian.webp 301",
        "/images/characters/claire.webp /assets/lovetypes/guardians/claire.webp 301",
        "/images/characters/dora.webp /assets/lovetypes/guardians/dora.webp 301",
        "/assets/lovetypes/share/iris-story.webp /assets/lovetypes/share/iris-story-zh.webp 301",
        "/assets/lovetypes/share/noah-story.webp /assets/lovetypes/share/noah-story-zh.webp 301",
        "/assets/lovetypes/share/vivian-story.webp /assets/lovetypes/share/vivian-story-zh.webp 301",
        "/assets/lovetypes/share/claire-story.webp /assets/lovetypes/share/claire-story-zh.webp 301",
        "/assets/lovetypes/share/dora-story.webp /assets/lovetypes/share/dora-story-zh.webp 301",
        f"/luna-yoga-music/luna.css {CSS_ASSET} 301",
        "/assets/lovetypes/guides/lovetypes-guide-toolkit.webp /assets/lovetypes/share/guide-toolkit-og.jpg 301",
        "/assets/lovetypes/backgrounds/quiz-desk.webp /assets/lovetypes/backgrounds/guardian-garden.webp 301",
        "/assets/lovetypes/backgrounds/quiz-desk-mobile.webp /assets/lovetypes/backgrounds/guardian-garden-mobile.webp 301",
        "/og-cover.webp /og-cover.jpg 301",
    ]
    redirect_lines += [
        f"/{cfg['prefix']}/luna/ /{cfg['prefix']}/luna-yoga-music/ 301"
        for cfg in LANGS.values()
        if cfg["prefix"]
    ]
    redirects = "\n".join(redirect_lines) + "\n"
    write(ROOT / "_redirects", redirects)


def write_support_files() -> None:
    paths = ["", "garden-map", "guides", "characters", "theory", "resources", "repair-plan", "keepsakes", "luna-yoga-music", "about", "contact", "privacy", "terms"]
    paths += [f"guides/{g['slug']}" for g in GUIDES]
    paths += [f"characters/{slug}" for slug in GUARDIANS]
    sitemap = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for path in paths:
        alternates = [f'    <xhtml:link rel="alternate" hreflang="{cfg["code"]}" href="{xml_escape(abs_url(code, path))}" />' for code, cfg in LANGS.items()]
        alternates.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{xml_escape(abs_url("zh", path))}" />')
        for lang in LANGS:
            url = abs_url(lang, path)
            sitemap.append(
                "  <url>\n"
                f"    <loc>{xml_escape(url)}</loc>\n"
                f"    <lastmod>{UPDATED}</lastmod>\n"
                "    <changefreq>weekly</changefreq>\n"
                "    <priority>0.8</priority>\n"
                + "\n".join(alternates)
                + "\n  </url>"
            )
    sitemap.append("</urlset>")
    write(ROOT / "sitemap.xml", "\n".join(sitemap) + "\n")
    write(ROOT / "robots.txt", "User-agent: *\nAllow: /\n\nSitemap: https://lovetypes.tw/sitemap.xml\n")
    headers = """/*
  Cache-Control: public, max-age=600
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Strict-Transport-Security: max-age=31536000
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'self'; form-action 'self' mailto:; upgrade-insecure-requests

/assets/*
  ! Cache-Control
  Cache-Control: public, max-age=31536000, immutable

/shared-*.css
  ! Cache-Control
  Cache-Control: public, max-age=31536000, immutable

/site-interactions-*.js
  ! Cache-Control
  Cache-Control: public, max-age=31536000, immutable

/deferred-external-*.js
  ! Cache-Control
  Cache-Control: public, max-age=31536000, immutable

/quiz-data-*.js
  ! Cache-Control
  Cache-Control: public, max-age=31536000, immutable

https://lovetypes.pages.dev/*
  X-Robots-Tag: noindex

https://:version.lovetypes.pages.dev/*
  X-Robots-Tag: noindex
"""
    write(ROOT / "_headers", headers)
    write_404_page()
    write_llms_txt()
    write_site_manifest()
    write_feed_xml()
    write_security_txt()
    write_ads_txt()
    write_redirects()


def apply_section_label_localization() -> None:
    """Keep visible universe labels localized while preserving English as the canonical style."""
    eyebrow_targets = [
        (QUIZ_LABELS, "destiny_ritual"),
        (AFFILIATE_COPY, "book_relics"),
        (LUNA_NIGHT_PROTOCOL, "night_supply_protocol"),
        (LUNA_GUARDIAN_FLOW, "guardian_night_supply"),
        (LUNA_OFFER, "luna_supply_entry"),
        (LUNA_RESUME, "your_night_supply"),
        (CONTACT_REQUESTS, "request_compass"),
        (CONTACT_REPAIR_REPORTS, "garden_repair_desk"),
        (GUARDIAN_ENTRY, "guardian_compass"),
        (GUARDIAN_NEED_ROUTER, "choose_by_current_need"),
        (GUIDE_INDEX_COMPASS, "reading_compass"),
        (GUIDE_DOMAIN_ROUTES, "guardian_reading_routes"),
        (SUPPLY_DECISION, "supply_compass"),
        (STARTER_KIT, "starter_kit"),
        (SUPPLY_WISHLIST, "supply_wishlist"),
        (COLLECTOR_LABELS, "guardian_keepsakes"),
        (KEEPSAKES_PAGE, "guardian_keepsake_hall"),
        (KEEPSAKE_RITUAL, "keepsake_ritual_route"),
        (REPAIR_PLAN, "seven_day_heart_plan"),
        (ABOUT_GARDEN_PASS, "heart_garden_pass"),
        (THEORY_DOMAIN_COMPASS, "five_domain_theory_compass"),
        (ABOUT_TRUST_CHARTER, "heart_garden_trust_charter"),
        (HOME_JOURNEY, "garden_journey"),
        (GARDEN_MAP, "heart_garden_map"),
    ]
    for table, label_key in eyebrow_targets:
        for lang in LANGS:
            table[lang]["eyebrow"] = SECTION_LABELS[lang][label_key]

    for lang in LANGS:
        LUNA_CONTENT[lang]["badge"] = SECTION_LABELS[lang]["moonlight_supply"]
        NOT_FOUND_COPY[lang]["eyebrow"] = SECTION_LABELS[lang]["not_found_garden"]
        NOT_FOUND_COPY[lang]["return_path"] = SECTION_LABELS[lang]["return_path"]
        POLICY_COMPASS_COPY[lang]["eyebrow"] = SECTION_LABELS[lang]["safety_boundary_map"]
        POLICY_COMPASS_COPY[lang]["detail_eyebrow"] = SECTION_LABELS[lang]["full_policy_notes"]


def main() -> None:
    apply_section_label_localization()
    cleanup_versioned_assets()
    write_css()
    write_versioned_scripts()
    write_quiz_data_assets()
    for lang in LANGS:
        home(lang)
        garden_map_page(lang)
        guides_index(lang)
        characters_index_page(lang)
        for idx, guide in enumerate(GUIDES):
            guide_page(lang, guide, idx)
        for slug, data in GUARDIANS.items():
            character_page(lang, slug, data)
        resources_page(lang)
        repair_plan_page(lang)
        keepsakes_page(lang)
        luna_page(lang)
        luna_alias_page(lang)
        for slug in ["theory", "about", "contact", "privacy", "terms"]:
            simple_page(lang, slug)
    for slug, title, desc, target in LEGACY_ZH_GUIDES:
        legacy_zh_guide_page(slug, title, desc, target)
    write_support_files()


if __name__ == "__main__":
    main()
