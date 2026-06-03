#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://lovetypes.tw"
ADSENSE_ACCOUNT = "ca-pub-4093856660317740"
UPDATED = "2026-06-03"


LANGS = {
    "zh": {
        "code": "zh-TW",
        "prefix": "",
        "name": "繁體中文",
        "brand": "LoveTypes 情感守護者宇宙",
        "tagline": "把愛之語測驗結果，變成真實關係裡聽得懂、做得到、能修復的溝通方式。",
        "start": "開始命運儀式",
        "guides": "深度指南",
        "guardians": "守護者",
        "theory": "理論",
        "resources": "資源",
        "about": "關於",
        "contact": "聯絡",
        "privacy": "隱私",
        "terms": "條款",
        "read": "閱讀指南",
        "learn_more": "了解更多",
        "practice": "今日練習",
        "boundary": "內容邊界",
        "boundary_text": "LoveTypes 內容用於自我理解與關係溝通練習，不提供心理諮商、醫療建議、法律建議或個別關係診斷。若你正面臨暴力、控制、創傷或高風險處境，請優先尋求可信任的人與專業支援。",
        "home_title": "LoveTypes｜五種愛之語測驗與關係溝通指南",
        "home_desc": "LoveTypes 將五種愛之語轉化為五位情感守護者，提供測驗、角色解讀、伴侶溝通句型與關係修復練習。",
        "guide_index_title": "LoveTypes 深度指南｜把愛之語帶回真實關係",
        "guide_index_desc": "閱讀 LoveTypes 五種愛之語指南：測驗結果、吵架修復、遠距關係、界線、安全感與伴侶對話練習。",
        "trust_intro": "LoveTypes 是一個以五種愛之語為基礎的原創關係溝通網站，透過角色化敘事、情境測驗與實作指南，幫助使用者整理被愛需求與表達方式。",
    },
    "en": {
        "code": "en",
        "prefix": "en",
        "name": "English",
        "brand": "LoveTypes Emotion Guardians",
        "tagline": "Turn your love-language result into practical words, boundaries, repair rituals, and relationship habits.",
        "start": "Take the ritual",
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
        "boundary_text": "LoveTypes is for self-reflection and relationship communication practice. It is not therapy, medical advice, legal advice, or a diagnosis. If you are facing violence, coercive control, trauma, or urgent risk, seek trusted local and professional support first.",
        "home_title": "LoveTypes | Love Language Quiz and Relationship Guides",
        "home_desc": "LoveTypes turns the five love languages into five emotion guardians with a quiz, practical scripts, repair exercises, and relationship guides.",
        "guide_index_title": "LoveTypes Guides | Bring Love Languages Into Real Relationships",
        "guide_index_desc": "Explore LoveTypes guides for quiz results, conflict repair, long-distance care, boundaries, emotional needs, and partner conversations.",
        "trust_intro": "LoveTypes is an original relationship communication site based on the five love languages. It combines character storytelling, scenario-based reflection, and practical guides to help readers name what helps them feel loved.",
    },
    "ja": {
        "code": "ja",
        "prefix": "ja",
        "name": "日本語",
        "brand": "LoveTypes 感情の守護者",
        "tagline": "愛の言語の結果を、会話・境界線・仲直り・日々の小さな行動へ変えるためのガイド。",
        "start": "儀式を始める",
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
        "boundary_text": "LoveTypes は自己理解と関係コミュニケーションの練習を目的としています。心理療法、医療助言、法律助言、診断ではありません。暴力、支配、トラウマ、緊急の危険がある場合は、信頼できる人や専門機関に相談してください。",
        "home_title": "LoveTypes｜愛の言語診断と関係コミュニケーションガイド",
        "home_desc": "LoveTypes は五つの愛の言語を五人の感情の守護者に置き換え、診断、会話例、仲直り練習、関係ガイドを提供します。",
        "guide_index_title": "LoveTypes ガイド｜愛の言語を現実の関係へ",
        "guide_index_desc": "診断結果、衝突後の修復、遠距離、境界線、感情ニーズ、パートナーとの会話を扱う LoveTypes ガイド。",
        "trust_intro": "LoveTypes は五つの愛の言語を土台にしたオリジナルの関係コミュニケーションサイトです。キャラクター表現、状況型の内省、実用的なガイドを通じて、愛される入口を言葉にします。",
    },
    "ko": {
        "code": "ko",
        "prefix": "ko",
        "name": "한국어",
        "brand": "LoveTypes 감정 수호자",
        "tagline": "사랑의 언어 결과를 실제 대화, 경계, 회복, 관계 습관으로 바꾸는 가이드.",
        "start": "의식 시작하기",
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
        "boundary_text": "LoveTypes는 자기 이해와 관계 대화 연습을 위한 콘텐츠입니다. 심리상담, 의료 조언, 법률 조언, 진단을 제공하지 않습니다. 폭력, 통제, 트라우마, 긴급 위험이 있다면 먼저 신뢰할 수 있는 사람과 전문 기관의 도움을 받으세요.",
        "home_title": "LoveTypes｜사랑의 언어 테스트와 관계 대화 가이드",
        "home_desc": "LoveTypes는 다섯 가지 사랑의 언어를 다섯 감정 수호자로 풀어내며 테스트, 대화 예시, 회복 연습, 관계 가이드를 제공합니다.",
        "guide_index_title": "LoveTypes 가이드｜사랑의 언어를 실제 관계로",
        "guide_index_desc": "테스트 결과, 갈등 회복, 장거리 관계, 경계, 정서적 욕구, 파트너 대화를 다루는 LoveTypes 가이드.",
        "trust_intro": "LoveTypes는 다섯 가지 사랑의 언어를 바탕으로 만든 오리지널 관계 커뮤니케이션 사이트입니다. 캐릭터 서사, 상황형 질문, 실용 가이드를 통해 사랑받는 방식을 말로 정리합니다.",
    },
    "es": {
        "code": "es",
        "prefix": "es",
        "name": "Español",
        "brand": "LoveTypes Guardianas Emocionales",
        "tagline": "Convierte tu resultado de lenguaje del amor en conversaciones, límites, reparación y hábitos reales.",
        "start": "Iniciar ritual",
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
        "boundary_text": "LoveTypes sirve para la autorreflexión y la práctica de comunicación en relaciones. No ofrece terapia, consejo médico, consejo legal ni diagnóstico. Si enfrentas violencia, control, trauma o riesgo urgente, busca primero apoyo profesional y personas de confianza.",
        "home_title": "LoveTypes | Test de lenguajes del amor y guías de relación",
        "home_desc": "LoveTypes transforma los cinco lenguajes del amor en cinco guardianas emocionales con test, guiones, ejercicios de reparación y guías de relación.",
        "guide_index_title": "Guías LoveTypes | Lleva los lenguajes del amor a la vida real",
        "guide_index_desc": "Explora guías sobre resultados, reparación de conflictos, distancia, límites, necesidades emocionales y conversaciones de pareja.",
        "trust_intro": "LoveTypes es un sitio original de comunicación relacional basado en los cinco lenguajes del amor. Combina personajes, reflexión situacional y guías prácticas para nombrar cómo una persona se siente amada.",
    },
}


