import re

from app.infrastructure.tools.tool_container import ToolContainer


class TextPostprocessor:
    tool_container: ToolContainer

    @staticmethod
    def process_tool_calls(response_text):
        pattern = r'<\|tool_call>(.*?)<tool_call\|>'

        tool_calls = []

        def replacer(match):
            full_match = match.group(0)
            content = match.group(1).strip()

            call_match = re.match(r'call:(\w+){(.*)}', content)

            if call_match:
                tool_name = call_match.group(1)
                params_str = call_match.group(2)

                params = TextPostprocessor._parse_custom_params(params_str)

                tool_calls.append({
                    "name": tool_name,
                    "parameters": params
                })

                return TextPostprocessor.tool_container.get_tool_call_display_text(tool_name, params)

            return full_match

        clean_text = re.sub(pattern, replacer, response_text, flags=re.DOTALL)

        return clean_text, tool_calls

    @staticmethod
    def parse_tool_calls(response_text):
        pattern = r'<|tool_call>(.*?)<tool_call|>'
        matches = re.findall(pattern, response_text, re.DOTALL)

        tool_calls = []
        for match in matches:
            call_match = re.match(r'call:(\w+){(.*)}', match.strip())
            if call_match:
                tool_name = call_match.group(1)
                params_str = call_match.group(2)
                params = TextPostprocessor._parse_custom_params(params_str)
                tool_calls.append({
                    "name": tool_name,
                    "parameters": params
                })
        return tool_calls

    @staticmethod
    def _parse_custom_params(text: str) -> dict[str | None, str]:
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