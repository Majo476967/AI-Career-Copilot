from langchain_core.tools import tool
from llm import get_chat_model


model = get_chat_model(temperature=0)


@tool
def analyze_jd(jd_text: str) -> str:
    """分析岗位JD，动态提取岗位核心能力和优先级。"""

    prompt = f"""
你是一名专业的岗位JD分析助手。

请严格根据下面这份JD进行分析：

{jd_text}

你的任务是：

1. 判断岗位名称
2. 提取岗位明确要求的核心能力
3. 判断每项能力的重要程度
4. 不允许套用固定岗位模板
5. JD没有要求的能力不要主动加入

请将能力分成：

- core_skills：岗位核心能力
- technical_skills：技术能力
- other_skills：其他相关能力

importance只能使用：
- high
- medium
- low

每项能力还要说明为什么这样判断。

输出必须是合法JSON，不要输出其他解释。

输出格式：

{{
    "job_title": "岗位名称",
    "core_skills": [
        {{
            "name": "能力名称",
            "importance": "high",
            "evidence": "JD中的判断依据"
        }}
    ],
    "technical_skills": [
        {{
            "name": "能力名称",
            "importance": "medium",
            "evidence": "JD中的判断依据"
        }}
    ],
    "other_skills": []
}}
"""

    response = model.invoke(prompt)

    return response.content


if __name__ == "__main__":

    jd = """
招聘后端开发实习生。

岗位要求：
1. 具备扎实的数据结构与算法基础
2. 熟练掌握Python
3. 熟悉MySQL及基础SQL
4. 具备良好的编码能力
5. 了解计算机网络和操作系统基础
6. 有后端项目开发经验优先
"""

    result = analyze_jd.invoke({
        "jd_text": jd
    })

    print(result)