GUARDIANS = {
    "iris": {
        "asset": "/assets/lovetypes/guardians/iris.webp",
        "prop": "/assets/lovetypes/props/affirmation-feather-pen.webp",
        "zh": ("艾莉絲", "肯定的言詞", "她守護被準確看見的心，提醒你把讚美說具體，把感謝說完整。"),
        "en": ("Iris", "Words of affirmation", "She protects the need to be seen clearly and teaches praise that is specific, honest, and timely."),
        "ja": ("アイリス", "肯定の言葉", "正確に見てもらいたい心を守り、具体的で誠実な言葉を届ける方法を教えます。"),
        "ko": ("아이리스", "인정의 말", "정확히 보이고 싶은 마음을 지키며 구체적이고 진심 어린 말의 힘을 알려 줍니다."),
        "es": ("Iris", "Palabras de afirmación", "Protege la necesidad de ser vista con precisión y enseña palabras concretas, honestas y oportunas."),
    },
    "noah": {
        "asset": "/assets/lovetypes/guardians/noah.webp",
        "prop": "/assets/lovetypes/props/quality-time-lantern.webp",
        "zh": ("諾雅", "優質的時光", "她守護專注陪伴，提醒你把注意力還給眼前的人。"),
        "en": ("Noah", "Quality time", "She protects focused presence and helps you return attention to the person in front of you."),
        "ja": ("ノア", "上質な時間", "集中した存在を守り、目の前の人に注意を戻すことを思い出させます。"),
        "ko": ("노아", "함께하는 시간", "집중된 존재감을 지키며 눈앞의 사람에게 주의를 돌리는 법을 알려 줍니다."),
        "es": ("Noah", "Tiempo de calidad", "Protege la presencia atenta y te ayuda a devolver la atención a la persona que tienes delante."),
    },
    "vivian": {
        "asset": "/assets/lovetypes/guardians/vivian.webp",
        "prop": "/assets/lovetypes/props/gifts-ribboned-gift-box.webp",
        "zh": ("薇薇安", "接受禮物", "她守護被記得的感覺，讓心意不只停在價格，而是停在細節。"),
        "en": ("Vivian", "Receiving gifts", "She protects the feeling of being remembered, where meaning lives in details rather than price."),
        "ja": ("ヴィヴィアン", "贈り物", "覚えていてもらえた感覚を守り、価値は値段ではなく細部に宿ると伝えます。"),
        "ko": ("비비안", "선물 받기", "기억되었다는 감각을 지키며 가격보다 세부적인 마음이 중요하다고 말합니다."),
        "es": ("Vivian", "Recibir regalos", "Protege la sensación de ser recordada, donde el valor está en el detalle y no en el precio."),
    },
    "claire": {
        "asset": "/assets/lovetypes/guardians/claire.webp",
        "prop": "/assets/lovetypes/props/service-tool-pouch.webp",
        "zh": ("克萊兒", "服務的行動", "她守護被分擔的安心，讓承諾落在可看見的行動裡。"),
        "en": ("Claire", "Acts of service", "She protects the relief of being supported and turns care into visible action."),
        "ja": ("クレア", "奉仕の行動", "支えられている安心を守り、思いやりを見える行動へ変えます。"),
        "ko": ("클레어", "봉사의 행동", "함께 짊어져 주는 안도감을 지키며 배려를 보이는 행동으로 바꿉니다."),
        "es": ("Claire", "Actos de servicio", "Protege el alivio de sentirse apoyada y convierte el cuidado en acción visible."),
    },
    "dora": {
        "asset": "/assets/lovetypes/guardians/dora.webp",
        "prop": "/assets/lovetypes/props/touch-golden-hug-glow.webp",
        "zh": ("朵拉", "身體的接觸", "她守護同意之後的靠近，讓身體重新知道自己是安全的。"),
        "en": ("Dora", "Physical touch", "She protects consensual closeness and helps the body remember safety."),
        "ja": ("ドーラ", "身体的なふれあい", "同意のある近さを守り、身体が安全を思い出す手助けをします。"),
        "ko": ("도라", "스킨십", "동의가 있는 가까움을 지키며 몸이 안전함을 다시 느끼게 합니다."),
        "es": ("Dora", "Contacto físico", "Protege la cercanía con consentimiento y ayuda al cuerpo a recordar seguridad."),
    },
}


