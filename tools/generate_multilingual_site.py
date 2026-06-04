#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://lovetypes.tw"
ADSENSE_ACCOUNT = "ca-pub-4093856660317740"
UPDATED = "2026-06-04"
ASSET_VERSION = "20260604-itemlists"
CSS_ASSET = f"/shared-{ASSET_VERSION}.css"
INTERACTIONS_ASSET = f"/site-interactions-{ASSET_VERSION}.js"
AFFILIATE_ASSET = f"/deferred-external-{ASSET_VERSION}.js"


FONT_CSS = ""


IMAGE_DIMENSIONS = {
    "/assets/lovetypes/backgrounds/guardian-garden-mobile.webp": (900, 506),
    "/assets/lovetypes/backgrounds/guardian-garden.webp": (1920, 1080),
    "/assets/lovetypes/share/guide-toolkit-og.jpg": (1200, 630),
    "/assets/lovetypes/guardians/claire.webp": (720, 1007),
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
    "/luna-yoga-music/images/flow.webp": (1536, 1024),
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
        "boundary": "Editorial boundary",
        "boundary_text": "The LoveTypes guardians and Heart Garden are metaphor tools for self-reflection and relationship communication. They are not therapy, medical advice, legal advice, or a relationship diagnosis. If you are facing violence, coercive control, trauma, or urgent risk, seek trusted local and professional support first.",
        "home_title": "LoveTypes | Love Language Quiz and Relationship Guides",
        "home_desc": "LoveTypes turns the five love languages into five emotion guardians, helping you enter the Heart Garden, recognize your doorway to feeling loved, name misfrequency, and practice repair.",
        "guide_index_title": "LoveTypes Guardian Guides | Bring Love Languages Into Real Relationships",
        "guide_index_desc": "Explore Heart Garden guides for quiz results, conflict repair, long-distance presence, boundaries, emotional needs, and partner conversations.",
        "trust_intro": "LoveTypes is a Heart Garden mapped by the five love languages. Through five emotion guardians, scenario-based reflection, and practical guides, it helps you name your need to feel loved, your misfrequency wounds, and the next words you can actually say.",
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
        "boundary": "Límite editorial",
        "boundary_text": "Las guardianas de LoveTypes y el Jardín del Corazón son herramientas metafóricas para la autorreflexión y la comunicación relacional. No ofrecen terapia, consejo médico, consejo legal ni diagnóstico individual. Si enfrentas violencia, control, trauma o riesgo urgente, busca primero apoyo profesional y personas de confianza.",
        "home_title": "LoveTypes | Test de lenguajes del amor y guías de relación",
        "home_desc": "LoveTypes transforma los cinco lenguajes del amor en cinco guardianas emocionales para entrar al Jardín del Corazón, reconocer tu entrada al amor, nombrar desajustes y practicar reparación.",
        "guide_index_title": "Guías de Guardianas LoveTypes | Lleva los lenguajes del amor a la vida real",
        "guide_index_desc": "Explora las guías del Jardín del Corazón sobre resultados, reparación de conflictos, presencia a distancia, límites, seguridad emocional y conversaciones de pareja.",
        "trust_intro": "LoveTypes es un Jardín del Corazón trazado por los cinco lenguajes del amor. Con cinco guardianas emocionales, reflexión situacional y guías prácticas, ayuda a nombrar la necesidad de sentirse amada, las heridas de desajuste y la próxima frase que sí puede decirse.",
        "resources_desc": "Encuentra entradas del Jardín del Corazón, perfiles de guardianas, teoría de lenguajes del amor y ejercicios prácticos para hallar la siguiente luz del camino.",
        "contact_desc": "Contacta a LoveTypes para correcciones de contenido, privacidad, colaboraciones o páginas del Jardín del Corazón que necesiten reparación.",
        "privacy_desc": f"Política de privacidad de LoveTypes sobre datos, servicios de terceros y contacto. Actualizada {UPDATED}.",
        "terms_desc": f"Términos de uso de LoveTypes sobre límites de contenido, propiedad intelectual, descargos y reglas del sitio. Actualizados {UPDATED}.",
        "luna_title": "Luna Yoga Music | Audio tranquilo para reflexionar",
        "luna_desc": "Luna Yoga Music ofrece audio tranquilo para escribir, descomprimir y reflexionar sobre relaciones, como una luz baja en el Jardín del Corazón de noche.",
    },
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
    },
    "en": {
        "eyebrow": "BOOK RELICS",
        "title": "Reading for the guardian journey",
        "intro": "If a guardian page helped you feel seen, these books can help turn that insight into everyday language and repair.",
        "button": "Open bookstore",
        "fit": "Best for",
        "limit": "Use with",
        "routes": "Guardian routes",
    },
    "ja": {
        "eyebrow": "BOOK RELICS",
        "title": "守護者の旅を深める本",
        "intro": "守護者ページで理解された感覚があったなら、これらの本はその理解を日常の言葉と修復へつなげます。",
        "button": "書店を見る",
        "fit": "向いている人",
        "limit": "使い方",
        "routes": "対応する守護者ルート",
    },
    "ko": {
        "eyebrow": "BOOK RELICS",
        "title": "수호자 여정을 이어 가는 책",
        "intro": "수호자 페이지에서 이해받는 느낌이 있었다면, 이 책들은 그 이해를 일상의 말과 회복으로 옮기는 데 도움을 줍니다.",
        "button": "서점 열기",
        "fit": "추천 대상",
        "limit": "사용 팁",
        "routes": "연결 수호자 루트",
    },
    "es": {
        "eyebrow": "BOOK RELICS",
        "title": "Libros para continuar el viaje de las guardianas",
        "intro": "Si una página de guardiana te hizo sentir vista, estos libros ayudan a llevar esa comprensión a palabras y reparación cotidiana.",
        "button": "Abrir librería",
        "fit": "Ideal para",
        "limit": "Úsalo con",
        "routes": "Rutas de guardianas",
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
        "saved_plan": "回到修復計畫",
        "saved_luna": "開啟 Luna",
        "saved_route": "查看補給路線",
        "saved_card": "開啟守護者卡",
        "saved_copy": "複製分享文字",
        "saved_clear": "清除上次結果",
        "routes_title": "延伸路線",
        "guardian_link": "閱讀守護者頁",
        "guide_link": "閱讀對應指南",
        "resources_link": "開啟旅人補給",
        "supply_action": "選擇這條補給路線",
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
        "saved_plan": "Return to repair plan",
        "saved_luna": "Open Luna",
        "saved_route": "View supply route",
        "saved_card": "Open guardian card",
        "saved_copy": "Copy share text",
        "saved_clear": "Clear last result",
        "routes_title": "Continue the path",
        "guardian_link": "Read guardian page",
        "guide_link": "Read matching guide",
        "resources_link": "Open resources",
        "supply_action": "Choose this supply route",
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
        "saved_plan": "修復プランへ戻る",
        "saved_luna": "Luna を開く",
        "saved_route": "補給ルートを見る",
        "saved_card": "守護者カードを開く",
        "saved_copy": "共有文をコピー",
        "saved_clear": "前回の結果を消す",
        "routes_title": "続きを読む道筋",
        "guardian_link": "守護者ページを読む",
        "guide_link": "対応ガイドを読む",
        "resources_link": "リソースを開く",
        "supply_action": "この補給ルートを選ぶ",
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
        "saved_plan": "회복 계획으로 돌아가기",
        "saved_luna": "Luna 열기",
        "saved_route": "보급 루트 보기",
        "saved_card": "수호자 카드 열기",
        "saved_copy": "공유 문구 복사",
        "saved_clear": "지난 결과 지우기",
        "routes_title": "이어 갈 길",
        "guardian_link": "수호자 페이지 읽기",
        "guide_link": "관련 가이드 읽기",
        "resources_link": "자료 열기",
        "supply_action": "이 보급 루트 선택",
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
        "saved_plan": "Volver al plan",
        "saved_luna": "Abrir Luna",
        "saved_route": "Ver ruta",
        "saved_card": "Abrir tarjeta",
        "saved_copy": "Copiar texto",
        "saved_clear": "Borrar resultado",
        "routes_title": "Continuar el camino",
        "guardian_link": "Leer página de guardiana",
        "guide_link": "Leer guía relacionada",
        "resources_link": "Abrir recursos",
        "supply_action": "Elegir esta ruta",
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
        "title": "先免費聆聽，再決定是否需要夜間補給套裝",
        "intro": "Luna 目前先作為免費聆聽與關係整理入口。若未來推出下載包、練習卡或睡前流程，會以不承諾療效、不取代諮商的方式呈現。",
        "items": [
            ("免費聆聽", "先用公開音樂陪你睡前書寫、吵架後冷卻，確認這種節奏是否真的適合你。"),
            ("接回守護者路線", "聽完後回到你的守護者補給路線，只選一個小任務，不把所有問題一次修完。"),
            ("未來補給通知", "如果你想要下載包、PDF 練習卡或睡前流程，可以先用聯絡信箱留下需求。"),
        ],
        "listen": "免費聆聽 Luna",
        "resources": "回到補給站",
        "contact": "告訴我們你需要的補給",
    },
    "en": {
        "eyebrow": "LUNA SUPPLY ENTRY",
        "title": "Listen free first, then decide whether a night supply pack fits",
        "intro": "Luna is currently a free listening and reflection doorway. If future downloads, practice cards, or bedtime flows become available, they will support repair without promising outcomes or replacing counseling.",
        "items": [
            ("Free listening", "Use the public music for bedtime journaling or post-conflict cooling, then notice whether the rhythm truly fits you."),
            ("Return to your route", "After listening, return to your guardian supply route and choose one small task instead of repairing everything at once."),
            ("Future supply note", "If you want downloads, PDF practice cards, or bedtime flows, use the contact inbox to tell us what would help."),
        ],
        "listen": "Listen to Luna free",
        "resources": "Return to supplies",
        "contact": "Tell us what supply you need",
    },
    "ja": {
        "eyebrow": "LUNA SUPPLY ENTRY",
        "title": "まず無料で聴き、夜の補給セットが必要か決める",
        "intro": "Luna は現在、無料で聴ける内省の入口です。将来ダウンロード、練習カード、就寝前フローを出す場合も、効果を約束せず、相談支援の代わりにはしません。",
        "items": [
            ("無料で聴く", "公開音楽を就寝前の日記や衝突後の静けさに使い、このリズムが自分に合うか確かめます。"),
            ("守護者ルートへ戻る", "聴いた後は守護者の補給ルートへ戻り、一つの小さな課題だけを選びます。"),
            ("今後の補給希望", "ダウンロード、PDF 練習カード、就寝前フローが必要なら、連絡先へ希望を送れます。"),
        ],
        "listen": "Luna を無料で聴く",
        "resources": "補給へ戻る",
        "contact": "必要な補給を伝える",
    },
    "ko": {
        "eyebrow": "LUNA SUPPLY ENTRY",
        "title": "먼저 무료로 듣고 밤 보급 세트가 맞는지 결정하기",
        "intro": "Luna는 현재 무료 청취와 관계 성찰의 입구입니다. 향후 다운로드, 연습 카드, 잠들기 전 흐름이 나오더라도 결과를 약속하거나 상담을 대신하지 않습니다.",
        "items": [
            ("무료 청취", "공개 음악을 잠들기 전 기록이나 다툼 뒤 진정에 사용하고, 이 리듬이 정말 맞는지 확인합니다."),
            ("수호자 루트로 돌아가기", "들은 뒤에는 수호자 보급 루트로 돌아가 작은 과제 하나만 고릅니다."),
            ("미래 보급 알림", "다운로드, PDF 연습 카드, 잠들기 전 흐름이 필요하다면 연락 메일로 알려 주세요."),
        ],
        "listen": "Luna 무료 듣기",
        "resources": "보급소로 돌아가기",
        "contact": "필요한 보급 알려주기",
    },
    "es": {
        "eyebrow": "LUNA SUPPLY ENTRY",
        "title": "Escucha gratis primero y decide si un pack nocturno encaja",
        "intro": "Luna funciona ahora como entrada gratuita de escucha y reflexión. Si más adelante hay descargas, tarjetas o rutinas nocturnas, serán apoyo para practicar, no promesa de resultado ni reemplazo de terapia.",
        "items": [
            ("Escucha gratis", "Usa la música pública para escribir antes de dormir o enfriar después de un conflicto y nota si el ritmo te sirve."),
            ("Vuelve a tu ruta", "Después de escuchar, vuelve a la ruta de tu guardiana y elige una tarea pequeña, no todo a la vez."),
            ("Aviso de recursos futuros", "Si quieres descargas, tarjetas PDF o rutinas nocturnas, usa el correo de contacto para decirnos qué ayudaría."),
        ],
        "listen": "Escuchar Luna gratis",
        "resources": "Volver a recursos",
        "contact": "Decir qué recurso necesitas",
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
        "title": "告訴我們你需要哪一種 Luna 補給",
        "intro": "如果你是從 Luna 或守護者補給路線來到這裡，請先選一種需求寄信。這能幫我們判斷下一批應優先整理下載包、PDF 練習卡，還是睡前流程。",
        "items": [
            ("下載包", "希望能離線聆聽、收藏音檔，或把 Luna 放進固定睡前儀式。"),
            ("PDF 練習卡", "希望把測驗結果、守護者任務與錯頻修復寫成可列印的短卡。"),
            ("睡前流程", "希望有 5 到 10 分鐘的步驟，陪你在吵架後冷卻、睡前整理或寫關係日記。"),
        ],
        "note": "來信時可附上你的守護者、想使用的情境與裝置。LoveTypes 不提供緊急支援、醫療建議或諮商替代。",
        "cta": "寄出 Luna 補給需求",
        "subject": "Luna%20night%20supply%20request",
    },
    "en": {
        "eyebrow": "REQUEST COMPASS",
        "title": "Tell us which Luna supply would help",
        "intro": "If you arrived from Luna or a guardian supply route, choose one request before writing. It helps us decide whether downloads, PDF practice cards, or bedtime flows should be prepared first.",
        "items": [
            ("Download pack", "You want offline listening, a saved audio set, or a stable bedtime ritual with Luna."),
            ("PDF practice cards", "You want printable cards that connect your quiz result, guardian task, and repair prompt."),
            ("Bedtime flow", "You want a 5 to 10 minute sequence for cooling down after conflict, bedtime reflection, or relationship journaling."),
        ],
        "note": "Include your guardian, use case, and device if relevant. LoveTypes does not provide emergency support, medical advice, or a replacement for counseling.",
        "cta": "Send Luna supply request",
        "subject": "Luna%20night%20supply%20request",
    },
    "ja": {
        "eyebrow": "REQUEST COMPASS",
        "title": "必要な Luna 補給を教えてください",
        "intro": "Luna や守護者の補給ルートから来た場合は、まず一つの希望を選んで送ってください。ダウンロード、PDF 練習カード、就寝前フローのどれを先に整えるべきか判断しやすくなります。",
        "items": [
            ("ダウンロードパック", "オフラインで聴きたい、音源を保存したい、Luna を就寝前の儀式に入れたい。"),
            ("PDF 練習カード", "診断結果、守護者の課題、修復プロンプトを印刷できる短いカードにしたい。"),
            ("就寝前フロー", "衝突後のクールダウン、寝る前の内省、関係日記に使える 5 から 10 分の手順がほしい。"),
        ],
        "note": "守護者、使いたい場面、端末を書ける範囲で添えてください。LoveTypes は緊急支援、医療助言、相談支援の代替を提供しません。",
        "cta": "Luna 補給希望を送る",
        "subject": "Luna%20night%20supply%20request",
    },
    "ko": {
        "eyebrow": "REQUEST COMPASS",
        "title": "필요한 Luna 보급을 알려 주세요",
        "intro": "Luna나 수호자 보급 루트에서 왔다면 먼저 한 가지 요청을 골라 보내 주세요. 다운로드, PDF 연습 카드, 잠들기 전 흐름 중 무엇을 먼저 준비할지 판단하는 데 도움이 됩니다.",
        "items": [
            ("다운로드 팩", "오프라인으로 듣거나 음원을 보관하고, Luna를 고정된 잠들기 전 의식에 넣고 싶을 때."),
            ("PDF 연습 카드", "테스트 결과, 수호자 과제, 회복 질문을 인쇄 가능한 짧은 카드로 정리하고 싶을 때."),
            ("잠들기 전 흐름", "다툼 뒤 진정, 잠들기 전 정리, 관계 일기에 쓸 5-10분 순서가 필요할 때."),
        ],
        "note": "가능하다면 수호자, 사용 장면, 기기를 함께 적어 주세요. LoveTypes는 긴급 지원, 의료 조언, 상담 대체를 제공하지 않습니다.",
        "cta": "Luna 보급 요청 보내기",
        "subject": "Luna%20night%20supply%20request",
    },
    "es": {
        "eyebrow": "REQUEST COMPASS",
        "title": "Cuéntanos qué recurso Luna necesitas",
        "intro": "Si llegaste desde Luna o desde una ruta de guardiana, elige una petición antes de escribir. Así sabremos si conviene preparar primero descargas, tarjetas PDF o rutinas nocturnas.",
        "items": [
            ("Pack de descarga", "Quieres escuchar sin conexión, guardar los audios o usar Luna como ritual estable antes de dormir."),
            ("Tarjetas PDF", "Quieres tarjetas imprimibles que unan tu resultado, tarea de guardiana y pregunta de reparación."),
            ("Rutina nocturna", "Quieres una secuencia de 5 a 10 minutos para calmarte tras un conflicto, reflexionar o escribir un diario de relación."),
        ],
        "note": "Incluye tu guardiana, situación de uso y dispositivo si ayuda. LoveTypes no ofrece apoyo de emergencia, consejo médico ni sustituto de terapia.",
        "cta": "Enviar petición Luna",
        "subject": "Luna%20night%20supply%20request",
    },
}


