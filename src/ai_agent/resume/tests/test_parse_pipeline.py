import unittest

from ai_agent.resume.router import _parse_resume_text


class ParsePipelineTests(unittest.IsolatedAsyncioTestCase):
    async def test_parse_with_explicit_sections(self):
        text = """
项目经历
校园招聘爬虫项目 - 后端开发
2025.01 - 2025.03
使用 FastAPI 与 Selenium 构建职位抓取流程。

自我评价
具备数据抓取与接口开发经验，执行力强。
""".strip()

        result = await _parse_resume_text(text, llm_fn=None)

        self.assertGreaterEqual(len(result.experiences), 1)
        self.assertIn("爬虫", result.experiences[0].title)
        self.assertIn("执行力", result.self_description.self_evaluation)

    async def test_parse_without_headings_falls_back_to_full_text(self):
        text = """
校园招聘爬虫项目 - 后端开发
2025.01 - 2025.03
使用 FastAPI 与 Selenium 构建职位抓取流程。
我希望从事后端开发岗位，擅长问题拆解与快速学习。
""".strip()

        result = await _parse_resume_text(text, llm_fn=None)

        self.assertGreaterEqual(len(result.experiences), 1)
        self.assertTrue(
            bool(result.self_description.self_evaluation)
            or bool(result.self_description.career_objective)
            or bool(result.self_description.personal_summary)
        )

    async def test_ai_fallback_is_used_when_regex_sections_missing(self):
        text = "一段没有明显标题的简历文本。"

        async def fake_llm(_prompt: str) -> str:
            return (
                '{"experiences":[{"title":"AI解析项目","role":"开发","organization":"某公司",'
                '"period":"2025.01-2025.03","tech_stack":["Python"],"description":"完成系统开发",'
                '"tags":["后端"]}],"self_description":{"self_evaluation":"踏实认真",'
                '"career_objective":"后端开发","personal_summary":"可快速上手","tags":["后端"]}}'
            )

        result = await _parse_resume_text(text, llm_fn=fake_llm)

        self.assertEqual(result.parse_method, "ai_fallback")
        self.assertEqual(result.experiences[0].title, "AI解析项目")
        self.assertEqual(result.self_description.career_objective, "后端开发")


if __name__ == "__main__":
    unittest.main()