GUIDES = [
    {
        "slug": "share-your-result",
        "guardian": "iris",
        "zh": ("測驗結果怎麼跟伴侶說", "把 LoveTypes 結果從有趣分享變成真正的關係對話。"),
        "en": ("How to Share Your Result With a Partner", "Turn your LoveTypes result from a fun share into a real relationship conversation."),
        "ja": ("結果をパートナーに伝える方法", "LoveTypes の結果を楽しい共有から本当の対話へ変える。"),
        "ko": ("결과를 파트너에게 말하는 방법", "LoveTypes 결과를 재미있는 공유에서 실제 관계 대화로 바꾸기."),
        "es": ("Cómo compartir tu resultado con tu pareja", "Convierte tu resultado LoveTypes en una conversación real de relación."),
    },
    {
        "slug": "repair-after-conflict",
        "guardian": "noah",
        "zh": ("吵架後的五種愛之語修復法", "用對方聽得懂的方式把道歉、時間、行動與安全感接回來。"),
        "en": ("Repair After Conflict With Five Love Languages", "Reconnect apology, time, action, memory, and safety in a language your partner can receive."),
        "ja": ("衝突後に五つの愛の言語で修復する", "相手が受け取れる形で謝罪、時間、行動、記憶、安全をつなぎ直す。"),
        "ko": ("갈등 후 다섯 가지 사랑의 언어로 회복하기", "상대가 받을 수 있는 방식으로 사과, 시간, 행동, 기억, 안전감을 다시 연결하기."),
        "es": ("Reparar después de un conflicto con cinco lenguajes", "Reconecta disculpa, tiempo, acción, memoria y seguridad en un idioma que la otra persona pueda recibir."),
    },
    {
        "slug": "words-of-affirmation-scripts",
        "guardian": "iris",
        "zh": ("肯定言詞的具體句型", "不空泛稱讚，而是把看見、感謝、承認與承諾說完整。"),
        "en": ("Practical Scripts for Words of Affirmation", "Replace vague compliments with clear seeing, gratitude, acknowledgement, and commitment."),
        "ja": ("肯定の言葉の実用フレーズ", "曖昧な褒め言葉ではなく、見ていること、感謝、承認、約束を伝える。"),
        "ko": ("인정의 말을 위한 실제 문장", "막연한 칭찬 대신 알아봄, 감사, 인정, 약속을 분명히 말하기."),
        "es": ("Frases prácticas para palabras de afirmación", "Cambia elogios vagos por observación, gratitud, reconocimiento y compromiso claros."),
    },
    {
        "slug": "acts-of-service-boundaries",
        "guardian": "claire",
        "zh": ("服務行動與情緒勞動界線", "分辨照顧、分擔、討好與被消耗，讓行動不變成壓迫。"),
        "en": ("Acts of Service and Emotional Labor Boundaries", "Tell care, support, people-pleasing, and exhaustion apart before action becomes pressure."),
        "ja": ("奉仕の行動と感情労働の境界線", "ケア、支援、迎合、消耗を区別し、行動が圧力にならないようにする。"),
        "ko": ("봉사의 행동과 감정 노동의 경계", "돌봄, 분담, 맞춰주기, 소진을 구분해 행동이 압박이 되지 않게 하기."),
        "es": ("Actos de servicio y límites del trabajo emocional", "Distingue cuidado, apoyo, complacencia y agotamiento antes de que la acción se vuelva presión."),
    },
    {
        "slug": "gifts-are-not-materialism",
        "guardian": "vivian",
        "zh": ("禮物型不是物質", "理解禮物背後的被記得、被觀察與被珍惜，而不是價格。"),
        "en": ("Receiving Gifts Is Not Materialism", "Understand the memory, attention, and care behind a gift rather than its price."),
        "ja": ("贈り物タイプは物質主義ではない", "値段ではなく、覚えていたこと、観察、思いやりを理解する。"),
        "ko": ("선물형은 물질주의가 아니다", "가격보다 기억, 관찰, 소중히 여김이 선물 뒤에 있다는 것을 이해하기."),
        "es": ("Recibir regalos no es materialismo", "Entiende la memoria, atención y cuidado detrás del regalo, no solo su precio."),
    },
    {
        "slug": "quality-time-long-distance",
        "guardian": "noah",
        "zh": ("優質時光與遠距關係", "遠距不是只能等待見面，也能設計有品質的日常連結。"),
        "en": ("Quality Time in Long-Distance Relationships", "Distance is not only waiting to meet; it can include designed moments of real presence."),
        "ja": ("遠距離関係の上質な時間", "会える日を待つだけでなく、日常に質のあるつながりを設計する。"),
        "ko": ("장거리 관계에서 함께하는 시간", "만남을 기다리기만 하는 대신 일상 속 집중된 연결을 설계하기."),
        "es": ("Tiempo de calidad en relaciones a distancia", "La distancia no es solo esperar verse; también puede diseñar presencia cotidiana."),
    },
    {
        "slug": "physical-touch-consent-safety",
        "guardian": "dora",
        "zh": ("身體接觸、同意與安全感", "親密不是理所當然，真正安定的靠近需要清楚同意。"),
        "en": ("Physical Touch, Consent, and Safety", "Closeness is not automatic; soothing touch requires clear consent and emotional safety."),
        "ja": ("身体的なふれあい、同意、安全感", "親密さは当然ではなく、安心できる接触には明確な同意が必要です。"),
        "ko": ("스킨십, 동의, 안전감", "가까움은 당연한 것이 아니며 안정되는 접촉에는 분명한 동의가 필요합니다."),
        "es": ("Contacto físico, consentimiento y seguridad", "La cercanía no es automática; el contacto que calma necesita consentimiento claro."),
    },
    {
        "slug": "weekly-relationship-review",
        "guardian": "claire",
        "zh": ("每週關係回顧問題", "用十五分鐘整理本週被愛時刻、錯頻片刻與下一步小約定。"),
        "en": ("Weekly Relationship Review Questions", "Use fifteen minutes to notice moments of love, misalignment, and one small next agreement."),
        "ja": ("週一回の関係ふり返り質問", "十五分で愛された瞬間、すれ違い、小さな次の約束を整理する。"),
        "ko": ("매주 관계 점검 질문", "15분 동안 사랑받은 순간, 어긋난 순간, 다음 작은 약속을 정리하기."),
        "es": ("Preguntas semanales para revisar la relación", "Usa quince minutos para notar amor, desajustes y un pequeño acuerdo siguiente."),
    },
    {
        "slug": "emotional-needs-checklist",
        "guardian": "vivian",
        "zh": ("情感需求自我檢查表", "把模糊的不舒服拆成可說出口的需要、界線與請求。"),
        "en": ("Emotional Needs Self-Checklist", "Turn vague discomfort into needs, boundaries, and requests you can actually name."),
        "ja": ("感情ニーズのセルフチェック", "曖昧なつらさを、言葉にできるニーズ、境界線、お願いへ分ける。"),
        "ko": ("정서적 욕구 자기 체크리스트", "막연한 불편함을 말할 수 있는 욕구, 경계, 요청으로 나누기."),
        "es": ("Lista de revisión de necesidades emocionales", "Convierte una incomodidad vaga en necesidades, límites y peticiones concretas."),
    },
    {
        "slug": "misfrequency-examples",
        "guardian": "iris",
        "zh": ("五種愛之語錯頻案例", "看懂你明明在付出，對方卻沒有收到的常見原因。"),
        "en": ("Love-Language Misfrequency Examples", "See why sincere effort may still miss the way another person receives love."),
        "ja": ("愛の言語のすれ違い例", "本気で尽くしていても、相手に届かない理由を理解する。"),
        "ko": ("사랑의 언어 어긋남 사례", "진심으로 노력해도 상대가 사랑으로 받지 못하는 이유 이해하기."),
        "es": ("Ejemplos de desajuste en lenguajes del amor", "Entiende por qué un esfuerzo sincero puede no sentirse como amor para la otra persona."),
    },
    {
        "slug": "relationship-stages",
        "guardian": "noah",
        "zh": ("單身、曖昧、交往、遠距如何使用結果", "不同關係階段，需要不同的解讀方式與行動尺度。"),
        "en": ("Using Your Result Across Relationship Stages", "Single, dating, committed, and long-distance seasons need different next steps."),
        "ja": ("関係段階ごとの結果の使い方", "独身、曖昧、交際中、遠距離では次の行動が変わります。"),
        "ko": ("관계 단계별 결과 활용법", "싱글, 썸, 연애, 장거리 단계마다 다른 다음 행동이 필요합니다."),
        "es": ("Usar tu resultado en distintas etapas de relación", "Soltería, citas, compromiso y distancia necesitan pasos diferentes."),
    },
    {
        "slug": "healthy-boundaries",
        "guardian": "dora",
        "zh": ("健康界線與關係安全", "愛之語不能取代尊重、同意、責任分擔與安全界線。"),
        "en": ("Healthy Boundaries and Relationship Safety", "Love languages cannot replace respect, consent, shared responsibility, and safety."),
        "ja": ("健康な境界線と関係の安全", "愛の言語は尊重、同意、責任、安全の代わりにはなりません。"),
        "ko": ("건강한 경계와 관계 안전", "사랑의 언어는 존중, 동의, 책임 분담, 안전을 대신할 수 없습니다."),
        "es": ("Límites saludables y seguridad relacional", "Los lenguajes del amor no reemplazan respeto, consentimiento, responsabilidad y seguridad."),
    },
]


