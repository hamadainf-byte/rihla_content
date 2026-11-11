"""يبني ملف catalog.json تلقائيًا من مجلد content.

الاستعمال (داخل هذا المجلد):   python build_catalog.py
لا يحتاج أي مكتبة إضافية.
"""
import json
import os
import urllib.parse

# عنوان موقعك على GitHub Pages (بدون / في النهاية)
BASE_URL = "https://hamadainf-byte.github.io/rihla_content"

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, "content")

STAGES = {
    "primary": ["p1", "p2", "p3", "p4", "p5"],
    "middle": ["m1", "m2", "m3", "m4"],
    "secondary": ["s1", "s2", "s3"],
}
SUBJECTS = [
    ("math", "رياضيات"),
    ("physics", "فيزياء"),
    ("arabic", "عربية"),
    ("english", "إنجليزية"),
]

# كلمات اسم الملف ← ما يظهر للتلميذ (عدّلها كما تشاء)
WORDS = {
    "bac": "بكالوريا",
    "bem": "شهادة التعليم المتوسط",
    "exam": "اختبار",
    "test": "اختبار",
    "devoir": "فرض",
    "td": "تمارين",
    "ex": "تمارين",
    "exercises": "تمارين",
    "summary": "ملخص",
    "resume": "ملخص",
    "lesson": "درس",
    "solution": "التصحيح",
    "correction": "التصحيح",
    "corrige": "التصحيح",
    "sujet": "الموضوع",
    "t1": "الفصل الأول",
    "t2": "الفصل الثاني",
    "t3": "الفصل الثالث",
}


def title_of(stem):
    """bac-2017-solution  ←  بكالوريا 2017 التصحيح"""
    parts = stem.replace("_", "-").split("-")
    return " ".join(WORDS.get(p.lower(), p) for p in parts if p)


def url_of(*parts):
    return BASE_URL + "/" + "/".join(urllib.parse.quote(p) for p in parts)


def pdf_names(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(f for f in os.listdir(folder) if f.lower().endswith(".pdf"))


def entries(stage, year, subject, kind, newest_first=False):
    folder = os.path.join(CONTENT, stage, year, subject, kind)
    names = pdf_names(folder)
    if newest_first:
        names.reverse()
    return [
        {
            "title": title_of(os.path.splitext(n)[0]),
            "url": url_of("content", stage, year, subject, kind, n),
        }
        for n in names
    ]


def read_videos(stage, year, subject):
    """ملف lessons/videos.txt: في كل سطر  عنوان الدرس | رابط يوتيوب"""
    path = os.path.join(CONTENT, stage, year, subject, "lessons", "videos.txt")
    items = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "|" in line:
                    title, link = (x.strip() for x in line.split("|", 1))
                    items.append({"title": title, "video": link})
    return items


def build():
    subjects = []
    total = 0
    for sid, name in SUBJECTS:
        years = {}
        for stage, year_ids in STAGES.items():
            for year in year_ids:
                lessons = read_videos(stage, year, sid) + [
                    {"title": e["title"], "pdf": e["url"]}
                    for e in entries(stage, year, sid, "lessons")
                ]
                data = {
                    "lessons": lessons,
                    "summaries": entries(stage, year, sid, "summaries"),
                    "exams": entries(stage, year, sid, "exams", newest_first=True),
                }
                if any(data.values()):
                    years[year] = data
                    total += sum(len(v) for v in data.values())
        subjects.append({"id": sid, "name": name, "enabled": True, "years": years})

    with open(os.path.join(HERE, "catalog.json"), "w", encoding="utf-8") as f:
        json.dump({"version": 1, "subjects": subjects}, f, ensure_ascii=False, indent=2)
    print("تم بناء catalog.json، عدد العناصر:", total)


if __name__ == "__main__":
    build()
