"""Explicit vocabulary; no model calls and no silent loss of unknown names."""
import unicodedata
import re

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


def normalize_alias(name):
    cleaned = clean_name(name)
    return _LOOKUP.get(key(cleaned), cleaned)


def normalize_capability(name):
    cleaned = clean_name(name)
    exact = _LOOKUP.get(key(cleaned))
    if exact:
        return exact
    # Latin boundaries avoid turning NoSQL / Pythonic into an unrelated capability.
    sql = bool(re.search(r"(?<![a-z])(?:sql|mysql|postgresql)(?![a-z])", cleaned, re.I)) or any(
        term in cleaned for term in ("数据库查询", "查询业务数据"))
    python = bool(re.search(r"(?<![a-z])python(?![a-z])", cleaned, re.I))
    research = any(term in cleaned for term in ("用户研究", "用户调研", "访谈", "问卷"))
    # Distinct explicit tools/domains in one name are ambiguous; do not silently drop one.
    if sum((sql, python, research)) > 1:
        return cleaned
    if sql:
        return "SQL"
    if python:
        return "Programming"
    if research:
        return "User Research"
    if any(term in cleaned for term in ("数据分析", "指标拆解", "指标变化", "业务指标")):
        return "Data Analysis"
    return cleaned


def calibrate_required_level(value, evidence):
    """JD-only calibration. Zero is an unresolved requirement, never user evidence.

    Explicit affirmative source language overrides model level. An existing positive
    level without a covered language pattern remains an analyzer inference.
    """
    if type(value) is not int or not 0 <= value <= 4:
        raise ValueError("岗位要求等级必须是 0～4 的整数；0 仅表示岗位未明确等级。")
    levels = []
    for excerpt in evidence.splitlines():
        # Exclude negated clauses, e.g. 不要求项目经验, rather than promoting them.
        clauses = [c for c in re.split(r"[，,；;。]", excerpt) if c.strip()]
        affirmative = "，".join(c for c in clauses if not re.search(r"不要求|无需|不需要|不必|无须", c))
        if not affirmative:
            levels.append(0)
        elif re.search(r"复杂系统设计|深度优化|规模化.{0,8}经验|专家级|design complex systems|deep optimiz", affirmative, re.I):
            levels.append(4)
        elif re.search(r"(?:真实|实际).{0,16}项目.{0,8}经验|项目[/／或及和、]*实习经验|项目经验|实习经验|业务落地|实际负责过|production experience|internship experience", affirmative, re.I):
            levels.append(3)
        elif re.search(r"能够(?:使用|用)|能(?:使用|用)|掌握.{0,12}(?:工具|SQL|Python)|(?:完成|进行|实现).{0,24}(?:练习|查询|分析|实现)|使用.{0,24}(?:查询|分析|实现)|can use|implement", affirmative, re.I):
            levels.append(2)
        elif re.search(r"了解|理解|熟悉.{0,12}(?:基础|概念)|understand|basic concepts", affirmative, re.I):
            levels.append(1)
        else:
            levels.append(value)
    return max(levels, default=0)


def normalize_jd_requirement(item):
    """Read projection also fixes legacy stored JD JSON without rewriting history."""
    result = dict(item)
    result["name"] = normalize_capability(item["name"])
    result["raw_names"] = list(dict.fromkeys(item.get("raw_names", [item["name"]])))
    result["required_level"] = calibrate_required_level(item["required_level"], item["evidence"])
    result["requirement_depth_unknown"] = result["required_level"] == 0
    return result


# Only explicit names, not fuzzy descriptions such as 数据能力 or 有分析能力.
EXPLICIT_RESUME_TERMS = ("SQL", "数据库查询", "MySQL", "Python", "Programming",
    "数据分析", "业务指标", "Data Analysis", "用户研究", "用户调研", "User Research",
    "Agent", "智能体", "RAG", "检索增强", "Evaluation", "评测")


def explicit_resume_capabilities(source):
    """Detect coverage omissions only. Never infer a level or add a capability."""
    source = unicodedata.normalize("NFKC", source)
    found = set()
    for term in EXPLICIT_RESUME_TERMS:
        pattern = re.escape(term)
        if term.isascii():
            pattern = r"(?<![a-z0-9_])" + pattern.replace(r"\ ", r"\s+") + r"(?![a-z0-9_])"
        if re.search(pattern, source, re.I):
            found.add(normalize_capability(term))
    return found



def missing_resume_capabilities(source, present, ignored=()):
    """Explain explicit omissions using exact original sentences, without a level."""
    missing = explicit_resume_capabilities(source) - set(present) - set(ignored)
    rows = []
    snippets = [m.group().strip() for m in re.finditer(r"[^。！？\n]+[。！？]?", source) if m.group().strip()]
    for name in sorted(missing):
        evidence = [snippet for snippet in snippets if name in explicit_resume_capabilities(snippet)]
        terms = []
        for term in EXPLICIT_RESUME_TERMS:
            pattern = re.escape(term)
            if term.isascii():
                pattern = r"(?<![a-z0-9_])" + pattern.replace(r"\ ", r"\s+") + r"(?![a-z0-9_])"
            if normalize_capability(term) == name and re.search(pattern, unicodedata.normalize("NFKC", source), re.I):
                terms.append(term)
        rows.append({"canonical_name": name, "matched_resume_terms": terms, "evidence_snippets": evidence})
    return rows