LEGACY_ZH_GUIDES = [
    ("before-sharing-result", "分享結果前，先把期待說清楚", "把測驗結果分享給伴侶或朋友前，先整理你真正想被理解的地方。", "share-your-result"),
    ("claire-acts-of-service", "克萊兒：服務行動與分擔的安心", "從克萊兒的守護者視角理解行動、承諾與情緒勞動界線。", "acts-of-service-boundaries"),
    ("conflict-repair-worksheet", "衝突修復工作表", "用五個步驟整理受傷片刻、修復語言與下一次衝突的安全約定。", "repair-after-conflict"),
    ("dialogue-scripts", "愛之語對話句型集", "用可以直接開口的句型，把測驗結果變成不指責的請求。", "words-of-affirmation-scripts"),
    ("dora-physical-touch", "朵拉：身體接觸與安全靠近", "從朵拉的守護者視角理解親密、同意、身體安定與界線。", "physical-touch-consent-safety"),
    ("guardian-pairings", "守護者配對與錯頻地圖", "看懂不同愛之語相遇時，哪些地方最容易互相誤解。", "misfrequency-examples"),
    ("heart-garden", "心語庭園：整理你的情感入口", "把被愛入口、情感傷口與可練習行動放回一張清楚地圖。", "emotional-needs-checklist"),
    ("iris-words-of-affirmation", "艾莉絲：肯定言詞不是甜言蜜語", "從艾莉絲的守護者視角理解具體肯定、感謝與被看見。", "words-of-affirmation-scripts"),
    ("love-language-examples", "五種愛之語生活例子", "用日常情境理解肯定、陪伴、禮物、行動與身體接觸如何被接收。", "misfrequency-examples"),
    ("misfrequency", "愛之語錯頻：為什麼你付出很多卻沒被收到", "整理常見錯頻案例，讓善意變成對方真的能接收的形式。", "misfrequency-examples"),
    ("noah-quality-time", "諾雅：優質時光與專注陪伴", "從諾雅的守護者視角理解專心、同在與遠距連結。", "quality-time-long-distance"),
    ("relationship-review-questions", "伴侶每週關係回顧問題", "用十五分鐘回顧被愛時刻、錯頻片刻、修復需求與下週小約定。", "weekly-relationship-review"),
    ("use-your-result", "測驗結果怎麼真正用在關係裡", "把守護者結果從有趣標籤，變成能說出口的需求與行動。", "share-your-result"),
    ("vivian-receiving-gifts", "薇薇安：禮物不是物質，而是被記得", "從薇薇安的守護者視角理解心意、細節與被珍惜的感覺。", "gifts-are-not-materialism"),
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
        "why": "這個主題之所以重要，是因為很多關係問題不是沒有愛，而是愛沒有用對方能接收的形式抵達。LoveTypes 把抽象的愛之語整理成五位守護者，目的不是替人貼標籤，而是幫你找到更精準的表達方式。",
        "notice": "開始之前，先把「我希望對方懂我」拆成三句話：我現在最缺的是什麼？我最害怕被誤解的地方是什麼？如果對方只能做一個小行動，哪一個行動最能讓我安心？",
        "scripts": ["我不是要你猜我的心，我想練習把需要說清楚。", "如果你願意，我希望我們先從一個小改變開始。", "我需要的不是完美回應，而是知道你有把這件事放在心上。"],
        "practice": "今天只選一個具體情境，不要一次翻出所有舊帳。寫下觸發事件、自己的感覺、背後的愛之語需求，以及一個對方能在二十四小時內做到的小請求。",
        "mistakes": "不要把測驗結果當作命令，也不要用「我就是這一型」停止溝通。類型只是入口，真正重要的是你們能不能把需求翻成彼此都願意承擔的小行動。",
        "reflection": ["我最容易用哪一種方式付出，卻忽略對方真正接收的語言？", "如果我把需求說得更具體，會不會少一點委屈與猜測？", "這個練習需要對方配合到什麼程度，才算合理而不是壓迫？"],
    },
    "en": {
        "why": "This topic matters because many relationship problems are not a lack of love. The love simply arrives in a form the other person cannot easily receive. LoveTypes uses guardians not to label people, but to make needs easier to name and discuss.",
        "notice": "Before starting, split the wish to be understood into three sentences: what do I need most right now, where do I fear being misunderstood, and what one small action would help me feel safer?",
        "scripts": ["I do not want you to guess my heart; I want to practice naming my need clearly.", "If you are willing, I would like us to begin with one small change.", "I do not need a perfect response. I need to know this matters to you."],
        "practice": "Choose one concrete situation today. Write the trigger, the feeling, the love-language need underneath it, and one request the other person could realistically do within twenty-four hours.",
        "mistakes": "Do not use a quiz result as a command, and do not say 'this is just my type' to stop the conversation. Type language is only a doorway; the real work is translating needs into shared action.",
        "reflection": ["Which love language do I naturally give while missing what the other person receives?", "Would more specific requests reduce resentment and guessing?", "How much cooperation is reasonable before the request becomes pressure?"],
    },
    "ja": {
        "why": "このテーマが大切なのは、関係の問題の多くが愛の不足ではなく、相手が受け取りにくい形で愛が届いていることから起こるからです。LoveTypes の守護者は人を分類するためではなく、ニーズを言葉にしやすくするための入口です。",
        "notice": "始める前に「わかってほしい」を三つに分けます。今いちばん足りないものは何か。どこを誤解されるのが怖いか。相手が一つだけ行動するなら、何が安心につながるか。",
        "scripts": ["心を当ててほしいのではなく、必要なことを言葉にする練習をしたい。", "よければ、まず一つだけ小さな変化から始めたい。", "完璧な返事ではなく、このことを大切に扱っていると知りたい。"],
        "practice": "今日は一つの具体的な場面だけを選びます。きっかけ、感情、その下にある愛の言語のニーズ、そして二十四時間以内にできる小さなお願いを書いてください。",
        "mistakes": "診断結果を命令として使わないでください。「私はこのタイプだから」で会話を止めることも避けます。タイプは入口であり、本当に大切なのはニーズを共同の行動へ翻訳することです。",
        "reflection": ["私はどの愛の言語で与えがちで、相手が受け取る言語を見逃しているか。", "お願いを具体的にすれば、我慢や推測は減るか。", "このお願いはどこまでなら協力で、どこからが圧力になるか。"],
    },
    "ko": {
        "why": "이 주제가 중요한 이유는 많은 관계 문제가 사랑이 없어서가 아니라 사랑이 상대가 받기 어려운 형태로 도착하기 때문입니다. LoveTypes의 수호자는 사람을 낙인찍기 위한 것이 아니라 욕구를 더 쉽게 말하기 위한 입구입니다.",
        "notice": "시작하기 전에 '나를 이해해 줬으면 좋겠다'를 세 문장으로 나누세요. 지금 가장 필요한 것은 무엇인가, 어떤 부분이 오해될까 두려운가, 상대가 하나만 한다면 어떤 행동이 가장 안심되는가.",
        "scripts": ["내 마음을 맞혀 달라는 것이 아니라 필요한 것을 분명히 말하는 연습을 하고 싶어.", "괜찮다면 작은 변화 하나부터 시작하고 싶어.", "완벽한 답보다 이 일을 마음에 두고 있다는 것을 알고 싶어."],
        "practice": "오늘은 구체적인 상황 하나만 고르세요. 계기, 감정, 그 아래의 사랑의 언어 욕구, 그리고 24시간 안에 현실적으로 할 수 있는 작은 요청을 적습니다.",
        "mistakes": "테스트 결과를 명령처럼 쓰지 마세요. '나는 원래 이 타입이야'라고 말하며 대화를 멈추는 것도 피해야 합니다. 유형은 입구일 뿐, 중요한 것은 욕구를 함께할 수 있는 행동으로 번역하는 것입니다.",
        "reflection": ["나는 어떤 사랑의 언어로 주로 표현하면서 상대가 받는 언어를 놓치고 있을까?", "요청을 더 구체적으로 말하면 서운함과 추측이 줄어들까?", "이 요청은 어디까지가 협력이고 어디부터가 압박일까?"],
    },
    "es": {
        "why": "Este tema importa porque muchos problemas de relación no nacen de la falta de amor, sino de un amor que llega en una forma difícil de recibir. LoveTypes usa guardianas no para etiquetar, sino para hacer las necesidades más conversables.",
        "notice": "Antes de empezar, divide el deseo de ser entendida en tres frases: qué necesito ahora, dónde temo ser malinterpretada y qué pequeña acción me ayudaría a sentir más seguridad.",
        "scripts": ["No quiero que adivines mi corazón; quiero practicar nombrar mi necesidad con claridad.", "Si estás dispuesto/a, me gustaría empezar con un cambio pequeño.", "No necesito una respuesta perfecta. Necesito saber que esto te importa."],
        "practice": "Elige hoy una situación concreta. Escribe el detonante, la emoción, la necesidad de lenguaje del amor que hay debajo y una petición realista para las próximas veinticuatro horas.",
        "mistakes": "No uses el resultado como una orden ni como una excusa para cerrar la conversación. El tipo es una puerta de entrada; el trabajo real es traducir necesidades en acciones compartidas.",
        "reflection": ["Qué lenguaje suelo ofrecer mientras pierdo de vista el que la otra persona recibe?", "Si hago peticiones más concretas, disminuirán el resentimiento y las suposiciones?", "Hasta dónde esta petición es cooperación y desde dónde se vuelve presión?"],
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
        "guardian_use": "{name} 是一個象徵入口，不是固定身份。你可以用這位守護者說明什麼讓你感到安全、什麼讓你覺得沒有被接住，以及哪一個小行動能讓關心更容易被你收到。",
        "editorial": "每一個 LoveTypes 頁面都先從一個實際關係問題出發，再連回五種愛之語框架、守護者隱喻，以及讀者不需要註冊帳號也能嘗試的小練習。我們維持反思式語氣，而不是診斷式語氣；當頁面太薄、太重複，或太偏向導流而不是讀者價值時，就會重新整理。",
        "disclosure": "LoveTypes 可能在相關頁面揭露流量分析、聯盟連結或廣告資訊。目前這個審核優先版本先停用廣告腳本，但保留清楚的網站所有權、聯絡、sitemap 與政策資訊，方便讀者與搜尋/廣告審核系統確認。",
        "contact": "若要回報內容修正、隱私問題、合作疑慮或壞頁面，請寄到 <a href=\"mailto:s755102@gmail.com\">s755102@gmail.com</a> 或使用聯絡頁。有效回報最好附上頁面網址、裝置、瀏覽器，以及你認為需要改善的句子或段落。",
    },
    "en": {
        "guardian_use": "{name} is a symbolic entry point, not a fixed identity. Use this guardian to describe what helps you feel safe, what makes you feel missed, and what small action would make care easier to receive.",
        "editorial": "Every LoveTypes page begins with a practical relationship question, then connects that question to the five love-language framework, the guardian metaphor, and a small exercise a reader can try without needing an account. We keep the tone reflective rather than diagnostic, and we update pages when a section is too thin, repetitive, or focused on promotion instead of reader value.",
        "disclosure": "LoveTypes may disclose measurement, affiliate links, or advertising information when those services are active. In this review-focused version, advertising scripts are disabled while clear ownership, contact, sitemap, and policy information remain available to readers and crawlers.",
        "contact": "For content corrections, privacy questions, partnership concerns, or broken-page reports, contact <a href=\"mailto:s755102@gmail.com\">s755102@gmail.com</a> or use the contact page. Helpful reports include the page URL, device, browser, and the sentence or section you believe should be improved.",
    },
    "ja": {
        "guardian_use": "{name} は固定された身分ではなく、気持ちを言葉にするための象徴的な入口です。この守護者を使って、何が安心につながるのか、何が受け止められていない感覚を生むのか、どんな小さな行動なら思いやりを受け取りやすいのかを説明できます。",
        "editorial": "LoveTypes の各ページは、実際の関係で起こる問いから始まり、五つの愛の言語、守護者の比喩、そして登録なしで試せる小さな練習へつなげます。診断ではなく内省の語り口を保ち、内容が薄い、重複している、読者価値より誘導が強いと判断したページは更新します。",
        "disclosure": "LoveTypes では、利用している場合にアクセス解析、アフィリエイトリンク、広告に関する情報を開示します。現在の審査重視版では広告スクリプトを停止しつつ、所有者情報、連絡先、サイトマップ、ポリシー情報を読者とクローラーが確認できるようにしています。",
        "contact": "内容修正、プライバシー、提携、ページ不具合に関する連絡は <a href=\"mailto:s755102@gmail.com\">s755102@gmail.com</a> または連絡ページからお願いします。ページ URL、端末、ブラウザ、改善が必要だと思う文や段落があると確認しやすくなります。",
    },
    "ko": {
        "guardian_use": "{name}는 고정된 정체성이 아니라 마음을 설명하기 위한 상징적 입구입니다. 이 수호자를 통해 무엇이 나를 안전하게 하는지, 어떤 상황에서 놓친 느낌이 드는지, 어떤 작은 행동이 배려를 더 쉽게 받게 하는지 말할 수 있습니다.",
        "editorial": "LoveTypes의 각 페이지는 실제 관계 질문에서 시작해 다섯 가지 사랑의 언어, 수호자 은유, 계정 없이도 시도할 수 있는 작은 연습으로 이어집니다. 진단이 아니라 성찰의 어조를 유지하며, 내용이 얇거나 반복적이거나 독자 가치보다 홍보가 강한 페이지는 다시 정리합니다.",
        "disclosure": "LoveTypes는 사용 중인 경우 분석, 제휴 링크, 광고 관련 정보를 고지합니다. 현재 심사 중심 버전에서는 광고 스크립트를 비활성화하고, 소유권, 연락처, 사이트맵, 정책 정보를 독자와 크롤러가 확인할 수 있게 유지합니다.",
        "contact": "콘텐츠 수정, 개인정보, 협업 문의, 깨진 페이지 신고는 <a href=\"mailto:s755102@gmail.com\">s755102@gmail.com</a> 또는 연락 페이지로 보내 주세요. 페이지 URL, 기기, 브라우저, 개선이 필요한 문장이나 단락을 함께 보내면 확인이 빠릅니다.",
    },
    "es": {
        "guardian_use": "{name} es una entrada simbólica, no una identidad fija. Puedes usar esta guardiana para explicar qué te ayuda a sentir seguridad, qué te hace sentir no recibida y qué pequeña acción vuelve el cuidado más fácil de aceptar.",
        "editorial": "Cada página de LoveTypes empieza con una pregunta práctica de relación y la conecta con el marco de los cinco lenguajes del amor, la metáfora de las guardianas y un ejercicio pequeño que la persona puede probar sin crear una cuenta. Mantenemos un tono reflexivo, no diagnóstico, y actualizamos páginas cuando son demasiado delgadas, repetitivas o centradas en promoción.",
        "disclosure": "LoveTypes puede divulgar información sobre medición, enlaces afiliados o publicidad cuando esos servicios estén activos. En esta versión enfocada en revisión, los scripts publicitarios están desactivados mientras la propiedad, contacto, sitemap y políticas siguen disponibles para lectores y rastreadores.",
        "contact": "Para correcciones de contenido, privacidad, colaboraciones o páginas rotas, escribe a <a href=\"mailto:s755102@gmail.com\">s755102@gmail.com</a> o usa la página de contacto. Un reporte útil incluye URL, dispositivo, navegador y la frase o sección que debería mejorar.",
    },
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


