#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
BACKLOG_PATH = PROMOTION_DIR / "asset-build-backlog.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "now-asset-production-pack.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "now-asset-production-pack.json"
GUARDIAN_ORDER = ("iris", "noah", "vivian", "claire", "dora")
MIN_SUBTITLE_LINES_PER_SCRIPT = 8
REQUIRED_QUIZ_CTA = "完成 15 題測驗"
FORBIDDEN_CLAIMS = ("診斷", "療效", "保證修復", "必須購買")
GUARDIAN_VARIANTS = {
    "iris": {
        "theme": "浪漫與文字",
        "emotion_types": ["已讀沉默", "想被看見", "清楚回應"],
        "title": "你等的不是秒回，是一句清楚的在乎",
        "hook": "如果他回很慢，你第一個害怕的是什麼？",
        "lines": [
            "他不是沒回。",
            "但你心裡已經跑完一整場雨。",
            "A：我是不是不重要了。",
            "B：我是不是又太敏感了。",
            "C：我只是想聽一句清楚的話。",
            "艾莉絲不會叫你猜。",
            "她會把沉默翻成你真正想說的句子。",
            "你最想被哪一句話接住？",
            "完成 15 題測驗，找到你的情感守護者。",
        ],
        "visual": [
            "晨曦玻璃花園，手機已讀訊息停在畫面中央。",
            "羽筆把模糊問號改寫成金色短句。",
            "A/B/C 選項以玻璃光牌浮現。",
        ],
        "comment": "留言 A/B/C，或寫下你最想聽見的那句話。",
    },
    "noah": {
        "theme": "神秘與宇宙",
        "emotion_types": ["陪伴缺席", "遠距不安", "約定被取消"],
        "title": "他人在你旁邊，心卻像不在場",
        "hook": "你最怕的不是孤單，是明明有人卻沒有被陪伴。",
        "lines": [
            "有些約會很安靜。",
            "不是因為舒服。",
            "而是你感覺他其實不在。",
            "A：一直看手機。",
            "B：約定常常被延後。",
            "C：聽你說話卻沒有記住。",
            "諾雅會在星海裡替你留一盞燈。",
            "提醒你要的不是黏人。",
            "而是一段真正在場的時間。",
            "完成 15 題測驗，找到你的情感守護者。",
        ],
        "visual": [
            "星海圖書館，桌上攤開星圖與兩只杯子。",
            "其中一盞燈忽明忽暗，最後穩定亮起。",
            "A/B/C 選項像星座節點連線。",
        ],
        "comment": "留言 A/B/C，你最不能接受哪一種不在場？",
    },
    "vivian": {
        "theme": "被重視與儀式感",
        "emotion_types": ["被忘記", "儀式感", "心意確認"],
        "title": "你不是想要禮物，你想知道自己有沒有被記得",
        "hook": "重要日子被忘記時，你真正痛的是哪裡？",
        "lines": [
            "那一天不只是日期。",
            "是你偷偷期待被記得的證據。",
            "A：他忘了你說過的話。",
            "B：他覺得這不重要。",
            "C：他補救時像在交差。",
            "薇薇安守護的不是價格。",
            "而是被放在心上的痕跡。",
            "你最想被記得的是哪件小事？",
            "完成 15 題測驗，找到你的情感守護者。",
        ],
        "visual": [
            "月光記憶工坊，緞帶、票根與小禮盒排列在桌面。",
            "忘記的日期被金色墨水重新圈起。",
            "A/B/C 選項像抽屜標籤打開。",
        ],
        "comment": "留言一個你希望被記得的小日子，或選 A/B/C。",
    },
    "claire": {
        "theme": "療癒與陪伴",
        "emotion_types": ["沒被分擔", "行動落差", "疲憊關係"],
        "title": "你要的不是幫忙，是有人看見你快撐不住了",
        "hook": "當你說沒事的時候，你其實希望他做什麼？",
        "lines": [
            "你不是什麼都能自己來。",
            "你只是太習慣先撐住。",
            "A：希望他主動分擔。",
            "B：希望他記得你累在哪裡。",
            "C：希望他不要等你崩潰才行動。",
            "克萊兒不會把愛說得很大聲。",
            "她會把愛放進一個具體動作。",
            "你現在最想被分擔的是什麼？",
            "完成 15 題測驗，找到你的情感守護者。",
        ],
        "visual": [
            "溫室修復間，工具袋、澆水壺與被扶起的小植物。",
            "待辦清單上的重擔被一個暖白光點接住。",
            "A/B/C 選項像工具吊牌浮現。",
        ],
        "comment": "留言 A/B/C，或寫下你最希望有人幫你接住的一件事。",
    },
    "dora": {
        "theme": "溫暖與擁抱",
        "emotion_types": ["安全距離", "界線", "被安撫"],
        "title": "你不是任性，你只是需要一種安全的靠近",
        "hook": "你最想要的親密，是靠近，還是先被允許？",
        "lines": [
            "有些擁抱很近。",
            "卻不一定讓人安心。",
            "A：我想先確認界線。",
            "B：我想被溫柔安撫。",
            "C：我想有人問我可不可以。",
            "朵拉守護的不是強迫靠近。",
            "而是讓身體知道自己安全。",
            "你最需要哪一種靠近？",
            "完成 15 題測驗，找到你的情感守護者。",
        ],
        "visual": [
            "玫瑰金安全聖域，柔軟布料與暖光圍出安全邊界。",
            "兩個人影停在合適距離，光圈慢慢靠近。",
            "A/B/C 選項像柔軟織帶標籤。",
        ],
        "comment": "留言 A/B/C，你最需要哪一種安全靠近？",
    },
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def script_policy() -> dict[str, object]:
    return {
        "guardianOrder": list(GUARDIAN_ORDER),
        "minSubtitleLinesPerScript": MIN_SUBTITLE_LINES_PER_SCRIPT,
        "requiredQuizCta": REQUIRED_QUIZ_CTA,
        "forbiddenClaims": list(FORBIDDEN_CLAIMS),
        "rule": "每支 now content variant 必須有足夠字幕行、保留測驗 CTA，且不得使用診斷、療效、保證修復或必須購買說法。",
    }


def build_script(item: dict) -> dict:
    guardian = item["guardianId"]
    variant = GUARDIAN_VARIANTS[guardian]
    return {
        "id": f"{guardian}-now-content-variant-01",
        "backlog_item_id": item["id"],
        "guardian_id": guardian,
        "guardian_name": item["guardianName"],
        "guardian_theme": variant["theme"],
        "emotion_types": variant["emotion_types"],
        "title": variant["title"],
        "hook": variant["hook"],
        "full_subtitle_script": variant["lines"],
        "visual_suggestions": variant["visual"],
        "comment_cta": variant["comment"],
        "tracked_url": item.get("sourceTrackedUrl") or item["targetUrl"],
        "source_task_id": item["sourceTaskId"],
        "safety": item["safety"],
    }


def build_pack(backlog: dict) -> dict:
    now_items = [
        item for item in backlog.get("items", [])
        if item.get("priority") == "now" and item.get("assetType") == "content_variant"
    ]
    now_items.sort(key=lambda item: GUARDIAN_ORDER.index(item["guardianId"]))
    scripts = [build_script(item) for item in now_items]
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "backlog": str(BACKLOG_PATH.relative_to(ROOT)),
        },
        "scriptPolicy": script_policy(),
        "scriptCount": len(scripts),
        "guardianCount": len({script["guardian_id"] for script in scripts}),
        "expectedScriptCount": len(now_items),
        "expectedGuardianCount": len({item["guardianId"] for item in now_items}),
        "scripts": scripts,
        "productionChecklist": [
            "每支短片維持單一 CTA：完成 15 題測驗，找到你的情感守護者。",
            "字幕逐行短句，不一次揭示答案，保留留言互動。",
            "畫面使用對應守護者宇宙，不交換角色色系或象徵物。",
            "不使用診斷、療效、保證修復或必須購買說法。",
            "發布後回填 posting-queue.csv 與 platform-kpi-tracker.csv；週回顧才彙總 kpi-tracker.csv。",
        ],
    }


