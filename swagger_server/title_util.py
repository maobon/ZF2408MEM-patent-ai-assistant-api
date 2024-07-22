def generate_report_title(key=None, industry=None, area=None, applicant=None):
    title_parts = []
    title_parts.append(f"一篇关于")
    if applicant:
        title_parts.append(applicant)
    if area:
        title_parts.append(f"在{area}")
    if industry:
        if "行业" not in industry:
            industry += "行业"
        title_parts.append(industry)
    if key:
        if "技术" not in key:
            key += "技术"
        title_parts.append(key)

    title_parts.append("的专利报告")

    return "".join(title_parts)