def nav(lang: str, active: str = "") -> str:
    t = LANGS[lang]
    items = [
        (lang_url(lang), t["brand"].split()[0]),
        (lang_url(lang, "guides"), t["guides"]),
        (lang_url(lang, "characters/iris"), t["guardians"]),
        (lang_url(lang, "theory"), t["theory"]),
        (lang_url(lang, "resources"), t["resources"]),
        (lang_url(lang, "about"), t["about"]),
    ]
    links = "".join(f'<a class="{"active" if active == label else ""}" href="{href}">{escape(label)}</a>' for href, label in items)
    lang_links = "".join(f'<a href="{lang_url(code)}" lang="{cfg["code"]}">{cfg["name"]}</a>' for code, cfg in LANGS.items())
    return f"""
<header class="site-nav">
  <a class="brand" href="{lang_url(lang)}" aria-label="{escape(t["brand"])}"><span>LoveTypes</span></a>
  <nav class="nav-links" aria-label="Primary navigation">{links}</nav>
  <div class="language-switcher">{lang_links}</div>
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


def head(lang: str, title: str, desc: str, path: str = "", page_type: str = "website", image: str = "/og-cover.jpg") -> str:
    canonical = abs_url(lang, path)
    alternates = "\n".join(f'  <link rel="alternate" hreflang="{cfg["code"]}" href="{abs_url(code, path)}" />' for code, cfg in LANGS.items())
    alternates += f'\n  <link rel="alternate" hreflang="x-default" href="{abs_url("zh", path)}" />'
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
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@500;700&family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/shared.css?v=20260603-multilingual" />
</head>
"""


