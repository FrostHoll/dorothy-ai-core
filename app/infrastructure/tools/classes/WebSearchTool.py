from typing import Any

from ddgs import DDGS

from app.infrastructure.tools.tool_abc import ToolABC
from app.infrastructure.tools.tool_parameter import ToolParameter


class WebSearchTool(ToolABC):
    def __init__(self):
        super().__init__()
        self._parameters = [
            ToolParameter("query", "string", "Search query. Must be clear, specific, and concise. "
                                             "Use English for better results, or Russian if the topic is region-specific.", required=True)
        ]
        self.ddgs_client = DDGS()

    def get_name(self) -> str:
        return "WebSearch"

    def get_description(self) -> str:
        return ("PURPOSE: Perform Google search and return 5 top results (title, URL, snippet/body).\n"
                "WHEN TO USE:\n"
                "- When the user asks for current information (news, exchange rates, dates, recent events)\n"
                "- When you are uncertain about your internal knowledge\n"
                "- When the user explicitly requests to search for something\n"
                "- BEFORE using GetWebpageTool — always search FIRST, then read pages\n"
                "RESTRICTIONS — DO NOT call this tool for:\n"
                "- Drugs, weapons, hacking, fraud, or any illegal activity\n"
                "- Extremism, terrorism, hate speech- Pornography or NSFW content\n")

    async def _execute(self, params: dict[str, str]) -> Any:
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
        return f"| Ищу по запросу \"{query}\"... |"