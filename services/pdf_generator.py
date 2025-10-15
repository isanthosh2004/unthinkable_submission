"""
PDF Generator Service for Code Review Assistant
Handles generation of PDF reports from markdown content
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import re
from io import BytesIO
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import markdown
from markdown.extensions import codehilite, fenced_code


class PDFGenerator:
    """Service for generating PDF reports from code review content"""

    def __init__(self, reports_dir: str = "reports"):
        """
        Initialize PDF generator

        Args:
            reports_dir: Directory to store generated PDF files
        """
        self.reports_dir = reports_dir
        self._ensure_reports_dir()

        # Initialize styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _ensure_reports_dir(self):
        """Ensure reports directory exists"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the PDF"""
        # Title style
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Title"],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue,
            )
        )

        # Heading styles
        self.styles.add(
            ParagraphStyle(
                name="CustomHeading1",
                parent=self.styles["Heading1"],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=12,
                textColor=colors.darkblue,
                borderWidth=1,
                borderColor=colors.lightgrey,
                borderPadding=5,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="CustomHeading2",
                parent=self.styles["Heading2"],
                fontSize=14,
                spaceAfter=8,
                spaceBefore=8,
                textColor=colors.darkblue,
            )
        )

        # Code style
        self.styles.add(
            ParagraphStyle(
                name="CodeStyle",
                parent=self.styles["Normal"],
                fontSize=9,
                fontName="Courier",
                leftIndent=20,
                rightIndent=20,
                spaceAfter=6,
                spaceBefore=6,
                backColor=colors.lightgrey,
                borderWidth=1,
                borderColor=colors.grey,
                borderPadding=5,
            )
        )

        # Metadata style
        self.styles.add(
            ParagraphStyle(
                name="MetadataStyle",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.darkgrey,
                alignment=TA_CENTER,
            )
        )

    # -------------------------------------------------------------------------
    # 📈 Complexity Graph Generation
    # -------------------------------------------------------------------------
    def generate_complexity_graph(self, file_name: str) -> BytesIO:
        """
        Generate a complexity graph (Time vs Space Complexity)
        Args:
            file_name: The name of the code file
        Returns:
            BytesIO buffer containing the image
        """
        complexities = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n²)"]
        n_values = [1, 2, 3, 4, 5]
        time_values = [t ** 2 for t in n_values]  # Example time complexity
        space_values = [t for t in n_values]  # Example space complexity

        plt.figure(figsize=(4, 3))
        plt.plot(n_values, time_values, label="Time Complexity (O(n²))", marker="o")
        plt.plot(n_values, space_values, label="Space Complexity (O(n))", marker="s")
        plt.xlabel("Input Size (n)")
        plt.ylabel("Growth Rate")
        plt.legend()
        plt.title(f"Complexity Graph: {file_name}")
        plt.grid(True)

        # Save plot to a BytesIO buffer
        img_buf = BytesIO()
        plt.tight_layout()
        plt.savefig(img_buf, format="png")
        plt.close()
        img_buf.seek(0)
        return img_buf

    # -------------------------------------------------------------------------
    # 🧾 PDF Generation
    # -------------------------------------------------------------------------
    def generate_report(
        self, file_contents: List[Dict[str, Any]], review_content: str, metadata: Dict[str, Any]
    ) -> str:
        """
        Generate a PDF report from code review content

        Args:
            file_contents: List of file dictionaries with content
            review_content: Markdown formatted review content
            metadata: Additional metadata about the review

        Returns:
            Path to the generated PDF file
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"code_review_report_{timestamp}.pdf"
            filepath = os.path.join(self.reports_dir, filename)

            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )

            # Build story (content)
            story = []

            # Add title
            story.append(Paragraph("Code Review Report", self.styles["CustomTitle"]))
            story.append(Spacer(1, 20))

            # Add metadata
            story.extend(self._add_metadata_section(metadata, file_contents))
            story.append(Spacer(1, 20))

            # Add file contents section
            story.extend(self._add_file_contents_section(file_contents))
            story.append(PageBreak())

            # Add review content
            story.extend(self._parse_markdown_content(review_content))

            # Build PDF
            doc.build(story)
            return filepath

        except Exception as e:
            raise Exception(f"Failed to generate PDF report: {str(e)}")

    # -------------------------------------------------------------------------
    # 📄 Metadata Section
    # -------------------------------------------------------------------------
    def _add_metadata_section(
        self, metadata: Dict[str, Any], file_contents: List[Dict[str, Any]]
    ) -> List:
        """Add metadata section to PDF"""
        story = []

        # Create metadata table
        metadata_data = [
            ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Files Reviewed", str(len(file_contents))],
            ["Model Used", metadata.get("model_used", "N/A")],
            ["Total Tokens", str(metadata.get("total_tokens", "N/A"))],
        ]

        metadata_table = Table(metadata_data, colWidths=[2 * inch, 3 * inch])
        metadata_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ("BACKGROUND", (0, 0), (0, -1), colors.grey),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.whitesmoke),
                ]
            )
        )

        story.append(Paragraph("Report Information", self.styles["CustomHeading1"]))
        story.append(metadata_table)
        story.append(Spacer(1, 12))

        return story

    # -------------------------------------------------------------------------
    # 📜 File Contents Section with Complexity Graph
    # -------------------------------------------------------------------------
    def _add_file_contents_section(self, file_contents: List[Dict[str, Any]]) -> List:
        """Add file contents section to PDF"""
        story = []
        story.append(Paragraph("Code Files Reviewed", self.styles["CustomHeading1"]))

        for i, file_info in enumerate(file_contents, 1):
            # File header
            story.append(
                Paragraph(f"File {i}: {file_info['name']}", self.styles["CustomHeading2"])
            )

            # File metadata
            metadata_text = f"Size: {file_info['size']:,} bytes | Type: {file_info['type']}"
            story.append(Paragraph(metadata_text, self.styles["MetadataStyle"]))
            story.append(Spacer(1, 6))

            # File content (truncated if too long)
            content = file_info["content"]
            if len(content) > 2000:
                content = content[:2000] + "\n\n... [Content truncated for PDF display] ..."

            # Add code lines
            lines = content.split("\n")
            for line in lines[:50]:
                if line.strip():
                    story.append(Paragraph(line, self.styles["CodeStyle"]))
                else:
                    story.append(Spacer(1, 6))

            if len(lines) > 50:
                story.append(
                    Paragraph("... [Additional lines truncated] ...", self.styles["CodeStyle"])
                )

            story.append(Spacer(1, 12))

            # Add complexity graph for this file
            story.append(
                Paragraph(
                    f"Complexity Graph for {file_info['name']}", self.styles["CustomHeading2"]
                )
            )
            graph_img = self.generate_complexity_graph(file_info["name"])
            story.append(Image(graph_img, width=400, height=300))
            story.append(Spacer(1, 20))

        return story

    # -------------------------------------------------------------------------
    # 🧩 Markdown Parsing Section
    # -------------------------------------------------------------------------
    def _parse_markdown_content(self, markdown_content: str) -> List:
        """Parse markdown content and convert to PDF elements"""
        story = []

        html = markdown.markdown(
            markdown_content, extensions=["codehilite", "fenced_code", "tables"]
        )

        sections = self._split_by_headers(markdown_content)

        for section in sections:
            if section.strip():
                story.extend(self._process_section(section))

        return story

    def _split_by_headers(self, content: str) -> List[str]:
        """Split markdown content by headers"""
        sections = re.split(r"\n(#{2,3})\s+", content)

        result = []
        for i in range(0, len(sections), 2):
            if i + 1 < len(sections):
                header = sections[i].strip()
                content_part = sections[i + 1].strip() if i + 1 < len(sections) else ""
                if header and content_part:
                    result.append(f"{header}\n{content_part}")
            elif sections[i].strip():
                result.append(sections[i].strip())

        return result

    def _process_section(self, section: str) -> List:
        """Process a markdown section and convert to PDF elements"""
        story = []
        lines = section.split("\n")

        current_paragraph = []

        for line in lines:
            line = line.strip()

            if not line:
                if current_paragraph:
                    story.append(Paragraph(" ".join(current_paragraph), self.styles["Normal"]))
                    current_paragraph = []
                story.append(Spacer(1, 6))
                continue

            if line.startswith("##"):
                if current_paragraph:
                    story.append(Paragraph(" ".join(current_paragraph), self.styles["Normal"]))
                    current_paragraph = []

                header_text = line.replace("#", "").strip()
                story.append(Paragraph(header_text, self.styles["CustomHeading1"]))
                story.append(Spacer(1, 6))

            elif line.startswith("###"):
                if current_paragraph:
                    story.append(Paragraph(" ".join(current_paragraph), self.styles["Normal"]))
                    current_paragraph = []

                header_text = line.replace("#", "").strip()
                story.append(Paragraph(header_text, self.styles["CustomHeading2"]))
                story.append(Spacer(1, 4))

            elif line.startswith("```"):
                if current_paragraph:
                    story.append(Paragraph(" ".join(current_paragraph), self.styles["Normal"]))
                    current_paragraph = []
                continue

            elif line.startswith("- ") or line.startswith("* "):
                if current_paragraph:
                    story.append(Paragraph(" ".join(current_paragraph), self.styles["Normal"]))
                    current_paragraph = []

                bullet_text = line[2:].strip()
                story.append(Paragraph(f"• {bullet_text}", self.styles["Normal"]))

            else:
                current_paragraph.append(line)

        if current_paragraph:
            story.append(Paragraph(" ".join(current_paragraph), self.styles["Normal"]))

        return story

    # -------------------------------------------------------------------------
    # 📁 PDF Report Info
    # -------------------------------------------------------------------------
    def get_report_info(self, filepath: str) -> Dict[str, Any]:
        """
        Get information about a generated report

        Args:
            filepath: Path to the PDF file

        Returns:
            Dictionary with report information
        """
        try:
            if not os.path.exists(filepath):
                return {"exists": False}

            stat = os.stat(filepath)
            return {
                "exists": True,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
        except Exception as e:
            return {"exists": False, "error": str(e)}

