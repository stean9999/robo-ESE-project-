import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header on pages 2+
        if self._pageNumber > 1:
            self.drawString(54, 11 * inch - 36, "Robotics Lab ESE — TurtleBot3 Auto Nav Complete Hinglish Guide")
            self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "Exam & Viva Preparation")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 8.5 * inch - 54, 46)

        self.drawString(54, 32, "TurtleBot3 Autonomous Navigation | Complete Hinglish Notes for LAB ESE")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 54, 32, page_str)
        self.restoreState()

def build_pdf(filename="TurtleBot3_Autonomous_Navigation_Preparation_Guide.pdf"):
    pdf_path = os.path.join(r"C:\Users\hp\Desktop\LAB ESE for ROBO", filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    base_styles = getSampleStyleSheet()

    # Colors
    primary = colors.HexColor("#1e3a8a")     # Deep Blue
    secondary = colors.HexColor("#0284c7")   # Teal / Sky Blue
    accent = colors.HexColor("#0f766e")      # Dark Cyan
    dark_text = colors.HexColor("#0f172a")
    body_text = colors.HexColor("#334155")

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=28,
        textColor=primary,
        alignment=0,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=secondary,
        alignment=0,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Heading3_Custom',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=dark_text,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=body_text,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'Body_Bold',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=dark_text
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=base_styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=2,
        spaceAfter=2
    )

    q_style = ParagraphStyle(
        'Q_Style',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=accent,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    ans_style = ParagraphStyle(
        'Ans_Style',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=body_text,
        spaceAfter=6
    )

    story = []

    def make_box(content_flowables, border_color=primary, bg_color=colors.HexColor("#f8fafc")):
        t = Table([[content_flowables]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('BOX', (0,0), (-1,-1), 1, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ('LEFTPADDING', (0,0), (-1,-1), 9),
            ('RIGHTPADDING', (0,0), (-1,-1), 9),
        ]))
        return t

    # -------------------------------------------------------------
    # COVER / HEADER BANNER
    # -------------------------------------------------------------
    story.append(Paragraph("TurtleBot3 Autonomous Navigation — Complete Hinglish Guide", title_style))
    story.append(Paragraph("LAB ESE Exam Preparation: How It Works, Code Explanation & Top Viva Questions", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=primary, spaceAfter=10))

    meta_text = [
        Paragraph("<b>Subject:</b> Robotics Laboratory (LAB ESE Exam)", body_style),
        Paragraph("<b>Language:</b> Hinglish (Simple, Natural & Technical)", body_style),
        Paragraph("<b>Package:</b> <font name='Courier'>auto_nav</font> (TurtleBot3 Burger / Waffle)", body_style),
        Paragraph("<b>Target OS:</b> ROS 1 (Noetic / Melodic) on Ubuntu", body_style)
    ]
    meta_table = Table([[meta_text[0], meta_text[1]], [meta_text[2], meta_text[3]]], colWidths=[252, 252])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # CHAPTER 1: MOTIVE KYA HAI?
    # -------------------------------------------------------------
    story.append(Paragraph("1. Project ka Motive kya hai? (Kyu banaya gaya ye project?)", h1_style))
    story.append(Paragraph(
        "<b>Normal ROS me problem kya hoti hai:</b> Jab hum college lab me normal TurtleBot3 navigation sikhate hain, toh hume RViz khol kar <b>mouse se haath se do buttons click karne padte hain</b>:<br/>"
        "1. Pehle <i>'2D Pose Estimate'</i> click karke robot ko map par starting jagah batani padti hai.<br/>"
        "2. Fir <i>'2D Nav Goal'</i> par click karke destination batana padta hai.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Real Industry (Amazon / Flipkart Warehouse) me ye kyu fail ho jayega:</b> Socho agar ek warehouse me 500 autonomous mobile robots (AMRs) chal rahe hain, toh kya koi insaan baith kar 500 baar mouse se click karega? Bilkul nahi! Wahan sab kuch <b>100% fully automatic (programmatic)</b> hona chahiye bina kisi human intervention ke.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Hamare Project ka Solution:</b> Humne do custom Python scripts banayi hain jo bina mouse touch kiye pura kaam khud karti hain:<br/>"
        "• <b>Node 1 (<font name='Courier'>initial_pose.py</font>):</b> Code ke through robot ki initial location aur covariance AMCL ko bhej kar robot ko map par instant lock kar deta hai.<br/>"
        "• <b>Node 2 (<font name='Courier'>waypoint_navigator.py</font>):</b> Robot ko ek ke baad ek 4 warehouse stations (Loading Dock &rarr; Shelf &rarr; Sorting Desk &rarr; Charging Dock) par bhejta hai aur har jagah 2 second rukta hai samaan load/unload karne ke liye.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # CHAPTER 2: KAAM KAISE KARTA HAI?
    # -------------------------------------------------------------
    story.append(Paragraph("2. Ye System Kaam Kaise Karta Hai? (Architecture Explained)", h1_style))
    story.append(Paragraph(
        "Yeh poora navigation system 4 main layers me milkar kaam karta hai:",
        body_style
    ))

    arch_data = [
        [Paragraph("<b>Layer / Part</b>", body_bold), Paragraph("<b>ROS Node / Topic</b>", body_bold), Paragraph("<b>Hinglish me Asli Kaam</b>", body_bold)],
        [
            Paragraph("<b>1. Simulation Engine</b>", body_style),
            Paragraph("<font name='Courier'>Gazebo</font><br/>Topics: <font name='Courier'>/odom, /scan, /cmd_vel</font>", code_style),
            Paragraph("3D world simulator jisme robot physical world ki tarah wheels ghumata hai aur 360-degree LiDAR laser scan phekta hai.", body_style)
        ],
        [
            Paragraph("<b>2. Localization (AMCL)</b>", body_style),
            Paragraph("<font name='Courier'>amcl node</font><br/>Topic: <font name='Courier'>/initialpose</font>", code_style),
            Paragraph("Robot ko static map par dhundne ka kaam karta hai. Green particles se robot ki location estimate karta hai.", body_style)
        ],
        [
            Paragraph("<b>3. Navigation Planner</b>", body_style),
            Paragraph("<font name='Courier'>move_base</font><br/>Action: <font name='Courier'>MoveBaseAction</font>", code_style),
            Paragraph("Global Planner (A*) se poora safe rasta nikalta hai aur Local Planner (DWA) se obstacles ko bachata hua wheel velocity bhejta hai.", body_style)
        ],
        [
            Paragraph("<b>4. Hamara Custom Code</b>", body_style),
            Paragraph("<font name='Courier'>auto_nav package</font><br/>Scripts: <font name='Courier'>initial_pose.py, waypoint_navigator.py</font>", code_style),
            Paragraph("Mission Controller jo pehle localization lock karwata hai aur fir saare warehouse stations par robot ko safely drive karwata hai.", body_style)
        ]
    ]
    t_arch = Table(arch_data, colWidths=[120, 130, 254])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # CHAPTER 3: DONO PYTHON CODES KA POSTMORTEM
    # -------------------------------------------------------------
    story.append(Paragraph("3. Dono Python Nodes Ka Postmortem (Deep Code Explanation)", h1_style))

    story.append(Paragraph("A. Node 1: <font name='Courier'>initial_pose.py</font> (Automatic Localization Setting)", h2_style))
    story.append(Paragraph(
        "Is script ka kaam hai RViz ke '2D Pose Estimate' button ko code se replace karna. Yeh <font name='Courier'>PoseWithCovarianceStamped</font> message type use karke topic <font name='Courier'>/initialpose</font> par publish karta hai.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Covariance kyu di aur 36 numbers ka kya matlab hai?</b><br/>"
        "AMCL koi simple calculator nahi hai, yeh ek <b>probabilistic particle filter</b> hai. Isko sirf (x, y) coordinates dene se kaam nahi banta, isko thodi <i>uncertainty (shak/doubt)</i> deni padti hai taaki ye particles ka ghera bana sake. Isme 6x6 matrix (36 numbers) hota hai [x, y, z, roll, pitch, yaw]:",
        body_style
    ))
    story.append(Paragraph("• <b>Index 0:</b> <font name='Courier'>Var(x) = 0.25</font> &rarr; X direction me 0.5 meter ka uncertainty error (&radic;0.25 = 0.5m).", body_style))
    story.append(Paragraph("• <b>Index 7:</b> <font name='Courier'>Var(y) = 0.25</font> &rarr; Y direction me 0.5 meter ka uncertainty error (&radic;0.25 = 0.5m).", body_style))
    story.append(Paragraph("• <b>Index 35:</b> <font name='Courier'>Var(yaw) &approx; 0.0685 rad<sup>2</sup></font> &rarr; Angle me lagbhag 15 degrees ka standard deviation.", body_style))
    story.append(Paragraph("• <b>Publisher Race Condition Fix:</b> ROS me jab publisher banta hai, toh subscriber se connect hone me aadha second lagta hai. Agar hum turant publish kar denge toh message miss ho jayega! Isliye humne code me lagaya: <font name='Courier'>while pub.get_num_connections() == 0: rate.sleep()</font> taaki jab AMCL connect ho tabhi publish ho.", body_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("B. Node 2: <font name='Courier'>waypoint_navigator.py</font> (Warehouse Mission Planner)", h2_style))
    story.append(Paragraph(
        "Yeh script ek <b>Action Client</b> hai jo <font name='Courier'>move_base</font> ke Action Server se baat karta hai using <font name='Courier'>actionlib</font>. Isme 4 stations pre-defined hain:",
        body_style
    ))

    wp_data = [
        [Paragraph("<b>Station Name</b>", body_bold), Paragraph("<b>Map Coords (X, Y, Yaw)</b>", body_bold), Paragraph("<b>Simulated Task (2s Dwell Time)</b>", body_bold)],
        [Paragraph("1. Loading Dock", body_style), Paragraph("(-1.8m, -0.5m, 0.0 rad)", code_style), Paragraph("Warehouse pallets ko robot ke upar load karna", body_style)],
        [Paragraph("2. Shelf Area A", body_style), Paragraph("(0.5m, 1.5m, 1.57 rad)", code_style), Paragraph("Inventory items ko rack shelf me store karna", body_style)],
        [Paragraph("3. Sorting Desk", body_style), Paragraph("(1.8m, -1.0m, 3.14 rad)", code_style), Paragraph("Parcels ke barcodes scan aur verify karna", body_style)],
        [Paragraph("4. Charging Base", body_style), Paragraph("(-0.5m, 0.5m, -1.57 rad)", code_style), Paragraph("Battery charge hone ke liye dock hona (Mission Finish)", body_style)]
    ]
    t_wp = Table(wp_data, colWidths=[120, 160, 224])
    t_wp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_wp)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Action Client ke 3 Important Callbacks:</b>", body_bold))
    story.append(Paragraph("• <b>active_cb():</b> Jab <font name='Courier'>move_base</font> goal accept kar leta hai aur rasta plan karna shuru karta hai.", body_style))
    story.append(Paragraph("• <b>feedback_cb(feedback):</b> Robot raste me chalte hue har thodi der me apni live location <font name='Courier'>(x, y)</font> terminal me print karta rehta hai.", body_style))
    story.append(Paragraph("• <b>done_cb(status, result):</b> Jab robot station par pahunch jata hai ya rasta block hota hai. Agar <font name='Courier'>status == GoalStatus.SUCCEEDED</font> (Code 3) hai toh robot 2 second ruk kar agle station par nikalta hai.", body_style))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # CHAPTER 4: TERMINAL ME KAISE CHALANA HAI
    # -------------------------------------------------------------
    story.append(Paragraph("4. Terminal me Kaise Chalana Hai (Step-by-Step Practical Guide)", h1_style))
    story.append(Paragraph("Ubuntu Linux PC (College Lab) me 4 alag-alag terminals khol kar yeh commands sequence me chalani hain:", body_style))

    terms = [
        ("Terminal 1: Gazebo 3D World Launch Karo",
         "export TURTLEBOT3_MODEL=burger\nsource ~/catkin_ws/devel/setup.bash\nroslaunch turtlebot3_gazebo turtlebot3_world.launch",
         "Isse 3D simulator open hoga aur robot (-2.0, -0.5) par spawn ho jayega."),
        
        ("Terminal 2: AMCL, Navigation Stack aur RViz Launch Karo",
         "export TURTLEBOT3_MODEL=burger\nsource ~/catkin_ws/devel/setup.bash\nroslaunch turtlebot3_navigation turtlebot3_navigation.launch",
         "Isse 2D map, costmaps aur RViz open hoga. Shuru me green dots poore map me bikhre hue dikhenge."),
        
        ("Terminal 3: Robot ki Initial Pose Automatic Lock Karo",
         "source ~/catkin_ws/devel/setup.bash\nrosrun auto_nav initial_pose.py",
         "Yeh hamari pehli script hai. RViz me dekho: bikhre hue green dots turant robot ke upar aakar lock ho jayenge!"),
        
        ("Terminal 4: Multi-Station Warehouse Mission Shuru Karo",
         "source ~/catkin_ws/devel/setup.bash\nrosrun auto_nav waypoint_navigator.py",
         "Yeh hamari doosri script hai. Robot khud-b-khud Loading Dock -> Shelf -> Sorting Desk -> Charging Dock par jayega aur har jagah 2s pause karega!")
    ]

    for title, cmd, desc in terms:
        t_box = [
            Paragraph(f"<b>{title}</b>", h3_style),
            Paragraph(f"<font color='#0284c7'><b>Kaam kya hai:</b></font> {desc}", body_style),
            Table([[Paragraph(f"<font name='Courier'>{cmd.replace(chr(10), '<br/>')}</font>", code_style)]],
                  colWidths=[480],
                  style=[
                      ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")),
                      ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
                      ('TOPPADDING', (0,0), (-1,-1), 5),
                      ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                      ('LEFTPADDING', (0,0), (-1,-1), 8),
                      ('RIGHTPADDING', (0,0), (-1,-1), 8),
                  ])
        ]
        story.append(make_box(t_box, border_color=colors.HexColor("#cbd5e1"), bg_color=colors.HexColor("#f8fafc")))
        story.append(Spacer(1, 6))

    story.append(Paragraph(
        "<b>⚡ Shortcut (1 Command me Sab Kuch):</b> Agar 4 terminal alag-alag nahi kholne, toh Ubuntu terminal me run karo: <font name='Courier'>cd ~/catkin_ws/src/auto_nav/scripts &amp;&amp; ./run_all.sh</font> — yeh script charo steps automatically delay ke saath execute kar degi!",
        body_style
    ))
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # CHAPTER 5: TOP 15 THEORY & VIVA QUESTIONS IN HINGLISH
    # -------------------------------------------------------------
    story.append(Paragraph("5. Top 15 Lab Viva & Theory Questions (Sab Kuch Hinglish me)", h1_style))
    story.append(Paragraph("Examiner / Mam jo questions sabse zyada puchte hain, unke perfect ready-made answers:", body_style))

    viva_hinglish = [
        (
            "Q1. ROS Topic, Service aur ActionLib me kya farak hai? Navigation me ActionLib kyu use kiya?",
            "• <b>Topic:</b> Ek-tarfa (one-way) hota hai, jaise radio broadcast. Publisher bhejta hai par pata nahi chalta ki receiver ne padha ya nahi.<br/>"
            "• <b>Service:</b> Request-Response hota hai. Client request bhejta hai aur jab tak answer nahi aata tab tak code freeze (block) rehta hai. Isko beech me cancel nahi kar sakte.<br/>"
            "• <b>ActionLib (Action Client/Server):</b> Lambe tasks (jaise navigation jo 20 second le sakti hai) ke liye banaya gaya hai. Yeh <b>continuous feedback</b> deta hai ki robot kahan tak pahuncha, beech me <b>cancel/preempt</b> kiya ja sakta hai, aur goal complete hone par status code deta hai. Isliye navigation me sirf ActionLib chalta hai."
        ),
        (
            "Q2. AMCL kya hai aur yeh robot ko kaise localize karta hai?",
            "AMCL ka full form hai <b>Adaptive Monte Carlo Localization</b>. Yeh ek <b>2D Particle Filter</b> hai. Shuru me yeh map par hazaron random green dots (particles) fek deta hai. Jaise hi robot chalta hai aur LiDAR se laser scan maarta hai, AMCL real sensor data ko static map ki deewaron se match karta hai. Jo particles sahi match hote hain unki probability badh jaati hai aur galat waale delete ho jaate hain. Thodi der me saare particles robot ke exact position par aakar lock ho jaate hain."
        ),
        (
            "Q3. /initialpose topic par sirf (x, y, yaw) bhejne se kaam kyu nahi chalta? Covariance kyu zaroori hai?",
            "Kyunki AMCL koi fix calculation nahi karta, yeh ek <i>probabilistic (sambhavna par aadharit)</i> algorithm hai. Agar hum covariance nahi denge, toh AMCL ko lagega robot ka position 100% accurate hai aur wo particles ka spread (cloud) hi nahi banayega. Covariance matrix se hum AMCL ko uncertainty dete hain (<font name='Courier'>Var(x)=0.25</font> yani &plusmn;0.5m ka daayra), jisse particles us point ke aas-paas ek cluster bana kar sensor data se real position lock kar lete hain."
        ),
        (
            "Q4. move_base ke andar Global Planner aur Local Planner me kya difference hai?",
            "• <b>Global Planner (e.g., NavFn, A*, Dijkstra):</b> Poore map ka bird-eye view dekh kar shuru se aakhri tak ka sabse chhota obstacle-free rasta (global path) nikalta hai. Yeh static map par kaam karta hai.<br/>"
            "• <b>Local Planner (e.g., DWA - Dynamic Window Approach):</b> Robot ke just aage ka chhota hissa (3x3 meter) dekhta hai. Agar aage koi achanak naya obstacle (jaise koi insaan ya dabba) aa jaye, toh yeh global path ko thoda mod kar robot ke wheels ko velocity commands (<font name='Courier'>/cmd_vel</font>) bhejta hai."
        ),
        (
            "Q5. Costmap kya hota hai? Global Costmap vs Local Costmap samjhao.",
            "Costmap ek 2D grid map hota hai jisme har cell ko 0 se 254 tak ka number (cost) diya jata hai. 0 matlab free space, aur 254 matlab deewar/obstacle. Obstacle ke chaaron taraf ek <b>Inflation Radius</b> banaya jata hai taaki robot deewar se ragad khaye bina door se nikal sake.<br/>"
            "• <b>Global Costmap:</b> Poore warehouse map ka costmap hota hai long-term planning ke liye.<br/>"
            "• <b>Local Costmap:</b> Robot ke aas-paas ka chhota dynamic costmap hota hai jo live LiDAR scan se real-time update hota rehta hai."
        ),
        (
            "Q6. Angle ko Quaternion me convert kyu kiya? (qx, qy, qz, qw) kya hain?",
            "Normal 3D geometry me hum angles ko Roll, Pitch, Yaw (Euler angles) bolte hain. Par Euler angles me ek problem hoti hai jisko <b>Gimbal Lock</b> kehte hain (jab do axes align ho jaati hain toh ek degree of freedom kho jati hai). ROS internal math me Quaternions use karta hai jo 4 numbers <font name='Courier'>(x, y, z, w)</font> hote hain. 2D ground robot ke liye sirf Z-axis par Yaw rotation (&theta;) hota hai, iska formula hai: <font name='Courier'>qz = sin(&theta;/2), qw = cos(&theta;/2), qx = 0, qy = 0</font>."
        ),
        (
            "Q7. initial_pose.py me 'ROS Publisher Race Condition' kya hoti hai aur humne kaise solve kiya?",
            "Jab code me hum <font name='Courier'>rospy.Publisher()</font> banate hain, toh background me ROS master aur AMCL subscriber ke beech TCP network connection banne me kuch milliseconds lagte hain. Agar code agli hi line par <font name='Courier'>pub.publish()</font> chala de, toh subscriber ready nahi hota aur message hawa me gayab ho jata hai! Isko <i>Race Condition</i> kehte hain. Humne code me lagaya: <font name='Courier'>while pub.get_num_connections() == 0: rate.sleep()</font> — yeh line tab tak wait karti hai jab tak AMCL sach me sunne ke liye connect na ho jaye."
        ),
        (
            "Q8. Navigation me TF (Transform Tree) frames (map, odom, base_link) ka kya role hai?",
            "• <b>map:</b> Fixed world coordinate system. AMCL <font name='Courier'>map &rarr; odom</font> ka transform nikal kar wheel drift ko theek karta hai.<br/>"
            "• <b>odom:</b> Wheel encoders ke hisab se robot ka position. Yeh smooth hota hai par waqt ke saath slip hone se drift ho jata hai.<br/>"
            "• <b>base_footprint:</b> Zameen par robot ke center ka 2D point.<br/>"
            "• <b>base_link:</b> Robot ki physical body ka frame.<br/>"
            "• <b>base_scan:</b> LiDAR sensor ka frame jahan se laser nikalta hai."
        ),
        (
            "Q9. Agar raste me koi achanak aakar khada ho jaye toh robot kya karega?",
            "Jab aage rasta block hota hai, toh <font name='Courier'>move_base</font> <b>Recovery Behaviors</b> chalata hai: (1) Pehle costmap ko clear karke check karta hai ki koi sensor glitch toh nahi hai; (2) Fir robot apni hi jagah par 360 degree ghumta hai (Rotate in place) taaki aas-paas ka naya rasta dhund sake; (3) Agar fir bhi rasta band hai, toh Action Server goal ko <font name='Courier'>GoalStatus.ABORTED</font> declare kar deta hai. Hamara script isko gracefully catch karke agle station par move ho jata hai."
        ),
        (
            "Q10. Warehouse robotics me 'Dwell Time' ka kya matlab hai?",
            "Dwell time ka matlab hota hai robot ka station par rukne ka time. Hamare code me <font name='Courier'>rospy.sleep(2.0)</font> lagaya gaya hai. Yeh 2 second isliye rukta hai taaki industry me pallet load karna, robotic arm se samaan uthana, barcode scan karna ya charging dock par connect hone ka time simulate ho sake."
        ),
        (
            "Q11. MoveBaseGoal me 'header.frame_id = map' kyu likhte hain?",
            "Kyunki warehouse ke stations (x, y) coordinates static world map ke hisab se hain. Agar galti se hum <font name='Courier'>frame_id = 'base_link'</font> likh de, toh robot usko apni current moving body ke hisab se manega (jaise 'jahan khade ho wahan se 2 meter aage jao') aur robot deewaron me takrane lagega."
        ),
        (
            "Q12. Differential Drive robot kaise mudta (turn karta) hai?",
            "TurtleBot3 Burger me do wheels hote hain aur har wheel ki apni alag motor hoti hai. Agar dono wheel same speed me aage chalein toh robot seedha chalta hai. Agar left wheel ko rokk kar sirf right wheel chalayein toh robot left mudta hai. Aur agar ek wheel aage aur doosra peeche chalayein toh robot apni hi jagah par 360 degree ghum sakta hai (zero turn radius)."
        ),
        (
            "Q13. GoalStatus codes ka kya matlab hota hai?",
            "• <b>PENDING (0):</b> Goal server ke paas pahunch gaya par abhi execution start nahi hua.<br/>"
            "• <b>ACTIVE (1):</b> Robot raste me chal raha hai aur goal process ho raha hai.<br/>"
            "• <b>SUCCEEDED (3):</b> Robot target station par tolerance limit ke andar safely pahunch gaya.<br/>"
            "• <b>ABORTED (4):</b> Rasta band hone ya kisi error ki wajah se goal cancel ho gaya."
        ),
        (
            "Q14. package.xml aur CMakeLists.txt me kon-kon si dependencies daali hain aur kyu?",
            "Humne 5 main dependencies daali hain: (1) <font name='Courier'>rospy</font> - Python me ROS chalane ke liye; (2) <font name='Courier'>actionlib</font> - Action client/server chalane ke liye; (3) <font name='Courier'>move_base_msgs</font> - MoveBaseAction messages ke liye; (4) <font name='Courier'>geometry_msgs</font> - Point, Pose, Quaternion coordinate messages ke liye; (5) <font name='Courier'>nav_msgs</font> - Odometry aur Path ke liye."
        ),
        (
            "Q15. Examiner / Mam ke saamne 1 Minute me is project ko kaise explain karein?",
            "<i>'Mam, normal ROS practicals me RViz me jaa kar mouse se 2D Pose Estimate aur 2D Nav Goal click karna padta hai jo industry me impossible hai. Is project me humne do custom Python scripts banayi hain: Pehli script (<font name='Courier'>initial_pose.py</font>) bina mouse ke /initialpose topic par covariance ke saath message bhej kar AMCL particle filter ko automatically lock kar deti hai. Aur doosri script (<font name='Courier'>waypoint_navigator.py</font>) ek Action Client hai jo move_base se connect hokar robot ko 4 warehouse stations par sequentially drive karwati hai with a 2-second dwell delay at each station.'</i>"
        )
    ]

    for q, ans in viva_hinglish:
        q_box = [
            Paragraph(q, q_style),
            Paragraph(ans, ans_style)
        ]
        story.append(make_box(q_box, border_color=colors.HexColor("#e2e8f0"), bg_color=colors.HexColor("#f8fafc")))
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # CHAPTER 6: QUICK COMMAND CHEAT SHEET
    # -------------------------------------------------------------
    story.append(Paragraph("6. Quick Revision Commands Cheat Sheet", h1_style))

    cheat_data = [
        [Paragraph("<b>Kya Check Karna Hai</b>", body_bold), Paragraph("<b>Terminal Command</b>", body_bold)],
        [
            Paragraph("Saare running nodes ki list dekhna", body_style),
            Paragraph("<font name='Courier'>rosnode list</font>", code_style)
        ],
        [
            Paragraph("Robot ki current live position dekhna", body_style),
            Paragraph("<font name='Courier'>rostopic echo /odom/pose/pose</font>", code_style)
        ],
        [
            Paragraph("move_base ka goal status dekhna", body_style),
            Paragraph("<font name='Courier'>rostopic echo /move_base/status</font>", code_style)
        ],
        [
            Paragraph("Emergency me robot ko turant rokkna", body_style),
            Paragraph("<font name='Courier'>rostopic pub /cmd_vel geometry_msgs/Twist '{}'</font>", code_style)
        ],
        [
            Paragraph("TF Frames ka PDF graph generate karna", body_style),
            Paragraph("<font name='Courier'>rosrun tf view_frames &amp;&amp; evince frames.pdf</font>", code_style)
        ]
    ]
    t_cheat = Table(cheat_data, colWidths=[180, 324])
    t_cheat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_cheat)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Hinglish PDF Generated successfully at: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path)} bytes")

if __name__ == "__main__":
    build_pdf()
