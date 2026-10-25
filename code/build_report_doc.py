import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

FIGURE_MAPPINGS = {
    1: [
        ("Figure 1.1-1: PostgreSQL 18.6 connection and Africa/Kigali timezone configuration",
         "screenshots/database timezone.png",
         "psql connection to database 'mobile_money' confirming PostgreSQL 18.6 and session timezone 'Africa/Kigali'."),
        ("Figure 1.1-2: PostgreSQL dedicated memory configuration (shared_buffers and work_mem)",
         "screenshots/shared buffers informations.png",
         "PostgreSQL settings verification showing shared_buffers = 4GB and work_mem = 64MB.")
    ],
    2: [
        ("Figure 1.1-3: Neo4j Desktop DBMS 2026.05.0 components and runtime environment",
         "screenshots/Neo4j  db compents and version .png",
         "Neo4j DBMS components output confirming Neo4j Kernel 2026.05.0, Cypher 5.25, and OpenJDK 21."),
        ("Figure 1.1-4: Neo4j database status and service instances",
         "screenshots/Neo4j  databases.png",
         "Neo4j SHOW DATABASES command confirming default database 'neo4j' online.")
    ],
    3: [
        ("Figure 1.2-1: Synthetic generator schema and field types inspection",
         "screenshots/field and data info ().png",
         "Inspection of dataset_info() schema showing 5 synthetic data streams."),
        ("Figure 1.2-2: Sample 10 customer records from the generator",
         "screenshots/10  customers.png",
         "First 10 generated customer records with customer_id and region."),
        ("Figure 1.2-3: Sample 10 transfer records from the generator",
         "screenshots/10 transfers.png",
         "First 10 generated transfer records with transfer_id, sender_id, receiver_id, and amount.")
    ],
    4: [
        ("Figure 1.2-4: Execution of capture.py streaming 20,993,500 records to CSV",
         "screenshots/caputing datas using capture file.png",
         "Execution of capture.py writing 20,993,500 records to CSV in 122.7 seconds."),
        ("Figure 1.2-5: Complete audit summary JSON output (capture_audit.json)",
         "screenshots/capture_audit.json.png",
         "Content of capture_audit.json verifying exact stream record counts and total volume.")
    ],
    5: [
        ("Figure 2.1-1: Relational table schema definitions in pgAdmin",
         "screenshots/tables schema.png",
         "pgAdmin 4 interface confirming creation of the five tables in mobile_money database."),
        ("Figure 2.1-2: PostgreSQL table schema and constraints in psql console",
         "screenshots/chema in terminal .png",
         "psql console output verifying table definitions, column types, and primary keys.")
    ],
    6: [
        ("Figure 2.2-1: PostgreSQL verification: Row counts for all five tables",
         "screenshots/verfication Row counts.png",
         "Verification query confirming 20,003,300 transfers, 248,000 accounts, and 228,000 customers."),
        ("Figure 2.2-2: PostgreSQL verification: Account role distribution",
         "screenshots/verfication Accounts Roles.png",
         "Verification query showing 240,000 person, 6,000 merchant, and 2,000 agent accounts."),
        ("Figure 2.2-3: PostgreSQL verification: Transfer count, volume, and date bounds",
         "screenshots/verfication Transfers.png",
         "Verification query confirming total volume of 231,482,327,870 RWF across September 2026.")
    ],
    7: [
        ("Figure 2.2-4: PostgreSQL verification: Table storage footprint breakdown",
         "screenshots/verfication Table sizes.png",
         "Verification query showing relations and index sizes totaling 3.728 GB."),
        ("Figure 2.2-5: PostgreSQL verification: Database total on-disk size",
         "screenshots/verfication databases sizes.png",
         "Verification query pg_database_size confirming total size of 3,728 MB."),
        ("Figure 2.2-6: PostgreSQL verification: Primary keys, foreign keys, and check constraints",
         "screenshots/verfication Constraints.png",
         "Verification query confirming all primary keys, foreign keys, and check constraints validated.")
    ],
    8: [
        ("Figure 3.1-1: Conceptual property graph schema drawing with mapped attributes and relationships",
         "screenshots/(accounts.customer_id, account_devices.account_id and device_id, transfers.sender_id and receiver_id) becomes a relationship (OWNS, USED_DEVICE, TRANSFER) cyper.png",
         "Graph schema diagram illustrating Customer-OWNS->Account, Account-USED_DEVICE->Device, and multi-edge Account-TRANSFER->Account.")
    ],
    9: [
        ("Figure 3.2-1: Neo4j admin import: Relationship counts and ingestion speed",
         "screenshots/OWNS 248,000, TRANSFER 20,003,300, USED_DEVICE 285,600.png",
         "Neo4j admin import output showing 20,536,900 relationships imported in 50.4 s."),
        ("Figure 3.2-2: Neo4j admin import: Node counts and import completion",
         "screenshots/nodes number.png",
         "Neo4j admin import output showing 704,600 nodes imported successfully.")
    ],
    10: [
        ("Figure 3.2-3: Neo4j constraint creation and verification (Customer, Account, Device)",
         "screenshots/Three uniqueness constraints.png",
         "SHOW CONSTRAINTS output confirming uniqueness constraints on Customer, Account, and Device IDs."),
        ("Figure 3.2-4: Neo4j range index on TRANSFER.occurred_at timestamp",
         "screenshots/A RANGE index on TRANSFER.occurred_at.png",
         "SHOW INDEXES output confirming RANGE index on TRANSFER.occurred_at is ONLINE."),
        ("Figure 3.2-5: Neo4j indexes and constraints summary list",
         "screenshots/neo4j indexes.png",
         "Listing of all active indexes and constraints in Neo4j DBMS.")
    ],
    11: [
        ("Figure 3.2-6: Neo4j verification: Total node counts across labels",
         "screenshots/neo 4j verfication  number of nodes.png",
         "Cypher verification queries confirming 704,600 total nodes (228k Customer, 248k Account, 228.6k Device)."),
        ("Figure 3.2-7: Neo4j verification: Account role distribution in graph",
         "screenshots/neo 4j verfication roles.png",
         "Cypher verification query showing 240k person, 6k merchant, and 2k agent account nodes."),
        ("Figure 3.2-8: Neo4j verification: Distinct ID checks and graph integrity",
         "screenshots/neo 4j verfication distinct IDs.png",
         "Cypher query verifying distinct count of IDs and absence of null or orphaned entities.")
    ],
    12: [
        ("Figure 3.3-1: SQL multi-table JOIN trace for Account 998 in PostgreSQL",
         "screenshots/(accounts.customer_id, account_devices.account_id and device_id, transfers.sender_id and receiver_id) becomes a relationship (OWNS, USED_DEVICE, TRANSFER).png",
         "PostgreSQL psql output executing 4-table join tracing Account 998 to its customer owner, device, and outgoing transfer.")
    ],
    13: [
        ("Figure 3.3-2: Cypher pattern MATCH trace for Account 998 in Neo4j Browser",
         "screenshots/(accounts.customer_id, account_devices.account_id and device_id, transfers.sender_id and receiver_id) becomes a relationship (OWNS, USED_DEVICE, TRANSFER) cyper.png",
         "Neo4j Browser output displaying graphical path from Customer 998 to Account 998, Device 998, and Transfer 20000001.")
    ],
    14: [
        ("Figure 5.3-1: Set C 6-transfer circular payment cycle topology diagram",
         "results/diagram_cycle_C.png",
         "Visual graph showing 6-transfer cycle originating at Account 206978 through 5 accounts returning 271,176 RWF in 200 s.")
    ],
    15: [
        ("Figure 6.1-1: Automated test suite verification: 61/61 test cases matching with 0 errors",
         "screenshots/61 cases saved, 0 mismatches or errors.png",
         "Console output of run_all.py confirming 100% agreement between PostgreSQL and Neo4j."),
        ("Figure 6.1-2: Automated test suite: Verification counts for all workloads",
         "screenshots/counts verfiations .png",
         "Verification query summary confirming all row counts and output records agree perfectly.")
    ],
    16: [
        ("Figure 6.1-3: Independent verification in pure Python without database engines",
         "screenshots/indendepend check .png",
         "Execution of independent_check.py validating device overlaps and cycle formation directly from CSV files.")
    ],
    17: [
        ("Figure 6.2-1: Performance benchmark execution: 5-run median latency across all 21 queries",
         "screenshots/all 21 cases with 5 measured runs per engine, and the medians match your console runs..png",
         "Automated benchmark console output displaying median, min, and max millisecond measurements across all 21 test queries.")
    ],
    18: [
        ("Figure 7.1-1: Concurrency stress test: 16 parallel client workers completion log",
         "screenshots/16 clients ran with 2,910 completions, errors 0, incorrect 0 and timeouts0.png",
         "Concurrency test console output recording 0 errors, 0 timeouts, and 0 incorrect results across 16 parallel clients."),
        ("Figure 7.1-2: Concurrency benchmark summary metrics and throughput results",
         "screenshots/concurrency _final .png",
         "Completed concurrency benchmark summary across 1, 4, 8, and 16 client loads.")
    ],
    19: [
        ("Figure 7.1-3: Concurrency throughput and latency scaling curves across 1, 4, 8, and 16 clients",
         "results/concurrency_plot.png",
         "Throughput (cycles/s) and p95 latency curves demonstrating Neo4j scaling to 836.6 cycles/s vs. PostgreSQL saturation at 0.91 cycles/s.")
    ],
    20: [
        ("Figure 8.1-1: Device co-location topology for Account 206978 showing loop accounts on handset 228043",
         "results/diagram_devices_C.png",
         "Bipartite network showing Account 206978 connected to handsets 228043 and 206976, highlighting loop accounts in blue.")
    ],
    21: [
        ("Figure 9.2-1: Reproducibility verification: 61 cases saved and verified",
         "screenshots/61 cases saved .png",
         "Final verification confirming all 61 cases saved with 0 mismatches."),
        ("Figure 9.2-2: Project source code file integrity and repository verification",
         "screenshots/save all python file.png",
         "Source code directory tree and SHA256 integrity verification across all scripts.")
    ]
}

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_footer_page_number(run):
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def add_formatted_text(p, text, font_name="Calibri", font_size=10.5, color_rgb=(0x22, 0x22, 0x22)):
    tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
    for tok in tokens:
        if not tok:
            continue
        run = p.add_run()
        run.font.name = font_name
        run.font.size = Pt(font_size)
        run.font.color.rgb = RGBColor(*color_rgb)
        
        if tok.startswith('**') and tok.endswith('**') and len(tok) >= 4:
            run.text = tok[2:-2]
            run.font.bold = True
        elif tok.startswith('*') and tok.endswith('*') and len(tok) >= 2:
            run.text = tok[1:-1]
            run.font.italic = True
        elif tok.startswith('`') and tok.endswith('`') and len(tok) >= 2:
            run.text = tok[1:-1]
            run.font.name = "Consolas"
            run.font.size = Pt(font_size * 0.92)
            run.font.color.rgb = RGBColor(0x90, 0x20, 0x20)
        else:
            run.text = tok

