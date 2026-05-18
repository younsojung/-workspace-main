#!/usr/bin/env python3
"""
YouTube → Notion handler.

Subcommands:
  extract  --url URL              # Print metadata + transcript as JSON (stdout)
  save     --stdin                # Read enriched JSON from stdin, create Notion page

The "save" command expects the JSON from extract plus Claude-generated fields:
  summary, insights, category, tags (list)
"""

import argparse
import json
import os
import re
import sys
from datetime import date


def _load_dotenv() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    for n in range(1, 6):
        env_path = os.path.abspath(os.path.join(here, *([".."] * n), ".env"))
        if os.path.isfile(env_path):
            with open(env_path, encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and k not in os.environ:
                        os.environ[k] = v
            return


_load_dotenv()

import requests  # noqa: E402

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
YOUTUBE_DB_ID = "35d9073fdb96811bbfcee7d6367df6ec"


# ---------- EXTRACT ----------

def _download_caption(url: str, ext: str) -> str:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    if ext == "json3":
        data = r.json()
        texts = []
        for ev in data.get("events", []):
            for seg in ev.get("segs", []):
                t = seg.get("utf8")
                if t and t != "\n":
                    texts.append(t)
        return _normalize("".join(texts))
    if ext == "vtt":
        out = []
        skip_prefix = ("WEBVTT", "Kind:", "Language:", "NOTE")
        for line in r.text.splitlines():
            line = line.strip()
            if not line or "-->" in line or any(line.startswith(p) for p in skip_prefix):
                continue
            line = re.sub(r"<[^>]+>", "", line)
            if line and (not out or out[-1] != line):
                out.append(line)
        return _normalize(" ".join(out))
    return ""


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _fetch_transcript(info: dict, langs=("ko", "en")):
    for source in ("subtitles", "automatic_captions"):
        for lang in langs:
            entries = info.get(source, {}).get(lang) or []
            for ext in ("json3", "vtt"):
                for e in entries:
                    if e.get("ext") == ext:
                        try:
                            txt = _download_caption(e["url"], ext)
                            if txt:
                                return txt, lang, source
                        except Exception:
                            continue
    return None, None, None


def cmd_extract(url: str, pretty: bool = False) -> None:
    try:
        from yt_dlp import YoutubeDL
    except ImportError:
        _die("yt-dlp not installed. Activate .venv and run: pip install yt-dlp")

    with YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as ydl:
        info = ydl.extract_info(url, download=False)

    transcript, lang, source = _fetch_transcript(info)

    upload_date_raw = info.get("upload_date")
    upload_date_iso = (
        f"{upload_date_raw[:4]}-{upload_date_raw[4:6]}-{upload_date_raw[6:8]}"
        if upload_date_raw and len(upload_date_raw) == 8
        else None
    )

    dur = info.get("duration") or 0
    h, rem = divmod(int(dur), 3600)
    m, s = divmod(rem, 60)
    dur_str = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

    result = {
        "video_id": info.get("id"),
        "title": info.get("title"),
        "channel": info.get("uploader") or info.get("channel"),
        "channel_url": info.get("uploader_url") or info.get("channel_url"),
        "upload_date": upload_date_iso,
        "duration_seconds": dur,
        "duration": dur_str,
        "thumbnail_url": info.get("thumbnail"),
        "description": info.get("description"),
        "view_count": info.get("view_count"),
        "source_url": info.get("webpage_url") or url,
        "transcript": transcript,
        "transcript_lang": lang,
        "transcript_source": source,
        "transcript_available": transcript is not None,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2 if pretty else None))


# ---------- SAVE ----------

def _truncate(text: str, limit: int = 1900) -> str:
    if not text:
        return ""
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _build_properties(data: dict) -> dict:
    today = date.today().isoformat()
    props: dict = {
        "제목": {"title": [{"text": {"content": data.get("title", "Untitled")}}]},
        "시청 상태": {"select": {"name": "미시청"}},
        "추가일": {"date": {"start": today}},
    }
    if data.get("source_url"):
        props["URL"] = {"url": data["source_url"]}
    if data.get("channel"):
        props["채널"] = {"rich_text": [{"text": {"content": data["channel"]}}]}
    if data.get("upload_date"):
        props["게시일"] = {"date": {"start": data["upload_date"]}}
    if data.get("thumbnail_url"):
        props["썸네일"] = {
            "files": [{
                "type": "external",
                "name": f"{data.get('video_id', 'thumbnail')}.jpg",
                "external": {"url": data["thumbnail_url"]},
            }]
        }
    if data.get("category"):
        props["카테고리"] = {"select": {"name": data["category"]}}
    if data.get("tags"):
        props["태그"] = {"multi_select": [{"name": t} for t in data["tags"]]}
    if data.get("summary"):
        props["요약"] = {"rich_text": [{"text": {"content": _truncate(data["summary"])}}]}
    if data.get("insights"):
        props["핵심 인사이트"] = {"rich_text": [{"text": {"content": _truncate(data["insights"])}}]}
    return props


