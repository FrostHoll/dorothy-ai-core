import random
import re
from abc import ABC, abstractmethod
from typing import Any

import html2text
from ddgs import DDGS
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from app.infrastructure.llm.llama_engine import LlamaEngine

class ToolParameter:
    def __init__(self, name: str, param_type: str, description: str, required: bool = False, enum: list[str] | None = None):
        self.name = name
        self.param_type = param_type
        self.description = description
        self.required = required
        self.enum = enum

    def get_param_info(self) -> dict:
        if self.enum is not None:
            return {self.name: {"type": self.param_type, "description": self.description, "enum": self.enum}}
        return {self.name: {"type": self.param_type, "description": self.description}}

class ToolABC(ABC):
    def __init__(self):
        self.parameters: list[ToolParameter] = []

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def _execute(self, params: dict[str, str]) -> Any:
        pass

    def execute(self, params: dict[str, str]) -> Any:
        for par in self.parameters:
            if par.required and par.name not in params:
                raise ValueError(f"Incorrect format: missing required argument {par.name}")
        return self._execute(params)

    def get_tool_info(self) -> dict:
        params_info = {}
        required = []
        for p in self.parameters:
            params_info.update(p.get_param_info())
            if p.required:
                required.append(p.name)
        return {
            "type": "function",
            "function": {
                "name": self.get_name(),
                "description": self.get_description(),
                "parameters": {
                    "type": "object",
                    "properties": params_info,
                    "required": required
                }
            }
        }

class RollNumberTool(ToolABC):
    def __init__(self):
        super().__init__()
        self.parameters = [
            ToolParameter("maxRange", "integer", "Maximum value of the range. Inclusive.")
        ]

    def get_description(self) -> str:
        return "Get random number in range from 0 to 100 by default."

    def get_name(self) -> str:
        return "roll_number"

    def _execute(self, params: dict[str, str]) -> Any:
        max_range = 100
        if "maxRange" in params:
            max_range = params["maxRange"]
        return random.randint(0, max_range)

class EpicTool(ToolABC):
    def __init__(self):
        super().__init__()
        self.parameters = [
            ToolParameter("note", "string", "Note about user, need to be saved to memory.", required=True)
        ]

    def get_name(self) -> str:
        return "note"

    def get_description(self) -> str:
        return "Use this tool to save notes about user. Notes are used to personalize conversation with user. Note every information you might use further in the conversation. Call this at any time you need it."

    def _execute(self, params: dict[str, str]) -> Any:
        print(params["note"])
        return "Note has been saved."

class WebSearchTool(ToolABC):
    def __init__(self):
        super().__init__()
        self.parameters = [
            ToolParameter("query", "string", "Query text to search.", required=True)
        ]

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
        ddgs_client = DDGS()
        results = ddgs_client.text(query, max_results=5, region="ru-ru")
        return results

    def _results_to_string(self, sources: list[dict[str, str]]) -> str:
        return "\n".join(
            f"Source {i + 1}:\n" + "\n".join(f"{k}: {v}" for k, v in src.items())
            for i, src in enumerate(sources)
        )

class GetWebpageTool(ToolABC):
    def __init__(self):
        super().__init__()
        self.parameters = [
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
                "If you need more information, but it's locked under symbols limitation, you can safely call this tool again"
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

class ToolContainer:
    def __init__(self):
        self.tools = {}

    def register_tool(self, tool: ToolABC):
        self.tools[tool.get_name()] = tool

    def execute(self, tool_call):
        tool_name = tool_call["name"]
        if tool_name in self.tools:
            tool: ToolABC = self.tools[tool_name]
            result = tool.execute(tool_call["parameters"])
            return result
        else:
            raise ValueError(f"Unable to find tool {tool_name}")

    def get_tools_info(self) -> list:
        return [tool.get_tool_info() for _, tool in self.tools.items()]

def parse_params(params: str):
    params_dict = {}
    for p in params.split(','):
        if len(p.split(':')) != 2:
            continue
        param_name, param_value = p.split(':')
        params_dict.update({param_name: param_value})
    return params_dict

def parse_custom_params(text: str) -> dict[str, str]:
    params = {}
    buffer = []
    current_key = None
    in_value = False
    in_string = False

    normalized = text.replace('<|"|>', '"')

    i = 0
    while i < len(normalized):
        char = normalized[i]

        if not in_value:
            if char == ':':
                current_key = "".join(buffer).strip()
                buffer = []
                in_value = True
                i += 1
                continue
            elif char == ',':
                i += 1
                continue
        else:
            if char == '"' and (i == 0 or normalized[i - 1] != '\\'):
                in_string = not in_string

            if char == ',' and not in_string:
                value = "".join(buffer).strip()
                if current_key:
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    params[current_key] = value
                buffer = []
                current_key = None
                in_value = False
                i += 1
                continue

        buffer.append(char)
        i += 1

    if in_value and current_key:
        value = "".join(buffer).strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        params[current_key] = value

    return params

def parse_tool_calls(response_text):
    pattern = r'<|tool_call>(.*?)<tool_call|>'
    matches = re.findall(pattern, response_text, re.DOTALL)

    tool_calls = []
    for match in matches:
        call_match = re.match(r'call:(\w+){(.*)}', match.strip())
        if call_match:
            tool_name = call_match.group(1)
            params_str = call_match.group(2)
            params = parse_custom_params(params_str)
            tool_calls.append({
                "name": tool_name,
                "parameters": params
            })
    return tool_calls

if __name__ == "__main__":
    container = ToolContainer()
    tool4 = WebSearchTool()
    tool5 = GetWebpageTool()
    container.register_tool(tool4)
    container.register_tool(tool5)

    tools_info = container.get_tools_info()

    print(tools_info)

    model = LlamaEngine(tools_info)

    history = [{"role": "system", "content": "You are an AI assistant, who can use tools. If tool is malfunctioning, alert user and do not hallucinate the answer."}]

    while True:
        user_input = input(">>>")

        history.append({"role": "user", "content": user_input})

        _, response, _ = model.create_chat_completion(history)

        history.append({"role": "assistant", "content": response})

        while "tool_call" in response:
            tool_calls = parse_tool_calls(response)
            print(tool_calls)
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