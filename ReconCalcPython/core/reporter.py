import datetime

def generate_markdown_report(results):
    lines = []
    lines.append("# Software Reconnaissance Report")
    lines.append(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    lines.append("## Common Software Elements (CELEMS)")
    lines.append(f"Total: {len(results['celems'])}")
    if results['celems']:
        lines.append("\n```")
        for elem in sorted(results['celems']):
            lines.append(elem)
        lines.append("```\n")
    else:
        lines.append("None found.\n")

    for f in results['features']:
        lines.append(f"## Feature: {f['name']}")
        
        sections = [
            ("Unique Elements (UELEMS)", f['uelems']),
            ("Relevant Elements (RELEMS)", f['relems']),
            ("Indispensably Involved (IIELEMS)", f['iielems']),
            ("Involved Elements (IELEMS)", f['ielems']),
            ("Shared Elements (SHARED)", f['shared'])
        ]
        
        for title, elements in sections:
            lines.append(f"### {title}")
            lines.append(f"Count: {len(elements)}")
            if elements:
                lines.append("\n```")
                for elem in sorted(elements):
                    lines.append(elem)
                lines.append("```\n")
            else:
                lines.append("None found.\n")
                
    return "\n".join(lines)

def generate_html_report(results):
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reconnaissance Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1000px; margin: 0 auto; padding: 20px; background-color: #f4f7f6; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        .header {{ border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-bottom: 30px; }}
        .feature-card {{ background: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 30px; padding: 20px; }}
        .section-title {{ font-weight: bold; margin-top: 20px; color: #2980b9; border-left: 4px solid #3498db; padding-left: 10px; }}
        .count {{ font-size: 0.9em; color: #7f8c8d; font-style: italic; }}
        pre {{ background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px; padding: 10px; overflow-x: auto; max-height: 300px; font-size: 0.85em; }}
        .celems {{ background: #e8f4fd; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Software Reconnaissance Report</h1>
        <p>Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="feature-card celems">
        <h2>Common Software Elements (CELEMS)</h2>
        <p class="count">Total procedures: {len(results['celems'])}</p>
        <pre>{"\\n".join(sorted(results['celems'])) if results['celems'] else "None found."}</pre>
    </div>
"""

    for f in results['features']:
        html += f"""
    <div class="feature-card">
        <h2>Feature: {f['name']}</h2>
        
        <div class="section-title">Unique Elements (UELEMS) <span class="count">({len(f['uelems'])})</span></div>
        <pre>{"\\n".join(sorted(f['uelems'])) if f['uelems'] else "None found."}</pre>

        <div class="section-title">Relevant Elements (RELEMS) <span class="count">({len(f['relems'])})</span></div>
        <pre>{"\\n".join(sorted(f['relems'])) if f['relems'] else "None found."}</pre>

        <div class="section-title">Indispensably Involved (IIELEMS) <span class="count">({len(f['iielems'])})</span></div>
        <pre>{"\\n".join(sorted(f['iielems'])) if f['iielems'] else "None found."}</pre>

        <div class="section-title">Involved Elements (IELEMS) <span class="count">({len(f['ielems'])})</span></div>
        <pre>{"\\n".join(sorted(f['ielems'])) if f['ielems'] else "None found."}</pre>

        <div class="section-title">Shared Elements (SHARED) <span class="count">({len(f['shared'])})</span></div>
        <pre>{"\\n".join(sorted(f['shared'])) if f['shared'] else "None found."}</pre>
    </div>
"""

    html += """
</body>
</html>
"""
    return html