def format_row(row, is_header=False, is_even=False):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    if is_header:
        trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

    for cell in row.cells:
        if is_header:
            set_cell_background(cell, "1F4E78")
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for r in p.runs:
                    r.font.name = "Calibri"
                    r.font.size = Pt(9.5)
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        else:
            bg = "F4F6F9" if is_even else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=140, right=140)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.name = "Calibri"
                    r.font.size = Pt(9.0)
                    r.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

def build_docx(markdown_path, docx_path, base_dir=r"c:\assignement"):
    print("Initializing Document...")
    doc = docx.Document()
    
    # Page setup: Standard Letter / A4 with clean margins
    for sec in doc.sections:
        sec.top_margin = Inches(0.85)
        sec.bottom_margin = Inches(0.85)
        sec.left_margin = Inches(0.9)
        sec.right_margin = Inches(0.9)
        sec.different_first_page_header_footer = True
        
        # Configure Footer for subsequent pages
        footer = sec.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f_run1 = f_p.add_run("Advanced Big Data Analytics – Assignment II – Group report | Page ")
        f_run1.font.name = "Calibri"
        f_run1.font.size = Pt(9.0)
        f_run1.font.color.rgb = RGBColor(0x77, 0x77, 0x77)
        add_footer_page_number(f_p.add_run())

    # Read markdown
    with open(markdown_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # --- COVER PAGE ---
    # Preserving the user's manual change: "Department of information Technology"
    print("Building Cover Page (Strictly 1 Page)...")
    logo_path = os.path.join(base_dir, "report", "auca_logo.png")
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(8)
        p_logo.paragraph_format.space_after = Pt(6)
        p_logo.add_run().add_picture(logo_path, width=Inches(1.6))

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_after = Pt(2)
    r_inst = p_inst.add_run("ADVENTIST UNIVERSITY OF CENTRAL AFRICA\n")
    r_inst.font.name = "Calibri"
    r_inst.font.size = Pt(13)
    r_inst.font.bold = True
    r_inst.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)
    
    # User's edit: "Department of information Technology"
    r_dept = p_inst.add_run("Department of information Technology\n")
    r_dept.font.name = "Calibri"
    r_dept.font.size = Pt(10)
    r_dept.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    r_course = p_inst.add_run("Advanced Big Data Analytics (Master of Science in Big Data Analytics)")
    r_course.font.name = "Calibri"
    r_course.font.size = Pt(11)
    r_course.font.bold = True
    r_course.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(20)
    p_title.paragraph_format.space_after = Pt(4)
    r_asgn = p_title.add_run("Assignment II\n")
    r_asgn.font.name = "Calibri"
    r_asgn.font.size = Pt(22)
    r_asgn.font.bold = True
    r_asgn.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)

    r_topic = p_title.add_run("Mobile Money Investigations with PostgreSQL and Neo4j")
    r_topic.font.name = "Calibri"
    r_topic.font.size = Pt(16)
    r_topic.font.bold = True
    r_topic.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(4)
    p_sub.paragraph_format.space_after = Pt(20)
    r_sub = p_sub.add_run("Data Ingestion, Relational and Graph Schema Modeling, Forensic Graph Traversals,\nBenchmark Comparisons, Concurrency Stress-Testing, and Regulatory Decision Analysis for 20 Million Transactions")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(10)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

    p_grp = doc.add_paragraph()
    p_grp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_grp.paragraph_format.space_before = Pt(8)
    p_grp.paragraph_format.space_after = Pt(4)
    r_grp = p_grp.add_run("Group members")
    r_grp.font.name = "Calibri"
    r_grp.font.size = Pt(11)
    r_grp.font.bold = True
    r_grp.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)

    tbl_members = doc.add_table(rows=4, cols=4)
    tbl_members.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_members, color="B0C4DE", sz="6", val="single")

    headers = ["No.", "Full name", "Student ID", "Email"]
    widths = [Inches(0.6), Inches(2.4), Inches(1.1), Inches(2.3)]
    
    for j, h in enumerate(headers):
        cell = tbl_members.rows[0].cells[j]
        cell.width = widths[j]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j in [0, 2] else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)

    format_row(tbl_members.rows[0], is_header=True)

    members_data = [
        ("1", "Amie Marie Flora Dushimumukiza", "101405", "dushimumukiza.flora@auca.ac.rw"),
        ("2", "Kwizera Rene", "101379", "rene.kwizera@auca.ac.rw"),
        ("3", "Grace Teta", "101378", "grace.teta@auca.ac.rw")
    ]
    for i, data in enumerate(members_data, 1):
        row = tbl_members.rows[i]
        for j, val in enumerate(data):
            cell = row.cells[j]
            cell.width = widths[j]
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j in [0, 2] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
        format_row(row, is_header=False, is_even=(i % 2 == 0))

    p_lect = doc.add_paragraph()
    p_lect.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lect.paragraph_format.space_before = Pt(20)
    p_lect.paragraph_format.space_after = Pt(2)
    r_lect = p_lect.add_run("Lecturer: Temitope Oguntade")
    r_lect.font.name = "Calibri"
    r_lect.font.size = Pt(11)
    r_lect.font.bold = True
    r_lect.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_after = Pt(2)
    r_meta = p_meta.add_run("Submission Date: 25 October 2026 (Due: 26 October 2026 at 11:59 PM CAT)\nGitHub: https://github.com/KWIZERARENE/Mobile-Money-Investigations-with-PostgreSQL-and-Neo4j")
    r_meta.font.name = "Calibri"
    r_meta.font.size = Pt(9.0)
    r_meta.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    # Page Break after Cover Page
    doc.add_page_break()

    # --- TABLE OF CONTENTS (PAGE 2) ---
    # Exact user-requested specification:
    print("Building Refined Table of Contents (User Format)...")
    p_toc_hdr = doc.add_paragraph()
    p_toc_hdr.paragraph_format.space_before = Pt(10)
    p_toc_hdr.paragraph_format.space_after = Pt(10)
    r_toc_hdr = p_toc_hdr.add_run("TABLE OF CONTENTS")
    r_toc_hdr.font.name = "Calibri"
    r_toc_hdr.font.size = Pt(16)
    r_toc_hdr.font.bold = True
    r_toc_hdr.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)

    user_toc_data = [
        (True, "1 Capture the Data", "4"),
        (False, "1.1 Prepare Your Workspace", "4"),
        (False, "1.2 Build capture.py and Dataset Audit", "6"),
        (True, "2 Build PostgreSQL", "11"),
        (False, "2.1 Define the Five Tables", "11"),
        (False, "2.2 Bulk-Load, Indexing, and Verification", "15"),
        (True, "3 Build Neo4j", "21"),
        (False, "3.1 Map the Same Facts into Graph Topologies", "21"),
        (False, "3.2 Prepare CSVs and Admin Import", "22"),
        (False, "3.3 Inspect One Account in Both Models", "28"),
        (True, "4 Answer Routine Business Questions", "31"),
        (False, "4.1 Q1: Account Activity", "31"),
        (False, "4.2 Q2: Daily Activity and Month-Long Reconciliations", "32"),
        (False, "4.3 Q3: Shared Devices and Temporal Overlaps", "33"),
        (True, "5 Investigate Connected Accounts", "35"),
        (False, "5.1 Q4: Ownership and Device Networks", "35"),
        (False, "5.2 Q5: Rapid Onward Payments", "36"),
        (False, "5.3 Q6: Circular Payments", "37"),
        (False, "5.4 Q7: Shortest Transfer Connection", "39"),
        (True, "6 Check Correctness and Performance", "41"),
        (False, "6.1 Build One Comparison Program (61 Cases)", "41"),
        (False, "6.2 Time a Fixed Selection (21 Cases)", "44"),
        (False, "6.3 Execution Plans and SQL Improvement (q7_v2)", "47"),
        (True, "7 Test Concurrent Requests", "49"),
        (False, "7.1 Build a Multi-Process Load Test", "49"),
        (False, "7.2 Explain Concurrency Scaling and Saturation", "52"),
        (True, "8 Make and Defend Decisions", "54"),
        (False, "8.1 Prioritize Suspect Accounts for Regulatory Review", "58"),
        (False, "8.2 Architectural Recommendation (500 Words)", "58"),
        (False, "8.3 Individual Judgements and Technical Reflections", "59"),
        (True, "9 Submit Reproducible Work", "60"),
        (False, "9.1 Organize the Report", "60"),
        (False, "9.2 Make the Work Reproducible", "61"),
        (False, "9.3 Document Contributions", "65"),
    ]

    for is_major, title, page_str in user_toc_data:
        p_item = doc.add_paragraph()
        p_item.paragraph_format.line_spacing = 1.05
        
        if is_major:
            p_item.paragraph_format.space_before = Pt(5)
            p_item.paragraph_format.space_after = Pt(2)
            p_item.paragraph_format.left_indent = Inches(0.0)
            
            # Title
            r_t = p_item.add_run(title)
            r_t.font.name = "Calibri"
            r_t.font.size = Pt(10.5)
            r_t.font.bold = True
            r_t.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)
            
            # Dots
            dots_len = max(3, 76 - int(len(title) * 1.4))
            r_d = p_item.add_run(" " + "." * dots_len + " ")
            r_d.font.name = "Calibri"
            r_d.font.size = Pt(9.0)
            r_d.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
            
            # Page Number
            r_p = p_item.add_run(page_str)
            r_p.font.name = "Calibri"
            r_p.font.size = Pt(10.5)
            r_p.font.bold = True
            r_p.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)
        else:
            p_item.paragraph_format.space_before = Pt(1)
            p_item.paragraph_format.space_after = Pt(1.5)
            p_item.paragraph_format.left_indent = Inches(0.2)
            
            # Title
            r_t = p_item.add_run(title)
            r_t.font.name = "Calibri"
            r_t.font.size = Pt(9.5)
            r_t.font.bold = False
            r_t.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
            
            # Dots
            dots_len = max(3, 72 - int(len(title) * 1.35))
            r_d = p_item.add_run(" " + "." * dots_len + " ")
            r_d.font.name = "Calibri"
            r_d.font.size = Pt(9.0)
            r_d.font.color.rgb = RGBColor(0xAA, 0xAA, 0xAA)
            
            # Page Number
            r_p = p_item.add_run(page_str)
            r_p.font.name = "Calibri"
            r_p.font.size = Pt(9.5)
            r_p.font.bold = False
            r_p.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # Page Break after TOC
    doc.add_page_break()

    # --- EXECUTIVE SUMMARY (PAGE 3) ---
    print("Building Executive Summary...")
    h_exec = doc.add_heading(level=1)
    h_exec.paragraph_format.space_before = Pt(10)
    h_exec.paragraph_format.space_after = Pt(6)
    r = h_exec.add_run("Executive Summary")
    r.font.name = "Calibri"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)

    lines = md_text.splitlines()
    
    idx_exec = 0
    for i, l in enumerate(lines):
        if l.strip().startswith("## Executive Summary"):
            idx_exec = i
            break
            
    idx_toc = 0
    for i, l in enumerate(lines):
        if l.strip().startswith("## Table of Contents"):
            idx_toc = i
            break

    idx_sec1 = 0
    for i, l in enumerate(lines):
        if l.strip().startswith("# 1 Capture the data"):
            idx_sec1 = i
            break

    for l in lines[idx_exec+1 : idx_toc]:
        l_str = l.strip()
        if not l_str or l_str == "---":
            continue
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        add_formatted_text(p, l_str)

    # Page Break before Section 1 (starts on Page 4)
    doc.add_page_break()

    # --- PROCESS BODY LINES FROM SECTION 1 ---
    print("Parsing Report Body Sections 1 to 9...")
    body_lines = lines[idx_sec1:]
    
    in_code_block = False
    code_lines = []
    
    in_table = False
    table_lines = []
    
    placeholder_num = 0
    i = 0
    n_lines = len(body_lines)

    while i < n_lines:
        line = body_lines[i]
        stripped = line.strip()

        # Check for placeholder block start
        if stripped.startswith("```") and i + 1 < n_lines and "IMAGE PLACEHOLDER" in body_lines[i+1]:
            placeholder_num += 1
            i += 1
            while i < n_lines and not body_lines[i].strip().startswith("```"):
                i += 1
            i += 1 # skip closing ```
            
            # Embed mapped images for this placeholder
            if placeholder_num in FIGURE_MAPPINGS:
                figs = FIGURE_MAPPINGS[placeholder_num]
                for fig_title, img_rel_path, caption in figs:
                    img_full_path = os.path.join(base_dir, img_rel_path)
                    if os.path.exists(img_full_path):
                        p_img = doc.add_paragraph()
                        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p_img.paragraph_format.space_before = Pt(8)
                        p_img.paragraph_format.space_after = Pt(3)
                        p_img.paragraph_format.keep_with_next = True
                        
                        p_img.add_run().add_picture(img_full_path, width=Inches(6.0))
                        
                        p_cap = doc.add_paragraph()
                        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p_cap.paragraph_format.space_before = Pt(2)
                        p_cap.paragraph_format.space_after = Pt(12)
                        
                        r_fig = p_cap.add_run(f"{fig_title}\n")
                        r_fig.font.name = "Calibri"
                        r_fig.font.size = Pt(9.5)
                        r_fig.font.bold = True
                        r_fig.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)
                        
                        r_desc = p_cap.add_run(caption)
                        r_desc.font.name = "Calibri"
                        r_desc.font.size = Pt(9.0)
                        r_desc.font.italic = True
                        r_desc.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
                    else:
                        print(f"Warning: Image not found {img_full_path}")
            continue

        # Check for regular code block
        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_lines = []
            else:
                in_code_block = False
                if code_lines:
                    tbl_code = doc.add_table(rows=1, cols=1)
                    tbl_code.alignment = WD_TABLE_ALIGNMENT.CENTER
                    cell = tbl_code.rows[0].cells[0]
                    cell.width = Inches(6.5)
                    set_cell_background(cell, "F8F9FA")
                    set_cell_margins(cell, top=80, bottom=80, left=140, right=140)
                    
                    tcPr = cell._tc.get_or_add_tcPr()
                    bdr = parse_xml(
                        f'<w:tcBorders {nsdecls("w")}>'
                        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>'
                        f'<w:left w:val="single" w:sz="18" w:space="0" w:color="1F4E78"/>'
                        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>'
                        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>'
                        f'</w:tcBorders>'
                    )
                    tcPr.append(bdr)
                    
                    p_c = cell.paragraphs[0]
                    p_c.paragraph_format.space_before = Pt(2)
                    p_c.paragraph_format.space_after = Pt(2)
                    p_c.paragraph_format.line_spacing = 1.05
                    
                    full_code_text = "\n".join(code_lines)
                    r_code = p_c.add_run(full_code_text)
                    r_code.font.name = "Consolas"
                    r_code.font.size = Pt(8.5)
                    r_code.font.color.rgb = RGBColor(0x24, 0x29, 0x2E)
                    
                    p_after = doc.add_paragraph()
                    p_after.paragraph_format.space_before = Pt(0)
                    p_after.paragraph_format.space_after = Pt(4)
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Check for markdown table
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                in_table = True
                table_lines = [stripped]
            else:
                table_lines.append(stripped)
            i += 1
            continue
        else:
            if in_table:
                in_table = False
                rows_data = []
                for tl in table_lines:
                    cells = [c.strip() for c in tl.strip("|").split("|")]
                    if all(set(c).issubset({'-', ':', ' '}) for c in cells):
                        continue
                    rows_data.append(cells)
                    
                if rows_data:
                    n_rows = len(rows_data)
                    n_cols = max(len(r) for r in rows_data)
                    norm_rows = []
                    for r in rows_data:
                        if len(r) < n_cols:
                            r = r + [""] * (n_cols - len(r))
                        norm_rows.append(r[:n_cols])
                        
                    t_doc = doc.add_table(rows=n_rows, cols=n_cols)
                    t_doc.alignment = WD_TABLE_ALIGNMENT.CENTER
                    set_table_borders(t_doc, color="D3D3D3", sz="4", val="single")
                    
                    for r_idx, row_vals in enumerate(norm_rows):
                        table_row = t_doc.rows[r_idx]
                        is_hdr = (r_idx == 0)
                        for c_idx, val in enumerate(row_vals):
                            cell = table_row.cells[c_idx]
                            p = cell.paragraphs[0]
                            p.paragraph_format.space_before = Pt(2)
                            p.paragraph_format.space_after = Pt(2)
                            p.paragraph_format.line_spacing = 1.05
                            add_formatted_text(p, val, font_size=9.0 if not is_hdr else 9.5)
                        format_row(table_row, is_header=is_hdr, is_even=(r_idx % 2 == 0))
                        
                    p_spacer = doc.add_paragraph()
                    p_spacer.paragraph_format.space_after = Pt(4)

        # Headings
        if stripped.startswith("# "):
            h = doc.add_heading(level=1)
            h.paragraph_format.space_before = Pt(16)
            h.paragraph_format.space_after = Pt(5)
            h.paragraph_format.keep_with_next = True
            r = h.add_run(stripped[2:])
            r.font.name = "Calibri"
            r.font.size = Pt(14.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)
            i += 1
            continue

        if stripped.startswith("## "):
            h = doc.add_heading(level=2)
            h.paragraph_format.space_before = Pt(12)
            h.paragraph_format.space_after = Pt(4)
            h.paragraph_format.keep_with_next = True
            r = h.add_run(stripped[3:])
            r.font.name = "Calibri"
            r.font.size = Pt(12)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)
            i += 1
            continue

        if stripped.startswith("### "):
            h = doc.add_heading(level=3)
            h.paragraph_format.space_before = Pt(9)
            h.paragraph_format.space_after = Pt(3)
            h.paragraph_format.keep_with_next = True
            r = h.add_run(stripped[4:])
            r.font.name = "Calibri"
            r.font.size = Pt(10.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)
            i += 1
            continue

        if stripped == "---":
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3.5)
        p.paragraph_format.line_spacing = 1.15
        
        if stripped.startswith("- ") or stripped.startswith("* "):
            p.paragraph_format.left_indent = Inches(0.25)
            r_bullet = p.add_run("• ")
            r_bullet.font.name = "Calibri"
            r_bullet.font.bold = True
            r_bullet.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)
            add_formatted_text(p, stripped[2:])
        elif re.match(r"^\d+\.\s+", stripped):
            m = re.match(r"^(\d+\.)\s+(.*)", stripped)
            p.paragraph_format.left_indent = Inches(0.25)
            r_num = p.add_run(f"{m.group(1)} ")
            r_num.font.name = "Calibri"
            r_num.font.bold = True
            r_num.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)
            add_formatted_text(p, m.group(2))
        else:
            add_formatted_text(p, stripped)

        i += 1

    print(f"Saving final Word document to: {docx_path}")
    doc.save(docx_path)
    print("Document successfully created!")

if __name__ == "__main__":
    md_file = r"c:\assignement\report\Assignment_II_Group_Report.md"
    docx_file = r"c:\assignement\report\Assignment_II_Group_Report.docx"
    build_docx(md_file, docx_file)
