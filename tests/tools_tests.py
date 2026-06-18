import random
from typing import Any

import html2text
from ddgs import DDGS
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from app.infrastructure.llm.llama_engine import LlamaEngine
from app.infrastructure.tools.text_postprocessor import TextPostprocessor
from app.infrastructure.tools.tool_abc import ToolABC
from app.infrastructure.tools.tool_container import ToolContainer
from app.infrastructure.tools.tool_parameter import ToolParameter
from app.infrastructure.tools.tool_proxy import ToolProxy


class RollNumberTool(ToolABC):
    def __init__(self):
        super().__init__()
        self._parameters = [
            ToolParameter("maxRange", "integer", "Maximum value of the range. Inclusive.")
        ]

    def get_description(self) -> str:
        return "Get random number in range from 0 to 100 by default."

    def get_name(self) -> str:
        return "roll_number"

    def _execute(self, params: dict[str, str]) -> Any:
        max_range = 100
        if "maxRange" in params:
            max_range = int(params["maxRange"])
        return random.randint(0, max_range)

    def get_display_text(self, params: dict[str, str]) -> str:
        max_range = 100
        if "maxRange" in params:
            max_range = params["maxRange"]
        return f"|Генерирую случайное число от 0 до {max_range}|"

class WebSearchTool(ToolABC):
    def __init__(self):
        super().__init__()
        self._parameters = [
            ToolParameter("query", "string", "Query text to search.", required=True)
        ]
        self.ddgs_client = DDGS()

    def get_name(self) -> str:
        return "WebSearch"

    def get_description(self) -> str:
        return ("Use this tool to search for information through Google. This tool returns 5 top entries. "
                "Use this tool when user explicitly asks for it, or when it is necessary. The results are automatically sorted by relevance.")

    def _execute(self, params: dict[str, str]) -> Any:
        query = params["query"]
        results = self._search_duckduckgo(query)
        return self._results_to_string(results)

    def _search_duckduckgo(self, query: str) -> list[dict[str, str]]:
        results = self.ddgs_client.text(query, max_results=5, region="ru-ru")
        return results

    def _results_to_string(self, sources: list[dict[str, str]]) -> str:
        return "\n".join(
            f"Source {i + 1}:\n" + "\n".join(f"{k}: {v}" for k, v in src.items())
            for i, src in enumerate(sources)
        )

    def get_display_text(self, params: dict[str, str]) -> str:
        query = params["query"]
        return f"|Ищу по запросу {query}...|"

class GetWebpageTool(ToolABC):
    def __init__(self):
        super().__init__()
        self._parameters = [
            ToolParameter("url", "string", "The URL to a webpage you want to get.", required=True),
            ToolParameter("substring", "string", "The substring to search for in the page content. "
                                                 "There's a high chance of not finding the specified substring, in this case try using other substring."),
            ToolParameter("maxSymbols", "integer", "Limit the number of symbols of the retrieved page. "
                                                   "If not specified, defaults to 1000.")
        ]
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(
            args=["--disable-http2"],
            headless=True
        )
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='ru-RU',
            timezone_id='Europe/Moscow'
        )
        self.context.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                        })
                    """)
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = True
        self.h2t.body_width = 0
        self.h2t.ignore_images = True
        self.cached_page: dict[str, str] = {}

    def get_name(self) -> str:
        return "GetWebpage"

    def get_description(self) -> str:
        return ("Use this tool to get whole content of the webpage. You can use this tool in combination with WebSearchTool, "
                "to get more useful information. You can pass a substring from \'body\' from search result to get more clean content. "
                "If you need more information, but it's locked under symbols limitation, you can safely call this tool again. "
                "IMPORTANT: It is highly recommended to use with \'substring\' parameter. "
                "If you specified substring and it was not found, the tool will return a full page. "
                "Some webpages cannot be accessed due to security reasons or being banned. "
                "If you encountered security template page or timeout error, DO NOT try to access it further.")

    def _execute(self, params: dict[str, str]) -> Any:
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
                raw_page_content = self._get_page_content(url)
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

    def close(self) -> None:
        self.context.close()
        self.browser.close()
        self.p.stop()

    def _get_page_content(self, url: str) -> str | None:
        page = self.context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_selector("body", timeout=5000)
            return page.content()
        except Exception as e:
            print(f"Error during loading page: {str(e)}")
            return None
        finally:
            page.close()

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
        return f"|Читаю страницу {url}...|"

class ListToolsTool(ToolABC):
    def __init__(self, tool_container: ToolContainer):
        super().__init__()
        self.tool_container = tool_container

    def get_name(self) -> str:
        return "ListTools"

    def get_description(self) -> str:
        return "This tool returns list of all tools and their current state (enabled/disabled). Use this tool if you're not sure, what tools you have and whether it's enabled."

    def _execute(self, params: dict[str, str]) -> Any:
        return str(self.tool_container.get_all_tools())

    def get_display_text(self, params: dict[str, str]) -> str:
        return "|Смотрю доступные инструменты...|"

if __name__ == "__main__":
    container = ToolContainer()
    TextPostprocessor.tool_container = container
    container.register_tool(ToolProxy(ListToolsTool, tool_container=container))
    container.register_tool(ToolProxy(GetWebpageTool))
    container.register_tool(ToolProxy(WebSearchTool))
    container.register_tool(ToolProxy(RollNumberTool))

    container.enable_tool("ListToolsTool")
    container.enable_tool("WebSearchTool")
    container.enable_tool("GetWebpageTool")

    model = LlamaEngine(container)

    history = [{"role": "system", "content": "You are an AI assistant, who can use tools. If tool is malfunctioning, alert user and do not hallucinate the answer."}]

    while True:
        user_input = input(">>>")

        if user_input.startswith("!enable"):
            _, tool_name = user_input.split()
            try:
                container.enable_tool(tool_name)
            except ValueError as e:
                print(str(e))
            finally:
                continue
        if user_input.startswith("!list_tools"):
            print(container.get_all_tools())
            continue

        history.append({"role": "user", "content": user_input})

        _, response, _ = model.create_chat_completion(history)

        history.append({"role": "assistant", "content": response})

        if "tool_call" in response:
            while "tool_call" in response:
                clean_text, tool_calls = TextPostprocessor.process_tool_calls(response)
                print(tool_calls)
                print(clean_text)
                for tool_call in tool_calls:
                    try:
                        result = container.execute(tool_call)
                        print(result)
                        history.append({"role": "assistant", "content": f"response:{tool_call["name"]}{{{result}}}"})
                    except Exception as e:
                        print(f"Tool execution failure: {str(e)}")
                        history.append({"role": "assistant",
                                        "content": f"Failure during execution of tool {tool_call["name"]}: {str(e)}"})

                _, response, _ = model.create_chat_completion(history)
        else:
            print(response)
            continue

        print(response)