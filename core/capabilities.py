"""Explicit vocabulary; no model calls and no silent loss of unknown names."""
import unicodedata

VOCABULARY = (
    "Agent", "RAG", "Evaluation", "Prompt Engineering", "SQL", "Data Analysis",
    "User Research", "Product Design", "Growth", "Commercial Analysis", "Programming",
)
ALIASES = {
    "Agent": ["智能体", "AI Agent", "Agent开发", "智能体开发"],
    "RAG": ["检索增强生成", "检索增强", "RAG开发"],
    "Evaluation": ["评测", "模型评测", "AI Evaluation", "模型评估"],
    "Prompt Engineering": ["提示词工程", "提示工程", "Prompt"],
    "SQL": ["SQL能力", "数据库查询", "MySQL查询"],
    "Data Analysis": ["数据能力", "业务数据分析", "指标分析", "数据分析", "数据分析能力"],
    "User Research": ["用户研究", "用户调研"],
    "Product Design": ["产品设计", "产品方案设计"],
    "Growth": ["增长", "用户增长"],
    "Commercial Analysis": ["商业分析", "商业化分析"],
    "Programming": ["编程", "程序设计", "编程能力", "Python", "Python编程"],
}


def clean_name(name):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("能力名称必须为非空文本。")
    return " ".join(unicodedata.normalize("NFKC", name).split())


def key(name):
    return clean_name(name).replace(" ", "").casefold()


_LOOKUP = {key(alias): canonical for canonical in VOCABULARY
           for alias in [canonical, *ALIASES[canonical]]}


def normalize_capability(name):
    cleaned = clean_name(name)
    return _LOOKUP.get(key(cleaned), cleaned)
