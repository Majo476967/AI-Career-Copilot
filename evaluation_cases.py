evaluation_cases = [
    {
        "name": "AI产品经理-Agent弱",
        "jd": """
招聘AI产品经理实习生。

岗位要求：
1. 熟悉大模型应用
2. 有Agent产品经验
3. 熟悉Prompt Engineering
4. 有产品需求分析能力
5. 掌握Python
6. 有SQL基础优先
""",
        "user_profile": """
软件工程专业大三学生。
掌握Python、Prompt Engineering。
做过RAG知识库项目，使用LangChain、FAISS、Embedding和豆包大模型。
有AI产品经理实习经历，参与需求分析、竞品调研和产品流程设计。
目前Agent只有基础Tool Calling实践，SQL基础薄弱。
""",
        "expected_top_priority": "Agent"
    },

    {
        "name": "后端岗位-SQL弱",
        "jd": """
招聘后端开发实习生。

岗位要求：
1. 具备扎实的数据结构与算法基础
2. 熟练掌握Python
3. 熟悉MySQL及基础SQL
4. 具备良好的编码能力
5. 了解计算机网络和操作系统基础
6. 有后端项目开发经验优先
""",
        "user_profile": """
软件工程专业大三学生。
掌握Python，有AI项目开发实践。
SQL基础较薄弱。
有一定编码经验，但没有明确后端项目经历。
""",
        "expected_top_priority": "SQL"
    },

    {
        "name": "数据分析岗位-Python弱",
        "jd": """
招聘数据分析实习生。

岗位要求：
1. 熟练掌握SQL
2. 熟悉Python数据处理
3. 掌握Excel
4. 具备数据分析和指标拆解能力
5. 有数据分析项目经验优先
""",
        "user_profile": """
SQL基础较好，能够完成常见查询。
Excel使用熟练。
有基础数据分析经验。
Python数据处理能力较弱。
""",
        "expected_top_priority": "Python"
    },

    {
        "name": "产品岗位-数据能力弱",
        "jd": """
招聘产品经理实习生。

岗位要求：
1. 具备用户需求分析能力
2. 能够完成产品流程和PRD设计
3. 具备基础数据分析能力
4. 熟悉常见产品指标
5. 有互联网产品实习经验优先
""",
        "user_profile": """
有产品经理实习经历。
参与过需求分析、竞品分析、产品流程设计和原型设计。
数据分析和产品指标能力较弱。
""",
        "expected_top_priority": "数据分析"
    },

    {
        "name": "AI产品岗位-Agent和LLM较强",
        "jd": """
招聘AI产品经理实习生。

岗位要求：
1. 熟悉LLM应用
2. 有Agent实践经验
3. 有AI产品设计能力
4. 具备数据分析意识
5. 有Evaluation经验优先
""",
        "user_profile": """
做过RAG项目和Multi-Tool Agent项目。
熟悉Prompt、LangChain、Embedding和LLM API调用。
有AI产品经理实习经历。
数据分析能力一般，Evaluation基础较弱。
""",
        "expected_top_priority": "数据分析或Evaluation"
    }
]