def _notion_headers() -> dict:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        _die("NOTION_TOKEN not set (check workspace .env)")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def cmd_save(stdin_data: str) -> None:
    try:
        data = json.loads(stdin_data)
    except json.JSONDecodeError as e:
        _die(f"Invalid JSON on stdin: {e}")

    payload = {
        "parent": {"database_id": YOUTUBE_DB_ID},
        "properties": _build_properties(data),
    }
    r = requests.post(f"{NOTION_API_BASE}/pages", headers=_notion_headers(), json=payload, timeout=30)
    if not r.ok:
        _die(f"Notion API error {r.status_code}: {r.text}")

    out = r.json()
    print(json.dumps({
        "ok": True,
        "page_id": out.get("id"),
        "page_url": out.get("url"),
    }, ensure_ascii=False, indent=2))


# ---------- UPDATE ----------

def cmd_update(page_id: str, stdin_data: str) -> None:
    """Update an existing Notion page's properties from JSON on stdin."""
    try:
        data = json.loads(stdin_data)
    except json.JSONDecodeError as e:
        _die(f"Invalid JSON on stdin: {e}")

    payload = {"properties": _build_properties(data)}
    r = requests.patch(f"{NOTION_API_BASE}/pages/{page_id}", headers=_notion_headers(), json=payload, timeout=30)
    if not r.ok:
        _die(f"Notion API error {r.status_code}: {r.text}")

    out = r.json()
    print(json.dumps({
        "ok": True,
        "page_id": out.get("id"),
        "page_url": out.get("url"),
    }, ensure_ascii=False, indent=2))


# ---------- LIST CHANNEL ----------

def cmd_list_channel(channel_url: str, max_count: int = 10) -> None:
    """List recent videos from a YouTube channel (fast, flat extraction)."""
    try:
        from yt_dlp import YoutubeDL
    except ImportError:
        _die("yt-dlp not installed")

    if not channel_url.rstrip("/").endswith("/videos"):
        videos_url = channel_url.rstrip("/") + "/videos"
    else:
        videos_url = channel_url

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "playlistend": max_count,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(videos_url, download=False)

    entries = info.get("entries") or []
    videos = []
    for e in entries[:max_count]:
        if not e:
            continue
        vid = e.get("id")
        if not vid:
            continue
        videos.append({
            "video_id": vid,
            "title": e.get("title"),
            "url": e.get("url") or f"https://www.youtube.com/watch?v={vid}",
            "duration_seconds": e.get("duration"),
        })

    print(json.dumps({
        "channel_title": info.get("channel") or info.get("uploader") or info.get("title"),
        "channel_url": channel_url,
        "video_count": len(videos),
        "videos": videos,
    }, ensure_ascii=False, indent=2))


# ---------- CHECK EXISTS ----------

def cmd_check_exists(video_id: str) -> None:
    """Check whether a video_id is already in the YouTube archive DB."""
    payload = {
        "filter": {
            "property": "URL",
            "url": {"contains": video_id},
        },
        "page_size": 1,
    }
    r = requests.post(
        f"{NOTION_API_BASE}/databases/{YOUTUBE_DB_ID}/query",
        headers=_notion_headers(),
        json=payload,
        timeout=30,
    )
    if not r.ok:
        _die(f"Notion API error {r.status_code}: {r.text}")

    results = r.json().get("results", [])
    exists = len(results) > 0
    print(json.dumps({
        "exists": exists,
        "video_id": video_id,
        "page_id": results[0]["id"] if exists else None,
        "page_url": results[0]["url"] if exists else None,
    }, ensure_ascii=False, indent=2))


def _die(msg: str) -> None:
    print(json.dumps({"error": msg}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="YouTube → Notion handler")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_extract = sub.add_parser("extract", help="Extract metadata + transcript")
    p_extract.add_argument("--url", required=True)
    p_extract.add_argument("--pretty", action="store_true")

    p_save = sub.add_parser("save", help="Create Notion page from JSON on stdin")
    p_save.add_argument("--stdin", action="store_true")

    p_update = sub.add_parser("update", help="Update Notion page properties from JSON on stdin")
    p_update.add_argument("--page-id", required=True)
    p_update.add_argument("--stdin", action="store_true")

    p_list = sub.add_parser("list-channel", help="List recent videos from a channel")
    p_list.add_argument("--url", required=True, help="Channel URL (e.g. https://www.youtube.com/@handle)")
    p_list.add_argument("--max", type=int, default=10)

    p_check = sub.add_parser("check-exists", help="Check if video_id exists in DB")
    p_check.add_argument("--video-id", required=True)

    args = parser.parse_args()

    if args.cmd == "extract":
        cmd_extract(args.url, pretty=args.pretty)
    elif args.cmd == "save":
        cmd_save(sys.stdin.read())
    elif args.cmd == "update":
        cmd_update(args.page_id, sys.stdin.read())
    elif args.cmd == "list-channel":
        cmd_list_channel(args.url, max_count=args.max)
    elif args.cmd == "check-exists":
        cmd_check_exists(args.video_id)


if __name__ == "__main__":
    main()
