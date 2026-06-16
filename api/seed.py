"""
Seed: subjects, topics, demo tutor, demo learners, sample assessment.
Run: python seed.py
"""
import sys
from database import SessionLocal, init_db
from models.user import User, Tutor, Learner, UserRole, LearnerTrack
from models.assessment import Subject, Topic, Assessment, Question, Option, QuestionType, Difficulty
from core.security import hash_password

init_db()
db = SessionLocal()

# ── Subjects ──────────────────────────────────────────────────────────────────
SUBJECTS = [
    {"name": "Mathematics",            "code": "MATH",   "description": "CAPS Mathematics Gr 10–12 & Matric Upgrade"},
    {"name": "Mathematical Literacy",  "code": "MLIT",   "description": "CAPS Mathematical Literacy Gr 10–12"},
    {"name": "Physical Sciences",      "code": "PHSC",   "description": "CAPS Physical Sciences (Physics + Chemistry) Gr 10–12"},
    {"name": "Python & Data Science",  "code": "PYDS",   "description": "Intro to Python programming and data science fundamentals"},
    {"name": "Cybersecurity Awareness","code": "CYBER",  "description": "Digital safety, threats, and online security for everyday users"},
]

subject_map = {}
for s in SUBJECTS:
    existing = db.query(Subject).filter(Subject.code == s["code"]).first()
    if not existing:
        obj = Subject(**s)
        db.add(obj)
        db.flush()
        subject_map[s["code"]] = obj
    else:
        subject_map[s["code"]] = existing

# ── Topics ────────────────────────────────────────────────────────────────────
TOPICS = {
    "MATH": [
        ("Algebra & Equations",        "Equations & Inequalities"),
        ("Functions & Graphs",         "Functions"),
        ("Trigonometry",               "Trigonometry"),
        ("Euclidean Geometry",         "Euclidean Geometry & Measurement"),
        ("Analytical Geometry",        "Analytical Geometry"),
        ("Statistics & Probability",   "Statistics"),
        ("Sequences & Series",         "Sequences & Series"),
        ("Finance, Growth & Decay",    "Finance"),
        ("Calculus",                   "Differential Calculus"),
    ],
    "MLIT": [
        ("Numbers & Calculations",     "Numbers"),
        ("Patterns & Relationships",   "Patterns, relationships & representations"),
        ("Finance",                    "Finance"),
        ("Measurement",                "Measurement"),
        ("Maps, Plans & Scales",       "Maps, plans & other representations of the physical world"),
        ("Data Handling",              "Data handling"),
        ("Probability",                "Probability"),
    ],
    "PHSC": [
        ("Mechanics",                  "Mechanics"),
        ("Waves, Sound & Light",       "Waves, Sound & Light"),
        ("Electricity & Magnetism",    "Electricity & Magnetism"),
        ("Matter & Materials",         "Matter & Materials"),
        ("Chemical Change",            "Chemical Change"),
        ("Chemical Systems",           "Chemical Systems"),
        ("Modern Physics",             "Matter & Beyond"),
    ],
    "PYDS": [
        ("Python Basics",              "Variables, data types, I/O"),
        ("Control Flow",               "If/else, loops"),
        ("Functions & Modules",        "Functions, imports, libraries"),
        ("Data Structures",            "Lists, dicts, sets, tuples"),
        ("File Handling & CSV",        "Reading/writing files"),
        ("Pandas & NumPy Basics",      "DataFrames, arrays"),
        ("Data Visualisation",         "Matplotlib, Seaborn basics"),
        ("Intro to ML",                "scikit-learn, train/test split, simple models"),
    ],
    "CYBER": [
        ("Digital Threats",            "Malware, phishing, social engineering"),
        ("Password Security",          "Strong passwords, MFA, password managers"),
        ("Safe Browsing",              "HTTPS, VPN, public Wi-Fi risks"),
        ("Social Media Safety",        "Privacy settings, oversharing risks"),
        ("Data Privacy & POPIA",       "SA data protection rights"),
        ("Incident Response Basics",   "What to do when you're compromised"),
    ],
}

for code, topics in TOPICS.items():
    subj = subject_map[code]
    for name, caps in topics:
        if not db.query(Topic).filter(Topic.subject_id == subj.id, Topic.name == name).first():
            db.add(Topic(subject_id=subj.id, name=name, caps_section=caps))

db.commit()
print("✓ Subjects & topics seeded")

# ── Demo Tutor ─────────────────────────────────────────────────────────────────
if not db.query(User).filter(User.phone == "+27838751445").first():
    tutor_user = User(
        full_name="Dingaan Machethe",
        phone="+27838751445",
        email="machethedm@gmail.com",
        hashed_password=hash_password("SKYLearn@2026"),
        role=UserRole.TUTOR,
    )
    db.add(tutor_user); db.flush()
    db.add(Tutor(
        user_id=tutor_user.id,
        qualification="MSc Data Science (UEL) | PGDip Data Science (Regenesys) | CND (EC-Council)",
        bio="Founder of SKYLearn-Innovation NPO. Data Scientist, AI/ML Engineer and educator.",
    ))
    db.commit()
    print(f"✓ Demo tutor: +27838751445 / SKYLearn@2026")
else:
    print("  Tutor already exists")

