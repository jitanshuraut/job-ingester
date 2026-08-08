import os
import time
import logging
import requests
from random import uniform
from dotenv import load_dotenv
from collections import defaultdict
from typing import List


class TelegramException(Exception):
    pass


class TelegramBot:
    API_BASE = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self):
        load_dotenv()
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_ids_raw = os.getenv("TELEGRAM_CHAT_IDS", "")
        self.chat_ids = [c.strip() for c in chat_ids_raw.split(",") if c.strip()]
        if not self.bot_token or not self.chat_ids:
            raise TelegramException(
                "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_IDS environment variables are required"
            )
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
        return logger

    def _call(self, method: str, payload: dict, chat_id: str = "") -> dict:
        url = self.API_BASE.format(token=self.bot_token, method=method)
        for attempt in range(3):
            try:
                r = requests.post(url, json=payload, timeout=15)
                data = r.json()
                if not data.get("ok"):
                    desc = data.get("description", "unknown")
                    if "retry after" in desc:
                        try:
                            secs = int(desc.split("retry after ")[1].split()[0])
                        except Exception:
                            secs = 5
                        self.logger.warning("Rate limited, waiting %ss...", secs)
                        time.sleep(secs + 1)
                        continue
                    self.logger.error("Telegram API error: %s", desc)
                return data
            except Exception as e:
                self.logger.error("Telegram API call failed: %s", e)
                if attempt < 2:
                    time.sleep(2)
        return {"ok": False}

    def send_message(self, text: str, parse_mode: str = "HTML") -> dict:
        results = []
        for chat_id in self.chat_ids:
            chunks = self._split_message(text)
            for chunk in chunks:
                result = self._call("sendMessage", {
                    "chat_id": chat_id,
                    "text": chunk,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": True,
                }, chat_id=chat_id)
                results.append(result)
        return {"ok": all(r.get("ok") for r in results)}

    def _split_message(self, text: str, max_len: int = 4000) -> list[str]:
        if len(text) <= max_len:
            return [text]
        chunks = []
        while text:
            if len(text) <= max_len:
                chunks.append(text)
                break
            split_at = text.rfind("\n\n", 0, max_len)
            if split_at == -1:
                split_at = text.rfind("\n", 0, max_len)
            if split_at == -1:
                split_at = max_len
            chunks.append(text[:split_at])
            text = text[split_at:].lstrip("\n")
        return chunks

    def _escape(self, text: str) -> str:
        return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _experience_label(self, title: str) -> tuple[str, str]:
        t = title.lower()
        if any(kw in t for kw in ("intern", "trainee", "fresher", "graduate")):
            return "🟢", "Fresher / Internship Opportunity"
        if any(kw in t for kw in ("senior", "lead", "manager", "principal", "staff", "head", "architect", "director")):
            return "🟡", "Experienced Opportunity"
        return "🔵", "Opportunity"

    def _format_single_job(self, job) -> str:
        emoji, label = self._experience_label(job.title or "")
        company = self._escape(job.company or "—")
        title = self._escape(job.title or "—")
        loc = self._escape(job.location or "—")
        date = self._escape(str(job.posted_date or "") or "—")
        jid = self._escape(str(job.jobid or "") or "—")

        text = (
            f"\U0001F680 New Opportunity Alert ({emoji} {label})\n\n"
            f"\U0001F3E2 Company: <b>{company}</b>\n\n"
            f"\U0001F4CC Role: <b>{title}</b>\n\n"
            f"\U0001F4CD Location: {loc}\n\n"
            f"\U0001F4C5 Posted: {date}\n\n"
            f"\U0001F194 Req ID: {jid}"
        )

        if job.experience_years:
            text += f"\n\n\u23F0 Experience: {self._escape(job.experience_years)}"
        if job.skills:
            text += f"\n\n\uD83D\uDD27 Skills: {self._escape(job.skills)}"

        if job.url:
            text += f'\n\n\U0001F517 Apply here: <a href="{job.url}">{job.url}</a>'

        return text

    def send_jobs(self, jobs: list) -> dict:
        try:
            results = []
            total = len(jobs)
            for i, job in enumerate(jobs, 1):
                text = self._format_single_job(job)
                result = self.send_message(text)
                results.append(result)
                if i % 10 == 0 or i == total:
                    self.logger.info("Sent %d/%d jobs", i, total)
                time.sleep(uniform(1.0, 1.5))
            return {"ok": all(r.get("ok") for r in results), "count": len(results)}
        except Exception as e:
            error_msg = f"Error sending Telegram notification: {e}"
            self.logger.error(error_msg)
            return {"ok": False, "error": error_msg}