def layout(lang: str, title: str, desc: str, path: str, body: str, active: str = "", page_type: str = "website", image: str = "/og-cover.jpg", schema: str = "") -> str:
    return head(lang, title, desc, path, page_type, image) + f"""<body>
<a class="skip-link" href="#main">Skip to content</a>
{nav(lang, active)}
{schema}
<main id="main">
{body}
</main>
{footer(lang)}
</body>
</html>
"""


def write(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


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


def character_card(lang: str, slug: str, data: dict) -> str:
    name, typ, desc = data[lang]
    return f"""
<a class="guardian-card" href="{lang_url(lang, "characters/" + slug)}">
  <img src="{data["asset"]}" alt="{escape(name)}" loading="lazy" />
  <div><span>{escape(typ)}</span><h3>{escape(name)}</h3><p>{escape(desc)}</p></div>
</a>
"""


def home(lang: str) -> None:
    t = LANGS[lang]
    guide_cards = "".join(guide_card(lang, g) for g in GUIDES[:6])
    guardian_cards = "".join(character_card(lang, slug, data) for slug, data in GUARDIANS.items())
    body = f"""
<section class="hero">
  <div class="hero-copy">
    <p class="eyebrow">LOVE LANGUAGE PRACTICE LIBRARY</p>
    <h1>{escape(t["brand"])}</h1>
    <p class="lead">{escape(t["tagline"])}</p>
    <div class="hero-actions"><a class="primary-btn" href="{lang_url(lang, "guides")}">{escape(t["guides"])}</a><a class="secondary-btn" href="#quiz-section">{escape(t["start"])}</a></div>
  </div>
  <picture><source media="(max-width: 720px)" srcset="/assets/lovetypes/backgrounds/guardian-garden-mobile.webp" /><img src="/assets/lovetypes/backgrounds/guardian-garden.webp" alt="LoveTypes guardian garden" /></picture>
</section>
<section class="section intro-grid">
  <div><p class="eyebrow">EDITORIAL PROMISE</p><h2>{escape(t["trust_intro"])}</h2></div>
  <div class="text-stack"><p>{escape(PRACTICAL_COPY[lang]["why"])}</p><p>{escape(PRACTICAL_COPY[lang]["notice"])}</p></div>
</section>
<section class="section" id="guides-section"><div class="section-head"><p class="eyebrow">PRACTICAL GUIDES</p><h2>{escape(t["guide_index_title"])}</h2><a href="{lang_url(lang, "guides")}">{escape(t["learn_more"])}</a></div><div class="card-grid">{guide_cards}</div></section>
<section class="section" id="types-section"><div class="section-head"><p class="eyebrow">FIVE GUARDIANS</p><h2>{escape(t["guardians"])}</h2></div><div class="guardian-grid">{guardian_cards}</div></section>
<section class="quiz-band" id="quiz-section">
  <div><p class="eyebrow">SELF-REFLECTION RITUAL</p><h2>{escape(t["start"])}</h2><p>{escape(t["tagline"])}</p></div>
  <div class="quiz-preview">
    <h3>{escape(GUIDES[0][lang][0])}</h3>
    <p>{escape(PRACTICAL_COPY[lang]["practice"])}</p>
    <a class="primary-btn" href="{lang_url(lang, "guides/share-your-result")}">{escape(t["read"])}</a>
  </div>
</section>
"""
    schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"{escape(t["brand"])}","url":"{DOMAIN}{lang_url(lang).rstrip("/")}/","inLanguage":"{t["code"]}"}}</script>'
    write(page_path(lang), layout(lang, t["home_title"], t["home_desc"], "", body, "", "website", "/og-cover.jpg", schema))