RESOURCE_PATHS = {
    "zh": [("先測驗", "完成 15 道心語，確認目前最需要被接收的愛之語。"), ("再讀守護者", "從結果頁進入對應角色，理解自己為什麼容易在這裡受傷。"), ("最後選補給", "依照當下狀態選擇指南、書卷或 Luna 音樂，不一次修完整座庭園。")],
    "en": [("Take the ritual", "Answer 15 prompts to see the love language you most need received now."), ("Read the guardian", "Use the result page to understand why this area can feel tender."), ("Choose supplies", "Pick a guide, book, or Luna audio for the current moment, not the whole relationship at once.")],
    "ja": [("まず診断", "15問で今いちばん受け取りたい愛の言語を見ます。"), ("守護者を読む", "結果ページから、その領域がなぜ傷つきやすいかを理解します。"), ("補給を選ぶ", "今の状態に合うガイド、本、Luna 音楽を一つ選びます。")],
    "ko": [("먼저 의식", "15문항으로 지금 가장 받고 싶은 사랑의 언어를 봅니다."), ("수호자 읽기", "결과 페이지에서 왜 이 영역이 예민한지 이해합니다."), ("자료 선택", "지금 상태에 맞는 가이드, 책, Luna 음악 중 하나를 고릅니다.")],
    "es": [("Primero ritual", "Responde 15 señales para ver qué lenguaje necesitas recibir ahora."), ("Lee la guardiana", "Desde el resultado entiende por qué esa zona puede doler."), ("Elige recursos", "Toma una guía, libro o audio Luna para el momento actual, no toda la relación de una vez.")],
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
        "title": "想要哪一種守護者補給？",
        "intro": "如果書卷還不是你現在需要的補給，可以先告訴我們你想要哪位守護者的可下載素材、PDF 練習卡、桌布或短流程。這會幫助我們決定下一批自有補給優先做什麼。",
        "request": "提出補給願望",
        "note": "來信不需要提供測驗分數；寫下守護者、使用情境與你希望帶走的素材即可。LoveTypes 不承諾療效，也不取代諮商。",
        "subject": "LoveTypes%20guardian%20supply%20wishlist",
        "body": "我想要的守護者補給：",
    },
    "en": {
        "eyebrow": "SUPPLY WISHLIST",
        "title": "Which guardian supply should exist next?",
        "intro": "If a book is not the supply you need right now, tell us which guardian should receive a download, PDF practice card, wallpaper, or short ritual first. This helps us prioritize future LoveTypes-owned supplies.",
        "request": "Send supply wish",
        "note": "You do not need to send quiz scores. Include the guardian, use case, and the material you would actually keep. LoveTypes does not promise outcomes or replace counseling.",
        "subject": "LoveTypes%20guardian%20supply%20wishlist",
        "body": "The guardian supply I want:",
    },
    "ja": {
        "eyebrow": "SUPPLY WISHLIST",
        "title": "次にほしい守護者補給は？",
        "intro": "本が今の補給ではない場合、どの守護者のダウンロード、PDF 練習カード、壁紙、短い儀式がほしいか教えてください。今後の LoveTypes 自有補給の優先順位を決める助けになります。",
        "request": "補給の希望を送る",
        "note": "診断スコアは不要です。守護者、使いたい場面、実際に保存したい素材を書いてください。LoveTypes は効果を約束せず、相談支援の代わりにもなりません。",
        "subject": "LoveTypes%20guardian%20supply%20wishlist",
        "body": "ほしい守護者補給：",
    },
    "ko": {
        "eyebrow": "SUPPLY WISHLIST",
        "title": "다음에 어떤 수호자 보급이 필요할까요?",
        "intro": "지금 책이 필요한 보급이 아니라면, 어떤 수호자의 다운로드, PDF 연습 카드, 배경화면, 짧은 의식이 먼저 필요할지 알려 주세요. 향후 LoveTypes 자체 보급 우선순위를 정하는 데 도움이 됩니다.",
        "request": "보급 희망 보내기",
        "note": "테스트 점수는 보내지 않아도 됩니다. 수호자, 사용 장면, 실제로 보관하고 싶은 자료를 적어 주세요. LoveTypes는 결과를 약속하거나 상담을 대신하지 않습니다.",
        "subject": "LoveTypes%20guardian%20supply%20wishlist",
        "body": "내가 원하는 수호자 보급:",
    },
    "es": {
        "eyebrow": "SUPPLY WISHLIST",
        "title": "Qué recurso de guardiana debería existir después?",
        "intro": "Si un libro no es el recurso que necesitas ahora, cuéntanos qué guardiana debería tener primero una descarga, tarjeta PDF, fondo de pantalla o ritual corto. Esto ayuda a priorizar futuros recursos propios de LoveTypes.",
        "request": "Enviar deseo",
        "note": "No necesitas enviar puntajes. Incluye la guardiana, el uso y el material que realmente guardarías. LoveTypes no promete resultados ni reemplaza terapia.",
        "subject": "LoveTypes%20guardian%20supply%20wishlist",
        "body": "El recurso de guardiana que quiero:",
    },
}


SUPPLY_LABELS = {
    "zh": {
        "eyebrow": "GUARDIAN SUPPLY ROUTES",
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
        "eyebrow": "GUARDIAN SUPPLY ROUTES",
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
        "eyebrow": "GUARDIAN SUPPLY ROUTES",
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
        "eyebrow": "GUARDIAN SUPPLY ROUTES",
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
        "share_hint": "Úsala en historias, envíala a una pareja o ponla en tu diario relacional como puerta de lenguaje del corazón.",
    },
}