def render_markdown(pack: dict) -> str:
    lines = [
        "# LoveTypes Now Asset Production Pack",
        "",
        f"- 產生日期：{pack['generatedAt']}",
        f"- 腳本數：{pack['scriptCount']}",
        f"- 守護者數：{pack['guardianCount']}",
        "",
        "## 製作規則",
        "",
    ]
    lines.extend(f"- {item}" for item in pack["productionChecklist"])
    policy = pack.get("scriptPolicy", {})
    if policy:
        lines.extend([
            "",
            "## 腳本完整性規則",
            "",
            f"- 最少字幕行：{policy['minSubtitleLinesPerScript']}",
            f"- 必須保留 CTA：{policy['requiredQuizCta']}",
            f"- 禁止詞：{', '.join(policy['forbiddenClaims'])}",
        ])
    for script in pack["scripts"]:
        lines.extend([
            "",
            f"## {script['guardian_name']}（{script['guardian_id']}）",
            "",
            f"### 影片標題",
            "",
            script["title"],
            "",
            "### Hook",
            "",
            script["hook"],
            "",
            "### 完整字幕腳本",
            "",
        ])
        lines.extend(f"{index}. {line}" for index, line in enumerate(script["full_subtitle_script"], start=1))
        lines.extend(["", "### 畫面建議", ""])
        lines.extend(f"- {item}" for item in script["visual_suggestions"])
        lines.extend([
            "",
            "### 結尾留言引導",
            "",
            script["comment_cta"],
            "",
            f"- 追蹤入口：{script['tracked_url']}",
            f"- 來源任務：{script['source_task_id']}",
            f"- 安全邊界：{script['safety']}",
        ])
    return "\n".join(lines).rstrip() + "\n"


