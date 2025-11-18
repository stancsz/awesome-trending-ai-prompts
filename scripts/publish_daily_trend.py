from trending_utils import build_readme_section, collect_recent_prompts, update_readme


def publish_trends() -> None:
    trending_data = collect_recent_prompts()
    section = build_readme_section(trending_data)
    update_readme(section)
    print("Trending section refreshed using the most recent rows from each provider CSV.")


if __name__ == "__main__":
    publish_trends()
