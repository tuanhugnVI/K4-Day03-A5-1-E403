"""
🔌 MULTI-PROVIDER LLM ADAPTER (OpenAI, Gemini, Anthropic, OpenRouter & Offline Mock)
Hỗ trợ chuyển đổi linh hoạt giữa các nhà cung cấp AI chỉ bằng cách đổi biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho tất cả các LLM Provider"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env!"
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (GPT-4o, GPT-3.5-turbo, etc.)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env!"
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude Provider (Claude 3.5 Sonnet, Claude 3 Haiku)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "claude-3-haiku-20240307"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_anthropic_api_key_here":
            return "[Anthropic Error]: Chưa cấu hình ANTHROPIC_API_KEY trong file .env!"
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            kwargs = {
                "model": self.model_name,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                kwargs["system"] = system_prompt
                
            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            return f"[Anthropic Exception]: {str(e)}"


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter Provider (Hỗ trợ gọi mọi model qua OpenRouter API)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "google/gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return "[OpenRouter Error]: Chưa cấu hình OPENROUTER_API_KEY trong file .env!"
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[OpenRouter API Error {res.status_code}]: {res.text}"
        except Exception as e:
            return f"[OpenRouter Exception]: {str(e)}"


class MockProvider(BaseLLMProvider):
    """Offline Mock Provider cho Cupid Agent (Cho bài test không cần kết nối API)"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        text = prompt.lower()
        is_chatbot = "baseline" in system_prompt.lower() or "thông thường" in system_prompt.lower()
        
        # Test Case 1: "Ghép đôi là gì?"
        if "ghép đôi là gì" in text:
            if is_chatbot:
                return "Ghép đôi (matching) là quá trình tìm kiếm và kết nối những người có sở thích, tính cách, quan điểm sống hoặc tiêu chí phù hợp với nhau để tạo lập mối quan hệ."
            return "Thought: Đây là câu hỏi lý thuyết đơn giản, không cần sử dụng tool.\nFinal Answer: Ghép đôi (matching) là quá trình phân tích thông tin cá nhân (sở thích, tính cách, vị trí địa lý, mục tiêu mối quan hệ) để kết nối những người có mức độ tương thích cao với nhau."

        # Test Case 2: "3 lời khuyên hẹn hò"
        if "lời khuyên" in text and "hẹn hò" in text:
            if is_chatbot:
                return "3 lời khuyên khi đi hẹn hò lần đầu:\n1. Chọn không gian thoải mái, dễ nói chuyện.\n2. Lắng nghe chân thành và tôn trọng đối phương.\n3. Giữ thái độ tự tin, tự nhiên và là chính mình."
            return "Thought: Đây là câu hỏi tư vấn chung, không cần truy cứu database hay gọi tool.\nFinal Answer: 3 lời khuyên giúp buổi hẹn hò đầu tiên thành công:\n1. **Chuẩn bị tâm lý tự tin & thoải mái**: Chọn trang phục lịch sự và địa điểm phù hợp.\n2. **Lắng nghe tích cực**: Chủ động đặt câu hỏi mở và chia sẻ chân thành.\n3. **Giữ sự lịch sự & đúng giờ**: Thể hiện sự tôn trọng thời gian của đối phương."

        # Test Case 3: "Minh"
        if "minh" in text:
            if is_chatbot:
                return "Chào bạn Minh, với một người Song Tử năng động thích du lịch và nấu ăn, bạn nên tìm người có cùng sở thích. Một người phù hợp có thể là người cũng sống ở Hà Nội, có thể là Thiên Bình hoặc Bảo Bình. Điểm tương thích ước lượng khoảng 80%."
            else:
                if "observation:" not in text:
                    return "Thought: Người dùng muốn tìm đối tượng phù hợp. Trước tiên cần lấy hồ sơ chi tiết của Minh.\nAction: get_user_profile['Minh']"
                elif "hồ sơ minh:" in text and "search_partner" not in text:
                    return "Thought: Đã có profile Minh. Cần tìm ứng viên phù hợp (nghiêm túc, ở Hà Nội hoặc gần đó, hợp cung).\nAction: search_partner['Hà Nội', 'Nghiêm túc']"
                elif "tìm thấy" in text and "calculate_compatibility" not in text:
                    return "Thought: Có ứng viên phù hợp. Cần tính compatibility score để so sánh.\nAction: calculate_compatibility['Minh', 'Lan']"
                elif "điểm tương thích minh-lan" in text:
                    return "Thought: Tôi đã có đủ thông tin để đưa ra lời khuyên ghép đôi cho Minh.\nFinal Answer: Dựa trên hồ sơ của bạn, hệ thống tìm thấy các ứng viên phù hợp tại Hà Nội. Lan (24 tuổi, Bảo Bình) có điểm tương thích cao nhất: 85/100 — đặc biệt rất hợp về cung hoàng đạo (90%) và khoảng cách địa lý (100%). Gợi ý: Bạn có thể rủ Lan đi du lịch ngắn ngày để tìm hiểu thêm!"

        # Test Case 4: "An", "Bình", "Chi"
        if "an" in text and ("bình" in text or "chi" in text):
            if is_chatbot:
                return "Chào An! Dựa trên thông tin của bạn (ở TP.HCM), Chi cũng ở TP.HCM nên sẽ hợp hơn Bình (ở Đà Nẵng) do không bị trở ngại yêu xa. Điểm tương thích ước tính: Chi 85%, Bình 60%."
            else:
                if "observation:" not in text:
                    return "Thought: Cần lấy hồ sơ của An trước để biết tiêu chí so sánh.\nAction: get_user_profile['An']"
                elif "hồ sơ an:" in text and "an-bình" not in text:
                    return "Thought: Có profile An. Giờ tính điểm tương thích với Bình (Đà Nẵng).\nAction: calculate_compatibility['An', 'Bình']"
                elif "an-bình" in text and "an-chi" not in text:
                    return "Thought: An-Bình được 62/100. Tiếp tục tính với Chi (TP.HCM) để so sánh.\nAction: calculate_compatibility['An', 'Chi']"
                elif "an-chi" in text:
                    return "Thought: Đã có đủ dữ liệu so sánh. An-Chi (91/100) cao hơn hẳn An-Bình (62/100) chủ yếu do khoảng cách địa lý.\nFinal Answer: Kết quả so sánh: Chi (91/100) phù hợp với bạn hơn Bình (62/100). Dù cả hai đều khá hợp về mục tiêu và cung hoàng đạo, nhưng điểm khoảng cách địa lý của Bình rất thấp (30% do yêu xa giữa TP.HCM - Đà Nẵng). Chi ở cùng thành phố nên đạt điểm địa lý tuyệt đối (100%). Bạn nên ưu tiên tìm hiểu Chi nhé!"

        # Test Case 5: Edge Case Atlantis
        if "atlantis" in text or "alien" in text or "hack nasa" in text:
            if is_chatbot:
                return "Xin lỗi, tôi không thể tìm thấy thành phố Atlantis hay mục tiêu hack NASA trong cơ sở dữ liệu."
            else:
                if "observation:" not in text:
                    return "Thought: Cần lấy hồ sơ người dùng để tìm kiếm. Tuy nhiên tham số có vẻ bất thường.\nAction: get_user_profile['Atlantis_user']"
                elif "không tìm thấy hồ sơ" in text and "search_partner" not in text:
                    return "Thought: Hồ sơ không tồn tại. Thử tìm kiếm đối tượng theo thành phố và mục tiêu được cung cấp.\nAction: search_partner['Atlantis', 'hack NASA']"
                else:
                    return "Thought: Cả 2 tool đều báo lỗi. Thông tin đầu vào không hợp lệ (thành phố hư cấu, tuổi âm, cung hoàng đạo không tồn tại). Tôi nên thông báo cho người dùng.\nFinal Answer: Xin lỗi, tôi không thể thực hiện yêu cầu này vì các thông tin cung cấp (thành phố \"Atlantis\", tuổi -5, cung \"Alien\") không hợp lệ hoặc không tồn tại trong hệ thống. Vui lòng cung cấp thông tin thật để tôi hỗ trợ tìm kiếm đối tượng phù hợp cho bạn!"

        if is_chatbot:
            return "Tôi là Cupid Chatbot. Vui lòng đặt câu hỏi về tìm kiếm đối tượng ghép đôi."
        return "Thought: Nhận được câu hỏi từ người dùng.\nFinal Answer: Chào bạn! Tôi là Cupid Agent. Tôi có thể hỗ trợ tra cứu hồ sơ và tìm kiếm đối tượng ghép đôi phù hợp cho bạn."


def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    """Factory function tự chọn Provider từ biến môi trường LLM_PROVIDER"""
    name = (provider_name or os.getenv("LLM_PROVIDER") or "mock").lower().strip()
    
    if name == "gemini":
        return GeminiProvider()
    elif name == "openai":
        return OpenAIProvider()
    elif name == "anthropic":
        return AnthropicProvider()
    elif name == "openrouter":
        return OpenRouterProvider()
    else:
        return MockProvider()


if __name__ == "__main__":
    print("=== TEST MULTI-PROVIDER LLM ADAPTER ===")
    provider = get_llm_provider()
    print(f"✅ Provider đang dùng: {provider.__class__.__name__}")
    print(f"🤖 User Query: Hello")
    print(f"💬 Response  : {provider.generate('Hello')}")