def guides_index(lang: str) -> None:
    t = LANGS[lang]
    cards = "".join(guide_card(lang, g) for g in GUIDES)
    body = f"""
<section class="page-hero compact"><p class="eyebrow">LOVE LANGUAGE FIELD GUIDE</p><h1>{escape(t["guide_index_title"])}</h1><p>{escape(t["guide_index_desc"])}</p></section>
<section class="section"><div class="card-grid wide">{cards}</div></section>
<section class="section note-section"><h2>{escape(t["boundary"])}</h2><p>{escape(t["boundary_text"])}</p></section>
"""
    write(page_path(lang, "guides"), layout(lang, t["guide_index_title"], t["guide_index_desc"], "guides", body, t["guides"]))


def guide_page(lang: str, guide: dict, index: int) -> None:
    t = LANGS[lang]
    labels = TOPIC_DETAILS[lang]
    copy = PRACTICAL_COPY[lang]
    title, desc = guide[lang]
    guardian = GUARDIANS[guide["guardian"]][lang]
    related = [g for g in GUIDES if g["slug"] != guide["slug"]]
    next_a = related[(index + 1) % len(related)]
    next_b = related[(index + 4) % len(related)]
    scripts = "".join(f"<li>{escape(item)}</li>" for item in copy["scripts"])
    reflections = "".join(f"<li>{escape(item)}</li>" for item in copy["reflection"])
    body = f"""
<section class="article-hero">
  <div><p class="eyebrow">{escape(guardian[1])}</p><h1>{escape(title)}</h1><p>{escape(desc)}</p></div>
  <img src="{GUARDIANS[guide["guardian"]]["prop"]}" alt="{escape(guardian[1])}" />
</section>
<section class="article-shell">
  <article class="article-body">
    <p class="lede">{escape(desc)} {escape(copy["why"])}</p>
    <h2>{escape(labels["why"])}</h2><p>{escape(copy["why"])}</p>
    <h2>{escape(labels["notice"])}</h2><p>{escape(copy["notice"])}</p>
    <h2>{escape(labels["scripts"])}</h2><ul>{scripts}</ul>
    <h2>{escape(labels["practice"])}</h2><p>{escape(copy["practice"])}</p>
    <div class="callout"><strong>{escape(t["practice"])}</strong><p>{escape(guardian[2])}</p></div>
    <h2>{escape(labels["mistakes"])}</h2><p>{escape(copy["mistakes"])}</p>
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
    write(page_path(lang, "guides/" + guide["slug"]), layout(lang, title, desc, "guides/" + guide["slug"], body, t["guides"], "article", "/assets/lovetypes/share/guide-toolkit-og.jpg", schema))


def legacy_zh_guide_page(slug: str, title: str, desc: str, canonical_target: str) -> None:
    lang = "zh"
    t = LANGS[lang]
    copy = PRACTICAL_COPY[lang]
    related = next(g for g in GUIDES if g["slug"] == canonical_target)
    body = f"""
<section class="article-hero">
  <div><p class="eyebrow">LOVETYPES ARCHIVE GUIDE</p><h1>{escape(title)}</h1><p>{escape(desc)}</p></div>
  <img src="/assets/lovetypes/share/guide-toolkit-og.jpg" alt="LoveTypes guide" />
</section>
<section class="article-shell">
  <article class="article-body">
    <p class="lede">{escape(desc)} 這一頁保留原有主題，同時改寫成更完整、可閱讀、可練習的指南內容。</p>
    <h2>先把結果翻成真實需求</h2>
    <p>{escape(copy["notice"])}</p>
    <h2>把理解變成可以做的小行動</h2>
    <p>{escape(copy["practice"])}</p>
    <h2>可以直接開口的句型</h2>
    <ul>{"".join(f"<li>{escape(item)}</li>" for item in copy["scripts"])}</ul>
    <h2>不要讓類型取代溝通</h2>
    <p>{escape(copy["mistakes"])}</p>
    <div class="callout safety"><strong>{escape(t["boundary"])}</strong><p>{escape(t["boundary_text"])}</p></div>
  </article>
  <aside class="article-side"><h2>延伸閱讀</h2>{guide_card(lang, related)}</aside>
</section>
"""
    write(page_path(lang, "guides/" + slug), layout(lang, title, desc, "guides/" + slug, body, t["guides"], "article", "/assets/lovetypes/share/guide-toolkit-og.jpg"))


def character_page(lang: str, slug: str, data: dict) -> None:
    t = LANGS[lang]
    labels = PAGE_SECTIONS[lang]
    copy = PRACTICAL_COPY[lang]
    name, typ, desc = data[lang]
    related_guides = [g for g in GUIDES if g["guardian"] == slug][:3]
    related_html = "".join(guide_card(lang, g) for g in related_guides)
    scripts = "".join(f"<li>{escape(item)}</li>" for item in copy["scripts"])
    reflections = "".join(f"<li>{escape(item)}</li>" for item in copy["reflection"])
    body = f"""
<section class="guardian-hero">
  <div><p class="eyebrow">{escape(typ)}</p><h1>{escape(name)}</h1><p>{escape(desc)}</p><a class="primary-btn" href="{lang_url(lang, "guides")}">{escape(t["guides"])}</a></div>
  <img src="{data["asset"]}" alt="{escape(name)}" />
</section>
<section class="section intro-grid">
  <div><h2>{escape(labels["how"])}</h2><p>{escape(copy["why"])}</p><p>{escape(desc)}</p></div>
  <div class="text-stack"><h2>{escape(labels["need"])}</h2><p>{escape(copy["notice"])}</p><p>{escape(copy["practice"])}</p></div>
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
<section class="section"><div class="section-head"><p class="eyebrow">RELATED GUIDES</p><h2>{escape(t["read"])}</h2></div><div class="card-grid">{related_html}</div></section>
"""
    write(page_path(lang, "characters/" + slug), layout(lang, f"{name} | {typ} | LoveTypes", desc, "characters/" + slug, body, t["guardians"], "profile", data["asset"]))


def simple_page(lang: str, slug: str) -> None:
    t = LANGS[lang]
    labels = PAGE_SECTIONS[lang]
    copy = PRACTICAL_COPY[lang]
    titles = {
        "theory": (t["theory"], t["tagline"]),
        "resources": (t["resources"], t["guide_index_desc"]),
        "about": (t["about"], t["trust_intro"]),
        "contact": (t["contact"], "s755102@gmail.com"),
        "privacy": (t["privacy"], f"LoveTypes privacy policy. Updated {UPDATED}."),
        "terms": (t["terms"], f"LoveTypes terms of use. Updated {UPDATED}."),
        "luna-yoga-music": ("Luna Yoga Music", "A calm companion resource for reflection, journaling, and relationship decompression."),
    }
    title, desc = titles[slug]
    extra = ""
    if slug == "contact":
        extra = '<p class="contact-line"><a href="mailto:s755102@gmail.com">s755102@gmail.com</a></p>'
    if slug in {"privacy", "terms"}:
        extra = f"<p><strong>Updated:</strong> {UPDATED}</p>"
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
    write(page_path(lang, slug), layout(lang, f"{title} | LoveTypes", desc, slug, body, title))


def write_css() -> None:
    css = """