KEEPSAKES_PAGE = {
    "zh": {
        "title": "守護者收藏室",
        "desc": "集中保存 LoveTypes 五位守護者故事卡，讓測驗結果成為可以分享、回看與延伸補給的收藏入口。",
        "eyebrow": "GUARDIAN KEEPSAKE HALL",
        "intro": "每張卡都是一個心語入口：適合發限動、傳給伴侶、放進關係日記，或作為未來守護者補給與低價收藏商品的基礎。",
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
        "desc": "After the quiz, you do not need to repair the whole relationship at once. Use seven days to turn your guardian result into a route you can revisit: notice the wound, ask for one small action, then choose one supply to support practice.",
        "days_title": "One-week practice route",
        "guardian_title": "Adjust by guardian",
        "start": "Start quiz",
        "resources": "Open supply station",
        "download": "Save this route",
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
        "desc": "Después del test, no hace falta reparar toda la relación de una vez. Usa siete días para convertir tu resultado en una ruta revisitable: mira la herida, pide una acción pequeña y elige un recurso para practicar.",
        "days_title": "Ruta de práctica semanal",
        "guardian_title": "Ajusta por guardiana",
        "start": "Iniciar test",
        "resources": "Abrir recursos",
        "download": "Guardar esta ruta",
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
        "prop": "/assets/lovetypes/props/affirmation-feather-pen.webp",
        "zh": ("艾莉絲", "肯定的言詞", "她在晨曦玻璃花園守護被準確看見的心，替那些等很久的話點亮名字。"),
        "en": ("Iris", "Words of affirmation", "In the dawn-glass garden, she guards the heart that longs to be seen clearly and gives names to words that waited too long."),
        "ja": ("アイリス", "肯定の言葉", "夜明けのガラス庭園で、正確に見てもらいたい心を守り、長く待っていた言葉に名前を与えます。"),
        "ko": ("아이리스", "인정의 말", "새벽 유리 정원에서 정확히 보이고 싶은 마음을 지키며, 오래 기다린 말들에 이름을 붙여 줍니다."),
        "es": ("Iris", "Palabras de afirmación", "En el jardín de cristal del amanecer, protege el corazón que quiere ser visto con precisión y da nombre a palabras que esperaron demasiado."),
    },
    "noah": {
        "asset": "/assets/lovetypes/guardians/noah.webp",
        "prop": "/assets/lovetypes/props/quality-time-lantern.webp",
        "zh": ("諾雅", "優質的時光", "她航行在星海書庫與安靜海面之間，守護真正留在彼此身邊的時間。"),
        "en": ("Noah", "Quality time", "Between the star-sea library and a quiet shore, she guards the kind of time where two people truly stay."),
        "ja": ("ノア", "上質な時間", "星海の書庫と静かな海辺のあいだを進み、二人が本当にそこに留まる時間を守ります。"),
        "ko": ("노아", "함께하는 시간", "별바다 서고와 고요한 해변 사이를 항해하며, 두 사람이 진짜로 머무는 시간을 지킵니다."),
        "es": ("Noah", "Tiempo de calidad", "Entre la biblioteca del mar estelar y una orilla tranquila, protege el tiempo en que dos personas realmente se quedan."),
    },
    "vivian": {
        "asset": "/assets/lovetypes/guardians/vivian.webp",
        "prop": "/assets/lovetypes/props/gifts-ribboned-gift-box.webp",
        "zh": ("薇薇安", "接受禮物", "她在月光記憶工坊收藏被想起的證據，讓心意停在細節，而不是價格。"),
        "en": ("Vivian", "Receiving gifts", "In the moonlit memory workshop, she collects proof of being remembered and keeps meaning in details, not price."),
        "ja": ("ヴィヴィアン", "贈り物", "月光の記憶工房で、思い出してもらえた証を集め、心意を値段ではなく細部に残します。"),
        "ko": ("비비안", "선물 받기", "달빛 기억 공방에서 떠올려졌다는 증거를 모으고, 마음을 가격이 아니라 세부에 머물게 합니다."),
        "es": ("Vivian", "Recibir regalos", "En el taller de memoria bajo la luna, guarda pruebas de haber sido recordada y deja el significado en los detalles, no en el precio."),
    },
    "claire": {
        "asset": "/assets/lovetypes/guardians/claire.webp",
        "prop": "/assets/lovetypes/props/service-tool-pouch.webp",
        "zh": ("克萊兒", "服務的行動", "她守著不停修復的溫室，把承諾放回日常，讓疲憊不再只由一個人撐住。"),
        "en": ("Claire", "Acts of service", "In a greenhouse of ongoing repair, she returns promises to daily life so one tired person does not hold everything alone."),
        "ja": ("クレア", "奉仕の行動", "修復の続く温室を守り、約束を日常へ戻して、疲れを一人だけで抱えないようにします。"),
        "ko": ("클레어", "봉사의 행동", "계속 수리되는 온실을 지키며 약속을 일상으로 돌려놓고, 피로를 한 사람만 버티지 않게 합니다."),
        "es": ("Claire", "Actos de servicio", "En un invernadero siempre en reparación, devuelve las promesas a la vida diaria para que una sola persona cansada no sostenga todo."),
    },
    "dora": {
        "asset": "/assets/lovetypes/guardians/dora.webp",
        "prop": "/assets/lovetypes/props/touch-golden-hug-glow.webp",
        "zh": ("朵拉", "身體的接觸", "她在柔暖聖域守護經過同意的靠近，讓身體重新記得安全的溫度。"),
        "en": ("Dora", "Physical touch", "In a warm sanctuary, she guards closeness after consent and helps the body remember the temperature of safety."),
        "ja": ("ドーラ", "身体的なふれあい", "やわらかな聖域で、同意の後にある近さを守り、身体が安全の温度を思い出すよう助けます。"),
        "ko": ("도라", "스킨십", "따뜻한 성역에서 동의 이후의 가까움을 지키며 몸이 안전의 온도를 다시 기억하게 합니다."),
        "es": ("Dora", "Contacto físico", "En un santuario cálido, protege la cercanía después del consentimiento y ayuda al cuerpo a recordar la temperatura de la seguridad."),
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


SITE_COPY = {
    "zh": {
        "guardian_use": "{name}是心語庭園裡的一扇門，不是固定身份。你可以用這位守護者說明什麼讓你感到安全、哪一種錯頻最容易刺痛你，以及哪一個小行動能讓關心更容易被你收到。",
        "editorial": "每一個 LoveTypes 頁面都先從一個真實關係問題出發，再把問題帶回五種愛之語、心語庭園的守護者隱喻，以及讀者不需要註冊帳號也能嘗試的小練習。我們維持反思式語氣，而不是診斷式語氣；當頁面太薄、太重複，或太偏向導流而不是讀者價值時，就會重新整理，讓每盞燈都能指向實際修復。",
        "disclosure": "LoveTypes 會在相關頁面揭露流量分析、聯盟連結或廣告資訊。旅人補給頁可能包含聯盟連結；若你透過這些連結購買，本站可能獲得少量佣金，但不影響你的購買價格。網站仍保留清楚的所有權、聯絡、sitemap 與政策資訊，方便讀者與搜尋/廣告審核系統確認這座心語庭園的來源與邊界。",
        "contact": "若要回報內容修正、隱私問題、合作疑慮或壞頁面，請寄到 <a href=\"mailto:contact@lovetypes.tw\">contact@lovetypes.tw</a> 或使用聯絡頁。有效回報最好附上頁面網址、裝置、瀏覽器，以及你認為需要重新點亮或修復的句子或段落。",
    },
    "en": {
        "guardian_use": "{name} is a doorway in the Heart Garden, not a fixed identity. Use this guardian to describe what helps you feel safe, which misfrequency hurts most, and what small action would make care easier to receive.",
        "editorial": "Every LoveTypes page begins with a real relationship question, then brings it back to the five love languages, the Heart Garden guardian metaphor, and a small exercise a reader can try without an account. We keep the tone reflective rather than diagnostic; when a page is thin, repetitive, or too promotional, we revise it so every lamp points toward practical repair.",
        "disclosure": "LoveTypes discloses measurement, affiliate links, or advertising information where those services are used. The Resources page may contain affiliate links; if you purchase through them, this site may earn a small commission at no extra cost to you. Clear ownership, contact, sitemap, and policy information remain available so readers and crawlers can understand the source and boundary of this Heart Garden.",
        "contact": "For content corrections, privacy questions, partnership concerns, or broken-page reports, contact <a href=\"mailto:contact@lovetypes.tw\">contact@lovetypes.tw</a> or use the contact page. Helpful reports include the page URL, device, browser, and the sentence or section you believe should be relit or repaired.",
    },
    "ja": {
        "guardian_use": "{name} は心語の庭にある一つの扉であり、固定された身分ではありません。この守護者を使って、何が安心につながるのか、どのすれ違いがいちばん痛むのか、どんな小さな行動なら思いやりを受け取りやすいのかを説明できます。",
        "editorial": "LoveTypes の各ページは、実際の関係で起こる問いから始まり、五つの愛の言語、心語の庭の守護者の比喩、そして登録なしで試せる小さな練習へつなげます。診断ではなく内省の語り口を保ち、内容が薄い、重複している、読者価値より誘導が強いと判断したページは、実際の修復に向かう灯りになるよう更新します。",
        "disclosure": "LoveTypes では、利用しているページでアクセス解析、アフィリエイトリンク、広告に関する情報を開示します。リソースページにはアフィリエイトリンクが含まれる場合があり、購入時に価格は変わりませんが、当サイトに少額の報酬が入ることがあります。所有者情報、連絡先、サイトマップ、ポリシー情報も確認できるようにしています。",
        "contact": "内容修正、プライバシー、提携、ページ不具合に関する連絡は <a href=\"mailto:contact@lovetypes.tw\">contact@lovetypes.tw</a> または連絡ページからお願いします。ページ URL、端末、ブラウザ、もう一度灯すべき、または修復すべき文や段落があると確認しやすくなります。",
    },
    "ko": {
        "guardian_use": "{name}는 마음의 정원에 있는 하나의 문이지 고정된 정체성이 아닙니다. 이 수호자를 통해 무엇이 나를 안전하게 하는지, 어떤 어긋남이 가장 아픈지, 어떤 작은 행동이 배려를 더 쉽게 받게 하는지 말할 수 있습니다.",
        "editorial": "LoveTypes의 각 페이지는 실제 관계 질문에서 시작해 다섯 가지 사랑의 언어, 마음의 정원 수호자 은유, 계정 없이도 시도할 수 있는 작은 연습으로 이어집니다. 진단이 아니라 성찰의 어조를 유지하며, 내용이 얇거나 반복적이거나 독자 가치보다 홍보가 강한 페이지는 실제 회복을 향한 등불이 되도록 다시 정리합니다.",
        "disclosure": "LoveTypes는 해당 서비스가 사용되는 페이지에서 분석, 제휴 링크, 광고 관련 정보를 고지합니다. 자료 페이지에는 제휴 링크가 포함될 수 있으며, 이를 통해 구매하면 구매 가격은 변하지 않지만 사이트가 소정의 수수료를 받을 수 있습니다. 소유권, 연락처, 사이트맵, 정책 정보도 계속 확인할 수 있습니다.",
        "contact": "콘텐츠 수정, 개인정보, 협업 문의, 깨진 페이지 신고는 <a href=\"mailto:contact@lovetypes.tw\">contact@lovetypes.tw</a> 또는 연락 페이지로 보내 주세요. 페이지 URL, 기기, 브라우저, 다시 켜거나 수리해야 할 문장이나 단락을 함께 보내면 확인이 빠릅니다.",
    },
    "es": {
        "guardian_use": "{name} es una puerta del Jardín del Corazón, no una identidad fija. Puedes usar esta guardiana para explicar qué te ayuda a sentir seguridad, qué desajuste te duele más y qué pequeña acción vuelve el cuidado más fácil de recibir.",
        "editorial": "Cada página de LoveTypes empieza con una pregunta real de relación y la lleva de vuelta a los cinco lenguajes del amor, la metáfora de las guardianas del Jardín del Corazón y un ejercicio pequeño que la persona puede probar sin crear una cuenta. Mantenemos un tono reflexivo, no diagnóstico, y revisamos las páginas demasiado delgadas, repetitivas o promocionales para que cada luz apunte a una reparación práctica.",
        "disclosure": "LoveTypes divulga información sobre medición, enlaces afiliados o publicidad en las páginas donde se usan esos servicios. La página de Recursos puede contener enlaces afiliados; si compras a través de ellos, el sitio puede recibir una pequeña comisión sin cambiar tu precio. La propiedad, contacto, sitemap y políticas siguen disponibles para explicar el origen y los límites de este Jardín del Corazón.",
        "contact": "Para correcciones de contenido, privacidad, colaboraciones o páginas rotas, escribe a <a href=\"mailto:contact@lovetypes.tw\">contact@lovetypes.tw</a> o usa la página de contacto. Un reporte útil incluye URL, dispositivo, navegador y la frase o sección que debería volver a encenderse o repararse.",
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
        attrs.append('fetchpriority="high"')
        attrs.append('decoding="async"')
    elif lazy:
        attrs.append('loading="lazy"')
        attrs.append('decoding="async"')
    else:
        attrs.append('loading="eager"')
        attrs.append('decoding="async"')
    if class_name:
        attrs.append(f'class="{class_name}"')
    return "<img " + " ".join(attrs) + " />"


def json_text(value: str) -> str:
    return escape(value).replace('"', '\\"')


def nav(lang: str, active: str = "", path: str = "") -> str:
    t = LANGS[lang]
    items = [
        (lang_url(lang, "guides"), t["guides"]),
        (lang_url(lang, "characters"), t["guardians"]),
        (lang_url(lang, "theory"), t["theory"]),
        (lang_url(lang, "resources"), t["resources"]),
        (lang_url(lang, "about"), t["about"]),
    ]
    links = "".join(f'<a class="{"active" if active == label else ""}" href="{href}">{escape(label)}</a>' for href, label in items)
    lang_links = "".join(f'<a href="{lang_url(code, path)}" lang="{cfg["code"]}">{cfg["name"]}</a>' for code, cfg in LANGS.items())
    return f"""
<header class="site-nav">
  <a class="brand" href="{lang_url(lang)}" aria-label="{escape(t["brand"])}"><span>LoveTypes</span></a>
  <nav class="nav-links" aria-label="Primary navigation">{links}</nav>
  <details class="language-menu">
    <summary aria-label="Language menu"><span></span></summary>
    <div class="language-switcher">{lang_links}</div>
  </details>
</header>
"""


def footer(lang: str) -> str:
    t = LANGS[lang]
    cards = [
        (lang_url(lang, "guides"), t["guides"], t["guide_index_desc"]),
        (lang_url(lang, "theory"), t["theory"], t["tagline"]),
        (lang_url(lang, "about"), t["about"], t["trust_intro"]),
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
    return f'<nav class="breadcrumb" aria-label="Breadcrumb">{"<span>/</span>".join(links)}</nav>'


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


def head(lang: str, title: str, desc: str, path: str = "", page_type: str = "website", image: str = "/og-cover.jpg") -> str:
    canonical = abs_url(lang, path)
    alternates = "\n".join(f'  <link rel="alternate" hreflang="{cfg["code"]}" href="{abs_url(code, path)}" />' for code, cfg in LANGS.items())
    alternates += f'\n  <link rel="alternate" hreflang="x-default" href="{abs_url("zh", path)}" />'
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
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <link rel="canonical" href="{canonical}" />
{alternates}
  <link rel="icon" href="/favicon.ico" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <meta property="og:type" content="{page_type}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:title" content="{escape(title)}" />
  <meta property="og:description" content="{escape(desc)}" />
  <meta property="og:image" content="{DOMAIN}{image}" />
  <meta name="twitter:card" content="summary_large_image" />
{hero_preload}  <link rel="stylesheet" href="{CSS_ASSET}" />
</head>
"""


def layout(lang: str, title: str, desc: str, path: str, body: str, active: str = "", page_type: str = "website", image: str = "/og-cover.jpg", schema: str = "", affiliate: bool = False) -> str:
    external_script = ""
    if affiliate:
        external_script = f'\n<script src="{AFFILIATE_ASSET}" data-affiliate defer></script>'
    return head(lang, title, desc, path, page_type, image) + f"""<body>
<a class="skip-link" href="#main">Skip to content</a>
{nav(lang, active, path)}
{schema}
{breadcrumb_schema(lang, path, title)}
{breadcrumb_nav(lang, path, title)}
<main id="main">
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
    keep = {
        CSS_ASSET.lstrip("/"),
        INTERACTIONS_ASSET.lstrip("/"),
        AFFILIATE_ASSET.lstrip("/"),
    }
    for pattern in ("shared-*.css", "site-interactions-*.js", "deferred-external-*.js"):
        for path in ROOT.glob(pattern):
            if path.name not in keep:
                path.unlink()


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
    current = slug == current_slug
    attrs = 'class="guardian-card is-current" aria-current="page"' if current else 'class="guardian-card"'
    return f"""
<a {attrs} href="{lang_url(lang, "characters/" + slug)}">
  {img_tag(data["asset"], name)}
  <div><span>{escape(typ)}</span><h3>{escape(name)}</h3><p>{escape(desc)}</p></div>
</a>
"""


def character_link_card(lang: str, slug: str, data: dict, current_slug: str = "") -> str:
    name, typ, _desc = data[lang]
    current = slug == current_slug
    attrs = 'class="guardian-card is-current" aria-current="page"' if current else 'class="guardian-card"'
    return f"""
<a {attrs} href="{lang_url(lang, "characters/" + slug)}">
  {img_tag(data["asset"], name)}
  <div><span>{escape(typ)}</span><h3>{escape(name)}</h3></div>
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


def supply_route_card(lang: str, slug: str) -> str:
    labels = SUPPLY_LABELS[lang]
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
  </div>
  <div class="supply-route-actions">
    <a class="primary-btn" href="{lang_url(lang, "guides/" + guide["slug"])}">{escape(labels["read_guide"])}</a>
    <a class="secondary-btn" href="{lang_url(lang, "luna-yoga-music")}">{escape(labels["open_luna"])}</a>
    <button class="secondary-btn" type="button" data-copy-supply-route data-route-summary="{summary_json}">{escape(labels["copy_route"])}</button>
    <a class="secondary-btn" href="{book["url"]}" target="_blank" rel="noopener sponsored">{escape(AFFILIATE_COPY[lang]["button"])}</a>
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
        cards.append(f"""
<a class="supply-quick-card" href="#supply-{slug}">
  {img_tag(data["asset"], name)}
  <span class="eyebrow">{escape(typ)}</span>
  <h3>{escape(route["title"])}</h3>
  <p>{escape(route["desc"])}</p>
  <strong>{escape(labels["route"])}</strong>
</a>
""")
    return f"""
<section class="section supply-quick-routes">
  <div class="section-head">
    <div><p class="eyebrow">{escape(labels["quick_route"])}</p><h2>{escape(labels["title"])}</h2></div>
    <a href="{lang_url(lang)}#quiz-section">{escape(t["start"])}</a>
  </div>
  <p class="section-intro">{escape(labels["intro"])}</p>
  <div class="supply-quick-grid">{"".join(cards)}</div>
</section>
"""


def supply_wishlist_section(lang: str) -> str:
    labels = SUPPLY_WISHLIST[lang]
    cards = []
    for slug, data in GUARDIANS.items():
        route = supply_route(lang, slug)
        guardian_name, guardian_type, _guardian_desc = data[lang]
        accent = next(meta["color"] for meta in QUIZ_TYPES.values() if meta["slug"] == slug)
        body = quote(f'{labels["body"]} {guardian_name} · {route["title"]}\n\n')
        cards.append(f"""
<article class="supply-wishlist-card" style="--route-accent:{accent}">
  {img_tag(data["prop"], route["title"])}
  <div>
    <p class="eyebrow">{escape(guardian_name)} · {escape(guardian_type)}</p>
    <h3>{escape(route["title"])}</h3>
    <p>{escape(route["mission"])}</p>
    <a href="mailto:contact@lovetypes.tw?subject={labels["subject"]}&body={body}">{escape(labels["request"])}</a>
  </div>
</article>
""")
    return f"""
<section class="section supply-wishlist-section">
  <div class="section-head"><div><p class="eyebrow">{escape(labels["eyebrow"])}</p><h2>{escape(labels["title"])}</h2></div><a href="{lang_url(lang, "contact")}">{escape(LANGS[lang]["contact"])}</a></div>
  <p class="section-intro">{escape(labels["intro"])}</p>
  <div class="supply-wishlist-grid">{"".join(cards)}</div>
  <p class="supply-wishlist-note">{escape(labels["note"])}</p>
</section>
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
    data_attrs = (
        f'data-story-name="{escape(name)}" '
        f'data-story-title="{escape(typ)}" '
        f'data-story-quote="{escape(route["mission"])}" '
        f'data-story-image="{escape(guardian["asset"])}" '
        f'data-story-slug="{escape(slug)}" '
        f'data-story-kicker="{escape(labels["story_kicker"])}" '
        f'data-story-cta="{escape(labels["story_cta"])}" '
        f'data-story-error="{escape(labels["story_error"])}"'
    )
    return f"""
<article class="{class_name}">
  <a class="collector-image-link" href="{image}" target="_blank" rel="noopener">
    {img_tag(image, f"{name} {labels['card']}")}
  </a>
  <div>
    <p class="eyebrow">{escape(typ)}</p>
    <h3>{escape(name)}</h3>
    <p>{escape(route["desc"])}</p>
    <div class="collector-actions">
      <a class="primary-btn" href="{image}" target="_blank" rel="noopener">{escape(labels["open"])}</a>
      <a class="secondary-btn" href="{image}" download>{escape(labels["download"])}</a>
      <button class="secondary-btn" type="button" data-result-action="story" {data_attrs}>{escape(labels["story"])}</button>
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


def keepsake_resume_script(lang: str) -> str:
    data = quiz_payload(lang)
    return f"""
<script>
(() => {{
  const quiz = {data};
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
    <article class="keepsake-resume-card" style="--result-accent:${{result.color}}">
      <a class="keepsake-resume-image" href="${{result.storyImage}}" target="_blank" rel="noopener">
        <img src="${{result.storyImage}}" alt="${{result.collectorTitle}} ${{result.name}}" loading="eager" decoding="async">
      </a>
      <div>
        <p class="eyebrow">${{result.collectorTitle}}</p>
        <h2>${{result.name}} · ${{result.type}}</h2>
        <p>${{result.collectorHint}}</p>
        <p><strong>${{result.supplyTitle}}</strong> · ${{result.supplyMission}}</p>
        <div class="keepsake-resume-actions">
          <a class="primary-btn" href="${{result.storyImage}}" target="_blank" rel="noopener">${{result.collectorOpen}}</a>
          <a class="secondary-btn" href="${{result.storyImage}}" download>${{result.collectorSave}}</a>
          <button class="secondary-btn" type="button" data-result-action="story" data-story-name="${{result.name}}" data-story-title="${{result.type}}" data-story-quote="${{result.supplyMission}}" data-story-image="${{result.image}}" data-story-slug="${{result.slug}}" data-story-kicker="${{result.collectorStoryKicker}}" data-story-cta="${{result.collectorStoryCta}}" data-story-error="${{result.collectorStoryError}}">${{result.collectorStory}}</button>
          <a class="secondary-btn" href="${{result.resourceUrl}}">${{quiz.labels.saved_route}}</a>
          <a class="secondary-btn" href="${{result.planUrl}}">${{quiz.labels.saved_plan}}</a>
          <button class="secondary-btn" type="button" data-clear-keepsake-result>${{quiz.labels.saved_clear}}</button>
        </div>
      </div>
    </article>`;
  box.hidden = false;
  box.querySelector('[data-clear-keepsake-result]').addEventListener('click', clearSavedResult);
}})();
</script>
"""


def keepsakes_page(lang: str) -> None:
    labels = KEEPSAKES_PAGE[lang]
    t = LANGS[lang]
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
<section class="section keepsake-personal-resume" data-keepsake-saved hidden></section>
{collector_section(lang)}
<section class="section keepsake-use-section">
  <div class="section-head"><div><p class="eyebrow">SAVE · SHARE · RETURN</p><h2>{escape(labels["how_title"])}</h2></div></div>
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


def character_supply_panel(lang: str, slug: str) -> str:
    labels = SUPPLY_LABELS[lang]
    route = supply_route(lang, slug)
    guide = route["guide"]
    book = route["book"]
    return f"""
<section class="section supply-panel-section">
  <div class="section-head">
    <div><p class="eyebrow">{escape(labels["deeper_route"])}</p><h2>{escape(route["title"])}</h2></div>
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
    <a class="secondary-btn" href="{lang_url(lang, "luna-yoga-music")}">{escape(labels["open_luna"])}</a>
    <a class="secondary-btn" href="{book["url"]}" target="_blank" rel="noopener sponsored">{escape(AFFILIATE_COPY[lang]["button"])}</a>
  </div>
</section>
"""


def character_route_snapshot(lang: str, slug: str) -> str:
    labels = SUPPLY_LABELS[lang]
    route = supply_route(lang, slug)
    guide = route["guide"]
    book = route["book"]
    guardian_name, guardian_type, _guardian_desc = route["guardian"][lang]
    guide_title, guide_desc = guide[lang]
    intro_joiner = "。" if lang == "zh" else ". "
    return f"""
<section class="section guardian-route-snapshot">
  <div class="section-head">
    <div><p class="eyebrow">{escape(labels["quick_route"])}</p><h2>{escape(route["title"])}</h2></div>
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
            "notice": "Mientras lees, elige una escena reciente: qué palabra, tiempo, acción, recuerdo o cercanía hizo que \"{desc}\" se volviera especialmente visible?",
            "practice": "Diseña hoy una práctica pequeña para {title}. Convierte la necesidad en una petición posible y mantén el plazo dentro de veinticuatro horas.",
            "mistakes": "No uses {title} como prueba de que alguien debe cambiar de inmediato. Úsalo como mapa para separar emoción, límite y petición en la puerta de {name}.",
            "scripts": ["No quiero decidir quién tiene razón; quiero explicar qué significa para mí \"{desc}\".", "Si reparamos solo un paso pequeño de {title}, me gustaría empezar con esta acción posible.", "Necesito que entiendas la situación de {name}, no solo la etiqueta."],
            "reflection": ["Qué desajuste reciente se parece más a {title}?", "Para \"{desc}\", qué quiero que la otra persona haga concretamente en lugar de adivinar mis emociones?", "La petición sería más clara si uso el lenguaje de {typ}?"],
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
        guide = next(g for g in GUIDES if g["slug"] == meta["guide"])
        route = supply_route(lang, meta["slug"])
        resource_url = lang_url(lang, "resources") + f"#supply-{meta['slug']}"
        results[key] = {
            "name": name,
            "type": typ,
            "desc": desc,
            "image": guardian["asset"],
            "color": meta["color"],
            "guardianUrl": lang_url(lang, "characters/" + meta["slug"]),
            "guideUrl": lang_url(lang, "guides/" + meta["guide"]),
            "guideTitle": guide[lang][0],
            "resourceUrl": resource_url,
            "supplyTitle": route["title"],
            "supplyDesc": route["desc"],
            "supplyMission": route["mission"],
            "supplyText": route["supply"],
            "supplyBook": route["book"]["title"][lang],
            "supplyBookUrl": route["book"]["url"],
            "lunaUrl": lang_url(lang, "luna-yoga-music"),
            "storyImage": guardian_story_image(lang, meta["slug"]),
            "slug": meta["slug"],
            "collectorTitle": COLLECTOR_LABELS[lang]["card"],
            "collectorHint": COLLECTOR_LABELS[lang]["share_hint"],
            "collectorOpen": COLLECTOR_LABELS[lang]["open"],
            "collectorSave": COLLECTOR_LABELS[lang]["download"],
            "collectorHall": COLLECTOR_LABELS[lang]["hall"],
            "collectorHallUrl": lang_url(lang, "keepsakes"),
            "collectorStory": COLLECTOR_LABELS[lang]["story"],
            "collectorStoryKicker": COLLECTOR_LABELS[lang]["story_kicker"],
            "collectorStoryCta": COLLECTOR_LABELS[lang]["story_cta"],
            "collectorStoryError": COLLECTOR_LABELS[lang]["story_error"],
            "planUrl": lang_url(lang, "repair-plan") + f"#plan-{meta['slug']}",
            "planLabel": REPAIR_PLAN[lang]["title"],
            "tips": QUIZ_TIPS[lang][key],
            "starterKit": starter_kit_payload(lang, resource_url),
        }
    payload = {
        "labels": QUIZ_LABELS[lang],
        "questions": questions,
        "results": results,
        "order": type_order,
        "shareUrl": DOMAIN + lang_url(lang).rstrip("/") + "/",
    }
    return json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")


def quiz_script(lang: str) -> str:
    data = quiz_payload(lang)
    return f"""
<script>
(() => {{
  const quiz = {data};
  const root = document.querySelector('[data-quiz-root]');
  if (!root) return;
  const intro = root.querySelector('[data-quiz-intro]');
  const quizBox = root.querySelector('[data-quiz-box]');
  const resultBox = root.querySelector('[data-quiz-result]');
  const savedBox = root.querySelector('[data-quiz-saved]');
  const startButtons = root.querySelectorAll('[data-quiz-start]');
  const storageKey = `lovetypes:${{location.pathname}}:quiz-result`;
  const sharedStorageKey = "lovetypes:{lang}:quiz-result";
  let current = 0;
  let selected = null;
  const answers = [];

  function show(el) {{ el.hidden = false; }}
  function hide(el) {{ el.hidden = true; }}
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
  function renderSavedResult() {{
    if (!savedBox) return;
    const saved = readSavedResult();
    if (!saved) {{
      hide(savedBox);
      savedBox.innerHTML = '';
      return;
    }}
    const result = quiz.results[saved.primaryKey];
    const cardUrl = new URL(result.storyImage, location.origin).href;
    const savedShareText = `${{quiz.labels.share_prefix}}：${{result.name}}｜${{result.type}} ${{cardUrl}}`;
    savedBox.innerHTML = `
      <article class="quiz-saved-card" style="--result-accent:${{result.color}}">
        <img src="${{result.image}}" alt="${{result.name}}" loading="lazy" decoding="async">
        <div>
          <p class="eyebrow">${{quiz.labels.saved_title}}</p>
          <h3>${{result.name}} · ${{result.type}}</h3>
          <p>${{quiz.labels.saved_intro}}</p>
          <div class="quiz-saved-actions">
            <a href="${{result.planUrl}}">${{quiz.labels.saved_plan}}</a>
            <a href="${{result.lunaUrl}}">${{quiz.labels.saved_luna}}</a>
            <a href="${{result.resourceUrl}}">${{quiz.labels.saved_route}}</a>
            <a href="${{result.storyImage}}" target="_blank" rel="noopener">${{quiz.labels.saved_card}}</a>
            <button type="button" data-result-action="story" data-story-name="${{result.name}}" data-story-title="${{result.type}}" data-story-quote="${{result.supplyMission}}" data-story-image="${{result.image}}" data-story-slug="${{result.slug}}" data-story-kicker="${{result.collectorStoryKicker}}" data-story-cta="${{result.collectorStoryCta}}" data-story-error="${{result.collectorStoryError}}">${{result.collectorStory}}</button>
            <button type="button" data-share-saved-result>${{quiz.labels.share}}</button>
            <button type="button" data-copy-saved-result>${{quiz.labels.saved_copy}}</button>
            <button type="button" data-clear-saved-result>${{quiz.labels.saved_clear}}</button>
          </div>
        </div>
      </article>`;
    show(savedBox);
    savedBox.querySelector('[data-share-saved-result]').addEventListener('click', async (event) => {{
      await shareGuardianResult(result, savedShareText, cardUrl, event.currentTarget);
    }});
    savedBox.querySelector('[data-copy-saved-result]').addEventListener('click', async (event) => {{
      await copyShareText(savedShareText, event.currentTarget);
    }});
    savedBox.querySelector('[data-clear-saved-result]').addEventListener('click', () => {{
      localStorage.removeItem(storageKey);
      localStorage.removeItem(sharedStorageKey);
      renderSavedResult();
    }});
  }}
  function progressText() {{
    return quiz.labels.progress.replace('{{current}}', String(current + 1)).replace('{{total}}', String(quiz.questions.length));
  }}
  function renderQuestion() {{
    const q = quiz.questions[current];
    quizBox.innerHTML = `
      <div class="quiz-progress"><div class="quiz-progress-bar"><span style="width:${{Math.round(current / quiz.questions.length * 100)}}%"></span></div><p>${{progressText()}}</p></div>
      <article class="quiz-card">
        <p class="eyebrow">${{quiz.labels.question}} ${{current + 1}}</p>
        <h3>${{q.text}}</h3>
        <div class="quiz-options">
          ${{q.options.map((opt, idx) => `<button type="button" class="quiz-option" data-type="${{opt.type}}"><span>${{idx + 1}}</span>${{opt.text}}</button>`).join('')}}
        </div>
        <button type="button" class="primary-btn quiz-next" disabled>${{current === quiz.questions.length - 1 ? quiz.labels.see : quiz.labels.next}}</button>
      </article>`;
    selected = null;
    quizBox.querySelectorAll('.quiz-option').forEach((button) => {{
      button.addEventListener('click', () => {{
        selected = button.dataset.type;
        quizBox.querySelectorAll('.quiz-option').forEach((item) => item.classList.remove('selected'));
        button.classList.add('selected');
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
  function renderResult() {{
    hide(quizBox);
    const counts = Object.fromEntries(quiz.order.map((key) => [key, 0]));
    answers.forEach((key) => counts[key] += 1);
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    const primaryKey = sorted[0][0];
    const secondaryKey = sorted[1] && sorted[1][1] === sorted[0][1] ? sorted[1][0] : null;
    const result = quiz.results[primaryKey];
    const total = answers.length || 1;
    const cardUrl = new URL(result.storyImage, location.origin).href;
    const shareText = `${{quiz.labels.share_prefix}}：${{result.name}}｜${{result.type}} ${{cardUrl}}`;
    window.lovetypesLastResult = {{
      name: result.name,
      title: result.type,
      quote: result.supplyMission,
      image: result.image,
      slug: result.slug
    }};
    try {{
      localStorage.setItem(storageKey, JSON.stringify({{ primaryKey, savedAt: new Date().toISOString() }}));
      localStorage.setItem(sharedStorageKey, JSON.stringify({{ primaryKey, savedAt: new Date().toISOString() }}));
    }} catch (error) {{}}
    resultBox.innerHTML = `
      <article class="quiz-result-card" style="--result-accent:${{result.color}}">
        <img src="${{result.image}}" alt="${{result.name}}" loading="lazy" decoding="async">
        <div class="quiz-result-copy">
          <p class="eyebrow">${{quiz.labels.result_label}}</p>
          <h3>${{result.name}}</h3>
          <span class="result-type">${{result.type}}${{secondaryKey ? ' · ' + quiz.labels.tie : ''}}</span>
          <p>${{result.desc}}</p>
        </div>
      </article>
      <section class="quiz-score-card"><h3>${{quiz.labels.score_title}}</h3>
        ${{sorted.map(([key, count]) => {{
          const item = quiz.results[key];
          const pct = Math.round(count / total * 100);
          return `<div class="score-row"><div><span>${{item.type}}</span><strong>${{pct}}%</strong></div><div class="score-bar"><span style="width:${{pct}}%; background:${{item.color}}"></span></div></div>`;
        }}).join('')}}
      </section>
      <section class="quiz-advice-card"><h3>${{quiz.labels.tips_title}}</h3><ul>${{result.tips.map((tip) => `<li>${{tip}}</li>`).join('')}}</ul></section>
      <section class="quiz-action-compass" aria-label="${{quiz.labels.compass_title}}">
        <div class="quiz-action-head">
          <p class="eyebrow">${{quiz.labels.compass_title}}</p>
          <h3>${{result.name}} ${{quiz.labels.routes_title}}</h3>
        </div>
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
            <a href="${{result.resourceUrl}}">${{quiz.labels.book_action}}</a>
          </article>
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
        <a class="secondary-btn" href="${{result.resourceUrl}}">${{quiz.labels.supply_action}}</a>
      </section>
      <section class="quiz-collector-card">
        <img src="${{result.storyImage}}" alt="${{result.collectorTitle}} ${{result.name}}" loading="lazy" decoding="async">
        <div>
          <p class="eyebrow">${{result.collectorTitle}}</p>
          <h3>${{result.name}}</h3>
          <p>${{result.collectorHint}}</p>
          <div class="quiz-collector-actions">
            <a class="primary-btn" href="${{result.storyImage}}" target="_blank" rel="noopener">${{result.collectorOpen}}</a>
            <a class="secondary-btn" href="${{result.storyImage}}" download>${{result.collectorSave}}</a>
            <button class="secondary-btn" type="button" data-result-action="story" data-story-kicker="${{result.collectorStoryKicker}}" data-story-cta="${{result.collectorStoryCta}}" data-story-error="${{result.collectorStoryError}}">${{result.collectorStory}}</button>
            <a class="secondary-btn" href="${{result.collectorHallUrl}}">${{result.collectorHall}}</a>
          </div>
        </div>
      </section>
      <nav class="quiz-route-card" aria-label="${{quiz.labels.routes_title}}">
        <a class="primary-btn" href="${{result.planUrl}}">${{result.planLabel}}</a>
        <a class="secondary-btn" href="${{result.resourceUrl}}">${{quiz.labels.resources_link}}</a>
        <a class="secondary-btn" href="${{result.guardianUrl}}">${{quiz.labels.guardian_link}}</a>
        <a class="secondary-btn" href="${{result.guideUrl}}">${{quiz.labels.guide_link}}</a>
      </nav>
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
    renderSavedResult();
    resultBox.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }}
  function startQuiz() {{
    current = 0;
    selected = null;
    answers.length = 0;
    hide(intro);
    hide(resultBox);
    show(quizBox);
    renderQuestion();
    quizBox.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }}
  startButtons.forEach((button) => button.addEventListener('click', startQuiz));
  renderSavedResult();
}})();
</script>
"""


def supply_resume_script(lang: str) -> str:
    data = quiz_payload(lang)
    bookstore_label = AFFILIATE_COPY[lang]["button"]
    return f"""
<script>
(() => {{
  const quiz = {data};
  const bookstoreLabel = "{escape(bookstore_label)}";
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

  function clearSavedResult() {{
    storageKeys.forEach((key) => localStorage.removeItem(key));
    box.hidden = true;
    box.innerHTML = '';
  }}

  const saved = readSavedResult();
  if (!saved) return;
  const result = quiz.results[saved.primaryKey];
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
    <article class="quiz-saved-card supply-resume-card" style="--result-accent:${{result.color}}">
      <img src="${{result.image}}" alt="${{result.name}}" loading="eager" decoding="async">
      <div>
        <p class="eyebrow">${{quiz.labels.saved_title}}</p>
        <h2>${{result.supplyTitle}}</h2>
        <p>${{result.name}} · ${{result.type}}</p>
        <p>${{result.supplyDesc}}</p>
        <div class="supply-resume-next">
          ${{resumeSteps.map((step) => `
            <section>
              <span>${{step.number}}</span>
              <h3>${{step.title}}</h3>
              <p>${{step.desc}}</p>
              <a href="${{step.href}}" ${{step.external ? 'target="_blank" rel="noopener sponsored"' : ''}}>${{step.action}}</a>
            </section>
          `).join('')}}
        </div>
        <div class="quiz-saved-actions">
          <a href="${{result.planUrl}}">${{quiz.labels.saved_plan}}</a>
          <a href="${{result.lunaUrl}}">${{quiz.labels.saved_luna}}</a>
          <a href="${{result.resourceUrl}}">${{quiz.labels.saved_route}}</a>
          <a href="${{result.guardianUrl}}">${{quiz.labels.guardian_link}}</a>
          <button type="button" data-clear-supply-result>${{quiz.labels.saved_clear}}</button>
        </div>
      </div>
    </article>`;
  box.hidden = false;
  box.querySelector('[data-clear-supply-result]').addEventListener('click', clearSavedResult);
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
    data = quiz_payload(lang)
    return f"""
<script>
(() => {{
  const quiz = {data};
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
    <article class="quiz-saved-card guide-resume-card" style="--result-accent:${{result.color}}">
      <img src="${{result.image}}" alt="${{result.name}}" loading="lazy" decoding="async">
      <div>
        <p class="eyebrow">${{quiz.labels.guide_resume_title}}</p>
        <h2>${{result.name}} · ${{result.type}}</h2>
        <p>${{quiz.labels.guide_resume_intro}}</p>
        <div class="quiz-saved-actions">
          <a href="${{result.planUrl}}">${{quiz.labels.saved_plan}}</a>
          <a href="${{result.guardianUrl}}">${{quiz.labels.guardian_link}}</a>
          <a href="${{result.resourceUrl}}">${{quiz.labels.saved_route}}</a>
          <a href="${{result.lunaUrl}}">${{quiz.labels.saved_luna}}</a>
          <button type="button" data-clear-guide-result>${{quiz.labels.saved_clear}}</button>
        </div>
      </div>
    </article>`;
  box.hidden = false;
  box.querySelector('[data-clear-guide-result]').addEventListener('click', clearSavedResult);
}})();
</script>
"""


def home(lang: str) -> None:
    t = LANGS[lang]
    quiz = QUIZ_LABELS[lang]
    guide_cards = "".join(guide_card(lang, g) for g in GUIDES[:6])
    guardian_cards = "".join(character_card(lang, slug, data) for slug, data in GUARDIANS.items())
    body = f"""
<section class="hero">
  <div class="hero-copy">
    <p class="eyebrow">HEART GARDEN FIELD NOTES</p>
    <h1>{escape(t["brand"])}</h1>
    <p class="lead">{escape(t["tagline"])}</p>
    <div class="hero-actions"><a class="primary-btn" href="{lang_url(lang, "guides")}">{escape(t["guides"])}</a><a class="secondary-btn" href="#quiz-section">{escape(t["start"])}</a></div>
  </div>
  <picture><source media="(max-width: 720px)" srcset="/assets/lovetypes/backgrounds/guardian-garden-mobile.webp" width="900" height="506" />{img_tag("/assets/lovetypes/backgrounds/guardian-garden.webp", "LoveTypes guardian garden", lazy=False, priority=True)}</picture>
</section>
<section class="section intro-grid">
  <div><p class="eyebrow">UNIVERSE PROMISE</p><h2>{escape(t["trust_intro"])}</h2></div>
  <div class="text-stack"><p>{escape(PRACTICAL_COPY[lang]["why"])}</p><p>{escape(PRACTICAL_COPY[lang]["notice"])}</p></div>
</section>
<section class="section" id="guides-section"><div class="section-head"><p class="eyebrow">GUARDIAN FIELD GUIDES</p><h2>{escape(t["guide_index_title"])}</h2><a href="{lang_url(lang, "guides")}">{escape(t["learn_more"])}</a></div><div class="card-grid">{guide_cards}</div></section>
<section class="section" id="types-section"><div class="section-head"><p class="eyebrow">FIVE GUARDIANS</p><h2>{escape(t["guardians"])}</h2><a href="{lang_url(lang, "characters")}">{escape(t["learn_more"])}</a></div><div class="guardian-grid">{guardian_cards}</div></section>
<section class="quiz-band" id="quiz-section">
  <div class="quiz-shell" data-quiz-root>
    <div class="quiz-intro" data-quiz-intro>
      <p class="eyebrow">{escape(quiz["eyebrow"])}</p>
      <h2>{escape(quiz["title"])}</h2>
      <p>{escape(quiz["intro"])}</p>
      <button type="button" class="primary-btn" data-quiz-start>{escape(quiz["start"])}</button>
    </div>
    <div class="quiz-saved" data-quiz-saved hidden></div>
    <div class="quiz-stage" data-quiz-box hidden></div>
    <div class="quiz-result" data-quiz-result hidden></div>
  </div>
</section>
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"{escape(t["brand"])}","url":"{DOMAIN}{lang_url(lang).rstrip("/")}/","inLanguage":"{t["code"]}"}}</script>'
    write(page_path(lang), layout(lang, t["home_title"], t["home_desc"], "", body + quiz_script(lang), "", "website", "/og-cover.jpg", schema))


def characters_index_page(lang: str) -> None:
    t = LANGS[lang]
    guardian_cards = "".join(character_card(lang, slug, data) for slug, data in GUARDIANS.items())
    title = f"{t['guardians']} | LoveTypes"
    desc = t["trust_intro"]
    body = f"""
<section class="page-hero compact guardian-index-hero">
  <p class="eyebrow">FIVE GUARDIANS</p>
  <h1>{escape(t["guardians"])}</h1>
  <p>{escape(desc)}</p>
  <div class="hero-actions"><a class="primary-btn" href="{lang_url(lang)}#quiz-section">{escape(t["start"])}</a><a class="secondary-btn" href="{lang_url(lang, "guides")}">{escape(t["guides"])}</a></div>
</section>
<section class="section">
  <div class="section-head"><p class="eyebrow">HEART GARDEN MAP</p><h2>{escape(t["guardians"])}</h2><a href="{lang_url(lang, "resources")}">{escape(t["resources"])}</a></div>
  <div class="guardian-grid">{guardian_cards}</div>
</section>
<section class="section intro-grid">
  <div><h2>{escape(PAGE_SECTIONS[lang]["how"])}</h2><p>{escape(PRACTICAL_COPY[lang]["why"])}</p></div>
  <div class="text-stack"><h2>{escape(PAGE_SECTIONS[lang]["need"])}</h2><p>{escape(PRACTICAL_COPY[lang]["notice"])}</p><p>{escape(PRACTICAL_COPY[lang]["practice"])}</p></div>
</section>
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"CollectionPage","name":"{escape(t["guardians"])}","description":"{escape(desc)}","url":"{abs_url(lang, "characters")}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
    guardian_items = [(data[lang][0], abs_url(lang, "characters/" + slug)) for slug, data in GUARDIANS.items()]
    schema += item_list_schema(t["guardians"], desc, guardian_items)
    write(page_path(lang, "characters"), layout(lang, title, desc, "characters", body, t["guardians"], "website", "/og-cover.jpg", schema))


def guides_index(lang: str) -> None:
    t = LANGS[lang]
    cards = "".join(guide_card(lang, g) for g in GUIDES)
    body = f"""
<section class="page-hero compact"><p class="eyebrow">HEART GARDEN FIELD GUIDE</p><h1>{escape(t["guide_index_title"])}</h1><p>{escape(t["guide_index_desc"])}</p></section>
{guide_index_compass(lang)}
<section class="section"><div class="card-grid wide">{cards}</div></section>
<section class="section note-section"><h2>{escape(t["boundary"])}</h2><p>{escape(t["boundary_text"])}</p></section>
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"CollectionPage","name":"{escape(t["guide_index_title"])}","description":"{escape(t["guide_index_desc"])}","url":"{abs_url(lang, "guides")}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
    guide_items = [(guide[lang][0], abs_url(lang, "guides/" + guide["slug"])) for guide in GUIDES]
    schema += item_list_schema(t["guide_index_title"], t["guide_index_desc"], guide_items)
    write(page_path(lang, "guides"), layout(lang, t["guide_index_title"], t["guide_index_desc"], "guides", body, t["guides"], "website", "/og-cover.jpg", schema))


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
  {img_tag(GUARDIANS[guide["guardian"]]["prop"], guardian[1], lazy=False)}
</section>
<section class="section guide-personal-resume" data-guide-saved hidden></section>
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
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Article","headline":"{escape(title)}","description":"{escape(desc)}","url":"{abs_url(lang, "guides/" + guide["slug"])}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","author":{{"@type":"Organization","name":"LoveTypes"}},"publisher":{{"@type":"Organization","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
    write(page_path(lang, "guides/" + guide["slug"]), layout(lang, title, desc, "guides/" + guide["slug"], body + guide_resume_script(lang), t["guides"], "article", "/assets/lovetypes/share/guide-toolkit-og.jpg", schema))


def legacy_zh_guide_page(slug: str, title: str, desc: str, canonical_target: str) -> None:
    lang = "zh"
    t = LANGS[lang]
    related = next(g for g in GUIDES if g["slug"] == canonical_target)
    guardian = GUARDIANS[related["guardian"]][lang]
    detail = guide_detail_copy(lang, title, desc, guardian)
    body = f"""
<section class="article-hero">
  <div><p class="eyebrow">HEART GARDEN ARCHIVE</p><h1>{escape(title)}</h1><p>{escape(desc)}</p></div>
  {img_tag("/assets/lovetypes/share/guide-toolkit-og.jpg", "LoveTypes guide", lazy=False)}
</section>
<section class="section guide-personal-resume" data-guide-saved hidden></section>
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
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Article","headline":"{escape(title)}","description":"{escape(desc)}","url":"{abs_url(lang, "guides/" + slug)}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","author":{{"@type":"Organization","name":"LoveTypes"}},"publisher":{{"@type":"Organization","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
    write(page_path(lang, "guides/" + slug), layout(lang, title, desc, "guides/" + slug, body + guide_resume_script(lang), t["guides"], "article", "/assets/lovetypes/share/guide-toolkit-og.jpg", schema))


def character_page(lang: str, slug: str, data: dict) -> None:
    t = LANGS[lang]
    labels = PAGE_SECTIONS[lang]
    name, typ, desc = data[lang]
    detail = character_detail_copy(lang, name, typ, desc)
    related_guides = [g for g in GUIDES if g["guardian"] == slug][:3]
    related_html = "".join(guide_card(lang, g) for g in related_guides)
    guardian_nav = "".join(character_link_card(lang, item_slug, item_data, slug) for item_slug, item_data in GUARDIANS.items())
    scripts = "".join(f"<li>{escape(item)}</li>" for item in detail["scripts"])
    reflections = "".join(f"<li>{escape(item)}</li>" for item in detail["reflection"])
    body = f"""
<section class="guardian-hero">
  <div><p class="eyebrow">{escape(typ)}</p><h1>{escape(name)}</h1><p>{escape(desc)}</p><div class="hero-actions"><a class="primary-btn" href="{lang_url(lang)}#quiz-section">{escape(t["start"])}</a><a class="secondary-btn" href="{lang_url(lang, "characters")}">{escape(t["guardians"])}</a></div></div>
  {img_tag(data["asset"], name, lazy=False)}
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
<section class="section"><div class="section-head"><p class="eyebrow">RELATED GUIDES</p><h2>{escape(t["read"])}</h2></div><div class="card-grid">{related_html}</div></section>
<section class="section guardian-nav-section"><div class="section-head"><p class="eyebrow">FIVE GUARDIANS</p><h2>{escape(t["guardians"])}</h2><a href="{lang_url(lang, "characters")}">{escape(t["learn_more"])}</a></div><div class="guardian-grid compact">{guardian_nav}</div></section>
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"ProfilePage","name":"{escape(name)}","description":"{escape(desc)}","url":"{abs_url(lang, "characters/" + slug)}","inLanguage":"{t["code"]}","about":{{"@type":"Thing","name":"{escape(typ)}"}},"dateModified":"{UPDATED}"}}</script>'
    write(page_path(lang, "characters/" + slug), layout(lang, f"{name} | {typ} | LoveTypes", desc, "characters/" + slug, body, t["guardians"], "profile", data["asset"], schema))


