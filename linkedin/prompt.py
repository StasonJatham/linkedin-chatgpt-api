from pathlib import Path


PROMPT_DIR = Path("../prompts")

def build_cve_to_wordpress(cve: str) -> str:
    template_path = PROMPT_DIR / "cve_to_wp.txt"
    raw = template_path.read_text(encoding="utf-8")
    filled = raw.replace("{{INPUT}}", cve)
    return filled


def build_blog_to_linkedin(blog: str) -> str:
    template_path = PROMPT_DIR / "linkedin_post.txt"
    raw = template_path.read_text(encoding="utf-8")
    filled = raw.replace("{{INPUT}}", blog)
    return filled

# build_cve_to_wordpress
# blog = send_to_gpt
# build_blog_to_linkedin(blog)
# linkedin = send_to_gpt
# publish_wp
# publish_linkedin