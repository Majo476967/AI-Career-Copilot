from tools.jd_analyzer import analyze_jd


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