def resources_page(lang: str) -> None:
    t = LANGS[lang]
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
{image}  <span class="eyebrow">TRAVELER SUPPLY</span>
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
  <a class="primary-btn affiliate-book-link" href="{book["url"]}" target="_blank" rel="noopener sponsored">{escape(affiliate_labels["button"])}</a>
</article>
""")
    body = f"""
<section class="page-hero compact"><p class="eyebrow">HEART GARDEN SUPPLIES</p><h1>{escape(t["resources"])}</h1><p>{escape(t["resources_desc"])}</p><p class="affiliate-disclosure">{escape(AFFILIATE_DISCLOSURE[lang])}</p></section>
<section class="section quiz-saved supply-personal-resume" data-supply-saved hidden></section>
{supply_quick_route_nav(lang)}
<section class="section resource-path"><div><p class="eyebrow">SUPPLY ROUTE</p><h2>{escape(t["resources_desc"])}</h2></div><div class="resource-steps">{resource_steps}</div></section>
<section class="section supply-compass">
  <div class="section-head"><div><p class="eyebrow">{escape(decision["eyebrow"])}</p><h2>{escape(decision["title"])}</h2></div></div>
  <p class="section-intro">{escape(decision["intro"])}</p>
  <div class="supply-compass-grid">{decision_steps}</div>