:root{--rose:#bd5260;--ink:#302425;--muted:#766160;--cream:#fff8f2;--paper:#fffdf9;--line:#ecd8d5;--sage:#6b7f6a;--gold:#b78b45;--lilac:#7666a8;--shadow:0 18px 54px rgba(76,42,43,.11);--serif:'Noto Serif TC',serif;--sans:'Noto Sans TC',system-ui,sans-serif}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--cream);color:var(--ink);font-family:var(--sans);line-height:1.75}a{color:inherit}.skip-link{position:absolute;left:-999px;top:8px;background:var(--ink);color:#fff;padding:8px 12px;border-radius:8px;z-index:999}.skip-link:focus{left:8px}.site-nav{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:20px;padding:14px 28px;background:rgba(255,248,242,.95);backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}.brand{text-decoration:none;font-weight:900;color:var(--rose);font-family:var(--serif);font-size:1.25rem}.nav-links{display:flex;gap:18px;flex:1}.nav-links a,.language-switcher a{text-decoration:none;color:var(--muted);font-weight:700;font-size:.9rem}.nav-links a.active,.nav-links a:hover,.language-switcher a:hover{color:var(--rose)}.language-switcher{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end}.hero{min-height:calc(100vh - 64px);display:grid;grid-template-columns:minmax(0,1fr) minmax(320px,46vw);gap:30px;align-items:center;padding:64px min(7vw,92px) 52px;background:linear-gradient(120deg,#fffaf6 0%,#fdf0ef 54%,#edf4ec 100%)}.hero picture,.hero img{width:100%;height:100%;min-height:420px;object-fit:cover;border-radius:8px;box-shadow:var(--shadow)}.hero-copy{max-width:760px}.eyebrow{margin:0 0 10px;color:var(--sage);font-size:.78rem;font-weight:900;letter-spacing:.12em;text-transform:uppercase}.hero h1,.page-hero h1,.article-hero h1,.guardian-hero h1{font-family:var(--serif);font-size:clamp(2.2rem,5vw,5rem);line-height:1.04;margin:0 0 18px;color:var(--ink);letter-spacing:0}.lead,.hero p,.page-hero p,.article-hero p,.guardian-hero p{font-size:clamp(1.02rem,1.4vw,1.26rem);color:var(--muted);max-width:760px}.hero-actions{display:flex;gap:14px;flex-wrap:wrap;margin-top:28px}.primary-btn,.secondary-btn{display:inline-flex;align-items:center;justify-content:center;min-height:46px;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:900}.primary-btn{background:var(--rose);color:#fff}.secondary-btn{border:1px solid var(--rose);color:var(--rose);background:#fff}.section{padding:64px min(7vw,92px)}.section-head{display:flex;align-items:end;justify-content:space-between;gap:20px;margin-bottom:22px}.section-head h2,.intro-grid h2,.quiz-band h2,.article-body h2,.article-side h2{font-family:var(--serif);font-size:clamp(1.55rem,2.6vw,2.6rem);line-height:1.15;margin:0 0 12px}.intro-grid{display:grid;grid-template-columns:minmax(260px,42%) 1fr;gap:40px}.text-stack p,.article-body p,.article-body li{font-size:1.03rem;color:var(--muted)}.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}.card-grid.wide{grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}.content-card,.guardian-card,.article-side .content-card,.footer-grid a{display:block;background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:22px;text-decoration:none;box-shadow:0 10px 30px rgba(76,42,43,.06)}.content-card h3,.guardian-card h3{font-family:var(--serif);margin:6px 0 10px;font-size:1.25rem}.content-card p,.guardian-card p,.footer-grid span{color:var(--muted)}.card-link{color:var(--rose);font-weight:900}.guardian-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px}.guardian-card img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:6px;margin-bottom:14px}.guardian-card span{color:var(--gold);font-weight:900}.quiz-band{margin:36px min(7vw,92px) 72px;padding:38px;display:grid;grid-template-columns:1fr minmax(260px,420px);gap:28px;background:#2f2527;color:#fff;border-radius:8px}.quiz-band p{color:#f4dfdc}.quiz-preview{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);border-radius:8px;padding:22px}.page-hero,.article-hero,.guardian-hero{padding:72px min(7vw,92px);background:linear-gradient(120deg,#fffaf6,#f7e8e6)}.page-hero.compact{min-height:300px}.article-hero,.guardian-hero{display:grid;grid-template-columns:1fr minmax(180px,340px);gap:36px;align-items:center}.article-hero img,.guardian-hero img{width:100%;border-radius:8px;box-shadow:var(--shadow)}.article-shell{display:grid;grid-template-columns:minmax(0,760px) minmax(260px,340px);gap:34px;align-items:start;padding:56px min(7vw,92px)}.article-body{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:clamp(24px,4vw,44px)}.article-body.standalone{max-width:900px;margin:0 auto}.article-body .lede{font-size:1.2rem;color:var(--ink)}.article-body h2{margin-top:34px}.article-body ul,.article-body ol{padding-left:24px}.callout{margin:26px 0;padding:20px;border-left:5px solid var(--rose);background:#fff4f3;border-radius:8px}.callout.safety{border-left-color:var(--sage);background:#f2f7f1}.article-side{position:sticky;top:90px;display:grid;gap:16px}.guardian-hero{background:linear-gradient(120deg,#fff8f2,#eef5ef)}.note-section{background:#fff}.contact-line a{font-size:1.25rem;color:var(--rose);font-weight:900}.site-footer{padding:44px min(7vw,92px);background:#2f2527;color:#fff}.footer-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin-bottom:24px}.footer-grid a{background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.16);color:#fff}.site-footer p,.site-footer span{color:#ead6d4}.site-footer a{color:#fff}@media(max-width:840px){.site-nav{align-items:flex-start;flex-direction:column}.nav-links{flex-wrap:wrap}.hero,.intro-grid,.quiz-band,.article-hero,.guardian-hero,.article-shell{grid-template-columns:1fr}.hero{padding-top:40px}.hero picture,.hero img{min-height:280px}.article-side{position:static}.section-head{display:block}.language-switcher{justify-content:flex-start}}
"""
    write(ROOT / "shared.css", css.strip() + "\n")


def write_support_files() -> None:
    urls = []
    for lang in LANGS:
        paths = ["", "guides", "theory", "resources", "about", "contact", "privacy", "terms"]
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
    write(ROOT / "_headers", "/*\n  Cache-Control: public, max-age=600\n\n/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n\n/shared.css*\n  Cache-Control: public, max-age=31536000, immutable\n")


def main() -> None:
    write_css()
    for lang in LANGS:
        home(lang)
        guides_index(lang)
        for idx, guide in enumerate(GUIDES):
            guide_page(lang, guide, idx)
        for slug, data in GUARDIANS.items():
            character_page(lang, slug, data)
        for slug in ["theory", "resources", "about", "contact", "privacy", "terms"]:
            simple_page(lang, slug)
        simple_page(lang, "luna-yoga-music")
    for slug, title, desc, target in LEGACY_ZH_GUIDES:
        legacy_zh_guide_page(slug, title, desc, target)
    write_support_files()


if __name__ == "__main__":
    main()
