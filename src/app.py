"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer / Integrator)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import re
import sys
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()


def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_action(text: str):
    """
    Trích xuất tên tool và danh sách tham số từ chuỗi 'Action: tool_name['arg1', 'arg2']'
    """
    match = re.search(r"Action:\s*(\w+)\[(.*?)\]", text, re.DOTALL | re.IGNORECASE)
    if not match:
        return None, []
    
    tool_name = match.group(1).strip()
    raw_args = match.group(2).strip()
    
    if not raw_args:
        return tool_name, []
    
    args = [arg.strip(" '\"\t\r\n") for arg in raw_args.split(",")]
    return tool_name, args


def execute_tool(tool_name: str, args: list) -> str:
    """Thực thi tool được yêu cầu từ AVAILABLE_TOOLS"""
    if tool_name not in AVAILABLE_TOOLS:
        return f"LỖI: Công cụ '{tool_name}' không tồn tại trong hệ thống."
    
    tool_func = AVAILABLE_TOOLS[tool_name]
    try:
        return tool_func(*args)
    except Exception as e:
        return f"LỖI THỰC THI TOOL '{tool_name}': {str(e)}"


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")
    return response


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) hoàn chỉnh có Guardrails.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    history = f"Question: \"{user_query}\"\n"
    step = 0
    output = ""
    
    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")
        
        # 1. Gọi LLM sinh Thought & Action
        output = provider.generate(history, system_prompt=REACT_SYSTEM_PROMPT)
        print(output.strip())
        
        # 2. Kiểm tra câu trả lời cuối cùng (Final Answer)
        if "Final Answer:" in output:
            break
            
        # 3. Trích xuất Action và gọi Tool tương ứng
        tool_name, args = parse_action(output)
        if tool_name:
            observation = execute_tool(tool_name, args)
            print(f"👁️ Observation: {observation}")
            # Cập nhật lịch sử vòng lặp với kết quả Observation vừa thu được
            history += f"\n{output.strip()}\nObservation: {observation}\n"
        else:
            break
            
    # 4. Phanh an toàn: Giới hạn số bước lặp (Guardrail Trigger)
    if step >= MAX_ITERATIONS and "Final Answer:" not in output:
        print(f"\n🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("   💘 ĐỀ TÀI: CUPID AGENT — TRỢ LÝ GHÉP ĐÔI")
    print("==================================================")
    
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    # Chạy thử nghiệm toàn bộ 5 Test Cases
    for tc in tests:
        print("\n==================================================")
        print(f"📋 TEST CASE #{tc['id']}: [{tc['category']}]")
        print(f"❓ Câu hỏi: {tc['question']}")
        print(f"🎯 Hành vi kỳ vọng: {tc['expected_behavior']}")
        print("--------------------------------------------------")
        
        print("\n--- 🤖 DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
        run_baseline_chatbot(tc['question'], provider)
        
        print("\n--- 🧠 DEMO 2: CHẠY TRÊN REACT AGENT ---")
        run_react_agent(tc['question'], provider)