# ── Demo Learners ──────────────────────────────────────────────────────────────
demo_learners = [
    {"full_name": "Thabo Mokoena",  "phone": "+27710000001", "grade": "12", "track": LearnerTrack.CAPS_FULL_TIME},
    {"full_name": "Lerato Sithole", "phone": "+27710000002", "grade": "11", "track": LearnerTrack.CAPS_FULL_TIME},
    {"full_name": "Sipho Nkosi",    "phone": "+27710000003", "grade": "UPGRADE", "track": LearnerTrack.MATRIC_UPGRADE},
    {"full_name": "Naledi Dlamini", "phone": "+27710000004", "grade": "10", "track": LearnerTrack.CODING},
]
for dl in demo_learners:
    if not db.query(User).filter(User.phone == dl["phone"]).first():
        u = User(
            full_name=dl["full_name"],
            phone=dl["phone"],
            hashed_password=hash_password("Learner@2026"),
            role=UserRole.LEARNER,
        )
        db.add(u); db.flush()
        db.add(Learner(user_id=u.id, grade=dl["grade"], track=dl["track"]))
        db.commit()
        print(f"✓ Learner: {dl['phone']} / Learner@2026")
    else:
        print(f"  Learner {dl['phone']} exists")

# ── Sample Assessment (Mathematics — Algebra) ──────────────────────────────────
tutor_user = db.query(User).filter(User.phone == "+27838751445").first()
tutor = db.query(Tutor).filter(Tutor.user_id == tutor_user.id).first()
math_subj = subject_map["MATH"]
algebra_topic = db.query(Topic).filter(Topic.subject_id == math_subj.id, Topic.name == "Algebra & Equations").first()

if tutor and not db.query(Assessment).filter(Assessment.title == "Algebra: Equations & Inequalities — Gr 11").first():
    a = Assessment(
        tutor_id=tutor.id,
        subject_id=math_subj.id,
        title="Algebra: Equations & Inequalities — Gr 11",
        description="Covers linear equations, quadratic equations, and simultaneous equations.",
        time_limit_min=45,
        is_published=True,
        total_marks=10,
    )
    db.add(a); db.flush()

    q1 = Question(
        assessment_id=a.id, topic_id=algebra_topic.id,
        text="Solve for x: 2x + 5 = 13",
        q_type=QuestionType.SHORT_ANSWER, marks=2,
        difficulty=Difficulty.EASY, concept_tag="linear equations",
        order_num=1, correct_answer="4",
    )
    db.add(q1); db.flush()

    q2 = Question(
        assessment_id=a.id, topic_id=algebra_topic.id,
        text="Which of the following is the correct factorisation of x² - 9?",
        q_type=QuestionType.MCQ, marks=2,
        difficulty=Difficulty.EASY, concept_tag="factorisation",
        order_num=2,
    )
    db.add(q2); db.flush()
    for txt, correct in [("(x+3)(x-3)", True), ("(x-3)(x-3)", False), ("(x+9)(x-1)", False), ("(x+3)(x+3)", False)]:
        db.add(Option(question_id=q2.id, text=txt, is_correct=correct))

    q3 = Question(
        assessment_id=a.id, topic_id=algebra_topic.id,
        text="Solve the simultaneous equations:\n  3x + y = 10\n  x - y = 2",
        q_type=QuestionType.SHORT_ANSWER, marks=3,
        difficulty=Difficulty.MEDIUM, concept_tag="simultaneous equations",
        order_num=3, correct_answer="x=3, y=1",
    )
    db.add(q3); db.flush()

    q4 = Question(
        assessment_id=a.id, topic_id=algebra_topic.id,
        text="Which inequality is represented by the solution x > -2 and x ≤ 5?",
        q_type=QuestionType.MCQ, marks=1,
        difficulty=Difficulty.MEDIUM, concept_tag="inequalities",
        order_num=4,
    )
    db.add(q4); db.flush()
    for txt, correct in [("-2 < x ≤ 5", True), ("-2 ≤ x < 5", False), ("x > -2 or x > 5", False), ("x ≤ -2 and x > 5", False)]:
        db.add(Option(question_id=q4.id, text=txt, is_correct=correct))

    q5 = Question(
        assessment_id=a.id, topic_id=algebra_topic.id,
        text="Determine the roots of x² - 5x + 6 = 0",
        q_type=QuestionType.MCQ, marks=2,
        difficulty=Difficulty.MEDIUM, concept_tag="quadratic equations",
        order_num=5,
    )
    db.add(q5); db.flush()
    for txt, correct in [("x = 2 or x = 3", True), ("x = -2 or x = -3", False), ("x = 1 or x = 6", False), ("x = 2 or x = -3", False)]:
        db.add(Option(question_id=q5.id, text=txt, is_correct=correct))

    db.commit()
    print("✓ Sample assessment seeded (Algebra Gr 11, 5 questions, 10 marks)")
else:
    print("  Sample assessment already exists")

db.close()
print("\nSeed complete.")
print("─" * 50)
print("Demo accounts:")
print("  Tutor:   +27838751445 / SKYLearn@2026")
print("  Learner: +27710000001 / Learner@2026  (Thabo, Gr 12)")
print("  Learner: +27710000002 / Learner@2026  (Lerato, Gr 11)")
print("  Learner: +27710000003 / Learner@2026  (Sipho, Upgrade)")
print("  Learner: +27710000004 / Learner@2026  (Naledi, Coding)")
