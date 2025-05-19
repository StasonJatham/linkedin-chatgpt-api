from pathlib import Path
from jinja2 import Environment, FileSystemLoader

PROMPT_DIR = Path("../prompts")
env = Environment(
    loader=FileSystemLoader(PROMPT_DIR),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)


def build_prompt(template_name: str, **context) -> str:
    """
    Lädt das Template template_name aus PROMPT_DIR und füllt es
    mit den Schlüssel-Wert-Paaren aus context.
    """
    tmpl = env.get_template(template_name)
    return tmpl.render(**context)


def build_cve_to_wordpress(cve: str) -> str:
    return build_prompt("cve_to_wp.txt", INPUT=cve)


def build_blog_to_linkedin(blog: str) -> str:
    return build_prompt("linkedin_post.txt", INPUT=blog)


if __name__ == "__main__":
    print(build_cve_to_wordpress("CVE-2025-1234"))
    print(build_blog_to_linkedin("So schreibst du bessere LinkedIn-Posts"))

# build_cve_to_wordpress
# blog = send_to_gpt
# build_blog_to_linkedin(blog)
# linkedin = send_to_gpt
# publish_wp
# publish_linkedin