</section>
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
<section class="section affiliate-books"><div class="section-head"><p class="eyebrow">{escape(affiliate_labels["eyebrow"])}</p><h2>{escape(affiliate_labels["title"])}</h2></div><p>{escape(affiliate_labels["intro"])}</p><div class="affiliate-book-grid">{"".join(book_cards)}</div><p class="affiliate-disclosure">{escape(AFFILIATE_DISCLOSURE[lang])}</p></section>
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
    data = quiz_payload(lang)
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
<script>
(() => {{
  const quiz = {data};
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
    form.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
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
      <article class="repair-resume-card" style="--result-accent:${{result.color}}">
        <img src="${{result.image}}" alt="${{result.name}}" loading="lazy" decoding="async">
        <div>
          <p class="eyebrow">${{resumeTitle}}</p>
          <h2>${{result.name}} · ${{result.type}}</h2>
          <p>${{resumeIntro}}</p>
          <p><strong>${{result.supplyTitle}}</strong> · ${{result.supplyMission}}</p>
          <div class="repair-resume-actions">
            <a class="primary-btn" href="${{result.planUrl}}">${{resumePlan}}</a>
            <button class="secondary-btn" type="button" data-fill-repair>${{resumeFill}}</button>
            <a class="secondary-btn" href="${{result.storyImage}}" target="_blank" rel="noopener">${{quiz.labels.saved_card}}</a>
            <a class="secondary-btn" href="${{result.collectorHallUrl}}">${{result.collectorHall}}</a>
            <a class="secondary-btn" href="${{result.lunaUrl}}">${{quiz.labels.saved_luna}}</a>
            <a class="secondary-btn" href="${{result.supplyBookUrl}}" target="_blank" rel="noopener sponsored">${{bookstoreLabel}}</a>
          </div>
        </div>
      </article>`;
    resumeBox.hidden = false;
    resumeBox.querySelector('[data-fill-repair]')?.addEventListener('click', () => fillFromResult(result));
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
  <textarea data-field="{idx}" placeholder="{escape(placeholder)}"></textarea>
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
      <a class="secondary-btn" href="{lang_url(lang, "luna-yoga-music")}">{escape(SUPPLY_LABELS[lang]["open_luna"])}</a>
      <a class="secondary-btn" href="{book["url"]}" target="_blank" rel="noopener sponsored">{escape(AFFILIATE_COPY[lang]["button"])}</a>
    </div>
  </div>
</article>
""")
    body = f"""
<section class="page-hero compact repair-plan-hero">
  <p class="eyebrow">{escape(plan["eyebrow"])}</p>
  <h1>{escape(plan["title"])}</h1>
  <p>{escape(plan["desc"])}</p>
  <div class="hero-actions"><a class="primary-btn" href="{lang_url(lang)}#quiz-section">{escape(plan["start"])}</a><a class="secondary-btn" href="{lang_url(lang, "resources")}">{escape(plan["resources"])}</a></div>
</section>
<section class="section repair-result-resume" data-repair-saved hidden></section>
<section class="section repair-plan-section">
  <div class="section-head"><div><p class="eyebrow">WEEK ROUTE</p><h2>{escape(plan["days_title"])}</h2></div><a href="{lang_url(lang, "resources")}">{escape(plan["resources"])}</a></div>
  <div class="repair-day-grid">{days}</div>
</section>
<section class="section repair-worksheet-section">
  <div class="section-head"><div><p class="eyebrow">PRINTABLE WORKSHEET</p><h2>{escape(plan["worksheet_title"])}</h2></div><button class="secondary-btn print-button" type="button" onclick="window.print()">{escape(plan["print"])}</button></div>
  <p class="section-intro">{escape(plan["worksheet_intro"])}</p>
  <div class="worksheet-meta"><p>{escape(plan["autosave"])}</p><div><span data-worksheet-status>{escape(plan["saved"])}</span><button class="primary-btn compact-action" type="button" data-copy-worksheet-summary>{escape(plan["copy_summary"])}</button><button class="secondary-btn" type="button" data-clear-worksheet>{escape(plan["clear"])}</button></div></div>
  <form class="repair-worksheet" data-repair-worksheet>{worksheet_fields}</form>
</section>
{repair_worksheet_script(lang)}
<section class="section repair-guardian-section">
  <div class="section-head"><div><p class="eyebrow">GUARDIAN ROUTES</p><h2>{escape(plan["guardian_title"])}</h2></div><a href="{lang_url(lang)}#quiz-section">{escape(plan["start"])}</a></div>
  <div class="repair-guardian-grid">{"".join(guardian_rows)}</div>
</section>
<section class="section intro-grid">
  <div><h2>{escape(t["boundary"])}</h2><p>{escape(t["boundary_text"])}</p></div>
  <div class="text-stack"><h2>{escape(SUPPLY_LABELS[lang]["not_now"])}</h2><p>{escape(SUPPLY_LABELS[lang]["not_now_text"])}</p></div>
</section>
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"HowTo","name":"{escape(plan["title"])}","description":"{escape(plan["desc"])}","url":"{abs_url(lang, "repair-plan")}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
    page_title = f"{plan['title']} | LoveTypes" if lang == "zh" else f"{plan['title']} | LoveTypes {t['name']}"
    write(page_path(lang, "repair-plan"), layout(lang, page_title, plan["desc"], "repair-plan", body, plan["title"], "article", "/assets/lovetypes/share/guide-toolkit-og.jpg", schema))


def luna_resume_script(lang: str) -> str:
    data = quiz_payload(lang)
    labels = LUNA_RESUME[lang]
    flow = LUNA_GUARDIAN_FLOW[lang]
    return f"""
<script>
(() => {{
  const quiz = {data};
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
    <article class="luna-resume-card" style="--result-accent:${{result.color}}">
      <img src="${{result.image}}" alt="${{result.name}}" loading="lazy" decoding="async">
      <div>
        <p class="eyebrow">${{labels.eyebrow}}</p>
        <h2>${{labels.title}}</h2>
        <p>${{labels.intro}}</p>
        <p><strong>${{result.name}} · ${{result.type}}</strong></p>
        <p><strong>${{labels.practice}}:</strong> ${{practice}}</p>
        <div class="luna-resume-actions">
          <a class="primary-btn" href="${{result.planUrl}}">${{labels.repair}}</a>
          <a class="secondary-btn" href="${{result.resourceUrl}}">${{labels.route}}</a>
          <a class="secondary-btn" href="${{result.supplyBookUrl}}" target="_blank" rel="noopener sponsored">${{labels.book}}</a>
        </div>
      </div>
    </article>`;
  box.hidden = false;
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
    <a class="primary-btn" href="https://www.youtube.com/channel/UCPeQjvN9q2kY2s09PuRSL6w" target="_blank" rel="noopener">{escape(offer["listen"])}</a>
    <a class="secondary-btn" href="{lang_url(lang, "resources")}">{escape(offer["resources"])}</a>
    <a class="secondary-btn" href="mailto:contact@lovetypes.tw?subject=Luna%20night%20supply">{escape(offer["contact"])}</a>
  </div>
</section>
"""


def luna_page(lang: str) -> None:
    t = LANGS[lang]
    luna = LUNA_CONTENT[lang]
    flow = LUNA_GUARDIAN_FLOW[lang]
    use_cases = "".join(f"<article><h3>{escape(title)}</h3><p>{escape(desc)}</p></article>" for title, desc in LUNA_USE_CASES[lang])
    guardian_flow_cards = []
    for slug, data in GUARDIANS.items():
        name, typ, _desc = data[lang]
        guardian_flow_cards.append(f"""
<article class="luna-guardian-card">
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
    <div class="hero-actions"><a class="primary-btn" href="{lang_url(lang, "resources")}">{escape(luna["primary"])}</a><a class="secondary-btn" href="{lang_url(lang, "guides/repair-after-conflict")}">{escape(luna["secondary"])}</a></div>
  </div>
  <div class="luna-orb">{img_tag("/luna-yoga-music/images/hero.webp", "Luna Yoga Music", lazy=False, priority=True)}</div>
</section>
<section class="section luna-result-resume" data-luna-saved hidden></section>
{luna_night_protocol(lang)}
<section class="section luna-strip">
  <div><p class="eyebrow">CALM PATHS</p><h2>{escape(t["luna_desc"])}</h2></div>
  <div class="luna-card-grid">{"".join(section_cards)}</div>
</section>
<section class="section luna-use-cases">
  <div class="section-head"><div><p class="eyebrow">NIGHT HEART SUPPLY</p><h2>{escape(luna["headline"])}</h2></div><a href="{lang_url(lang, "resources")}">{escape(luna["primary"])}</a></div>
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
    write(page_path(lang, "luna-yoga-music"), layout(lang, page_title, t["luna_desc"], "luna-yoga-music", body, t["resources"], "website", "/luna-yoga-music/images/hero.webp", schema))


def contact_request_section(lang: str) -> str:
    request = CONTACT_REQUESTS[lang]
    cards = "".join(
        f"<article><span>{idx}</span><h3>{escape(title)}</h3><p>{escape(body)}</p></article>"
        for idx, (title, body) in enumerate(request["items"], 1)
    )
    return f"""
<section class="section contact-request-section">
  <div class="section-head"><div><p class="eyebrow">{escape(request["eyebrow"])}</p><h2>{escape(request["title"])}</h2></div></div>
  <p class="section-intro">{escape(request["intro"])}</p>
  <div class="contact-request-grid">{cards}</div>
  <div class="contact-request-note">
    <p>{escape(request["note"])}</p>
    <a class="primary-btn" href="mailto:contact@lovetypes.tw?subject={request["subject"]}">{escape(request["cta"])}</a>
  </div>
</section>
"""


def simple_page(lang: str, slug: str) -> None:
    t = LANGS[lang]
    labels = PAGE_SECTIONS[lang]
    copy = PRACTICAL_COPY[lang]
    titles = {
        "theory": (t["theory"], t["tagline"]),
        "resources": (t["resources"], t["resources_desc"]),
        "about": (t["about"], t["trust_intro"]),
        "contact": (t["contact"], t["contact_desc"]),
        "privacy": (t["privacy"], t["privacy_desc"]),
        "terms": (t["terms"], t["terms_desc"]),
        "luna-yoga-music": (t["luna_title"], t["luna_desc"]),
    }
    title, desc = titles[slug]
    if slug == "about":
        about_items = "".join(f"<h2>{escape(heading)}</h2><p>{body_text}</p>" for heading, body_text in ABOUT_SECTIONS[lang])
        body = f"""
<section class="page-hero compact"><p class="eyebrow">ABOUT LOVETYPES</p><h1>{escape(title)}</h1><p>{escape(desc)}</p></section>
<section class="section article-body standalone">
  {about_items}
  <h2>{escape(t["boundary"])}</h2>
  <p>{escape(t["boundary_text"])}</p>
  <div class="callout"><strong>LoveTypes</strong><p>{escape(PRACTICAL_COPY[lang]["mistakes"])}</p></div>
</section>
"""
        schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"AboutPage","name":"{escape(title)}","description":"{escape(desc)}","url":"{abs_url(lang, slug)}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
        page_title = f"{title} | LoveTypes" if lang == "zh" else f"{title} | LoveTypes {t['name']}"
        write(page_path(lang, slug), layout(lang, page_title, desc, slug, body, title, "website", "/og-cover.jpg", schema))
        return
    if slug == "theory":
        theory_items = "".join(f"<h2>{escape(heading)}</h2><p>{escape(body_text)}</p>" for heading, body_text in THEORY_SECTIONS[lang])
        guardian_cards = "".join(character_card(lang, guardian_slug, guardian_data) for guardian_slug, guardian_data in GUARDIANS.items())
        faq_items = "".join(f"<article><h3>{escape(q)}</h3><p>{escape(a)}</p></article>" for q, a in THEORY_FAQ[lang])
        body = f"""
<section class="page-hero compact"><p class="eyebrow">LOVE LANGUAGE THEORY</p><h1>{escape(title)}</h1><p>{escape(desc)}</p><div class="hero-actions"><a class="primary-btn" href="{lang_url(lang)}#quiz-section">{escape(t["start"])}</a><a class="secondary-btn" href="{lang_url(lang, "characters")}">{escape(t["guardians"])}</a></div></section>
<section class="section article-body standalone">
  {theory_items}
  <h2>{escape(t["boundary"])}</h2>
  <p>{escape(t["boundary_text"])}</p>
</section>
<section class="section guardian-nav-section"><div class="section-head"><p class="eyebrow">FIVE GUARDIANS</p><h2>{escape(t["guardians"])}</h2><a href="{lang_url(lang, "characters")}">{escape(t["learn_more"])}</a></div><div class="guardian-grid compact">{guardian_cards}</div></section>
<section class="section faq-section"><div class="section-head"><p class="eyebrow">LOVE LANGUAGE FAQ</p><h2>{escape(t["theory"])}</h2></div><div class="faq-grid">{faq_items}</div></section>
"""
        schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"{escape(title)}","description":"{escape(desc)}","url":"{abs_url(lang, slug)}","inLanguage":"{t["code"]}","dateModified":"{UPDATED}","about":{{"@type":"Thing","name":"Five love languages"}},"isPartOf":{{"@type":"WebSite","name":"LoveTypes","url":"{DOMAIN}/"}}}}</script>'
        page_title = f"{title} | LoveTypes" if lang == "zh" else f"{title} | LoveTypes {t['name']}"
        write(page_path(lang, slug), layout(lang, page_title, desc, slug, body, title, "website", "/og-cover.jpg", schema))
        return
    extra = ""
    if slug == "contact":
        extra = '<p class="contact-line"><a href="mailto:contact@lovetypes.tw">contact@lovetypes.tw</a></p>'
    if slug in {"privacy", "terms"}:
        extra = f"<p><strong>Updated:</strong> {UPDATED}</p>"
    if slug in {"contact", "privacy", "terms"}:
        policy_items = "".join(f"<h2>{escape(heading)}</h2><p>{escape(body_text)}</p>" for heading, body_text in POLICY_SECTIONS[lang][slug])
        schema_type = {"contact": "ContactPage", "privacy": "WebPage", "terms": "WebPage"}[slug]
        contact_requests = contact_request_section(lang) if slug == "contact" else ""
        body = f"""
<section class="page-hero compact"><p class="eyebrow">LOVETYPES</p><h1>{escape(title)}</h1><p>{escape(desc)}</p>{extra}</section>
{contact_requests}
<section class="section article-body standalone">
  {policy_items}
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
    css_path = ROOT / "shared.css"
    css = css_path.read_text(encoding="utf-8")
    write(css_path, css.strip() + "\n")
    write(ROOT / CSS_ASSET.lstrip("/"), css.strip() + "\n")


def write_versioned_scripts() -> None:
    for source, target in (
        ("site-interactions.js", INTERACTIONS_ASSET),
        ("deferred-external.js", AFFILIATE_ASSET),
    ):
        script = (ROOT / source).read_text(encoding="utf-8")
        write(ROOT / target.lstrip("/"), script.strip() + "\n")


def write_support_files() -> None:
    urls = []
    for lang in LANGS:
        paths = ["", "guides", "characters", "theory", "resources", "repair-plan", "keepsakes", "luna-yoga-music", "about", "contact", "privacy", "terms"]
        paths += [f"guides/{g['slug']}" for g in GUIDES]
        paths += [f"characters/{slug}" for slug in GUARDIANS]
        for path in paths:
            urls.append(abs_url(lang, path))
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        sitemap.append(f"  <url><loc>{url}</loc><lastmod>{UPDATED}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>")
    sitemap.append("</urlset>")
    write(ROOT / "sitemap.xml", "\n".join(sitemap) + "\n")
    write(ROOT / "robots.txt", "User-agent: *\nAllow: /\n\nSitemap: https://lovetypes.tw/sitemap.xml\n")
    write(ROOT / "_headers", "/*\n  Cache-Control: public, max-age=600\n\n/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n\n/shared-*.css\n  Cache-Control: public, max-age=31536000, immutable\n\n/site-interactions-*.js\n  Cache-Control: public, max-age=31536000, immutable\n\n/deferred-external-*.js\n  Cache-Control: public, max-age=31536000, immutable\n")


def main() -> None:
    cleanup_versioned_assets()
    write_css()
    write_versioned_scripts()
    for lang in LANGS:
        home(lang)
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
        for slug in ["theory", "about", "contact", "privacy", "terms"]:
            simple_page(lang, slug)
    for slug, title, desc, target in LEGACY_ZH_GUIDES:
        legacy_zh_guide_page(slug, title, desc, target)
    write_support_files()


if __name__ == "__main__":
    main()
