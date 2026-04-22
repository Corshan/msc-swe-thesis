import os
import argparse
from core.parser import ControlFile, load_profile, convert_ppf_to_pro
from core.recon_calc import ReconAnalyzer
from core.reporter import generate_markdown_report, generate_html_report

def main():
    parser = argparse.ArgumentParser(description="ReconCalc Python - Software Reconnaissance Tool")
    parser.add_argument("control_file", help="Path to the .ctl control file")
    parser.add_argument("--output", "-o", default="report", help="Output base name (default: report)")
    parser.add_argument("--format", "-f", choices=["html", "md", "both"], default="both", help="Output format")
    
    args = parser.parse_args()

    if not os.path.exists(args.control_file):
        print(f"Error: Control file {args.control_file} not found.")
        return

    print(f"Loading control file: {args.control_file}")
    ctl = ControlFile(args.control_file)
    
    base_dir = os.path.dirname(args.control_file)

    def profile_loader(filename):
        path = os.path.join(base_dir, filename)
        if not os.path.exists(path):
            print(f"Warning: Profile {path} not found.")
            return set()
        
        if ctl.format == 'ppf':
            return convert_ppf_to_pro(path)
        else:
            return load_profile(path)

    analyzer = ReconAnalyzer(ctl.features, ctl.testcases, ctl.mapping, profile_loader)
    print("Performing analysis...")
    results = analyzer.analyze_all()

    if args.format in ["md", "both"]:
        md_report = generate_markdown_report(results)
        with open(f"{args.output}.md", "w") as f:
            f.write(md_report)
        print(f"Markdown report saved to {args.output}.md")

    if args.format in ["html", "both"]:
        html_report = generate_html_report(results)
        with open(f"{args.output}.html", "w") as f:
            f.write(html_report)
        print(f"HTML report saved to {args.output}.html")

    print("Finished.")

if __name__ == "__main__":
    main()