def validate_pack(pack: dict) -> list[str]:
    issues: list[str] = []
    expected_guardians = int(pack.get("expectedGuardianCount", 0) or 0)
    expected_scripts = int(pack.get("expectedScriptCount", 0) or 0)
    policy = pack.get("scriptPolicy", {})
    min_subtitle_lines = int(policy.get("minSubtitleLinesPerScript", 0) or 0) if isinstance(policy, dict) else 0
    required_cta = str(policy.get("requiredQuizCta", "")) if isinstance(policy, dict) else ""
    forbidden = tuple(policy.get("forbiddenClaims", [])) if isinstance(policy, dict) else ()
    if min_subtitle_lines < 1 or not required_cta or not forbidden:
        issues.append("missing script policy")
    if pack.get("guardianCount") != expected_guardians:
        issues.append(f"expected {expected_guardians} guardians in now asset production pack")
    if pack.get("scriptCount") != expected_scripts:
        issues.append(f"expected {expected_scripts} now scripts")
    required = {"id", "guardian_id", "guardian_name", "guardian_theme", "emotion_types", "title", "hook", "full_subtitle_script", "visual_suggestions", "comment_cta"}
    for script in pack.get("scripts", []):
        missing = [field for field in required if not script.get(field)]
        if missing:
            issues.append(f"{script.get('id', '<unknown>')}: missing {', '.join(missing)}")
        if len(script.get("full_subtitle_script", [])) < min_subtitle_lines:
            issues.append(f"{script.get('id', '<unknown>')}: subtitle script should have at least {min_subtitle_lines} lines")
        if required_cta not in " ".join(script.get("full_subtitle_script", [])):
            issues.append(f"{script.get('id', '<unknown>')}: subtitle script missing quiz CTA")
        text = " ".join(script.get("full_subtitle_script", [])) + " " + script.get("comment_cta", "")
        for word in forbidden:
            if word in text:
                issues.append(f"{script.get('id', '<unknown>')}: forbidden claim {word}")
    return issues


def write_outputs(pack: dict, output: Path, json_output: Path) -> None:
    output.write_text(render_markdown(pack), encoding="utf-8")
    json_output.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LoveTypes production pack for current priority asset backlog items.")
    parser.add_argument("--backlog", default=str(BACKLOG_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    pack = build_pack(load_json(Path(args.backlog)))
    issues = validate_pack(pack)
    if not args.check:
        write_outputs(pack, Path(args.output), Path(args.json_output))
        print(f"promotion_now_asset_pack={args.output}")
        print(f"promotion_now_asset_pack_json={args.json_output}")
    print(f"promotion_now_asset_pack_scripts={pack['scriptCount']}")
    print(f"promotion_now_asset_pack_guardians={pack['guardianCount']}")
    print(f"promotion_now_asset_pack_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
