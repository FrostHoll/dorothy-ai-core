from typing import Any

import html2text
from bs4 import BeautifulSoup
from playwright.async_api import Browser, BrowserContext, async_playwright

from app.infrastructure.tools.tool_abc import ToolABC
from app.infrastructure.tools.tool_parameter import ToolParameter


class GetWebpageTool(ToolABC):
    def __init__(self):
        super().__init__()
        self._parameters = [
            ToolParameter("url", "string", "Full URL of the webpage to fetch.", required=True),
            ToolParameter("substring", "string", "A text fragment that definitely appears on the page "
                                                 "(e.g., from the snippet/body of search results). "
                                                 "If found, the output starts from this substring, giving you the most relevant portion. "
                                                 "If NOT found, the tool returns the beginning of the page (up to maxSymbols). "
                                                 "Recommendation: always take substring from the 'body' field of WebSearchTool results."),
            ToolParameter("maxSymbols", "integer", "Maximum number of characters to extract from the page. "
                                                   "Default: 1000. If the returned fragment is too short or doesn't contain the needed info, "
                                                   "INCREASE this value (e.g., to 3000 or 5000) on subsequent calls. "
                                                   "Don't hesitate to increase it — it's safe and encouraged.")
        ]
        self.playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = True
        self.h2t.body_width = 0
        self.h2t.ignore_images = True
        self.cached_page: dict[str, str] = {}

    def get_name(self) -> str:
        return "GetWebpage"

    def get_description(self) -> str:
        return ("PURPOSE: Fetch and extract text content from a webpage (full or partial) for in-depth reading.\n"
                "WHEN TO USE:\n"
                "- Immediately AFTER WebSearchTool — to read the most relevant pages from search results\n"
                "- When the search snippet doesn't provide enough detail\n"
                "- When you need exact quotes, statistics, arguments, or comprehensive explanations\n"
                "- When you need to verify facts from the snippet\n"
                "HOW TO USE SUBSTRING & MAXSYMBOLS EFFECTIVELY:\n"
                "SUBSTRING:\n"
                "- ALWAYS take it from the \"body\" field of a WebSearchTool result - This ensures you jump directly to the relevant section of the page\n"
                "- If substring is not found, the page will be returned from the beginning (good for fallback)\n"
                "MAXSYMBOLS:- Start with 1500 for most pages- If the returned content is cut off in the middle of useful information → "
                "call AGAIN with the same URL and substring, but increase maxSymbols to 3000 or 5000\n"
                "- You can safely call this tool 2–3 times per URL — it's not wasteful, it's how you get complete data\n"
                "ERROR HANDLING:\n"
                "- If you get a timeout, access denied error → DO NOT retry this URL - Move to the next result from your search\n"
                "- If substring is not found, and the returned beginning isn't useful → try another substring from the same snippet, "
                "or increase maxSymbols\n"
                "REMEMBER: Multiple calls to this tool are NORMAL and EXPECTED when gathering thorough information.")

    async def _init_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            args=["--disable-http2"],
            headless=True
        )
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='ru-RU',
            timezone_id='Europe/Moscow'
        )
        await self.context.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                        })
                    """)

    async def _execute(self, params: dict[str, str]) -> Any:
        if self.browser is None:
            await self._init_browser()

        url = params["url"]
        substring: str | None = None
        max_symbols: int = 1000
        if "substring" in params:
            substring = params["substring"]
        if "maxSymbols" in params:
            max_symbols = int(params["maxSymbols"])
        try:
            meta_text = f"[Showing First {max_symbols} Symbols]\n"
            if url in self.cached_page:
                clean_text = self.cached_page[url]
            else:
                raw_page_content = await self._get_page_content(url)
                if not raw_page_content:
                    raise Exception("Failed to load page. Check logs.")
                clean_text = self._parse_text_content(raw_page_content)
                self.cached_page[url] = clean_text
            if substring:
                specified_text = self._try_find_substring(clean_text, substring)
                if not specified_text:
                    meta_text += "[Substring Match Found: False]\n"
                    return meta_text + clean_text[:max_symbols]
                else:
                    meta_text += "[Filtered Page Content]\n[Substring Match Found: True]\n"
                    return meta_text + specified_text[:max_symbols]
            return meta_text + clean_text[:max_symbols]
        except Exception as e:
            raise Exception(f"Error occured during getting content of a webpage: {str(e)}")

    async def close(self) -> None:
        if self.context:
            await self.context.close()
        if self.browser:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()

    async def _get_page_content(self, url: str) -> str | None:
        page = await self.context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_selector("body", timeout=5000)
            return await page.content()
        except Exception as e:
            print(f"Error during loading page: {str(e)}")
            return None
        finally:
            await page.close()

    def _parse_text_content(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'input', 'video', 'img', 'iframe']):
            tag.decompose()
        clean_html = str(soup)
        return self.h2t.handle(clean_html)

    def _get_first_n_words_with_offset(self, s: str, n: int, start: int):
        words = s.split()
        return " ".join(words[start:n + start])

    def _try_find_substring(self, text: str, sub: str) -> str | None:
        words = 3
        offset = 0
        max_words = len(text.split())
        found = False
        result: str | None = None
        while not found:
            curr_sub = self._get_first_n_words_with_offset(sub, words, offset)
            if not curr_sub.strip():
                print("Failed to find sub. Halting...")
                break
            print(f"Try to find sub: {curr_sub}")
            index = text.find(curr_sub)
            if index > -1:
                print(f"Found at {index}")
                found = True
                result = text[index:]
            else:
                offset += words
                print("Failed to find sub. Moving to next...")
                if offset + words > max_words:
                    print("Reached max attempts. Halting...")
                    break
        return result

    def get_display_text(self, params: dict[str, str]) -> str:
        url = params["url"]
        return f"| Читаю страницу \"{url}\"... |"